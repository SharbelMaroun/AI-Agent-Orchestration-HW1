from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from fourier.sdk.lstm_classifier import LSTMModel
from fourier.sdk.rnn_classifier import RNNModel

_CONFIG_DIR = Path(__file__).resolve().parents[3] / "config"
_MODELS_DIR = Path(__file__).resolve().parents[3] / "models"


def _load_training_config() -> dict[str, Any]:
    path = _CONFIG_DIR / "training_config.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def generate_synthetic_data(n: int = 1000) -> tuple[np.ndarray, np.ndarray]:
    cfg = _load_training_config()["data"]
    freqs: list[float] = cfg["class_frequencies_hz"]
    window_pts: int = int(cfg["window_points"])
    noise_std: float = float(cfg["noise_std"])
    samples_per_class = n // len(freqs)
    t = np.linspace(0, float(cfg["window_seconds"]), window_pts, endpoint=False)
    X_list, y_list = [], []
    for cls, freq in enumerate(freqs):
        for _ in range(samples_per_class):
            phase = np.random.uniform(0, 2 * math.pi)
            signal = np.sin(2 * math.pi * float(freq) * t + phase)
            signal = _add_noise(signal, std=noise_std)
            signal = signal / max(float(np.max(np.abs(signal))), 1e-8)
            X_list.append(signal.reshape(window_pts, 1).astype(np.float32))
            y_list.append(cls)
    return np.array(X_list, dtype=np.float32), np.array(y_list, dtype=np.int64)


def _add_noise(arr: np.ndarray, std: float) -> np.ndarray:
    return arr + np.random.normal(0, std, size=arr.shape)


def _split_data(
    X: np.ndarray, y: np.ndarray, test_ratio: float | None = None
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if test_ratio is None:
        test_ratio = float(_load_training_config()["data"]["test_ratio"])
    idx = np.random.permutation(len(X))
    split = int(len(X) * (1 - test_ratio))
    train_idx, test_idx = idx[:split], idx[split:]
    return X[train_idx], X[test_idx], y[train_idx], y[test_idx]


def _train_epoch(
    model: nn.Module, loader: DataLoader, optimizer: torch.optim.Optimizer, criterion: nn.Module
) -> float:
    model.train()
    total_loss = 0.0
    for xb, yb in loader:
        optimizer.zero_grad()
        loss = criterion(model(xb), yb)
        loss.backward()
        optimizer.step()
        total_loss += float(loss.item())
    return total_loss / len(loader)


def _eval_model(model: nn.Module, loader: DataLoader) -> float:
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for xb, yb in loader:
            preds = torch.argmax(model(xb), dim=1)
            correct += int((preds == yb).sum())
            total += len(yb)
    return correct / total if total > 0 else 0.0


def save_weights(model: nn.Module, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), path)


def train_rnn(config: dict[str, Any] | None = None) -> RNNModel:
    cfg = config or _load_training_config()["rnn"]
    X, y = generate_synthetic_data(int(_load_training_config()["data"]["n_samples"]))
    X_tr, X_te, y_tr, y_te = _split_data(X, y)
    bs = int(cfg["batch_size"])
    loader = DataLoader(TensorDataset(torch.tensor(X_tr), torch.tensor(y_tr)), batch_size=bs, shuffle=True)
    test_loader = DataLoader(TensorDataset(torch.tensor(X_te), torch.tensor(y_te)), batch_size=bs)
    model = RNNModel(hidden_size=int(cfg["hidden_size"]), num_layers=int(cfg["num_layers"]))
    optimizer = torch.optim.Adam(model.parameters(), lr=float(cfg["learning_rate"]))
    criterion = nn.CrossEntropyLoss()
    for epoch in range(1, int(cfg["epochs"]) + 1):
        loss = _train_epoch(model, loader, optimizer, criterion)
        if epoch % int(cfg["log_every_n_epochs"]) == 0:
            print(f"RNN epoch {epoch}/{cfg['epochs']} loss={loss:.4f} acc={_eval_model(model, test_loader):.2%}")
    save_weights(model, _MODELS_DIR / "rnn_classifier.pt")
    return model


def train_lstm(config: dict[str, Any] | None = None) -> LSTMModel:
    cfg = config or _load_training_config()["lstm"]
    X, y = generate_synthetic_data(int(_load_training_config()["data"]["n_samples"]))
    X_tr, X_te, y_tr, y_te = _split_data(X, y)
    bs = int(cfg["batch_size"])
    loader = DataLoader(TensorDataset(torch.tensor(X_tr), torch.tensor(y_tr)), batch_size=bs, shuffle=True)
    test_loader = DataLoader(TensorDataset(torch.tensor(X_te), torch.tensor(y_te)), batch_size=bs)
    model = LSTMModel(
        hidden_size=int(cfg["hidden_size"]), num_layers=int(cfg["num_layers"]), dropout=float(cfg["dropout"])
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=float(cfg["learning_rate"]))
    criterion = nn.CrossEntropyLoss()
    for epoch in range(1, int(cfg["epochs"]) + 1):
        loss = _train_epoch(model, loader, optimizer, criterion)
        if epoch % int(cfg["log_every_n_epochs"]) == 0:
            print(f"LSTM epoch {epoch}/{cfg['epochs']} loss={loss:.4f} acc={_eval_model(model, test_loader):.2%}")
    save_weights(model, _MODELS_DIR / "lstm_classifier.pt")
    return model


if __name__ == "__main__":
    print("Training RNN...")
    train_rnn()
    print("Training LSTM...")
    train_lstm()
    print("Done.")
