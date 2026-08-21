# -*- coding: utf-8 -*-

"""Utilities for updating the database.
"""

from contextlib import closing

import mysql.connector

from . import DatabaseError, get_connection, get_obsday_id, get_sw_id

from ..config import get_option
from ..logging import logger


def insert_level0(
    connection: mysql.connector.connection_cext.CMySQLConnection,
    obsday_id: int,
    catalog,
):
    """Update the chromag_level0 database table."""
    logger.info("inserting level 0 files into database...")
    with closing(connection.cursor()) as cursor:
        pass


def insert_level1(
    connection: mysql.connector.connection_cext.CMySQLConnection,
    obsday_id: int,
    catalog,
):
    """Update the chromag_level1 database table."""
    logger.info("inserting level 1 files into database...")
    sw_id = get_sw_id(connection)
    logger.info("not implemented")
    logger.warning("not implemented")


def insert_level2(
    connection: mysql.connector.connection_cext.CMySQLConnection,
    obsday_id: int,
    catalog,
):
    """Update the chromag_level2 database table."""
    logger.info("inserting level 2 files into database...")
    logger.warning("not implemented")


def insert_level3(
    connection: mysql.connector.connection_cext.CMySQLConnection,
    obsday_id: int,
    catalog,
):
    """Update the chromag_level2 database table."""
    logger.info("inserting level 3 files into database...")
    logger.warning("not implemented")


def insert_files(run, catalog):
    """Insert results of processing into database."""
    if get_option("database", "update"):
        logger.info("inserting files into database...")

        config_filename = get_option("database", "config_filename")
        config_section = get_option("database", "config_section")

        level_routines = [insert_level0, insert_level1, insert_level2, insert_level3]

        try:
            with closing(get_connection(config_filename, config_section)) as connection:
                obsday_id = get_obsday_id(connection, run.observing_day)
                for insert_level_routine in level_routines:
                    insert_level_routine(connection, obsday_id, catalog)
        except mysql.connector.errors.Error as e:
            raise DatabaseError(e.msg)
    else:
        logger.info("skipped files results into database")
