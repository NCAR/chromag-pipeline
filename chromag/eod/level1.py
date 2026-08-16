# -*- coding: utf-8 -*-

"""Module containing the level 1 processing."""

import datetime

from .. import __version__
from .. import __revision__
from ..config import get_basedir
from ..datetime import datetime2dateobs
from ..display import write_intensity_image, write_iquv_image
from ..pipeline import step
from ..file import ChroMagL1File, write_l1_file


@step()
def dark_correct(run, l1_file: ChroMagL1File):
    """Apply dark subtraction to raw data."""
    # get averaged dark of same exposure time
    dark = run.calibration.get_dark(l1_file.exposure)
    for i in range(4):
        l1_file.data[i, :, :] -= dark.squeeze()

    # update header
    l1_file.primary_header["DARK_COR"] = True
    # [TODO]: which dark(s) used?


@step()
def update_header(run, l1_file: ChroMagL1File):
    l1_file.primary_header["DATE_DP"] = datetime2dateobs(datetime.datetime.now())
    l1_file.primary_header["DPSWID"] = f"{__version__} [{__revision__}]"


@step()
def process(run):
    """Run the level 1 processing."""

    # [TODO]: need to do this by wave region?

    process_basedir = get_basedir(run.observing_day, "process")
    l1_dir = os.path.join(process_basedir, run.observing_day, "level1")
    if not os.path.isdir(l1_dir):
        create_dir(l1_dir)
        logger.info("created level1 directory")

    run.logger.info("L1 processing...")

    # loop through science files and perform the following steps:
    science_files = run.catalog[run.catalog.is_science]
    n_science_files = len(science_files)
    for i, raw_file in enumerate(science_files):
        run.logger.info(f"processing {i+1}/{n_science_files}: {raw_file.basename}")

        l1_file = ChroMagL1File(raw_file)

        # apply non-linearity camera correction (if necessary)

        # initial quality check
        #   discard really bad data

        # apply camera corrections, i.e., hot pixels, etc.

        dark_correct(run, l1_file)

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
