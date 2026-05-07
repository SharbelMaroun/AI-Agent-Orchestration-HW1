# PLAN — Fourier Frequency App
**Version:** 1.07 | **Status:** Approved | **Owner:** sharbelm

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
│     __init__(config)            ← loads RESOLUTION, DURATION, DEFAULTS, alpha, beta
│     process()                   ← returns {continuous, discrete} with parametric noise
│     _perturbed_params()         ← draws ε~Uniform(-1,1); returns (A_eff, φ_eff)
│     _validate_config()          ← checks required keys + α,β ∈ [0,1]
│
├── window_extractor.py           (purely deterministic — no noise injection)
│     __init__(config)            ← loads RESOLUTION, DURATION from config
│     process(signal)             ← returns normalized (1, N, 1) np.float32 tensor
│     _slice_window(signal)       ← extracts window_points consecutive samples
│     _normalize(arr)             ← (arr − μ) / σ
│     _validate_config()          ← checks window bounds
│
└── window_extractor.py  (continued — see above)
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

### ADR-07: Manual ("Book-Faithful") RNN as a Regressor

**Status:** Accepted (v1.05)

**Context:** The Identification task is to recover the 10 coordinates of the user-chosen channel from a 10-sample summation window. The Fourier projection (ADR earlier) solves this deterministically; the lecturer additionally requires an RNN regressor that learns the same mapping. PyTorch's `nn.RNN` hides `W_x`, `W_h`, `b` and the time-step loop inside a fused kernel; the textbook (`concepts/RNN-BOOK.pdf`) presents the recurrence with these parameters explicit.

**Decision:** Implement `BookRNNRegressor(nn.Module)` with `W_x`, `W_h`, `b`, `W_y`, `b_y` as explicit `nn.Parameter`s and a Python `for t in range(seq_len)` loop. Per-step input is the concatenation `[sample_t, C_0..C_3]` so the network always knows which channel to extract. The output head is **linear, not softmax**, producing 10 real-valued coordinates. Loss is MSE on per-sample-amplitude-normalised data. `nn.RNN` is forbidden.

**Consequences:**
- Direct correspondence between book equations and source code. ✓
- Slower than `nn.RNN` on CPU; acceptable since `seq_len = 10`.
- Per-sample amplitude normalisation (divide by `max(|samples|)` at both training and inference) keeps the network's working range in `[−1, 1]` regardless of the user's amplitude choices.

---

### ADR-09: Manual ("Book-Faithful") LSTM as a Regressor

**Status:** Accepted (v1.05)

**Context:** Same regression task as ADR-07. The textbook (`concepts/LSTM-book.pdf`) §6.1 derives the four LSTM gates and cell-state update from first principles. `nn.LSTM` collapses the four gate weights into a single fused tensor and hides the loop.

**Decision:** Implement `BookLSTMRegressor(nn.Module)` with `W_f`, `W_i`, `W_C`, `W_o` and their biases as **separate** `nn.Parameter`s, time-step loop in Python, forget-bias init to 1.0, cell-state addition (Eq. 4.3), `h_t = o_t ⊙ tanh(C_t)`. Output head is linear → 10 coordinates. Same MSE loss and normalisation as the RNN regressor — they share `_generate_dataset` so any prediction difference is purely architectural. `nn.LSTM` is forbidden.

**Consequences:**
- Apples-to-apples comparison RNN vs. LSTM. ✓
- LSTM has ~4× the parameters of RNN (per book §5.4).
- Slower than `nn.LSTM`; acceptable for `seq_len = 10`.

---

### ADR-10: Both Networks Run Side-by-Side With the Fourier Baseline

**Status:** Accepted (v1.05)

**Context:** The user expects to see all three reconstructions of the chosen wave's 10 coordinates so the trained networks can be evaluated against the deterministic Fourier baseline.

