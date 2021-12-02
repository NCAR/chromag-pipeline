# -*- coding: utf-8 -*-

"""Utilities for handling sub-commands for command line utilities.
"""

import argparse

from .. import __version__
from .log import add_log_subcommand
from .ls import add_ls_subcommand
from .eod import add_eod_subcommand


def print_help(args):
    args.parser.print_help()


def main():
    name = f"ChroMag pipeline {__version__}"
    parser = argparse.ArgumentParser(description=name)

    # top-level options
    parser.add_argument("-v", "--version",
                        action="version",
                        version=name)
    
    # show help if no sub-command given
    parser.set_defaults(func=print_help, parser=parser)

    # TODO: it would be nice to group sub-commands into groups, but that is not
    # possible with argparse right now
    # helpers: list, ls, log, versions
    # processing: rt, eod, cal, reprocess
    # clearday, archive
    # testing: regress, simulate, validate
    # etc: script
    subparsers = parser.add_subparsers(help="sub-command help")

    add_ls_subcommand(subparsers)
    add_log_subcommand(subparsers)
    add_eod_subcommand(subparsers)

    # parse args and call appropriate sub-command
    args = parser.parse_args()
    if parser.get_default("func"):
        args.func(args)
    else:
        parser.print_help()
