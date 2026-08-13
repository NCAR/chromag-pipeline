# -*- coding: utf-8 -*-

"""Module handling reading/writing ChroMag files."""

import grp
import os

from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np

from ..datetime import datetime2dateobs
from .file import ChroMagL1File
from ..logging import logger
from ..lines import property


def write_l1_file(l1_file: ChroMagL1File):
    """Write a level 1 ChroMag file."""
    output_filename = l1_file.get_filename("filename")
    l1_dir = os.path.dirname(output_filename)
    if not os.path.isdir(l1_dir):
        logger.info("creating level1 directory")
        create_dir(l1_dir)

    hdu = fits.PrimaryHDU(data=l1_file.data)
    hdu.header = l1_file.primary_header
    hdu.writeto(output_filename, overwrite=True)

    output_basename = os.path.basename(output_filename)
    logger.info(f"wrote {output_basename}...")


def create_dir(dir: str):
    """Create directory, making sure is in the cordyn group."""
    os.mkdir(dir)
    gid = grp.getgrnam("cordyn").gr_gid
    os.chown(dir, -1, gid)


def write_l1_intensity_image(l1_file: ChroMagL1File):
    """Write a quicklook PNG file displaying the level 1 intensity."""
    output_filename = l1_file.get_filename("i_quicklook")
    l1_dir = os.path.dirname(output_filename)
    if not os.path.isdir(l1_dir):
        logger.info("creating level1 directory")
        create_dir(l1_dir)

    imdata = l1_file.data[0, :, :].squeeze()

    # [TODO]: mask

    display_min = property(l1_file.wave_region, "display_i_min")
    display_max = property(l1_file.wave_region, "display_i_max")
    display_exp = property(l1_file.wave_region, "display_i_exp")
    display_gamma = property(l1_file.wave_region, "display_i_gamma")

    imdata = np.clip(imdata, a_min=display_min, a_max=display_max) ** display_exp

    dpi = 100.0
    px = 1.0 / dpi
    fig = plt.figure(frameon=False)
    fig.set_size_inches(imdata.shape[1] * px, imdata.shape[0] * px)

    ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
    ax.set_axis_off()
    fig.add_axes(ax)

    fontsize = 18
    left_pad = 10.0
    start_height = 100.0
    line_height = 40.0
    im = ax.imshow(
        imdata, vmin=display_min, vmax=display_max, cmap="Greys_r", aspect="auto"
    )
    ax.text(left_pad, start_height, "MLSO ChroMag", color="w", size=fontsize)
    ax.text(
        left_pad,
        start_height + line_height,
        datetime2dateobs(l1_file.date_obs),
        color="w",
        size=fontsize,
    )
    ax.text(
        left_pad,
        start_height + 2 * line_height,
        rf"$\mathrm{{Intensity}}^{{{display_exp}}}$",
        color="w",
        size=fontsize,
    )
    ax.text(
        left_pad,
        start_height + 3 * line_height,
        f"min/max: ${display_min}^{{{display_exp}}}-{display_max}^{{{display_exp}}}$, gamma: {display_gamma:0.1f}",
        color="w",
        size=fontsize,
    )
    # [TODO]: add colorbar

    plt.savefig(output_filename, dpi=dpi)
    plt.close(fig)

    output_basename = os.path.basename(output_filename)
    logger.info(f"wrote {output_basename}...")


def write_l1_iquv_image(l1_file: ChroMagL1File):
    """Write a quicklook PNG file displaying the level 1 intensity."""
    output_filename = l1_file.get_filename("iquv_quicklook")
    l1_dir = os.path.dirname(output_filename)
    if not os.path.isdir(l1_dir):
        logger.info("creating level1 directory")
        create_dir(l1_dir)

    # [TODO]: write IQUV quicklook

    output_basename = os.path.basename(output_filename)
    logger.info(f"wrote {output_basename}...")
