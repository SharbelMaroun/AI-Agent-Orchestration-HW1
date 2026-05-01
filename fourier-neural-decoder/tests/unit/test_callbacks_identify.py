from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from dash import html, no_update

from fourier.shared.constants import WAVE_NAMES
from fourier.shared.types import ClassifierResult
from fourier.ui.callbacks_identify import _run_identify


def _make_figure(y: list[float] | None = None) -> dict:
    if y is None:
        y = [0.0] * 501
    return {"data": [{"y": y}]}


def _make_result(cls: int = 0, confidence: float = 0.9) -> ClassifierResult:
    probs = [0.0, 0.0, 0.0, 0.0]
    probs[cls] = confidence
    runner_up = (cls + 1) % 4
    probs[runner_up] = round(1.0 - confidence, 6)
    return ClassifierResult(
        predicted_class=cls,
        class_name=WAVE_NAMES[cls],
        confidence=confidence,
        probabilities=probs,
        runner_up=runner_up,
    )


def _mock_gatekeeper(return_value) -> MagicMock:
    gk = MagicMock()
    gk.call.return_value = return_value
    return gk


def test_identify_rnn_calls_gatekeeper():
    gk = _mock_gatekeeper(_make_result(0))
    panel, style, _, diff_style = _run_identify(gk, 0.0, 0.0, "RNN", _make_figure())
    assert gk.call.call_count == 1
    assert style == {"display": "block"}
    assert diff_style == {"display": "none"}


def test_identify_lstm_calls_gatekeeper():
    gk = _mock_gatekeeper(_make_result(1))
    panel, style, _, diff_style = _run_identify(gk, 0.0, 0.0, "LSTM", _make_figure())
    assert gk.call.call_count == 1
    assert style == {"display": "block"}
    assert diff_style == {"display": "none"}


def test_identify_both_calls_gatekeeper_twice():
    gk = MagicMock()
    gk.call.side_effect = [_make_result(0), _make_result(0)]
    panel, style, diff_panel, diff_style = _run_identify(gk, 0.0, 0.0, "Both", _make_figure())
    assert gk.call.call_count == 2
    assert style == {"display": "block"}
    assert diff_style == {"display": "block"}


def test_identify_both_calls_result_comparator():
    gk = MagicMock()
    rnn_r = _make_result(0, 0.9)
    lstm_r = _make_result(0, 0.85)
    gk.call.side_effect = [rnn_r, lstm_r]
    with patch("fourier.ui.callbacks_identify.ResultComparator") as mock_comp:
        mock_comp.return_value.process.return_value = {
            "agreement": True, "rnn_predicted": WAVE_NAMES[0], "lstm_predicted": WAVE_NAMES[0],
            "confidence_delta": 0.05, "runner_up_diff": "same"
        }
        _run_identify(gk, 0.0, 0.0, "Both", _make_figure())
    mock_comp.return_value.process.assert_called_once_with(rnn_r, lstm_r)


def test_identify_both_result_panel_has_two_sub_panels():
    gk = MagicMock()
    gk.call.side_effect = [_make_result(0), _make_result(1)]
    panel, _, _, _ = _run_identify(gk, 0.0, 0.0, "Both", _make_figure())
    assert isinstance(panel, html.Div)
    assert isinstance(panel.children, list)
    assert len(panel.children) == 2


def test_identify_rnn_passes_noise_sigma_to_extractor():
    gk = _mock_gatekeeper(_make_result(0))
    t = np.linspace(0, 10, 501)
    y = list(50 * np.sin(2 * np.pi * 0.5 * t))
    with patch("fourier.ui.callbacks_identify.WindowExtractor") as mock_ext:
        mock_ext.return_value.process.return_value = np.zeros((1, 50, 1), dtype="float32")
        _run_identify(gk, 2.0, 0.3, "RNN", _make_figure(y))
    mock_ext.return_value.process.assert_called_once()
    _, kwargs = mock_ext.return_value.process.call_args
    assert kwargs.get("noise_sigma") == pytest.approx(0.3)


def test_identify_result_panel_shown_after_identify():
    gk = _mock_gatekeeper(_make_result(0))
    _, style, _, _ = _run_identify(gk, 0.0, 0.0, "RNN", _make_figure())
    assert style.get("display") == "block"
