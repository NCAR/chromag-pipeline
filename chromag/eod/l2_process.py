# -*- coding: utf-8 -*-

"""Module containing the level 2 processing."""

from ..pipeline import step


@step()
def run_l2_process(run):
    run.logger.debug("L2 processing stuff...")
