# -*- coding: utf-8 -*-

"""Handle properties of the spectral lines."""

import os

import epochs


cp = None


def initialize_lines():
    global cp

    lines_root = os.path.dirname(os.path.abspath(__file__))
    lines_spec = os.path.join(lines_root, "lines.spec.cfg")
    cp = epochs.ConfigParser(lines_spec)

    lines_cfg = os.path.join(lines_root, "lines.cfg")
    cp.read(lines_cfg)


def available_lines():
    """List the available spectral lines. Returns a list of string names."""
    if cp is None:
        initialize_lines()

    return cp.specification.sections()


def line_property(line_name, property_name):
    """Retrieve a property of a given spectral line."""
    if cp is None:
        initialize_lines()

    return cp.get(line_name, property_name)
