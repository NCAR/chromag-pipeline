# -*- coding: utf-8 -*-

"""Create calibration to retrieve needed flat, darks, or demodulation matrix.
"""

import datetime
import os
import glob
from typing import Tuple, Optional
from scipy.ndimage import center_of_mass, shift, gaussian_filter

from netCDF4 import Dataset
import numpy as np

from .. import __version__
from .. import __revision__
from ..logging import logger
from .kll_routine import kll_routine
from ..config import get_option


def create_full_frame_flat(
    non_kll_flat: np.ndarray,
    kll_object: np.ndarray,
    kll_ref_flat: np.ndarray,
    transition_width_px: float = 30.0,
) -> np.ndarray:
    """Derives a flat field valid to the edges of the detector by combining

    log-subtracted solar data inside the disk with reference KLL gain outside.
    """
    ny, nx = non_kll_flat.shape

    # begin with aligning the centered flat and kll object in case of offset
    core_non_kll = non_kll_flat > (0.50 * np.nanmax(non_kll_flat))
    core_kll_obj = kll_object > (0.50 * np.nanmax(kll_object))

    cy_non_kll, cx_non_kll = center_of_mass(core_non_kll)
    cy_kll_obj, cx_kll_obj = center_of_mass(core_kll_obj)

    dy = cy_non_kll - cy_kll_obj
    dx = cx_non_kll - cx_kll_obj

    aligned_kll_object = shift(kll_object, shift=(dy, dx), mode="constant", cval=0.0)

    # adjust for difference in radius
    y_idx, x_idx = np.ogrid[:ny, :nx]
    dist_map = np.sqrt((x_idx - cx_non_kll) ** 2 + (y_idx - cy_non_kll) ** 2)

    # detect horizontal disk radius
    center_row = int(cy_non_kll)
    profile = non_kll_flat[center_row, int(cx_non_kll) :]
    radius_candidates = np.where(profile < 0.20 * np.nanmax(profile))[0]
    solar_radius = (
        float(radius_candidates[0])
        if len(radius_candidates) > 0
        else 0.45 * min(ny, nx)
    )

    # define inner boundary (100% updated data) and outer boundary (100% KLL reference)
    r_inner = solar_radius - transition_width_px
    r_outer = solar_radius

    # define valid interior - strictly positive masks for log space
    valid_interior = (
        (dist_map <= r_outer) & (non_kll_flat > 0) & (aligned_kll_object > 0)
    )

    # gain scaling inside the clear core
    core_mask = dist_map <= (0.75 * solar_radius)
    flux_ratio = np.median(non_kll_flat[core_mask]) / np.median(
        aligned_kll_object[core_mask]
    )
    scaled_kll_obj = aligned_kll_object * flux_ratio

    # log subtraction on solar disk
    # ln(Gain) = ln(Image) - ln(Object) -> Gain = exp(ln(Image) - ln(Object))
    interior_flat = np.ones_like(non_kll_flat)
    interior_flat[valid_interior] = np.exp(
        np.log(non_kll_flat[valid_interior]) - np.log(scaled_kll_obj[valid_interior])
    )
    # normalize interior flat to median = 1.0 - or should use mean?
    interior_flat /= np.median(interior_flat[core_mask])

    # normalize external reference KLL flat - or should use mean?
    normalized_kll_ref = kll_ref_flat / np.median(kll_ref_flat[core_mask])

    # smooth radial alpha-blending accross limb, may need modification
    # alpha = 1.0 at center, fades to 0.0 at outer edge of transition zone
    alpha = np.clip((r_outer - dist_map) / (r_outer - r_inner), 0.0, 1.0)
    alpha = gaussian_filter(alpha, sigma=2.0)

    # master flat combines today's interior flat with edge reference flat
    full_frame_flat = alpha * interior_flat + (1.0 - alpha) * normalized_kll_ref

    # final overall normalization
    full_frame_flat /= np.median(full_frame_flat)

    return full_frame_flat


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

        # Darks
        self.dark_files = None
        self.darks_used = []
        self.dark_images = None
        self.dark_exposures = None

        # KLL Flats (Native Kuhn-Lin)
        self.flat_kll_files = None
        self.flat_kll_images = None
        self.flat_kll_exposures = None
        self.flat_kll_wavelengths = None
        self.flat_kll_objects = []  # Stores objects returned by kll_routine
        self.flats_kll_used = []

        # Non-KLL / Final Master Flats
        self.flat_files = None
        self.flat_images = None
        self.flat_exposures = None
        self.flat_wavelengths = None
        self.flats_used = []

        self.add_catalog(catalog)

    def add_catalog(self, catalog):
        """Processes darks, same-day KLL flats, and non-KLL flats from catalog."""
        # 1. Load and process Darks
        self._process_darks(catalog)

        # 2. Load and process KLL Flats (if present today)
        self._process_kll_flats(catalog)

        # 3. Load and process non-KLL Flats (modified via same-day or historical KLL)
        self._process_non_kll_flats(catalog)

    def _process_darks(self, catalog):
        """(1) Load darks and group by unique exposure time."""
        self.dark_files = [f for f in catalog if f.is_dark]
        n_darks = len(self.dark_files)

        if n_darks == 0:
            logger.info("No dark files found in catalog.")
            return

        logger.info(f"found {n_darks} dark file{'s'[:n_darks^1]}")
        dark_images = [
            np.mean(d.data, axis=0) if d.data.ndim == 3 else d.data
            for d in self.dark_files
        ]
        dark_exposures = np.array([d.exposure for d in self.dark_files])

        dark_identifiers = np.array([f"{e:0.6f}" for e in dark_exposures])
        unique_ids = np.unique(dark_identifiers)

        n_unique_darks = len(unique_ids)
        height, width = dark_images[0].shape[-2:]
        dtype = dark_images[0].dtype

        logger.info(f"creating {n_unique_darks} master dark{'s'[:n_unique_darks^1]}")

        self.dark_images = np.zeros((n_unique_darks, height, width), dtype=dtype)
        self.dark_exposures = np.zeros(n_unique_darks)

        for i, u in enumerate(unique_ids):
            mask = dark_identifiers == u
            indices = np.nonzero(mask)[0]
            indices_str = ", ".join(str(idx) for idx in indices.tolist())
            logger.debug(
                f"producing master dark {i+1}/{n_unique_darks} from files {indices_str}"
            )

            self.darks_used.append(indices)
            self.dark_images[i, :, :] = np.mean(
                [dark_images[idx] for idx in indices], axis=0
            )
            self.dark_exposures[i] = dark_exposures[indices[0]]

        for f in self.dark_files:
            del f.data

    def _process_kll_flats(self, catalog):
        """(2 & 4) Load KLL flats and execute Kuhn-Lin routine returning flat and object."""
        self.flat_kll_files = [f for f in catalog if f.is_kll_flat]
        n_flats = len(self.flat_kll_files)

        if n_flats == 0:
            return

        logger.info(f"found {n_flats} KLL offset flat file{'s'[:n_flats^1]}")

        flat_kll_images = [f.data for f in self.flat_kll_files]
        flat_kll_exposures = np.array([f.exposure for f in self.flat_kll_files])
        flat_kll_wavelengths = np.array([f.wavelength for f in self.flat_kll_files])

        flat_identifiers = np.array(
            [
                f"{e:0.6f}_{w:0.2f}"
                for e, w in zip(flat_kll_exposures, flat_kll_wavelengths)
            ]
        )
        unique_ids = np.unique(flat_identifiers)
        n_unique_flats = len(unique_ids)

        height, width = flat_kll_images[0].shape[-2:]
        dtype = flat_kll_images[0].dtype

        logger.info(
            f"creating {n_unique_flats} KLL master flat{'s'[:n_unique_flats^1]}"
        )

        self.flat_kll_images = np.zeros((n_unique_flats, height, width), dtype=dtype)
        self.flat_kll_exposures = np.zeros(n_unique_flats)
        self.flat_kll_wavelengths = np.zeros(n_unique_flats)
        self.flat_kll_objects = []
        self.flats_kll_used = []

        for i, u in enumerate(unique_ids):
            mask = flat_identifiers == u
            indices = np.nonzero(mask)[0]

            exp = flat_kll_exposures[indices[0]]
            dark, _ = self.get_dark(exp)

            group_frames = [flat_kll_images[idx] for idx in indices]
            self.flats_kll_used.append(indices)

            # Call KLL routine and capture both flat frame and returned metadata object
            kll_flat, kll_obj = kll_routine(group_frames, dark)
            self.flat_kll_images[i, :, :] = kll_flat
            self.flat_kll_objects.append(kll_obj)

            self.flat_kll_exposures[i] = exp
            self.flat_kll_wavelengths[i] = flat_kll_wavelengths[indices[0]]

        for f in self.flat_kll_files:
            del f.data

    def _process_non_kll_flats(self, catalog):
        """(3 & 5) Load non-KLL flats and modify using same-day or most recent KLL object."""
        self.flat_files = [f for f in catalog if f.is_flat and not f.is_kll_flat]
        n_flats = len(self.flat_files)

        # If no non-KLL flats exist today, promote KLL flats to primary flats (if any were taken)
        if n_flats == 0:
            if self.flat_kll_images is not None:
                self.flat_files = self.flat_kll_files
                self.flat_images = self.flat_kll_images
                self.flat_exposures = self.flat_kll_exposures
                self.flat_wavelengths = self.flat_kll_wavelengths
                self.flats_used = self.flats_kll_used
            return

        logger.info(f"found {n_flats} non-offset flat file{'s'[:n_flats^1]}")

        flat_images = [f.data for f in self.flat_files]
        flat_exposures = np.array([f.exposure for f in self.flat_files])
        flat_wavelengths = np.array([f.wavelength for f in self.flat_files])

        flat_identifiers = np.array(
            [f"{e:0.6f}_{w:0.2f}" for e, w in zip(flat_exposures, flat_wavelengths)]
        )
        unique_ids = np.unique(flat_identifiers)
        n_unique_flats = len(unique_ids)

        height, width = flat_images[0].shape[-2:]
        dtype = flat_images[0].dtype

        self.flat_images = np.zeros((n_unique_flats, height, width), dtype=dtype)
        self.flat_exposures = np.zeros(n_unique_flats)
        self.flat_wavelengths = np.zeros(n_unique_flats)
        self.flats_used = []

        for i, u in enumerate(unique_ids):
            mask = flat_identifiers == u
            indices = np.nonzero(mask)[0]

            exp_val = flat_exposures[indices[0]]
            wv_val = flat_wavelengths[indices[0]]

            # Raw dark-subtracted mean flat for this group
            dark, _ = self.get_dark(exp_val)
            raw_mean_flat = (
                np.mean([flat_images[idx] for idx in indices], axis=0) - dark
            )

            # Step 5: Check same-day KLL flats first, or fetch from most recent KLL calibration file
            kll_ref_flat, kll_ref_object = self._get_matching_kll_flat(exp_val, wv_val)

            if kll_ref_flat is not None:

                # Step 6: correct non-KLL flat with matching KLL object & flat
                corrected_flat = create_full_frame_flat(
                    raw_mean_flat, kll_ref_object, kll_ref_flat
                )
                self.flat_images[i, :, :] = corrected_flat
                logger.info(f"Group {u}: Modified non-KLL flat using KLL ref")

            else:

                # still need to change this - I dont think we're supposed to just use the dark corrected?
                logger.info(
                    f"No reference KLL flat found for exp={exp_val}, wv={wv_val}. Using raw dark-subtracted flat."
                )
                self.flat_images[i, :, :] = raw_mean_flat

            self.flats_used.append(indices)
            self.flat_exposures[i] = exp_val
            self.flat_wavelengths[i] = wv_val

        for f in self.flat_files:
            del f.data

    def _get_matching_kll_flat(
        self, exposure: float, wavelength: float
    ) -> Optional[np.ndarray]:
        """Finds same-day KLL flat or queries historical calibration file."""
        # 1. Search same-day KLL flats
        if self.flat_kll_images is not None and len(self.flat_kll_images) > 0:
            exp_diffs = np.abs(self.flat_kll_exposures - exposure)
            wv_diffs = np.abs(self.flat_kll_wavelengths - wavelength)
            matches = np.where(
                (exp_diffs < self.exposure_tolerance)
                & (wv_diffs < self.wavelength_tolerance)
            )[0]
            if len(matches) > 0:
                logger.info("Found matching KLL flat from today's observations.")
                idx = matches[0]
                kll_obj = (
                    self.flat_kll_objects[idx]
                    if idx < len(self.flat_kll_objects)
                    else None
                )
                return self.flat_kll_images[idx], kll_obj

        # 2. Search most recent past calibration file
        return self.find_recent_kll_flat(exposure, wavelength)

    def find_recent_kll_flat(
        self, exposure: float, wavelength: float
    ) -> Optional[np.ndarray]:
        """(5) Searches calibration directory for the most recent NetCDF file containing KLL flats."""
        cal_dir = get_option("process", "caldir")
        logger.info("cal_dir = ", cal_dir)
        if not os.path.exists(cal_dir):
            return None

        # Sort files by modification time (descending)
        cal_files = sorted(
            [
                os.path.join(cal_dir, f)
                for f in os.listdir(cal_dir)
                if f.endswith(".nc")
            ],
            key=os.path.getmtime,
            reverse=True,
        )

        for cal_file in cal_files:
            try:
                with Dataset(cal_file, "r") as root:
                    # Look inside dedicated KLL group first, or fallback to main Flats
                    target_group = None
                    if "KLL_Flats" in root.groups:
                        target_group = root.groups["KLL_Flats"]
                    # elif "Flats" in root.groups:
                    #    target_group = root.groups["Flats"]

                    if target_group is not None:
                        exposures = target_group.variables["exposures"][:]
                        wavelengths = target_group.variables["wavelengths"][:]

                        exp_diffs = np.abs(exposures.data - exposure)
                        wv_diffs = np.abs(wavelengths.data - wavelength)
                        matches = np.where(
                            (exp_diffs < self.exposure_tolerance)
                            & (wv_diffs < self.wavelength_tolerance)
                        )[0]

                        if len(matches) > 0:
                            logger.info(
                                f"Found reference KLL flat in historical file: {cal_file}"
                            )
                            return (
                                target_group.variables["images"][matches[0]],
                                target_group.variables["objects"][matches[0]],
                            )
            except Exception as e:
                logger.debug(f"Could not read {cal_file}: {e}")

        return None

    def get_dark(self, exposure: float) -> Tuple[np.ndarray, int]:
        """Get dark matching the exposure."""
        exp_diffs = np.abs(self.dark_exposures - exposure)
        matching_indices = np.where(exp_diffs < self.exposure_tolerance)[0]
        if len(matching_indices) == 0:
            matching_indices = [np.argmin(exp_diffs)]
        dark = np.array(self.dark_images)[matching_indices[0]]

        return dark, matching_indices[0]

    def save_file(self, filename: str):
        """(6) Save calibration artifacts (Darks, Final Flats, Native KLL Flats) to NetCDF file."""
        if self.dark_images is None and self.flat_images is None:
            logger.warning("No calibration data to save.")
            return

        with Dataset(filename, "w") as root_group:
            root_group.Created = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            root_group.Version = __version__
            root_group.Revision = __revision__

            dims = (
                self.dark_images.shape
                if self.dark_images is not None
                else self.flat_images.shape
            )
            root_group.createDimension("xsize", dims[2])
            root_group.createDimension("ysize", dims[1])

            # Write Darks Group
            if self.dark_images is not None:
                dark_group = root_group.createGroup("Darks")
                dark_group.createDimension("n_darks", len(self.dark_exposures))

                dark_images_var = dark_group.createVariable(
                    "images", "f4", ("n_darks", "ysize", "xsize")
                )
                dark_images_var[:] = self.dark_images

                dark_exps_var = dark_group.createVariable(
                    "exposures", "f4", ("n_darks",)
                )
                dark_exps_var[:] = self.dark_exposures

            # Write Master Flats Group (Final Calibrated Flats)
            if self.flat_images is not None:
                flat_group = root_group.createGroup("Flats")
                flat_group.createDimension("n_flats", len(self.flat_exposures))

                flat_images_var = flat_group.createVariable(
                    "images", "f4", ("n_flats", "ysize", "xsize")
                )
                flat_images_var[:] = self.flat_images

                flat_exps_var = flat_group.createVariable(
                    "exposures", "f4", ("n_flats",)
                )
                flat_exps_var[:] = self.flat_exposures

                flat_wvs_var = flat_group.createVariable(
                    "wavelengths", "f4", ("n_flats",)
                )
                flat_wvs_var[:] = self.flat_wavelengths

            # Write Native KLL Group (Dedicated group for future daily lookups)
            if self.flat_kll_images is not None:
                kll_group = root_group.createGroup("KLL_Flats")
                kll_group.createDimension("n_kll_flats", len(self.flat_kll_exposures))

                kll_images_var = kll_group.createVariable(
                    "images", "f4", ("n_kll_flats", "ysize", "xsize")
                )
                kll_images_var[:] = self.flat_kll_images

                kll_objects_var = kll_group.createVariable(
                    "objects", "f4", ("n_kll_flats", "ysize", "xsize")
                )
                kll_objects_var[:] = self.flat_kll_objects

                kll_exps_var = kll_group.createVariable(
                    "exposures", "f4", ("n_kll_flats",)
                )
                kll_exps_var[:] = self.flat_kll_exposures

                kll_wvs_var = kll_group.createVariable(
                    "wavelengths", "f4", ("n_kll_flats",)
                )
                kll_wvs_var[:] = self.flat_kll_wavelengths

        logger.info(f"Saved calibration file: {filename}")

    def __str__(self) -> str:
        """Provide a string representation of the object for debugging."""
        n_darks = 0 if self.dark_images is None else len(self.dark_images)
        n_flats = 0 if self.flat_images is None else len(self.flat_images)
        return f"calibration <{n_darks} dark{'s'[:n_darks^1]}, {n_flats} flat{'s'[:n_flats^1]}>"
