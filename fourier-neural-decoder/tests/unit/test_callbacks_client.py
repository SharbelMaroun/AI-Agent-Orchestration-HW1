from __future__ import annotations

from fourier.ui.callbacks_client import CLIENTSIDE_CHART_JS


def test_js_string_is_non_empty():
    assert len(CLIENTSIDE_CHART_JS.strip()) > 0


def test_js_string_contains_function_keyword():
    assert "function(" in CLIENTSIDE_CHART_JS


def test_js_string_contains_overlay_traces():
    assert "overlayTraces" in CLIENTSIDE_CHART_JS


def test_js_string_contains_sum_y():
    assert "sumY" in CLIENTSIDE_CHART_JS


def test_js_string_contains_t_cont():
    assert "tCont" in CLIENTSIDE_CHART_JS


def test_js_function_has_23_parameters():
    first_brace = CLIENTSIDE_CHART_JS.index("{")
    sig = CLIENTSIDE_CHART_JS[:first_brace]
    params_str = sig.split("(")[1].rsplit(")", 1)[0]
    params = [p.strip() for p in params_str.split(",") if p.strip()]
    assert len(params) == 23


def test_js_uses_noise_sigma():
    assert "noiseSigma" in CLIENTSIDE_CHART_JS


def test_js_shows_noisy_dots_when_sigma_positive():
    assert "sigma > 0" in CLIENTSIDE_CHART_JS


def test_js_uses_channel_vector_C():
    assert "C[i]" in CLIENTSIDE_CHART_JS


def test_js_channel_vector_checks_one():
    assert "C[i] !== 1" in CLIENTSIDE_CHART_JS


def test_js_contains_vrect_shape():
    assert "shapes" in CLIENTSIDE_CHART_JS


def test_js_vrect_has_x0_window_start():
    assert "x0: ws" in CLIENTSIDE_CHART_JS


def test_js_vrect_x1_is_window_plus_one():
    assert "x1: ws + 1" in CLIENTSIDE_CHART_JS


def test_js_vrect_color_is_amber():
    assert "251,191,36" in CLIENTSIDE_CHART_JS


def test_js_overlay_chart_y_range():
    assert "[-100,100]" in CLIENTSIDE_CHART_JS or "[-100, 100]" in CLIENTSIDE_CHART_JS


def test_js_sum_chart_dark_background():
    assert "#020617" in CLIENTSIDE_CHART_JS


def test_js_sum_chart_y_range():
    assert "[-150,150]" in CLIENTSIDE_CHART_JS or "[-150, 150]" in CLIENTSIDE_CHART_JS
