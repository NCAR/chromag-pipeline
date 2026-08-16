# -*- coding: utf-8 -*-

"""Routines for archiving ChroMag level 0 data, i.e., sending data to cold
storage.
"""

import os

from ..config import get_option, get_basedir
from ..file import create_dir, make_tarball, make_tarlist
from ..logging import logger


def archive_l0(run):
    """Create level 0 archive tarball. Use the level 0 files in the raw
    directory, but produce a .tar.gz file in the level0/ directory of the
    process directory.
    """
    raw_basedir = get_basedir(run.observing_day, "raw")
    raw_dir = os.path.join(raw_basedir, run.observing_day)

    process_basedir = get_basedir(run.observing_day, "process")
    l0_dir = os.path.join(process_basedir, run.observing_day, "level0")
    if not os.path.isdir(l0_dir):
        logger.info("creating level0 directory")
        create_dir(l0_dir)

    tarball_basename = f"{run.observing_day}.chromag.l0.tar.gz"
    tarball_filename = os.path.join(l0_dir, tarball_basename)

    logger.info("creating level 0 tarball...")
    try:
        tarball_filename = make_tarball(
            tarball_filename, raw_basedir, run.observing_day
        )
    except Exception as e:
        logger.error(f"error creating level 0 tarball: {e}")
        return
    logger.info("created level 0 tarball")

    tarlist_basename = f"{run.observing_day}.chromag.l0.tarlist"
    tarlist_filename = os.path.join(l0_dir, tarlist_basename)
    make_tarlist(tarball_filename, tarlist_filename)
    logger.info("created level 0 tarlist")

    gateway_dir = get_option("archive", "gateway_dir")
    if gateway_dir is not None:
        if not os.path.isdir(gateway_dir):
            create_dir(gateway_dir)

        gateway_filename = os.path.join(gateway_dir, tarball_basename)
        if os.path.islink(gateway_filename):
            os.remove(gateway_filename)

        os.symlink(tarball_filename, gateway_filename)
        logger.info("sent level 0 tarball to archive via gateway")
