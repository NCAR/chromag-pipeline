# -*- coding: utf-8 -*-

"""Module to plot engineering data for the entire mission. Data to be plotted
here must be stored in a database table to be retrieved for plotting.
"""

from contextlib import closing
import os

import mysql.connector

from .. import mission_start
from ..config import get_option
from ..database import DatabaseError, query, get_connection
from ..datetime import decompose_date
from ..logging import logger
from ..pipeline import step


@step()
def write_imagescale_plot(
    image_scale_plot_filename: str,
    connection: mysql.connector.connection_cext.CMySQLConnection,
):
    sql_cmd = "select date_obs, imagescale from chromag_level1 order by date_obs;"
    results = query(connection, sql_cmd)
    logger.debug(f"retrieved {len(results)} image scales")
    for r in results:
        pass


@step(top=True)
def write_mission_plots(date_run):
    """Write the mission plots."""
    eng_basedir = get_option("engineering", "basedir")
    if eng_basedir is not None:
        eng_dir = os.path.join(eng_basedir, *decompose_date(date_run.observing_day))
        if not os.path.isdir(eng_dir):
            os.makedirs(eng_dir)
    else:
        logger.warn("engineering.basedir not set, skipping mission plots")

    if get_option("database", "update"):
        config_filename = get_option("database", "config_filename")
        config_section = get_option("database", "config_section")
        try:
            with closing(get_connection(config_filename, config_section)) as connection:
                # [TODO]: call various mission plotting routines here
                image_scale_filename = os.path.join(
                    eng_dir, f"{date_run.observing_day}.chromag.imagescale.mission.png"
                )
                write_imagescale_plot(image_scale_filename, connection)
        except mysql.connector.errors.Error as e:
            logger.error(e, exc_info=True)
            raise DatabaseError(e.msg)
