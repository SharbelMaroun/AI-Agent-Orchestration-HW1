# Neural Signal Decoder
**Version:** 1.00 | Fourier Frequency App with ML-Powered Signal Identification

A professional-grade, browser-based tool for Fourier synthesis and deep learning signal decomposition. Compose complex waveforms from up to four harmonic components, select any 1-second window from the composite signal, and let an RNN or LSTM classifier identify the dominant sinusoidal component — all without writing a single line of code.

---

## Table of Contents

1. [Technical Stack](#technical-stack)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage Guide](#usage-guide)
5. [Documentation Map](#documentation-map)
6. [Project Directory](#project-directory)
7. [Contributing](#contributing)

---

## Technical Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Package Manager | `uv` (pip is forbidden) | latest |
| Web Framework | Dash (Flask-based) | ≥ 2.17.0 |
| Visualization | Plotly | ≥ 5.20.0 |
| Numerical Computing | NumPy | ≥ 1.24.0 |
| ML Framework | PyTorch (CPU) | ≥ 2.0.0 |
| Linting | Ruff | zero violations required |
| Testing | pytest + pytest-cov | ≥ 85% coverage required |

> **Architecture:** SDK-First design with the 150-Line Rule. All business logic lives in `src/fourier/sdk/`. The UI is a thin consumer of the SDK. See `docs/PLAN.md` for the full C4 architecture.

---

## Installation

### Prerequisites

Install the `uv` package manager. **Do not use `pip` or `venv` — they are forbidden in this project.**

```powershell
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd AI-Agent-Orchestration-HW1

# 2. Install all dependencies (creates .venv automatically)
uv sync

# 3. Copy the environment template and fill in your values
cp .env-example .env
```

### Train the ML Models (first run only)

The RNN and LSTM classifiers require pre-trained weight files. Generate them once:

```bash
uv run python src/fourier/services/train_models.py
```

This writes `models/rnn_classifier.pt` and `models/lstm_classifier.pt`. Training takes approximately 2–5 minutes on a modern CPU.

### Run the App

```bash
uv run python -m fourier
```

Open your browser and navigate to `http://127.0.0.1:8050`.

---

## Configuration

All configuration lives in `config/` — **no values are hardcoded in source files.**

### `config/app_config.json`

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
  "low_confidence_threshold": 0.40
}
```

| Key | Description |
|-----|-------------|
| `resolution` | Number of sample points per waveform (default 500 = 50 pts/sec over 10 s) |
| `duration` | Total display window in seconds |
| `debug` | Set `true` for Dash hot-reload during development |
| `rnn_model_path` | Path to the trained RNN weight file |
| `lstm_model_path` | Path to the trained LSTM weight file |
| `low_confidence_threshold` | If the top class probability is below this value, a "Low Confidence" warning is shown |

### `config/rate_limits.json`

```json
{
  "version": "1.00",
  "rnn_max_calls_per_minute": 60,
  "lstm_max_calls_per_minute": 30,
  "inference_timeout_seconds": 5,
  "max_retries": 2
}
```

### `.env`

Copy `.env-example` to `.env` and fill in any required secrets. The `.env` file is never committed to version control.

```
# .env-example
APP_SECRET_KEY=change-me
```

---

## Usage Guide

### 1. Harmonic Synthesis (Left Sidebar)

The left sidebar contains four **channel panels** — one per harmonic. Each panel exposes:

| Control | Range | Description |
|---------|-------|-------------|
| Enable toggle | On / Off | Include or exclude this harmonic from both charts |
| Frequency slider | 0.1 – 5.0 Hz | Oscillation frequency of the sine wave |
| Amplitude slider | 0 – 100 | Peak value of the wave |
| Phase slider | 0 – 2π rad | Time offset of the wave |
| Display mode | Line / Dots | Continuous waveform or discrete sampled points |
| Sampling rate | 1 – 50 Hz | (Dots mode only) Controls sampling density |

Sliders update charts on release. All four panels start at factory defaults (see `docs/PRD.md` Section 3, FR-01).

**Reset:** Click the **Reset** button in the header to restore all 24 controls to defaults in one action.

### 2. Real-Time Waveform Visualization (Main Area)

Two charts are displayed:

- **Overlay Chart** (top, light background): Each enabled channel plotted individually in its accent color (indigo / purple / pink / rose).
- **Summation Chart** (bottom, dark navy background): The composite signal — the sum of all enabled channels.

Both charts share the same x-axis (0–10 s) and y-axis (−100 to 100).

### 3. 1-Second Window Selection

Below the **Summation Chart**, a slider labeled **"Analysis Window Start (s)"** lets you select a 1-second analysis window anywhere in the 10-second range.

- Drag the slider from **0.0 to 9.0 s** (step: 0.1 s).
- A semi-transparent **amber highlight band** appears on the Summation Chart, showing the exact 1-second window that will be analyzed.
- The label above the slider updates to display `Analysis Window: [t_start, t_start + 1.0] s`.

The window is always exactly **1 second wide** — the slider enforces this constraint.

### 4. Algorithm Selection & Identification

Below the window slider, choose an algorithm:

| Option | Description |
|--------|-------------|
| **RNN** | Run the Recurrent Neural Network classifier only |
| **LSTM** | Run the Long Short-Term Memory classifier only |
| **Both** | Run both classifiers and compare results |

Click **Identify**. A loading spinner is shown during inference (typically < 2 seconds).

### 5. Interpreting Results

#### Single Algorithm Mode (RNN or LSTM)

The results panel shows:

- **Identified Channel:** Name and default frequency of the detected harmonic.
- **Confidence:** The model's certainty (0–100%).
- **Probability Bar Chart:** Four horizontal bars showing the full softmax output for all channels.

If the top-class confidence is below the threshold set in `config/app_config.json` (`low_confidence_threshold`), a **"Low Confidence"** warning is displayed.

#### Both Mode (Comparison & Diff)

Two result panels are shown side by side, followed by a **Diff Summary**:

| Diff Field | Description |
|------------|-------------|
| Agreement | Whether both algorithms chose the same channel |
| Confidence Δ | LSTM confidence − RNN confidence (in percentage points) |
| Top-class diff | Side-by-side winning probabilities |
| Runner-up diff | Second-highest class from each model |

If the two algorithms **disagree**, the diff panel displays a red warning with both predictions shown explicitly.

---

## Documentation Map

| Document | Purpose |
|----------|---------|
| `docs/PRD.md` | User problems, functional/non-functional requirements, measurable KPIs |
| `docs/PLAN.md` | C4 architecture diagrams (all 4 levels), 6 ADRs, full API schemas, directory blueprint |
| `docs/TODO.md` | 7-phase task list with Definition of Done for every task |
| `docs/PRD_RNN.md` | Feature PRD for the RNN classifier (math, architecture, training, failure modes) |
| `docs/PRD_LSTM.md` | Feature PRD for the LSTM classifier (math, architecture, training, comparison diff) |
| `docs/Prompt_Log.md` | Book of Prompts — records every major AI-generated component |
| `docs/RNN.md` | Reference: RNN mathematical foundations and implementation principles |
| `docs/LSTM.md` | Reference: LSTM internal mechanisms and implementation guide |
| `notebooks/analysis.ipynb` | Sensitivity analysis, mathematical proofs (LaTeX), high-resolution visualizations |

---

## Project Directory

```
AI-Agent-Orchestration-HW1/
├── src/fourier/
│   ├── sdk/
│   │   ├── signal_generator.py      # Fourier synthesis logic
│   │   ├── window_extractor.py      # 1-second window extraction & normalization
│   │   ├── rnn_classifier.py        # RNN inference
│   │   ├── lstm_classifier.py       # LSTM inference
│   │   └── result_comparator.py     # Diff computation
│   ├── services/
│   │   └── train_models.py          # Offline model training script
│   ├── ui/
│   │   ├── layout.py                # Dash HTML layout
│   │   ├── callbacks_client.py      # Client-side JS callbacks (< 50 ms renders)
│   │   └── callbacks_server.py      # Server-side Python callbacks
│   ├── shared/
│   │   ├── version.py               # VERSION = "1.00"
│   │   └── constants.py             # WAVE_NAMES, COLORS
│   └── gatekeeper.py                # Central API gatekeeper (rate limits, retries, logging)
├── tests/                           # pytest, ≥ 85% coverage
├── models/
│   ├── rnn_classifier.pt            # Pre-trained RNN weights
│   └── lstm_classifier.pt           # Pre-trained LSTM weights
├── config/
│   ├── app_config.json              # App settings (no hardcoded values in source)
│   └── rate_limits.json             # Inference rate limits
├── notebooks/
│   └── analysis.ipynb               # Research & sensitivity analysis
├── docs/                            # All planning and design documents
├── assets/
│   └── clientside.js                # Extracted clientside JS callback
├── .env-example                     # Secret template (copy to .env)
├── .gitignore                       # Excludes .env, __pycache__, .venv
├── pyproject.toml                   # uv-managed; includes Ruff + pytest config
└── README.md                        # This file
```

---

## Contributing

### Quality Gates (must pass before any commit)

```bash
# Linting — zero violations required
uv run ruff check src/

# Tests — minimum 85% coverage
uv run pytest --cov=src --cov-fail-under=85

# Type check (optional but encouraged)
uv run mypy src/
```

### Rules

- **Package manager:** `uv` only. Never use `pip install` or `python -m venv`.
- **File length:** No source file may exceed 150 lines.
- **No hardcoding:** All URLs, timeouts, and limits must live in `config/`.
- **Secrets:** Never commit `.env`. Add new secret keys to `.env-example` with dummy values.
- **TDD:** Write failing tests before implementing any new feature (Red → Green → Refactor).
- **Prompt log:** Add an entry to `docs/Prompt_Log.md` for every major AI-generated component.
