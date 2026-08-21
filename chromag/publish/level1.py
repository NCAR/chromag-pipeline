# -*- coding: utf-8 -*-

"""Routines for publishing, and retracting, level 1 ChroMag data, i.e.,
sending data to the web archive.
"""

import os

from ..config import get_option, get_basedir
from ..logging import logger


def publish_l1(run):
    """Clear the level 1 data from the web archive directories."""
    process_basedir = get_basedir(run.observing_day, "process")
    l1_dir = os.path.join(process_basedir, run.observing_day, "level1")
    if not os.path.isdir(l1_dir):
        logger.warning("no level1 directory to publish")

    # [TODO]: where should I get these from?
    wave_regions = ["587", "617", "656", "854", "1083"]
    for w in wave_regions:
        if get_option(w, "publish_l1"):
            wave_files = run.catalog[
                run.catalog.is_flat & (run.catalog.wave_region == w)
            ]
            logger.info(f"publishing {len(wave_files)} {w} nm level 1 files...")
            for f in wave_files:
                filename = f.l1_file.get_filename("filename")
                basename = os.path.basename(filename)
                logger.debug(f"{basename}")
        else:
            logger.info(f"skipped publishing {w} nm level 1 files")


def clearday_l1(run):
    # get web archive dir, fullres dir
    # delete all files with "chromag" in the same
    pass
