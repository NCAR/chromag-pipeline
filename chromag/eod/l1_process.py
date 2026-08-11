# -*- coding: utf-8 -*-

"""Module containing the level 1 processing."""

from ..pipeline import step
from ..file import ChroMagL1File
from ..fileio import write_l1_file


@step()
def run_l1_process(run):
    """Run the level 1 processing."""

    # [TODO]: need to do this by line?

    run.logger.info("L1 processing...")

    # loop through science files and perform the following steps:
    for raw_file in run.catalog[run.catalog.is_science]:
        run.logger.info(f"processing {raw_file.basename}")

        l1_file = ChroMagL1File(raw_file)

        # apply non-linearity camera correction (if necessary)
        # initial quality check
        #   discard really bad data
        # apply camera corrections, i.e., hot pixels, etc.

        # apply dark subtraction
        # [TODO]: move to subroutine
        # get master dark of same exposure time
        dark = run.calibration.get_dark(raw_file.exposure)
        for i in range(4):
            l1_file.data[i, :, :] -= dark.squeeze()

        # apply gain
        # demodulation
        # off-band leakage subtraction
        # distortion correction
        # rotate solar North up
        # mask outer field of view
        # polarimetric coordinate transformation
        # [TODO]: write output (FITS, PNG, etc.)
        write_l1_file(l1_file)
        del l1_file.data

        # some sort of quality assessment TBD
        #   based on simple assessment of light level etc. in Level 0 data
        #   possibly use data from Tip/Tilt system
        #   more sophisticated metrics from Level1B data that may reject data
        #     for some higher-level uses but not others
