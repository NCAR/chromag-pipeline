# -*- coding: utf-8 -*-

"""Handle properties of the spectral lines."""

import datetime
import os
from typing import TypeVar

import epochs

DateValue = TypeVar("DateValue", str, datetime.datetime)


ep = None


def get(property_name, date: DateValue):
    """Get property value for a given datetime."""
    global ep

    # read the epochs files if it hasn't been initialized already
    if ep is None:
        epochs_root = os.path.dirname(os.path.abspath(__file__))
        epochs_spec_filename = os.path.join(epochs_root, "epochs.spec.cfg")
        ep = epochs.EpochConfigParser(epochs_spec_filename)

        epochs_cfg_filename = os.path.join(epochs_root, "epochs.cfg")
        ep.read(epochs_cfg_filename)

    return ep.get(property_name, date)
