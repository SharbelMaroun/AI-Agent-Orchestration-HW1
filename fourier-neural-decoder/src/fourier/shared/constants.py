import math

RESOLUTION = 500
DURATION = 10
PI2 = 2 * math.pi

WAVE_NAMES = [
    "sin1",
    "sin2",
    "sin3",
    "sin4",
]

COLORS = [
    "#38bdf8",
    "#f59e0b",
    "#22c55e",
    "#ef4444",
]

DEFAULTS = [
    {"amplitude": 50, "frequency": 0.5, "phase": 0.0, "sampling_rate": 20, "alpha": 0, "beta": 0},
    {"amplitude": 30, "frequency": 1.0, "phase": math.pi / 2, "sampling_rate": 20, "alpha": 0, "beta": 0},
    {"amplitude": 20, "frequency": 1.5, "phase": math.pi, "sampling_rate": 20, "alpha": 0, "beta": 0},
    {"amplitude": 10, "frequency": 2.0, "phase": 3 * math.pi / 2, "sampling_rate": 20, "alpha": 0, "beta": 0},
]

ALPHA_MAX_PCT = 100  # amplitude noise slider max (percent of A)
BETA_MAX_PCT = 100   # phase noise slider max (percent of π)

EXTRACT_POINTS = 10   # number of discrete sample points extracted per wave
ID_MODE_SR = 1000     # sampling rate (Hz) locked in identification mode

# Fixed signals used in Identification Mode
ID_MODE_SIGNALS = [
    {"frequency": 0.5, "amplitude": 60, "phase": 0.0},
    {"frequency": 1.0, "amplitude": 40, "phase": round(math.pi / 4, 2)},
    {"frequency": 1.5, "amplitude": 25, "phase": round(math.pi / 3, 2)},
    {"frequency": 2.0, "amplitude": 15, "phase": round(math.pi / 2, 2)},
]
