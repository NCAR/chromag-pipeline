# -*- coding: utf-8 -*-

"""Module handling reading/writing ChroMag files."""

import grp
import math
import os
import shutil
import tarfile

from astropy.io import fits
import numpy as np

from ..logging import logger


def human_bytes(n_bytes: int) -> str:
    if n_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(n_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(n_bytes / p, 2)
    return f"{s} {size_name[i]}"


def create_dir(dir: str, /, *, basepath: str = None):
    """Create directory, making sure is in the cordyn group. If present,
    `basepath` specifies the base of the `dir` name that can be omitted in the
    log messages.
    """
    if basepath is not None:
        dirname = dir.removeprefix(basepath)
    else:
        dirname = dir
    os.mkdir(dir)
    gid = grp.getgrnam("cordyn").gr_gid
    os.chown(dir, -1, gid)
    logger.debug(f"created ~~~{dirname}")


def make_tarball(tarball_filename: str, basedir: str, directory: str):
    """Make a tarball of the given name. `directory` is the path (relative to
    `basedir`) to the directory to tar.
    """
    tarball_basename = tarball_filename.removesuffix(".tar.gz")
    return shutil.make_archive(
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
        for n in names:
            f.write(f"{n}\n")


def read_rawheader(filename: str):
    """Read the primary header of a raw ChroMag FITS file."""
    with fits.open(filename) as f:
        primary_header = f[0].header

    # [TODO]: repair header from known epoch-based issues

    return primary_header


def read_rawdata(filename: str):
    """Read the data from raw ChroMag FITS file."""
    with fits.open(filename) as f:
        data = f[0].data.astype(np.float32)

    # [TODO]: repair data from known epoch-based issues

    return data


def write_fits_file(output_filename: str, data: np.ndarray, primary_header):
    """Write a FITS file with only a primary extension."""
    hdu = fits.PrimaryHDU(data=data)
    hdu.header = primary_header
    hdu.writeto(output_filename, overwrite=True)
