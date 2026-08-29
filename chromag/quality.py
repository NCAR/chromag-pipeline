# -*- coding: utf-8 -*-

"""Routines for deteriming the quality of a raw ChroMag file.

Quality determines the suitability of a raw file to be processed to level 1.
A bitmask indicates which conditions have failed the quality process. If any
condition fails, the file is not processd.
"""

import os

from .config import get_basedir
from .file import ChroMagRawFile
from .logging import logger
from .pipeline import step
from .waveregions import available_waveregions


PASS = 0
FAIL = 1


sgsloop_threshold = 0.99


def check_sgsloop(l0_file: ChroMagRawFile):
    """Check to make sure the SGS system was tracking the sun."""
    sgsloop = l0_file.primary_header["SGSLOOP"]
    if sgsloop is None:
        return PASS
    return PASS if sgsloop > sgsloop_threshold else FAIL


check_sgsloop.name = "SGSLOOP"
check_sgsloop.description = f"check SGSLOOP is > {sgsloop_threshold}"


def check_inout(l0_file: ChroMagRawFile):
    """Check to make sure hardward positions are either in or out."""
    # [TODO]: need to know correct position range for science files
    # potential keywords to check: CALP_POS, CAM_POS, COVR_POS, DIFF_POS,
    # HRF_POS, OSF_POS, TT_XPOS, TT_XSTD, TT_YPOS, TT_YSTD
    return PASS


check_inout.name = "INOUT"
check_inout.description = "check positions are in or out"


science_conditions = [check_sgsloop, check_inout]
science_quality_names = [c.name for c in science_conditions]
science_quality_descriptions = [c.description for c in science_conditions]


def sci_quality_name(quality_bitmask: int) -> str:
    """Convert a science quality bitmask into a string name."""
    quality_name = "|".join(
        [
            condition_name
            for i, condition_name in enumerate(science_quality_names)
            if quality_bitmask & 2**i
        ]
    )
    return quality_name


@step()
def sci_quality_check(l0_file: ChroMagRawFile):
    """Perform quality check for a raw file."""
    quality_bitmask = 0
    for c, condition in enumerate(science_conditions):
        quality_bitmask |= condition(l0_file) * 2**c

    return quality_bitmask


@step(top=True)
def write_quality_file(catalog, wave_region: str, output_filename: str):
    """Write the quality file for the given wave region."""
    column_names = ["Filename", "Reason"]
    column_widths = [40, 6]

    with open(output_filename, "w") as f:
        f.write(
            f"{column_names[0]:{column_widths[0]}s}{column_names[1]:{column_widths[1]}s}\n"
        )
        for file in catalog[catalog.is_science & (catalog.wave_region == wave_region)]:
            components = [
                f"{file.basename:{column_widths[0]}s}",
                f"{file.quality_bitmask:{column_widths[1]}d}",
            ]
            f.write("".join(components) + "\n")
        f.write("\nQuality bitmask codes\n")
        f.write("Code    Description\n")
        for i, description in enumerate(science_quality_descriptions):
            f.write(f"{2**i:5d}   {description}\n")
    logger.info(f"wrote {os.path.basename(output_filename)}")


@step(top=True)
def write_quality_files(catalog, observing_day: str):
    for w in available_waveregions():
        basename = f"{observing_day}.chromag.{w}.quality.log"
        filename = os.path.join(
            get_basedir(observing_day, "process"), observing_day, "level1", basename
        )
        write_quality_file(catalog, w, filename)
