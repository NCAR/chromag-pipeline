# -*- coding: utf-8 -*-

"""Module containing the level 1 processing."""

from ..pipeline import step


@step()
def run_l1_process(run):
    """Run the level 1 processing."""

    # [TODO]: need to do this by line?

    run.logger.debug("L1 processing...")

    # loop through science files and perform the following steps:
    for file in run.catalog[run.catalog.is_science]:
        run.logger.info(f"processing {file}")
        # apply non-linearity camera correction (if necessary)
        # initial quality check
        #   discard really bad data
        # apply camera corrections, i.e., hot pixels, etc.
        # [TODO]: apply dark subtraction
        # apply gain
        # demodulation
        # off-band leakage subtraction
        # distortion correction
        # rotate solar North up
        # mask outer field of view
        # polarimetric coordinate transformation
        # [TODO]: write output (FITS, PNG, etc.)
        # some sort of quality assessment TBD
        #   based on simple assessment of light level etc. in Level 0 data
        #   possibly use data from Tip/Tilt system
        #   more sophisticated metrics from Level1B data that may reject data
        #     for some higher-level uses but not others
        pass
