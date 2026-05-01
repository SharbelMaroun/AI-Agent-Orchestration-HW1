from __future__ import annotations

import numpy as np
import pytest

from fourier.gatekeeper import ModelGatekeeper
from fourier.sdk.lstm_classifier import LSTMClassifier
from fourier.sdk.rnn_classifier import RNNClassifier
from fourier.sdk.result_comparator import ResultComparator
from fourier.sdk.window_extractor import WindowExtractor
from fourier.shared.config_loader import load_app_config, load_rate_limits


@pytest.fixture
def configs():
    return {
        "app": load_app_config(),
        "rate": load_rate_limits()
    }


@pytest.fixture
def gatekeeper(configs):
    return ModelGatekeeper(configs["rate"])


def test_rnn_end_to_end_flow(configs, gatekeeper):
    rnn_cfg = {
        "hidden_size": 64, "num_layers": 1, "weights_path": configs["app"]["rnn_model_path"]
    }
    rnn_clf = RNNClassifier(rnn_cfg)
    t = np.linspace(0, 10, 501)
    y = 50 * np.sin(2 * np.pi * 0.5 * t + 0.0)
    extractor = WindowExtractor({"window_start": 2.0})
    window = extractor.process(y)
    result = gatekeeper.call(rnn_clf.process, window)
    assert result["predicted_class"] == 0
    assert result["class_name"] == "Fundamental"
    assert result["confidence"] > 0.5


def test_lstm_end_to_end_flow(configs, gatekeeper):
    lstm_cfg = {
        "hidden_size": 128, "num_layers": 2, "dropout": 0.3, "weights_path": configs["app"]["lstm_model_path"]
    }
    lstm_clf = LSTMClassifier(lstm_cfg)
    t = np.linspace(0, 10, 501)
    y = 30 * np.sin(2 * np.pi * 1.0 * t + np.pi/2)
    extractor = WindowExtractor({"window_start": 3.5})
    window = extractor.process(y)
    result = gatekeeper.call(lstm_clf.process, window)
    assert result["predicted_class"] == 1
    assert result["class_name"] == "Second Harmonic"
    assert result["confidence"] > 0.9


def test_both_mode_comparison(configs, gatekeeper):
    rnn_clf = RNNClassifier({
        "hidden_size": 64, "num_layers": 1, "weights_path": configs["app"]["rnn_model_path"]
    })
    lstm_clf = LSTMClassifier({
        "hidden_size": 128, "num_layers": 2, "dropout": 0.3, "weights_path": configs["app"]["lstm_model_path"]
    })
    t = np.linspace(0, 10, 501)
    y = 20 * np.sin(2 * np.pi * 1.5 * t + np.pi)
    extractor = WindowExtractor({"window_start": 5.0})
    window = extractor.process(y)
    rnn_res = gatekeeper.call(rnn_clf.process, window)
    lstm_res = gatekeeper.call(lstm_clf.process, window)
    comparator = ResultComparator({})
    diff = comparator.process(rnn_res, lstm_res)
    assert diff["agreement"] is True
    assert diff["rnn_predicted"] == "Third Harmonic"
    assert diff["lstm_predicted"] == "Third Harmonic"


def test_window_boundary_left(configs):
    t = np.linspace(0, 10, 501)
    y = np.sin(2 * np.pi * 0.5 * t)
    extractor = WindowExtractor({"window_start": 0.0})
    window = extractor.process(y)
    assert window.shape == (1, 50, 1)


def test_window_boundary_right(configs):
    t = np.linspace(0, 10, 501)
    y = np.sin(2 * np.pi * 0.5 * t)
    extractor = WindowExtractor({"window_start": 9.0})
    window = extractor.process(y)
    assert window.shape == (1, 50, 1)


def test_all_channels_disabled_no_crash(configs, gatekeeper):
    y = np.zeros(501)
    extractor = WindowExtractor({"window_start": 2.0})
    window = extractor.process(y)
    rnn_clf = RNNClassifier({
        "hidden_size": 64, "num_layers": 1, "weights_path": configs["app"]["rnn_model_path"]
    })
    result = gatekeeper.call(rnn_clf.process, window)
    assert "predicted_class" in result


