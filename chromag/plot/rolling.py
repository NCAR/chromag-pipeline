# -*- coding: utf-8 -*-

"""Module to plot engineering data from the last `n` days of observations. Data
to be plotted here must be stored in a database table to be retrieved for
plotting.
"""

import os

from ..config import get_option
from ..database import query
from ..datetime import decompose_date
from ..logging import logger
from ..pipeline import step


@step(top=True)
def write_rolling_plots(date_run):
    """Write the rolling plots."""
    eng_basedir = get_option("engineering", "basedir")
    if eng_basedir is not None:
        eng_dir = os.path.join(eng_basedir, *decompose_date(date_run.observing_day))
        if not os.path.isdir(eng_dir):
            os.makedirs(eng_dir)
    else:
        logger.warn("engineering.basedir not set, skipping rolling plots")

    # [TODO]: call various rolling plotting routines here
