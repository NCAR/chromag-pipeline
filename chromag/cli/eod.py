# -*- coding: utf-8 -*-

"""Create and handle end-of-day (eod) sub-command.
"""

import os
import sys

from .helper import add_run_arguments, split_dates
from ..eod import run, clearday


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
        run(d, args.configuration_filename, reprocessing=False)


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
        run(d, args.configuration_filename, reprocessing=True)


def add_eod_subcommand(subparsers):
    """Add end-of-day (eod) subcommand to the argparse subparsers."""
    parser = subparsers.add_parser(
        "end-of-day", aliases=["eod"], help="run end-of-day pipeline"
    )
    add_run_arguments(parser)
    parser.set_defaults(func=process_eod, parser=parser)

    parser = subparsers.add_parser(
        "reprocess", help="clear output for day and run end-of-day pipeline"
    )
    add_run_arguments(parser)
    parser.set_defaults(func=process_reprocess, parser=parser)
