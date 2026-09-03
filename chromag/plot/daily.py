# -*- coding: utf-8 -*-

"""Module to plot daily engineering data.
"""

import os

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, FixedLocator
from matplotlib.transforms import IdentityTransform
import numpy as np

from . import darken

from .. import mission_start
from ..config import get_option
from ..datetime import obsday_hours2str, decompose_date
from ..logging import logger
from ..pipeline import step
from ..waveregions import available_waveregions, waveregion_property

START_TIME = 6  # 6 am HST
END_TIME = 18  # 6 pm HST

TIMELINE_BINS_PER_HOUR = 6  # bins are 10 minutes
TIMELINE_MAX_WAVE_FILES_PER_BIN = 100
TIMELINE_MAX_DARK_FILES_PER_BIN = 10


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
        ax.set_xlabel("Observing day time [HST]", fontsize=label_fontsize)
        ax.set_title(t)

    plt.savefig(output_filename)
    plt.close(fig)
    logger.info(f"wrote {os.path.basename(output_filename)}")


@step()
def write_seeing_plot(output_filename: str, date_run):
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


@step(top=True)
def write_daily_plots(date_run):
    """Write the daily plots."""
    eng_basedir = get_option("engineering", "basedir")
    if eng_basedir is not None:
        eng_dir = os.path.join(eng_basedir, *decompose_date(date_run.observing_day))
        if not os.path.isdir(eng_dir):
            os.makedirs(eng_dir)
    else:
        logger.warn("engineering.basedir not set, skipping daily plots")

    seeing_filename = os.path.join(
        eng_dir, f"{date_run.observing_day}.chromag.seeing.daily.png"
    )

    write_seeing_plot(seeing_filename, date_run)


def write_timeline(output_filename: str, catalog, binsize: int = 15):
    """Create a timeline of the observations for the day."""
    wave_regions = available_waveregions()
    figsize = (7, 2)
    label_fontsize = 8
    edge_darkening_factor = 0.7
    n_rows = len(wave_regions) + 1  # one for every wave region plus darks
    n_cols = 1
    fig, axes = plt.subplots(
        n_rows, n_cols, sharex=True, figsize=figsize, layout="constrained"
    )

    for i, w in enumerate(wave_regions):
        wave_files = catalog[catalog.wave_region == w]
        wave_color = waveregion_property(w, "color", mission_start)
        # [TODO]: to add flats/cal files:
        # - change histtype to "stepfilled"
        # - pass [sci_files, flat_files, cal_files]
        # - pass color=[sci_color, flat_color, cal_color]
        # - use alpha=
        # [TODO]: might need to do histogram separately so that I can determine
        # the TIMELINE MAX_WAVE_FILES_PER_BIN for this day because I think that
        # it could be over 600 files in 10 minutes, at least theoretically
        axes[i].hist(
            wave_files.obsday_hours,
            bins=(END_TIME - START_TIME) * TIMELINE_BINS_PER_HOUR,
            range=(START_TIME, END_TIME),
            color=wave_color,
            edgecolor=darken(wave_color, factor=edge_darkening_factor),
            histtype="stepfilled",
        )
        axes[i].set_ylim(0, TIMELINE_MAX_WAVE_FILES_PER_BIN)
        axes[i].tick_params(
            left=False, bottom=False, labelleft=False, labelbottom=False
        )
        axes[i].spines["top"].set_visible(False)
        axes[i].spines["left"].set_visible(False)
        axes[i].spines["right"].set_visible(False)
        axes[i].spines["bottom"].set_color("#d0d0d0")
        axes[i].set_ylabel(f"{w} nm", fontsize=label_fontsize, rotation=0)

    dark_files = catalog[catalog.is_dark]
    dark_index = len(wave_regions)
    axes[dark_index].hist(
        dark_files.obsday_hours,
        bins=(END_TIME - START_TIME) * TIMELINE_BINS_PER_HOUR,
        range=(START_TIME, END_TIME),
        color="#606060",
        edgecolor=darken("#606060", factor=edge_darkening_factor),
        histtype="stepfilled",
    )
    # [TODO]: darks might need a different scale, we will never take enough
    # darks to show up as much
    axes[dark_index].set_ylim(0, TIMELINE_MAX_DARK_FILES_PER_BIN)
    axes[dark_index].set_yticks([])
    axes[dark_index].tick_params(left=False, labelsize=label_fontsize)
    axes[dark_index].spines["top"].set_visible(False)
    axes[dark_index].spines["left"].set_visible(False)
    axes[dark_index].spines["right"].set_visible(False)
    axes[dark_index].spines["bottom"].set_color("#d0d0d0")
    axes[dark_index].set_ylabel("darks", fontsize=label_fontsize, rotation=0)
    axes[dark_index].xaxis.set_major_locator(
        FixedLocator(range(START_TIME, END_TIME + 1, 1))
    )
    axes[dark_index].xaxis.set_major_formatter(FuncFormatter(obsday_hours_formatter))

    axes[dark_index].set_xlabel("Observing day time [HST]", fontsize=label_fontsize)

    binsize_msg = f"max {TIMELINE_MAX_WAVE_FILES_PER_BIN} in wave region, {TIMELINE_MAX_DARK_FILES_PER_BIN} dark files per {60 // TIMELINE_BINS_PER_HOUR:d} min bin"
    annotation = fig.text(
        5.0, 5.0, binsize_msg, transform=IdentityTransform(), fontsize=6, color="grey"
    )
    annotation.set_in_layout(False)

    plt.savefig(output_filename)
    plt.close(fig)
