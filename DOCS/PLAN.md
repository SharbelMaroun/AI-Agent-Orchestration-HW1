# PLAN — Fourier Frequency App
**Version:** 1.00 | **Status:** Approved | **Owner:** sharbelm

---

## 1. C4 Model

### Level 1 — System Context

```
┌─────────────────────────────────────────────────────┐
│                    <<System>>                       │
│              Fourier Frequency App                  │
│                                                     │
│  Interactive browser-based tool for Fourier         │
│  synthesis and ML-powered signal identification.    │
└───────────────────────┬─────────────────────────────┘
                        │  HTTP (localhost:8050)
                        │
              ┌─────────▼─────────┐
              │      <<User>>     │
              │  Student /        │
              │  Educator /       │
              │  Self-learner     │
              └───────────────────┘

External Systems: None (fully self-contained; no external APIs in v1.00)
```

---

### Level 2 — Container

```
┌──────────────────────────────────────────────────────────────────┐
│                     Fourier Frequency App                        │
│                                                                  │
│  ┌─────────────────────┐      ┌────────────────────────────┐    │
│  │   Browser (Client)  │◄────►│  Dash / Flask Web Server   │    │
│  │                     │ HTTP │  [Python process]           │    │
│  │  Plotly charts      │      │  src/fourier/ui/           │    │
│  │  Clientside JS      │      │  layout.py                 │    │
│  │  C = channel vector │      │  callbacks_client.py       │    │
│  │                     │      │  callbacks_server.py       │    │
│  │                     │      │  callbacks_identify.py     │    │
│  └─────────────────────┘      │  callbacks_result.py       │    │
│                               └──────────┬─────────────────┘    │
│                                          │ Python calls          │
│                               ┌──────────▼─────────────────┐    │
│                               │       SDK Layer             │    │
│                               │  src/fourier/sdk/          │    │
│                               │  signal_generator.py       │    │
│                               │  window_extractor.py       │    │
│                               │  rnn_classifier.py         │    │
│                               │  lstm_classifier.py        │    │
│                               │  result_comparator.py      │    │
│                               └──────────┬─────────────────┘    │
│                                          │                       │
│                               ┌──────────▼─────────────────┐    │
│                               │      Gatekeeper             │    │
│                               │  src/fourier/gatekeeper.py │    │
│                               │  Rate limiting, retry,      │    │
│                               │  logging for ML inference   │    │
│                               └──────────┬─────────────────┘    │
│                                          │ loads                 │
│                               ┌──────────▼─────────────────┐    │
│                               │    Model Weight Files       │    │
│                               │  models/rnn_classifier.pt  │    │
│                               │  models/lstm_classifier.pt │    │
│                               └────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Config Store  (config/app_config.json,                  │    │
│  │                 config/rate_limits.json)                  │    │
│  └─────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

---

### Level 3 — Component (SDK Layer)

```
src/fourier/sdk/
│
├── signal_generator.py
│     __init__(config)          ← loads RESOLUTION, DURATION, DEFAULTS from config
│     process(channels)         ← returns {overlay_traces, sum_trace} for Plotly
│     _validate_config()        ← checks required keys exist
│
├── window_extractor.py
│     __init__(config)          ← loads RESOLUTION, DURATION from config
│     process(sum_trace, t_start, noise_sigma=0.0) ← returns normalized+noisy (50,) np.ndarray
│     _inject_noise(arr, sigma) ← adds N(0, sigma²) Gaussian noise when sigma > 0
│     _validate_config()        ← checks window bounds
│
├── rnn_classifier.py
│     __init__(config)          ← loads model weights from config["rnn_model_path"]
│     process(window)           ← returns {"class", "confidence", "probabilities"}
│     _validate_config()        ← checks file exists
│
├── lstm_classifier.py
│     __init__(config)          ← loads model weights from config["lstm_model_path"]
│     process(window)           ← returns {"class", "confidence", "probabilities"}
│     _validate_config()        ← checks file exists
│
└── result_comparator.py
      __init__()
      process(rnn_result, lstm_result) ← returns diff dict
      _validate_config()        ← no-op (stateless utility)
```

---

### Level 4 — Code (Key Classes)

#### `SignalGenerator`
```python
class SignalGenerator:
    def __init__(self, config: dict) -> None: ...
    def process(self, channels: list[ChannelConfig]) -> SignalResult: ...
    def _validate_config(self) -> None: ...

@dataclass
class ChannelConfig:
    enabled: bool
    frequency: float   # Hz
    amplitude: float
    phase: float       # radians
    mode: str          # "continuous" | "discrete"
    sampling_rate: float

@dataclass
class SignalResult:
    overlay_traces: list[dict]   # Plotly trace dicts
    sum_trace: dict              # Plotly trace dict
    sum_y: list[float]           # raw values for ML extraction
