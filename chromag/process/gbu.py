# -*- coding: utf-8 -*-


"""Routines for deteriming the GBU status of a level 1 ChroMag file.

GBU determines the suitability of a level 1 file to be processed to level 2.
A bitmask indicates which conditions have failed the GBU process. If any
condition fails, the file is not processd.
"""

import os

from ..config import get_basedir
from ..file import ChroMagL1File
from ..logging import logger
from ..pipeline import step
from ..waveregions import available_waveregions


PASS = 0
FAIL = 1


def gbu_bitmask(gbu_name: str, gbu_names: list[str]) -> int:
    """Convert a string of GBU condition names separated with "|" to a GBU
    bitmask."""
    if gbu_name == "":
        return 0

    bitmask = 0
    for name in gbu_names.split("|"):
        try:
            bitmask |= 1 << gbu_names.index(name)
        except ValueError as e:
            logger.error(f"{name} is not in {'|'.join(gbu_names)}")
    return bitmask


def gbu_name(gbu_bitmask: int) -> str:
    """Convert a GBU bitmask into a string name."""
    name = "|".join(
        [
            condition_name
            for i, condition_name in enumerate(gbu_names)
            if gbu_bitmask & (1 << i)
        ]
    )
    return name


# [TODO]: example GBU condition

# [TODO]: whatever this should be
background_threshold = 1.0


def check_background(l0_file: ChroMagL1File) -> int:
    """Check to make sure the SGS system was tracking the sun."""
    # [TODO]: implement
    return PASS


check_background.name = "BKG"
check_background.description = f"check background is < {background_threshold}"


gbu_conditions = [check_background]
gbu_names = [c.name for c in gbu_conditions]
gbu_descriptions = [c.description for c in gbu_conditions]


@step(top=True)
def gbu_check(catalog):
    """Perform GBU check for a level 1 file."""
    for w in available_waveregions():
        for raw_file in catalog[catalog.is_science & (catalog.wave_region == w)]:
            # GBU only run on valid level 1 files that passed quality
            l1_file = raw_file.l1_file
            if l1_file is None:
                continue

            gbu_bitmask = 0
            for c, condition in enumerate(gbu_conditions):
                gbu_bitmask |= condition(l1_file) * (1 << c)

            l1_file.gbu_bitmask = gbu_bitmask


@step(top=True)
def write_gbu_log(catalog, wave_region: str, output_filename: str):
    """Write the GBU log for the given wave region."""
    column_names = ["Filename", "Reason"]
    column_widths = [40, 6]

    with open(output_filename, "w") as f:
        f.write(
            f"{column_names[0]:{column_widths[0]}s}{column_names[1]:{column_widths[1]}s}\n"
        )
        for raw_file in catalog[
            catalog.is_science & (catalog.wave_region == wave_region)
        ]:
            l1_file = raw_file.l1_file
            if l1_file is not None:
                l1_basename = os.path.basename(l1_file.get_filename("filename"))
                components = [
                    f"{l1_basename:{column_widths[0]}s}",
                    f"{l1_file.gbu_bitmask:{column_widths[1]}d}",
                ]
                f.write("".join(components) + "\n")
        f.write("\nGBU bitmask codes\n")
        f.write("Code    Description\n")
        for i, description in enumerate(gbu_descriptions):
            f.write(f"{1<<i:5d}   {description}\n")
    logger.info(f"wrote {os.path.basename(output_filename)}")


@step(top=True)
def write_gbu_logs(catalog, observing_day: str):
    """Write the GBU logs."""
    for w in available_waveregions():
        basename = f"{observing_day}.chromag.{w}.gbu.log"
        filename = os.path.join(
            get_basedir(observing_day, "process"), observing_day, "level1", basename
        )
        write_gbu_log(catalog, w, filename)
