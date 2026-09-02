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


def fake_sgs(header: fits.header.Header):
    """Header repair that inserts synthetic SGS values into the header. Useful
    for testing when no real SGS values are available."""
    import math
    import random
    from ..datetime import dateobs2datetime, obsday_hours
    from .file import FormattedFloat

    logger.warn("setting fake SGS values")
    dt = dateobs2datetime(header["DATE-OBS"])
    ohrs = obsday_hours(dt)

    header["SGSDIMV"] = FormattedFloat(
        8.0 / (1.0 + math.exp(-(ohrs - 6.0))) + random.gauss(0.0, 0.1), "0.3f"
    )
    header["SGSDIMS"] = FormattedFloat(
        0.00125 * (ohrs - 6.0) + 0.01 + random.gauss(0.0, 0.005), "%0.3f"
    )
    header["SGSSUMV"] = FormattedFloat(
        8.0 / (1.0 + math.exp(-(ohrs - 6.0))) + random.gauss(0.0, 0.1), "0.3f"
    )
    header["SGSSUMS"] = FormattedFloat(
        0.00125 * (ohrs - 6.0) + 0.01 + random.gauss(0.0, 0.005), "%0.3f"
    )
    header["SGSRAV"] = FormattedFloat(0.999 + random.gauss(0.0, 0.001), "%0.3f")
    header["SGSRAS"] = FormattedFloat(
        0.0025 * (ohrs - 6.0) + 0.01 + random.gauss(0.0, 0.005), "%0.3f"
    )
    header["SGSDECV"] = FormattedFloat(0.999 + random.gauss(0.0, 0.001), "%0.3f")
    header["SGSDECS"] = FormattedFloat(
        0.0025 * (ohrs - 6.0) + 0.01 + random.gauss(0.0, 0.005), "%0.3f"
    )
    header["SGSSCINT"] = FormattedFloat(
        0.8125 * (ohrs - 6.0) + 1.5 + random.gauss(0.0, 0.1), "%0.3f"
    )
    header["SGSLOOP"] = FormattedFloat(
        min(0.999 + random.gauss(0.0, 0.005), 1.0), "%0.2f"
    )
    header["SGSRAZR"] = FormattedFloat(random.gauss(-10.0, 1.0), "%0.1f")
    header["SGSDECZR"] = FormattedFloat(random.gauss(20.0, 1.0), "%0.1f")

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
