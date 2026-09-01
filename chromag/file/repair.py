# -*- coding: utf-8 -*-

"""Module for repairing raw data in epochs with known issues."""

from inspect import isclass

from astropy.io import fits
import numpy as np

from .file import ChroMagRawFile
from ..logging import logger


# ---- header repair routine ----


def null_header(header: fits.header.Header):
    """Example repair routine that doesn't do anything."""
    return header


# ---- data repair routines ----


def null_data(data: np.ndarray):
    """Example repair routine that doesn't do anything."""
    return data


# ---- main routine ----


def repair(item: np.ndarray | fits.header.Header, routines: list[str] = None):
    """Repair the given data by calling the given list of names of repair
    routines that are in this module."""
    repair_routines = {
        name: object
        for name, object in globals().items()
        if callable(object) and not isclass(object) and object not in exclude
    }
    if routines is not None:
        for r in routines:
            repair_routines[r](item)


exclude = [repair, isclass]
