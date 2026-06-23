# -*- coding: utf-8 -*-

"""Module handling ChroMag files."""

import os

from astropy.io import fits

from .datetime import dateobs2datetime

# 20250813T215541.869Z.fits
l0_basename_format = "{year:04d}{month:02d}{day:02d}T{hour:02d}{minute:02d}{second:02d}.{milliseconds}Z.fits"


class ChroMagFile:
    """Class representing a ChroMag file, starting from raw and potentially
    progresssing to a level 1 file.
    """

    def __init__(self, filename):
        self.filename = filename
        self.basename = os.path.basename(self.filename)
        with fits.open(filename) as f:
            primary_header = f[0].header

            self.date_obs = dateobs2datetime(primary_header["DATE-OBS"])

            # possible values Scientific, Engineering, or Calibration
            self.datatype = primary_header["DATATYPE"]

            self.wavelength = primary_header["WAVELNTH"]
            self.exposure = primary_header["EXPTIME"]

            self.scan_i = primary_header["SCAN_I"]
            self.scan_n = primary_header["SCAN_N"]

            self.obs_description = primary_header["OBS_DESC"]

            # possible values Sun, Diffuser, Dark, or Lamp
            self.object = primary_header["OBJECT"]

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
