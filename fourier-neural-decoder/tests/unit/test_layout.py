from __future__ import annotations

import pytest
from dash import html

from fourier.ui.layout import (
    _build_footer,
    _build_header,
    _build_sidebar,
    _build_wave_panel,
    build_layout,
    make_slider,
)
from fourier.shared.version import VERSION


def _find_ids(component, collected=None):
    if collected is None:
        collected = []
    if hasattr(component, "id") and component.id:
        collected.append(component.id)
    children = getattr(component, "children", None)
    if children is None:
        return collected
    kids = children if isinstance(children, list) else [children]
    for child in kids:
        if hasattr(child, "id") or hasattr(child, "children"):
            _find_ids(child, collected)
    return collected


def _contains_text(component, text: str) -> bool:
    if isinstance(component, str):
        return text in component
    if hasattr(component, "children"):
        kids = component.children
        if isinstance(kids, str):
            return text in kids
        if isinstance(kids, list):
            return any(_contains_text(k, text) for k in kids)
        return _contains_text(kids, text)
    return False


def test_build_layout_returns_html_div():
    assert isinstance(build_layout(), html.Div)


def test_header_contains_fourier_synthesis():
    header = _build_header()
    assert _contains_text(header, "Fourier Synthesis")


def test_wave_panel_contains_enabled_checklist():
    panel = _build_wave_panel(0)
    ids = _find_ids(panel)
    assert "enabled-0" in ids


def test_wave_panel_contains_freq_slider():
    panel = _build_wave_panel(0)
    ids = _find_ids(panel)
    assert "freq-0" in ids


def test_wave_panel_contains_amp_slider():
    panel = _build_wave_panel(0)
    ids = _find_ids(panel)
    assert "amp-0" in ids


def test_wave_panel_contains_phase_slider():
    panel = _build_wave_panel(0)
    ids = _find_ids(panel)
    assert "phase-0" in ids


def test_wave_panel_contains_dots_checklist():
    panel = _build_wave_panel(0)
    ids = _find_ids(panel)
    assert "dots-0" in ids


def test_wave_panel_contains_sr_slider():
    panel = _build_wave_panel(0)
    ids = _find_ids(panel)
    assert "sr-0" in ids


def test_wave_panel_contains_vector_div():
    panel = _build_wave_panel(0)
    ids = _find_ids(panel)
    assert "vector-0" in ids


def _find_slider(comp):
    from dash import dcc
    if isinstance(comp, dcc.Slider):
        return comp
    children = getattr(comp, "children", None)
    if children is None:
        return None
    if not isinstance(children, list):
        children = [children]
    for k in children:
        result = _find_slider(k)
        if result is not None:
            return result
    return None


def test_make_slider_updatemode_drag():
    slider_div = make_slider("test-id", "Label", 0.0, 1.0, 0.1, 0.5)
    slider = _find_slider(slider_div)
    assert slider is not None
    assert getattr(slider, "updatemode", None) == "drag"


def test_make_slider_marks_none():
    slider_div = make_slider("test-id2", "Label", 0.0, 1.0, 0.1, 0.5)
    slider = _find_slider(slider_div)
    assert slider is not None
    assert getattr(slider, "marks", "NOT_SET") is None


def test_layout_contains_overlay_chart():
    layout = build_layout()
    ids = _find_ids(layout)
    assert "overlay-chart" in ids


def test_layout_contains_sum_chart():
    layout = build_layout()
    ids = _find_ids(layout)
    assert "sum-chart" in ids


def test_layout_contains_window_slider():
    layout = build_layout()
    ids = _find_ids(layout)
    assert "window-slider" in ids


def test_layout_contains_per_wave_alpha_sliders():
    layout = build_layout()
    ids = _find_ids(layout)
    for i in range(4):
        assert f"alpha-{i}" in ids


def test_layout_contains_per_wave_beta_sliders():
    layout = build_layout()
    ids = _find_ids(layout)
    for i in range(4):
        assert f"beta-{i}" in ids


def test_layout_contains_id_mode_lock_wrappers():
    layout = build_layout()
    ids = _find_ids(layout)
    for i in range(4):
        assert f"enabled-wrap-{i}" in ids
        assert f"fixed-controls-{i}" in ids
        assert f"noise-controls-{i}" in ids



def test_layout_contains_identify_btn():
    layout = build_layout()
    ids = _find_ids(layout)
    assert "identify-btn" in ids


def test_footer_displays_version():
    footer = _build_footer()
    assert _contains_text(footer, VERSION)


def test_layout_contains_active_channels_store():
    from dash import dcc
    layout = build_layout()

    def find_store(comp, store_id):
        if isinstance(comp, dcc.Store) and getattr(comp, "id", None) == store_id:
            return comp
        children = getattr(comp, "children", None)
        if children is None:
            return None
        if not isinstance(children, list):
            children = [children]
        for k in children:
            result = find_store(k, store_id)
            if result is not None:
                return result
        return None

    active_store = find_store(layout, "active-channels")
    assert active_store is not None
    assert active_store.data == [1, 1, 1, 1]

    extract_store = find_store(layout, "extract-vector")
    assert extract_store is not None
    # v1.07: extract target is locked to channel 1 (Second Harmonic).
    assert extract_store.data == [0, 1, 0, 0]


def test_four_wave_panels_in_layout():
    layout = build_layout()
    for i in range(4):
        ids = _find_ids(layout)
        assert f"wave-panel-{i}" in ids


def _find_slider_by_id(comp, sid: str):
    from dash import dcc
    if isinstance(comp, dcc.Slider) and getattr(comp, "id", None) == sid:
        return comp
    children = getattr(comp, "children", None)
    if children is None:
        return None
    if not isinstance(children, list):
        children = [children]
    for k in children:
        result = _find_slider_by_id(k, sid)
        if result is not None:
            return result
    return None


def test_freq_slider_range():
    panel = _build_wave_panel(0)
    slider = _find_slider_by_id(panel, "freq-0")
    assert slider is not None
    assert slider.min == 0.1
    assert slider.max == 5.0


def test_amp_slider_range():
    panel = _build_wave_panel(0)
    slider = _find_slider_by_id(panel, "amp-0")
    assert slider is not None
    assert slider.min == 0
    assert slider.max == 100


def test_phase_slider_range():
    import math
    panel = _build_wave_panel(0)
    slider = _find_slider_by_id(panel, "phase-0")
    assert slider is not None
    assert slider.min == 0.0
    assert slider.max == pytest.approx(round(2 * math.pi, 2), abs=0.01)


def test_sr_slider_range():
    panel = _build_wave_panel(0)
    slider = _find_slider_by_id(panel, "sr-0")
    assert slider is not None
    assert slider.min == 1
    assert slider.max == 50


def test_sidebar_style_allows_vertical_scroll():
    sidebar = _build_sidebar()
    style = getattr(sidebar, "style", {}) or {}
    assert style.get("overflowY") == "auto"
    assert style.get("height") == "100%"
