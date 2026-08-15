# -*- coding: utf-8 -*-

"""Module handling reading/writing ChroMag files."""

import grp
import os
import shutil
import tarfile

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


def make_tarball(tarball_filename: str, basedir: str, directory: str):
    """Make a tarball of the given name. `directory` is the path (relative to
    `basedir`) to the directory to tar.
    """
    tarball_basename = tarball_filename.removesuffix(".tar.gz")
    shutil.make_archive(
        tarball_basename, "gztar", basedir, directory, True, False, None, None, logger
    )


def make_tarlist(tar_filename: str, tarlist_filename: str):
    """Write a tarlist for the given tar file. Assumes all the files are in a
    directory, so eliminates the directory entry and the directory name in the
    path of the other entries.
    """
    with tarfile.open(tar_filename) as f:
        names = f.getnames()
    with open(tarlist_filename, "w") as f:
        for n in names[1:]:  # assume first entry is the directory name
            f.write(f"{os.path.basename(n)}\n")
