# -*- coding: utf-8 -*-

"""Sub-package for end-of-day processing
"""

import logging
import os

from ..config import read_config, get_option

from ..pipeline import Run
from ..logging import setup_logging, get_level

from .inventory import inventory
from .l1_process import l1_process
from .l2_process import l2_process


def run(date, config_filename):
    """Run the end-of-day processing.
    """
    read_config(config_filename)

    log_basedir = get_option("logging", "basedir")
    log_filename = os.path.join(log_basedir, f"{date}.chromag.eod.log")

    level = get_level(get_option("logging", "level"))
    rotate = get_option("logging", "rotate")
    max_version = get_option("logging", "max_version")

    logger = setup_logging(log_filename, level=level, rotate=rotate,
        max_version=max_version)

    run = Run(date, "eod", logger)

    logger.info(f"starting pipeline on {date}...")

    run.catalog = inventory(run, skip=False)
    l1_process(run, skip=not get_option("level1", "process"))
    l2_process(run, skip=not get_option("level2", "process"))

    logger.info(f"done...")