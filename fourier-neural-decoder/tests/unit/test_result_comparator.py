from __future__ import annotations

import pytest

from fourier.sdk.result_comparator import ResultComparator
from fourier.shared.types import ClassifierResult


def _result(cls: int, confidence: float, runner_up: int) -> ClassifierResult:
    probs = [0.0, 0.0, 0.0, 0.0]
    probs[cls] = confidence
    remaining = 1.0 - confidence
    probs[runner_up] = remaining
    from fourier.shared.constants import WAVE_NAMES
    return ClassifierResult(
        predicted_class=cls,
        class_name=WAVE_NAMES[cls],
        confidence=confidence,
        probabilities=probs,
        runner_up=runner_up,
    )


def test_init_accepts_config_dict():
    comp = ResultComparator(config={})
    assert comp.config == {}


def test_validate_config_passes_on_empty_config():
    ResultComparator(config={})


def test_process_returns_diff_result():
    comp = ResultComparator()
    rnn = _result(0, 0.8, 1)
    lstm = _result(0, 0.9, 1)
    diff = comp.process(rnn, lstm)
    for key in ("agreement", "rnn_predicted", "lstm_predicted", "confidence_delta", "runner_up_diff"):
        assert key in diff


def test_agreement_true_when_both_predict_same_class():
    comp = ResultComparator()
    diff = comp.process(_result(1, 0.7, 0), _result(1, 0.8, 0))
    assert diff["agreement"] is True


def test_agreement_false_when_predictions_differ():
    comp = ResultComparator()
    diff = comp.process(_result(0, 0.7, 1), _result(2, 0.8, 1))
    assert diff["agreement"] is False


def test_rnn_predicted_equals_class_name():
    rnn = _result(0, 0.9, 1)
    diff = ResultComparator().process(rnn, _result(0, 0.8, 1))
    assert diff["rnn_predicted"] == rnn["class_name"]


def test_lstm_predicted_equals_class_name():
    lstm = _result(2, 0.85, 0)
    diff = ResultComparator().process(_result(2, 0.7, 0), lstm)
    assert diff["lstm_predicted"] == lstm["class_name"]


def test_confidence_delta_is_abs_difference():
    rnn = _result(0, 0.80, 1)
    lstm = _result(0, 0.95, 1)
    diff = ResultComparator().process(rnn, lstm)
    assert diff["confidence_delta"] == pytest.approx(abs(0.80 - 0.95), abs=1e-4)


def test_confidence_delta_rounds_to_4_decimal_places():
    rnn = _result(0, 0.123456, 1)
    lstm = _result(0, 0.234567, 1)
    diff = ResultComparator().process(rnn, lstm)
    assert diff["confidence_delta"] == round(diff["confidence_delta"], 4)


def test_runner_up_diff_is_string():
    diff = ResultComparator().process(_result(0, 0.8, 1), _result(0, 0.9, 2))
    assert isinstance(diff["runner_up_diff"], str)


def test_runner_up_diff_same_runner_up():
    diff = ResultComparator().process(_result(0, 0.8, 1), _result(0, 0.9, 1))
    assert "Both" in diff["runner_up_diff"]


def test_runner_up_diff_different_runner_up():
    diff = ResultComparator().process(_result(0, 0.8, 1), _result(0, 0.9, 2))
    assert "RNN" in diff["runner_up_diff"] and "LSTM" in diff["runner_up_diff"]
