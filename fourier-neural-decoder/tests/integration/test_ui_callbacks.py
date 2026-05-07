from __future__ import annotations

import pytest
from fourier.shared.constants import DEFAULTS
from fourier.ui.callbacks_server import (
    toggle_wave_fn, toggle_sr_fn, update_vector_fn,
)


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
