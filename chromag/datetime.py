# -*- coding: utf-8 -*-

"""Utilities for handling dates/times.
"""

import math


def human_timedelta(timedelta):
    secs = timedelta.total_seconds()

    units = [("day", 60 * 60 * 24),
             ("hr", 60 * 60),
             ("min", 60),
             ("sec", 1)]
    parts = []
    for unit, mul in units:
        if secs / mul >= 1 or mul == 1:
            if mul > 1:
                n = int(math.floor(secs / mul))
                secs -= n * mul
            else:
                n = "%d" % secs
            parts.append("%s %s%s" % (n, unit, "" if n == 1 else "s"))
    return " ".join(parts)
