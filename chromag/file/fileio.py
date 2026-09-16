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


def human_bytes(n_bytes: int, n_decimals: int = 1) -> str:
    """Convert an integer number of bytes to a string representing that in B,
    KB, MB, GB, etc.
    """
    if n_bytes == 0:
        return "0 B"
    sizenames = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    n_sizes = len(sizenames)
    i = math.floor(math.log(n_bytes, 1024))
    p = 1 << (10 * i)  # 1024^i = (2^10)^i = 2^(10*i), 2^n = 1 << n
    if i >= n_sizes:
        s = round(n_bytes / p * 1024 ** (n_sizes - i + 1), n_decimals)
        units = sizenames[-1]
    else:
        s = round(n_bytes / p, n_decimals)
        units = sizenames[i]
    return f"{s} {units}"


def create_dir(cdir: str, /, *, basepath: str = None):
    """Create directory, making sure is in the cordyn group. If present,
    `basepath` specifies the base of the `dir` name that can be omitted in the
    log messages. Doesn't create directory if it already exists.
    """
    if not os.path.isdir(cdir):
        if basepath is not None:
            dirname = cdir.removeprefix(basepath)
        else:
            dirname = cdir
        os.mkdir(dir)
        logger.debug(f"created ~~~{dirname}")

    group_id = os.stat(cdir).st_gid
    cordyn_id = grp.getgrnam("cordyn").gr_gid
    if group_id != cordyn_id:
        os.chown(dir, -1, cordyn_id)
        logger.debug(f"changed group ID from {group_id} to {cordyn_id}")


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
    with open(tarlist_filename, "w", encoding="utf-8") as f:
        for n in names:
            f.write(f"{n}\n")


def write_fits_file(output_filename: str, data: np.ndarray, primary_header):
    """Write a FITS file with only a primary extension."""
    hdu = fits.PrimaryHDU(data=data)
    hdu.header = primary_header
    hdu.writeto(output_filename, overwrite=True)
