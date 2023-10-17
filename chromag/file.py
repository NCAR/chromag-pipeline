# -*- coding: utf-8 -*-

import os

from astropy.io import fits


class ChroMagFile:
    def __init__(self, filename):
        self.filename = filename
        self.basename = os.path.basename(self.filename)
        with fits.open(filename) as f:
            primary_header = f[0].header
            self.datatype = primary_header["DATATYPE"]
            self.wavelength = primary_header["WAVELNTH"]
            self.scan_i = primary_header["SCAN_I"]
            self.scan_n = primary_header["SCAN_N"]

    def __str__(self):
        wavelength = f"{self.wavelength} nm" if self.wavelength is not None else "---"
        return(f"{self.basename} [{wavelength}] ({self.datatype} scan: {self.scan_i}/{self.scan_n})")
