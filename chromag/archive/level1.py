# -*- coding: utf-8 -*-

"""Routines for archiving ChroMag level 1 data, i.e., tarring and sending level
1 data to cold storage.
"""

import os

from .. import __version__
from ..config import get_option, get_basedir
from ..file import create_dir, make_tarball, make_tarlist
from ..logging import logger
from ..pipeline import step


@step()
def archive_l1(run):
    """Create level 1 archive tarball from the files in the level1/ directory."""
    if not get_option("level1", "archive"):
        logger.info("skipping archiving level 1 data")
        return

    process_basedir = get_basedir(run.observing_day, "process")
    l1_dir = os.path.join(process_basedir, run.observing_day, "level1")
    if not os.path.isdir(l1_dir):
        logger.warn("no level1/ directory to archive")
        return

    tarball_basename = f"{run.observing_day}.chromag.l1.{__version__}.tar.gz"
    tarball_filename = os.path.join(l1_dir, tarball_basename)

    # [TODO]: should it be limited to only certain files? maybe use
    # tarfile.TarFile.add() to individually add files.
    logger.info("creating level 1 tarball...")
    try:
        tarball_filename = make_tarball(
            tarball_filename,
            process_basedir,
            os.path.join(run.observing_day, "level1"),
        )
    except Exception as e:
        logger.error(f"error creating level 1 tarball: {e}")
        return
    logger.info("created level 1 tarball")

    tarlist_basename = f"{run.observing_day}.chromag.l1.{__version__}.tarlist"
    tarlist_filename = os.path.join(l1_dir, tarlist_basename)
    make_tarlist(tarball_filename, tarlist_filename)
    logger.info("created level 1 tarlist")

    gateway_dir = get_option("archive", "gateway_dir")
    if gateway_dir is not None:
        if not os.path.isdir(gateway_dir):
            create_dir(gateway_dir)

        gateway_filename = os.path.join(gateway_dir, tarball_basename)
        if os.path.islink(gateway_filename):
            os.remove(gateway_filename)

        os.symlink(tarball_filename, gateway_filename)
        logger.info("sent level 1 tarball to archive via gateway")
    else:
        logger.warn("no archive gateway set, not sending to archive")
