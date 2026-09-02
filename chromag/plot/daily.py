# -*- coding: utf-8 -*-

"""Module to plot daily engineering data.
"""

import os

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, FixedLocator
from matplotlib.transforms import IdentityTransform
import numpy as np

from ..config import get_option
from ..datetime import obsday_hours2str, decompose_date
from ..logging import logger


START_TIME = 6  # 6 am HST
END_TIME = 18  # 6 pm HST


def obsday_hours_formatter(obsday_hours: float, pos: float) -> str:
    """Format an obsday_hours (fractional hours) value into a formatted
    string.
    """
    return obsday_hours2str(obsday_hours)


def _daily_time_series(
    output_filename: str,
    times: list[float],
    datasets: list[np.ndarray],
    titles: list[str],
    ytitles: list[str],
    yranges: list[tuple],
):
    """Make a generic daily time series plot with potentially many panels."""
    n_plots = len(datasets)

    label_fontsize = 8.0
    figsize = (8.0, 2.25 * n_plots)
    fig, axes = plt.subplots(n_plots, 1, figsize=figsize, layout="constrained")

    for ax, d, t, yt, yr in zip(axes, datasets, titles, ytitles, yranges):
        ax.scatter(times, d, c="b", marker="o", s=1.0)
        ax.set_ylabel(yt, fontsize=label_fontsize)
        ax.set_ylim(yr)
        ax.grid(axis="y", color="#d0d0d0")
        ax.spines["top"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_xlim((START_TIME, END_TIME))
        ax.xaxis.set_major_locator(FixedLocator(range(START_TIME, END_TIME + 1, 1)))
        ax.xaxis.set_major_formatter(FuncFormatter(obsday_hours_formatter))
        ax.set_xlabel("observing day [HST]", fontsize=label_fontsize)
        ax.set_title(t)

    plt.savefig(output_filename)
    plt.close(fig)
    logger.info(f"wrote {os.path.basename(output_filename)}")


def seeing_plot(output_filename: str, date_run):
    """Write 3 panel seeing plot with SGSDIMV, SGSDIMS, and SGSSCINT."""

    catalog = date_run.catalog

    times = catalog.obsday_hours
    dimv = catalog.get_headervalues("SGSDIMV")
    dims = catalog.get_headervalues("SGSDIMS")
    scint = catalog.get_headervalues("SGSSCINT")

    titles = ["DIMV", "DIMS", "Seeing"]
    ytitles = ["DIMV [volts]", "DIMS [volts]", "Scintillation [arcsec]"]
    yranges = [(0.0, 10.0), (0.0, 0.1), (0.0, 8.0)]

    logger.info("plotting seeing...")
    _daily_time_series(
        output_filename, times, [dimv, dims, scint], titles, ytitles, yranges
    )


def daily_plots(date_run):
    """Write the daily plots."""
    eng_basedir = get_option("engineering", "basedir")
    if eng_basedir is not None:
        eng_dir = os.path.join(eng_basedir, *decompose_date(date_run.observing_day))
        if not os.path.isdir(eng_dir):
            os.makedirs(eng_dir)
    else:
        logger.warn("engineering.basedir not set, skipping daily plots")

    seeing_filename = os.path.join(
        eng_dir, f"{date_run.observing_day}.chromag.seeing.png"
    )

    seeing_plot(seeing_filename, date_run)
