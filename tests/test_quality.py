# -*- coding: utf-8 -*-

"""Tests for `quality` module.
"""

import pytest

from chromag.quality import (
    sci_quality_bitmask,
    sci_quality_name,
    cal_quality_bitmask,
    cal_quality_name,
)


def test_sci_quality_bitmask():
    assert sci_quality_bitmask("") == 0b00
    assert sci_quality_bitmask("SGSLOOP") == 0b01
    assert sci_quality_bitmask("SGSLOOP|POSITIONS") == 0b11


def test_sci_quality_name():
    assert sci_quality_name(0b00) == ""
    assert sci_quality_name(0b01) == "SGSLOOP"
    assert sci_quality_name(0b11) == "SGSLOOP|POSITIONS"


def test_cal_quality_bitmask():
    assert sci_quality_bitmask("") == 0b00
    assert sci_quality_bitmask("SGSLOOP") == 0b01
    assert sci_quality_bitmask("SGSLOOP|POSITIONS") == 0b11


def test_cal_quality_name():
    assert cal_quality_name(0b00) == ""
    assert cal_quality_name(0b01) == "SGSLOOP"
    assert cal_quality_name(0b11) == "SGSLOOP|POSITIONS"
