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
    cp.read(config_filename)
    return(cp.is_valid())


def get_option(section_name, option_name):
    """Retrieve an option of a section."""
    value = cp.get(section_name, option_name)
    return(value)


def get_basedir(date, type):
    value = get_option(type, "basedir")
    if value is not None:
        return(value)

    routing_filename = cp.get(type, "routing_file")
    if routing_filename is None:
        return(None)

    routing_file = configparser.ConfigParser()
    routing_file.read(routing_filename)
    routing_section = f"chromag-{type}"
    options = routing_file.options(routing_section)
    for o in options:
        if fnmatch.fnmatch(date, o):
            return(routing_file.get(routing_section, o))

    return(None)
