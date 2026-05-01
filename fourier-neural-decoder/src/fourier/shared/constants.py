import math

RESOLUTION = 500
DURATION = 10
PI2 = 2 * math.pi

WAVE_NAMES = [
    "Fundamental",
    "Second Harmonic",
    "Third Harmonic",
    "Fourth Harmonic",
]

COLORS = [
    "#38bdf8",
    "#f59e0b",
    "#22c55e",
    "#ef4444",
]

DEFAULTS = [
    {"amplitude": 50, "frequency": 0.5, "phase": 0.0, "sampling_rate": 20},
    {"amplitude": 30, "frequency": 1.0, "phase": math.pi / 2, "sampling_rate": 20},
    {"amplitude": 20, "frequency": 1.5, "phase": math.pi, "sampling_rate": 20},
    {"amplitude": 10, "frequency": 2.0, "phase": 3 * math.pi / 2, "sampling_rate": 20},
]