```

#### `RNNClassifier` / `LSTMClassifier`
```python
class RNNClassifier:
    def __init__(self, config: dict) -> None: ...
    def process(self, window: np.ndarray) -> ClassificationResult: ...
    def _validate_config(self) -> None: ...

@dataclass
class ClassificationResult:
    class_index: int
    channel_name: str
    confidence: float
    probabilities: list[float]   # length 4, sums to 1.0
```

#### `ResultComparator`
```python
class ResultComparator:
    def __init__(self) -> None: ...
    def process(
        self,
        rnn: ClassificationResult,
        lstm: ClassificationResult,
    ) -> ComparisonResult: ...
    def _validate_config(self) -> None: ...

@dataclass
class ComparisonResult:
    agreement: bool
    confidence_delta: float        # LSTM − RNN, percentage points
    top_class_rnn: float
    top_class_lstm: float
    runner_up_rnn: tuple[int, float]
    runner_up_lstm: tuple[int, float]
    disagreement_warning: bool
```

---

## 2. Architectural Decision Records (ADRs)

### ADR-01: Client-Side JavaScript for Real-Time Chart Updates

**Status:** Accepted

**Context:** Dash's standard server-side callbacks have ~100–300 ms round-trip latency per slider change. With 24 simultaneous slider inputs, this becomes perceptible.

**Decision:** Use Dash `clientside_callback` with inline JavaScript to compute and render both Plotly figures entirely in the browser, bypassing the network for every slider event.

**Consequences:**
- Chart updates render in < 50 ms. ✓
- Signal math is duplicated in Python (server) and JS (client). Must keep in sync.
- JS embedded in Python reduces testability. Mitigated by extracting JS to a separate `.js` asset file in `assets/`.

---

### ADR-02: Pre-Trained Model Weights (Offline Training)

**Status:** Accepted

**Context:** Training RNN/LSTM inside the Dash app on each startup would add 10–30 seconds latency before the app is usable.

**Decision:** Train models offline via `src/fourier/services/train_models.py` and commit the serialized weight files (`models/*.pt`) to the repository.

**Consequences:**
- App starts in < 3 seconds. ✓
- Model weights must be regenerated and recommitted if training data or architecture changes.
- Weight files are binary; diffs are not human-readable. Acceptable for this project scale.

---

### ADR-03: PyTorch as the ML Framework

**Status:** Accepted

**Context:** Both TensorFlow/Keras and PyTorch are viable. The project requires a CPU-only deployment with minimal dependency footprint.

**Decision:** Use PyTorch (`torch>=2.0.0`). Reasons: smaller install footprint than TensorFlow for CPU-only use, cleaner imperative API for simple RNN/LSTM implementations, and better Windows compatibility.

**Consequences:**
- Single additional dependency (`torch`). ✓
- Developers unfamiliar with PyTorch must learn its `nn.Module` API.

---

### ADR-04: `uv` as the Exclusive Package Manager

**Status:** Accepted (mandated by INSTRUCTIONS.md)

**Context:** Multiple Python package managers exist (`pip`, `conda`, `poetry`, `uv`).

**Decision:** Use `uv` exclusively. `pip` and `venv` are forbidden in this project.

**Consequences:**
- Faster installs and deterministic lock files via `uv.lock`. ✓
- CI/CD must have `uv` installed (not just `pip`).

---

### ADR-05: SDK-First Architecture

**Status:** Accepted (mandated by INSTRUCTIONS.md)

**Context:** Mixing business logic with UI callbacks makes unit testing difficult and violates separation of concerns.

**Decision:** All signal generation, ML inference, and comparison logic lives in `src/fourier/sdk/`. The UI (`src/fourier/ui/`) only calls SDK methods and maps results to Dash component props.

**Consequences:**
- SDK modules are fully unit-testable without a running Dash server. ✓
- UI callbacks are thin wrappers — easy to maintain and swap UI frameworks later.

---

### ADR-06: `ModelGatekeeper` for All ML Inference

**Status:** Accepted (mandated by INSTRUCTIONS.md)

**Context:** Without centralized control, ML inference calls have no rate limiting, retry logic, or audit trail.

**Decision:** All calls to `RNNClassifier.process()` and `LSTMClassifier.process()` are routed through `ModelGatekeeper`, which reads rate limits from `config/rate_limits.json`.

**Consequences:**
- Single point of control for ML call policy. ✓
- Slight overhead per call (negligible for CPU inference).

---

## 3. API Schemas

### 3.1 `SignalGenerator.process()` — Input / Output

**Input:** `list[ChannelConfig]` — 4 items (one per channel)

```json
[
  {
    "enabled": true,
    "frequency": 0.5,
    "amplitude": 50,
    "phase": 0.0,
    "mode": "continuous",
    "sampling_rate": 20
  }
]
```

**Output:** `SignalResult`

```json
{
  "overlay_traces": [
    {
      "x": [0.0, 0.02, "..."],
      "y": [0.0, 3.14, "..."],
      "name": "CH1 · Fundamental",
      "mode": "lines",
      "line": {"color": "#6366f1"}
    }
  ],
  "sum_trace": {
    "x": [0.0, 0.02, "..."],
    "y": [0.0, 5.27, "..."],
    "name": "Σ",
    "mode": "lines",
    "line": {"color": "#ffffff"}
  },
  "sum_y": [0.0, 5.27, "..."]
}
```

---

### 3.2 `WindowExtractor.process()` — Input / Output

**Input:**
```json
{
  "sum_y": [0.0, 5.27, "..."],
  "t_start": 2.4,
  "noise_sigma": 0.0
}
```

**Output:** `np.ndarray` of shape `(50,)`, dtype `float32`, values nominally in `[−1.0, 1.0]` (may exceed range when noise_sigma > 0)

---

### 3.3 `RNNClassifier.process()` / `LSTMClassifier.process()` — Input / Output

**Input:** `np.ndarray` shape `(50,)`, values `[−1.0, 1.0]`

**Output:** `ClassificationResult`

```json
{
  "class_index": 1,
  "channel_name": "Second Harmonic",
  "confidence": 0.873,
  "probabilities": [0.112, 0.873, 0.011, 0.004]
}
```

---

### 3.4 `ResultComparator.process()` — Input / Output

**Input:** Two `ClassificationResult` objects (RNN, LSTM)

**Output:** `ComparisonResult`

```json
{
  "agreement": true,
  "confidence_delta": 4.3,
  "top_class_rnn": 0.873,
  "top_class_lstm": 0.916,
  "runner_up_rnn": [0, 0.112],
  "runner_up_lstm": [0, 0.071],
  "disagreement_warning": false
}
```

---

### 3.5 `config/app_config.json` — Schema

```json
{
  "version": "1.00",
  "resolution": 500,
  "duration": 10,
  "debug": false,
  "host": "127.0.0.1",
  "port": 8050,
  "rnn_model_path": "models/rnn_classifier.pt",
  "lstm_model_path": "models/lstm_classifier.pt",
  "window_size_seconds": 1.0,
  "low_confidence_threshold": 0.40,
  "noise_default": 0.0,
  "noise_max": 0.5
}
```

---

### 3.6 `config/rate_limits.json` — Schema

```json
{
  "version": "1.00",
  "rnn_max_calls_per_minute": 60,
  "lstm_max_calls_per_minute": 30,
  "inference_timeout_seconds": 5,
  "max_retries": 2
}
```

---

## 4. Directory Blueprint (per INSTRUCTIONS.md)

```
fourier-freq-app/
├── src/fourier/
│   ├── sdk/
│   │   ├── signal_generator.py      (≤ 150 lines)
│   │   ├── window_extractor.py      (≤ 150 lines)
│   │   ├── rnn_classifier.py        (≤ 150 lines)
│   │   ├── lstm_classifier.py       (≤ 150 lines)
│   │   └── result_comparator.py     (≤ 150 lines)
│   ├── services/
│   │   └── train_models.py          (≤ 150 lines)
│   ├── ui/
│   │   ├── layout.py                (≤ 150 lines)
│   │   ├── callbacks_client.py      (≤ 150 lines)
│   │   ├── callbacks_server.py      (≤ 150 lines)
│   │   ├── callbacks_identify.py    (≤ 150 lines)
│   │   └── callbacks_result.py      (≤ 150 lines)
│   ├── shared/
│   │   ├── version.py               — VERSION = "1.01"
│   │   └── constants.py             — WAVE_NAMES, COLORS (loaded from config)
│   └── gatekeeper.py                (≤ 150 lines)
├── tests/
│   ├── test_signal_generator.py
│   ├── test_window_extractor.py
│   ├── test_rnn_classifier.py
│   ├── test_lstm_classifier.py
│   ├── test_result_comparator.py
│   └── test_gatekeeper.py
├── models/
│   ├── rnn_classifier.pt
│   └── lstm_classifier.pt
├── config/
│   ├── app_config.json
│   └── rate_limits.json
├── notebooks/
│   └── analysis.ipynb
├── docs/
│   ├── PRD.md
│   ├── PRD_RNN.md
│   ├── PRD_LSTM.md
│   ├── PLAN.md
│   ├── TODO.md
│   ├── PROMPT_LOG.md
│   ├── RNN.md
│   ├── LSTM.md
│   └── Project_Description.md
├── assets/
│   └── clientside.js                — extracted JS callback
├── .env-example
├── .gitignore                       — includes .env, models/*.pt (if large)
├── pyproject.toml                   — managed by uv; includes Ruff + pytest config
└── README.md
```
