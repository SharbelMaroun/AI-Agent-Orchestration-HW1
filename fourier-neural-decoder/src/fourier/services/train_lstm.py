from __future__ import annotations

from pathlib import Path
from typing import Any

from fourier.sdk.lstm_regressor import BookLSTMRegressor
from fourier.services._train_loop import run_training
from fourier.services.train_rnn import _generate_dataset


def train_lstm(lstm_cfg: dict[str, Any], data_cfg: dict[str, Any], out_path: Path) -> dict[str, float]:
    dataset = _generate_dataset(
        n_samples=int(data_cfg["n_samples"]),
        alpha_max=float(data_cfg.get("alpha_train_max", 0.3)),
        beta_max=float(data_cfg.get("beta_train_max", 0.3)),
        seed=int(data_cfg.get("seed", 42)),
    )
    return run_training(
        build_model=lambda: BookLSTMRegressor(hidden_size=int(lstm_cfg["hidden_size"])),
        model_cfg=lstm_cfg, data_cfg=data_cfg, dataset=dataset, out_path=out_path, name="lstm",
    )
