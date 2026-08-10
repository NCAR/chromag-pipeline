# -*- coding: utf-8 -*-

"""Create and handle createdb sub-command.
"""

from configparser import NoSectionError
import os

from ..config import read_config, get_option
from ..database import initialize_tables, DatabaseConnectionError
from ..logging import setup_logging, get_level


def process_createdb(args):
    """Main routine to handle keyword arguments and dispatch the work.

    System status code is 0 for a valid run, 1 if configuration file is not
    found.
    """
    if not os.path.isfile(args.configuration_filename):
        args.parser.error(
            f"configuration file not found: {args.configuration_filename}"
        )
        sys.exit(1)

    read_config(args.configuration_filename)

    level = get_level(get_option("logging", "level"))
    logger = setup_logging(None, level=level)

    if get_option("database", "update"):
        config_filename = get_option("database", "config_filename")
        config_section = get_option("database", "config_section")
        try:
            initialize_tables(config_filename, config_section)
        except FileNotFoundError as e:
            args.parser.error(f"file {config_filename} not found")
        except NoSectionError as e:
            args.parser.error(f"section {config_section} not found in config file")
        except DatabaseConnectionError as e:
            args.parser.error(e)


def add_createdb_subcommand(subparsers):
    """Add createdb subcommand to the argparse subparsers."""
    createdb_parser = subparsers.add_parser(
        "createdb", help="create the ChroMag database tables"
    )
    flags_help = """Configuration filename"""
    createdb_parser.add_argument(
        "-f", "--configuration-filename", type=str, help=flags_help, default=None
    )
    createdb_parser.set_defaults(func=process_createdb, parser=createdb_parser)
