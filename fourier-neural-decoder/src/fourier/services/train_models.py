from __future__ import annotations

import copy
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
    """Generate composite multi-channel signals. Label = dominant (highest-amplitude) channel."""
    cfg = _load_training_config()["data"]
    if "seed" in cfg:
        np.random.seed(int(cfg["seed"]))
    freqs: list[float] = cfg["class_frequencies_hz"]
    window_pts: int = int(cfg["window_points"])
    noise_std: float = float(cfg["noise_std"])
    samples_per_class = n // len(freqs)
    t = np.linspace(0, float(cfg["window_seconds"]), window_pts, endpoint=False)
    X_list, y_list = [], []
    for dominant_cls, dominant_freq in enumerate(freqs):
        for _ in range(samples_per_class):
            amp_dominant = np.random.uniform(0.6, 1.0)
            phase_d = np.random.uniform(0, 2 * math.pi)
            signal = amp_dominant * np.sin(2 * math.pi * float(dominant_freq) * t + phase_d)
            n_others = np.random.randint(0, len(freqs))
            other_cls = np.random.choice(
                [i for i in range(len(freqs)) if i != dominant_cls], n_others, replace=False
            )
            for oc in other_cls:
                amp_other = np.random.uniform(0.1, amp_dominant * 0.55)
                phase_o = np.random.uniform(0, 2 * math.pi)
                signal += amp_other * np.sin(2 * math.pi * float(freqs[oc]) * t + phase_o)
            signal = _add_noise(signal, std=noise_std)
            mean, std = float(np.mean(signal)), float(np.std(signal))
            signal = (signal - mean) / std if std > 1e-8 else np.zeros_like(signal)
            X_list.append(signal.reshape(window_pts, 1).astype(np.float32))
            y_list.append(dominant_cls)
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
    model: nn.Module, loader: DataLoader, optimizer: torch.optim.Optimizer,
    criterion: nn.Module, grad_clip: float = 1.0,
) -> float:
    model.train()
    total_loss = 0.0
    for xb, yb in loader:
        optimizer.zero_grad()
        loss = criterion(model(xb), yb)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), max_norm=grad_clip)
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
    step_size = int(cfg.get("lr_step", 50))
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=step_size, gamma=float(cfg.get("lr_gamma", 0.5)))
    criterion = nn.CrossEntropyLoss()
    grad_clip = float(cfg.get("grad_clip", 1.0))
    early_stop_acc = float(cfg.get("early_stop_acc", 1.0))
    best_acc, best_state = 0.0, None
    for epoch in range(1, int(cfg["epochs"]) + 1):
        loss = _train_epoch(model, loader, optimizer, criterion, grad_clip)
        scheduler.step()
        acc = _eval_model(model, test_loader)
        if acc > best_acc:
            best_acc = acc
            best_state = copy.deepcopy(model.state_dict())
        if epoch % int(cfg["log_every_n_epochs"]) == 0:
            print(f"RNN epoch {epoch}/{cfg['epochs']} loss={loss:.4f} acc={acc:.2%} best={best_acc:.2%}")
        if best_acc >= early_stop_acc:
            print(f"RNN early stop at epoch {epoch} — reached {best_acc:.2%}")
            break
    if best_state is not None:
        model.load_state_dict(best_state)
    print(f"RNN best accuracy: {best_acc:.2%}")
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
    step_size = int(cfg.get("lr_step", 50))
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=step_size, gamma=float(cfg.get("lr_gamma", 0.5)))
    criterion = nn.CrossEntropyLoss()
    grad_clip = float(cfg.get("grad_clip", 1.0))
    early_stop_acc = float(cfg.get("early_stop_acc", 1.0))
    best_acc, best_state = 0.0, None
    for epoch in range(1, int(cfg["epochs"]) + 1):
        loss = _train_epoch(model, loader, optimizer, criterion, grad_clip)
        scheduler.step()
        acc = _eval_model(model, test_loader)
        if acc > best_acc:
            best_acc = acc
            best_state = copy.deepcopy(model.state_dict())
        if epoch % int(cfg["log_every_n_epochs"]) == 0:
            print(f"LSTM epoch {epoch}/{cfg['epochs']} loss={loss:.4f} acc={acc:.2%} best={best_acc:.2%}")
        if best_acc >= early_stop_acc:
            print(f"LSTM early stop at epoch {epoch} — reached {best_acc:.2%}")
            break
    if best_state is not None:
        model.load_state_dict(best_state)
    print(f"LSTM best accuracy: {best_acc:.2%}")
    save_weights(model, _MODELS_DIR / "lstm_classifier.pt")
    return model


if __name__ == "__main__":
    print("Training RNN...")
    train_rnn()
    print("Training LSTM...")
    train_lstm()
    print("Done.")
