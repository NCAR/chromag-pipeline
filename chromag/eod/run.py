# -*- coding: utf-8 -*-

"""Module defining the actions to perform in an eod run.
"""

from collections import OrderedDict
import datetime
import os

from .clearday import clearday
from .level1 import process as process_l1
from .level2 import process as process_l2
from .inventory import run_inventory

from .. import __version__, __revision__
from ..archive import archive_l0, archive_l1, archive_l2
from ..calibration import Calibration
from ..config import read_config, get_option
from ..database import DatabaseError, insert_files
from ..datetime import human_timedelta
from ..logging import setup_logging, get_level
from ..pipeline import Run
from ..publish import publish_l1, publish_l2, publish_l3
from ..quality import write_quality_files


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

    date_run = Run(observing_day, "eod")

    logger.info(f"starting pipeline on {observing_day}...")
    logger.info(f"pipeline version {__version__} [{__revision__}]")

    start_dt = datetime.datetime.now()

    if reprocessing:
        try:
            clearday(date_run)
        except DatabaseError as e:
            logger.error("error clearing database...")
            logger.error(e)

    date_run.catalog = run_inventory(date_run, skip=False)

    date_run.calibration = Calibration(date_run.catalog)

    cal_dir = get_option("process", "caldir")
    if cal_dir is not None:
        if not os.path.isdir(cal_dir):
            os.mkdir(cal_dir)

        cal_basename = date_run.calibration.basename
        cal_filename = os.path.join(cal_dir, cal_basename)
        date_run.calibration.save_file(cal_filename)
        logger.info(f"wrote {cal_basename}")
    else:
        logger.warning("process.caldir not set, not writing cal file")

    process_l1(date_run, skip=not get_option("level1", "process"))
    write_quality_files(date_run.catalog, date_run.observing_day)

    process_l2(date_run, skip=not get_option("level2", "process"))

    publish_levels = {"level1": publish_l1, "level2": publish_l2, "level3": publish_l3}
    for level, publish_routine in publish_levels.items():
        if get_option(level, "publish"):
            publish_routine(date_run)

    try:
        insert_files(date_run, date_run.catalog)
    except DatabaseError as e:
        logger.error("error updating database...")
        logger.error(e)

    if not reprocessing:
        archive_l0(date_run)
    archive_l1(date_run)
    archive_l2(date_run)

    end_dt = datetime.datetime.now()
    time_interval = end_dt - start_dt
    human_time = human_timedelta(time_interval)
    logger.info(f"done: {human_time}")

    return date_run
