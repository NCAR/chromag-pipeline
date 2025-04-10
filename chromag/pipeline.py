# -*- coding: utf-8 -*-

"""Class for representing a pipeline run, decorator for pipeline steps, etc.
"""

import datetime
import functools
import logging

from .calibration.photometric import photometric_calibration
from .datetime import human_timedelta


logger = logging.getLogger("ChroMag")


def step():
    def actual_decorator(func):
        @functools.wraps(func)
        def func_wrapper(*args, skip: bool = False, **kwargs):
            e = {"func": func}

            if skip:
                if logger:
                    logger.info(f"skipping {func.__name__}", extra=e)
            else:
                if logger:
                    logger.info(f"starting {func.__name__}", extra=e)
                    start_dt = datetime.datetime.now()
                value = func(*args, **kwargs)
                if logger:
                    end_dt = datetime.datetime.now()
                    time_interval = end_dt - start_dt
                    human_time = human_timedelta(time_interval)
                    logger.info(f"done with {func.__name__}: {human_time}", extra=e)
                return value

        return func_wrapper

    return actual_decorator


class Run:
    def __init__(self, date: str, mode: str, logger: logging.Logger):
        self.date = date
        self.mode = mode
        self.logger = logger
        self._catalog = None
        self._photometric_calibration = None

    @property
    def catalog(self):
        return self._catalog

    @catalog.setter
    def catalog(self, catalog):
        self._catalog = catalog

    @property
    def photometric_calibration(self):
        return self._photometric_calibration

    @photometric_calibration.setter
    def photometric_calibration(self, photometric_calibration: photometric_calibration):
        self._photometric_calibration = photometric_calibration
