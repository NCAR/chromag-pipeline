# -*- coding: utf-8 -*-

"""Utilities for handling dates/times.
"""

import math


def human_timedelta(timedelta):
    """Create a human-readable string for a timedelta, for example, like
    "2 days 4 hrs 10 mins 5 secs".
    """
    secs = timedelta.total_seconds()
    decimals = max(0, -math.ceil(math.log10(secs)) + 3)
    secs_format = f"%0.{decimals}f"

    # secs_format = "%0.3f" if secs < 1.0 else "%0.2f" if secs < 10.0 else "%0.1f"

    units = [("day", 60 * 60 * 24), ("hr", 60 * 60), ("min", 60), ("sec", 1)]
    parts = []
    for unit, mul in units:
        if secs / mul >= 1 or mul == 1:
            if mul > 1:
                n = int(math.floor(secs / mul))
                secs -= n * mul
            else:
                n = secs_format % secs
            parts.append("%s %s%s" % (n, unit, "" if n == 1 else "s"))
    return " ".join(parts)