**Decision:** The Identify callback runs the Fourier projection, RNN regressor, and LSTM regressor on the **same** 10-sample window and the **same** C one-hot. The result panel shows three columns — Fourier, RNN, LSTM — alongside `real`, plus a per-method MAE summary line. No code from the Fourier path was modified to add the regressors; the regressors are independent SDK classes loaded lazily as module-level singletons in `callbacks_identify.py`.

**Consequences:**
- One Identify click → three reconstructions, directly comparable. ✓
- The Fourier baseline serves as a "reference answer" that the trained networks aim to approach.

---

### ADR-11: FC (MLP) Regressor as a Non-Recurrent Baseline

**Status:** Accepted (v1.06)

**Context:** With RNN and LSTM regressors in place, a non-recurrent baseline lets us answer the empirical question "does recurrence actually help on a 10-sample window?". The FC sees the entire window as a flat vector and cannot use temporal order.

**Decision:** Add `BookFCRegressor(nn.Module)` as a fourth independent SDK class with `W_1`, `b_1`, `W_2`, `b_2` as explicit `nn.Parameter`s. Two-layer MLP: `ReLU(W_1·[samples, C] + b_1)` → linear output layer → 10-d coordinates. Same `_generate_dataset`, same MSE loss, same per-sample normalisation as the RNN/LSTM regressors. Wired into the Identify callback alongside the recurrent models.

**Consequences:**
- Direct comparison: same training data, same loss, same evaluation pipeline, only architecture differs. ✓
- The FC is permutation-invariant on the input — documented limitation that makes it the proper baseline.
- Empirically (default 4-channel summation) the FC reaches **summed MAE 43.76**, beating LSTM (47.81) and RNN (57.77). On this task and at this sequence length, recurrence does not earn its extra parameters.
- Inference cost: FC ≪ RNN < LSTM (no time loop in FC).

---

### ADR-007 (v1.07) — Parametric α/β Noise Model

**Status:** Accepted | **Date:** 2026-05-07

**Context:** The legacy noise model added Gaussian `N(0, σ²)` to the rendered output of each channel. This is *additive output noise*, which conflates "signal" and "measurement noise" and gives only one knob (σ).

**Decision:** Replace additive noise with a **parametric** model that perturbs a sine's amplitude and phase directly, with a single ε draw per channel per evaluation:

$$y_k(t) = (A_k + \alpha_k\!\cdot\!A_k\!\cdot\!\varepsilon)\,\sin\!\big(2\pi f_k t + \varphi_k + \beta_k\!\cdot\!\pi\!\cdot\!\varepsilon\big),\quad \varepsilon\sim\mathrm{Uniform}(-1,+1)$$

- **α** (amplitude noise, %) and **β** (phase noise, %) are independent per-channel sliders → 8 sliders total.
- ε is drawn **once per channel per evaluation** — the perturbation gives a single jittered sine, not a stochastic process.
- Symmetric jitter: at α = 100 %, A_eff ∈ [0, 2A]; at β = 100 %, φ shift ∈ [−π, +π].
- `WindowExtractor` no longer injects noise — it is a pure deterministic windowing function.

**Consequences:**
- The slider semantics now match physical intuition: α controls amplitude jitter, β controls phase jitter, both as percentages of the natural scale (A and π respectively).
- Training and inference must use the same noise model. `_generate_dataset` draws α, β, ε per channel per example; target = clean (un-perturbed) chosen channel — model learns to denoise.
- Removed `_noise_label` (Clean/Light/Medium/Heavy) — slider value already shows the percentage.

---

### ADR-009 (v1.07) — Gatekeeper as Local-Inference Wrapper

**Status:** Accepted | **Date:** 2026-05-07

**Context:** CLAUDE.md §5 mandates that "ALL external API requests MUST pass through a dedicated Gatekeeper class" handling rate limiting, retries, and logging. This app has **zero external API dependencies**: all inference is local PyTorch on CPU; the only "service calls" are `RNNRegressor.process()`, `LSTMRegressor.process()`, and `FCRegressor.process()` running in-process.

**Decision:** Keep the Gatekeeper, but scope it to **local-inference instrumentation** rather than network mediation:

