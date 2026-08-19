# -*- coding: utf-8 -*-


""" Create and handle log sub-command.
"""

import collections
import datetime
import glob
import os
import re
import time

import rich

from ..logging import DATE_FORMAT as LOG_DATE_FORMAT

POLL_SECS = 0.1
LEVELS = ["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"]


def print_bold(text: str):
    rich.print(f"[bold magenta]{text}[/]")
    # rich.print(f"[bold red]{text}[/]")


def bold(text: str):
    return f"[bold magenta]{text}[/]"
    # return f"[bold red]{text}[/]"


def prune_logfiles(files, max_version):
    """Delete files with a version after them that is larger than max_version.
    For example, `test.log.10` would be deleted if `max_version` is 9.
    """
    version_re = re.compile(r"\d+")
    for f in files:
        versions = glob.glob(f"{f}.*")
        for v in versions:
            n = v[len(f) + 1 :]
            if version_re.match(n):
                if int(n) > max_version:
                    file_to_delete = f"{f}.{n}"
                    os.remove(file_to_delete)


def begins_with_date(line, fmt):
    """Determine if a line starts with a date of the given format."""
    # use current date/time to determine the length of a date/time with the
    # given format
    dt_length = len(datetime.datetime.now().strftime(fmt))

    try:
        dt = datetime.datetime.strptime(line[0:dt_length], fmt)
        return dt is not None
    except ValueError:
        return False


def filter_file(logfile, level_index, follow, tail, error_writer):
    """Filter a given log file at the given level (DEBUG, INFO, WARN, ERROR,
    or CRITICAL). Optionally, "follow" the log file, i.e., continuously
    wait for new lines to be added to the log file and filter them.
    """
    loglevel_filter = "|".join(LEVELS[level_index:])
    loglevel_prog = re.compile(f".*({loglevel_filter}):.*")
    logstart_prog = re.compile(r"(\[\d+\] )?\d{8}.\d{6}")
    exact_loglevel_prog = re.compile(f".*{LEVELS[level_index]}:.*")

    matched_last_line = False
    exact_matched_last_line = False

    line = "not empty"

    if tail is not None:
        queue = collections.deque(maxlen=tail)

    try:
        with open(logfile, "r") as f:
            try:
                while follow or line != "":
                    line = f.readline()
                    if line == "":
                        try:
                            time.sleep(POLL_SECS)
                        except IOError:
                            return
                        continue

                    if loglevel_prog.match(line):
                        matched_last_line = True
                        exact_matched_last_line = (
                            True if exact_loglevel_prog.match(line) else False
                        )
                        try:
                            if tail is None:
                                if exact_matched_last_line:
                                    print(line.rstrip())
                                else:
                                    print_bold(line.rstrip())
                            else:
                                if exact_matched_last_line:
                                    queue.append(line.rstrip())
                                else:
                                    queue.append(bold(line.rstrip()))
                        except IOError:
                            return
                    else:
                        if matched_last_line:
                            if begins_with_date(line, LOG_DATE_FORMAT):
                                matched_last_line = False
                            else:
                                try:
                                    if tail is None:
                                        print(line.rstrip())
                                    else:
                                        queue.append(line.rstrip())
                                except IOError:
                                    return
            except KeyboardInterrupt:
                print()
                return
    except IOError:
        error_writer("Problem reading %s" % logfile)

    if tail is not None:
        for line in queue:
            if line.startswith("["):
                rich.print(line)
            else:
                print(line)


def log_subcommand(args):
    """Main routine to handle keyword arguments and dispatch the work."""
    date_prog = re.compile(r"^\d{8}$")

    logfiles = []
    for f in args.logfiles:
        logfiles.append(f)

    follow = args.follow
    if follow and len(args.logfiles) > 1:
        args.parser.error("cannot follow multiple files")

    if args.prune is not None:
        prune_logfiles(args.logfiles, int(args.prune))
        return

    # default is to not filter
    if args.level:
        level = args.level.upper()
    elif args.critical:
        level = "CRITICAL"
    elif args.error:
        level = "ERROR"
    elif args.warn:
        level = "WARN"
    elif args.info:
        level = "INFO"
    else:
        level = "DEBUG"

    try:
        level_index = LEVELS.index(level)
    except ValueError:
        args.parser.error(f"invalid level: {level}")

    for i, f in enumerate(args.logfiles):
        if len(args.logfiles) > 1:
            if i != 0:
                print("")
            print(f)
            print("-" * len(f))
        filter_file(f, level_index, follow, args.tail, args.parser.error)


def add_log_subcommand(subparsers):
    """Add log subcommand to the argparse subparsers."""
    log_parser = subparsers.add_parser(
        "log",
        help="display, and optionally filter, log output from the ChroMag pipeline",
    )
    log_parser.add_argument(
        "logfiles", nargs="+", help="UCoMP log filename or date", metavar="logfile"
    )
    level_help = "filter level: DEBUG INFO WARN ERROR CRITICAL (default DEBUG)"
    log_parser.add_argument("-l", "--level", help=level_help)
    prune_help = "delete rotated logs with versions higher than MAX_VERSION"
    log_parser.add_argument("-p", "--prune", help=prune_help, metavar="MAX_VERSION")
    log_parser.add_argument(
        "-f", "--follow", help="output appended data as file grows", action="store_true"
    )
    log_parser.add_argument(
        "-t",
        "--tail",
        type=int,
        metavar="N",
        help="show the last N lines of the log at the otherwise given level",
    )
    log_parser.add_argument(
        "-d", "--debug", help="DEBUG filter level", action="store_true"
    )
    log_parser.add_argument(
        "-i", "--info", help="INFO filter level", action="store_true"
    )
    log_parser.add_argument(
        "-w", "--warn", help="WARN filter level", action="store_true"
    )
    log_parser.add_argument(
        "-e", "--error", help="ERROR filter level", action="store_true"
    )
    log_parser.add_argument(
        "-c", "--critical", help="CRITICAL filter level", action="store_true"
    )
    log_parser.set_defaults(func=log_subcommand, parser=log_parser)
