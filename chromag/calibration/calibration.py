# -*- coding: utf-8 -*-

"""Create calibration to retrieve needed flat, darks, or demodulation matrix.
"""

import datetime
import os
import glob

from netCDF4 import Dataset
import numpy as np

from .. import __version__
from .. import __revision__
from ..logging import logger
from .kll_routine import kll_routine
from ..config import get_option


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

        self.flat_kll_files = None
        self.flat_kll_images = None
        self.flat_kll_exposures = None
        self.flat_kll_wavelengths = None
        self.flats_kll_used = []

        self.flat_files = None
        self.flat_images = None
        self.flat_exposures = None
        self.flat_wavelengths = None
        self.flats_used = []
        self.flat_scale_factors = None

        self.add_catalog(catalog)

    def add_catalog(self, catalog):

        # darks
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

        # KLL flats
        self.flat_kll_files = [f for f in catalog if f.is_kll_flat]
        if len(self.flat_kll_files) > 0:

            flat_kll_images = [f.data for f in self.flat_kll_files]
            flat_kll_exposures = np.array([f.exposure for f in self.flat_kll_files])
            flat_kll_wavelengths = np.array([f.wavelength for f in self.flat_kll_files])

            n_flats = len(self.flat_kll_files)
            logger.info(f"found {n_flats} offset flat file{'s'[:n_flats^1]}")

            # consolidate flats by exposure time, wavelength,
            # camera gain, camera bit depth, and camera temperature
            flat_identifiers = np.array(
                [
                    f"{e:0.6f}_{w:0.2f}"
                    for e, w in zip(flat_kll_exposures, flat_kll_wavelengths)
                ]
            )
            unique_ids = np.unique(flat_identifiers)
            n_unique_flats = len(unique_ids)
            # dims = self.flat_kll_files[0].data.shape
            frame_shape = flat_kll_images[0].shape
            height, width = frame_shape[-2], frame_shape[-1]
            dtype = self.flat_kll_files[0].data.dtype
            logger.info(f"creating {n_unique_flats} KLL flat{'s'[:n_unique_flats^1]}")

            self.flat_kll_images = np.zeros(
                (n_unique_flats, height, width), dtype=dtype
            )
            self.flat_kll_exposures = np.zeros(n_unique_flats, dtype=np.float32)
            self.flat_kll_wavelengths = np.zeros(n_unique_flats, dtype=np.float32)
            self.flats_kll_used = []

            for i, u in enumerate(unique_ids):
                mask = flat_identifiers == u
                indices = np.nonzero(mask)[0]
                indices_str = ", ".join(str(idx) for idx in indices.tolist())
                logger.debug(
                    f"producing KLL flat {i}/{n_unique_flats} from files {indices_str}"
                )

                # collect raw frames for this specific group and call KLL algorithm
                group_frames = [flat_kll_images[idx] for idx in indices]
                self.flats_kll_used.append(indices)
                self.flat_kll_images[i, :, :], _ = kll_routine(group_frames)

                self.flat_kll_exposures[i] = flat_kll_exposures[indices[0]]
                self.flat_kll_wavelengths[i] = flat_kll_wavelengths[indices[0]]

            for f in self.flat_kll_files:
                del f.data

            # then the KLL flats BECOME our flats!
            self.flat_files = self.flat_kll_files
            self.flat_images = self.flat_kll_images
            self.flat_exposures = self.flat_kll_exposures
            self.flat_wavelengths = self.flat_kll_wavelengths
            self.flats_used = self.flats_kll_used

        else:

            # non-KLL flats
            self.flat_files = [f for f in catalog if f.is_flat]
            if len(self.flat_files) > 0:

                flat_images = [f.data for f in self.flat_files]
                flat_exposures = np.array([f.exposure for f in self.flat_files])
                flat_wavelengths = np.array([f.wavelength for f in self.flat_files])

                n_flats = len(self.flat_files)
                logger.info(f"found {n_flats} non-offset flat file{'s'[:n_flats^1]}")

                # consolidate flats by exposure time, wavelength,
                # camera gain, camera bit depth, and camera temperature
                flat_identifiers = np.array(
                    [
                        f"{e:0.6f}_{w:0.2f}"
                        for e, w in zip(flat_exposures, flat_wavelengths)
                    ]
                )
                unique_ids = np.unique(flat_identifiers)
                n_unique_flats = len(unique_ids)
                frame_shape = flat_images[0].shape
                height, width = frame_shape[-2], frame_shape[-1]
                # dims = self.flat_files[0].data.shape
                dtype = self.flat_files[0].data.dtype
                logger.info(
                    f"creating {n_unique_flats} KLL flat{'s'[:n_unique_flats^1]}"
                )

                self.flat_images = np.zeros(
                    (n_unique_flats, height, width), dtype=dtype
                )
                # np.zeros((n_unique_flats, dims[1], dims[2]), dtype=dtype)
                self.flat_exposures = np.zeros(n_unique_flats, dtype=np.float32)
                self.flat_wavelengths = np.zeros(n_unique_flats, dtype=np.float32)
                self.flat_scale_factors = np.zeros(n_unique_flats, dtype=np.float32)

                for i, u in enumerate(unique_ids):
                    mask = flat_identifiers == u
                    indices = np.nonzero(mask)[0]

                    # stack non-KLL flats and take raw mean image
                    raw_mean_flat = np.mean(
                        [flat_images[idx] for idx in indices], axis=0
                    )
                    exp_val = flat_exposures[indices[0]]
                    wv_val = flat_wavelengths[indices[0]]

                    # grab reference KLL flat matching (exposure, wavelength)
                    kll_ref_flat = np.squeeze(
                        self.find_recent_kll_flat(exp_val, wv_val)
                    )

                    if kll_ref_flat is not None:
                        # masking zero values and taking ratio
                        valid_pixels = (raw_mean_flat > 0) & (kll_ref_flat > 0)
                        scale_factor = np.median(
                            kll_ref_flat[valid_pixels] / raw_mean_flat[valid_pixels]
                        )

                        # apply constant to scale reference KLL flat
                        self.flat_images[i, :, :] = kll_ref_flat * scale_factor
                        self.flat_scale_factors[i] = scale_factor
                        logger.info(
                            f"Group {u}: Applied KLL scale factor = {scale_factor:.6f}"
                        )
                    else:
                        logger.warning(
                            f"No reference KLL flat matching exp={exp_val}, wv={wv_val}. Falling back to raw mean flat."
                        )
                        self.flat_images[i, :, :] = raw_mean_flat
                        self.flat_scale_factors[i] = 1.0

                    self.flats_used.append(indices)
                    self.flat_exposures[i] = exp_val
                    self.flat_wavelengths[i] = wv_val

                for f in self.flat_files:
                    del f.data

        # [TODO]: consolidate flats by exposure time, camera gain, camera bit
        # depth, and camera temperature, then perform Kuhn-Lin to get a single
        # flat for each combination

    def get_dark(self, exposure: float) -> np.ndarray:
        """Get dark matching the exposure."""

        exp_diffs = np.abs(self.dark_exposures - exposure)
        matching_indices = np.where(exp_diffs < self.exposure_tolerance)[0]
        dark = np.array(self.dark_images)[matching_indices[0]]

        return dark, matching_indices[0]

    def get_flat(self, exposure: float, wavelength: float, kll=False) -> np.ndarray:
        """Get closest flat to the given time matching the exposure and wavelength."""

        # generate list of matching exposures and wavelengths for a specified tolerance
        if not kll:
            fe = self.flat_exposures
            fw = self.flat_wavelengths
            fi = self.flat_images
        else:
            fe = self.flat_kll_exposures
            fw = self.flat_kll_wavelengths
            fi = self.flat_kll_images
        exp_diffs = np.array([np.abs(e - exposure) for e in fe])
        wv_diffs = np.array([np.abs(w - wavelength) for w in fw])
        matching_idxs = np.where(
            (exp_diffs < self.exposure_tolerance)
            & (wv_diffs < self.wavelength_tolerance)
        )[0]
        matching_idxs = np.array([int(i) for i in matching_idxs])
        flat = np.array(fi)[matching_idxs]

        return flat

    def find_recent_kll_flat(self, exposure: float, wavelength: float) -> np.ndarray:
        """Get the most recent KLL flat matching exposure and wavelength."""

        # load most recent cal file
        cal_dir = get_option("process", "caldir")
        latest_file = None
        latest_time = 0
        flat = None
        with os.scandir(cal_dir) as entries:
            for entry in entries:
                if entry.is_file():
                    mod_time = entry.stat().st_mtime
                    if mod_time > latest_time:
                        latest_time = mod_time
                        latest_file = entry.path

        if latest_file is not None:
            logger.info(f"retrieving flat from file {latest_file}")

            # read in file as KLL flats (part of class)
            with Dataset(latest_file, "r") as root_group:
                if "Flats" in root_group.groups:
                    flat_group = root_group.groups["Flats"]
                    self.flat_kll_images = flat_group.variables["images"][:]
                    self.flat_kll_exposures = flat_group.variables["exposures"][:]
                    self.flat_kll_wavelengths = flat_group.variables["wavelengths"][:]

                    # get matching exposure and wavelength
                    flat = self.get_flat(exposure, wavelength, kll=True)

        return flat

    def __str__(self) -> str:
        """Provide a string representation of the object for debugging."""
        n_darks = 0 if self.dark_files is None else len(self.dark_files)
        n_flats = 0 if self.flat_files is None else len(self.flat_files)
        return f"calibration <{n_darks} dark{'s'[:n_darks^1]}, {n_flats} flat{'s'[:n_flats^1]}>"

    def save_file(self, filename: str):
        """Save calibration file with darks, flats, and demodulation matrices."""

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
        n_flats = flat_group.createDimension("n_flats", len(self.flat_exposures))
        flat_images = flat_group.createVariable(
            "images",
            "f4",
            (
                "n_flats",
                "ysize",
                "xsize",
            ),
        )
        if len(self.flat_images) > 0:
            flat_images[:] = self.flat_images

        flat_exposures = flat_group.createVariable("exposures", "f4", ("n_flats",))
        flat_exposures[:] = self.flat_exposures

        flat_wavelengths = flat_group.createVariable("wavelengths", "f4", ("n_flats",))
        flat_wavelengths[:] = self.flat_wavelengths

        flat_scale_factors = flat_group.createVariable(
            "scale_factors", "f4", ("n_flats",)
        )
        flat_scale_factors[:] = self.flat_scale_factors

        demod_group = root_group.createGroup("Demodulation")

        root_group.close()

    def restore_file(self, filename: str):
        """Restore a netCDF calibration file into a Calibration object."""
        pass
