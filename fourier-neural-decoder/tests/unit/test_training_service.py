from __future__ import annotations

import numpy as np
import pytest

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from fourier.services.train_models import (
    _add_noise,
    _eval_model,
    _split_data,
    _train_epoch,
    generate_synthetic_data,
    save_weights,
)


def test_generate_synthetic_data_returns_tuple():
    result = generate_synthetic_data(n=100)
    assert isinstance(result, tuple) and len(result) == 2


def test_X_shape_is_n_by_50_by_1():
    X, _ = generate_synthetic_data(n=100)
    assert X.shape == (100, 50, 1)


def test_y_shape_is_n():
    _, y = generate_synthetic_data(n=100)
    assert y.shape == (100,)


def test_y_values_in_0_to_3():
    _, y = generate_synthetic_data(n=100)
    assert set(y.tolist()).issubset({0, 1, 2, 3})


def test_data_is_balanced_25_per_class():
    _, y = generate_synthetic_data(n=100)
    for cls in range(4):
        assert int(np.sum(y == cls)) == 25


def _dominant_freq(signal: np.ndarray) -> float:
    fft = np.abs(np.fft.rfft(signal))
    freqs = np.fft.rfftfreq(len(signal), d=1.0 / len(signal))
    return float(freqs[1 + int(np.argmax(fft[1:]))])


def test_class_0_uses_05hz_pattern():
    np.random.seed(42)
    X, y = generate_synthetic_data(n=200)
    dominant = [_dominant_freq(X[i].reshape(50)) for i in range(len(y)) if y[i] == 0]
    assert any(abs(f - 0.5) < 1.0 for f in dominant)


def test_class_1_uses_1hz_pattern():
    np.random.seed(42)
    X, y = generate_synthetic_data(n=200)
    dominant = [_dominant_freq(X[i].reshape(50)) for i in range(len(y)) if y[i] == 1]
    assert any(abs(f - 1.0) < 1.0 for f in dominant)


def test_class_2_uses_15hz_pattern():
    np.random.seed(42)
    X, y = generate_synthetic_data(n=200)
    dominant = [_dominant_freq(X[i].reshape(50)) for i in range(len(y)) if y[i] == 2]
    assert any(abs(f - 1.5) < 1.0 for f in dominant)


def test_class_3_uses_2hz_pattern():
    np.random.seed(42)
    X, y = generate_synthetic_data(n=200)
    dominant = [_dominant_freq(X[i].reshape(50)) for i in range(len(y)) if y[i] == 3]
    assert any(abs(f - 2.0) < 1.0 for f in dominant)


def test_generated_x_values_normalized_in_minus1_1():
    X, _ = generate_synthetic_data(n=100)
    assert float(np.max(np.abs(X))) <= 1.0 + 1e-6


def test_add_noise_adds_gaussian_noise():
    arr = np.zeros(50)
    noisy = _add_noise(arr, std=0.1)
    assert not np.array_equal(arr, noisy)


def test_split_data_returns_4_arrays():
    X = np.random.randn(100, 50, 1).astype(np.float32)
    y = np.zeros(100, dtype=np.int64)
    result = _split_data(X, y)
    assert len(result) == 4


def test_split_data_train_is_80_percent():
    X = np.random.randn(100, 50, 1).astype(np.float32)
    y = np.zeros(100, dtype=np.int64)
    X_train, X_test, y_train, y_test = _split_data(X, y, test_ratio=0.2)
    assert len(X_train) == 80


def test_split_data_test_is_20_percent():
    X = np.random.randn(100, 50, 1).astype(np.float32)
    y = np.zeros(100, dtype=np.int64)
    X_train, X_test, y_train, y_test = _split_data(X, y, test_ratio=0.2)
    assert len(X_test) == 20


def _tiny_loader():
    X = torch.randn(16, 50, 1)
    y = torch.randint(0, 4, (16,))
    return DataLoader(TensorDataset(X, y), batch_size=8)


def test_train_epoch_returns_float():
    from fourier.sdk.rnn_classifier import RNNModel
    model = RNNModel(hidden_size=8, num_layers=1)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    criterion = nn.CrossEntropyLoss()
    loss = _train_epoch(model, _tiny_loader(), optimizer, criterion)
    assert isinstance(loss, float) and loss >= 0


def test_eval_model_returns_accuracy_float():
    from fourier.sdk.rnn_classifier import RNNModel
    model = RNNModel(hidden_size=8, num_layers=1)
    acc = _eval_model(model, _tiny_loader())
    assert 0.0 <= acc <= 1.0


def test_save_weights_creates_file(tmp_path):
    from fourier.sdk.rnn_classifier import RNNModel
    model = RNNModel(hidden_size=8, num_layers=1)
    path = tmp_path / "test.pt"
    save_weights(model, path)
    assert path.exists()


_TINY_TRAINING_CFG = {
    "rnn": {"hidden_size": 8, "num_layers": 1, "learning_rate": 0.01,
            "batch_size": 8, "epochs": 1, "log_every_n_epochs": 1},
    "lstm": {"hidden_size": 8, "num_layers": 2, "dropout": 0.0, "learning_rate": 0.01,
             "batch_size": 8, "epochs": 1, "log_every_n_epochs": 1},
    "data": {"n_samples": 40, "test_ratio": 0.25, "noise_std": 0.01,
             "class_frequencies_hz": [0.5, 1.0, 1.5, 2.0], "window_seconds": 1.0, "window_points": 50},
}


def test_train_rnn_returns_rnn_model(monkeypatch, tmp_path):
    import fourier.services.train_models as tm
    from fourier.sdk.rnn_classifier import RNNModel
    monkeypatch.setattr(tm, "_load_training_config", lambda: _TINY_TRAINING_CFG)
    monkeypatch.setattr(tm, "_MODELS_DIR", tmp_path)
    model = tm.train_rnn()
    assert isinstance(model, RNNModel)


def test_train_rnn_saves_weights_file(monkeypatch, tmp_path):
    import fourier.services.train_models as tm
    monkeypatch.setattr(tm, "_load_training_config", lambda: _TINY_TRAINING_CFG)
    monkeypatch.setattr(tm, "_MODELS_DIR", tmp_path)
    tm.train_rnn()
    assert (tmp_path / "rnn_classifier.pt").exists()


def test_train_lstm_returns_lstm_model(monkeypatch, tmp_path):
    import fourier.services.train_models as tm
    from fourier.sdk.lstm_classifier import LSTMModel
    monkeypatch.setattr(tm, "_load_training_config", lambda: _TINY_TRAINING_CFG)
    monkeypatch.setattr(tm, "_MODELS_DIR", tmp_path)
    model = tm.train_lstm()
    assert isinstance(model, LSTMModel)


def test_train_lstm_saves_weights_file(monkeypatch, tmp_path):
    import fourier.services.train_models as tm
    monkeypatch.setattr(tm, "_load_training_config", lambda: _TINY_TRAINING_CFG)
    monkeypatch.setattr(tm, "_MODELS_DIR", tmp_path)
    tm.train_lstm()
    assert (tmp_path / "lstm_classifier.pt").exists()
