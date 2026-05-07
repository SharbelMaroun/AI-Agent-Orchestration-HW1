from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn

from fourier.shared.constants import EXTRACT_POINTS
from fourier.shared.types import RegressorResult


class BookLSTMRegressor(nn.Module):
    """Vanilla LSTM regressor (book §6.1 form) that outputs the 10 reconstructed
    coordinates of the user-chosen wave.

    Per-step input is [sample_t, C₀, C₁, C₂, C₃]; concatenated input to the gates
    is z_t = [h_{t-1}, x_t]. All four gate matrices are kept as separate
    nn.Parameters; cell-state update uses addition (Eq. 4.3).

        f_t  = σ(W_f · z_t + b_f)
        i_t  = σ(W_i · z_t + b_i)
        C̃_t  = tanh(W_C · z_t + b_C)
        o_t  = σ(W_o · z_t + b_o)
        C_t  = f_t ⊙ C_{t-1} + i_t ⊙ C̃_t
        h_t  = o_t ⊙ tanh(C_t)
    Output:
        y = W_y · h_T + b_y    (no softmax — regression)
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
        z_size = self.hidden_size + self.input_size

        self.W_f = nn.Parameter(torch.empty(self.hidden_size, z_size))
        self.W_i = nn.Parameter(torch.empty(self.hidden_size, z_size))
        self.W_C = nn.Parameter(torch.empty(self.hidden_size, z_size))
        self.W_o = nn.Parameter(torch.empty(self.hidden_size, z_size))
        self.b_f = nn.Parameter(torch.ones(self.hidden_size))   # forget bias = 1
        self.b_i = nn.Parameter(torch.zeros(self.hidden_size))
        self.b_C = nn.Parameter(torch.zeros(self.hidden_size))
        self.b_o = nn.Parameter(torch.zeros(self.hidden_size))

        self.W_y = nn.Parameter(torch.empty(self.output_size, self.hidden_size))
        self.b_y = nn.Parameter(torch.zeros(self.output_size))

        self._init_weights()

    def _init_weights(self) -> None:
        bound = 1.0 / np.sqrt(self.hidden_size)
        for p in (self.W_f, self.W_i, self.W_C, self.W_o, self.W_y):
            nn.init.uniform_(p, -bound, bound)

    def forward(self, samples: torch.Tensor, c_vector: torch.Tensor) -> torch.Tensor:
        batch_size, seq_len, _ = samples.shape
        h = torch.zeros(batch_size, self.hidden_size, dtype=samples.dtype, device=samples.device)
        C = torch.zeros(batch_size, self.hidden_size, dtype=samples.dtype, device=samples.device)
        c_expanded = c_vector.unsqueeze(1).expand(batch_size, seq_len, self.c_size)
        x_full = torch.cat([samples, c_expanded], dim=2)
        for t in range(seq_len):
            z = torch.cat([h, x_full[:, t, :]], dim=1)
            f_t = torch.sigmoid(z @ self.W_f.T + self.b_f)
            i_t = torch.sigmoid(z @ self.W_i.T + self.b_i)
            C_tilde = torch.tanh(z @ self.W_C.T + self.b_C)
            o_t = torch.sigmoid(z @ self.W_o.T + self.b_o)
            C = f_t * C + i_t * C_tilde
            h = o_t * torch.tanh(C)
        return h @ self.W_y.T + self.b_y


class LSTMRegressor:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self._validate_config()
        self.model = BookLSTMRegressor(
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
            raise ValueError(f"Corrupted LSTM regressor weights — missing keys: {missing}")
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
