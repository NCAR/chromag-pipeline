# -*- coding: utf-8 -*-

"""Module handling ChroMag files."""

import configparser
import os

from astropy.io import fits
from astropy.io.fits.card import Card, _format_float
import numpy as np

from ..config import get_basedir
from ..datetime import filename2datetime, dateobs2datetime, obsday_hours
from ..epochs import get_epochvalue


l1b_header_template = None
keyword_formats = None


def initialize_l1_header():
    """Read the level 1 header template if it hasn't been read yet."""
    global l1b_header_template
    if l1b_header_template is None:
        with open(
            os.path.join(os.path.dirname(__file__), "l1b_header_template.txt"), "r"
        ) as f:
            l1b_header_template = f.read()


def initialize_keyword_formats():
    """Read the formats for the keywords present in the raw header if they
    haven't been read yet.
    """
    global keyword_formats
    if keyword_formats is None:
        cp = configparser.ConfigParser()
        cp.read(os.path.join(os.path.dirname(__file__), "keyword_formats.cfg"))
        keyword_formats = {
            k.upper(): cp.get("formats", k) for k in cp.options("formats")
        }


class ChroMagRawFile:
    """Class representing a ChroMag raw file."""

    def __init__(self, filename: str, observing_day: str):
        self.filename = filename
        self.basename = os.path.basename(self.filename)

        self.quality_bitmask = 0

        self.l1_file = None
        self._data = None
        self.observing_day = observing_day

        self.primary_header = read_rawheader(filename)
        self.date_obs = dateobs2datetime(self.primary_header["DATE-OBS"])
        self.obsday_hours = obsday_hours(self.date_obs)

        # [TODO]: what should be done if required FITS keywords are
        # missing? Probably should fail in some way instead of just giving
        # a default value. Maybe there should be a validation before
        # attempting to process?

        # possible values Scientific, Engineering, or Calibration
        self.datatype = (
            self.primary_header["DATATYPE"]
            if "DATATYPE" in self.primary_header
            else None
        )

        self.wavelength = (
            self.primary_header["WAVELNTH"]
            if "WAVELNTH" in self.primary_header
            else None
        )
        self.wave_region = (
            str(int(float(self.primary_header["OSF_ID"])))
            if "OSF_ID" in self.primary_header
            else None
        )
        self.exposure = (
            self.primary_header["EXPTIME"] if "EXPTIME" in self.primary_header else None
        )

        self.scan_i = (
            self.primary_header["SCAN_I"] if "SCAN_I" in self.primary_header else None
        )
        self.scan_n = (
            self.primary_header["SCAN_N"] if "SCAN_N" in self.primary_header else None
        )

        self.obs_description = (
            self.primary_header["OBS_DESC"]
            if "OBS_DESC" in self.primary_header
            else None
        )

        # possible values Sun, Diffuser, Dark, or Lamp
        self.object = (
            self.primary_header["OBJECT"] if "OBJECT" in self.primary_header else None
        )

        # adding this 8/21 as synthetic flats have option in header called OFFSET
        # which can be "True" or "False", assuming now we do not know the offset
        self.offset = (
            self.primary_header["OFFSET"] if "OFFSET" in self.primary_header else None
        )

    @property
    def is_dark(self):
        return self.datatype == "Calibration" and self.object == "Dark"

    @property
    def is_flat(self):
        # TODO: is this the right way to tell if a file is a flat?
        return (
            self.datatype == "Calibration"
            and self.object == "Diffuser"
            and self.offset == "False"
        )

    @property
    def is_kll_flat(self):
        # TODO: is this the right way to tell if a file is a flat?
        return (
            self.datatype == "Calibration"
            and self.object == "Diffuser"
            and self.offset == "True"
        )

    @property
    def is_science(self):
        return self.datatype == "Scientific"

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
            self._data = read_rawdata(self.filename)
        return self._data

    @data.setter
    def data(self, im: np.ndarray):
        self._data = im

    @data.deleter
    def data(self):
        del self._data


