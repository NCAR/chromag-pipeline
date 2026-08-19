# -*- coding: utf-8 -*-

"""Utilities for querying the database.
"""

import mysql
import mysql.connector

from ..logging import logger
from ..datetime import short2hyphenated


def get_obsday_id(
    connection: mysql.connector.connection_cext.CMySQLConnection, obs_date: str
):
    """Retrieve the observing day identifier given the "observing day", i.e.,
    the HST date of the observations. If there isn't a row for it yet, create a
    new row for the observing day.
    """

    cursor = connection.cursor()

    date = short2hyphenated(obs_date)
    cmd = f'select day_id from mlso_numfiles where obs_day = "{date}" limit 1;'
    cursor.execute(cmd)
    result = cursor.fetchone()
    if result is None:
        logger.debug(f"inserting {date} into mlso_numfiles...")
        cmd = f'insert into mlso_numfiles (obs_day) values ("{date}")'
        cursor.execute(cmd)
        obsday_id = cursor.lastrowid
        logger.debug(f"inserted obsday_id={obsday_id} for {date}")
    else:
        obsday_id = result[0]
        logger.debug(f"found obsday_id={obsday_id} for {date}")

    connection.commit()
    cursor.close()

    return obsday_id
