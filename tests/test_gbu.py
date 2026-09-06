# -*- coding: utf-8 -*-

"""Tests for `process.gbu` module.
"""

import pytest

from chromag.process.gbu import (
    gbu_bitmask,
    gbu_name,
)


def test_gbu_bitmask():
    assert gbu_bitmask("") == 0b00
    assert gbu_bitmask("BKG") == 0b01


def test_gbu_name():
    assert gbu_name(0b00) == ""
    assert gbu_name(0b01) == "BKG"
