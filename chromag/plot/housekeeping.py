# -*- coding: utf-8 -*-

import configparser
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PLOT_ROOT = os.path.dirname(os.path.abspath(__file__))
HOUSEKEEPING_CFG = os.path.join(PLOT_ROOT, "housekeeping.cfg")


def plot_time_series(plot_filename, column_name, df, options):
    bottom = options.getfloat("min", fallback=None)
    top    = options.getfloat("max", fallback=None)
    xtitle = options.get("xtitle", fallback=None)
    ytitle = options.get("ytitle", fallback=None)
    yvalues = df[column_name].values
    xvalues_name = options.get("xvalues", fallback=None)

    if xvalues_name is None:
        xvalues = np.arange(len(yvalues))
    else:
        xvalues = df[xvalues_name].values

    print(f"plot '{column_name}' to {plot_filename} from {bottom} to {top}")

    fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.plot(xvalues, yvalues)
    ax.set_ylim(bottom=bottom, top=top)
    if xtitle is not None:
        ax.set_xlabel(xtitle)
    if ytitle is not None:
        ax.set_ylabel(ytitle)
    plt.savefig(plot_filename)


def plot(date:str, housekeeping_filename:str):
    """Plot every column in a housekeeping file.
    """
    options = configparser.ConfigParser()
    options.read(HOUSEKEEPING_CFG)

    df = pd.read_csv(housekeeping_filename, skiprows=6)
    for column_name in df:
        if "filename" not in options[column_name]: continue

        plot_filename = options.get(column_name, "filename")
        plot_filename = plot_filename.format(date=date)

        plot_time_series(plot_filename, column_name, df, options[column_name])


if __name__ == "__main__":
    plot("20211119", "20211119 ChroMag Housekeeping.csv")
