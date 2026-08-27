# -*- coding: utf-8 -*-

"""Module handling reading/writing ChroMag level 1 files."""

import os

from astropy.io import fits

from .file import ChroMagL1File
from .fileio import create_dir, write_fits_file

from ..logging import logger


# [TODO]: it would be good to make this a pipeline.step if I can get around the
# circular imports
def write_l1_file(l1_file: ChroMagL1File):
    """Write a level 1 ChroMag file."""
    output_filename = l1_file.get_filename("filename")
    l1_dir = os.path.dirname(output_filename)
    if not os.path.isdir(l1_dir):
        create_dir(l1_dir, basepath=l1_dir)

    write_fits_file(output_filename, l1_file.data, l1_file.primary_header)

    output_basename = os.path.basename(output_filename)
    logger.debug(f"wrote {output_basename}")


# [TODO]: it would be good to make this a pipeline.step if I can get around the
# circular imports
def write_l1_intermediate(l1_file: ChroMagL1File, name: str):
    """Write a partially processed level 1 file. The `name` argument indicates
    which step of the processing was last completed.
    """
    logger.debug(f"writing {name} intermediate product")

    output_filename = l1_file.get_filename("intermediate", intermediate_step=name)
    intermediate_dir = os.path.dirname(output_filename)
    if not os.path.isdir(intermediate_dir):
        create_dir(intermediate_dir, basepath=os.path.dirname(intermediate_dir))

    write_fits_file(output_filename, l1_file.data, l1_file.primary_header)

    output_basename = os.path.basename(output_filename)
    logger.debug(f"wrote {output_basename}")
