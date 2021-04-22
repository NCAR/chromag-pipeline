# -*- coding: utf-8 -*-

"""Sub-package for end-of-day processing
"""

import logging
import os

from ..config import read_config, get_option

from ..pipeline import Run
from ..logging import setup_logging, get_level


def run(date, config_filename):
    """Run the end-of-day processing.
    """
    run = Run(date, "eod")
    read_config(config_filename)

    log_basedir = get_option("logging", "basedir")
    log_filename = os.path.join(log_basedir, f"{date}.chromag.eod.log")

    level = get_level(get_option("logging", "level"))
    rotate = get_option("logging", "rotate")
    max_version = get_option("logging", "max_version")

    logger = setup_logging(log_filename, level=level, rotate=rotate,
        max_version=max_version)

    logger.info(f"starting pipeline on {date}...")
    logger.info(f"done...")