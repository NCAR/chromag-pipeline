# -*- coding: utf-8 -*-

"""Utilities for clearing the database results..
"""

from contextlib import closing

import mysql.connector

from . import DatabaseError, get_connection, get_obsday_id

from ..config import get_option
from ..logging import logger


def clear_table(
    connection: mysql.connector.connection_cext.CMySQLConnection,
    obsday_id: int,
    table_name: str,
):
    """Remove entries from given table and matching `obsday_id`."""
    with closing(connection.cursor()) as cursor:
        cmd = f"delete from {table_name} where obsday_id={obsday_id}"
        cursor.execute(cmd)
        logger.info(f"{cursor.rowcount} rows deleted from {table_name}")


def clearday(date_run):
    if get_option("database", "update"):
        config_filename = get_option("database", "config_filename")
        config_section = get_option("database", "config_section")

        table_names = ["chromag_level0", "chromag_level1", "chromag_web"]
        try:
            with closing(get_connection(config_filename, config_section)) as connection:
                obsday_id = get_obsday_id(connection, date_run.observing_day)
                for t in table_names:
                    clear_table(connection, obsday_id, t)
        except mysql.connector.errors.Error as e:
            raise DatabaseError(e.msg)
