# -*- coding: utf-8 -*-

"""Sub-package for end-of-day processing
"""

import datetime
import logging
import os

from .clearday import clearday
from .inventory import run_inventory, Catalog
from .level1 import process as process_l1
from .level2 import process as process_l2

from .. import __version__
from ..archive import archive_l0, archive_l1, archive_l2
from ..calibration import make_calibration
from ..config import read_config, get_option
from ..datetime import human_timedelta
from ..logging import setup_logging, get_level
from ..pipeline import Run


# set umask for process: rwxrwxr-x for directories, rw-rw-r--- for files
os.umask(0o002)


def run(observing_day: str, config_filename: str, reprocessing: bool = False):
    """Run the end-of-day processing."""
    read_config(config_filename)

    log_basedir = get_option("logging", "basedir")

    log_filename = os.path.join(log_basedir, f"{observing_day}.chromag.eod.log")

    level = get_level(get_option("logging", "level"))
    rotate = get_option("logging", "rotate")
    max_version = get_option("logging", "max_version")

    logger = setup_logging(
        log_filename, level=level, rotate=rotate, max_version=max_version
    )

    date_run = Run(observing_day, "eod", logger)

    logger.info(f"starting pipeline on {observing_day}...")
    start_dt = datetime.datetime.now()

    if reprocessing:
        clearday(date_run)

    date_run.catalog = run_inventory(date_run, skip=False)

    date_run.calibration = make_calibration(date_run.catalog)

    cal_dir = get_option("process", "caldir")
    if cal_dir is not None:
        if not os.path.isdir(cal_dir):
            os.mkdir(cal_dir)
        cal_basename = f"{observing_day}.chromag.calibration.{__version__}.nc"
        cal_filename = os.path.join(cal_dir, cal_basename)
        date_run.calibration.save_file(cal_filename)
        logger.info(f"wrote {cal_basename}")
    else:
        logger.info("process/caldir not set, not writing cal file")

    process_l1(date_run, skip=not get_option("level1", "process"))
    process_l2(date_run, skip=not get_option("level2", "process"))

    if not reprocessing:
        archive_l0(date_run)
    archive_l1(date_run)
    archive_l2(date_run)

    end_dt = datetime.datetime.now()
    time_interval = end_dt - start_dt
    human_time = human_timedelta(time_interval)
    logger.info(f"done: {human_time}")
