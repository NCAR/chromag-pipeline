# -*- coding: utf-8 -*-

"""Utilities for communicating with the database.
"""

import os


class DatabaseError(Exception):
    """Exception to indicate a problem connecting to the database."""


from .connect import get_connection
from .update import (
    get_obsday_id,
    get_sw_id,
    get_level_id,
    get_filetype_id,
    get_producttype_id,
)
from .clearday import clearday
from .initialize import initialize_tables
from .insert import insert_files

from ..logging import logger
