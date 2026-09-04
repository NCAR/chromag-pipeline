# -*- coding: utf-8 -*-

"""Tests for `cli` module.
"""

import pytest

from chromag.cli import helper


class ParseError(Exception):
    pass


def fake_error_handler(*args):
    raise ParseError(*args)


def test_split_dates_one():
    d = "20250813"
    dates = helper.split_dates(d, fake_error_handler)
    assert len(dates) == 1
    assert dates[0] == d


def test_split_dates_range():
    dates = helper.split_dates("20250813-20250815", fake_error_handler)
    assert len(dates) == 2
    assert dates[0] == "20250813"
    assert dates[1] == "20250814"


def test_split_dates_list():
    dates = helper.split_dates("20250813,20250815", fake_error_handler)
    assert len(dates) == 2
    assert dates[0] == "20250813"
    assert dates[1] == "20250815"


def test_split_dates_badrange():
    try:
        dates = helper.split_dates("20250815-20250813", fake_error_handler)
        pytest.fail("should have produced error")
    except ParseError as e:
        pass


def test_split_dates_badexpr():
    try:
        dates = helper.split_dates("2025081", fake_error_handler)
        pytest.fail("should have produced error")
    except ParseError as e:
        pass


def test_increment_date():
    assert helper.increment_date("20251231") == "20260101"
