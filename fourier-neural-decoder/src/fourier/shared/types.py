from typing import TypedDict


class ChannelConfig(TypedDict):
    amplitude: float
    frequency: float
    phase: float
    sampling_rate: float
    enabled: bool


class WindowSlice(TypedDict):
    window_start: float
    duration: float
    signal_values: list[float]


class ClassifierResult(TypedDict):
    predicted_class: int
    class_name: str
    confidence: float
    probabilities: list[float]
    runner_up: int


class DiffResult(TypedDict):
    agreement: bool
    rnn_predicted: str
    lstm_predicted: str
    confidence_delta: float
    runner_up_diff: str
