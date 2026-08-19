# -*- coding: utf-8 -*-

"""Module for clearing existing published ChroMag data."""

import os
import shutil

from ..config import get_basedir
from ..database import clearday as db_clearday
from ..logging import logger
from ..pipeline import step
from ..publish import clearday_l1


@step(top=True)
def clearday(run):
    """Remove all results for a day, from the database, process directory, and
    the web archive (but not the standard archive).
    """
    logger.info(f"clearing {run.observing_day}...")

    # clear processing directory
    process_basedir = get_basedir(run.observing_day, "process")
    process_dir = os.path.join(process_basedir, run.observing_day)
    if os.path.isdir(process_dir):
        logger.info(f"removing process directory {run.observing_day}/...")
        shutil.rmtree(process_dir)
    else:
        logger.info("process directory already cleared")

    # clear database
    db_clearday(run)

    # clear web directories
    clearday_l1(run)
