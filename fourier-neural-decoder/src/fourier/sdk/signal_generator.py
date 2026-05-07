from __future__ import annotations

import math
from typing import Any

import numpy as np

from fourier.shared.constants import DURATION, PI2, RESOLUTION


class SignalGenerator:
    """Sine generator with parametric noise.

    y(t) = (A + α·A·ε)·sin(2π·f·t + φ + β·π·ε), ε ~ Uniform(-1, 1).
    α and β are slider fractions in [0, 1] (i.e. percent / 100). One ε per
    evaluation per channel — the perturbation defines a single jittered sine,
    not per-sample noise.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self._validate_config()

    def _validate_config(self) -> None:
        required_keys = ("frequency", "amplitude", "phase", "sampling_rate")
        missing_keys = [key for key in required_keys if key not in self.config]
        if missing_keys:
            raise KeyError(f"Missing required config keys: {', '.join(missing_keys)}")
        if float(self.config["amplitude"]) < 0:
            raise ValueError("amplitude must be >= 0")
        if float(self.config["frequency"]) <= 0:
            raise ValueError("frequency must be > 0")
        if float(self.config["sampling_rate"]) < 1:
            raise ValueError("sampling_rate must be >= 1")
        for key in ("alpha", "beta"):
            if key in self.config:
                v = float(self.config[key])
                if v < 0 or v > 1:
                    raise ValueError(f"{key} must be in [0, 1]")

    def _build_time_axis(self) -> np.ndarray:
        return np.linspace(0.0, float(DURATION), int(RESOLUTION) + 1, dtype=float)

    def _build_discrete_times(self) -> np.ndarray:
        sampling_rate = float(self.config["sampling_rate"])
        n_samples = int(np.floor(float(DURATION) * sampling_rate)) + 1
        return np.arange(n_samples, dtype=float) / sampling_rate

    def _evaluate(self, t: np.ndarray) -> np.ndarray:
        """y(t_k) = (A + α·A·ε_k)·sin(2πf t_k + φ + β·π·ε_k), ε_k ~ U(-1,+1) per sample."""
        a = float(self.config["amplitude"])
        ph = float(self.config["phase"])
        f = float(self.config["frequency"])
        alpha = float(self.config.get("alpha", 0.0))
        beta = float(self.config.get("beta", 0.0))
        if alpha == 0.0 and beta == 0.0:
            return a * np.sin(float(PI2) * f * t + ph)
        rng = self.config.get("rng")
        draw = (rng.uniform if rng is not None else np.random.uniform)
        eps = draw(-1.0, 1.0, size=t.shape)
        return (a + alpha * a * eps) * np.sin(float(PI2) * f * t + ph + beta * math.pi * eps)

    def _compute_continuous(self, t: np.ndarray) -> np.ndarray:
        return self._evaluate(t)

    def _compute_discrete(self, t: np.ndarray) -> np.ndarray:
        return self._evaluate(t)

    def process(self) -> dict[str, Any]:
        t_cont = self._build_time_axis()
        t_disc = self._build_discrete_times()
        return {
            "continuous": self._evaluate(t_cont),
            "discrete": {"t": t_disc, "y": self._evaluate(t_disc)},
        }
