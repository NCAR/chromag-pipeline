# -*- coding: utf-8 -*-

"""Routines for deteriming the quality of a raw ChroMag file.

Quality determines the suitability of a raw file to be processed to level 1.
A bitmask indicates which conditions have failed the quality process. If any
condition fails, the file is not processd.
"""

from .file import ChroMagRawFile
from .pipeline import step

PASS = 0
FAIL = 1


def sci_condition1(l0_file: ChroMagRawFile):
    """Test condition that randomly passes 95% of the time. Not a real
    condition."""
    import random

    x = random.random()
    return PASS if x < 0.90 else FAIL


sci_condition1.name = "condition1"


def sci_condition2(l0_file: ChroMagRawFile):
    """Test condition that randomly passes 95% of the time. Not a real
    condition."""
    import random

    x = random.random()
    return PASS if x < 0.90 else FAIL


sci_condition2.name = "condition2"


def sci_condition3(l0_file: ChroMagRawFile):
    """Test condition that randomly passes 95% of the time. Not a real
    condition."""
    import random

    x = random.random()
    return PASS if x < 0.90 else FAIL


sci_condition3.name = "condition3"


science_conditions = [sci_condition1, sci_condition2, sci_condition3]

science_quality_names = [c.name for c in science_conditions]


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
