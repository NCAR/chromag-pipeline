# -*- coding: utf-8 -*-

"""Utilities for handling dates/times.
"""

import datetime
import math


def human_timedelta(timedelta: datetime.timedelta) -> str:
    """Create a human-readable string for a timedelta, for example, like
    "2 days 4 hrs 10 mins 5 secs".
    """
    secs = timedelta.total_seconds()
    if secs < 0:
        secs = -secs
        before = " before"
    else:
        before = ""
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
                n = str(n)
            else:
                n = secs_format % secs
            if n != "0":
                parts.append("%s %s%s" % (n, unit, "" if n == "1" else "s"))

    result = " ".join(parts)
    return f"{result}{before}"


def dateobs2datetime(date_obs: str) -> datetime.datetime:
    """Convert DATE-OBS format string representing date/time to a Python
    datetime object.
    """
    return datetime.datetime.fromisoformat(date_obs)


def datetime2dateobs(dt: datetime.datetime, no_milliseconds=False) -> str:
    """Convert a Python datetime object to a string in DATE-OBS format, with
    milliseconds, or optionally without the milliseconds.
    """
    if no_milliseconds:
        return dt.isoformat(sep="T", timespec="seconds")
    else:
        return dt.isoformat(sep="T", timespec="milliseconds")


def obsday_hours2str(obsday_hours: float) -> str:
    """Format an `obsday_hours` (fractional hours into an HST day) value into a
    formatted string of the time.
    """
    hours = int(obsday_hours)
    mins = int((obsday_hours - hours) * 60)
    am_pm = "pm" if hours >= 12 else "am"
    if hours > 12:
        hours -= 12
    if hours == 12 and mins == 0:
        return "noon"
    else:
        return f"{hours} {am_pm}" if mins == 0 else f"{hours}:{mins:02d} {am_pm}"


def ut2hst(dt: datetime.datetime) -> datetime.datetime:
    """Convert date/time from UT to HST time zone."""
    return dt - datetime.timedelta(hours=10)


def obsday_hours(dt: datetime.datetime) -> float:
    """Return the numbers of hours into the observing day."""
    hst = ut2hst(dt)
    return hst.hour + hst.minute / 60.0 + hst.second / 60.0 / 60.0


def short2hyphenated(short_date: str) -> str:
    """Convert a "short date", like "20240409", to a hyphenated date, like
    "2024-04-9".
    """
    return f"{short_date[0:4]}-{short_date[4:6]}-{short_date[6:8]}"


def decompose_date(short_date: str) -> list[str]:
    """Decompose a short date "YYYYMMDD" into an array ["YYYY", "MM", "DD"]."""
    return [short_date[0:4], short_date[4:6], short_date[6:8]]
