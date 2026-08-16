# -*- coding: utf-8 -*-

"""Create and handle clearday sub-command.
"""

from configparser import NoSectionError
import datetime
import os

from .helper import add_run_arguments, split_dates

from .. import __version__, __revision__
from ..config import read_config, get_option
from ..datetime import human_timedelta
from ..eod import clearday
from ..logging import get_level, setup_logging
from ..pipeline import Run


def handle_clearday(args):
    """Main routine to handle keyword arguments and dispatch the work.

    System status code is 0 for a valid run, 1 if configuration file is not
    found.
    """
    dates = split_dates(",".join(args.dates), args.parser.error)

    if not os.path.isfile(args.configuration_filename):
        args.parser.error(
            f"configuration file not found: {args.configuration_filename}"
        )
        sys.exit(1)

    read_config(args.configuration_filename)

    log_basedir = get_option("logging", "basedir")
    log_level = get_level(get_option("logging", "level"))
    rotate = get_option("logging", "rotate")
    max_version = get_option("logging", "max_version")

    for d in dates:
        log_filename = os.path.join(log_basedir, f"{d}.chromag.eod.log")
        logger = setup_logging(
            log_filename, level=log_level, rotate=rotate, max_version=max_version
        )
        date_run = Run(d, "eod", logger)
        logger.info(f"clearing results for on {d}...")
        logger.info(f"pipeline version {__version__} [{__revision__}]")
        start_dt = datetime.datetime.now()

        clearday(date_run)

        human_time = human_timedelta(datetime.datetime.now() - start_dt)
        logger.info(f"done: {human_time}")


def add_clearday_subcommand(subparsers):
    """Add clearday subcommand to the argparse subparsers."""
    clearday_parser = subparsers.add_parser(
        "clearday", help="clear results for the given date(s)"
    )
    add_run_arguments(clearday_parser)  # -f and dates
    clearday_parser.set_defaults(func=handle_clearday, parser=clearday_parser)