- `src/fourier/gatekeeper.py` defines `Gatekeeper(config).process(name, fn, *args)` — wraps any callable with structured logging (call name, attempt #, duration, total call count) and a configurable retry policy.
- All three regressors are invoked through `_gatekeeper.process(...)` in `callbacks_identify._infer()`.
- No rate limiting is enforced (no shared bottleneck to protect); `max_retries` defaults to 1 to handle transient PyTorch glitches.

**Consequences:**
- The literal CLAUDE.md rule is satisfied — every model call passes through the Gatekeeper.
- The Gatekeeper provides a uniform extension point if external APIs are added later (e.g., uploading a window to a remote inference service).
- Logging is centralized: every inference call produces a structured DEBUG record without the regressors needing to log themselves.

---

### ADR-010 (v1.07) — Single-Threaded Execution

**Status:** Accepted | **Date:** 2026-05-07

**Context:** CLAUDE.md §10 expects an explicit parallelism strategy: multiprocessing for CPU-bound work, multithreading for I/O-bound work.

**Decision:** Run the entire app **single-threaded** in the Dash worker process.

**Rationale:**
- **Inference is sub-millisecond.** Each regressor processes a 10-sample window through a ~5–18 K parameter model. Wall-clock per call is < 1 ms; the three calls + Fourier projection complete in well under the 200 ms NFR-02 latency budget. Parallelizing across the three networks would add more thread-startup overhead than it saves.
- **Charts render client-side.** The 10 001-point Σ-chart in ID mode is built in JavaScript on the user's browser (`callbacks_client.py`). The Python server never touches per-frame data.
- **No I/O.** The app has no network calls, no file I/O during interaction, and no external APIs. There is nothing to overlap.
- **Training is offline.** `services/train_*` are run-once scripts; CPU-bound training is a single process by design (PyTorch handles intra-op parallelism via BLAS).

**Conditions under which this would change:**
1. Models grow to where single-call inference exceeds ~50 ms — then `multiprocessing.Pool` over the three regressors becomes worthwhile.
2. The app gains an external inference service (remote API) — then per-request `multithreading` for I/O overlap.
3. Dataset generation moves to live (per-Identify) instead of offline — `multiprocessing` over independent training examples.

Until any of those land, single-threaded is the simpler, faster, and easier-to-debug choice.

---

### ADR-008 (v1.07) — ID-Mode Sample Rate 1 kHz

**Status:** Accepted | **Date:** 2026-05-07

**Context:** Identification mode previously sampled at `ID_MODE_SR = 20 Hz` — Nyquist-compliant for the 0.5–2 Hz harmonics, but the 10-sample window covered 0.5 s, which is half a cycle of the slowest channel. The lecturer's reference design specifies 1000 samples/sec for dataset construction.

**Decision:** Bump ID-mode sample rate to `ID_MODE_SR = 1000 Hz`. Keep `EXTRACT_POINTS = 10`. Window now spans **0.01 s = 10 ms**.

- `window_duration` in `app_config.json` → `0.01`.
- Window slider: `step = 0.001 s` (one-sample resolution), `max = 9.99 s`.
- Highlight rectangle on the Σ-chart is `0.01 s` wide (visually a thin amber line — intentional).
- Σ-chart in ID mode renders 10 001 dots; marker size reduced to `1.5 px` for density.
- Training generator `_generate_dataset` draws `n_start ~ Uniform{0, …, 10 000−10}` per example so the model sees windows from anywhere in the 10 s range.

**Consequences:**
- Per-window MAE rose vs. 20 Hz (≈ 1.2 vs ≈ 0.3 in raw amplitude units, ~2–3 % of typical channel amplitude). Inherent to the spec — a 10 ms window covers only 1/200 of a 0.5 Hz cycle, so the network sees near-flat slices.
- Inference rendering remains responsive (Plotly handles 10 K dots fine on modern browsers).
- One-sample slider precision lets the user examine arbitrary 10-sample positions, not just multiples of 0.1 s.

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
