# -*- coding: utf-8 -*-

"""Utilities for initializing the database.
"""

from contextlib import closing

import mysql
import mysql.connector
import os

from . import DatabaseError, get_connection

from ..logging import logger

DATABASE_DIR = os.path.dirname(os.path.abspath(__file__))
TABLE_NAMES = ["chromag_sw", "chromag_level0", "chromag_level1", "chromag_web"]


def get_table_definition(table_name: str):
    """Read the `{table_name}.tbl` file in this directory and return it."""
    table_filename = os.path.join(DATABASE_DIR, table_name + ".tbl")
    with open(table_filename, "r") as f:
        table_definition = f.read()
    return table_definition


def delete_table(cursor: mysql.connector.cursor_cext.CMySQLCursor, table_name: str):
    """Deletes a database table of the given name, e.g., "chromag_level0", if
    it exists.
    """
    cursor.execute(f"drop table if exists {table_name}")


def create_table(cursor: mysql.connector.cursor_cext.CMySQLCursor, table_name: str):
    """Creates a database table of the given name, e.g., "chromag_level0"."""
    table_definition = get_table_definition(table_name)

    # create table
    cursor.execute(table_definition)


def initialize_tables(config_filename: str, config_section: str):
    """Delete any existing tables and then re-create new tables."""

    try:
        with closing(get_connection(config_filename, config_section)) as connection:
            logger.info(f"connected to database")
            with closing(connection.cursor()) as cursor:
                for t in reversed(TABLE_NAMES):
                    delete_table(cursor, t)
                    logger.info(f"deleted {t} database table")
                for t in TABLE_NAMES:
                    create_table(cursor, t)
                    logger.info(f"created {t} database table")
            connection.commit()
    except mysql.connector.errors.Error as e:
        raise DatabaseError(e.msg)

    logger.info("closed database connection")
