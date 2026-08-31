# -*- coding: utf-8 -*-

"""Create and handle process and reprocess sub-commands.
"""

import os
import sys

from .helper import add_run_arguments, split_dates

from ..config import read_config, get_basedir
from ..logging import logger
from ..notifications import notify_process
from ..pipeline import LockException, RunLock
from ..process import run, clearday


def handle_process(args):
    """Main routine to handle keyword arguments and dispatch the processing
    work from either the process or reprocess subcommand. The "reprocessing"
    attribute of `args` is set when creating the argument parsers to the
    appropriate value and passed on to `run` routine.

    System status code is the number of failing date.
    """
    subcommand = "reprocess" if args.reprocessing else "process"
    dates = split_dates(",".join(args.dates), args.parser.error)

    if not os.path.isfile(args.configuration_filename):
        args.parser.exit(
            1, f"configuration file not found: {args.configuration_filename}"
        )

    read_config(args.configuration_filename)

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
            print(f"processing directory for {d} locked, skipping")
            exit_code += 1
        except Exception as e:
            logger.critical(e, exc_info=True)
            print(
                f"chromag {subcommand} command failed, see log for details",
                file=sys.stderr,
            )
            exit_code += 1

        notify_process(d, date_run, subcommand)

    sys.exit(exit_code)


def add_process_subcommand(subparsers):
    """Add process and reprocess subcommands to the argparse subparsers."""
    parser = subparsers.add_parser("process", help="run pipeline on the given dates")
    add_run_arguments(parser)
    parser.set_defaults(func=handle_process, parser=parser, reprocessing=False)

    parser = subparsers.add_parser("reprocess", help="reprocess the given dates")
    add_run_arguments(parser)
    parser.set_defaults(func=handle_process, parser=parser, reprocessing=True)
