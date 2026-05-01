from __future__ import annotations

from dash import html

from fourier.shared.constants import WAVE_NAMES
from fourier.shared.types import ClassifierResult
from fourier.ui.callbacks_server import (
    _build_diff_summary,
    _build_single_result_panel,
    _noise_label,
)


def _result(cls: int, confidence: float, runner_up: int) -> ClassifierResult:
    probs = [0.0, 0.0, 0.0, 0.0]
    probs[cls] = confidence
    probs[runner_up] = round(1.0 - confidence, 6)
    return ClassifierResult(
        predicted_class=cls,
        class_name=WAVE_NAMES[cls],
        confidence=confidence,
        probabilities=probs,
        runner_up=runner_up,
    )


def test_noise_label_clean_for_zero():
    assert _noise_label(0.0) == "Clean"


def test_noise_label_light_for_015():
    assert _noise_label(0.15) == "Light"


def test_noise_label_medium_for_030():
    assert _noise_label(0.30) == "Medium"


def test_noise_label_heavy_for_050():
    assert _noise_label(0.50) == "Heavy"


def test_build_single_result_panel_returns_div():
    panel = _build_single_result_panel(_result(0, 0.9, 1))
    assert isinstance(panel, html.Div)


def test_build_single_result_panel_shows_class_name():
    result = _result(1, 0.8, 0)

    def has_text(comp, text):
        if isinstance(comp, str):
            return text in comp
        if hasattr(comp, "children"):
            kids = comp.children if isinstance(comp.children, list) else [comp.children]
            return any(has_text(k, text) for k in kids if k is not None)
        return False

    assert has_text(_build_single_result_panel(result), result["class_name"])


def test_build_single_result_panel_shows_4_probability_bars():
    panel = _build_single_result_panel(_result(0, 0.9, 1))
    count = [0]

    def count_divs(comp):
        if isinstance(comp, html.Div):
            count[0] += 1
        if hasattr(comp, "children"):
            kids = comp.children if isinstance(comp.children, list) else [comp.children]
            for k in kids:
                if k is not None:
                    count_divs(k)

    count_divs(panel)
    assert count[0] >= 4


def test_build_diff_summary_returns_div():
    diff = {"agreement": True, "confidence_delta": 0.05, "runner_up_diff": "Both: Fundamental"}
    assert isinstance(_build_diff_summary(diff), html.Div)


def test_build_diff_summary_shows_yes_when_agreement():
    diff = {"agreement": True, "confidence_delta": 0.0, "runner_up_diff": "x"}
    panel = _build_diff_summary(diff)

    def has_text(comp, text):
        if isinstance(comp, str):
            return text in comp
        if hasattr(comp, "children"):
            kids = comp.children if isinstance(comp.children, list) else [comp.children]
            return any(has_text(k, text) for k in kids if k is not None)
        return False

    assert has_text(panel, "YES")


def test_build_diff_summary_shows_no_when_no_agreement():
    diff = {"agreement": False, "confidence_delta": 0.1, "runner_up_diff": "x"}
    panel = _build_diff_summary(diff)

    def has_text(comp, text):
        if isinstance(comp, str):
            return text in comp
        if hasattr(comp, "children"):
            kids = comp.children if isinstance(comp.children, list) else [comp.children]
            return any(has_text(k, text) for k in kids if k is not None)
        return False

    assert has_text(panel, "NO")


def test_build_diff_summary_shows_confidence_delta():
    diff = {"agreement": True, "confidence_delta": 0.1234, "runner_up_diff": "x"}
    panel = _build_diff_summary(diff)

    def has_text(comp, text):
        if isinstance(comp, str):
            return text in comp
        if hasattr(comp, "children"):
            kids = comp.children if isinstance(comp.children, list) else [comp.children]
            return any(has_text(k, text) for k in kids if k is not None)
        return False

    assert has_text(panel, "0.1234")
