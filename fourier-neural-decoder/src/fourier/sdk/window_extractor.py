from __future__ import annotations

from typing import Any

import numpy as np

from fourier.shared.constants import DURATION, RESOLUTION


class WindowExtractor:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self._validate_config()

    def _validate_config(self, noise_sigma: float = 0.0) -> None:
        if "window_start" not in self.config:
            raise KeyError("Missing required config key: window_start")

        window_start = float(self.config["window_start"])
        max_start = float(self.config.get("max_window_start", 9.0))
        if window_start < 0:
            raise ValueError("window_start must be >= 0")
        if window_start > max_start:
            raise ValueError(f"window_start must be <= {max_start}")

        if noise_sigma < 0:
            raise ValueError("noise_sigma must be >= 0")
        if noise_sigma > 0.5:
            raise ValueError("noise_sigma must be <= 0.5")

    def _slice_window(self, signal: np.ndarray) -> np.ndarray:
        signal_arr = np.asarray(signal, dtype=float)
        window_points = int(self.config.get("window_points", 50))
        window_start = float(self.config["window_start"])
        points_per_second = float(RESOLUTION) / float(DURATION)

        start_index = int(round(window_start * points_per_second))
        max_start_index = len(signal_arr) - window_points
        if window_start == float(self.config.get("max_window_start", 9.0)):
            start_index = max_start_index
        else:
            start_index = max(0, min(start_index, max_start_index))

        return signal_arr[start_index : start_index + window_points]

    def _normalize(self, arr: np.ndarray) -> np.ndarray:
        mean = float(np.mean(arr))
        std = float(np.std(arr))
        if std == 0:
            return np.zeros_like(arr, dtype=float)
        return (arr - mean) / std

    def _reshape(self, arr: np.ndarray) -> np.ndarray:
        return arr.astype(np.float32).reshape(1, 50, 1)

    def _inject_noise(self, arr: np.ndarray, sigma: float) -> np.ndarray:
        if sigma <= 0:
            return arr
        noise = np.random.normal(loc=0.0, scale=sigma, size=arr.shape)
        return arr + noise

    def process(self, signal: np.ndarray, noise_sigma: float = 0.0) -> np.ndarray:
        self._validate_config(noise_sigma=noise_sigma)
        sliced = self._slice_window(signal)
        normalized = self._normalize(sliced)
        noisy = self._inject_noise(normalized, noise_sigma)
        return self._reshape(noisy)
