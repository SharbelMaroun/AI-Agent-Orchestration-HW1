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
    seed: int,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Build (samples, c_vectors, targets) for the regression task.

    Matches the app's identification mode exactly:
      - Amplitudes and phases are FIXED at ID_MODE_SIGNALS (the same reference
        signals the UI locks when entering identification mode).
      - Each example varies only the context-window start (n_start) and the
        per-channel noise (α, β, per-sample ε).
      - Trained on LOW noise only (α, β ~ Uniform(0, alpha_max/beta_max) where
        alpha_max, beta_max ≪ 1) so the model is reliable for normal slider
        ranges; high-noise robustness is not the training objective.
      - Target = clean chosen channel at the same t_grid → models learn to
        denoise the chosen frequency component out of the noisy summation.
    """
    rng = np.random.default_rng(seed)
    n_classes = len(ID_MODE_SIGNALS)
    total_samples = int(DURATION * ID_MODE_SR) + 1
    max_n_start = total_samples - EXTRACT_POINTS

    # Fixed reference signals — the same the app locks in identification mode.
    amps = np.array([float(s["amplitude"]) for s in ID_MODE_SIGNALS])
    phases = np.array([float(s["phase"]) for s in ID_MODE_SIGNALS])
    freqs = np.array([float(s["frequency"]) for s in ID_MODE_SIGNALS])

    samples_list, c_list, target_list = [], [], []
    for _ in range(n_samples):
        alphas = rng.uniform(0.0, alpha_max, size=n_classes)
        betas = rng.uniform(0.0, beta_max, size=n_classes)

        n_start = int(rng.integers(0, max_n_start + 1))
        t_grid = (n_start + np.arange(EXTRACT_POINTS, dtype=np.float64)) / float(ID_MODE_SR)

        per_channel_clean = np.zeros((n_classes, EXTRACT_POINTS), dtype=np.float64)
        per_channel_noisy = np.zeros((n_classes, EXTRACT_POINTS), dtype=np.float64)
        for k in range(n_classes):
            f = float(freqs[k])
            # Per-sample ε: independent draw for each of the 10 time points.
            eps_k = rng.uniform(-1.0, 1.0, size=EXTRACT_POINTS)
            a_eff = amps[k] + alphas[k] * amps[k] * eps_k
            ph_eff = phases[k] + betas[k] * math.pi * eps_k
            per_channel_clean[k] = amps[k] * np.sin(2 * math.pi * f * t_grid + phases[k])
            per_channel_noisy[k] = a_eff * np.sin(2 * math.pi * f * t_grid + ph_eff)
        summed = per_channel_noisy.sum(axis=0)

        # v1.07c: chosen channel is locked to index 1 (sin2) to match the
        # deployed inference path which always sends C = [0, 1, 0, 0].
        # Quadruples the effective training signal for the actual task.
        chosen = 1
        c_vec = np.zeros(n_classes, dtype=np.float32)
        c_vec[chosen] = 1.0
        target = per_channel_clean[chosen].astype(np.float32)

        # No per-sample normalization: with fixed-signal identification mode, the
        # summation magnitude is naturally bounded (Σ|A_k| ≤ 140) and the target
        # mapping is deterministic in n_start. Per-sample scaling caused targets
        # to explode when the summation hit destructive-interference troughs.
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
        alpha_max=float(data_cfg.get("alpha_train_max", 0.3)),
        beta_max=float(data_cfg.get("beta_train_max", 0.3)),
        seed=int(data_cfg.get("seed", 42)),
    )
    return run_training(
        build_model=lambda: BookRNNRegressor(hidden_size=int(rnn_cfg["hidden_size"])),
        model_cfg=rnn_cfg, data_cfg=data_cfg, dataset=dataset, out_path=out_path, name="rnn",
    )
