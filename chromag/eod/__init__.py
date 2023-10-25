# -*- coding: utf-8 -*-

"""Sub-package for end-of-day processing
"""

import datetime
import logging
import os

from ..config import read_config, get_option
from ..datetime import human_timedelta
from ..pipeline import Run
from ..logging import setup_logging, get_level

from .inventory import run_inventory
from .l1_process import run_l1_process
from .l2_process import run_l2_process


def run(date, config_filename):
    """Run the end-of-day processing."""
    read_config(config_filename)

    log_basedir = get_option("logging", "basedir")
    log_filename = os.path.join(log_basedir, f"{date}.chromag.eod.log")

    level = get_level(get_option("logging", "level"))
    rotate = get_option("logging", "rotate")
    max_version = get_option("logging", "max_version")

    logger = setup_logging(
        log_filename, level=level, rotate=rotate, max_version=max_version
    )

    date_run = Run(date, "eod", logger)

    logger.info(f"starting pipeline on {date}...")
    start_dt = datetime.datetime.now()

    date_run.catalog = run_inventory(date_run, skip=False)

    run_l1_process(date_run, skip=not get_option("level1", "process"))
    run_l2_process(date_run, skip=not get_option("level2", "process"))

    end_dt = datetime.datetime.now()
    time_interval = end_dt - start_dt
    human_time = human_timedelta(time_interval)
    logger.info(f"done: {human_time}")
