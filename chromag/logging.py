# -*- coding: utf-8 -*-

"""Module containing helper functions for logging.
"""

import glob
import logging
import os


logger = logging.getLogger()

LEVELS = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARN": logging.WARN,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG}


def rotate_logs(basename, max_version=None):
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

    versions = [int(f[n + 1:]) for f in files if f[n + 1:].isdigit()]
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


def get_level(level_name):
    """Convert a string name to a logging level constant value.

       level_name : str
         case insensitive level name
    """
    return LEVELS[level_name.upper()]


class WrappedFormatter(logging.Formatter):
    """Custom formatter, overrides funcName with value of funcName_override if
       it exists.
    """
    def format(self, record):
        if hasattr(record, "func"):
            record.funcName = record.func.__name__
        return super(WrappedFormatter, self).format(record)


def setup_logging(filename,
                  level=logging.DEBUG,
                  rotate=False,
                  max_version=None):
    if rotate:
        rotate_logs(filename, max_version=max_version)

    handler = logging.FileHandler(filename)
    logger.addHandler(handler)

    fmt = "%(asctime)s %(funcName)s: %(levelname)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    formatter = WrappedFormatter(fmt, datefmt=datefmt)
    handler.setFormatter(formatter)

    logger.setLevel(level)

    return(logger)