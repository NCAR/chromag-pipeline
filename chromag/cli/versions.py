# -*- coding: utf-8 -*-

"""Create and handle versions sub-command, which looks up the processing for
specified dates.
"""

from contextlib import closing
import datetime
import os

from .helper import add_run_arguments, split_dates

from .. import MISSION_START
from ..config import read_config, get_option
from ..datetime import short2hyphenated
from ..database import DatabaseError, get_connection


versions_query = """
select chromag_sw.version, chromag_sw.revision, date_processed
from chromag_process
inner join mlso_numfiles on obsday_id=mlso_numfiles.day_id
inner join chromag_sw on chromag_sw_id=chromag_sw.sw_id
where mlso_numfiles.obs_day="{obs_day}" limit 1;
"""

processing_query = """
select hostname, mlso_numfiles.obs_day, chromag_sw.version
from chromag_process
inner join mlso_numfiles on obsday_id=mlso_numfiles.day_id
inner join chromag_sw on chromag_sw_id=chromag_sw.sw_id
where status="processing";
"""


def handle_processing(cursor):
    cursor.execute(processing_query)
    processing_result = cursor.fetchall()
    if processing_result is None:
        return
    for r in processing_result:
        d = r[1].strftime("%Y%m%d")
        print(f"{d}: {r[0]} [{r[2]}]")


def handle_versions(args):
    """Main routine to handle keyword arguments and dispatch the work.

    System status code is 0 for a valid run, 1 if configuration file is not
    found.
    """
    if not os.path.isfile(args.configuration_filename):
        args.parser.error(
            f"configuration file not found: {args.configuration_filename}"
        )

    read_config(args.configuration_filename)

    db_config_filename = get_option("database", "config_filename")
    db_config_section = get_option("database", "config_section")

    with closing(get_connection(db_config_filename, db_config_section)) as connection:
        with closing(connection.cursor()) as cursor:
            try:
                if args.processing:
                    handle_processing(cursor)
                else:
                    date_expr = ",".join(args.dates).strip(" ")
                    if date_expr == "":
                        mission_start = datetime.datetime.strptime(
                            MISSION_START, "%Y-%m-%d"
                        ).strftime("%Y%m%d")
                        tomorrow = (
                            datetime.datetime.now() + datetime.timedelta(days=1)
                        ).strftime("%Y%m%d")
                        date_expr = f"{mission_start}-{tomorrow}"
                    dates = split_dates(date_expr, args.parser.error)

                    for d in dates:
                        obs_day = short2hyphenated(d)
                        cursor.execute(versions_query.format(obs_day=obs_day))
                        versions_result = cursor.fetchone()
                        if versions_result is None:
                            continue
                        output = f"{d}: {versions_result[0]}"
                        if args.verbose:
                            output += f" [{versions_result[1]}, {versions_result[2]:%Y-%m-%dT%H:%M:%S}]"
                        print(output)
            except DatabaseError as e:
                args.parser.error(e)
            except Exception as e:
                args.parser.error(e)


def add_versions_subcommand(subparsers):
    """Add versions subcommand to the argparse subparsers."""
    versions_parser = subparsers.add_parser(
        "versions", help="find versions for the given date(s)"
    )
    versions_parser.add_argument(
        "-v", "--verbose", help="set to show full output", action="store_true"
    )
    versions_parser.add_argument(
        "--processing",
        help="set to show dates that are currently processing",
        action="store_true",
    )
    add_run_arguments(versions_parser)  # -f and dates
    versions_parser.set_defaults(func=handle_versions, parser=versions_parser)
