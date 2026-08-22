# -*- coding: utf-8 -*-

"""Utilities for updating the database.
"""

from contextlib import closing
import os

import mysql.connector

from . import DatabaseError, get_connection, get_obsday_id, get_sw_id

from ..config import get_option
from ..datetime import datetime2dateobs
from ..lines import available_lines
from ..logging import logger


def insert_level0(
    connection: mysql.connector.connection_cext.CMySQLConnection,
    obsday_id: int,
    catalog,
):
    """Update the chromag_level0 database table."""
    logger.info(f"inserting {len(catalog)} level 0 files into database...")
    with closing(connection.cursor()) as cursor:
        for f in catalog:
            fields = {
                "filename": (f'"{f.basename}"', "s"),
                "filesize": (os.path.getsize(f.filename), "d"),
                "date_obs": (f'"{datetime2dateobs(f.date_obs)}"', "s"),
                "obsday_id": (obsday_id, "d"),
                "datatype": (f'"{f.datatype}"', "s"),
                "object": (f'"{f.object}"', "s"),
                "wave_region": (f'"{f.wave_region}"', "s"),
                "wavelength": (f.wavelength, "0.3f"),
                "exposure": (f.exposure, "0.3f"),
                "scan_i": (f.scan_i, "d"),
                "scan_n": (f.scan_n, "d"),
            }
            field_names = ",".join(fields.keys())
            field_values = ",".join([f"{v[0]:{v[1]}}" for v in fields.values()])
            cmd = f"insert into chromag_level0 ({field_names}) value ({field_values});"
            cursor.execute(cmd)
            logger.debug(f"inserted {f.basename}")

    connection.commit()


def insert_level1(
    connection: mysql.connector.connection_cext.CMySQLConnection,
    obsday_id: int,
    catalog,
):
    """Update the chromag_level1 database table."""
    logger.info("inserting level 1 files into database...")

    sw_id = get_sw_id(connection)
    wave_regions = available_lines()
    with closing(connection.cursor()) as cursor:
        for w in wave_regions:
            for f in catalog[catalog.is_science & (catalog.wave_region == w)]:
                l1_file = f.l1_file
                filename = l1_file.get_filename("filename")
                basename = os.path.basename(filename)
                fields = {
                    "filename": (f'"{basename}"', "s"),
                    "l0_filename": (f'"{f.basename}"', "s"),
                    "filesize": (os.path.getsize(filename), "d"),
                    "date_obs": (f'"{datetime2dateobs(f.date_obs)}"', "s"),
                    "obsday_id": (obsday_id, "d"),
                    "wave_region": (f'"{f.wave_region}"', "s"),
                    "wavelength": (f.wavelength, "0.3f"),
                    "exposure": (f.exposure, "0.3f"),
                    "scan_i": (f.scan_i, "d"),
                    "scan_n": (f.scan_n, "d"),
                    "chromag_sw_id": (sw_id, "d"),
                }
                field_names = ",".join(fields.keys())
                field_values = ",".join([f"{v[0]:{v[1]}}" for v in fields.values()])
                cmd = f"insert into chromag_level1 ({field_names}) value ({field_values});"
                cursor.execute(cmd)

                logger.debug(f"inserted {basename}")

    connection.commit()


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
