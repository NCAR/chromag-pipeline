# -*- coding: utf-8 -*-

"""Module containing the level 1 processing."""

from ..pipeline import step


@step()
def run_l1_process(run):
    """Run the level 1 processing."""
    run.logger.debug("L1 processing...")