def test_noise_sigma_impact():
    t = np.linspace(0, 10, 501)
    y = np.sin(2 * np.pi * 0.5 * t)
    extractor = WindowExtractor({"window_start": 2.0})
    window_clean = extractor.process(y, noise_sigma=0.0)
    window_noisy = extractor.process(y, noise_sigma=0.3)
    assert not np.array_equal(window_clean, window_noisy)


def test_noise_sigma_out_of_range():
    extractor = WindowExtractor({"window_start": 2.0})
    with pytest.raises(ValueError):
        extractor.process(np.zeros(501), noise_sigma=0.6)


def test_gatekeeper_retries(configs):
    gk = ModelGatekeeper({**configs["rate"], "max_retries": 1})
    call_count = 0

    def failing_fn():
        nonlocal call_count
        call_count += 1
        raise RuntimeError("Transient failure")

    with pytest.raises(RuntimeError):
        gk.call(failing_fn)

    # attempt 1 + 1 retry = 2 calls
    assert call_count == 2


def test_single_channel_enabled(configs, gatekeeper):
    t = np.linspace(0, 10, 501)
    y = 50 * np.sin(2 * np.pi * 0.5 * t)
    extractor = WindowExtractor({"window_start": 1.0})
    window = extractor.process(y)
    rnn_cfg = {"hidden_size": 64, "num_layers": 1, "weights_path": configs["app"]["rnn_model_path"]}
    result = gatekeeper.call(RNNClassifier(rnn_cfg).process, window)
    assert "predicted_class" in result
    assert 0 <= result["predicted_class"] <= 3


def test_agreement_true_when_classifiers_match(configs, gatekeeper):
    t = np.linspace(0, 10, 501)
    y = 50 * np.sin(2 * np.pi * 0.5 * t)
    extractor = WindowExtractor({"window_start": 2.0})
    window = extractor.process(y)
    rnn_clf = RNNClassifier({"hidden_size": 64, "num_layers": 1, "weights_path": configs["app"]["rnn_model_path"]})
    lstm_clf = LSTMClassifier({"hidden_size": 128, "num_layers": 2, "dropout": 0.3, "weights_path": configs["app"]["lstm_model_path"]})
    rnn_r = gatekeeper.call(rnn_clf.process, window)
    lstm_r = gatekeeper.call(lstm_clf.process, window)
    if rnn_r["predicted_class"] == lstm_r["predicted_class"]:
        diff = ResultComparator({}).process(rnn_r, lstm_r)
        assert diff["agreement"] is True


def test_agreement_false_when_classifiers_disagree():
    from fourier.shared.constants import WAVE_NAMES
    from fourier.shared.types import ClassifierResult

    def make_result(cls: int) -> ClassifierResult:
        probs = [0.0, 0.0, 0.0, 0.0]
        probs[cls] = 0.9
        probs[(cls + 1) % 4] = 0.1
        return ClassifierResult(predicted_class=cls, class_name=WAVE_NAMES[cls],
                                confidence=0.9, probabilities=probs, runner_up=(cls + 1) % 4)

    diff = ResultComparator({}).process(make_result(0), make_result(1))
    assert diff["agreement"] is False


def test_confidence_delta_zero_when_same_confidence():
    from fourier.shared.constants import WAVE_NAMES
    from fourier.shared.types import ClassifierResult

    def make_result(cls: int) -> ClassifierResult:
        probs = [0.0, 0.0, 0.0, 0.0]
        probs[cls] = 0.8
        probs[(cls + 1) % 4] = 0.2
        return ClassifierResult(predicted_class=cls, class_name=WAVE_NAMES[cls],
                                confidence=0.8, probabilities=probs, runner_up=(cls + 1) % 4)

    diff = ResultComparator({}).process(make_result(0), make_result(0))
    assert diff["confidence_delta"] == pytest.approx(0.0, abs=1e-6)
