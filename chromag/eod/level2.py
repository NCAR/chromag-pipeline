# -*- coding: utf-8 -*-

"""Module containing the level 2 processing."""

from ..pipeline import step


@step()
def process(run):
    """Run the level 2 processing."""
    process_basedir = get_basedir(run.observing_day, "process")
    l2_dir = os.path.join(process_basedir, run.observing_day, "level2")
    if not os.path.isdir(l2_dir):
        create_dir(l2_dir)
        logger.info("created level2 directory")

    run.logger.info("L2 processing...")
