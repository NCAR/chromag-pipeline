# -*- coding: utf-8 -*-

"""Create calibration to retrieve needed flat, darks, or demodulation matrix.
"""

import datetime
import os

from netCDF4 import Dataset
import numpy as np

from .. import __version__
from .. import __revision__
from ..logging import logger


class Calibration:
    """Class representing the photometric/polarimetric calibration artifacts
    needed to calibrate the science images.
    """

    def __init__(self, catalog):
        self.catalog = catalog

        if len(catalog) > 0:
            observing_day = catalog.catalog[0].observing_day
            self.basename = f"{observing_day}.chromag.calibration.{__version__}.nc"
        else:
            self.basename = None

        self.exposure_tolerance = 1.0e-8
        self.wavelength_tolerance = 1.0e-8

        self.dark_files = None
        self.darks_used = []
        self.dark_images = None
        self.dark_exposures = None

        self.flat_files = None
        self.flat_images = None
        self.flat_exposures = None
        self.flat_wavelengths = None

        self.add_catalog(catalog)

    def add_catalog(self, catalog):
        self.dark_files = [f for f in catalog if f.is_dark]

        dark_images = np.array([np.mean(d.data, axis=0) for d in self.dark_files])
        dark_exposures = np.array([d.exposure for d in self.dark_files])

        n_darks = len(self.dark_files)
        logger.info(f"found {n_darks} dark file{'s'[:n_darks^1]}")
        for i, (f, e) in enumerate(zip(self.dark_files, dark_exposures)):
            logger.debug(f"{i}/{n_darks}: {os.path.basename(f.filename)} [{e:0.6f} ms]")

        # consolidate darks by exposure time, camera gain, camera bit depth,
        # and camera temperature

        # [TODO]: add camera gain, camera bit depth, and camera temperature to
        # dark identifiers and save them in the class/netCDF file -- this
        # information is not in the FITS headers yet, though
        dark_identifiers = np.array([f"{e:0.6f}" for e in dark_exposures])
        unique_ids = np.unique(dark_identifiers)

        n_unique_darks = len(unique_ids)
        dims = self.dark_files[0].data.shape
        dtype = self.dark_files[0].data.dtype

        logger.info(f"creating {n_unique_darks} master dark{'s'[:n_unique_darks^1]}")

        self.dark_images = np.zeros((n_unique_darks, dims[1], dims[2]), dtype=dtype)
        self.dark_exposures = np.zeros(n_unique_darks, dtype=np.float32)
        for i, u in enumerate(unique_ids):
            mask = dark_identifiers == u
            indices = np.nonzero(mask)[0]
            indices_str = ", ".join(str(i) for i in indices.tolist())
            logger.debug(
                f"producing master dark {i}/{n_unique_darks} from files {indices_str}"
            )
            self.darks_used.append(indices)
            self.dark_images[i, :, :] = np.mean(dark_images[mask, :, :], axis=0)
            self.dark_exposures[i] = dark_exposures[indices[0]]

        for f in self.dark_files:
            del f.data

        self.flat_files = [f for f in catalog if f.is_flat]
        self.flat_images = [f.data for f in self.flat_files]
        self.flat_exposures = np.array([d.exposure for d in self.flat_files])
        self.flat_wavelengths = np.array([d.wavelength for d in self.flat_files])

        # also need to do kll flats, but will want to treat them differently?
        self.flat_kll_files = [f for f in catalog if f.is_kll_flat]
        self.flat_kll_images = [f.data for f in self.flat_kll_files]
        self.flat_kll_exposures = np.array([d.exposure for d in self.flat_kll_files])
        self.flat_kll_wavelengths = np.array(
            [d.wavelength for d in self.flat_kll_files]
        )

        # [TODO]: consolidate flats by exposure time, camera gain, camera bit
        # depth, and camera temperature, then perform Kuhn-Lin to get a single
        # flat for each combination

    def get_dark(self, exposure: float) -> np.ndarray:
        """Get dark matching the exposure."""

        exp_diffs = np.abs(self.dark_exposures - exposure)
        matching_indices = np.where(exp_diffs < self.exposure_tolerance)[0]
        dark = np.array(self.dark_images)[matching_indices[0]]

        return dark, matching_indices[0]

    def get_flat(self, time, exposure, wavelength) -> np.ndarray:
        """Get closest flat to the given time matching the exposure and wavelength."""

        # generate list of matching exposures and wavelengths for a specified tolerance
        exp_diffs = np.array([np.abs(e - exposure) for e in self.flat_exposures])
        wv_diffs = np.array([np.abs(w - wavelength) for w in self.flat_wavelengths])
        matching_idxs = np.where(
            (exp_diffs < self.exposure_tolerance)
            & (wv_diffs < self.wavelength_tolerance)
        )[0]
        matching_idxs = np.array([int(i) for i in matching_idxs])
        flat = np.array(self.flat_images)[matching_idxs]

        return flat

    def __str__(self) -> str:
        """Provide a string representation of the object for debugging."""
        n_darks = 0 if self.dark_files is None else len(self.dark_files)
        n_flats = 0 if self.flat_files is None else len(self.flat_files)
        return f"calibration <{n_darks} dark{'s'[:n_darks^1]}, {n_flats} flat{'s'[:n_flats^1]}>"

    def save_file(self, filename: str):
        """Save calibration file with darks, flats, and demodulation matrics."""

        if self.dark_files is None or self.flat_files is None:
            return

        root_group = Dataset(filename, "w")

        now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        root_group.Created = now
        root_group.Version = __version__
        root_group.Revision = __revision__

        # [TODO]: set other metadata

        dims = self.dark_images.shape
        xsize = root_group.createDimension("xsize", dims[2])
        ysize = root_group.createDimension("ysize", dims[1])

        dark_group = root_group.createGroup("Darks")
        n_darks = dark_group.createDimension("n_darks", len(self.dark_exposures))

        dark_images = dark_group.createVariable(
            "images",
            "f4",
            (
                "n_darks",
                "ysize",
                "xsize",
            ),
        )
        dark_images[:, :, :] = self.dark_images

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

    def restore_file(self, filename: str):
        """Restore a netCDF calibration file into a Calibration object."""
        pass
