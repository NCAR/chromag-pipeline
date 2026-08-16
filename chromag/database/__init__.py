# -*- coding: utf-8 -*-

"""Utilities for communicating with the database.
"""

import configparser
import datetime
import errno
import os

import mysql
import mysql.connector

from .clearday import clearday

from .. import __version__
from .. import __revision__
from ..logging import logger


DATABASE_DIR = os.path.dirname(os.path.abspath(__file__))
TABLE_NAMES = ["chromag_sw", "chromag_level0", "chromag_level1", "chromag_web"]


class DatabaseConnectionError(Exception):
    """Exception to indicate a problem connecting to the database."""


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


def get_obsday_id(cursor: mysql.connector.cursor_cext.CMySQLCursor, obs_date: str):
    """Retrieve the observing day identifier given the "observing day", i.e.,
    the HST date of the observations.
    """
    cmd = f'select day_id from mlso_numfiles where obs_day = "{obs_date}" limit 1;'
    cursor.execute(cmd)
    result = cursor.fetchone()
    obsday_id = result[0]
    return obsday_id


def update_sw(cursor: mysql.connector.cursor_cext.CMySQLCursor):
    """Update the versions table with the version of the this code."""

    # check to see if version is already present
    query = 'select count(sw_id) from ucomp_sw where sw_version="{__version__}" and sw_revision="{__revision__}"'
    logger.info(query)
    cursor.execute(query)
    n_matching_rows = cursor.fetchone()[0]

    if n_matching_rows == 0:
        # "release date" is first use
        release_date = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

        cmd = f'insert into chromag_sw (release_date, version, revision) values ("{release_date}", "{__version__}", "{__revision__}");'
        logger.info(cmd)
        cursor.execute(cmd)


def get_connection(config_filename: str, config_section: str):
    """Make connection to database given the configuration filename and section
    within it with login details for the database. Returns connection.
    """
    if not os.path.exists(config_filename):
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), config_filename
        )

    cp = configparser.ConfigParser()
    cp.read(config_filename)

    host = cp.get(config_section, "host")
    user = cp.get(config_section, "user")
    password = cp.get(config_section, "password")
    database = cp.get(config_section, "database")

    connection = mysql.connector.connect(
        host=host, user=user, password=password, database=database
    )

    return connection


def initialize_tables(config_filename: str, config_section: str):
    """Delete any existing tables and then re-create new tables."""
    # [TODO]: add error checking
    try:
        connection = get_connection(config_filename, config_section)
        cursor = connection.cursor()
    except mysql.connector.errors.DatabaseError as e:
        raise DatabaseConnectionError(e.msg)

    logger.info(f"connected to database")

    for t in reversed(TABLE_NAMES):
        delete_table(cursor, t)
        logger.info(f"deleted {t} database table")

    for t in TABLE_NAMES:
        create_table(cursor, t)
        logger.info(f"created {t} database table")

    cursor.close()
    connection.close()

    logger.info("closed database connection")
