# -*- coding: utf-8 -*-

"""Module containing the level 2 processing."""

from ..pipeline import step


@step()
def process(run):
    """Run the level 2 processing."""
    run.logger.info("L2 processing stuff...")
