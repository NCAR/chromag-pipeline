# -*- coding: utf-8 -*-

"""Utilities for handling sub-commands for command line utilities.
"""

import argparse

from .. import __version__
from .. import __revision__

from .archive import add_archive_subcommand
from .cat import add_cat_subcommand
from .clearday import add_clearday_subcommand
from .createdb import add_createdb_subcommand
from .log import add_log_subcommand
from .ls import add_ls_subcommand
from .process import add_process_subcommand
from .ps import add_ps_subcommand
from .versions import add_versions_subcommand


def print_help(args):
    """Print the CLI help."""
    args.parser.print_help()


def setup():
    name = f"ChroMag pipeline {__version__} [{__revision__}]"
    # [TODO]: add suggest_on_error=True when we upgrade to Python 3.15
    parser = argparse.ArgumentParser(description=name)

    # top-level options
    parser.add_argument("-v", "--version", action="version", version=name)

    # show help if no sub-command given
    parser.set_defaults(func=print_help, parser=parser)

    subparsers = parser.add_subparsers(help="sub-command help")

    # helpers: archive, cat, clearday, createdb, ls, log, ps, versions
    add_archive_subcommand(subparsers)
    add_cat_subcommand(subparsers)
    add_clearday_subcommand(subparsers)
    add_createdb_subcommand(subparsers)
    add_log_subcommand(subparsers)
    add_ls_subcommand(subparsers)
    add_ps_subcommand(subparsers)
    add_versions_subcommand(subparsers)

    # processing: process, reprocess, realtime (rt), end-of-day (eod), cal
    add_process_subcommand(subparsers)

    # testing: regress, simulate, validate

    # etc: script

    # parse args and call appropriate sub-command
    return parser


def main():
    """Entry point for chromag command-line interface (CLI)."""
    try:
        parser = setup()

        args = parser.parse_args()
        if parser.get_default("func"):
            args.func(args)
        else:
            parser.print_help()
    except KeyboardInterrupt as e:
        print()
