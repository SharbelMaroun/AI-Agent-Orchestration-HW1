from __future__ import annotations

from typing import Any

from fourier.shared.constants import WAVE_NAMES
from fourier.shared.types import ClassifierResult, DiffResult


class ResultComparator:
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self._validate_config()

    def _validate_config(self) -> None:
        pass  # no required keys

    def _compute_agreement(self, rnn: ClassifierResult, lstm: ClassifierResult) -> bool:
        return rnn["predicted_class"] == lstm["predicted_class"]

    def _compute_confidence_delta(self, rnn: ClassifierResult, lstm: ClassifierResult) -> float:
        return round(abs(rnn["confidence"] - lstm["confidence"]), 4)

    def _compute_runner_up_diff(self, rnn: ClassifierResult, lstm: ClassifierResult) -> str:
        rnn_ru = WAVE_NAMES[rnn["runner_up"]]
        lstm_ru = WAVE_NAMES[lstm["runner_up"]]
        if rnn_ru == lstm_ru:
            return f"Both models have runner-up: {rnn_ru}"
        return f"RNN runner-up: {rnn_ru} | LSTM runner-up: {lstm_ru}"

    def process(self, rnn: ClassifierResult, lstm: ClassifierResult) -> DiffResult:
        return DiffResult(
            agreement=self._compute_agreement(rnn, lstm),
            rnn_predicted=rnn["class_name"],
            lstm_predicted=lstm["class_name"],
            confidence_delta=self._compute_confidence_delta(rnn, lstm),
            runner_up_diff=self._compute_runner_up_diff(rnn, lstm),
        )
