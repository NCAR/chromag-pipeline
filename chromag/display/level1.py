# -*- coding: utf-8 -*-

"""Module for making displays of level 1 images
"""

import os

import matplotlib.pyplot as plt
import numpy as np

from ..datetime import datetime2dateobs
from ..file import ChroMagL1File, create_dir
from ..lines import property
from ..logging import logger


def write_intensity_image(l1_file: ChroMagL1File):
    """Write a quicklook PNG file displaying the level 1 intensity."""
    output_filename = l1_file.get_filename("i_quicklook")
    l1_dir = os.path.dirname(output_filename)
    if not os.path.isdir(l1_dir):
        create_dir(l1_dir, basepath=l1_dir)

    imdata = l1_file.data[0, :, :].squeeze()

    # [TODO]: mask

    display_min = property(l1_file.wave_region, "display_i_min")
    display_max = property(l1_file.wave_region, "display_i_max")
    display_exp = property(l1_file.wave_region, "display_i_exp")
    display_gamma = property(l1_file.wave_region, "display_i_gamma")
    colormap = property(l1_file.wave_region, "colormap")
    ionization = property(l1_file.wave_region, "ionization")

    imdata = np.clip(imdata, a_min=display_min, a_max=display_max) ** display_exp

    dpi = 100.0
    px = 1.0 / dpi
    fig = plt.figure(frameon=False)
    fig.set_size_inches(imdata.shape[1] * px, imdata.shape[0] * px)

    ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
    ax.set_axis_off()
    fig.add_axes(ax)

    fontsize = 18
    left_pad = 15.0
    line_height = 2.0 * fontsize
    start_height = 2.0 * line_height
    im = ax.imshow(
        imdata,
        vmin=display_min**display_exp,
        vmax=display_max**display_exp,
        cmap=colormap,
        aspect="auto",
    )
    ax.text(left_pad, start_height, "MLSO ChroMag", color="w", fontsize=fontsize)
    ax.text(
        left_pad,
        start_height + line_height,
        datetime2dateobs(l1_file.date_obs),
        color="w",
        fontsize=fontsize,
    )
    ax.text(
        left_pad,
        start_height + 2 * line_height,
        f"{ionization} {l1_file.wavelength:0.3f} nm",
        color="w",
        fontsize=fontsize,
    )
    ax.text(
        left_pad,
        start_height + 3 * line_height,
        rf"$\mathrm{{Intensity}}^{{{display_exp}}}$",
        color="w",
        fontsize=fontsize,
    )
    ax.text(
        left_pad,
        start_height + 4 * line_height,
        f"min/max: ${display_min}^{{{display_exp}}}-{display_max}^{{{display_exp}}}$, gamma: {display_gamma:0.1f}",
        color="w",
        fontsize=fontsize,
    )

    cax = fig.add_axes([0.02, 0.05, 0.25, 0.02])
    cbar = fig.colorbar(im, cax=cax, orientation="horizontal")
    cbar.ax.tick_params(color="w", labelcolor="w", labelsize=15)
    cbar.outline.set_edgecolor("w")

    plt.savefig(output_filename, dpi=dpi)
    plt.close(fig)

    output_basename = os.path.basename(output_filename)
    logger.debug(f"wrote {output_basename}")


def write_iquv_image(l1_file: ChroMagL1File):
    """Write a quicklook PNG file displaying the level 1 intensity."""
    output_filename = l1_file.get_filename("iquv_quicklook")
    l1_dir = os.path.dirname(output_filename)
    if not os.path.isdir(l1_dir):
        create_dir(l1_dir, basepath=l1_dir)

    state_name = ["I", "Q", "U", "V"]
    display_name = {"I": "i", "Q": "qu", "U": "qu", "V": "v"}

    ionization = property(l1_file.wave_region, "ionization")

    reduce_factor = 4
    dpi = 100.0
    px = 1.0 / dpi

    nx = l1_file.data.shape[2]
    ny = l1_file.data.shape[1]

    # [TODO]: mask

    fontsize = 10
    left_pad = 15.0 * reduce_factor
    line_height = 2.0 * fontsize * reduce_factor

    fig = plt.figure(frameon=False)
    fig.set_size_inches(2 * nx * px / reduce_factor, 2 * ny * px / reduce_factor)

    for p in range(l1_file.data.shape[0]):
        sname = state_name[p]

        ax = plt.Axes(fig, [0.5 * (p % 2), 0.5 - 0.5 * (p // 2), 0.5, 0.5])
        ax.set_axis_off()
        fig.add_axes(ax)

        dname = display_name[sname]
        display_min = property(l1_file.wave_region, f"display_{dname}_min")
        display_max = property(l1_file.wave_region, f"display_{dname}_max")
        display_exp = property(l1_file.wave_region, f"display_{dname}_exp")
        display_gamma = property(l1_file.wave_region, f"display_{dname}_gamma")
        colormap = property(l1_file.wave_region, "colormap")

        imdata = l1_file.data[p, :, :].squeeze()
        imdata = np.clip(imdata, a_min=display_min, a_max=display_max) ** display_exp

        im = ax.imshow(
            imdata,
            vmin=display_min**display_exp,
            vmax=display_max**display_exp,
            cmap=colormap,
            aspect="auto",
        )
        if p == 0:
            ax.text(left_pad, line_height, "MLSO ChroMag", color="w", fontsize=fontsize)
            ax.text(
                left_pad,
                2 * line_height,
                f"{ionization} {l1_file.wavelength:0.3f} nm",
                color="w",
                fontsize=fontsize,
            )
        if abs(display_exp - 1.0) < 0.001:
            state_text = sname
            scaling_text = (
                f"min/max: ${display_min}-{display_max}$, gamma: {display_gamma:0.1f}"
            )
        else:
            state_text = rf"$\mathrm{{{sname}}}^{{{display_exp}}}$"
            scaling_text = f"min/max: ${display_min}^{{{display_exp}}}-{display_max}^{{{display_exp}}}$, gamma: {display_gamma:0.1f}"
        ax.text(
            left_pad,
            ny - 2 * line_height,
            state_text,
            color="w",
            fontsize=fontsize,
        )
        ax.text(
            left_pad,
            ny - line_height,
            scaling_text,
            color="w",
            fontsize=fontsize,
        )

    plt.savefig(output_filename, dpi=dpi)
    plt.close(fig)

    output_basename = os.path.basename(output_filename)
    logger.debug(f"wrote {output_basename}")
