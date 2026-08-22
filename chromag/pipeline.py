# -*- coding: utf-8 -*-

"""Class for representing a pipeline run, decorator for pipeline steps, etc.
"""

import datetime
import functools
import logging

from .calibration import Calibration
from .datetime import human_timedelta
from .file import write_l1_intermediate
from .logging import logger, null_logger_func


def step(top=False):
    """Function for decorating pipeline steps that logs basic information about
    the step, e.g., start it started/ended, how long it took. The `top`
    argument indicates whether it is a top-level step, with an INFO logging
    level, or not, with a DEBUG logging level.
    """

    def actual_decorator(func):
        @functools.wraps(func)
        def func_wrapper(
            *args,
            skip: bool = False,
            intermediate: bool = False,
            **kwargs,
        ):
            e = {"func": func}
            if logger is None:
                logger_func = null_logger_func
            else:
                logger_func = logger.info if top else logger.debug

            if skip:
                logger_func(f"skipped {func.__name__}", extra=e)
                return None
            else:
                logger_func(f"starting {func.__name__}...", extra=e)
                start_dt = datetime.datetime.now()

                value = func(*args, **kwargs)
                if intermediate:
                    write_l1_intermediate(args[1], func.__name__)

                end_dt = datetime.datetime.now()
                time_interval = end_dt - start_dt
                human_time = human_timedelta(time_interval)
                logger_func(f"done with {func.__name__}: {human_time}", extra=e)
                return value

        return func_wrapper

    return actual_decorator


class Run:
    """A class representing a pipeline run on a given observing day."""

    def __init__(self, observing_day: str, mode: str):
        self.observing_day = observing_day
        self.mode = mode
        self._catalog = None
        self._calibration = None

    @property
    def catalog(self):
        return self._catalog

    @catalog.setter
    def catalog(self, catalog):
        self._catalog = catalog

    @property
    def calibration(self):
        return self._calibration

    @calibration.setter
    def calibration(self, calibration: Calibration):
        self._calibration = calibration
