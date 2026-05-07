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


class RegressorResult(TypedDict):
    coordinates: list[float]   # 10 reconstructed values
    mae: float                 # mean abs error vs. ground truth (filled in by caller)
