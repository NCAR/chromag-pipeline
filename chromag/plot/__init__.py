# -*- coding: utf-8 -*-

"""Handle plotting."""

from .daily import daily_plots
from .timeline import write_timeline

from ..pipeline import step


@step(top=True)
def engineering_plots(date_run):
    daily_plots(date_run)
