# -*- coding: utf-8 -*-

"""Routines for archiving ChroMag level 2 data, i.e., sending data to cold
storage.
"""

import os

from .. import __version__
from ..config import get_option
from ..logging import logger
from ..pipeline import step


@step()
def archive_l2(run):
    """Create level 2 archive tarball from the files in the level2/ directory."""
    if not get_option("level2", "archive"):
        logger.info("skipping archiving level 2 data")
        return

    process_basedir = get_basedir(run.observing_day, "process")
    l2_dir = os.path.join(process_basedir, run.observing_day, "level2")
    if not os.path.isdir(l2_dir):
        logger.warn("no level2/ directory to archive")
        return

    tarball_basename = f"{run.observing_day}.chromag.l2.{__version__}.tar.gz"
    tarball_filename = os.path.join(l2_dir, tarball_basename)

    # [TODO]: should it be limited to only certain files? maybe use
    # tarfile.TarFile.add() to individually add files.
    logger.info("creating level 2 tarball...")
    try:
        tarball_filename = make_tarball(
            tarball_filename,
            process_basedir,
            os.path.join(run.observing_day, "level2"),
        )
    except Exception as e:
        logger.error(f"error creating level 2 tarball: {e}")
        return
    logger.info("created level 2 tarball")

    tarlist_basename = f"{run.observing_day}.chromag.l2.{__version__}.tarlist"
    tarlist_filename = os.path.join(l2_dir, tarlist_basename)
    make_tarlist(tarball_filename, tarlist_filename)
    logger.info("created level 2 tarlist")

    gateway_dir = get_option("archive", "gateway_dir")
    if gateway_dir is not None:
        if not os.path.isdir(gateway_dir):
            create_dir(gateway_dir)

        gateway_filename = os.path.join(gateway_dir, tarball_basename)
        if os.path.islink(gateway_filename):
            os.remove(gateway_filename)

        os.symlink(tarball_filename, gateway_filename)
        logger.info("sent level 2 tarball to archive via gateway")
    else:
        logger.warn("no archive gateway set, not sending to archive")
