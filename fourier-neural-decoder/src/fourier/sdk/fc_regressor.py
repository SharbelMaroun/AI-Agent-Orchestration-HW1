from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn

from fourier.shared.constants import EXTRACT_POINTS
from fourier.shared.types import RegressorResult


class BookFCRegressor(nn.Module):
    """Two-layer fully-connected regressor — non-recurrent baseline.

    Flattens the length-10 window and concatenates the 4-d C one-hot, then:
        a_1 = ReLU(W_1 · [samples, C] + b_1)
        y   = W_2 · a_1 + b_2

    No time loop, no recurrence — sees the whole window at once as a flat vector.
    """

    def __init__(
        self,
        hidden_size: int,
        c_size: int = 4,
        seq_len: int = EXTRACT_POINTS,
        output_size: int = EXTRACT_POINTS,
    ) -> None:
        super().__init__()
        self.hidden_size = int(hidden_size)
        self.c_size = int(c_size)
        self.seq_len = int(seq_len)
        self.output_size = int(output_size)
        self.input_size = self.seq_len + self.c_size

        self.W_1 = nn.Parameter(torch.empty(self.hidden_size, self.input_size))
        self.b_1 = nn.Parameter(torch.zeros(self.hidden_size))
        self.W_2 = nn.Parameter(torch.empty(self.output_size, self.hidden_size))
        self.b_2 = nn.Parameter(torch.zeros(self.output_size))

        self._init_weights()

    def _init_weights(self) -> None:
        # Kaiming-style for ReLU.
        bound_1 = np.sqrt(2.0 / self.input_size)
        bound_2 = np.sqrt(2.0 / self.hidden_size)
        nn.init.uniform_(self.W_1, -bound_1, bound_1)
        nn.init.uniform_(self.W_2, -bound_2, bound_2)

    def forward(self, samples: torch.Tensor, c_vector: torch.Tensor) -> torch.Tensor:
        # samples: (B, T, 1) or (B, T)        c_vector: (B, c_size)
        flat = samples.reshape(samples.shape[0], -1)            # (B, T)
        x = torch.cat([flat, c_vector], dim=1)                   # (B, T + c_size)
        a_1 = torch.relu(x @ self.W_1.T + self.b_1)              # (B, H)
        return a_1 @ self.W_2.T + self.b_2                        # (B, output_size)


class FCRegressor:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self._validate_config()
        self.model = BookFCRegressor(
            hidden_size=int(config["hidden_size"]),
            c_size=int(config.get("c_size", 4)),
            seq_len=int(config.get("seq_len", EXTRACT_POINTS)),
            output_size=int(config.get("output_size", EXTRACT_POINTS)),
        )
        self._load_weights()
        self.model.eval()

    def _validate_config(self) -> None:
        if "hidden_size" not in self.config:
            raise KeyError("Missing required config key: hidden_size")
        if int(self.config["hidden_size"]) <= 0:
            raise ValueError("hidden_size must be > 0")

    def _load_weights(self) -> None:
        weights_path = self.config.get("weights_path")
        if not weights_path:
            return
        path = Path(weights_path)
        if not path.exists():
            return
        state = torch.load(path, weights_only=True, map_location="cpu")
        expected = set(self.model.state_dict().keys())
        missing = expected - set(state.keys())
        if missing:
            raise ValueError(f"Corrupted FC regressor weights — missing keys: {missing}")
        self.model.load_state_dict(state)

    def process(self, window: np.ndarray, c_vector: list[int]) -> RegressorResult:
        raw = np.asarray(window, dtype=np.float32).reshape(-1)
        scale = float(np.max(np.abs(raw))) or 1.0
        arr = (raw / scale).astype(np.float32).reshape(1, -1, 1)
        c = np.asarray(c_vector, dtype=np.float32).reshape(1, -1)
        with torch.no_grad():
            out = self.model(torch.from_numpy(arr), torch.from_numpy(c))
        coords = (out.squeeze(0).numpy() * scale).tolist()
        return RegressorResult(coordinates=[float(v) for v in coords], mae=0.0)
