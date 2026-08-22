# -*- coding: utf-8 -*-

"""Utilities for retrieving items from the database that might need to be
created if they are not already there.
"""

from contextlib import closing
import datetime

import mysql.connector

from .. import __version__
from .. import __revision__

from ..datetime import short2hyphenated
from ..logging import logger


def get_sw_id(connection: mysql.connector.connection_cext.CMySQLConnection):
    """Update the versions table with the version of the this code."""

    with closing(connection.cursor()) as cursor:
        # check to see if version is already present
        query = f'select sw_id from chromag_sw where version="{__version__}" and revision="{__revision__}" limit 1'
        cursor.execute(query)
        result = cursor.fetchone()

        # update chromag_sw if no matching release was found
        if result is None:
            # "release date" is first use of the version in production
            release_date = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

            cmd = f'insert into chromag_sw (release_date, version, revision) values ("{release_date}", "{__version__}", "{__revision__}");'
            cursor.execute(cmd)
            sw_id = cursor.lastrowid
            connection.commit()
        else:
            sw_id = result[0]
            logger.debug(f"found sw_id={sw_id} for {__version__} [{__revision__}]")

    return sw_id


def get_obsday_id(
    connection: mysql.connector.connection_cext.CMySQLConnection, obs_date: str
):
    """Retrieve the observing day identifier given the "observing day", i.e.,
    the HST date of the observations. If there isn't a row for it yet, create a
    new row for the observing day.
    """

    with closing(connection.cursor()) as cursor:
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
            connection.commit()
        else:
            obsday_id = result[0]
            logger.debug(f"found obsday_id={obsday_id} for {date}")

    return obsday_id
