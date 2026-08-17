# -*- coding: utf-8 -*-

"""Module handling reading/writing ChroMag files."""

import grp
import os
import shutil
import tarfile

from ..logging import logger


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
    logger.info(f"created ~~~{dirname}")


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
