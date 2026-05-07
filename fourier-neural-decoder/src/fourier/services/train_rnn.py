from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import torch

from fourier.sdk.rnn_regressor import BookRNNRegressor
from fourier.services._train_loop import run_training
from fourier.shared.constants import DURATION, EXTRACT_POINTS, ID_MODE_SIGNALS, ID_MODE_SR


def _generate_dataset(
    n_samples: int,
    alpha_max: float,
    beta_max: float,
    amp_min: float,
    amp_max: float,
    seed: int,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Build (samples, c_vectors, targets) for the regression task.

    Parametric noise model (matches the UI sliders):
        y_k(t) = (A_k + α_k·A_k·ε_k) · sin(2π·f_k·t + φ_k + β_k·π·ε_k)
    with ε_k ~ Uniform(-1, 1) drawn once per channel per training example,
    α_k ~ Uniform(0, alpha_max), β_k ~ Uniform(0, beta_max).
    Target = clean (un-perturbed) chosen channel — model learns to denoise.
    """
    rng = np.random.default_rng(seed)
    n_classes = len(ID_MODE_SIGNALS)
    total_samples = int(DURATION * ID_MODE_SR) + 1
    max_n_start = total_samples - EXTRACT_POINTS

    samples_list, c_list, target_list = [], [], []
    for _ in range(n_samples):
        amps = rng.uniform(amp_min, amp_max, size=n_classes)
        phases = rng.uniform(0, 2 * math.pi, size=n_classes)
        alphas = rng.uniform(0.0, alpha_max, size=n_classes)
        betas = rng.uniform(0.0, beta_max, size=n_classes)

        n_start = int(rng.integers(0, max_n_start + 1))
        t_grid = (n_start + np.arange(EXTRACT_POINTS, dtype=np.float64)) / float(ID_MODE_SR)

        per_channel_clean = np.zeros((n_classes, EXTRACT_POINTS), dtype=np.float64)
        per_channel_noisy = np.zeros((n_classes, EXTRACT_POINTS), dtype=np.float64)
        for k, sig in enumerate(ID_MODE_SIGNALS):
            f = float(sig["frequency"])
            # Per-sample ε: independent draw for each of the 10 time points.
            eps_k = rng.uniform(-1.0, 1.0, size=EXTRACT_POINTS)
            a_eff = amps[k] + alphas[k] * amps[k] * eps_k
            ph_eff = phases[k] + betas[k] * math.pi * eps_k
            per_channel_clean[k] = amps[k] * np.sin(2 * math.pi * f * t_grid + phases[k])
            per_channel_noisy[k] = a_eff * np.sin(2 * math.pi * f * t_grid + ph_eff)
        summed = per_channel_noisy.sum(axis=0)

        chosen = int(rng.integers(0, n_classes))
        c_vec = np.zeros(n_classes, dtype=np.float32)
        c_vec[chosen] = 1.0
        target = per_channel_clean[chosen]

        # Per-sample normalization: scale both summed input and target by max(|summed|)
        # so the network learns a scale-invariant mapping in [-1, 1].
        scale = float(np.max(np.abs(summed))) or 1.0
        summed = summed / scale
        target = (target / scale).astype(np.float32)

        samples_list.append(summed.astype(np.float32))
        c_list.append(c_vec)
        target_list.append(target)

    samples = torch.from_numpy(np.stack(samples_list)).unsqueeze(-1)   # (N, 10, 1)
    c_vectors = torch.from_numpy(np.stack(c_list))                      # (N, 4)
    targets = torch.from_numpy(np.stack(target_list))                   # (N, 10)
    return samples, c_vectors, targets


def train_rnn(rnn_cfg: dict[str, Any], data_cfg: dict[str, Any], out_path: Path) -> dict[str, float]:
    dataset = _generate_dataset(
        n_samples=int(data_cfg["n_samples"]),
        alpha_max=float(data_cfg.get("alpha_train_max", 1.0)),
        beta_max=float(data_cfg.get("beta_train_max", 1.0)),
        amp_min=float(data_cfg["amp_min"]),
        amp_max=float(data_cfg["amp_max"]),
        seed=int(data_cfg.get("seed", 42)),
    )
    return run_training(
        build_model=lambda: BookRNNRegressor(hidden_size=int(rnn_cfg["hidden_size"])),
        model_cfg=rnn_cfg, data_cfg=data_cfg, dataset=dataset, out_path=out_path,
    )
