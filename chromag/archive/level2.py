# -*- coding: utf-8 -*-

"""Routines for archiving ChroMag level 2 data, i.e., sending data to cold
storage.
"""

from .. import __version__
from ..config import get_option
from ..logging import logger


def archive_l2(run):
    gateway_dir = get_option("archive", "gateway_dir")
    tarball_basename = f"{run.observing_day}.chromag.l2.{__version__}.tar.gz"

    # [TODO]: make tarball, tarlist
    logger.info("created level 2 tarball")
    # [TODO]: put link to tarball in gateway directory
    logger.info("sent level 2 tarball to archive via gateway")
