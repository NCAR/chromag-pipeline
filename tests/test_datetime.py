# -*- coding: utf-8 -*-

"""Tests for `datetime` module.
"""

import datetime

import pytest

from chromag.datetime import human_timedelta, dateobs2datetime, datetime2dateobs


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


def test_dateobs2datetime():
    d1 = datetime.datetime(2023, 10, 25, 10, 20, 35)
    assert d1 == dateobs2datetime("2023-10-25T10:20:35.000")
    assert d1 == dateobs2datetime("2023-10-25T10:20:35")


def test_datetime2dateobs():
    d1 = datetime.datetime(2023, 10, 25, 10, 20, 35)
    assert datetime2dateobs(d1) == "2023-10-25T10:20:35.000"
    assert datetime2dateobs(d1, no_milliseconds=True) == "2023-10-25T10:20:35"
