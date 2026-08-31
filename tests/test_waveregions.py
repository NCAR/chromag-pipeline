# -*- coding: utf-8 -*-

"""Tests for `waveregions` package.
"""

import pytest

from chromag.waveregions import available_waveregions, waveregion_property, _get_spec


standard_waveregions = ["587", "617", "656", "854", "1083"]


def test_available_waveregions():
    wave_regions = available_waveregions()
    assert len(wave_regions) == 5

    for s in standard_waveregions:
        assert s in wave_regions


def test_waveregion_property():
    tolerance = 0.0001
    center_wavelength = waveregion_property("617", "center_wavelength", "2026-08-28")
    assert type(center_wavelength) == float
    assert abs(center_wavelength - 617.3) < tolerance


def test_waveregion_properties():
    """Determine if all the wave regions have the same parameters. This is a
    test of the wave region configuration files, not the code.
    """
    cw = standard_waveregions[0]
    comparison_parameters = _get_spec(cw).specification.defaults().keys()
    n_comps = len(comparison_parameters)
    for w in standard_waveregions[1:]:
        wave_region_parameters = _get_spec(w).specification.defaults().keys()
        n_wave = len(wave_region_parameters)
        assert (
            n_wave == n_comps
        ), f"{cw}.spec.cfg has {n_wave} parameters, but {w}.spec.cfg has {n_comps}"
        for p in comparison_parameters:
            assert (
                p in wave_region_parameters
            ), f"{p} in {cw}.spec.cfg, but not {w}.spec.cfg"
