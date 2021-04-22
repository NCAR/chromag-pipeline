# -*- coding: utf-8 -*-

"""Handle configuration options."""

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
    return(cp.get(section_name, option_name))
    