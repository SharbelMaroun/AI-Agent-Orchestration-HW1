# PRD — Fourier Frequency App
**Version:** 1.07 | **Status:** Approved | **Owner:** sharbelm

---

## 1. Problem Statement

Students and engineers learning signal processing lack an interactive, hands-on tool that combines:
1. Real-time Fourier synthesis experimentation (build signals from harmonics).
2. Visual signal extraction — given a composite summation window, recover the discrete sample points of a chosen harmonic channel and compare them to the real isolated wave.

Existing tools are either static (textbook diagrams) or require coding expertise (NumPy/MATLAB scripts). There is no browser-based, zero-code tool that bridges synthesis *and* extraction analysis in a single UI.

---

## 2. Target Audience

| Persona | Description |
|---------|-------------|
| **Student** | Undergrad/postgrad in EE, CS, or Physics studying signal processing |
| **Educator** | Professor or TA using the app as a live classroom demo |
| **Self-learner** | Curious non-expert exploring wave physics without coding |

---

## 3. Functional Requirements

### FR-01 · Harmonic Synthesis
- The app shall provide 4 independent harmonic channels.
- Each channel shall expose: enable/disable toggle, frequency (0.1–5.0 Hz), amplitude (0–100), phase (0–2π), display mode (continuous / discrete).
- A discrete sampling mode shall show sampled dots and the discrete vector at a user-controlled sampling rate (1–50 Hz).

### FR-02 · Real-Time Visualization
- An **Overlay Chart** shall display all enabled individual waveforms simultaneously.
- A **Summation Chart** shall display the composite signal (sum of all enabled channels).
- Both charts shall update in under 50 ms on slider change (client-side rendering).
- Both charts shall share x-axis [0, 10 s] and y-axis [−100, 100].

### FR-03 · Reset
- A Reset button shall restore all 24 controls to factory defaults in one action.

### FR-04 · 10-Sample Window Selection
- The user shall be able to select a 10-sample analysis window on the Summation Chart via a slider (range 0–9.99 s, step 0.001 s = 1 sample at 1 kHz).
- At `ID_MODE_SR = 1000 Hz`, 10 samples span **0.01 s**; the highlighted band on the Summation Chart will appear as a thin vertical line. This is intentional — high temporal resolution.
- The selected window shall be highlighted on the Summation Chart as a semi-transparent amber rectangle.

### FR-05 · Identification Mode
- An **Enter Identification Mode** button shall lock all 4 channels to fixed reference signals and force all channels visible.
- An **Exit Identification Mode** button shall return the app to free-edit mode.
- While in identification mode, all channel sliders shall be locked (read-only).

### FR-06 · Wave Extraction (C Vector)
- A one-hot extract vector **C = [c₀, c₁, c₂, c₃]** shall represent which channel the user wants to extract (exactly one `1`).
- The user shall select the target wave via radio buttons visible only in identification mode.
- The **context window** is exactly **10 consecutive samples wide** at the identification-mode sampling rate (`ID_MODE_SR = 1000 Hz` → 0.01 s of signal). The user moves the window's start position with a slider in 1-sample (0.001 s) increments; the highlighted rectangle on the summation chart visualises this 10-sample window.
- Clicking **Identify** shall (a) read the 10 discrete summation samples inside the window, then (b) **extract the chosen channel's frequency component** from those samples using a least-squares Fourier projection over all 4 known channel frequencies, then (c) display the extracted component alongside the ground-truth pure wave at those time points.

### FR-07 · Extraction Result Panel
- The result panel shall present **three** different reconstructions of the chosen wave's 10 coordinates side-by-side, plus the ground truth:
  - **Fourier** column (amber) — the deterministic least-squares Fourier projection (baseline).
  - **RNN** column (purple) — coordinates produced by `BookRNNRegressor` (see `DOCS/PRD_RNN.md`).
  - **LSTM** column (green) — coordinates produced by `BookLSTMRegressor` (see `DOCS/PRD_LSTM.md`).
  - **real** column (wave color) — the ground-truth pure wave at the same time points.
  - **err(F)** column — `Fourier − real` per sample, green if `|error| ≤ 1`, red otherwise.
- A summary line below the table shall report **RNN MAE** and **LSTM MAE** vs. the ground truth, so the user can compare the three methods at a glance.
- All three reconstructions consume the **same** 10-sample window and the **same** C one-hot vector — only the algorithm differs.
- A loading spinner shall be shown while extraction is computed.

### FR-08 · Active Channels Vector
- The enabled state of all 4 channels shall be represented as a binary vector stored in `dcc.Store(id="active-channels")`.
- The clientside chart callback shall consume this vector to determine which channels to render.

