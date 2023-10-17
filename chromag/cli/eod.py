# -*- coding: utf-8 -*-

"""Create and handle end-of-day (eod) sub-command.
"""

import os

from .helper import add_run_arguments, split_dates
from ..eod import run


def process_eod(args):
    config_basename = args.configuration_filename
    dates = split_dates(",".join(args.dates), args.parser.error)
    for d in dates:
        run(d, args.configuration_filename)


def add_eod_subcommand(subparsers):
    parser = subparsers.add_parser("end-of-day", aliases=["eod"],
        help="run end-of-day pipeline")
    add_run_arguments(parser)
    parser.set_defaults(func=process_eod, parser=parser)