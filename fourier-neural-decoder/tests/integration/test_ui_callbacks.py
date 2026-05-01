from __future__ import annotations

import pytest
from fourier.shared.constants import DEFAULTS
from fourier.ui.callbacks_server import (
    _noise_label, toggle_wave_fn, toggle_sr_fn, update_vector_fn, reset_cb_fn
)


def test_reset_logic():
    results = reset_cb_fn(1)
    assert len(results) == 24
    assert results[0] == DEFAULTS[0]["frequency"]
    assert results[4] == DEFAULTS[0]["amplitude"]
    assert results[12] == ["on"]
    assert results[16] == []
    assert results[20] == DEFAULTS[0]["sampling_rate"]


def test_noise_label_mapping():
    assert _noise_label(0.0) == "Clean"
    assert _noise_label(0.1) == "Light"
    assert _noise_label(0.2) == "Medium"
    assert _noise_label(0.4) == "Heavy"


def test_toggle_wave_logic():
    # Enabled
    ctrl_style, panel_style = toggle_wave_fn(["on"])
    assert ctrl_style == {}
    assert panel_style["opacity"] == "1"
    
    # Disabled
    ctrl_style, panel_style = toggle_wave_fn([])
    assert ctrl_style == {"display": "none"}
    assert panel_style["opacity"] == "0.55"


def test_toggle_sr_logic():
    # Dots on
    style = toggle_sr_fn(["on"])
    assert style == {"display": "block"}
    
    # Dots off
    style = toggle_sr_fn([])
    assert style == {"display": "none"}


def test_update_vector_logic():
    # Dots off
    res = update_vector_fn(0, [], 20, 0.5, 50, 0)
    assert res == []
    
    # Dots on
    res = update_vector_fn(0, ["on"], 20, 0.5, 50, 0)
    assert hasattr(res, 'children')
    assert len(res.children) > 1
