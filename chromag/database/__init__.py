# -*- coding: utf-8 -*-

"""Utilities for communicating with the database.
"""

import os

from .connect import get_connection
from .query import get_obsday_id


class DatabaseError(Exception):
    """Exception to indicate a problem connecting to the database."""


from .clearday import clearday
from .initialize import initialize_tables

from ..logging import logger
