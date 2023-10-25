# -*- coding: utf-8 -*-

"""Utilities for handling sub-commands for command line utilities.
"""

import argparse

from .. import __version__

from .cat import add_cat_subcommand
from .eod import add_eod_subcommand
from .log import add_log_subcommand
from .ls import add_ls_subcommand


def print_help(args):
    """ "Print the CLI help."""
    args.parser.print_help()


def main():
    """Entry point for chromag CLI."""
    name = f"ChroMag pipeline {__version__}"
    parser = argparse.ArgumentParser(description=name)

    # top-level options
    parser.add_argument("-v", "--version", action="version", version=name)

    # show help if no sub-command given
    parser.set_defaults(func=print_help, parser=parser)

    subparsers = parser.add_subparsers(help="sub-command help")

    # helpers: cat, list, ls, log, versions
    add_cat_subcommand(subparsers)
    add_log_subcommand(subparsers)
    add_ls_subcommand(subparsers)

    # processing: rt, eod, cal, reprocess
    add_eod_subcommand(subparsers)

    # clearday, archive

    # testing: regress, simulate, validate

    # etc: script

    # parse args and call appropriate sub-command
    args = parser.parse_args()
    if parser.get_default("func"):
        args.func(args)
    else:
        parser.print_help()
