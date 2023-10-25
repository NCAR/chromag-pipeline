# -*- coding: utf-8 -*-

"""Handle configuration options."""

import configparser
import fnmatch
import os

import epochs


CONFIG_ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_SPEC = os.path.join(CONFIG_ROOT, "chromag.config.spec.cfg")

cp = epochs.ConfigParser(CONFIG_SPEC)


def read_config(config_filename):
    """Read a configuration file."""
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
