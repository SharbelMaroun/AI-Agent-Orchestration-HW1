# Fourier Neural Decoder

**Version 1.07** — Interactive Fourier synthesis and ML-powered signal regression.

Build composite waveforms from up to 4 harmonic channels, then use trained **RNN, LSTM, and FC** regressors to recover the 10 coordinates of any chosen channel from a 10-sample (10 ms) window of the noisy summation. Identification mode samples at **1000 Hz**; per-channel **α (amplitude) and β (phase)** sliders inject parametric noise.

---

## 1. Project Identity

| | |
|---|---|
| **Version** | 1.07 |
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
uv run python -c "
from pathlib import Path
from fourier.shared.config_loader import load_training_config
from fourier.services.train_rnn import train_rnn
from fourier.services.train_lstm import train_lstm
from fourier.services.train_fc import train_fc
cfg = load_training_config(); data_cfg = cfg['data']
for name, fn, key in [('rnn', train_rnn, 'rnn'), ('lstm', train_lstm, 'lstm'), ('fc', train_fc, 'fc')]:
    print(name, fn(cfg[key], data_cfg, Path(cfg[key]['weights_path'])))
"
```

Launch the app:

```bash
uv run python -m fourier
```

Open http://127.0.0.1:8050 in your browser.

---

## 4. Configuration

All runtime settings live in versioned JSON files — nothing is hardcoded in source.

### `config/app_config.json`

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `version` | string | `"1.07"` | App version |
| `resolution` | int | `500` | Points on the continuous overlay time axis |
| `duration` | int | `10` | Signal duration in seconds |
| `debug` | bool | `false` | Dash debug mode |
| `host` | string | `"127.0.0.1"` | Server bind address |
| `port` | int | `8050` | Server port |
| `window_duration` | float | `0.01` | Analysis window length in seconds (10 samples / 1000 Hz) |
| `window_points` | int | `10` | Samples in the analysis window |
| `alpha_default` / `alpha_max` | int | `0` / `100` | Per-channel amplitude-noise slider default / max (percent of A) |
| `beta_default` / `beta_max` | int | `0` / `100` | Per-channel phase-noise slider default / max (percent of π) |

Model weights are auto-discovered at `weights/{rnn,lstm,fc}_regressor.pt` via `config/training_config.json`.

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

## 6. Usage: ML Identification (Regression)

### Identification Mode

Click **Enter Identification Mode** to lock all 4 channels to fixed reference signals (frequencies 0.5, 1.0, 1.5, 2.0 Hz) and force the Σ-chart to render at 1000 Hz (10 001 dots over 10 s). The Wave-to-Extract is locked to channel 1 (1.0 Hz) → C = [0, 1, 0, 0].

### Selecting the Analysis Window

The **Window** slider (0.000 – 9.990 s, step 0.001 s) selects 10 consecutive samples (10 ms) of the noisy summation. The amber rectangle on the Σ-chart shows the picked window — at this scale it appears as a thin vertical line.

### Parametric α/β Noise

Each of the 4 channels has **two noise sliders** (8 total):

- **α — Amplitude noise (%)** — slider 0–100; perturbs A.
- **β — Phase noise (%)** — slider 0–100; perturbs φ.

The signal generated for channel *k* is:

```
y_k(t) = (A + α·A·ε) · sin(2π·f·t + φ + β·π·ε),    ε ~ Uniform(-1, +1)
```

A single ε is drawn per channel per evaluation (parametric jitter, not per-sample additive noise). At α = 100 %, the effective amplitude swings symmetrically in [0, 2A]; at β = 100 %, the phase shifts symmetrically in [−π, +π].

### Running Inference

Click **Identify**. All three regressors (RNN, LSTM, FC) plus a closed-form Fourier least-squares baseline run on the same 10-sample window and the same C one-hot vector. The result panel shows the four reconstructions side-by-side against the ground-truth pure-channel coordinates, plus per-method MAE.

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
│   │   ├── signal_generator.py      # Sine generation with parametric α/β noise
│   │   ├── window_extractor.py      # Pure deterministic slice + normalise (no noise)
│   │   ├── rnn_regressor.py         # Book-faithful Elman RNN regressor
│   │   ├── lstm_regressor.py        # Book-faithful LSTM regressor
│   │   └── fc_regressor.py          # 2-layer MLP baseline
│   ├── services/
│   │   ├── train_rnn.py             # Training pipeline + shared _generate_dataset
│   │   ├── train_lstm.py            # Reuses _generate_dataset
│   │   └── train_fc.py              # Reuses _generate_dataset
│   ├── ui/
│   │   ├── layout.py                # Dash component tree
│   │   ├── callbacks_client.py      # Client-side JS chart callback (parametric noise in JS)
│   │   ├── callbacks_server.py      # Toggle / reset / value-display callbacks
│   │   ├── callbacks_identify.py    # Identify callback (Fourier + 3 NN regressors)
│   │   └── callbacks_result.py      # Result panel rendering helpers
│   ├── shared/
│   │   ├── version.py               # VERSION = "1.07"
│   │   ├── constants.py             # WAVE_NAMES, COLORS, DEFAULTS, ID_MODE_SR=1000, EXTRACT_POINTS=10
│   │   ├── types.py                 # TypedDicts
│   │   └── config_loader.py         # load_app_config(), load_training_config()
│   └── __main__.py                  # Entry point
├── tests/
│   ├── unit/                        # Per-module unit tests
│   └── integration/                 # End-to-end flow tests
├── weights/
│   ├── rnn_regressor.pt
│   ├── lstm_regressor.pt
│   └── fc_regressor.pt
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
