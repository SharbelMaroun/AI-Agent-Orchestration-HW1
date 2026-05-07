"""Shared training-loop helpers for RNN / LSTM / FC regressors.

Each model has its own architecture but identical training pipeline:
shared `_generate_dataset`, MSE loss, Adam optimiser, gradient clipping,
80/20 train/test split. This module factors out the loop so each
`train_<model>.py` becomes a thin model-instantiation wrapper.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import torch
import torch.nn as nn


def split_train_test(
    x: torch.Tensor, c: torch.Tensor, y: torch.Tensor, test_ratio: float,
) -> tuple[tuple[torch.Tensor, ...], tuple[torch.Tensor, ...]]:
    test_n = int(x.shape[0] * float(test_ratio))
    train = (x[test_n:], c[test_n:], y[test_n:])
    test = (x[:test_n], c[:test_n], y[:test_n])
    return train, test


def fit(
    model: nn.Module,
    train: tuple[torch.Tensor, torch.Tensor, torch.Tensor],
    cfg: dict[str, Any],
) -> None:
    x_tr, c_tr, y_tr = train
    opt = torch.optim.Adam(model.parameters(), lr=float(cfg["learning_rate"]))
    loss_fn = nn.MSELoss()
    batch = int(cfg["batch_size"])
    epochs = int(cfg["epochs"])
    grad_clip = float(cfg.get("grad_clip", 1.0))

    for _ in range(epochs):
        model.train()
        idx = torch.randperm(x_tr.shape[0])
        for s in range(0, x_tr.shape[0], batch):
            sel = idx[s:s + batch]
            pred = model(x_tr[sel], c_tr[sel])
            loss = loss_fn(pred, y_tr[sel])
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
            opt.step()


def evaluate(model: nn.Module, test: tuple[torch.Tensor, torch.Tensor, torch.Tensor]) -> dict[str, float]:
    x_te, c_te, y_te = test
    model.eval()
    with torch.no_grad():
        pred_te = model(x_te, c_te)
        mae = float(torch.mean(torch.abs(pred_te - y_te)))
        rmse = float(torch.sqrt(torch.mean((pred_te - y_te) ** 2)))
    return {"test_mae": mae, "test_rmse": rmse}


def save_state(model: nn.Module, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), out_path)


def run_training(
    build_model: Any, model_cfg: dict[str, Any], data_cfg: dict[str, Any],
    dataset: tuple[torch.Tensor, torch.Tensor, torch.Tensor], out_path: Path,
) -> dict[str, float]:
    """Wire build_model + dataset + cfg into the standard fit/evaluate/save pipeline."""
    torch.manual_seed(int(data_cfg.get("seed", 42)))
    train, test = split_train_test(*dataset, test_ratio=float(data_cfg["test_ratio"]))
    model = build_model()
    fit(model, train, model_cfg)
    metrics = evaluate(model, test)
    save_state(model, out_path)
    return metrics
