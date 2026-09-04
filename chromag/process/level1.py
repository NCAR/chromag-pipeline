# -*- coding: utf-8 -*-

"""Module containing the level 1 processing."""

import datetime
import math
import os

import sunpy.coordinates.sun as sun

from .. import __version__
from .. import __revision__
from ..config import get_basedir, get_option
from ..datetime import datetime2dateobs, human_timedelta
from ..display import write_intensity_image, write_iquv_image
from ..pipeline import step
from ..file import (
    ChroMagRawFile,
    ChroMagL1File,
    FormattedFloat,
    write_l1_file,
    create_dir,
)
from ..logging import logger
from ..quality import sci_quality_check, sci_quality_name
from ..waveregions import waveregion_property


@step()
def quality_check(run, raw_file: ChroMagRawFile):
    """Performs quality check on the raw file. Returns whether it passed, i.e.,
    True if quality_bitmask is 0, False otherwise."""
    raw_file.quality_bitmask = sci_quality_check(raw_file)
    if raw_file.quality_bitmask != 0:
        quality_name = sci_quality_name(raw_file.quality_bitmask)
        logger.warn(f"failed quality {quality_name}, skipping L1")
    return raw_file.quality_bitmask == 0


@step()
def dark_correct(run, l1_file: ChroMagL1File):
    """Apply dark subtraction to raw data."""

    # get averaged dark of matching exposure time to science image
    dark, dark_index = run.calibration.get_dark(l1_file.exposure)

    # broadcast dark
    l1_file.data -= dark.reshape(1, *dark.shape)

    # update header
    l1_file.primary_header["DARK_COR"] = True
    l1_file.primary_header["DARKUSED"] = dark_index


@step()
def flat_correct(run, l1_file: ChroMagL1File):
    """Apply flat correction to dark-corrected data."""

    # get flat of matching exposure time & wavelength to science image
    flat, flat_index = run.calibration.get_flat(l1_file.exposure, l1_file.wavelength)

    # get averaged dark of matching exposure time to science image
    dark, dark_index = run.calibration.get_dark(l1_file.exposure)

    # mulitply with transmission and subtract off dark (??)
    flat_dark_corrected = flat - dark

    # correct science
    l1_file.data /= flat_dark_corrected.reshape(1, *dark.shape)

    # update header
    l1_file.primary_header["FLAT_COR"] = True
    l1_file.primary_header["FLATUSED"] = flat_index


@step()
def update_header(run, l1_file: ChroMagL1File):
    """Update the level 1 header once processing is complete."""

    # update ephemeris information
    dt = l1_file.date_obs
    l1_file.primary_header["SOLAR_P0"] = FormattedFloat(sun.P(dt).value, "0.3f")
    l1_file.primary_header["SOLAR_B0"] = FormattedFloat(sun.B0(dt).value, "0.3f")
    l1_file.primary_header["CAR_ROT"] = int(sun.carrington_rotation_number(dt))
    l1_file.primary_header["RSUN_OBS"] = FormattedFloat(
        sun.angular_radius(dt).value, "0.2f"
    )

    # update L1 processing information
    now = datetime2dateobs(datetime.datetime.now(), milliseconds=False)
    l1_file.primary_header["DATE"] = now
    l1_file.primary_header["DATE-L1"] = now
    l1_file.primary_header["L1SWID"] = f"{__version__} [{__revision__}]"
    l1_file.primary_header["CALWSID"] = f"{__version__} [{__revision__}]"
    l1_file.primary_header["CALFILE"] = run.calibration.basename

    platescale = waveregion_property(
        l1_file.wave_region, "platescale", l1_file.date_obs
    )
    l1_file.primary_header["CDELT1"] = FormattedFloat(platescale, "0.3f")
    l1_file.primary_header["CDELT2"] = FormattedFloat(platescale, "0.3f")

    # HISTORY section that is not part of template, added at the end of the
    # header
    steps = []
    if l1_file.primary_header["DARK_COR"]:
        steps.append("dark current subtracted")
    if l1_file.primary_header["FLAT_COR"]:
        steps.append("gain correctin applied")
    if l1_file.primary_header["DEMOD"]:
        steps.append("polarimetric demodulation performed")
    if l1_file.primary_header["DISTORT"]:
        steps.append("image distortion corrected")

    history = "Level 1 processing performed: " + ",".join(steps)
    l1_file.primary_header["HISTORY"] = history


@step(top=True)
def process(run):
    """Run the level 1 processing."""

    # [TODO]: need to do this by wave region?

    process_basedir = get_basedir(run.observing_day, "process")
    l1_dir = os.path.join(process_basedir, run.observing_day, "level1")
    if not os.path.isdir(l1_dir):
        create_dir(l1_dir, basepath=process_basedir)

    logger.info("L1 processing...")

    # loop through science files and perform the following steps:
    science_files = run.catalog[run.catalog.is_science]
    n_science_files = len(science_files)

    start_dt = datetime.datetime.now()
    i_format = f"{int(math.log(len(science_files), 10)) + 1}d"
    for i, raw_file in enumerate(science_files):
        logger.info(
            f"processing {i+1:{i_format}}/{n_science_files}: {raw_file.basename}..."
        )

        # initial quality check: do not process really bad data
        if not quality_check(run, raw_file):
            continue

        l1_file = ChroMagL1File(raw_file)

        # apply camera corrections, i.e., hot pixels, etc.

        dark_correct(
            run, l1_file, intermediate=get_option("intermediate", "dark_correction")
        )

        # apply non-linearity camera correction (if necessary)

        # apply flat

        # apply transmission

        # demodulation

        # off-band leakage subtraction

        # distortion correction

        # rotate solar North up

        # mask outer field of view

        # polarimetric coordinate transformation

        update_header(run, l1_file)

        write_l1_file(l1_file)
        write_intensity_image(l1_file)
        write_iquv_image(l1_file)

        del l1_file.data

        # some sort of quality assessment TBD
        #   based on simple assessment of light level etc. in Level 0 data
        #   possibly use data from Tip/Tilt system
        #   more sophisticated metrics from Level1B data that may reject data
        #     for some higher-level uses but not others

    end_dt = datetime.datetime.now()
    time_interval = end_dt - start_dt
    time_per_file = time_interval / n_science_files
    human_time = human_timedelta(time_per_file)
    logger.info(f"{human_time} per file for level 1 processing")
    run.l1_processing_time_per_file = time_per_file
