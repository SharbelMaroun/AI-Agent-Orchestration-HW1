from __future__ import annotations

from dash import html

from fourier.ui.layout import (
    _build_footer,
    _build_header,
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
    if hasattr(component, "children") and component.children:
        kids = component.children if isinstance(component.children, list) else [component.children]
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


def test_header_contains_reset_btn():
    header = _build_header()
    ids = _find_ids(header)
    assert "reset-btn" in ids


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


def test_layout_contains_noise_slider():
    layout = build_layout()
    ids = _find_ids(layout)
    assert "noise-slider" in ids


def test_layout_contains_noise_label():
    layout = build_layout()
    ids = _find_ids(layout)
    assert "noise-label" in ids


def test_layout_contains_algo_selector():
    layout = build_layout()
    ids = _find_ids(layout)
    assert "algo-selector" in ids


def test_layout_contains_identify_btn():
    layout = build_layout()
    ids = _find_ids(layout)
    assert "identify-btn" in ids


def test_footer_displays_version():
    footer = _build_footer()
    assert _contains_text(footer, VERSION)


def test_four_wave_panels_in_layout():
    layout = build_layout()
    for i in range(4):
        ids = _find_ids(layout)
        assert f"wave-panel-{i}" in ids
