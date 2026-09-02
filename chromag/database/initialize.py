# -*- coding: utf-8 -*-

"""Utilities for initializing the database.
"""

from contextlib import closing

import mysql
import mysql.connector
import os

from . import DatabaseError, get_connection

from ..logging import logger


def get_sql_cmds(table_name: str, type: str):
    """Read the `{table_name}.tbl` file in this directory and return it."""
    database_dir = os.path.dirname(os.path.abspath(__file__))
    cmd_filename = os.path.join(database_dir, f"{type}_{table_name}.sql")
    if os.path.exists(cmd_filename):
        with open(cmd_filename, "r") as f:
            sql_cmds = f.read()
        return sql_cmds
    else:
        return None


def delete_table(cursor: mysql.connector.cursor_cext.CMySQLCursor, table_name: str):
    """Deletes a database table of the given name, e.g., "chromag_level0", if
    it exists.
    """
    logger.info(f"dropping chromag_{table_name} database table...")
    cursor.execute(f"drop table if exists chromag_{table_name}")


def create_table(cursor: mysql.connector.cursor_cext.CMySQLCursor, table_name: str):
    """Creates a database table of the given name, e.g., "chromag_level0"."""
    table_definition = get_sql_cmds(table_name, "create")
    logger.info(f"creating chromag_{table_name} database table...")
    cursor.execute(table_definition)


def init_table(cursor: mysql.connector.cursor_cext.CMySQLCursor, table_name: str):
    """Creates a database table of the given name, e.g., "chromag_level0"."""
    table_initialization = get_sql_cmds(table_name, "init")
    if table_initialization is not None:
        logger.info(f"initializing chromag_{table_name}...")
        for line in table_initialization.split("\n"):
            cursor.execute(line)
    else:
        logger.info(f"no initialization for chromag_{table_name}")


def initialize_tables(config_filename: str, config_section: str):
    """Delete any existing tables and then re-create new tables and initialize
    them."""

    table_names = [
        "sw",
        "process",
        "level",
        "filetype",
        "producttype",
        "level0",
        "level1",
        "web",
    ]

    try:
        with closing(get_connection(config_filename, config_section)) as connection:
            logger.info(f"connected to database")
            with closing(connection.cursor()) as cursor:
                # delete tables
                for t in reversed(table_names):
                    delete_table(cursor, t)

                # create tables
                for t in table_names:
                    create_table(cursor, t)

                # initialize values in tables
                for t in table_names:
                    init_table(cursor, t)
            connection.commit()
    except mysql.connector.errors.Error as e:
        raise DatabaseError(e.msg)

    logger.info("closed database connection")
