from __future__ import annotations

from typing import Any

import numpy as np

from fourier.shared.constants import DURATION, RESOLUTION

_DEFAULT_WINDOW_POINTS = 50
_DEFAULT_MAX_WINDOW_START = float(DURATION) - 1.0


class WindowExtractor:
    """Slice / normalize / reshape the analysis window — no noise injection.

    Noise lives upstream in SignalGenerator (parametric α/β model). This class
    is purely a deterministic windowing function.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self._validate_config()

    def _validate_config(self) -> None:
        if "window_start" not in self.config:
            raise KeyError("Missing required config key: window_start")
        window_start = float(self.config["window_start"])
        max_start = float(self.config.get("max_window_start", _DEFAULT_MAX_WINDOW_START))
        if window_start < 0:
            raise ValueError("window_start must be >= 0")
        if window_start > max_start:
            raise ValueError(f"window_start must be <= {max_start}")

    def _window_points(self) -> int:
        return int(self.config.get("window_points", _DEFAULT_WINDOW_POINTS))

    def _slice_window(self, signal: np.ndarray) -> np.ndarray:
        signal_arr = np.asarray(signal, dtype=float)
        window_pts = self._window_points()
        window_start = float(self.config["window_start"])
        max_start = float(self.config.get("max_window_start", _DEFAULT_MAX_WINDOW_START))
        points_per_second = float(RESOLUTION) / float(DURATION)
        start_index = int(round(window_start * points_per_second))
        max_start_index = len(signal_arr) - window_pts
        if window_start == max_start:
            start_index = max_start_index
        else:
            start_index = max(0, min(start_index, max_start_index))
        return signal_arr[start_index : start_index + window_pts]

    def _normalize(self, arr: np.ndarray) -> np.ndarray:
        mean = float(np.mean(arr))
        std = float(np.std(arr))
        if std == 0:
            return np.zeros_like(arr, dtype=float)
        return (arr - mean) / std

    def _reshape(self, arr: np.ndarray) -> np.ndarray:
        pts = self._window_points()
        return arr.astype(np.float32).reshape(1, pts, 1)

    def process(self, signal: np.ndarray) -> np.ndarray:
        return self._reshape(self._normalize(self._slice_window(signal)))
