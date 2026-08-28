# -*- coding: utf-8 -*-

"""Handle properties of the wave regions."""

import collections
import datetime
import glob
import os
from typing import TypeVar

import epochs


DateValue = TypeVar("DateValue", str, datetime.datetime)

cps = None


def initialize_waveregions():
    global cps

    cps = collections.OrderedDict()
    waveregion_root = os.path.dirname(os.path.abspath(__file__))

    specs = glob.glob(os.path.join(waveregion_root, "*.spec.cfg"))
    for s in specs:
        cp = epochs.EpochConfigParser(s)
        waveregion = os.path.basename(s.removesuffix(".spec.cfg"))

        waveregion_cfg = os.path.join(waveregion_root, f"{waveregion}.cfg")
        cp.read(waveregion_cfg)
        cps[waveregion] = cp


def available_waveregions():
    """List the available wave regions. Returns a list of string names."""
    if cps is None:
        initialize_waveregions()

    return cps.keys()


def waveregion_property(waveregion: str, property_name: str, date: DateValue):
    """Retrieve a property of a given wave region."""
    if cps is None:
        initialize_waveregions()

    return cps[waveregion].get(property_name, date)
