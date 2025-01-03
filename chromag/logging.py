# -*- coding: utf-8 -*-

"""Module containing helper functions for logging.
"""

import glob
import logging
import os
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

DATE_FORMAT = "%Y%m%d.%H%M%S"


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
        print(type(record))
        if hasattr(record, "func"):
            record.funcName = record.func.__name__
        return super(WrappedFormatter, self).format(record)


def setup_logging(
    filename: str,
    level: int = logging.DEBUG,
    rotate: bool = True,
    max_version: Optional[int] = None,
) -> logging.Logger:
    """Configure the logging system."""
    log_dirname = os.path.dirname(filename)
    if not os.path.exists(log_dirname):
        os.makedirs(log_dirname)

    if rotate:
        rotate_logs(filename, max_version=max_version)

    logger.handlers = []
    handler = logging.FileHandler(filename)
    logger.addHandler(handler)

    fmt = "%(asctime)s %(funcName)s: %(levelname)s: %(message)s"
    formatter = WrappedFormatter(fmt, datefmt=DATE_FORMAT)
    handler.setFormatter(formatter)

    logger.setLevel(level)

    return logger
