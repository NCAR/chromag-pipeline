# -*- coding: utf-8 -*-

"""Module containing the level 1 processing."""

import datetime
import os

from .. import __version__
from .. import __revision__
from ..config import get_basedir, get_option
from ..datetime import datetime2dateobs, human_timedelta
from ..display import write_intensity_image, write_iquv_image
from ..pipeline import step
from ..file import ChroMagL1File, write_l1_file, create_dir
from ..logging import logger


@step()
def dark_correct(run, l1_file: ChroMagL1File):
    """Apply dark subtraction to raw data."""

    # get averaged dark of matching exposure time to science image
    dark, dark_index = run.calibration.get_dark(l1_file.exposure)

    # [TODO]: use broadcasting to speed this up
    dims = l1_file.data.shape
    for i in range(dims[0]):
        l1_file.data[i, :, :] -= dark.squeeze()

    # update header
    l1_file.primary_header["DARK_COR"] = True
    l1_file.primary_header["DARKUSED"] = dark_index


@step()
def update_header(run, l1_file: ChroMagL1File):
    l1_file.primary_header["DATE_DP"] = datetime2dateobs(datetime.datetime.now())
    l1_file.primary_header["DPSWID"] = f"{__version__} [{__revision__}]"

    # [TODO]: should really get this from the calibration object
    cal_basename = f"{run.observing_day}.chromag.calibration.{__version__}.nc"
    l1_file.primary_header["CALFILE"] = cal_basename


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
    for i, raw_file in enumerate(science_files):
        logger.info(f"processing {i+1}/{n_science_files}: {raw_file.basename}...")

        l1_file = ChroMagL1File(raw_file)

        # apply non-linearity camera correction (if necessary)

        # initial quality check
        #   discard really bad data

        # apply camera corrections, i.e., hot pixels, etc.

        dark_correct(
            run, l1_file, intermediate=get_option("intermediate", "dark_correction")
        )

        # apply gain

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
