# -*- coding: utf-8 -*-

"""Handle properties of the spectral lines."""

import os

import epochs


LINES_ROOT = os.path.dirname(os.path.abspath(__file__))
LINES_CFG = os.path.join(LINES_ROOT, "lines.cfg")
LINES_SPEC = os.path.join(LINES_ROOT, "lines.spec.cfg")


cp = epochs.ConfigParser(LINES_SPEC)
cp.read(LINES_CFG)


def list():
    """List the available spectral lines. Returns an array of string names."""
    return cp.specification.sections()


def property(line_name, property_name):
    """Retrieve a property of a given spectral line."""
    return cp.get(line_name, property_name)
