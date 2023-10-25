# -*- coding: utf-8 -*-

"""Module to plot housekeeping engineering data.
"""

import configparser
import math
import os

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PLOT_ROOT = os.path.dirname(os.path.abspath(__file__))
HOUSEKEEPING_CFG = os.path.join(PLOT_ROOT, "housekeeping.cfg")


class InvalidPlotType(Exception):
    """Exception subclass to indicate an invalid plot type."""


def secs2time(secs: float, pos: int):  # pylint: disable=unused-argument
    """matplotlib.ticker formatter to convert seconds to a string displaying
    hours and minutes.
    """
    hrs = math.floor(secs / 60.0 / 60.0)
    mins = math.floor((secs - hrs * 60 * 60) / 60.0)
    return f"{hrs:02d}:{mins:02d}"


def get_formatter(formatter_name):
    """Create a formatter identified by name."""
    if formatter_name == "secs2time":
        formatter = matplotlib.ticker.FuncFormatter(secs2time)
    else:
        formatter = None

    return formatter


def plot_time_series(
    plot_filename, date, section, df
):  # pylint: disable=unused-argument
    """Render a time series plot into the given filename."""
    bottom = section.getfloat("min", fallback=None)
    top = section.getfloat("max", fallback=None)

    xtitle = section.get("xtitle", fallback=None)
    ytitle = section.get("ytitle", fallback=None)

    yvalues_name = section.get("yvalues", fallback=None)

    print(f"plotting time series '{yvalues_name}' to {plot_filename}")

    try:
        yvalues = df[yvalues_name].values
    except KeyError as e:
        print(f"column '{yvalues_name}' not found, skipping")
        return

    xvalues_name = section.get("xvalues", fallback=None)
    if xvalues_name is None:
        xvalues = np.arange(len(yvalues))
    else:
        try:
            xvalues = df[xvalues_name].values
        except KeyError as e:
            print(f"column '{xvalues_name}' not found, skipping")
            return

    title = section.get("title", fallback=None)

    xsize = section.getfloat("xsize", fallback="800")
    ysize = section.getfloat("ysize", fallback="300")
    dpi = 150
    xsize_inches = xsize / dpi
    ysize_inches = ysize / dpi

    fontsize = 6

    fig, ax = plt.subplots(nrows=1, ncols=1)  # , constrained_layout=True)
    fig.set_size_inches(xsize_inches, ysize_inches)

    ax.plot(xvalues, yvalues)

    if title is not None:
        ax.set_title(title, fontdict={"fontsize": 8})

    xtickformat = section.get("xtickformat", fallback=None)
    if xtickformat is not None:
        formatter = get_formatter(xtickformat)
        ax.xaxis.set_major_formatter(formatter)

    ax.xaxis.set_tick_params(labelsize=fontsize)
    ax.yaxis.set_tick_params(labelsize=fontsize)
    ax.yaxis.offsetText.set_fontsize(fontsize)

    ax.set_ylim(bottom=bottom, top=top)

    if xtitle is not None:
        ax.set_xlabel(xtitle, fontsize=fontsize)
    if ytitle is not None:
        ax.set_ylabel(ytitle, fontsize=fontsize)

    fig.tight_layout()
    plt.savefig(plot_filename, dpi=dpi)
    plt.close(fig)


def plot_scatter(plot_filename, date, section, df):
    """Render a scatter plot into the given filename.

    Not implemented yet.
    """


def dispatch_plot(date: str, section, df):
    """Send the given data to the correct renderer."""
    if "filename" not in section:
        return

    plot_type = section.get("type", fallback="timeseries").lower()

    plot_filename = section.get("filename")
    plot_filename = plot_filename.format(date=date)

    if plot_type == "timeseries":
        plot_time_series(plot_filename, date, section, df)
    elif plot_type == "scatter":
        plot_scatter(plot_filename, date, section, df)
    else:
        raise InvalidPlotType(
            f"invalid plot type '{plot_type}' in '{section.name}' plot"
        )


def plot(date: str, housekeeping_filename: str, skiprows: int = 0):
    """Plot every column in a housekeeping file."""
    options = configparser.ConfigParser()
    options.read(HOUSEKEEPING_CFG)

    df = pd.read_csv(housekeeping_filename, skiprows=skiprows)
    for plot_name in options.sections():
        try:
            dispatch_plot(date, options[plot_name], df)
        except InvalidPlotType as e:
            print(e)


if __name__ == "__main__":
    # plot("20211119", "20211119 ChroMag Housekeeping.csv", skiprows=6)
    plot("20220624", "20220624 ChroMag Housekeeping.csv")
