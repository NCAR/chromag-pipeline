# -*- coding: utf-8 -*-

"""Module handling reading/writing ChroMag files."""

import grp
import os

from astropy.io import fits

from .file import ChroMagL1File
from .logging import logger


def write_l1_file(l1_file: ChroMagL1File):
    """Write a level 1 ChroMag file."""
    l1_dir = os.path.dirname(l1_file.filename)
    if not os.path.isdir(l1_dir):
        logger.info("creating level1 directory")
        create_dir(l1_dir)

    hdu = fits.PrimaryHDU(data=l1_file.data)
    hdu.header = l1_file.primary_header
    hdu.writeto(l1_file.filename, overwrite=True)

    logger.info(f"wrote {l1_file.basename}...")


def create_dir(dir: str):
    """Create directory, making sure is in the cordyn group."""
    os.mkdir(dir)
    gid = grp.getgrnam("cordyn").gr_gid
    os.chown(dir, -1, gid)
