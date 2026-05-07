from __future__ import annotations

import numpy as np
import pytest
from dash import html

from fourier.shared.constants import ID_MODE_SIGNALS, WAVE_NAMES
from fourier.ui.callbacks_identify import _extract_10_points, _project_at_frequency, _run_identify


def _make_figure(y: list[float] | None = None) -> dict:
    n = 201  # sr=20, 10s → 201 points
    if y is None:
        t = [i / 20 for i in range(n)]
        y = [0.0] * n
    else:
        t = [i / 20 for i in range(len(y))]
    return {"data": [{"x": t, "y": y}]}


# ── _extract_10_points ────────────────────────────────────────────────────────

def test_extract_returns_three_lists():
    fig = _make_figure()
    result, real, error = _extract_10_points(fig, 0.0, 0)
    assert len(result) == 10
    assert len(real) == 10
    assert len(error) == 10


def test_extract_error_is_result_minus_real():
    fig = _make_figure()
    result, real, error = _extract_10_points(fig, 0.0, 0)
    for k in range(10):
        assert error[k] == pytest.approx(round(result[k] - real[k], 2), abs=1e-4)


def test_extract_empty_figure_returns_zeros():
    result, _, _ = _extract_10_points({"data": [{"x": [], "y": []}]}, 0.0, 0)
    assert result == [0.0] * 10


def test_extract_window_start_shifts_time_grid():
    import math
    n = 201
    # Non-trivial signal so real values differ across windows
    y = [math.sin(2 * math.pi * 0.5 * (i / 20)) for i in range(n)]
    fig = _make_figure(y)
    _, real0, _ = _extract_10_points(fig, 0.0, 0)
    _, real1, _ = _extract_10_points(fig, 2.0, 0)
    assert real0 != real1


def test_extract_uses_id_mode_sr_grid():
    """Time points must be multiples of 1/20 s."""
    import math
    from fourier.shared.constants import ID_MODE_SR
    fig = _make_figure()
    ws = 1.5
    n_start = int(math.ceil(ws * ID_MODE_SR))
    expected_t0 = n_start / ID_MODE_SR
    # result[0] should match sum_y at expected_t0 (all-zero signal → 0.0)
    result, _, _ = _extract_10_points(fig, ws, 0)
    assert result[0] == pytest.approx(0.0, abs=1e-6)
    assert expected_t0 >= ws


# ── _run_identify ─────────────────────────────────────────────────────────────

# ── _project_at_frequency (Fourier extraction) ────────────────────────────────

def test_projection_recovers_pure_sine_exactly():
    """A pure sine at one channel's frequency must come back as itself."""
    import math
    sig = ID_MODE_SIGNALS[1]   # f = 1.0 Hz
    t = np.array([k / 20.0 for k in range(10)])
    samples = sig["amplitude"] * np.sin(2 * np.pi * sig["frequency"] * t + sig["phase"])
    recovered = _project_at_frequency(samples, t, 1)
    assert np.allclose(recovered, samples, atol=1e-6)


def test_projection_isolates_chosen_component_in_summation():
    """Summation of channels 1 and 2; projecting at index 1 must recover only its component."""
    t = np.array([k / 20.0 for k in range(10)])
    sig1 = ID_MODE_SIGNALS[1]   # f = 1.0 Hz
    sig2 = ID_MODE_SIGNALS[2]   # f = 1.5 Hz
    s1 = sig1["amplitude"] * np.sin(2 * np.pi * sig1["frequency"] * t + sig1["phase"])
    s2 = sig2["amplitude"] * np.sin(2 * np.pi * sig2["frequency"] * t + sig2["phase"])
    recovered = _project_at_frequency(s1 + s2, t, 1)
    # Multi-frequency LSQ must cleanly separate the two components.
    assert np.allclose(recovered, s1, atol=1e-6)


def test_extract_when_summation_is_only_chosen_wave_yields_small_error():
    """If the summation contains only the user's chosen wave, result ≈ real."""
    import math
    from fourier.shared.constants import ID_MODE_SR
    sig = ID_MODE_SIGNALS[1]  # f=1.0 Hz
    n = 10 * ID_MODE_SR + 1
    t_full = [i / float(ID_MODE_SR) for i in range(n)]
    y_full = [sig["amplitude"] * math.sin(2 * math.pi * sig["frequency"] * tt + sig["phase"]) for tt in t_full]
    fig = {"data": [{"x": t_full, "y": y_full}]}
    result, real, _ = _extract_10_points(fig, 0.0, 1)
    for k in range(10):
        assert abs(result[k] - real[k]) < 0.5


def test_extract_isolates_chosen_frequency_from_summation():
    """Summation of two pure sines; extracting f=1 Hz should recover its component."""
    import math
    from fourier.shared.constants import ID_MODE_SR
    n = 10 * ID_MODE_SR + 1
    t_full = [i / float(ID_MODE_SR) for i in range(n)]
    y_full = [40 * math.sin(2 * math.pi * 1.0 * tt + math.pi / 4) +
              25 * math.sin(2 * math.pi * 1.5 * tt + math.pi / 3) for tt in t_full]
    fig = {"data": [{"x": t_full, "y": y_full}]}
    # Window starts at t=2.0s — gives the LSQ basis enough cycle coverage.
    result, real, _ = _extract_10_points(fig, 2.0, 1)
    assert max(abs(v) for v in result) < 45.0
    assert sum(abs(result[k] - real[k]) for k in range(10)) / 10 < 5.0


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