### FR-09 · Parametric Noise Injection (α / β Model)
- Each channel shall expose **two** noise sliders, both in percent (range 0–100 %, step 1, default 0):
  - **α — Amplitude noise (%)** — perturbs the channel's amplitude.
  - **β — Phase noise (%)** — perturbs the channel's phase.
- The signal generated for channel *k* shall be:
  $$y_k(t) = (A_k + \alpha_k\!\cdot\!A_k\!\cdot\!\varepsilon)\,\sin\!\big(2\pi f_k t + \varphi_k + \beta_k\!\cdot\!\pi\!\cdot\!\varepsilon\big),\quad \varepsilon\sim\mathrm{Uniform}(-1,+1)$$
- A **single** ε is drawn per channel per evaluation (parametric jitter on amplitude and phase, **not** per-sample additive noise).
- α and β are independent sliders per channel — 8 sliders total across the 4 harmonics.
- At α = 100 %, the effective amplitude swings symmetrically in [0, 2A]. At β = 100 %, the phase shifts symmetrically in [−π, +π] (full 2π span).
- Window extraction is purely deterministic — noise lives upstream in `SignalGenerator`, never in `WindowExtractor`.

---

## 4. Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-01 | Chart update latency | < 50 ms (client-side JS) |
| NFR-02 | Extraction latency | < 200 ms per click |
| NFR-03 | Test coverage | ≥ 85% (pytest) |
| NFR-04 | Code file length | ≤ 150 lines per file |
| NFR-05 | Linting | Zero Ruff violations |
| NFR-06 | Package manager | `uv` only |
| NFR-07 | No hardcoded config | All limits/URLs in versioned JSON/TOML |
| NFR-08 | Secret management | `.env` file, never committed |
| NFR-09 | Browser support | Latest Chrome, Firefox, Edge |
| NFR-10 | OS support | Windows, macOS, Linux |

---

## 5. Measurable KPIs

| KPI | Measurement | Target |
|-----|-------------|--------|
| Synthesis responsiveness | P95 latency from slider release to chart render | < 50 ms |
| Extraction error | Mean absolute error across 10 samples on clean signal | < 5% of amplitude |
| Coverage gate | `pytest --cov` output | ≥ 85% |
| Linting gate | `uv run ruff check src/` violations | 0 |

---

---

### FR-10 · RNN Regressor (Identification Mode)
- A vanilla Elman RNN built per `concepts/RNN-BOOK.pdf` shall accept the 10-sample summation window plus the C one-hot vector and **regress the 10 coordinates** of the chosen channel's pure wave.
- The C vector is concatenated to each per-step input (each step sees `[sample_t, c_0, c_1, c_2, c_3]`), so the network knows which channel to extract at every step.
- The final hidden state is projected linearly to a 10-dimensional output. The output is **raw real-valued coordinates** — no softmax, no classification.
- Loss during training: `MSELoss` on per-sample amplitude-normalised data.
- The RNN must be implemented from the book equations (manual `W_x`, `W_h`, `b` parameters, explicit time-step loop) — `nn.RNN` is not permitted.

### FR-11 · LSTM Regressor (Identification Mode)
- A vanilla LSTM cell built per `concepts/LSTM-book.pdf` §6.1 shall additionally regress the same 10 coordinates from the same input.
- Four separate gate matrices (`W_f`, `W_i`, `W_C`, `W_o`), forget-bias initialised to 1.0, cell-state addition (Eq. 4.3), `nn.LSTM` is not permitted.
- Same input format and loss as the RNN regressor.

### FR-12 · Fully Connected (FC) Regressor — Non-Recurrent Baseline
- A 2-layer MLP (see `DOCS/PRD_FC.md`) shall additionally regress the same 10 coordinates, providing a non-recurrent baseline for direct comparison against RNN and LSTM.
- The FC flattens the 10-sample window and concatenates the C one-hot to form a single 14-d input vector; applies `ReLU(W_1·x + b_1)` then a linear output layer.
- Same training pipeline (shared `_generate_dataset`, MSE, per-sample amplitude normalisation) and same UI integration.
- Result panel shows **four** reconstructions side-by-side: Fourier / RNN / LSTM / FC, plus the ground truth.

---

## 6. Out of Scope (v1.07)

- Classification of the chosen wave (the task is regression of the 10 coordinates, not predicting which class)
- GRU / bidirectional / multi-layer recurrent variants
- Convolutional or attention-based models
- Audio playback via Web Audio API
- FFT / frequency-domain chart
- User authentication or session persistence
- More than 4 harmonic channels
- Mobile layout optimization
