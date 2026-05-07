from __future__ import annotations

import math

from dash import html

from fourier.shared.constants import ID_MODE_SR, WAVE_NAMES
from fourier.ui.callbacks_identify import _run_identify, _window_and_truth


def _make_figure(y: list[float] | None = None) -> dict:
    n = 10 * ID_MODE_SR + 1
    if y is None:
        y = [0.0] * n
    t = [i / float(ID_MODE_SR) for i in range(len(y))]
    return {"data": [{"x": t, "y": y}]}


# ── _window_and_truth ─────────────────────────────────────────────────────────

def test_window_and_truth_returns_two_arrays_of_ten():
    fig = _make_figure()
    window, real = _window_and_truth(fig, 0.0, 0)
    assert len(window) == 10
    assert len(real) == 10


def test_window_and_truth_empty_figure_returns_zeros():
    window, _ = _window_and_truth({"data": [{"x": [], "y": []}]}, 0.0, 0)
    assert list(window) == [0.0] * 10


def test_window_start_shifts_truth():
    fig = _make_figure([math.sin(2 * math.pi * 0.5 * (i / float(ID_MODE_SR)))
                        for i in range(10 * ID_MODE_SR + 1)])
    _, real0 = _window_and_truth(fig, 0.0, 0)
    _, real1 = _window_and_truth(fig, 2.0, 0)
    assert real0 != real1


# ── _run_identify ─────────────────────────────────────────────────────────────

def test_run_identify_no_selection_returns_message():
    panel, style = _run_identify(0.0, _make_figure(), [0, 0, 0, 0])
    assert style == {"display": "block"}
    assert isinstance(panel, html.Div)


def test_run_identify_returns_panel_and_style():
    panel, style = _run_identify(0.0, _make_figure(), [1, 0, 0, 0])
    assert style == {"display": "block"}
    assert isinstance(panel, html.Div)


def test_run_identify_c_vector_selects_wave():
    for i in range(4):
        C = [1 if j == i else 0 for j in range(4)]
        panel, _ = _run_identify(0.0, _make_figure(), C)
        assert WAVE_NAMES[i] in str(panel)


def test_run_identify_result_panel_shown():
    _, style = _run_identify(0.0, _make_figure(), [0, 1, 0, 0])
    assert style.get("display") == "block"
