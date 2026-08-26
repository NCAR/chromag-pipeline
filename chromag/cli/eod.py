# -*- coding: utf-8 -*-

"""Create and handle end-of-day (eod) and reprocess sub-commands.
"""

import os
import sys

from .helper import add_run_arguments, split_dates

from ..config import read_config, get_basedir
from ..eod import run, clearday
from ..logging import logger
from ..notifications import notify_eod
from ..pipeline import LockException, RunLock


def process_eod(args):
    """Main routine to handle keyword arguments and dispatch the end-of-day
    work. The "reprocessing" attribute of `args` is set when creating the
    argument parsers to the appropriate value and passed on to `run` routine.

    System status code is the number of failing date.
    """
    dates = split_dates(",".join(args.dates), args.parser.error)

    if not os.path.isfile(args.configuration_filename):
        args.parser.error(
            f"configuration file not found: {args.configuration_filename}"
        )
        sys.exit(1)

    read_config(args.configuration_filename)

    subcommand = "reprocess" if args.reprocessing else "eod"
    exit_code = 0
    date_run = None
    for d in dates:
        try:
            lock_filename = os.path.join(get_basedir(d, "process"), d, ".lock")
            with RunLock(lock_filename) as lock:
                date_run = run(
                    d, args.configuration_filename, reprocessing=args.reprocessing
                )
        except LockException as e:
            print(
                f"chromag {subcommand}: processing directory for {d} locked, skipping"
            )
            exit_code += 1
        except Exception as e:
            logger.critical(e, exc_info=True)
            print(
                f"chromag {subcommand}: {subcommand} command failed, see log for details",
                file=sys.stderr,
            )
            exit_code += 1

        notify_eod(d, date_run)

    sys.exit(exit_code)


def add_eod_subcommand(subparsers):
    """Add end-of-day (eod) and reprocess subcommands to the argparse subparsers."""
    parser = subparsers.add_parser(
        "end-of-day", aliases=["eod"], help="run end-of-day pipeline on the given dates"
    )
    add_run_arguments(parser)
    parser.set_defaults(func=process_eod, parser=parser, reprocessing=False)

    parser = subparsers.add_parser("reprocess", help="reprocess the given dates")
    add_run_arguments(parser)
    parser.set_defaults(func=process_eod, parser=parser, reprocessing=True)
