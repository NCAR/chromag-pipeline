# -*- coding: utf-8 -*-

"""Handle retrieving configuration options.

chromag.config.spec.cfg defines the specification of valid configuration files.
It defines all the options to be set by the user of the pipeline, e.g., where
to look for the raw data, where to put the processed data, options on how
particular steps should run, etc.

In particular, `get_option` and `get_basedir` will be needed by many other
sections of the pipeline.
"""

import configparser
import fnmatch
import os

import epochs


cp = None


def read_config(config_filename):
    """Read a configuration file."""
    global cp
    if cp is None:
        config_root = os.path.dirname(os.path.abspath(__file__))
        config_spec = os.path.join(config_root, "chromag.config.spec.cfg")
        cp = epochs.ConfigParser(config_spec)
        cp.read(config_filename)
    return cp.is_valid()


def get_option(section_name, option_name):
    """Retrieve an option of a section."""
    value = cp.get(section_name, option_name)
    return value


def get_basedir(date, directory_type):
    """Retrieve the base directory of the given type for a date using either
    the `basedir` option if present or else the routing file."""
    value = get_option(directory_type, "basedir")
    if value is not None:
        return value

    routing_filename = cp.get(directory_type, "routing_file")
    if routing_filename is None:
        return None

    routing_file = configparser.ConfigParser()
    routing_file.read(routing_filename)
    routing_section = f"chromag-{directory_type}"
    options = routing_file.options(routing_section)
    for date_pattern in options:
        if fnmatch.fnmatch(date, date_pattern):
            return routing_file.get(routing_section, date_pattern)

    return None
