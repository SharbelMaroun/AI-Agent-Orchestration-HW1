from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn

from fourier.shared.constants import WAVE_NAMES
from fourier.shared.types import ClassifierResult


class LSTMModel(nn.Module):
    def __init__(self, hidden_size: int = 128, num_layers: int = 2, dropout: float = 0.3) -> None:
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=1,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0.0,
            batch_first=True,
        )
        self.dropout = nn.Dropout(p=dropout)
        self.fc = nn.Linear(hidden_size, 4)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out, _ = self.lstm(x)
        last = self.dropout(out[:, -1, :])
        return torch.softmax(self.fc(last), dim=1)


class LSTMClassifier:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self._validate_config()
        self.model = LSTMModel(
            hidden_size=int(config["hidden_size"]),
            num_layers=int(config["num_layers"]),
            dropout=float(config["dropout"]),
        )
        self._load_weights()
        self.model.eval()

    def _validate_config(self) -> None:
        for key in ("hidden_size", "num_layers", "dropout", "weights_path"):
            if key not in self.config:
                raise KeyError(f"Missing required config key: {key}")

    def _load_weights(self) -> None:
        path = Path(self.config["weights_path"])
        if not path.exists():
            raise FileNotFoundError(f"Weights file not found: {path}")
        state = torch.load(path, weights_only=True)
        expected = set(self.model.state_dict().keys())
        missing = expected - set(state.keys())
        if missing:
            raise ValueError(f"Corrupted model weights — missing keys: {missing}")
        self.model.load_state_dict(state)

    def _build_result(self, probs_tensor: torch.Tensor) -> ClassifierResult:
        probs = probs_tensor.squeeze(0).tolist()
        predicted_class = int(np.argmax(probs))
        sorted_indices = sorted(range(len(probs)), key=lambda i: probs[i], reverse=True)
        return ClassifierResult(
            predicted_class=predicted_class,
            class_name=WAVE_NAMES[predicted_class],
            confidence=round(float(probs[predicted_class]), 6),
            probabilities=[round(float(p), 6) for p in probs],
            runner_up=sorted_indices[1],
        )

    def process(self, window: np.ndarray) -> ClassifierResult:
        x = torch.tensor(window, dtype=torch.float32)
        with torch.no_grad():
            probs = self.model(x)
        return self._build_result(probs)
