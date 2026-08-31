# -*- coding: utf-8 -*-

"""Utilities for updating the database.
"""

from contextlib import closing
import os

import mysql.connector

from . import (
    DatabaseError,
    get_connection,
    get_obsday_id,
    get_sw_id,
    get_level_id,
    get_filetype_id,
    get_producttype_id,
)

from ..config import get_option
from ..datetime import datetime2dateobs
from ..waveregions import available_waveregions
from ..logging import logger


def insert_web(
    connection: mysql.connector.connection_cext.CMySQLConnection,
    obsday_id: int,
    catalog,
):
    """Update the chromag_web database table."""

    sw_id = get_sw_id(connection)
    iquv_id = get_producttype_id(connection, "IQUV")
    i_id = get_producttype_id(connection, "I")
    fits_id = get_filetype_id(connection, "FITS")
    png_id = get_filetype_id(connection, "PNG")
    level1_id = get_level_id(connection, "L1")

    wave_regions = available_waveregions()
    with closing(connection.cursor()) as cursor:
        for w in wave_regions:
            if get_option(w, "publish_l1"):
                cat = catalog[catalog.is_science & (catalog.wave_region == w)]
                logger.info(
                    f"inserting {len(cat)} {w} nm files into web database table..."
                )
                for f in cat:
                    l1_file = f.l1_file
                    if l1_file is not None:
                        for p in ["iquv", "i"]:
                            for type in ["filename", f"{p}_quicklook"]:
                                # don't have I only FITS files right now
                                if type == "filename" and p == "i":
                                    continue

                                filename = l1_file.get_filename(type)
                                basename = os.path.basename(filename)

                                filetype_id = fits_id if type == "filename" else png_id
                                producttype_id = i_id if p == "i" else iquv_id

                                fields = {
                                    "filename": (f'"{basename}"', "s"),
                                    "l0_filename": (f'"{f.basename}"', "s"),
                                    "filesize": (os.path.getsize(filename), "d"),
                                    "date_obs": (
                                        f'"{datetime2dateobs(f.date_obs)}"',
                                        "s",
                                    ),
                                    "obsday_id": (obsday_id, "d"),
                                    "wave_region": (f'"{f.wave_region}"', "s"),
                                    "wavelength": (f.wavelength, "0.3f"),
                                    "producttype_id": (producttype_id, "d"),
                                    "filetype_id": (filetype_id, "d"),
                                    "level_id": (level1_id, "d"),
                                }
                                field_names = ",".join(fields.keys())
                                field_values = ",".join(
                                    [f"{v[0]:{v[1]}}" for v in fields.values()]
                                )
                                cmd = f"insert into chromag_web ({field_names}) value ({field_values});"
                                try:
                                    cursor.execute(cmd)
                                    filename = l1_file.get_filename("filename")
                                    basename = os.path.basename(filename)
                                    logger.debug(f"inserted {basename}")
                                except mysql.connector.errors.Error as e:
                                    logger.error(e.msg)
                                    logger.error(
                                        f"error inserting {basename} into chromag_web"
                                    )
            else:
                logger.info(f"skipped inserting {w} nm files to web database table")

    connection.commit()


def insert_level0(
    connection: mysql.connector.connection_cext.CMySQLConnection,
    obsday_id: int,
    catalog,
):
    """Update the chromag_level0 database table."""
    logger.info(f"inserting {len(catalog)} files into level 0 database...")
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
            try:
                cursor.execute(cmd)
                logger.debug(f"inserted {f.basename}")
            except mysql.connector.errors.Error as e:
                logger.error(e.msg)
                logger.error(f"error inserting {f.basename} into chromag_level0")

    connection.commit()


def insert_level1(
    connection: mysql.connector.connection_cext.CMySQLConnection,
    obsday_id: int,
    catalog,
):
    """Update the chromag_level1 database table."""
    logger.info("inserting files into level 1 database...")

    sw_id = get_sw_id(connection)
    wave_regions = available_waveregions()
    with closing(connection.cursor()) as cursor:
        for w in wave_regions:
            cat = catalog[catalog.is_science & (catalog.wave_region == w)]
            logger.info(f"inserting {len(cat)} {w} nm files into level 1 database...")
            for f in cat:
                l1_file = f.l1_file
                if l1_file is not None:
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
                    try:
                        cursor.execute(cmd)
                        logger.debug(f"inserted {basename}")
                    except mysql.connector.errors.Error as e:
                        logger.error(e.msg)
                        logger.error(f"error inserting {basename} into chromag_level1")

    connection.commit()


def insert_level2(
    connection: mysql.connector.connection_cext.CMySQLConnection,
    obsday_id: int,
    catalog,
):
    """Update the chromag_level2 database table."""
    logger.info("inserting files into level 2 database...")

    # [TODO]: implement
    logger.warning("chromag_level2 insertion not implemented")


def insert_level3(
    connection: mysql.connector.connection_cext.CMySQLConnection,
    obsday_id: int,
    catalog,
):
    """Update the chromag_level3 database table."""
    logger.info("inserting files into level 3 database...")

    # [TODO]: implement
    logger.warning("chromag_level3 insertion not implemented")


def insert_files(run, catalog):
    """Insert results of processing into database."""
    if get_option("database", "update"):
        logger.info("inserting files into database...")

        config_filename = get_option("database", "config_filename")
        config_section = get_option("database", "config_section")

        level_routines = [
            insert_web,
            insert_level0,
            insert_level1,
            insert_level2,
            insert_level3,
        ]

        try:
            with closing(get_connection(config_filename, config_section)) as connection:
                obsday_id = get_obsday_id(connection, run.observing_day)
                for insert_level_routine in level_routines:
                    insert_level_routine(connection, obsday_id, catalog)
        except mysql.connector.errors.Error as e:
            logger.error(e, exc_info=True)
            raise DatabaseError(e.msg)

            raise e
    else:
        logger.info("skipped files results into database")
