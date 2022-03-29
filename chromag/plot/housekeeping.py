# -*- coding: utf-8 -*-

import configparser
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PLOT_ROOT = os.path.dirname(os.path.abspath(__file__))
HOUSEKEEPING_CFG = os.path.join(PLOT_ROOT, "housekeeping.cfg")


class InvalidPlotType(Exception):
    pass


def plot_time_series(plot_filename, date, section, df):
    bottom = section.getfloat("min", fallback=None)
    top    = section.getfloat("max", fallback=None)

    xtitle = section.get("xtitle", fallback=None)
    ytitle = section.get("ytitle", fallback=None)

    yvalues_name = section.get("yvalues", fallback=None)
    yvalues = df[yvalues_name].values

    xvalues_name = section.get("xvalues", fallback=None)
    if xvalues_name is None:
        xvalues = np.arange(len(yvalues))
    else:
        xvalues = df[xvalues_name].values

    title = section.get("title", fallback=None)

    xsize = section.getfloat("xsize", fallback="800")
    ysize = section.getfloat("ysize", fallback="300")
    dpi = 150
    xsize_inches = xsize / dpi
    ysize_inches = ysize / dpi

    print(f"plotting time series '{yvalues_name}' to {plot_filename}")

    fontsize = 6

    fig, ax = plt.subplots(nrows=1, ncols=1, constrained_layout=True)
    fig.set_size_inches(xsize_inches, ysize_inches)
    ax.plot(xvalues, yvalues)
    if title is not None:
        ax.set_title(title, fontdict={"fontsize": 8})
    ax.xaxis.set_tick_params(labelsize=fontsize)
    ax.yaxis.set_tick_params(labelsize=fontsize)
    ax.set_ylim(bottom=bottom, top=top)
    if xtitle is not None:
        ax.set_xlabel(xtitle, fontsize=fontsize)
    if ytitle is not None:
        ax.set_ylabel(ytitle, fontsize=fontsize)
    plt.savefig(plot_filename, dpi=dpi)


def plot_scatter(plot_filename, date, section, df):
    pass


def dispatch_plot(date:str, section, df):
    if "filename" not in section: return

    type = section.get("type", fallback="timeseries")
    type = type.lower()

    plot_filename = section.get("filename")
    plot_filename = plot_filename.format(date=date)

    if type == "timeseries":
        plot_time_series(plot_filename, date, section, df)
    elif type == "scatter":
        plot_scatter(plot_filename, date, section, df)
    else:
        raise InvalidPlotType(f"invalid plot type '{type}' in '{section.name}' plot")


def plot(date:str, housekeeping_filename:str):
    """Plot every column in a housekeeping file.
    """
    options = configparser.ConfigParser()
    options.read(HOUSEKEEPING_CFG)

    df = pd.read_csv(housekeeping_filename, skiprows=6)
    for plot_name in options.sections():
        try:
            dispatch_plot(date, options[plot_name], df)
        except InvalidPlotType as e:
            print(e)


if __name__ == "__main__":
    plot("20211119", "20211119 ChroMag Housekeeping.csv")
