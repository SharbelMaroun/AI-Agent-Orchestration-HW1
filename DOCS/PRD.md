# PRD — Fourier Frequency App
**Version:** 1.00 | **Status:** Approved | **Owner:** sharbelm

---

## 1. Problem Statement

Students and engineers learning signal processing lack an interactive, hands-on tool that combines:
1. Real-time Fourier synthesis experimentation (build signals from harmonics).
2. Intelligent signal decomposition (identify dominant harmonics from a composite window using ML).

Existing tools are either static (textbook diagrams) or require coding expertise (NumPy/MATLAB scripts). There is no browser-based, zero-code tool that bridges synthesis *and* ML-powered analysis in a single UI.

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

### FR-04 · 1-Second Window Selection
- The user shall be able to select a 1-second analysis window on the Summation Chart via a slider (range 0–9 s, step 0.1 s).
- The selected window shall be highlighted on the Summation Chart as a semi-transparent vertical band.

### FR-05 · Algorithm Selection
- The user shall choose from: **RNN**, **LSTM**, or **Both**.
- An **Identify** button shall trigger inference; a loading spinner shall be shown during computation.

### FR-06 · RNN Identification
- An RNN classifier shall accept the 50-point normalized window and output a 4-class probability distribution.
- The result panel shall show: identified channel, confidence score, and a 4-bar probability chart.

### FR-07 · LSTM Identification
- An LSTM classifier (2-layer, hidden=128, dropout=0.3) shall perform the same task as FR-06.

### FR-08 · Comparison Mode (Both)
- When Both is selected, results from RNN and LSTM shall be displayed side by side.
- A Diff Summary panel shall show: agreement flag, confidence delta (LSTM − RNN), top-class and runner-up probabilities from each model.

### FR-09 · Noise Injection Slider
- A **Noise Intensity** slider (id: `noise-slider`, range 0.0–0.5, step 0.01, default 0.0) shall be displayed in the ML identification panel.
- When σ > 0.0, Gaussian noise `N(0, σ²)` shall be added to the normalized 50-point window **after** normalization and **before** model inference.
- At σ = 0.0 the behavior shall be identical to the no-noise baseline.
- A dynamic text label shall describe the noise level (Clean / Light / Medium / Heavy) next to the slider value.
- The noise value shall be read from the slider on every Identify button click; it shall not trigger inference on its own.

---

## 4. Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-01 | Chart update latency | < 50 ms (client-side JS) |
| NFR-02 | Model inference latency | < 2 s per click on a modern CPU |
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
| Identification accuracy | Accuracy on held-out synthetic test set (per class, balanced) | ≥ 90% |
| RNN vs LSTM accuracy gap | Δ accuracy (LSTM − RNN) on test set | ≥ +3 pp |
| Coverage gate | `pytest --cov` output | ≥ 85% |
| Linting gate | `uv run ruff check src/` violations | 0 |

---

## 6. Out of Scope (v1.00)

- Audio playback via Web Audio API
- FFT / frequency-domain chart
- User authentication or session persistence
- More than 4 harmonic channels
- Mobile layout optimization
