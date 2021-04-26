# -*- coding: utf-8 -*-

import os


class ChroMagFile:
    def __init__(self, filename):
        self.filename = filename
        self.basename = os.path.basename(self.filename)
        self.type = None   # sci, cal
        self.wave_region = None

    def __str__(self):
        wave_region = f"{self.wave_region} nm" if self.wave_region is not None else "---"
        return(f"{self.basename} ({wave_region} nm) [{self.type}]")
