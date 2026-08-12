# -*- coding: utf-8 -*-

"""Module handling ChroMag files."""

import configparser
import os

from astropy.io import fits
from astropy.io.fits.card import Card, _format_float
import numpy as np

from ..config import get_basedir
from ..datetime import dateobs2datetime

# 20250813T215541.869Z.fits
l0_basename_format = "{year:04d}{month:02d}{day:02d}T{hour:02d}{minute:02d}{second:02d}.{milliseconds}Z.fits"
l1_basename_format = "{year:04d}{month:02d}{day:02d}T{hour:02d}{minute:02d}{second:02d}.{milliseconds}Z.chromag.l1.fits"

with open(os.path.join(os.path.dirname(__file__), "l1_header_template.txt"), "r") as f:
    l1_header_template = f.read()

cp = configparser.ConfigParser()
cp.read(os.path.join(os.path.dirname(__file__), "keyword_formats.cfg"))
keyword_formats = {k.upper(): cp.get("formats", k) for k in cp.options("formats")}
del cp


class ChroMagRawFile:
    """Class representing a ChroMag raw file."""

    def __init__(self, filename: str, observing_day: str):
        self.filename = filename
        self.basename = os.path.basename(self.filename)
        self.l1_file = None
        self._data = None
        self.observing_day = observing_day

        with fits.open(filename) as f:
            primary_header = f[0].header
            self.primary_header = primary_header

            self.date_obs = dateobs2datetime(primary_header["DATE-OBS"])

            # [TODO]: what should be done if required FITS keywords are
            # missing? Probably should fail in some way instead of just giving
            # a default value. Maybe there should be a validation before
            # attempting to process?

            # possible values Scientific, Engineering, or Calibration
            self.datatype = (
                primary_header["DATATYPE"] if "DATATYPE" in primary_header else None
            )

            self.wavelength = (
                primary_header["WAVELNTH"] if "WAVELNTH" in primary_header else None
            )
            self.wave_region = (
                str(int(float(primary_header["OSF_ID"])))
                if "OSF_ID" in primary_header
                else None
            )
            self.exposure = (
                primary_header["EXPTIME"] if "EXPTIME" in primary_header else None
            )

            self.scan_i = (
                primary_header["SCAN_I"] if "SCAN_I" in primary_header else None
            )
            self.scan_n = (
                primary_header["SCAN_N"] if "SCAN_N" in primary_header else None
            )

            self.obs_description = (
                primary_header["OBS_DESC"] if "OBS_DESC" in primary_header else None
            )

            # possible values Sun, Diffuser, Dark, or Lamp
            self.object = (
                primary_header["OBJECT"] if "OBJECT" in primary_header else None
            )

    def is_dark(self):
        return self.datatype == "Calibration" and self.object == "Dark"

    def is_flat(self):
        # TODO: is this the right way to tell if a file is a flat?
        return self.datatype == "Calibration" and self.object == "Diffuser"

    def is_science(self):
        return self.datatype == "Science"

    def __str__(self):
        if self.wavelength is None:
            wavelength = "---"
        else:
            if self.wavelength < 0.001:
                wavelength = "---"
            else:
                wavelength = f"{self.wavelength:0.3f}"
        datatype = self.datatype[0:3]
        return f"{self.basename} [{wavelength}] ({datatype} scan: {self.scan_i}/{self.scan_n})"

    @property
    def data(self):
        if self._data is None:
            with fits.open(self.filename) as f:
                self._data = f[0].data.astype(np.float32)
        return self._data

    @data.setter
    def data(self, im: np.ndarray):
        self._data = im

    @data.deleter
    def data(self):
        del self._data


class ChroMagL1File:
    """Class representing a ChroMag level 1 file"""

    def __init__(self, raw_file: ChroMagRawFile):
        self.raw_file = raw_file
        raw_file.l1_file = self

        self.observing_day = raw_file.observing_day

        self.wavelength = raw_file.wavelength
        self.wave_region = raw_file.wave_region
        self.exposure = raw_file.exposure

        self.primary_header = reorder_header(raw_file.primary_header)
        self.primary_header["LEVEL"] = "L1"

        self._data = None

    def get_filename(self, name: str):
        process_basedir = get_basedir(self.observing_day, "process")
        l1_dir = os.path.join(process_basedir, self.observing_day, "level1")

        prefix = self.raw_file.basename.removesuffix(".fits")

        if name == "filename":
            basename = f"{prefix}.chromag.l1.fits"
        elif name == "i_quicklook":
            basename = f"{prefix}.chromag.l1.i.png"
        elif name == "iquv_quicklook":
            basename = f"{prefix}.chromag.l1.iquv.png"

        return os.path.join(l1_dir, basename)

    @property
    def data(self):
        if self._data is None:
            with fits.open(self.raw_file.filename) as f:
                self._data = f[0].data.astype(np.float32)

        return self._data

    @data.setter
    def data(self, im: np.ndarray):
        self._data = im

    @data.deleter
    def data(self):
        del self._data


# save away default behavior, will need for non-FormattedFloat values
_orig_format_value = Card._format_value


class FormattedFloat(float):
    """Subclass float, adding a `fmt` attribute to specify how to format it,
    where `fmt` is an f-string format specifier.
    """

    def __new__(cls, value, fmt):
        obj = super().__new__(cls, value)
        obj.fmt = fmt
        return obj


def custom_format_value(self):
    """Method to be inserted into Card, so `self` is an instance of Card."""
    value = self.value

    # handle FormattedFloat values specially
    if isinstance(value, FormattedFloat):
        # format the float explicitly using your custom specifier
        value_str = f"{value:{value.fmt}}"
        # FITS requires the float string to be right-justified within 20 chars
        return f"{value_str:>20}"

    # revert to standard astropy behavior for all other data types
    return _orig_format_value(self)


# use our new custom float formatting function
Card._format_value = custom_format_value


def reorder_header(header: fits.header.Header):
    """Create a new header with the layout of a template (from the file
    l1_header_template.txt), but the values from the given header. Format the
    floating point values using the format specifications in
    keyword_formats.cfg.
    """
    h = fits.header.Header.fromstring(l1_header_template, sep="\n")
    for k, v in header.items():
        if k != "COMMENT" and k != "":
            if k in keyword_formats and v is not None:
                h[k] = FormattedFloat(v, keyword_formats[k])
            else:
                h[k] = v
    return h
