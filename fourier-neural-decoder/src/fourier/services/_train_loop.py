"""Shared training-loop helpers for RNN / LSTM / FC regressors.

Each model has its own architecture but identical training pipeline:
shared `_generate_dataset`, MSE loss, Adam optimiser, gradient clipping,
80/20 train/test split. This module factors out the loop so each
`train_<model>.py` becomes a thin model-instantiation wrapper.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn

logger = logging.getLogger(__name__)

# Tolerance for the "accuracy" metric — fraction of output values whose
# absolute error is within ACC_TOL of the truth (raw amplitude units).
ACC_TOL = 1.0
# How often (in epochs) to print metrics during fit.
LOG_EVERY = 5


def split_train_test(
    x: torch.Tensor, c: torch.Tensor, y: torch.Tensor, test_ratio: float,
) -> tuple[tuple[torch.Tensor, ...], tuple[torch.Tensor, ...]]:
    test_n = int(x.shape[0] * float(test_ratio))
    train = (x[test_n:], c[test_n:], y[test_n:])
    test = (x[:test_n], c[:test_n], y[:test_n])
    return train, test


def _epoch_metrics(model: nn.Module, x: torch.Tensor, c: torch.Tensor, y: torch.Tensor) -> dict[str, float]:
    model.eval()
    with torch.no_grad():
        pred = model(x, c)
        diff = pred - y
        mse = float(torch.mean(diff ** 2))
        mae = float(torch.mean(torch.abs(diff)))
        acc = float(torch.mean((torch.abs(diff) <= ACC_TOL).float()))
    return {"mse": mse, "mae": mae, "acc": acc}


def fit(
    model: nn.Module,
    train: tuple[torch.Tensor, torch.Tensor, torch.Tensor],
    cfg: dict[str, Any],
    test: tuple[torch.Tensor, torch.Tensor, torch.Tensor] | None = None,
    name: str = "model",
) -> None:
    x_tr, c_tr, y_tr = train
    opt = torch.optim.Adam(model.parameters(), lr=float(cfg["learning_rate"]))
    loss_fn = nn.MSELoss()
    batch = int(cfg["batch_size"])
    epochs = int(cfg["epochs"])
    grad_clip = float(cfg.get("grad_clip", 1.0))

    for epoch in range(1, epochs + 1):
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

        if epoch == 1 or epoch == epochs or epoch % LOG_EVERY == 0:
            tr = _epoch_metrics(model, x_tr, c_tr, y_tr)
            te = _epoch_metrics(model, *test) if test is not None else None
            te_str = (f"  test mse={te['mse']:.3f} mae={te['mae']:.3f} acc={te['acc']:.3f}"
                      if te is not None else "")
            logger.info(
                "[%s] epoch %3d/%d  train mse=%.3f mae=%.3f acc=%.3f%s",
                name, epoch, epochs, tr['mse'], tr['mae'], tr['acc'], te_str,
            )


def evaluate(model: nn.Module, test: tuple[torch.Tensor, torch.Tensor, torch.Tensor]) -> dict[str, float]:
    m = _epoch_metrics(model, *test)
    return {"test_mse": m["mse"], "test_mae": m["mae"], "test_acc": m["acc"],
            "test_rmse": m["mse"] ** 0.5}


def save_state(model: nn.Module, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), out_path)


def run_training(
    build_model: Any, model_cfg: dict[str, Any], data_cfg: dict[str, Any],
    dataset: tuple[torch.Tensor, torch.Tensor, torch.Tensor], out_path: Path,
    name: str = "model",
) -> dict[str, float]:
    """Wire build_model + dataset + cfg into the standard fit/evaluate/save pipeline."""
    torch.manual_seed(int(data_cfg.get("seed", 42)))
    train, test = split_train_test(*dataset, test_ratio=float(data_cfg["test_ratio"]))
    model = build_model()
    fit(model, train, model_cfg, test=test, name=name)
    metrics = evaluate(model, test)
    save_state(model, out_path)
    logger.info(
        "[%s] DONE  test mse=%.3f mae=%.3f acc=%.3f rmse=%.3f",
        name, metrics["test_mse"], metrics["test_mae"], metrics["test_acc"], metrics["test_rmse"],
    )
    return metrics
