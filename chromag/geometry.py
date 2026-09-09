# -*- coding: utf-8 -*-

"""Module containing routines for geometry related task such as masking.
"""

import datetime
from typing import TypeVar

import numpy as np

from . import MISSION_START

from .epochs import get_epochvalue

DateValue = TypeVar("DateValue", str, datetime.datetime)


def distance_array(dims: tuple, center: tuple = None):
    """Create array of distance to the center point. If not given the center is
    assumed to be the center of the array, i.e., for an array with dimensions
    given by `dim`, this is `((dims[0] - 1) / 2, (dims[1] - 1) / 2)`."""
    if center is None:
        center = ((dims[0] - 1) / 2, (dims[1] - 1) / 2)

    # create read-only views of the x and y values
    x = np.broadcast_to(np.arange(dims[0]) - center[0], reversed(dims)).T
    y = np.broadcast_to(np.arange(dims[1]) - center[1], dims)
    d = np.sqrt(x * x + y * y)
    return d


def field_mask(
    field_radius: float, /, *, center: tuple = None, date: DateValue | None = None
) -> np.ndarray:
    """Mask out the far field of a given radius."""
    dims = tuple(get_epochvalue("dimensions", MISSION_START if date is None else date))
    return distance_array(dims, center) < field_radius


def mask(
    field_radius: float,
    /,
    *,
    center: tuple = None,
    date: DateValue | None = None,
) -> np.ndarray:
    """Mask out the occulter and far field."""
    fmask = field_mask(field_radius, center=center, date=date)
    return fmask  # & other masks
