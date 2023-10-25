# -*- coding: utf-8 -*-

"""Handle properties of the spectral lines."""

import datetime
import os
from typing import TypeVar

import epochs

DateValue = TypeVar("DateValue", str, datetime.datetime)

EPOCHS_ROOT = os.path.dirname(os.path.abspath(__file__))
EPOCHS_CFG = os.path.join(EPOCHS_ROOT, "epochs.cfg")
EPOCHS_SPEC = os.path.join(EPOCHS_ROOT, "epochs.spec.cfg")


ep = epochs.EpochConfigParser(EPOCHS_SPEC)
ep.read(EPOCHS_CFG)


def get(property_name, date: DateValue):
    """Get property value for a given datetime."""
    return ep.get(property_name, date)
