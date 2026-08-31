# -*- coding: utf-8 -*-

"""Tests for `datetime` module.
"""

import datetime

import pytest

from chromag.datetime import (
    human_timedelta,
    filename2datetime,
    dateobs2datetime,
    datetime2dateobs,
    obsday_hours2str,
    ut2hst,
    obsday_hours,
    short2hyphenated,
    decompose_date,
)


def test_human_timedelta():
    d1 = datetime.datetime(2023, 10, 25, 10, 20, 35)
    d2 = datetime.datetime(2023, 10, 25, 10, 20, 35, 500000)
    d3 = datetime.datetime(2023, 10, 25, 10, 20, 43)
    d4 = datetime.datetime(2023, 10, 25, 10, 20, 53)
    d5 = datetime.datetime(2023, 10, 25, 10, 25, 45)
    d6 = datetime.datetime(2023, 10, 25, 11, 25, 45)
    d7 = datetime.datetime(2023, 10, 26, 11, 25, 45)
    d8 = datetime.datetime(2023, 11, 26, 11, 25, 45)
    d9 = datetime.datetime(2024, 11, 26, 11, 25, 45)

    assert human_timedelta(d2 - d1) == "0.500 secs"
    assert human_timedelta(d3 - d1) == "8.00 secs"
    assert human_timedelta(d4 - d1) == "18.0 secs"
    assert human_timedelta(d5 - d1) == "5 mins 10 secs"
    assert human_timedelta(d6 - d1) == "1 hr 5 mins 10 secs"
    assert human_timedelta(d7 - d1) == "1 day 1 hr 5 mins 10 secs"
    assert human_timedelta(d8 - d1) == "32 days 1 hr 5 mins 10 secs"
    assert human_timedelta(d9 - d1) == "398 days 1 hr 5 mins 10 secs"

    assert human_timedelta(d1 - d2) == "0.500 secs before"


def test_no_seconds():
    assert human_timedelta(datetime.timedelta(days=1, hours=5)) == "1 day 5 hrs"


def test_filename2datetime():
    dt = filename2datetime("20250813T215545.133Z.fits")
    assert dt == dateobs2datetime("2025-08-13T21:55:45.133")


def test_dateobs2datetime():
    d1 = datetime.datetime(2023, 10, 25, 10, 20, 35)
    assert d1 == dateobs2datetime("2023-10-25T10:20:35.000")
    assert d1 == dateobs2datetime("2023-10-25T10:20:35")


def test_datetime2dateobs():
    d1 = datetime.datetime(2023, 10, 25, 10, 20, 35)
    assert datetime2dateobs(d1) == "2023-10-25T10:20:35.000"
    assert datetime2dateobs(d1, milliseconds=False) == "2023-10-25T10:20:35"


def test_ut2hst():
    d1 = datetime.datetime(2023, 10, 25, 10, 20, 35)
    assert dateobs2datetime("2023-10-25T00:20:35") == ut2hst(d1)


def test_obsday_hours2str():
    assert obsday_hours2str(10.5) == "10:30 am"
    assert obsday_hours2str(9.75) == "9:45 am"
    assert obsday_hours2str(12) == "noon"
    assert obsday_hours2str(13) == "1 pm"
    assert obsday_hours2str(14.25) == "2:15 pm"


def test_obsday_hours():
    tolerance = 1.0 / 60.0 / 60.0  # nearest second
    dt_ut = datetime.datetime(2023, 10, 25, 18, 20, 35)
    ohours_hst = 8.0 + 20.0 / 60.0 + 35.0 / 60.0 / 60.0
    print(obsday_hours(dt_ut))
    assert abs(obsday_hours(dt_ut) - ohours_hst) < tolerance


def test_short2hyphenated():
    assert short2hyphenated("20260828") == "2026-08-28"


def test_decompose_date():
    year, month, day = decompose_date("20260828")
    assert year == "2026"
    assert month == "08"
    assert day == "28"
