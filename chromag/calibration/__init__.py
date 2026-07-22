# -*- coding: utf-8 -*-

"""Routines for handling photometric/polarimetric calibration."""

import datetime

from .. import __version__

from netCDF4 import Dataset
import numpy as np


class Calibration:
    """Class representing the photometric/polarimetric calibration artifacts
    needed to calibrate the science images.
    """

    def __init__(self, catalog):
        self.catalog = catalog

        self.exposure_tolerance = 1.0e-8

        self.dark_files = None
        self.dark_images = None
        self.dark_exposures = None

        self.flat_files = None
        self.flat_images = None
        self.flat_exposures = None
        self.flat_wavelengths = None

        self.add_catalog(catalog)

    def add_catalog(self, catalog):
        self.dark_files = [f for f in catalog if f.is_dark()]
        self.dark_images = [np.mean(d.data, axis=0) for d in self.dark_files]
        self.dark_exposures = np.array([d.exposure for d in self.dark_files])

        self.flat_files = [f for f in catalog if f.is_flat()]
        self.flat_images = [f.data for f in self.flat_files]
        self.flat_exposures = np.array([d.exposure for d in self.flat_files])
        self.flat_wavelengths = np.array([d.wavelength for d in self.flat_files])

    def get_dark(self, exposure: float):
        """Get closest dark to the given time matching the exposure."""

        # first generate list of matching exposures for a specified tolerance
        exp_diffs = np.array([e - exposure for e in self.dark_exposures])
        matching_exps = np.where(exp_diffs < self.exposure_tolerance)[0]
        matching_exps = np.array([int(i) for i in matching_exps])
        dark = np.array(self.dark_images)[matching_exps[0]]

        return dark

    def get_flat(self, time, exposure, wavelength):
        """Get closest flat to the given time matching the exposure and wavelength."""
        pass

    def __str__(self):
        n_darks = 0 if self.dark_files is None else len(self.dark_files)
        n_flats = 0 if self.flat_times is None else len(self.flat_files)
        return f"calibration <{n_darks} darks, {n_flats} flats>"

    def get_master_dark(self, exposure):
        """Get master dark for the day given an exposure time."""
        # average darks of same exposure across first dimension (4 polarization states)
        tol = 1e-8
        exp_diffs = np.array([e - exposure for e in self.dark_exps])
        matching_exps = np.where(exp_diffs < tol)[0]
        matching_exps = np.array([int(i) for i in matching_exps])
        dark_data_matching_exps = np.array(self.dark_data)[matching_exps]
        polavg_darks = []
        for data in dark_data_matching_exps:
            polavg_data = np.mean(data, axis=0)
            polavg_darks.append(polavg_data)

        # then average all into one master dark
        master_dark = np.mean(polavg_darks, axis=0)
        return master_dark

    def save_calibration_file(self, filename: str):
        """Save calibration file with master dark, should this be for one exposure time or contain multiple master darks?"""

        if self.dark_files is None or self.flat_files is None:
            return

        root_group = Dataset(filename, "w")

        now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        root_group.Created = now
        root_group.Version = __version__

        # [TODO]: set other metadata

        # [TODO]: find these sizes out from the data
        xsize = root_group.createDimension("xsize", 2560)
        ysize = root_group.createDimension("ysize", 2160)

        dark_group = root_group.createGroup("Darks")
        n_darks = dark_group.createDimension("n_darks", len(self.dark_files))

        dark_images = dark_group.createVariable(
            "images",
            "f4",
            (
                "n_darks",
                "ysize",
                "xsize",
            ),
        )
        for i, d in enumerate(self.dark_images):
            dark_images[i, :, :] = d

        dark_exposures = dark_group.createVariable("exposures", "f4", ("n_darks",))
        dark_exposures[:] = self.dark_exposures

        flat_group = root_group.createGroup("Flats")
        n_flats = flat_group.createDimension("n_flats", len(self.flat_files))
        flat_images = flat_group.createVariable(
            "images",
            "f4",
            (
                "n_flats",
                "ysize",
                "xsize",
            ),
        )
        for f, i in enumerate(self.flat_images):
            flat_images[:, :, i] = f

        flat_exposures = flat_group.createVariable("exposures", "f4", ("n_flats",))
        flat_exposures[:] = self.flat_exposures

        demod_group = root_group.createGroup("Demodulation")

        root_group.close()


def make_calibration(catalog):
    return Calibration(catalog)
