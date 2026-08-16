# -*- coding: utf-8 -*-

"""Module for clearing existing published ChroMag data."""

import os
import shutil

from ..config import get_basedir
from ..database import clearday as db_clearday
from ..logging import logger
from ..pipeline import step


@step()
def clearday(run):
    """Remove all results for a day, from the database, process directory, and
    the web archive (but not the standard archive).
    """
    logger.info(f"clearing {run.observing_day}...")

    process_basedir = get_basedir(run.observing_day, "process")
    process_dir = os.path.join(process_basedir, run.observing_day)
    logger.info(f"removing process directory {run.observing_day}/...")
    shutil.rmtree(process_dir)

    # [TODO]: implement
    #  - clear database tables
    #  - clear web directories
