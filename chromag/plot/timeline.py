# -*- coding: utf-8 -*-

"""Module to plot housekeeping engineering data.
"""

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, FixedLocator

from ..datetime import obsday_hours2str
from ..lines import available_lines, line_property

START_TIME = 6  # 6 am HST
END_TIME = 18  # 6 pm HST
BINS_PER_HOUR = 6  # bins are 10 minutes
MAX_FILES_PER_BIN = 100


def obsday_hours_formatter(obsday_hours: float, pos: float) -> str:
    """Format an obsday_hours (fractional hours) value into a formatted
    string.
    """
    return obsday_hours2str(obsday_hours)


def darken(color: str, factor: float = 0.5) -> str:
    """Darken the red, blue, green components of a color by the given factor.
    The color must be specified as "#RRGGBB".
    """
    r = max([int(factor * int(color[1:3], 16)), 0])
    g = max([int(factor * int(color[3:5], 16)), 0])
    b = max([int(factor * int(color[5:7], 16)), 0])
    return f"#{r:02x}{g:02x}{b:02x}"


def write_timeline(output_filename: str, catalog, binsize: int = 15):
    """Create a timeline of the observations for the day."""
    wave_regions = available_lines()
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
        wave_color = line_property(w, "color")
        # [TODO]: to add flats/cal files:
        # - change histtype to "stepfilled"
        # - pass [sci_files, flat_files, cal_files]
        # - pass color=[sci_color, flat_color, cal_color]
        # - use alpha=
        # [TODO]: might need to do histogram separately so that I can determine
        # the MAX_FILES_PER_BIN for this day because I think that it could be
        # over 600 files in 10 minutes, at least theoretically
        axes[i].hist(
            wave_files.obsday_hours,
            bins=(END_TIME - START_TIME) * BINS_PER_HOUR,
            range=(START_TIME, END_TIME),
            color=wave_color,
            edgecolor=darken(wave_color, factor=edge_darkening_factor),
            histtype="stepfilled",
        )
        axes[i].set_ylim(0, MAX_FILES_PER_BIN)
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
        bins=(END_TIME - START_TIME) * BINS_PER_HOUR,
        range=(START_TIME, END_TIME),
        color="#606060",
        edgecolor=darken("#606060", factor=edge_darkening_factor),
        histtype="stepfilled",
    )
    axes[dark_index].set_ylim(0, MAX_FILES_PER_BIN)
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
