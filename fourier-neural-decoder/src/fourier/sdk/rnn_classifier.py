from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn

from fourier.shared.constants import WAVE_NAMES
from fourier.shared.types import ClassifierResult


class RNNModel(nn.Module):
    def __init__(self, hidden_size: int = 64, num_layers: int = 1) -> None:
        super().__init__()
        self.rnn = nn.RNN(
            input_size=1,
            hidden_size=hidden_size,
            num_layers=num_layers,
            nonlinearity="tanh",
            batch_first=True,
        )
        self.fc = nn.Linear(hidden_size, 4)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        _, h_n = self.rnn(x)
        out = self.fc(h_n[-1])
        return torch.softmax(out, dim=1)


class RNNClassifier:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self._validate_config()
        self.model = RNNModel(
            hidden_size=int(config["hidden_size"]),
            num_layers=int(config["num_layers"]),
        )
        self._load_weights()
        self.model.eval()

    def _validate_config(self) -> None:
        for key in ("hidden_size", "num_layers", "weights_path"):
            if key not in self.config:
                raise KeyError(f"Missing required config key: {key}")

    def _load_weights(self) -> None:
        path = Path(self.config["weights_path"])
        if not path.exists():
            raise FileNotFoundError(f"Weights file not found: {path}")
        state = torch.load(path, weights_only=True)
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
