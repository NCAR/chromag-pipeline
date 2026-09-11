# -*- coding: utf-8 -*-

"""Create and handle control sub-command.
"""

import sys

from ..config import read_config
from ..control import is_running, set_running, set_stopped


def control_subcommand(args):
    """Handle control subcommand starting, stopping, and checking status."""
    if args.start and args.stop:
        args.parser.error("cannot set both --start and --stop")

    found, is_valid = read_config(args.configuration_filename)
    if not found:
        args.parser.error(
            f"configuration file not found: {args.configuration_filename}"
        )
    if not is_valid:
        args.parser.error(
            f"configuration file not valid: {args.configuration_filename}"
        )

    state_changed = False

    if args.start:
        state_changed = set_running()

    if args.stop:
        state_changed = set_stopped()

    state_changed = "changed" if state_changed else "not changed"

    running = is_running()
    if args.verbose:
        state = "running" if running else "stopped"
        print(f"state {state_changed}: processes are {state}")

    sys.exit(0 if running else 1)


def add_control_subcommand(subparsers):
    """Add control subcommand to the argparse subparsers."""
    control_parser = subparsers.add_parser(
        "control", help="start/stop processing of multiple dates"
    )
    control_parser.add_argument(
        "-f",
        "--configuration-filename",
        type=str,
        help="configuration filename",
        default=None,
    )
    control_parser.add_argument(
        "--start", help="set to allow dates to be processed", action="store_true"
    )
    control_parser.add_argument(
        "--stop", help="set to stop allowing dates to be processed", action="store_true"
    )
    control_parser.add_argument(
        "-v", "--verbose", help="set to print processing state", action="store_true"
    )
    control_parser.set_defaults(func=control_subcommand, parser=control_parser)
