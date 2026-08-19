# -*- coding: utf-8 -*-

"""Utilities for updating the database.
"""

import datetime

import mysql
import mysql.connector

from .. import __version__
from .. import __revision__

from ..logging import logger


def update_sw(cursor: mysql.connector.cursor_cext.CMySQLCursor):
    """Update the versions table with the version of the this code."""

    # check to see if version is already present
    query = 'select count(sw_id) from ucomp_sw where sw_version="{__version__}" and sw_revision="{__revision__}"'
    logger.info(query)
    cursor.execute(query)
    n_matching_rows = cursor.fetchone()[0]

    # update chromag_sw if no matching release was found
    if n_matching_rows == 0:
        # "release date" is first use of the version in production
        release_date = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

        cmd = f'insert into chromag_sw (release_date, version, revision) values ("{release_date}", "{__version__}", "{__revision__}");'
        logger.info(cmd)
        cursor.execute(cmd)
