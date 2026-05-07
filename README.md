# Fourier Neural Decoder
**Version:** 1.07 | Interactive Fourier synthesis and ML-powered signal regression.

> **Note for the grader:** Earlier prototypes — `fourier-freq-demo-app/` (the original Plotly demo built with Gemini's help, never refactored into the SDK) and `App-to-convert-to-python/` (the JavaScript reference implementation that was ported to Python) — have been **removed from the latest commit** so there is no ambiguity about which app to run. **The single canonical app is the Python package under `fourier-neural-decoder/`, started with `uv run python -m fourier`.** Both legacy folders are still recoverable from prior commits in this repo's git history (`git log --all`) if you ever need to inspect them.

A browser-based educational tool: compose composite waveforms from up to four harmonic channels, then use trained **RNN, LSTM, and FC regressors** to recover the 10 coordinates of any chosen channel from a 10-sample (10 ms) window of the noisy summation. Identification mode samples at **1000 Hz**; per-channel **α (amplitude) and β (phase)** sliders inject parametric noise.

> 🎥 **App walkthrough video:** [`DOCS/images/app-overview.mp4`](DOCS/images/app-overview.mp4) — a short screen recording demonstrating both modes (synthesis and identification), the three frames, the α / β noise sliders, the window slider at 1 kHz resolution, and the Identify result panel. Click the link to download / play; on github.com the link offers the raw file, and most local clones will preview the MP4 inline when the link is opened.

---

## Table of Contents

1. [Technical Stack](#technical-stack)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage Guide](#usage-guide)
5. [Training the Models](#training-the-models)
6. [Documentation Map](#documentation-map)
7. [Project Directory](#project-directory)
8. [Contributing](#contributing)
9. [Project Report (Summary)](#project-report-summary)

---

## Technical Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Package Manager | `uv` (pip is forbidden) | latest |
| Web Framework | Dash (Flask-based) | ≥ 2.17.0 |
| Visualization | Plotly (WebGL via `scattergl`) | ≥ 5.20.0 |
| Numerical Computing | NumPy | ≥ 1.24.0 |
| ML Framework | PyTorch (CPU) | ≥ 2.0.0 |
| Linting | Ruff | zero violations required |
| Testing | pytest + pytest-cov | ≥ 85 % coverage required |

> **Architecture:** SDK-first with the 150-line rule. All business logic lives in `fourier-neural-decoder/src/fourier/sdk/`. The UI is a thin consumer of the SDK. See [`DOCS/PLAN.md`](DOCS/PLAN.md) for the full C4 architecture and ADRs.

---

## Installation

### Prerequisites

Install the `uv` package manager. **`pip` and `venv` are forbidden in this project.**

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
git clone <repo-url>
cd AI-Agent-Orchestration-HW1/fourier-neural-decoder
uv sync
cp .env-example .env
```

### Train the regressors (first run only)

```bash
uv run python -m fourier.services.train_all
```

This writes `weights/{rnn,lstm,fc}_regressor.pt`. Training all three takes ~10–15 minutes on a modern CPU. Per-epoch logs (`mse`, `mae`, `acc`) are emitted on stderr.

### Run the app

```bash
uv run python -m fourier
```

Open `http://127.0.0.1:8050` in your browser.

---

## Configuration

All runtime settings live in `fourier-neural-decoder/config/` — nothing is hardcoded in source.

### `config/app_config.json`

```json
{
  "resolution": 500,
  "duration": 10,
  "debug": false,
  "host": "127.0.0.1",
  "port": 8050,
  "version": "1.07",
  "window_duration": 0.01,
  "window_points": 10,
  "alpha_default": 0,
  "beta_default": 0,
  "alpha_max": 100,
  "beta_max": 100
}
```

| Key | Description |
|-----|-------------|
| `resolution` | Continuous-overlay points per channel (500 = 50 pts/sec over 10 s) |
| `duration` | Total signal length in seconds |
| `debug` | Dash hot-reload (development only) |
| `host` / `port` | Server bind address |
| `window_duration` | Analysis-window length (10 samples / 1000 Hz = 0.01 s) |
| `window_points` | Samples in the analysis window |
| `alpha_default` / `alpha_max` | Per-channel amplitude-noise slider default / max (% of A) |
| `beta_default` / `beta_max` | Per-channel phase-noise slider default / max (% of π) |

### `config/training_config.json`

| Section | Key | Description |
|---|---|---|
| `rnn` / `lstm` / `fc` | `weights_path` | Where each model's trained weights are saved |
| | `hidden_size` | Recurrent / hidden width (default 64) |
| | `learning_rate`, `batch_size`, `epochs`, `grad_clip` | Adam hyper-params |
| `data` | `n_samples`, `test_ratio`, `seed` | Dataset size and 80 / 20 split |
| | `alpha_train_max`, `beta_train_max` | Upper bound of per-channel noise during training (default 0.3) |

### `config/rate_limits.json`

Reserved for future external-API integration. Used by the `Gatekeeper` class to wrap inference with retries / timeouts / structured logging.

### `.env`

Copy `.env-example` to `.env` for any secrets. `.env` is never committed.

---

## Usage Guide

### Two operational modes

| Mode | Purpose | What you can change |
|---|---|---|
| **Synthesis** (default) | Free harmonic exploration | Frequency, amplitude, phase, sampling rate, display mode (line / dots), enable toggles |
| **Identification** | ML inference on noisy samples | α / β noise sliders (8 total), window-start slider, Identify button. Frequency / amplitude / phase / sampling rate are **locked**. |

Click **Enter Identification Mode** to switch.

### The three frames

Three Plotly charts stack in the main area:

1. **Noisy overlay** (top, light background) — every enabled channel rendered with its α / β jitter applied per sample.
2. **Pure overlay** (middle, light background) — the same channels with **no noise**, always showing the true sines as a reference.
3. **Σ summation** (bottom, dark background) — the noisy composite that feeds the ML models. A thin amber rectangle marks the user-selected 10-sample analysis window.

### Synthesis mode controls

Each of the 4 channel panels in the sidebar exposes:

| Control | Range | Effect |
|---|---|---|
| Enable toggle | on / off | Include or exclude this channel from the charts |
| Frequency | 0.1 – 5.0 Hz | Oscillation rate |
| Amplitude | 0 – 100 | Peak value |
| Phase | 0 – 2π rad | Time offset |
| Display mode | line / dots | Continuous waveform or discrete sampled points |
| Sampling rate (dots only) | 1 – 50 Hz | Sampling density |

Charts update in real time (< 50 ms) via clientside JavaScript — no server round-trip.

### Identification mode

The 4 channels are locked to the reference signals:

| Channel | f (Hz) | A | φ (rad) |
|---|---|---|---|
| sin1 | 0.5 | 60 | 0 |
| **sin2 (extraction target)** | **1.0** | **40** | **π/4** |
| sin3 | 1.5 | 25 | π/3 |
| sin4 | 2.0 | 15 | π/2 |

The display sample rate is forced to **1000 Hz** (10 001 samples over 10 s).

#### Parametric α / β noise model

Each channel has two noise sliders:

- **α — Amp noise (%)** — slider 0 – 100; perturbs amplitude.
- **β — Phase noise (%)** — slider 0 – 100; perturbs phase.

The signal generated for channel *k* is:

```
y_k(t) = (A_k + α·A_k·ε) · sin(2π·f_k·t + φ_k + β·π·ε),    ε ~ Uniform(-1, +1) per sample
```

ε is drawn **per sample, per channel** — produces visible scatter around the true sine, not a shifted sine. At α = 100 % the amplitude swings symmetrically in `[0, 2A]`; at β = 100 % the phase shifts in `[−π, +π]`. The α / β sliders use `updatemode="mouseup"` so the chart updates only on slider release (avoids per-pixel lag at 1 kHz).

#### Window selection

The **Window-start slider** (0.000 – 9.990 s, step 0.001 s) selects a 10-sample (10 ms) slice of the noisy summation. The amber rectangle on the Σ-chart shows the picked window — at this scale it appears as a thin vertical line.

#### Running inference

Click **Identify**. All three regressors plus the ground-truth pure channel are evaluated on the same window. The result panel shows:

- A row per sample index (`n` 0–9).
- Columns: **RNN**, **LSTM**, **FC** predictions vs **real** ground truth.
- Three error columns (`err(R)`, `err(L)`, `err(F)`) — each cell is `prediction − truth`, green if `|err| ≤ 1`, red otherwise.
- Per-method **MAE** summary line.

---

## Training the Models

```bash
# from fourier-neural-decoder/
uv run python -m fourier.services.train_all          # noisy training (default), α,β ~ U(0, 0.3)
uv run python -m fourier.services.train_all --clean  # clean training, α=β=0, saves to weights/*_clean.pt
uv run python -m fourier.services.train_all rnn fc   # subset of models
```

Per-epoch logs are written to stderr in the format:

```
[rnn] epoch  10/150  train mse=584.12 mae=19.34 acc=0.050  test mse=634.21 mae=21.12 acc=0.030
```

`acc` is the fraction of output values within ±1.0 amplitude unit of truth — strict by design, pair it with MAE for a sane reading.

Each example is built as follows:

1. Locked chosen channel = sin2 (matches inference, which always sends `C = [0, 1, 0, 0]`).
2. Fixed amplitudes / phases from `ID_MODE_SIGNALS`.
3. Random window start `n_start ~ Uniform{0, 9991}`.
4. Per-channel α, β ~ Uniform(0, `alpha_train_max`); per-sample ε ~ Uniform(−1, +1).
5. Input = noisy summation (10 samples) + C one-hot. Target = clean chosen channel at the same `t_grid`. Loss = MSE in raw amplitude units.

---

## Documentation Map

| Document | Purpose |
|----------|---------|
| [`DOCS/PRD.md`](DOCS/PRD.md) | User problems, functional / non-functional requirements, KPIs |
| [`DOCS/PLAN.md`](DOCS/PLAN.md) | C4 diagrams, ADRs (1 – 10), API schemas, directory blueprint |
| [`DOCS/TODO.md`](DOCS/TODO.md) | Phased task list with Definition of Done for every task |
| [`DOCS/PRD_RNN.md`](DOCS/PRD_RNN.md) | Feature PRD for the RNN regressor (math, architecture, training) |
| [`DOCS/PRD_LSTM.md`](DOCS/PRD_LSTM.md) | Feature PRD for the LSTM regressor |
| [`DOCS/PRD_FC.md`](DOCS/PRD_FC.md) | Feature PRD for the FC baseline |
| [`DOCS/Prompt_Log.md`](DOCS/Prompt_Log.md) | Book of Prompts — every major AI-assisted component logged |
| [`DOCS/REPORT.md`](DOCS/REPORT.md) | Full project report (the summary at the bottom of this README is condensed from it) |
| [`fourier-neural-decoder/notebooks/analysis.ipynb`](fourier-neural-decoder/notebooks/analysis.ipynb) | Sensitivity analysis & visualisations |
| [`concepts/`](concepts/) | Lecturer's reference PDFs (`RNN-BOOK.pdf`, `LSTM-book.pdf`) — reference material, not project source |
| [`CLAUDE.md`](CLAUDE.md) | Project-wide instructions auto-loaded by Claude Code (renamed from the original `INSTRUCTIONS.md`) |

---

## Project Directory

```
AI-Agent-Orchestration-HW1/
├── CLAUDE.md                        # Project-wide instructions auto-loaded by Claude Code
├── README.md                        # This file (canonical user manual)
├── DOCS/                            # Planning and design documents
│   ├── PRD.md / PLAN.md / TODO.md
│   ├── PRD_RNN.md / PRD_LSTM.md / PRD_FC.md
│   ├── REPORT.md / Prompt_Log.md / Project_Description.md
│   └── images/                      # Figures referenced from REPORT.md and this README
├── concepts/                        # Lecturer's reference PDFs
└── fourier-neural-decoder/          # Python package (canonical app)
    ├── src/fourier/
    │   ├── sdk/
    │   │   ├── signal_generator.py      # Sine generation with parametric α/β noise
    │   │   ├── window_extractor.py      # Pure deterministic slice + normalise
    │   │   ├── rnn_regressor.py         # Book-faithful Elman RNN regressor
    │   │   ├── lstm_regressor.py        # Book-faithful LSTM regressor
    │   │   └── fc_regressor.py          # 2-layer MLP baseline
    │   ├── services/
    │   │   ├── _train_loop.py           # Shared fit/evaluate/save pipeline
    │   │   ├── train_rnn.py             # RNN trainer + shared dataset generator
    │   │   ├── train_lstm.py            # LSTM trainer
    │   │   ├── train_fc.py              # FC trainer
    │   │   └── train_all.py             # CLI runner for terminal training
    │   ├── ui/
    │   │   ├── layout.py                # Dash component tree
    │   │   ├── layout_id_mode.py        # Identification-mode UI builders
    │   │   ├── callbacks_client.py      # Clientside JS chart callback
    │   │   ├── callbacks_server.py      # Server callbacks (toggle, value display)
    │   │   ├── callbacks_id_mode.py     # Identification-mode entry / exit + UI lock
    │   │   ├── callbacks_identify.py    # Identify button handler
    │   │   ├── callbacks_result.py      # Result-panel rendering
    │   │   └── app.py                   # create_app() factory
    │   ├── shared/
    │   │   ├── version.py               # VERSION = "1.07"
    │   │   ├── constants.py             # ID_MODE_SR, EXTRACT_POINTS, ID_MODE_SIGNALS, …
    │   │   ├── types.py                 # TypedDicts
    │   │   └── config_loader.py         # load_app_config / load_training_config
    │   ├── gatekeeper.py                # Inference wrapper (logging + retry policy)
    │   └── __main__.py                  # Entry point with logging configured
    ├── tests/                           # pytest, ≥ 85 % coverage
    │   ├── unit/
    │   └── integration/
    ├── weights/                         # Trained model weights (.pt files)
    ├── config/                          # app_config / training_config / rate_limits
    ├── notebooks/
    │   └── analysis.ipynb
    ├── pyproject.toml                   # uv-managed; Ruff + pytest config
    ├── uv.lock
    ├── .env-example
    ├── .gitignore
    └── README.md                        # Stub — points to this root README
```

---

## Contributing

### Quality Gates (must pass before any commit)

```bash
# from fourier-neural-decoder/
uv run ruff check src/                                # zero violations required
uv run pytest --cov=src --cov-fail-under=85           # ≥ 85 % coverage required
```

### Rules

- **Package manager:** `uv` only. Never `pip install` or `python -m venv`.
- **File length:** No source file may exceed 150 lines.
- **No hardcoding:** All URLs, timeouts, and limits must live in `config/`.
- **Secrets:** Never commit `.env`. Add new secret keys to `.env-example` with dummy values.
- **TDD:** Write failing tests before implementing any new feature (Red → Green → Refactor).
- **Prompt log:** Add an entry to `DOCS/Prompt_Log.md` for every major AI-generated component.

---

# Project Report

> **Authors:** Sharbel Maroun and Amr Safadi worked together on this project from Sharbel's computer.

> Image references resolve to [`DOCS/images/`](DOCS/images/).

## 0. Development Journey

This project started with a session on Gemini, working through the lecture files from Moodle — especially the RNN and LSTM material. NotebookLM was the first attempt, but it errored out and never worked, so Gemini took over for the conceptual exploration.

Gemini's explanations of RNN and LSTM internals were used to build a small intuition-demo app for visualising harmonic synthesis (uploaded into this repo as `fourier-freq-demo-app/`, kept around for reference and removed from the v1.07b commit so the grader can't accidentally run the wrong app — see the note at the top of this README). Claude was then asked to write a description of that demo into `DOCS/Project_Description.md`.

From there the conversation moved to Claude with the full homework requirements and `INSTRUCTIONS.md` (a Gemini-summarised version of the Moodle assignment brief, later renamed to `CLAUDE.md` at the project root so Claude Code auto-loads it on every session). Claude built the foundational `PRD.md`, `PLAN.md`, `TODO.md`, and feature PRDs first — no code before docs. Implementation followed in 23 phases (logged in `DOCS/TODO.md`) using Claude Sonnet 4.6 by default, switching to Opus 4.6 when something took more than three prompts to land.

The project went through three architectural eras:

| Era | Task | Status |
|---|---|---|
| v1.00 – v1.04 | RNN / LSTM **classifiers** (which of 4 frequencies is in a 1-second window) | Superseded |
| v1.05 – v1.06 | RNN / LSTM / FC **regressors** (recover 10 coordinates of a chosen channel) | Superseded |
| **v1.07 – v1.07c (current)** | Same regression task at **1 kHz / 10 ms / locked `chosen = sin2`** with parametric α/β noise | **Final** |

## 0a. Why the v1.01 Classification Era Mattered (Historical)

Although v1.07 is a regression task, the original v1.01 classification experiment is the **strongest evidence for the lecturer's claim** about LSTM vs RNN, and is referenced in §14 below.

In that setup the network classified **which of 4 frequencies** sat inside a 50-sample / 1-second window. We observed:

- **Vanilla RNN:** loss pinned at `1.386 = ln(4)`, accuracy **stuck at ~25 %** (random chance on 4 balanced classes) for all 150 epochs. The vanishing gradient through 50 `tanh` recurrences killed the learning signal before it reached the early time-steps where frequency information lives.
- **LSTM:** reached **100 % accuracy from epoch 30 onward**. The additive cell-state update `C_t = f_t ⊙ C_{t-1} + i_t ⊙ C̃_t` provides a gradient highway that does not vanish.

That experiment is the textbook demonstration of the "RNN can't carry low-frequency info, LSTM can" claim. The 10-sample / 10 ms regression in v1.07 is a much shorter sequence where the gap shrinks but stays in the same direction (LSTM 5.55 MAE vs RNN 8.36 MAE, see §11).

## 0b. Notable Engineering Challenges (Resolved)

A handful of issues were significant enough to mention beyond the three v1.07b bugs in §6:

1. **RNN oscillation in v1.01 training** — the vanilla RNN reached 83 % accuracy at epoch 130 then collapsed to 24 % by epoch 150. Fixed by (a) `StepLR` halving the LR every 40 epochs and (b) saving the **best validation checkpoint** rather than the last epoch.
2. **Non-determinism from `ThreadPoolExecutor`** — the original `Gatekeeper` ran inference in a background thread; PyTorch returned different predictions depending on thread scheduling. Fixed by switching to a soft timeout in the main thread (true hard-kill timeouts aren't cross-platform on Windows without OS signals).
3. **Architecture-mismatch errors after `hidden_size` changes** — added explicit `state_dict` key validation before `load_state_dict()`, so a config change without a retrain produces a clear "missing keys" error instead of an opaque PyTorch traceback.
4. **`callbacks_server.py` exceeded 150 lines** — split into `callbacks_server.py`, `callbacks_identify.py`, `callbacks_id_mode.py`, `callbacks_result.py`. All UI files now ≤ 150 lines.
5. **Windows encoding issue in tests** — `test_version_consistency` crashed on the README's em-dashes under cp1255. Fixed with explicit `encoding="utf-8"`.

## 0c. What Went Well

- **SDK-first design** — every business-logic class lives in `src/fourier/sdk/`, callable without a running Dash server. This made 95 % test coverage achievable.
- **Config-driven hyperparameters** — switching `hidden_size`, learning rate, epoch count, or noise range never requires a code edit.
- **Gatekeeper around inference** — central place for logging and retry policy; one fix when the threading issue surfaced.
- **State-dict key validation** — caught architecture mismatches with a readable error.
- **Best-model checkpoint** — saved the architecture during RNN oscillation; without it the saved model would have been the 24 % epoch-150 weights.

---

> The summary below is the condensed-for-README version of the project report; further sub-sections come from the in-depth narrative.

## 1. App Architecture — Two Operational Modes

The app supports two distinct modes, each tied to a different educational objective.

| Mode | Purpose | Sliders enabled | Sliders locked |
|---|---|---|---|
| **Synthesis (default)** | Free exploration of harmonic superposition | Frequency, Amplitude, Phase, Sampling Rate, Display mode | — |
| **Identification** | Controlled signal extraction with ML inference | α / β noise sliders, Window slider, Identify button | Frequency, Amplitude, Phase locked to `ID_MODE_SIGNALS`; sample rate locked at 1000 Hz |

In Identification Mode the four channels are fixed to `(0.5, 1.0, 1.5, 2.0) Hz` with amplitudes `(60, 40, 25, 15)` and prescribed phases. The summation chart renders 10 001 samples over 10 s; a thin amber rectangle marks the user-selected 10-sample (10 ms) analysis window.

## 2. The Three Frames

Three Plotly charts stack vertically:
1. **Noisy overlay** — every enabled channel rendered with its α / β jitter applied per sample.
2. **Pure overlay** — same channels with **no noise** (always shows the true sines as a reference).
3. **Σ summation** — the noisy composite signal that feeds the network.

The pure frame is the visual ground truth — moving the noise sliders affects only the other two frames.

## 3. Parametric α / β Noise Model

Replaced the legacy single-σ Gaussian *output* noise with a parametric jitter on each sine's parameters, drawn fresh for every sample:

```
y_k(t) = (A_k + α_k · A_k · ε_k) · sin(2π · f_k · t + φ_k + β_k · π · ε_k),    ε_k ~ Uniform(-1, +1)
```

- **8 sliders total** — independent α (amplitude noise %) and β (phase noise %) per channel.
- ε is drawn **per sample, per channel** — produces visible scatter around the true sine, not a shifted sine.
- At α = 100 %, A swings symmetrically in `[0, 2A]`. At β = 100 %, the phase shifts in `[−π, +π]` (full 2 π span).

## 4. Identification Mode Inference

A single click of the Identify button runs three regressors on the same 10-sample window:

| Model | Architecture | Notes |
|---|---|---|
| **RNN** | Book-faithful Elman cell, H = 64, manual `W_x / W_h / b` | `nn.RNN` forbidden |
| **LSTM** | Book-faithful gated cell, separate `W_f / W_i / W_C / W_o`, additive cell-state update, forget-bias init = 1.0 | `nn.LSTM` forbidden |
| **FC** | 2-layer MLP, ReLU, ~ 1.6 K params | Non-recurrent baseline |

The result panel shows side-by-side reconstructions vs. the ground-truth pure channel, with per-method MAE and per-row error columns.

## 5. v1.07 — 1 kHz Sample Rate, Random Window Start

`ID_MODE_SR` was raised from 20 Hz to **1000 Hz** to match the lecturer's spec. The 10-sample window now spans **0.01 s = 10 ms** instead of 0.5 s. Training picks `n_start ~ Uniform{0, 9991}` per example so the model sees windows from any position in the 10 s range.

This made every individual prediction harder — a 10 ms window holds only ~1/200 of a 0.5 Hz cycle, so the input is nearly a straight line — but it directly implements the assignment requirement.

## 6. v1.07b — The Three Bugs That Shaped the Final Version

### Bug A — Predictions collapsed to ≈ 0

After locking the training distribution to `ID_MODE_SIGNALS` and adding parametric noise, every model's output was stuck near zero while the ground-truth chosen channel sat at ≈ −39 amplitude units.

![Result panel showing predictions ≈ 0 vs real ≈ −39](DOCS/images/resultsWithHighError+UI.png)

**Cause:** the training pipeline normalized both input and target by `max(|summed|)`. With *fixed* signals, the summation magnitude collapses near zero in destructive-interference troughs while the chosen channel can still sit near peak — making the normalized target blow up and forcing the network to predict the dataset mean (≈ 0).

**Fix:** dropped per-sample normalization. With bounded fixed signals (`Σ|A_k| = 140`), raw amplitude units work better than the textbook `[−1, 1]` recipe. Predictions now actually track the real values.

**Result after fixes A + C-lock (v1.07c):** the per-row error column dropped from ±30 – 45 to ±5 – 15 — predictions actually track the chosen channel rather than collapsing to zero.

![Identification result after the v1.07c fixes — much smaller errors](DOCS/images/betterResults.png)

The two changes that did this:
1. **Removed normalization** (Bug A above) — the network no longer trained against exploding targets in destructive-interference regions.
2. **Locked chosen channel = sin2 in training** — every one of the 6 000 examples now exercises the deployed task (was 25 % before; the other 75 % were teaching extraction of the unused channels). 4× more relevant signal, no architecture changes needed.

Both fixes preserve the book-faithful constraints (manual `W_x / W_h / b` for the RNN, separate gate matrices for the LSTM, no `nn.RNN` / `nn.LSTM`) — only the data distribution changed.

### Bug B — Severe rendering lag in identification mode

With three charts each rendering ~ 10 001 markers, dragging the noise sliders or scrolling the page froze the app.

**Cause:** Plotly's default SVG renderer creates one `<circle>` DOM node per dot — 120 K+ SVG elements were being relaid out on every reflow. Combined with `updatemode="drag"` on the noise sliders firing the clientside callback dozens of times per second.

**Fix:**
1. Added `type: 'scattergl'` to every trace — Plotly draws to a single `<canvas>` per chart instead of thousands of SVG nodes.
2. Switched only the α / β sliders to `updatemode="mouseup"` — chart updates once on release rather than mid-drag. Frequency / amplitude / phase sliders keep live drag because they're cheap.

### Bug C — `acc` metric stuck at 2–5 % every epoch

A screenshot during training showed `acc` flat across all 150 epochs while MSE/MAE were dropping — looking like the model never learned anything.

![Terminal during training — acc stuck at single-digit %](DOCS/images/badResults.png)

**Cause:** three stacked reasons:
1. `ACC_TOL = 1.0` raw amplitude unit demands ~0.7 % relative precision against a ±140 signal range — too strict to be a quality score.
2. The **information-bound** problem: 10 ms of a 0.5 Hz signal is nearly linear; the network cannot fully recover (A, φ) from such a slice.
3. **Destructive-interference troughs** make the input → target mapping high-Lipschitz; the network smooths these into mean predictions.

**Conclusion:** `acc` at strict tolerance is a tripwire, not a quality score. The real metrics are MSE and MAE — they did drop (RNN MAE 21 → 11). Pair `acc` with MAE on every chart.

## 7. Why LSTM Outperformed RNN

![Four frequency classes in a 1-second window](DOCS/images/fig1_four_classes.png)

In the historical (v1.01) classification setup with a 1-second window, LSTM reached 100 % accuracy while a vanilla RNN got stuck at chance. The gated cell-state highway lets the LSTM carry low-frequency context (the 0.5 Hz half-cycle) across the full 50 time-steps without it being squashed by the tanh nonlinearity. The vanilla RNN's hidden state collapses long before the sequence ends.

This advantage carries over to v1.07 regression: in the latest **clean-mode** run, the LSTM hit `MAE = 4.4` while RNN/FC plateaued at ~`8.5` — a 2× edge. The LSTM is the only model that consistently exploits the (admittedly thin) information in a 10 ms slice.

## 8. Network Depth Decision (v1.06)

Stayed at **1 hidden layer + 1 output layer** for every model. Reasoning:
1. Capacity isn't the bottleneck — the FC (~1.6 K params) plateaus at the same MAE as the LSTM (~18 K params).
2. An earlier H = 128 / 250-epoch experiment was *worse* than H = 64 / 150 epochs.
3. Comparison cleanliness: holding depth constant means any MAE difference reflects only the cell type.
4. The bottleneck is information, not parameters: 10 samples × 1 ms is the assignment's hard cap.

## 9. Training Pipeline (v1.07c)

Every training example:
1. **Locked chosen channel = sin2** — the only channel asked for at inference, so all 6 000 examples now exercise the deployed task (was 25 % before fix C-mismatch).
2. Fixed amplitudes/phases from `ID_MODE_SIGNALS` (no more random `(A, φ)` per example).
3. Random window start `n_start ~ Uniform{0, 9991}`.
4. Per-channel α, β ~ Uniform(0, 0.3) (or 0 in `--clean` mode); per-sample ε ~ Uniform(−1, +1).
5. Input = noisy summation (10 samples) + C one-hot. Target = clean chosen channel at the same `t_grid`. Loss = MSE in raw amplitude units.

Run in terminal:

```bash
uv run python -m fourier.services.train_all          # noisy training (default)
uv run python -m fourier.services.train_all --clean  # clean training, saves to weights/*_clean.pt
uv run python -m fourier.services.train_all rnn fc   # subset of models
```

Per-epoch logs report `mse`, `mae`, and `acc` on both train and test sets every 5 epochs.

## 10. Lessons Learned

- **Match training distribution to inference exactly** — the C-vector mismatch and the random-amplitude/phase mismatch each hurt accuracy more than any architecture choice.
- **Don't normalize unbounded what's already bounded** — with fixed signals, raw amplitude units beat `[−1, 1]` because the latter introduces singularities at destructive troughs.
- **`scattergl` is essentially free past ~5 K points** — the default SVG renderer drowns in DOM nodes long before WebGL breaks a sweat.
- **Strict-tolerance "accuracy" on regression problems with wide output range is misleading** — pair it with MAE to read it correctly.
- **Information-bound problems can't be fixed by adding layers.** When a 10 ms window only contains 1/200 of a cycle, no architecture rescues you. Real solutions either change the window or change the regression target (predict (A, φ) instead of 10 raw points).

---

# 11. Comparative Analysis: RNN vs LSTM vs FC

All three models were trained on the **same** dataset (locked `chosen = sin2`, fixed signal parameters, random `n_start`, parametric α/β noise) with the **same** hyper-parameters (`H = 64`, `lr = 0.005`, `150 epochs`, `batch = 64`, `6 000 samples`). The only thing that varies is the cell architecture.

### Architectural differences

| Property | RNN | LSTM | FC |
|---|---|---|---|
| Sees input as | sequence of 10 scalars | sequence of 10 scalars | **single 14-d vector** (10 + C) |
| Recurrence | yes (`h_t ← h_{t-1}`) | yes + cell-state highway | **no** |
| Activation | `tanh` | `σ` (gates) + `tanh` | `ReLU` |
| Parameters (H = 64) | ~ 5.1 K | **~ 18 K** | ~ **1.6 K** |
| Sensitive to time-order? | yes | yes | **no** — permuting the 10 samples gives the same output |
| Inference cost | mid (10-step loop) | mid (10-step loop, 4 gates each) | **lowest** (single matmul) |

### Why only the FC sees the input as a flat 14-d vector

A natural question reading the table above: *"the FC takes 10 samples + 4 C as a single 14-d vector — should the RNN and LSTM do the same?"* **No.** The flat-vector treatment is correct **only** for the FC; the RNN and LSTM must see the input as a sequence. Three reasons:

**1. Recurrent networks need a sequence to recur over.**
The RNN's defining update rule is `h_t = tanh(W_x · x_t + W_h · h_{t-1} + b)` — the hidden state evolves **sample-by-sample**. The LSTM's gated cell state `C_t = f_t ⊙ C_{t-1} + i_t ⊙ C̃_t` integrates information **across time**. If you flatten everything into a 14-d vector and feed it once:

- The recurrence becomes trivial (one step, or the same input replicated 10 times).
- The LSTM cell-state highway has nothing to integrate across.
- Both architectures degenerate into expensive, badly-parameterised MLPs.

You wouldn't get a Python error — PyTorch would run it — but you'd get **worse** results because you'd be using the wrong tool for the wrong input shape.

**2. The book equations require per-step input.**
`PRD_RNN.md` (`RNN-FR-02`) and `PRD_LSTM.md` (`LSTM-FR-02`), both derived directly from `concepts/RNN-BOOK.pdf` (Eq. 2.13–2.14) and `concepts/LSTM-book.pdf` (§6.1):

> *Input per timestep = `[sample_t, C_0, C_1, C_2, C_3]`. The C vector is concatenated to each timestep.*

Each step receives a **5-d** vector; the C is broadcast across all 10 steps so the network knows which channel to extract at every step. Flattening would violate the book-faithful mandate.

**3. It would invalidate the whole comparison the assignment is asking for.**
The point of running RNN / LSTM / FC side-by-side is:

> *"What does each architecture's inductive bias buy us on this task?"*

- **FC** has no temporal awareness → flat 14-d input is its natural format.
- **RNN** has plain hidden-state recurrence → per-step 5-d input.
- **LSTM** has gated cell-state recurrence → per-step 5-d input.

If we flattened the RNN/LSTM input, all three models would degenerate into similar MLP variants, and any MAE difference would reflect width / depth / activation rather than the cell type. The §14 analysis ("LSTM beats RNN because the gated cell state survives 10 time-steps where the RNN's vanishing gradient kills slow-varying context") would lose its empirical basis.

### What every model receives in practice

| Model | Shape received | Same 14 numbers reach the model? | Permutation-invariant? |
|---|---|---|---|
| **FC** | `(B, 14)` — flat | yes — concatenated once | yes (acceptable: FC has no time anyway) |
| **RNN** | `(B, 10, 5)` — 10 samples, each paired with the same 4-d C | yes — C repeated at every step | no (recurrence preserves order) |
| **LSTM** | `(B, 10, 5)` — identical layout to RNN | yes | no |

The user-visible interface is uniform — `process(window: 10-element array, c_vector: [0, 1, 0, 0])`. Internally each model reshapes / broadcasts the same two inputs into the form its architecture needs. There is no Tensorial information lost or gained between the three; only the way that information is presented to the cell.

### Test metrics (clean training, eval on `sin2`-only test set)

| Model | MSE | MAE | acc (±1.0) | RMSE |
|---|---|---|---|---|
| RNN | 147.0 | 8.36 | 12.0 % | 12.12 |
| **LSTM** | **125.4** | **5.55** | **42.1 %** | **11.20** |
| FC | 189.1 | 10.87 | 10.4 % | 13.75 |

Per-epoch terminal logs from the noisy-mode training run, one screenshot per architecture:

![RNN — per-epoch training log](DOCS/images/RNNNewTrainingResults.png)
![LSTM — per-epoch training log](DOCS/images/LSTMNewTrainingResults.png)
![FC — per-epoch training log](DOCS/images/FCNewTrainingResults.png)

These captures show `mse`, `mae`, and `acc` reported every 5 epochs for each architecture, ending in the `DONE` line that produces the noisy-training metrics tabulated below.

### What the numbers say

- **LSTM wins clearly** — we measure 33 % lower MAE than RNN and 49 % lower than FC, and the LSTM is the only model in our test set that breaks the strict `acc(±1)` threshold beyond noise. Its gated cell-state highway carries information across all 10 time-steps without being squashed by the `tanh` non-linearity.
- **RNN is mid-pack** — better than the FC, worse than the LSTM. Its hidden state degrades over the sequence, so it gets *some* benefit from the temporal structure but can't fully exploit it.
- **FC is the worst, but only by a little** — and it has 11× fewer parameters than the LSTM. The fact that it stays close to the RNN tells us the task is **information-bound, not capacity-bound**: with only 10 nearly-collinear samples, recurrence can't conjure information that isn't there.

### Historical evidence (v1.01 classification setup)

When the task was **classification on 1-second / 50-sample windows**, we saw a much larger gap: the LSTM reached 100 % accuracy on all 4 frequency classes while the vanilla RNN got stuck at chance. That experiment showed us the **upper bound** of the LSTM advantage when sequences are long enough for the vanishing-gradient problem to bite.

The v1.07 task (10-sample window) is too short to fully expose that gap, but the **direction of our result is the same**: LSTM > RNN > FC.

### Reading the numbers: why in-app MAE is lower than training-test MAE

A natural question when running the app: *"the training log said `[lstm] DONE test mae=12.11` but the result panel after I click Identify shows `LSTM MAE = 4.05` — which is right?"* **Both are correct**, measured on different data. Three factors explain the gap:

**1. Default weights are noisy-trained; you click Identify with clean sliders.**
`weights/lstm_regressor.pt` is the **noisy-trained** snapshot (`α, β ~ U(0, 0.3)` during training). Its training test set is a 1 200-example mix where every example has *some* noise. When you run the app with all sliders at 0, you feed the model a **clean** window — the easiest possible regime. The model has seen plenty of near-clean training examples (whenever both random draws landed near 0), so inference on a clean signal is easier than the average noisy test sample.

| Slider position | Expected single-window LSTM MAE |
|---|---|
| α = β = 0 (clean) | ≈ 4 – 7 |
| α, β ~ U(0, 0.3) average (training test set) | ≈ 12 |
| α = β = 100 % (outside training) | predictions collapse |

This pattern is the **direct visual confirmation** of the noise-precision regimes described in §12.

**2. Training-test MAE is averaged over ~1 200 windows; the app shows one.**
The test set is 20 % of 6 000 examples; each has a different `n_start` (anywhere in 10 s) and a fresh α / β draw. Some windows are inherently harder than others — destructive interference at certain `n_start` makes the input low-amplitude while the chosen channel is still near peak. Other windows are easier — chosen channel slowly varying near its own peak with constructive interference in the summation. The 12.11 you see in the log is the mean across that whole distribution; the 4.05 you see in the app is a single sample from it.

**3. The window you happened to pick is on the easy side.**
For the example above, the ground-truth column was `real ≈ 28.4 → 30.0` over 10 samples — `sin2` near its peak, slowly varying. The model only needs to output a roughly constant value near 30 to do well, which both RNN and LSTM nearly do. Move the window slider to a different position and you'll see the per-window MAE swing between ~2 and ~15. The mean across many positions is what matches the table in §11.

**How to verify:**

- Drag the window slider to positions 0.0, 1.5, 3.0, 4.5, 6.0, 7.5, 9.0 and click Identify each time. The per-window LSTM MAE should range from ~2 to ~15. The mean across a dozen windows should land near 5–6, matching the §11 clean-trained table.
- Crank α to 30 % with β = 0. The MAE should rise toward ~10–12, matching the noisy-training test-set average. That's the regime the default `*.pt` weights were optimised for.

Both confirmations are evidence that §11 (architecture ranking) and §12 (noise-precision relationship) are reporting the same model behaviour you observe in the running app.

---

# 12. Relation Between Noise and Precision

The α / β sliders do not introduce a fixed performance penalty — the relationship is regime-dependent and asymmetric.

### Three regimes

| Slider range | Distribution | Network behaviour |
|---|---|---|
| **0 % – 30 %** | Inside training distribution (`alpha_train_max = beta_train_max = 0.3`) | Best precision — predictions track the clean signal closely. |
| **30 % – 60 %** | Mild extrapolation | Predictions degrade gradually; bias toward the dataset mean grows. |
| **60 % – 100 %** | Hard extrapolation | Predictions become unreliable; the network has never seen this regime. |

### Why precision degrades with α

`α` perturbs amplitude: `A_eff = A · (1 + α · ε)` with ε ~ U(−1, +1). At α = 100 %, `A_eff` swings in `[0, 2A]`. Because ε is **per-sample**, the noise has zero mean — the underlying clean signal is still recoverable in expectation, and a denoising regressor can average it out. The MAE rises roughly **linearly** with α inside the training range.

### Why phase noise (β) is more destructive than amplitude noise (α)

Amplitude noise is **additive on the radius**: `(1 + αε)` is a multiplicative scalar near 1. Even at α = 100 % the underlying sinusoid keeps its frequency and phase — only its envelope wobbles.

Phase noise is **destructive on the argument**: `sin(2π f t + φ + βπε)`. At β = 100 % the phase shift covers the full `[−π, +π]` range, so consecutive samples become **uncorrelated** with the true frequency. The signal stops looking sinusoidal and starts looking like white noise around zero. There's no way for the network to recover the underlying sine when the phase information has been destroyed.

**Practical implication:** the network tolerates α much better than β. At α = 100 %, β = 0 %, predictions are still useful. At α = 0 %, β = 100 %, predictions collapse toward zero (the input is no longer a sine).

### A note on training-vs-inference mismatch

We chose a **deliberately conservative** training noise range (α, β ≤ 0.3) for two reasons:
1. To keep the network reliable in the slider regime that's actually useful (mild perturbation, not destruction).
2. Because training with very heavy noise teaches the network that the signal is essentially random — it then performs *worse* in the clean regime, which is the most common operating point.

This is recorded as a deliberate trade-off in `DOCS/Prompt_Log.md` (ENTRY-022 onward).

---

# 13. When to Use a Fully-Connected (FC) Network

The FC is the right choice in three situations:

### 1. The input has no temporal / sequential structure
If permuting the input dimensions doesn't change the meaning of the data — e.g. tabular features, a fixed-size feature vector extracted by some other process, scalar regression — then recurrence buys you nothing. The FC's permutation-invariance is a feature in those settings, not a bug.

### 2. You need a **baseline** to test whether recurrence is actually earning its weight
This is the FC's role in **this project**. With three models trained on identical data, the FC tells you: *"this is what you'd get without exploiting time order."* If the LSTM beats the FC by 5×, recurrence pays off. If they tie (as on noisy training in our case), recurrence isn't doing useful work and you should question whether it's worth the parameter / inference cost.

> **Our result:** clean training — LSTM beats FC by ~ 49 % MAE → recurrence pays off when information is sufficient. Noisy training — FC ties with RNN, only the LSTM pulls ahead → in the noise-limited regime, the LSTM's gated memory still helps but the RNN's plain recurrence doesn't.

### 3. Latency or capacity is the constraint
The FC has **11× fewer parameters than the LSTM** and **3× fewer than the RNN** at the same hidden width. Its forward pass is a single `ReLU(W₁ x + b₁) → W₂ ⋅ + b₂` — no time loop, no gate computation. For real-time inference on tiny devices, or when memory-per-model matters, the FC is the right starting point and you only escalate to recurrence if benchmarks justify it.

### When **not** to use FC

- Long sequences with non-trivial temporal dependencies (RNN/LSTM/Transformer territory).
- Spatial data with translation symmetry (CNN territory).
- When sequence length is variable (FC requires fixed input dimensionality).

---

# 14. Does the Lecturer's Claim Hold? "LSTM extracts all frequencies; RNN only handles high frequencies"

**Short answer: yes, in spirit — and our results back the direction of the claim, though the magnitudes vary by setup.**

### The classical justification

A vanilla RNN's hidden state `h_t = tanh(W_x x_t + W_h h_{t-1} + b)` is squashed by `tanh` at every time-step. Information from earlier samples decays roughly geometrically with the sequence length — this is the **vanishing-gradient problem**. **Slow-varying (low-frequency)** signals are precisely those whose informative variation spans many time-steps; their pattern is "remembered" only if the hidden state retains long-range context. The RNN can't, so it preferentially latches onto **fast-varying (high-frequency)** features that complete within a few steps.

The LSTM solves this by separating the **cell state `C_t` from the hidden state `h_t`**. The cell state is updated **additively** (`C_t = f_t ⊙ C_{t-1} + i_t ⊙ C̃_t`), with no `tanh` squash on the highway path. Information can flow across many time-steps essentially untouched, gated only by the forget gate. So the LSTM **can** carry low-frequency context, and that's exactly why it generalises to all four reference frequencies.

### What we observed in our experiments

| Setup | RNN result | LSTM result | Verdict |
|---|---|---|---|
| **v1.01 classification** (1-s window, 50 samples at 50 Hz, 4 frequency classes) | Stuck at **chance** across all 4 classes — never learned to distinguish low-frequency classes | **100 %** accuracy on all 4 classes | ✅ **Strongly supports** the lecturer's claim. The RNN literally fails to generalise; the LSTM nails every frequency. |
| **v1.07 regression** (10-ms window, 10 samples at 1 kHz, fixed `sin2 = 1 Hz`) | MAE 8.36 | MAE 5.55 | ✅ Direction agrees — LSTM is **33 % better** — but at this window length both architectures are limited by the information ceiling, not the gradient flow, so the gap is smaller. |

### Nuances we observed

- **The RNN isn't *purely* high-frequency-only:** we saw it still beat the FC on our regression task, which tells us it extracts *some* useful structure even from a fast-decaying hidden state. We read the lecturer's claim as "RNN is *biased toward* high frequencies", not "RNN can *only* see high frequencies".
- **The window length matters as much as the cell type.** A 50-sample window over a 0.5 Hz signal contains 25 % of one cycle — long enough for the RNN's vanishing gradient to bite. A 10-sample window over the same signal contains 0.5 % of one cycle — neither cell can use temporal structure that doesn't exist in the input. We observed the LSTM advantage shrink accordingly.
- **The LSTM advantage is most visible in clean conditions.** Under heavy noise we saw all three (RNN, LSTM, FC) degrade together because the noise was what limited accuracy, not the architecture. With clean data, the LSTM's superior memory paid the largest dividend.

### Final verdict

We find the lecturer's claim **theoretically sound and empirically supported**. Our v1.01 classification experiment is the textbook demonstration of the LSTM's universal-frequency advantage and the RNN's high-frequency bias. Our v1.07 regression experiment shows the same pattern in a more constrained regime — quieter, but in the same direction. **In every regime we tested on average, LSTM ≥ RNN.**

### Curvature determines which architecture wins (per-window)

Our "LSTM beats RNN" claim holds **on average across the test distribution**. It does **not** hold for every individual window. We deliberately captured a matched pair of windows that demonstrates the per-window behaviour exactly mirrors the lecturer's frequency-bias claim:

#### High-curvature window — RNN out-performs LSTM

![RNN out-performs LSTM on a high-curvature window](DOCS/images/curvatureRNNBetter.png)

When the user positions the window on a portion of the summation where the chosen channel is **changing rapidly** — high local curvature, large derivative, e.g. a zero-crossing region of `sin2` or a point where multiple channels rise simultaneously — the **RNN beats the LSTM** for that specific window. Reason:

- A high-curvature 10 ms slice is dominated by **high-frequency content** (the variation completes within just a handful of samples).
- The vanilla RNN is **biased toward high-frequency features** by construction — its hidden state can't carry low-frequency context but it does preserve fast within-window variation.
- The LSTM's gates **smooth out** rapid variation as a side-effect of the cell-state highway being designed to preserve slow-varying context. On a window where the *signal itself* is fast-varying, that smoothing is a hindrance.

#### Weak-curvature (near-flat) window — LSTM out-performs RNN

![LSTM out-performs RNN on a weak-curvature window](DOCS/images/weakCurvatureLSTMBetter.png)

When the window sits on a slow-varying region — e.g. the chosen channel is near its peak with `dy/dt ≈ 0` for the whole 10 ms slice — the picture flips:

- A near-flat 10 ms slice contains essentially **only low-frequency content** (the slow change of `sin2` toward / away from its peak).
- The vanilla RNN can't carry that information across 10 time-steps without the `tanh`-squashing degrading it; its hidden state effectively forgets the early samples by the time it reaches the output, so it predicts a fairly generic value with little curvature awareness.
- The LSTM's cell-state highway preserves the slow drift across all 10 steps; its prediction tracks the gentle slope.

**Crucially, the FC behaves like the RNN in this regime.** Look at the err columns in `weakCurvatureLSTMBetter.png`: FC and RNN errors are similar magnitudes; only LSTM tracks the slope cleanly. Reason: the FC's permutation-invariant treatment of the input gives it no temporal awareness at all — and on a near-flat window where the *only* useful information is the slow-drift trend across time-steps, lacking temporal awareness is functionally similar to the RNN's vanishing-gradient memory failure. **Both the RNN (memory destroyed by `tanh`) and the FC (no memory by design) end up unable to read the gentle curvature; only the LSTM's protected cell-state recovers it.**

#### Why this is the strongest possible support for the lecturer's claim

Two complementary screenshots, same architectures, same configurations, opposite outcomes — driven entirely by **which frequency content dominates the window**:

| Window type | Dominant frequency content | Best model | Why |
|---|---|---|---|
| **High curvature** | High-freq | **RNN** | RNN's high-freq bias is a feature; LSTM gates smooth it out |
| **Weak curvature** | Low-freq | **LSTM** | Only LSTM's protected cell state survives 10 steps; RNN forgets, FC has no memory |

This is the per-window counterpart of the v1.01 classification result: the same RNN failure mode (can't carry slow-varying context across many time-steps) and the same LSTM advantage (cell-state highway), playing out on individual 10 ms slices in the v1.07 regression task. **In aggregate the LSTM wins because real signals contain a mix of curvatures — and the LSTM is the only architecture that performs acceptably on both kinds of window.** The lecturer's claim ("RNN sees only high frequencies; LSTM sees all") isn't just a textbook generalisation; we directly observe it on individual windows in this app.

---

# 15. Implementation Choices That Could Change Which Model Wins

The current ranking we report (LSTM > RNN > FC on average; RNN > LSTM on high-curvature windows; FC ≈ RNN on near-flat windows) is specific to the choices we made in `training_config.json` and the SDK. Several of those choices are not unique — different reasonable choices would tip the comparison in different directions. We list them here so a future reader / re-trainer understands which knobs are load-bearing.

### 15.1 Window length — the single biggest lever

Our analysis window is **10 samples = 10 ms** at 1 kHz, fixed by the lecturer's spec. That's 1/200 of a 0.5 Hz cycle and ~1/100 of a 1 Hz cycle. With so little signal in each window, every model is fighting against the information ceiling, and the LSTM advantage is small (~33 % MAE reduction vs RNN).

| Window length | Predicted ranking | Reasoning |
|---|---|---|
| **5 ms (5 samples)** | All three near-tied at high MAE | Information ceiling is even tighter; even LSTM can't recover the channel reliably |
| **10 ms (current)** | LSTM > RNN > FC, gap ~ 33 – 49 % | Just enough information for the LSTM's gated memory to matter on near-flat windows |
| **100 ms (100 samples)** | LSTM ≫ RNN > FC, gap > 2× | Long-range context becomes critical; RNN's vanishing gradient bites |
| **1 s (1000 samples)** | LSTM ≫ RNN; FC unable to scale | Mirrors the v1.01 classification result: LSTM 100 %, RNN at chance |

We could not change the window length (lecturer's spec). If you re-run with a longer window, expect the LSTM advantage to grow substantially.

### 15.2 Number of training samples — diminishing returns past ~6 k

We trained on `n_samples = 6000` (1 200 test). Earlier we ran a `n_samples = 20000` experiment: every model improved by ~6 %, all ranks stayed the same. The data is **information-bound, not data-bound** — once you have ≥ ~5 000 samples of random `n_start`, the network has seen enough window positions; more data only adds redundancy.

If you run with **far fewer samples** (e.g. `n_samples = 500`), expect the FC to suffer disproportionately: fewer parameters mean less natural regularisation, and the FC's permutation-invariance becomes a liability when each example has to teach the network a unique input → output mapping with no inductive bias to lean on.

### 15.3 Hidden size — surprisingly not the bottleneck

We use `hidden_size = 64` everywhere. Earlier we ran an `H = 128` / 250-epoch / 12 K-sample experiment. **Result: the LSTM got worse** (MAE 0.232 vs the H=64 baseline's 0.203). Larger models trained longer on more data overfit a task that's already saturated by information.

| Hidden size | Predicted effect |
|---|---|
| 32 | RNN / FC degrade; LSTM still functional (gates buy capacity even at small H) |
| **64 (current)** | All three trained well; cell-type comparison is clean |
| 128 + | LSTM and RNN start to overfit; FC stays ~unchanged (already minimal) |
| 256 + | All three overfit the 6K dataset within 30 epochs |

Holding `H` constant across architectures is what makes the §11 ranking interpretable. If we doubled `H` only on the LSTM, its lead would look bigger, but the comparison would no longer be fair.

### 15.4 Training noise range — the regime knob

We train with `α, β ~ Uniform(0, 0.3)`. This produces models that are **best at low slider values** (the common operating regime) and gracefully degrade above ~30 % α/β.

If we changed `alpha_train_max` / `beta_train_max` in `training_config.json`:

| `alpha_train_max` = `beta_train_max` | Effect on the comparison |
|---|---|
| **0** (clean) | LSTM advantage grows: clean MAE 5.55 vs noisy 12.11. LSTM dominates by ~50 %. |
| **0.1 (light)** | LSTM advantage shrinks slightly; all three closer to clean numbers. |
| **0.3 (current)** | Models converge to similar MAE under noise; LSTM still leads but only by a few percent. |
| **0.6 – 1.0 (heavy)** | All three collapse toward predicting the dataset mean; ranking becomes noise. The networks can't extract a sine when phase is randomised. |

Heavy training noise actually **flattens the ranking** by destroying the signal the LSTM uses to outperform. We chose 0.3 deliberately to keep the architectural comparison meaningful.

### 15.5 Output head — the biggest unrealised improvement

Our networks output **10 raw coordinates**. Because we know the channel frequency at inference (`C` is one-hot over `ID_MODE_SIGNALS`), a more efficient head would output **2 numbers** — `(A_predicted, φ_predicted)` — and reconstruct the 10 coordinates analytically from `f_chosen`. This collapses the regression dimensionality 5×, gives the network a much stronger prior, and would (we expect) drop MAE by another 2–5×.

| Output head | Predicted MAE | Notes |
|---|---|---|
| **10 raw coords (current)** | LSTM 5.55 | Each output dimension fights for its own loss budget |
| **`(A, φ)` head + analytic reconstruction** | LSTM ~ 1 – 3 expected | Network only needs to estimate two well-conditioned numbers |

This is the single highest-leverage change we did **not** implement — it would benefit the FC most because the FC is currently the most over-parameterised relative to the task complexity, and reducing the output dimensionality would free its capacity.

### 15.6 Per-sample normalisation — a trap we hit and reverted

We tried `target / max(|summed|)` early. It blew up in destructive-interference troughs (Bug A in §6) and we removed it. Re-introducing it would collapse all three models to predict ~ 0 again — a regression we already observed. Keep it removed.

### 15.7 Locking `chosen` — quietly important

Training with `chosen = sin2` everywhere matches inference exactly. Earlier we trained with `chosen` drawn uniformly from {0, 1, 2, 3}; only 25 % of examples exercised the deployed task. Going back to random `chosen` would degrade the LSTM's clean MAE from 5.55 to roughly 8 (still leading the rest, but losing about ⅓ of its advantage).

### 15.8 Activation choice — the SIREN angle (untried)

The FC uses `ReLU`. The literature on **sinusoidal neural networks** (SIREN, FLM) suggests that replacing `ReLU` with `sin` activations on tasks with periodic targets can improve fit by 2 – 10 ×. We did **not** try this; the standard 2-layer MLP with ReLU was the agreed baseline. A `sin`-activated FC would likely close the gap to the LSTM and might even surpass it on clean windows, while losing to the LSTM under noise.

### Summary — which knob favours which model

| Knob | Direction | Helps |
|---|---|---|
| Longer window | ↑ samples | LSTM strongly; RNN moderately; FC scales poorly |
| More training data | ↑ samples | All equally past ~5 K |
| Larger H | ↑ params | LSTM marginally; RNN marginally; FC ~ no effect |
| Heavier training noise | ↑ noise | None — flattens the ranking |
| Lighter / clean training | ↓ noise | LSTM most |
| `(A, φ)` head | ↓ output dim | All; FC most |
| Lock `chosen = sin2` | ↑ task focus | LSTM most (already done) |
| `sin` activation in FC | activation swap | FC most (untried) |

**Read the rest of the report knowing that the rankings we observe are real but not unique** — we ran a comparison under one set of choices that respects the lecturer's spec and is internally consistent. Different reasonable choices would shift specific numbers; the high-level "LSTM ≥ RNN, FC is the cheap baseline" pattern is robust across all the regimes we explored.
