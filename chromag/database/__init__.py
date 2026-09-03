# -*- coding: utf-8 -*-

"""Utilities for communicating with the database.
"""

import os


class DatabaseError(Exception):
    """Exception to indicate a problem connecting to the database."""


from .connect import get_connection
from .update import (
    ProcessStatus,
    get_obsday_id,
    get_sw_id,
    get_level_id,
    get_filetype_id,
    get_producttype_id,
    set_process_id,
)
from .clearday import clearday
from .initialize import initialize_tables
from .insert import insert_files
from .query import query

from ..logging import logger
