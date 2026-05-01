from __future__ import annotations

import numpy as np
import pytest
import torch

from fourier.sdk.rnn_classifier import RNNClassifier, RNNModel


def _save_dummy_weights(path, hidden_size=64, num_layers=1):
    model = RNNModel(hidden_size=hidden_size, num_layers=num_layers)
    torch.save(model.state_dict(), path)


def _base_config(tmp_path, hidden_size=64, num_layers=1):
    weights = tmp_path / "rnn_test.pt"
    _save_dummy_weights(weights, hidden_size, num_layers)
    return {"hidden_size": hidden_size, "num_layers": num_layers, "weights_path": str(weights)}


def _window() -> np.ndarray:
    return np.random.randn(1, 50, 1).astype(np.float32)


def test_rnn_model_is_nn_module():
    assert isinstance(RNNModel(), torch.nn.Module)


def test_rnn_model_input_size_one():
    model = RNNModel()
    assert model.rnn.input_size == 1


def test_rnn_model_output_size_four():
    model = RNNModel()
    assert model.fc.out_features == 4


def test_rnn_model_forward_no_error():
    model = RNNModel()
    x = torch.randn(1, 50, 1)
    model(x)


def test_rnn_model_forward_returns_shape_1_4():
    model = RNNModel()
    x = torch.randn(1, 50, 1)
    out = model(x)
    assert out.shape == (1, 4)


def test_rnn_model_forward_output_sums_to_one():
    model = RNNModel()
    x = torch.randn(1, 50, 1)
    out = model(x)
    assert float(out.sum()) == pytest.approx(1.0, abs=1e-5)


def test_rnn_model_uses_tanh_activation():
    model = RNNModel()
    assert model.rnn.nonlinearity == "tanh"


def test_rnn_model_single_rnn_layer():
    model = RNNModel()
    assert isinstance(model.rnn, torch.nn.RNN)


def test_rnn_classifier_init_accepts_config(tmp_path):
    cfg = _base_config(tmp_path)
    clf = RNNClassifier(cfg)
    assert clf.config == cfg


def test_validate_config_raises_on_missing_hidden_size():
    with pytest.raises(KeyError):
        RNNClassifier({"num_layers": 1, "weights_path": "x.pt"})


def test_validate_config_raises_on_missing_num_layers():
    with pytest.raises(KeyError):
        RNNClassifier({"hidden_size": 64, "weights_path": "x.pt"})


def test_validate_config_raises_on_missing_weights_path():
    with pytest.raises(KeyError):
        RNNClassifier({"hidden_size": 64, "num_layers": 1})


def test_rnn_classifier_raises_file_not_found_on_missing_weights():
    with pytest.raises(FileNotFoundError):
        RNNClassifier({"hidden_size": 64, "num_layers": 1, "weights_path": "nonexistent.pt"})


def test_process_returns_classifier_result(tmp_path):
    clf = RNNClassifier(_base_config(tmp_path))
    result = clf.process(_window())
    for key in ("predicted_class", "class_name", "confidence", "probabilities", "runner_up"):
        assert key in result


def test_predicted_class_in_range_0_3(tmp_path):
    clf = RNNClassifier(_base_config(tmp_path))
    result = clf.process(_window())
    assert 0 <= result["predicted_class"] <= 3


def test_class_name_is_string(tmp_path):
    clf = RNNClassifier(_base_config(tmp_path))
    result = clf.process(_window())
    assert isinstance(result["class_name"], str)


def test_confidence_is_float_in_0_1(tmp_path):
    clf = RNNClassifier(_base_config(tmp_path))
    result = clf.process(_window())
    assert 0.0 <= result["confidence"] <= 1.0


def test_probabilities_is_list_of_4_summing_to_1(tmp_path):
    clf = RNNClassifier(_base_config(tmp_path))
    result = clf.process(_window())
    assert len(result["probabilities"]) == 4
    assert sum(result["probabilities"]) == pytest.approx(1.0, abs=1e-4)


def test_runner_up_is_second_highest(tmp_path):
    clf = RNNClassifier(_base_config(tmp_path))
    result = clf.process(_window())
    probs = result["probabilities"]
    sorted_idx = sorted(range(4), key=lambda i: probs[i], reverse=True)
    assert result["runner_up"] == sorted_idx[1]


def test_confidence_equals_max_probability(tmp_path):
    clf = RNNClassifier(_base_config(tmp_path))
    result = clf.process(_window())
    assert result["confidence"] == pytest.approx(max(result["probabilities"]), abs=1e-5)
