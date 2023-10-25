# -*- coding: utf-8 -*-

"""Tests for `string_helpers` package.
"""

import pytest

from chromag.string_helpers import truncate


def test_truncate_basic():
    assert truncate("A long test string", 10) == "A long ..."
    assert truncate("A short string", 20) == "A short string"


def test_truncate_padding():
    assert truncate("A short string", 20, padding=True) == "A short string      "


def test_truncate_alternate():
    assert truncate("A long test string", 10, continuation_chars="..") == "A long t.."
