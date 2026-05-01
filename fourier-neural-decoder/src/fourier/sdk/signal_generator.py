from __future__ import annotations

from typing import Any

import numpy as np

from fourier.shared.constants import DURATION, PI2, RESOLUTION


class SignalGenerator:
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

    def _build_time_axis(self) -> np.ndarray:
        return np.linspace(0.0, float(DURATION), int(RESOLUTION) + 1, dtype=float)

    def _compute_continuous(self, t: np.ndarray) -> np.ndarray:
        amplitude = float(self.config["amplitude"])
        frequency = float(self.config["frequency"])
        phase = float(self.config["phase"])
        return amplitude * np.sin(float(PI2) * frequency * t + phase)

    def _build_discrete_times(self) -> np.ndarray:
        sampling_rate = float(self.config["sampling_rate"])
        n_samples = int(np.floor(float(DURATION) * sampling_rate)) + 1
        return np.arange(n_samples, dtype=float) / sampling_rate

    def _compute_discrete(self, t: np.ndarray) -> np.ndarray:
        amplitude = float(self.config["amplitude"])
        frequency = float(self.config["frequency"])
        phase = float(self.config["phase"])
        return amplitude * np.sin(float(PI2) * frequency * t + phase)

    def process(self) -> dict[str, Any]:
        t_cont = self._build_time_axis()
        y_cont = self._compute_continuous(t_cont)
        t_disc = self._build_discrete_times()
        y_disc = self._compute_discrete(t_disc)
        return {"continuous": y_cont, "discrete": {"t": t_disc, "y": y_disc}}
