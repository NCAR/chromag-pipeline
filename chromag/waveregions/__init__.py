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


class WaveRegionError(Exception):
    """Exception to indicate a problem initializig the wave region
    configurations."""


def _get_spec(waveregion: str):
    """Get the `EpochConfigParser` spec for the given wave region."""
    if cps is None:
        _initialize_waveregions()

    return cps[waveregion].spec


def _initialize_waveregions():
    """Initialize the dict of wave region options."""
    global cps

    cps = collections.OrderedDict()
    waveregion_root = os.path.dirname(os.path.abspath(__file__))

    specs = glob.glob(os.path.join(waveregion_root, "*.spec.cfg"))
    for s in specs:
        cp = epochs.EpochConfigParser(s)
        waveregion = os.path.basename(s.removesuffix(".spec.cfg"))

        waveregion_cfg = os.path.join(waveregion_root, f"{waveregion}.cfg")
        cp.read(waveregion_cfg)

        try:
            if not cp.is_valid():
                raise WaveRegionError(f"{waveregion}.cfg not valid")
        except ValueError as e:
            raise WaveRegionError(e.msg)

        cps[waveregion] = cp


def available_waveregions():
    """List the available wave regions. Returns a list of string names."""
    if cps is None:
        _initialize_waveregions()

    return cps.keys()


def waveregion_property(waveregion: str, property_name: str, date: DateValue):
    """Retrieve a property of a given wave region."""
    if cps is None:
        _initialize_waveregions()

    return cps[waveregion].get(property_name, date)
