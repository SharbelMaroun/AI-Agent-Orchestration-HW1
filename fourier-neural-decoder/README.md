# Fourier Neural Decoder

**Version 1.01** — Interactive Fourier synthesis and ML-powered signal identification.

Build composite waveforms from up to 4 harmonic channels, then use trained RNN or LSTM classifiers to identify the dominant frequency class from any 1-second window of the signal.

---

## 1. Project Identity

| | |
|---|---|
| **Version** | 1.01 |
| **App title** | Fourier Synthesis |
| **Entry point** | `uv run fourier-app` |
| **Default URL** | http://127.0.0.1:8050 |

---

## 2. Tech Stack

| Layer | Technology |
|-------|-----------|
| UI framework | [Dash](https://dash.plotly.com/) |
| Charts | [Plotly](https://plotly.com/python/) |
| ML models | [PyTorch](https://pytorch.org/) |
| Signal math | [NumPy](https://numpy.org/) |
| Package manager | [uv](https://docs.astral.sh/uv/) |
| Linter | [Ruff](https://docs.astral.sh/ruff/) |
| Testing | [pytest](https://pytest.org/) + pytest-cov |

---

## 3. Installation

> `pip` and `venv` are **forbidden**. Use `uv` exclusively.

```bash
git clone <repo-url>
cd fourier-neural-decoder
uv sync
cp .env-example .env
```

Train model weights (required before first run):

```bash
uv run python -m fourier.services.train_models
```

Launch the app:

```bash
uv run fourier-app
```

Open http://127.0.0.1:8050 in your browser.

---

## 4. Configuration

All runtime settings live in versioned JSON files — nothing is hardcoded in source.

### `config/app_config.json`

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `version` | string | `"1.01"` | App version |
| `resolution` | int | `500` | Points on the continuous time axis |
| `duration` | int | `10` | Signal duration in seconds |
| `debug` | bool | `false` | Dash debug mode |
| `host` | string | `"127.0.0.1"` | Server bind address |
| `port` | int | `8050` | Server port |
| `window_duration` | float | `1.0` | ML analysis window length (seconds) |
| `window_points` | int | `50` | Samples in the analysis window |
| `noise_default` | float | `0.0` | Default noise σ for the slider |
| `noise_max` | float | `0.5` | Maximum allowed noise σ |
| `rnn_model_path` | string | `"models/rnn_classifier.pt"` | Path to RNN weights |
| `lstm_model_path` | string | `"models/lstm_classifier.pt"` | Path to LSTM weights |

### `config/rate_limits.json`

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `max_calls_per_minute` | int | `60` | Max ML inference calls per 60 s window |
| `max_retries` | int | `3` | Retry attempts on `RuntimeError` |
| `retry_delay_seconds` | float | `0.5` | Delay between retries |
| `timeout_seconds` | int | `10` | Per-call timeout |

---

## 5. Usage: Signal Synthesis

### Enabling / Disabling Channels

Each of the 4 harmonic channels (Fundamental, Second, Third, Fourth Harmonic) has an **enable checkbox** at the top of its panel. Unchecking hides all sliders and removes that channel from the overlay and summation charts.

### Adjusting Sliders

| Slider | Range | Effect |
|--------|-------|--------|
| **Frequency** | 0.1 – 5.0 Hz | Sets the oscillation rate of the channel |
| **Amplitude** | 0 – 100 | Sets the peak signal value |
| **Phase** | 0.0 – 6.28 rad | Shifts the waveform left/right in time |
| **Sampling Rate** | 1 – 50 Hz | Controls discrete sample density (dots mode only) |

Charts update in real time (< 50 ms) via client-side JavaScript — no server round-trip.

### Discrete Sampling Mode

Check the **Dots** checkbox on a channel to switch from a continuous line to discrete sample markers. The sampling rate slider (`sr`) becomes visible, controlling how many samples per second are shown. Nyquist aliasing artifacts appear when the sampling rate is less than twice the signal frequency.

### Reading the `y[n]` Vector

When dots mode is active, a monospace box below the channel panel shows the numeric values `y[0], y[1], …` — the discrete signal samples. Hover any value to see its index `n` and time `t` in seconds.

---

## 6. Usage: ML Identification

### Selecting the Analysis Window

The **Window** slider (0.0 – 9.0 s) on the summation chart selects the 1-second segment to analyse. The selected window is highlighted with an amber vertical band on the summation chart.

### Choosing the Algorithm

The **Algorithm** radio selector offers three modes:

| Mode | Behaviour |
|------|-----------|
| **RNN** | Runs the single-layer RNN classifier only |
| **LSTM** | Runs the 2-layer LSTM classifier only |
| **Both** | Runs both classifiers and shows a side-by-side diff |

### Noise Injection

The **Noise** slider (0.0 – 0.5) adds Gaussian noise `N(0, σ²)` to the normalised window *before* inference. A label shows the noise level: **Clean** (σ=0), **Light** (σ≤0.15), **Medium** (σ≤0.30), **Heavy** (σ>0.30). Use this to test model robustness.

Click **Identify** to run inference.

### Reading the Single-Algorithm Results Panel

The result panel shows:
- **Predicted class** name and confidence percentage
- **4 probability bars** — one per harmonic class, scaled proportionally

### Reading the Both-Mode Diff Summary

When **Both** is selected, two result panels appear side by side (RNN left, LSTM right), followed by a **Diff Summary** panel showing:
- **Agreement** — green YES / red NO badge
- **Confidence delta** — `|conf_RNN − conf_LSTM|` to 4 decimal places
- **Runner-up diff** — description of the second-highest class from each model

---

## 7. Documentation Map

| File | Purpose |
|------|---------|
| `DOCS/PRD.md` | Product Requirements — user problems, KPIs, functional/non-functional requirements |
| `DOCS/PLAN.md` | Architecture — C4 diagrams, ADRs, API schemas, directory blueprint |
| `DOCS/TODO.md` | Task list — all 507 tasks with Definition of Done per phase |
| `DOCS/PRD_RNN.md` | Feature PRD for the RNN classifier |
| `DOCS/PRD_LSTM.md` | Feature PRD for the LSTM classifier |
| `DOCS/RNN.md` | RNN architecture reference |
| `DOCS/LSTM.md` | LSTM architecture reference |
| `DOCS/Prompt_Log.md` | Book of Prompts — every major AI-generated component logged |
| `DOCS/Project_Description.md` | Original project brief |
| `notebooks/analysis.ipynb` | Research notebook — math proofs, sensitivity analysis, cost table |

---

## 8. Directory Blueprint

```
fourier-neural-decoder/
├── src/fourier/
│   ├── sdk/
│   │   ├── signal_generator.py      # Continuous + discrete signal synthesis
│   │   ├── window_extractor.py      # Slice, normalise, inject noise
│   │   ├── rnn_classifier.py        # RNN model + inference
│   │   ├── lstm_classifier.py       # LSTM model + inference
│   │   └── result_comparator.py     # Compare RNN vs LSTM outputs
│   ├── services/
│   │   └── train_models.py          # Offline training script
│   ├── ui/
│   │   ├── layout.py                # Dash component tree
│   │   ├── callbacks_client.py      # Client-side JS chart callback
│   │   ├── callbacks_server.py      # Server callbacks (toggle, reset, noise label)
│   │   ├── callbacks_identify.py    # Identify callback + pure logic
│   │   └── callbacks_result.py      # Result panel rendering helpers
│   ├── shared/
│   │   ├── version.py               # VERSION = "1.01"
│   │   ├── constants.py             # WAVE_NAMES, COLORS, DEFAULTS, PI2
│   │   ├── types.py                 # TypedDicts: ChannelConfig, ClassifierResult, DiffResult
│   │   └── config_loader.py         # load_app_config(), load_rate_limits()
│   ├── gatekeeper.py                # Rate limiting + retry for all ML calls
│   ├── app.py                       # create_app() factory
│   └── __main__.py                  # Entry point
├── tests/
│   ├── unit/                        # Per-module unit tests
│   └── integration/                 # End-to-end flow tests
├── models/
│   ├── rnn_classifier.pt
│   └── lstm_classifier.pt
├── config/
│   ├── app_config.json
│   ├── rate_limits.json
│   └── training_config.json
├── notebooks/
│   └── analysis.ipynb
├── DOCS/                            # All pre-development documentation
├── .env-example
├── pyproject.toml
└── README.md
```

---

## 9. Contributing

- **Package manager:** `uv` only — never `pip install` or `python -m venv`
- **Linting:** `uv run ruff check src/` must exit 0 before any commit
- **Tests:** `uv run pytest --cov=src --cov-fail-under=85` must pass
- **150-line rule:** No source file may exceed 150 lines — split into auxiliary modules if needed
- **No hardcoding:** All limits, paths, and config values must live in `config/*.json`
- **Building Block Pattern:** Every core class needs `__init__`, `process()`, and `_validate_config()`
