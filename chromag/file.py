# -*- coding: utf-8 -*-

"""Module handling ChroMag files."""

import os

from astropy.io import fits
import numpy as np

from .config import get_basedir
from .datetime import dateobs2datetime

# 20250813T215541.869Z.fits
l0_basename_format = "{year:04d}{month:02d}{day:02d}T{hour:02d}{minute:02d}{second:02d}.{milliseconds}Z.fits"
l1_basename_format = "{year:04d}{month:02d}{day:02d}T{hour:02d}{minute:02d}{second:02d}.{milliseconds}Z.chromag.l1.fits"

with open(os.path.join(os.path.dirname(__file__), "header_template.txt"), "r") as f:
    header_template = f.read()


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
                primary_header["DATATYPE"] if "DATATYPE" in primary_header else ""
            )

            self.wavelength = (
                primary_header["WAVELNTH"] if "WAVELNTH" in primary_header else 0.0
            )
            self.exposure = (
                primary_header["EXPTIME"] if "EXPTIME" in primary_header else 0.0
            )

            self.scan_i = primary_header["SCAN_I"] if "SCAN_I" in primary_header else 0
            self.scan_n = primary_header["SCAN_N"] if "SCAN_N" in primary_header else 0

            self.obs_description = (
                primary_header["OBS_DESC"] if "OBS_DESC" in primary_header else ""
            )

            # possible values Sun, Diffuser, Dark, or Lamp
            self.object = primary_header["OBJECT"] if "OBJECT" in primary_header else ""

    def is_dark(self):
        return self.datatype == "Calibration" and self.object == "Dark"

    def is_flat(self):
        # TODO: is this the right way to tell if a file is a flat?
        return self.datatype == "Calibration" and self.object == "Diffuser"

    def is_science(self):
        return self.datatype == "Science"

    def __str__(self):
        wavelength = f"{self.wavelength} nm" if self.wavelength is not None else "---"
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

        self.exposure = raw_file.exposure

        process_basedir = get_basedir(self.observing_day, "process")
        l1_dir = os.path.join(process_basedir, self.observing_day, "level1")

        prefix = self.raw_file.basename.removesuffix(".fits")
        self.basename = f"{prefix}.chromag.l1.fits"
        self.filename = os.path.join(l1_dir, self.basename)

        self.primary_header = reorder_header(raw_file.primary_header)
        self.primary_header["LEVEL"] = "L1"

        self._data = None

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


def reorder_header(header: fits.header.Header):
    h = fits.header.Header.fromstring(header_template, sep="\n")
    for k, v in header.items():
        if k != "COMMENT" and k != "":
            h[k] = v
    return h
