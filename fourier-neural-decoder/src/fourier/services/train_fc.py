from __future__ import annotations

from pathlib import Path
from typing import Any

from fourier.sdk.fc_regressor import BookFCRegressor
from fourier.services._train_loop import run_training
from fourier.services.train_rnn import _generate_dataset


def train_fc(fc_cfg: dict[str, Any], data_cfg: dict[str, Any], out_path: Path) -> dict[str, float]:
    dataset = _generate_dataset(
        n_samples=int(data_cfg["n_samples"]),
        alpha_max=float(data_cfg.get("alpha_train_max", 0.3)),
        beta_max=float(data_cfg.get("beta_train_max", 0.3)),
        seed=int(data_cfg.get("seed", 42)),
    )
    return run_training(
        build_model=lambda: BookFCRegressor(hidden_size=int(fc_cfg["hidden_size"])),
        model_cfg=fc_cfg, data_cfg=data_cfg, dataset=dataset, out_path=out_path, name="fc",
    )
