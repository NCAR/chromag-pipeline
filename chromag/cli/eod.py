# -*- coding: utf-8 -*-

"""Create and handle end-of-day (eod) and reprocess sub-commands.
"""

import os
import sys

from .helper import add_run_arguments, split_dates
from ..eod import run, clearday
from ..logging import logger


def process_eod(args):
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

    for d in dates:
        try:
            run(d, args.configuration_filename, reprocessing=False)
        except Exception as e:
            logger.exception("uncaught exception in end")
            logger.critical(e)
            print(
                "chromag eod: eod command failed, see log for details", file=sys.stderr
            )
            sys.exit(1)


def process_reprocess(args):
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

    for d in dates:
        try:
            run(d, args.configuration_filename, reprocessing=True)
        except Exception as e:
            logger.exception("uncaught exception in reprocess")
            logger.critical(e)
            print(
                "chromag reprocess: reprocess command failed, see log for details",
                file=sys.stderr,
            )
            sys.exit(1)


def add_eod_subcommand(subparsers):
    """Add end-of-day (eod) and reprocess subcommands to the argparse subparsers."""
    parser = subparsers.add_parser(
        "end-of-day", aliases=["eod"], help="run end-of-day pipeline on the given dates"
    )
    add_run_arguments(parser)
    parser.set_defaults(func=process_eod, parser=parser)

    parser = subparsers.add_parser("reprocess", help="reprocess the given dates")
    add_run_arguments(parser)
    parser.set_defaults(func=process_reprocess, parser=parser)
