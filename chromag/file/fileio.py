# -*- coding: utf-8 -*-

"""Module handling reading/writing ChroMag files."""

import grp
import os

from astropy.io import fits

from .file import ChroMagL1File
from ..logging import logger


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

    # [TODO]: write intensity quicklook

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