from .repair import repair


def read_rawheader(filename: str):
    """Read the primary header of a raw ChroMag FITS file."""
    with fits.open(filename) as f:
        primary_header = f[0].header

    dt = filename2datetime(filename)
    repair_routines = get_epochvalue("header_repair_routines", dt).split(",")

    # careful: "".split(",") == [""]
    if len(repair_routines) > 1 or len(repair_routines[0]) > 0:
        repair(primary_header, repair_routines)

    return primary_header


def read_rawdata(filename: str):
    """Read the data from raw ChroMag FITS file."""
    with fits.open(filename) as f:
        data = f[0].data.astype(np.float32)

    dt = filename2datetime(filename)
    repair_routines = get_epochvalue("data_repair_routines", dt).split(",")

    # careful: "".split(",") == [""]
    if len(repair_routines) > 1 or len(repair_routines[0]) > 0:
        repair(data, repair_routines)

    return data


class ChroMagL1File:
    """Class representing a ChroMag level 1 file"""

    def __init__(self, raw_file: ChroMagRawFile):
        self.raw_file = raw_file
        raw_file.l1_file = self

        self.observing_day = raw_file.observing_day
        self.date_obs = raw_file.date_obs

        self.wavelength = raw_file.wavelength
        self.wave_region = raw_file.wave_region
        self.exposure = raw_file.exposure

        self.gbu_mask = 0

        self.primary_header = reorder_header(raw_file.primary_header)
        self.primary_header["LEVEL"] = "1B"

        self._data = None

    def get_filename(
        self,
        name: str,
        /,
        *,
        fullpath: bool = True,
        intermediate_step: str | None = None,
    ):
        """Get a filename related to the file, e.g., "filename" for the level 1
        FITS file, "i_quicklook", "iquv_quicklook", or "intermediate".
        """
        process_basedir = get_basedir(self.observing_day, "process")
        output_dir = os.path.join(process_basedir, self.observing_day, "level1")

        prefix = self.raw_file.basename.removesuffix(".fits")

        if name == "filename":
            basename = f"{prefix}.chromag.{self.wave_region}.l1b.fits"
        elif name == "i_quicklook":
            basename = f"{prefix}.chromag.{self.wave_region}.l1b.i.png"
        elif name == "iquv_quicklook":
            basename = f"{prefix}.chromag.{self.wave_region}.l1b.iquv.png"
        elif name == "intermediate":
            output_dir = os.path.join(output_dir, intermediate_step)
            basename = (
                f"{prefix}.chromag.{self.wave_region}.l1b.{intermediate_step}.fits"
            )
        else:
            raise NameError(f"unknown filename type {name}")

        return os.path.join(output_dir, basename) if fullpath else basename

    @property
    def data(self):
        """Retrieve the NumPy ndarray representing the data, reading the file
        if neccessary.
        """
        if self._data is None:
            self._data = read_rawdata(self.raw_file.filename)

        return self._data

    @data.setter
    def data(self, im: np.ndarray):
        """Set the data of the file, for example, after a processing step."""
        self._data = im

    @data.deleter
    def data(self):
        """Free the memory of the data."""
        del self._data


# save away default behavior, will need for non-FormattedFloat values
_orig_format_value = Card._format_value


class FormattedFloat(float):
    """Subclass float, adding a `fmt` attribute to specify how to format the
    float, where `fmt` is an f-string format specifier.
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
    l1a_header_template.txt), but the values from the given header. Format the
    floating point values using the format specifications in
    keyword_formats.cfg.
    """
    initialize_l1_header()
    initialize_keyword_formats()

    h = fits.header.Header.fromstring(l1b_header_template, sep="\n")
    for k, v in header.items():
        if k != "COMMENT" and k != "":
            if k in keyword_formats and v is not None:
                h[k] = FormattedFloat(v, keyword_formats[k])
            else:
                h[k] = v
    return h
