# -*- coding: utf-8 -*-

"""Create and handle archive sub-command.
"""

from configparser import NoSectionError
import datetime
import os

from .helper import add_run_arguments, split_dates

from .. import __version__, __revision__
from ..archive import archive_l0, archive_l1, archive_l2
from ..config import read_config, get_option
from ..datetime import human_timedelta
from ..logging import get_level, setup_logging
from ..pipeline import Run


def handle_archive(args):
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

    archive_level = args.level

    archive_routine = {"0": archive_l0, "1": archive_l1, "2": archive_l2}

    for d in dates:
        log_filename = os.path.join(log_basedir, f"{d}.chromag.eod.log")
        logger = setup_logging(
            log_filename, level=log_level, rotate=rotate, max_version=max_version
        )
        date_run = Run(d, "eod", logger)
        logger.info(f"archiving level {archive_level} data on {d}...")
        logger.info(f"pipeline version {__version__} [{__revision__}]")
        start_dt = datetime.datetime.now()

        archive_routine[archive_level](date_run)

        human_time = human_timedelta(datetime.datetime.now() - start_dt)
        logger.info(f"done: {human_time}")


def add_archive_subcommand(subparsers):
    """Add archive subcommand to the argparse subparsers."""
    archive_parser = subparsers.add_parser(
        "archive", help="archive data of the given level and dates"
    )
    add_run_arguments(archive_parser)  # -f and dates
    archive_parser.add_argument(
        "-l", "--level", type=str, default=None, help="level to archive: 0, 1, 2, or 3"
    )
    archive_parser.set_defaults(func=handle_archive, parser=archive_parser)
