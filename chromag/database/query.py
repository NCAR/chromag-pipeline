# -*- coding: utf-8 -*-

"""Utilities for querying the database.
"""

from contextlib import closing

import mysql.connector

from ..logging import logger


def query(
    connection: mysql.connector.connection_cext.CMySQLConnection,
    sql_cmd: str,
):
    with closing(connection.cursor()) as cursor:
        cursor.execute(sql_cmd)
        results = cursor.fetchall()
    return results
