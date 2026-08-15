# -*- coding: utf-8 -*-

"""Module for clearing existing published ChroMag data."""

from ..logging import logger


def clearday(run):
    # [TODO]: implement
    #  - clear processing directory
    #  - clear database tables
    #  - clear web directories
    logger.info(f"clearing {run.observing_day}...")
