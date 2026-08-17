# -*- coding: utf-8 -*-

"""Module handling reading/writing ChroMag level 1 files."""

import os

from astropy.io import fits

from .file import ChroMagL1File
from .fileio import create_dir

from ..logging import logger


def write_l1_file(l1_file: ChroMagL1File):
    """Write a level 1 ChroMag file."""
    output_filename = l1_file.get_filename("filename")
    l1_dir = os.path.dirname(output_filename)
    if not os.path.isdir(l1_dir):
        logger.info("creating level1 directory")
        create_dir(l1_dir, basepath=l1_dir)

    hdu = fits.PrimaryHDU(data=l1_file.data)
    hdu.header = l1_file.primary_header
    hdu.writeto(output_filename, overwrite=True)

    output_basename = os.path.basename(output_filename)
    logger.info(f"wrote {output_basename}...")
