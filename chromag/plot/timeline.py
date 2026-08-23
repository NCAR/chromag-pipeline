# -*- coding: utf-8 -*-

"""Module to plot housekeeping engineering data.
"""

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, FixedLocator

from ..datetime import obsday_hours2str
from ..lines import available_lines, line_property

START_TIME = 6  # 6 am HST
END_TIME = 18  # 6 pm HST


def obsday_hours_formatter(obsday_hours: float, pos: float) -> str:
    """Format an obsday_hours (fractional hours) value into a formatted
    string.
    """
    return obsday_hours2str(obsday_hours)


def write_timeline(output_filename: str, catalog, binsize: int = 15):
    """Create a timeline of the observations for the day."""
    wave_regions = available_lines()
    figsize = (7, 2)
    label_fontsize = 8
    n_rows = len(wave_regions) + 1  # one for every wave region plus darks
    n_cols = 1
    fig, axes = plt.subplots(
        n_rows, n_cols, sharex=True, figsize=figsize, layout="constrained"
    )

    for i, w in enumerate(wave_regions):
        wave_files = catalog[catalog.wave_region == w]
        wave_color = line_property(w, "color")

        axes[i].hist(
            wave_files.obsday_hours,
            bins=(END_TIME - START_TIME) * 10,
            range=(START_TIME, END_TIME),
            color=wave_color,
        )
        axes[i].set_ylim(0, 30)
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
        bins=(END_TIME - START_TIME) * 10,
        range=(START_TIME, END_TIME),
        color="#606060",
    )
    axes[dark_index].set_ylim(0, 15)
    axes[dark_index].set_yticks([])
    axes[dark_index].tick_params(left=False, labelsize=label_fontsize)
    axes[dark_index].spines["top"].set_visible(False)
    axes[dark_index].spines["left"].set_visible(False)
    axes[dark_index].spines["right"].set_visible(False)
    axes[dark_index].spines["bottom"].set_color("#d0d0d0")
    axes[dark_index].set_ylabel("darks", fontsize=label_fontsize, rotation=0)
    axes[dark_index].xaxis.set_major_locator(FixedLocator(range(6, 19, 2)))
    axes[dark_index].xaxis.set_major_formatter(FuncFormatter(obsday_hours_formatter))
    axes[dark_index].set_xlabel("observing day [HST]", fontsize=label_fontsize)

    plt.savefig(output_filename)
    plt.close(fig)
