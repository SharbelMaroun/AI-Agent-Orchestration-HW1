from __future__ import annotations

from fourier.ui.callbacks_client import CLIENTSIDE_CHART_JS


def test_js_string_is_non_empty():
    assert len(CLIENTSIDE_CHART_JS.strip()) > 0


def test_js_string_contains_function_keyword():
    assert "function(" in CLIENTSIDE_CHART_JS


def test_js_string_contains_overlay_traces():
    assert "overlayTraces" in CLIENTSIDE_CHART_JS


def test_js_string_contains_t_cont():
    assert "tCont" in CLIENTSIDE_CHART_JS


def test_js_function_has_31_parameters():
    """activeChannels + 4 each of (freq,amp,phase,dots,sr) + windowStart
    + 4 alpha + 4 beta + idMode = 1 + 20 + 1 + 4 + 4 + 1 = 31."""
    first_brace = CLIENTSIDE_CHART_JS.index("{")
    sig = CLIENTSIDE_CHART_JS[:first_brace]
    params_str = sig.split("(")[1].rsplit(")", 1)[0]
    params = [p.strip() for p in params_str.split(",") if p.strip()]
    assert len(params) == 31


def test_js_uses_alpha_inputs():
    for i in range(4):
        assert f"alpha{i}" in CLIENTSIDE_CHART_JS


def test_js_uses_beta_inputs():
    for i in range(4):
        assert f"beta{i}" in CLIENTSIDE_CHART_JS


def test_js_implements_parametric_noise():
    assert "sampleAt" in CLIENTSIDE_CHART_JS
    assert "Math.PI" in CLIENTSIDE_CHART_JS


def test_js_uses_uniform_distribution():
    assert "2 * Math.random() - 1" in CLIENTSIDE_CHART_JS


def test_js_uses_active_channels():
    assert "activeChannels[i]" in CLIENTSIDE_CHART_JS


def test_js_active_channels_checks_one():
    assert "activeChannels[i] !== 1" in CLIENTSIDE_CHART_JS


def test_js_contains_vrect_shape():
    assert "shapes" in CLIENTSIDE_CHART_JS


def test_js_vrect_has_x0_window_start():
    assert "x0: ws" in CLIENTSIDE_CHART_JS


def test_js_vrect_x1_is_window_plus_10ms():
    """Window width = 10 samples / 1000 Hz = 0.01 seconds."""
    assert "x1: ws + 0.01" in CLIENTSIDE_CHART_JS


def test_js_id_mode_uses_1000hz():
    assert "const sumSr = 1000" in CLIENTSIDE_CHART_JS


def test_js_vrect_color_is_amber():
    assert "251,191,36" in CLIENTSIDE_CHART_JS


def test_js_overlay_chart_y_range():
    assert "[-100,100]" in CLIENTSIDE_CHART_JS or "[-100, 100]" in CLIENTSIDE_CHART_JS


def test_js_sum_chart_dark_background():
    assert "#020617" in CLIENTSIDE_CHART_JS


def test_js_sum_chart_y_range():
    assert "[-150,150]" in CLIENTSIDE_CHART_JS or "[-150, 150]" in CLIENTSIDE_CHART_JS
