# -*- coding: utf-8 -*-

"""Routines for publishing, and retracting, level 1 ChroMag data, i.e.,
sending data to the web archive.
"""

import os
import glob
import shutil

from ..config import get_option, get_basedir
from ..datetime import decompose_date
from ..waveregions import available_waveregions
from ..logging import logger


def publish_l1(run):
    """Clear the level 1 data from the web archive directories."""
    process_basedir = get_basedir(run.observing_day, "process")
    l1_dir = os.path.join(process_basedir, run.observing_day, "level1")
    if not os.path.isdir(l1_dir):
        logger.warning("no level1 directory to publish")

    webarchive_basedir = get_option("results", "webarchive_basedir")
    publish_to_webarchive = webarchive_basedir is not None
    if publish_to_webarchive:
        webarchive_dir = os.path.join(
            webarchive_basedir, *decompose_date(run.observing_day)
        )
        if not os.path.isdir(webarchive_dir):
            os.makedirs(webarchive_dir)

    fullres_basedir = get_option("results", "fullres_basedir")
    publish_to_fullres = fullres_basedir is not None
    if publish_to_fullres:
        fullres_dir = os.path.join(fullres_basedir, *decompose_date(run.observing_day))
        if not os.path.isdir(fullres_dir):
            os.makedirs(fullres_dir)

    wave_regions = available_waveregions()
    for w in wave_regions:
        if get_option(w, "publish_l1"):
            wave_files = run.catalog[
                run.catalog.is_science & (run.catalog.wave_region == w)
            ]
            logger.info(f"publishing {len(wave_files)} {w} nm level 1 files...")
            for f in wave_files:
                # [TODO]: check GBU file before publishing
                if publish_to_webarchive:
                    # there might not be a level 1 file because of quality
                    if f.l1_file is not None:
                        filename = f.l1_file.get_filename("filename")
                        basename = os.path.basename(filename)
                        shutil.copy(filename, os.path.join(webarchive_dir, basename))
                        logger.debug(f"published {basename}")
                if publish_to_fullres:
                    for p in ["i_quicklook", "iquv_quicklook"]:
                        # there might not be a level 1 file because of quality
                        if f.l1_file is not None:
                            filename = f.l1_file.get_filename(p)
                            basename = os.path.basename(filename)
                            shutil.copy(filename, os.path.join(fullres_dir, basename))
                            logger.debug(f"published {basename}")

        else:
            logger.info(f"skipped publishing {w} nm level 1 files")


def clearday_l1(run):
    """Remove published level 1 files from the web archive and fullres
    directories. Files removed are of the form `*.chromag.WWWW.l1.*`.
    """
    for type in ["webarchive", "fullres"]:
        basedir = get_option("results", f"{type}_basedir")
        if basedir is None:
            logger.info(f"no {type} directory specified, not clearing")
        else:
            logger.info(f"clearing {type} directory...")

            for w in available_waveregions():
                files = glob.glob(
                    os.path.join(
                        basedir,
                        *decompose_date(run.observing_day),
                        f"*.chromag.{w}.l1.*",
                    )
                )
                logger.info(f"removing {len(files)} {w} nm files in {type}")
                for f in files:
                    os.remove(f)
