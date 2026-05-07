from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn

from fourier.shared.constants import EXTRACT_POINTS
from fourier.shared.types import RegressorResult


class BookRNNRegressor(nn.Module):
    """Vanilla Elman RNN regressor that outputs the 10 reconstructed coordinates
    of the user-chosen wave.

    Per-step input is the concatenation [sample_t, C₀, C₁, C₂, C₃] — the C one-hot
    is repeated at every time step so the network sees, at every step, both the
    summation sample value and which channel it has been asked to extract.

    Recurrence (book Eq. 2.13–2.14):
        z_t = W_x · x_t + W_h · h_{t-1} + b
        h_t = tanh(z_t)
    Output:
        y = W_y · h_T + b_y    ∈ ℝ^{output_size}    (no softmax — regression)
    """

    def __init__(
        self,
        hidden_size: int,
        c_size: int = 4,
        output_size: int = EXTRACT_POINTS,
    ) -> None:
        super().__init__()
        self.hidden_size = int(hidden_size)
        self.c_size = int(c_size)
        self.output_size = int(output_size)
        self.input_size = 1 + self.c_size

        self.W_x = nn.Parameter(torch.empty(self.hidden_size, self.input_size))
        self.W_h = nn.Parameter(torch.empty(self.hidden_size, self.hidden_size))
        self.b = nn.Parameter(torch.zeros(self.hidden_size))

        self.W_y = nn.Parameter(torch.empty(self.output_size, self.hidden_size))
        self.b_y = nn.Parameter(torch.zeros(self.output_size))

        self._init_weights()

    def _init_weights(self) -> None:
        bound = 1.0 / np.sqrt(self.hidden_size)
        nn.init.uniform_(self.W_x, -bound, bound)
        nn.init.uniform_(self.W_h, -bound, bound)
        nn.init.uniform_(self.W_y, -bound, bound)

    def forward(self, samples: torch.Tensor, c_vector: torch.Tensor) -> torch.Tensor:
        # samples: (B, T, 1)        c_vector: (B, c_size)
        batch_size, seq_len, _ = samples.shape
        h = torch.zeros(batch_size, self.hidden_size, dtype=samples.dtype, device=samples.device)
        c_expanded = c_vector.unsqueeze(1).expand(batch_size, seq_len, self.c_size)
        x_full = torch.cat([samples, c_expanded], dim=2)            # (B, T, 1 + c_size)
        for t in range(seq_len):
            x_t = x_full[:, t, :]
            z_t = x_t @ self.W_x.T + h @ self.W_h.T + self.b
            h = torch.tanh(z_t)
        return h @ self.W_y.T + self.b_y                            # (B, output_size)


class RNNRegressor:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self._validate_config()
        self.model = BookRNNRegressor(
            hidden_size=int(config["hidden_size"]),
            c_size=int(config.get("c_size", 4)),
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
            raise ValueError(f"Corrupted RNN regressor weights — missing keys: {missing}")
        self.model.load_state_dict(state)

    def process(self, window: np.ndarray, c_vector: list[int]) -> RegressorResult:
        raw = np.asarray(window, dtype=np.float32).reshape(-1)
        scale = float(np.max(np.abs(raw))) or 1.0          # match training normalization
        arr = (raw / scale).astype(np.float32).reshape(1, -1, 1)
        c = np.asarray(c_vector, dtype=np.float32).reshape(1, -1)
        with torch.no_grad():
            out = self.model(torch.from_numpy(arr), torch.from_numpy(c))
        coords = (out.squeeze(0).numpy() * scale).tolist()
        return RegressorResult(coordinates=[float(v) for v in coords], mae=0.0)
