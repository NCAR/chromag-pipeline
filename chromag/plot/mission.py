# -*- coding: utf-8 -*-

"""Module to plot engineering data for the entire mission. Data to be plotted
here must be stored in a database table to be retrieved for plotting.
"""

from contextlib import closing
import datetime
import os

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, MonthLocator

# from matplotlib.transforms import IdentityTransform
import mysql.connector
import numpy as np

from .. import mission_start
from ..config import get_option
from ..database import DatabaseError, query, get_connection
from ..datetime import decompose_date
from ..logging import logger
from ..pipeline import step
from ..waveregions import available_waveregions


DATE_FORMAT = "%Y-%m"


def _mission_time_series(
    output_filename: str,
    datetimes: list[datetime.datetime],
    datasets: list[np.ndarray],
    titles: list[str],
    ytitles: list[str],
    yranges: list[tuple],
):
    """Make a generic daily time series plot with potentially many panels."""
    n_plots = len(datasets)
    last_datetime = datetimes[-1]

    label_fontsize = 8.0
    figsize = (8.0, 2.25 * n_plots)
    fig, axes = plt.subplots(n_plots, 1, figsize=figsize, layout="constrained")

    for ax, d, t, yt, yr in zip(axes, datasets, titles, ytitles, yranges):
        ax.scatter(datetimes, d, c="b", marker="o", s=1.0)
        ax.set_ylabel(yt, fontsize=label_fontsize)
        ax.set_ylim(yr)
        ax.grid(axis="y", color="#d0d0d0")
        ax.spines["top"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_xlim((mission_start, last_datetime))
        ax.xaxis.set_major_locator(MonthLocator(bymonth=[4, 8, 12]))
        ax.xaxis.set_major_formatter(DateFormatter(DATE_FORMAT))
        ax.set_xlabel("Date [UT]", fontsize=label_fontsize)
        ax.set_title(t)

    plt.savefig(output_filename)
    plt.close(fig)
    logger.info(f"wrote {os.path.basename(output_filename)}")


@step()
def write_imagescale_plot(
    imagescale_plot_filename: str,
    connection: mysql.connector.connection_cext.CMySQLConnection,
    wave_region: str,
):
    sql_cmd = "select date_obs, imagescale from chromag_level1 where wave_region='{wave_region}' order by date_obs;"
    results = query(connection, sql_cmd)
    if results is None:
        logger.debug("no image scale values found, skipped")
        return
    logger.debug(f"retrieved {len(results)} image scale values")
    datetimes = np.array([r[0] for r in results])
    imagescales = np.array([r[1] for r in results])
    _mission_time_series(
        imagescale_plot_filename,
        datetimes,
        [imagescales],
        [f"Image scale for {wave_region} nm"],
        ["Image scale [arcsec/pixel"],
        [(5.0, 6.0)],
    )


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
                for w in available_waveregions():
                    write_imagescale_plot(
                        os.path.join(
                            eng_dir,
                            f"{date_run.observing_day}.chromag.{w}.imagescale.mission.png",
                        ),
                        connection,
                        w,
                    )
        except mysql.connector.errors.Error as e:
            logger.error(e, exc_info=True)
            raise DatabaseError(e.msg)
