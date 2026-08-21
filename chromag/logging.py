# -*- coding: utf-8 -*-

"""Module containing helper functions for logging.

Notes about which logging level to use:

  - Use CRITICAL only when the pipeline is crashing.
  - Use ERROR for reporting on problems with the pipeline, e.g., the database
    was unreachable, a file couldn't be deleted/read/written, or some other
    internal infrastructure problem.
  - Use WARN for reporting on conditions that are unexpected, a problem in the
    data.
  - Use INFO for top-level steps of the pipeline.
  - Use DEBUG for anything else.
  - The overall principle is that if you filter on INFO messages that you
    should get a basic idea of what is happening and the big problems should
    stand out with higher level messages. Read the full log to get the details
    about a single operations.

A note on style:

  - Use "..." at the end of messages that are starting a process, e.g.,
    "processing f...", while messages like "processed f" after the process has
    been completed.
"""

import datetime
import glob
import logging
import os
import re
from typing import Optional


logger = logging.getLogger("ChroMag")

LEVELS = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARN": logging.WARN,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}
LEVEL_NAMES = ["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"]

DATE_FORMAT = "%Y%m%d.%H%M%S"


def null_logger_func(msg, **extra):
    """Function that takes the same arguments as logger.info, etc., but does
    nothing.
    """
    pass


class FileHandler(logging.FileHandler):
    """A subclass of the standard logging FileHandler that makes sure to write
    each log message to disk before moving on.
    """

    def flush(self):
        if self.stream and hasattr(self.stream, "flush"):
            self.stream.flush()

    def emit(self, record):
        super().emit(record)
        self.flush()
        os.fsync(self.stream.fileno())


def rotate_logs(basename: str, max_version: Optional[int] = None):
    """Rotate logs to allow a new log to be written as basename. If
    max_version is given, delete logs with given basename and versions
    beyond the max_version.

    Note: no rotating or pruning done if basename doesn't already exist.

    basename : str
      log base filename, i.e., without a ".x"
    max_version : int
      largest allowable version, set to 0 not keep any versions
    """

    # nothing to do if the basename doesn't already exist
    if not os.path.isfile(basename):
        return

    files = glob.glob(f"{basename}.*")
    n = len(basename)

    versions = [int(f[n + 1 :]) for f in files if f[n + 1 :].isdigit()]
    sorted_versions = sorted(versions, reverse=True)

    for v in sorted_versions:
        if max_version is not None and v >= max_version:
            os.remove(f"{basename}.{v}")
        else:
            os.rename(f"{basename}.{v}", f"{basename}.{v+1}")

    # move original if space
    if max_version is not None and max_version == 0:
        os.remove(basename)
    else:
        os.rename(basename, f"{basename}.1")


def get_level(level_name: str):
    """Convert a string name to a logging level constant value.

    level_name : str
      case insensitive level name: CRITICAL, ERROR, WARN, WARNING, INFO, DEBUG
    """
    return LEVELS[level_name.upper()]


class WrappedFormatter(logging.Formatter):
    """Custom formatter, overrides funcName with value of funcName_override if
    it exists.
    """

    def format(self, record: logging.LogRecord):
        if hasattr(record, "func"):
            record.funcName = record.func.__name__
        return super(WrappedFormatter, self).format(record)


def setup_logging(
    filename: str | None,
    level: int = logging.DEBUG,
    rotate: bool = True,
    max_version: Optional[int] = None,
) -> logging.Logger:
    """Configure the logging system."""
    if filename is not None:
        log_dirname = os.path.dirname(filename)
        if not os.path.exists(log_dirname):
            os.makedirs(log_dirname)

        if rotate:
            rotate_logs(filename, max_version=max_version)

    logger.handlers = []

    if filename is None:
        handler = logging.StreamHandler()
        logger.addHandler(handler)
    else:
        handler = FileHandler(filename)
        logger.addHandler(handler)

    fmt = "%(asctime)s %(funcName)s: %(levelname)s: %(message)s"
    formatter = WrappedFormatter(fmt, datefmt=DATE_FORMAT)
    handler.setFormatter(formatter)

    logger.setLevel(level)

    return logger


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


def filter_log(logfile: str, level_index: int):
    """Filter a given log file at the given level (DEBUG, INFO, WARN, ERROR,
    or CRITICAL).
    """
    loglevel_filter = "|".join(LEVEL_NAMES[level_index:])
    loglevel_prog = re.compile(f".*({loglevel_filter}):.*")
    logstart_prog = re.compile(r"(\[\d+\] )?\d{8}.\d{6}")

    matched_last_line = False

    results = []

    try:
        with open(logfile, "r") as f:
            for line in f:
                if loglevel_prog.match(line):
                    matched_last_line = True
                    results.append(line.rstrip())
                else:
                    if matched_last_line:
                        if begins_with_date(line, DATE_FORMAT):
                            matched_last_line = False
                        else:
                            results.append(line.rstrip())
    except IOError:
        logger.warn("problem reading {logfile}")

    return "\n".join(results)
