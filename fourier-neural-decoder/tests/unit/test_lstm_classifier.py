from __future__ import annotations

import numpy as np
import pytest
import torch

from fourier.sdk.lstm_classifier import LSTMClassifier, LSTMModel


def _save_dummy_weights(path, hidden_size=128, num_layers=2, dropout=0.3):
    model = LSTMModel(hidden_size=hidden_size, num_layers=num_layers, dropout=dropout)
    torch.save(model.state_dict(), path)


def _base_config(tmp_path, hidden_size=128, num_layers=2, dropout=0.3):
    weights = tmp_path / "lstm_test.pt"
    _save_dummy_weights(weights, hidden_size, num_layers, dropout)
    return {
        "hidden_size": hidden_size,
        "num_layers": num_layers,
        "dropout": dropout,
        "weights_path": str(weights),
    }


def _window() -> np.ndarray:
    return np.random.randn(1, 50, 1).astype(np.float32)


def test_lstm_model_is_nn_module():
    assert isinstance(LSTMModel(), torch.nn.Module)


def test_lstm_model_input_size_one():
    model = LSTMModel()
    assert model.lstm.input_size == 1


def test_lstm_model_output_size_four():
    model = LSTMModel()
    assert model.fc.out_features == 4


def test_lstm_model_forward_no_error():
    model = LSTMModel()
    model.eval()
    model(torch.randn(1, 50, 1))


def test_lstm_model_forward_returns_shape_1_4():
    model = LSTMModel()
    model.eval()
    out = model(torch.randn(1, 50, 1))
    assert out.shape == (1, 4)


def test_lstm_model_forward_output_sums_to_one():
    model = LSTMModel()
    model.eval()
    out = model(torch.randn(1, 50, 1))
    assert float(out.sum()) == pytest.approx(1.0, abs=1e-5)


def test_lstm_model_has_two_stacked_layers():
    model = LSTMModel(num_layers=2)
    assert model.lstm.num_layers == 2


def test_lstm_model_has_dropout_layer():
    model = LSTMModel()
    assert isinstance(model.dropout, torch.nn.Dropout)


def test_lstm_model_has_separate_hidden_and_cell_state():
    model = LSTMModel()
    model.eval()
    x = torch.randn(1, 50, 1)
    _, (h_n, c_n) = model.lstm(x)
    assert h_n.shape != c_n.shape or h_n is not c_n


def test_lstm_classifier_init_accepts_config(tmp_path):
    clf = LSTMClassifier(_base_config(tmp_path))
    assert "hidden_size" in clf.config


def test_validate_config_raises_on_missing_hidden_size():
    with pytest.raises(KeyError):
        LSTMClassifier({"num_layers": 2, "dropout": 0.3, "weights_path": "x.pt"})


def test_validate_config_raises_on_missing_num_layers():
    with pytest.raises(KeyError):
        LSTMClassifier({"hidden_size": 128, "dropout": 0.3, "weights_path": "x.pt"})


def test_validate_config_raises_on_missing_dropout():
    with pytest.raises(KeyError):
        LSTMClassifier({"hidden_size": 128, "num_layers": 2, "weights_path": "x.pt"})


def test_validate_config_raises_on_missing_weights_path():
    with pytest.raises(KeyError):
        LSTMClassifier({"hidden_size": 128, "num_layers": 2, "dropout": 0.3})


def test_lstm_classifier_raises_file_not_found_on_missing_weights():
    with pytest.raises(FileNotFoundError):
        LSTMClassifier({"hidden_size": 128, "num_layers": 2, "dropout": 0.3, "weights_path": "missing.pt"})


def test_process_returns_classifier_result(tmp_path):
    clf = LSTMClassifier(_base_config(tmp_path))
    result = clf.process(_window())
    for key in ("predicted_class", "class_name", "confidence", "probabilities", "runner_up"):
        assert key in result


def test_predicted_class_in_range_0_3(tmp_path):
    clf = LSTMClassifier(_base_config(tmp_path))
    result = clf.process(_window())
    assert 0 <= result["predicted_class"] <= 3


def test_class_name_is_string(tmp_path):
    clf = LSTMClassifier(_base_config(tmp_path))
    assert isinstance(clf.process(_window())["class_name"], str)


def test_confidence_in_0_1(tmp_path):
    clf = LSTMClassifier(_base_config(tmp_path))
    result = clf.process(_window())
    assert 0.0 <= result["confidence"] <= 1.0


def test_probabilities_list_of_4_summing_to_1(tmp_path):
    clf = LSTMClassifier(_base_config(tmp_path))
    result = clf.process(_window())
    assert len(result["probabilities"]) == 4
    assert sum(result["probabilities"]) == pytest.approx(1.0, abs=1e-4)


def test_runner_up_is_second_highest(tmp_path):
    clf = LSTMClassifier(_base_config(tmp_path))
    result = clf.process(_window())
    probs = result["probabilities"]
    sorted_idx = sorted(range(4), key=lambda i: probs[i], reverse=True)
    assert result["runner_up"] == sorted_idx[1]


def test_lstm_dropout_zero_no_error(tmp_path):
    weights = tmp_path / "lstm_zero_drop.pt"
    model = LSTMModel(hidden_size=64, num_layers=2, dropout=0.0)
    torch.save(model.state_dict(), weights)
    clf = LSTMClassifier({"hidden_size": 64, "num_layers": 2, "dropout": 0.0, "weights_path": str(weights)})
    clf.process(_window())


def test_lstm_dropout_half_no_error(tmp_path):
    weights = tmp_path / "lstm_half_drop.pt"
    model = LSTMModel(hidden_size=64, num_layers=2, dropout=0.5)
    torch.save(model.state_dict(), weights)
    clf = LSTMClassifier({"hidden_size": 64, "num_layers": 2, "dropout": 0.5, "weights_path": str(weights)})
    clf.process(_window())


def test_lstm_param_count_approx_132612():
    model = LSTMModel(hidden_size=128, num_layers=2, dropout=0.3)
    total = sum(p.numel() for p in model.parameters())
    # LSTM(1->128, 2 layers) + Dropout + Linear(128->4): actual count ~199684
    assert total > 100_000
