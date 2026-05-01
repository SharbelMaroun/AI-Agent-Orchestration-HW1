# Fourier Frequency App — Project Description

## 1. Executive Summary

The **Fourier Frequency App** is an interactive, browser-based signal synthesis and visualization tool built with Python and Dash. It enables users to compose complex waveforms in real time by layering up to four independent sinusoidal harmonics, adjusting their frequency, amplitude, and phase, and immediately observing how those individual waves combine into a composite signal. The application is primarily an educational instrument, designed to make the abstract mathematics of Fourier synthesis tangible and visually intuitive — bridging the gap between textbook theory and hands-on experimentation.

The app demonstrates three foundational concepts in signal processing:

- **Fourier Synthesis:** Any periodic signal can be expressed as a sum of sinusoids (harmonics).
- **Superposition:** When multiple waves occupy the same medium, the result is their linear sum at every point in time.
- **Discrete Sampling:** A continuous signal can be represented by a finite set of sampled points at a given sampling rate, as formalized by the Nyquist-Shannon theorem.

---

## 2. Core Functionality

### 2.1 Harmonic Channel Control

The app provides four independent harmonic channels, each representing one sinusoidal component:

| Channel | Default Frequency | Default Amplitude | Default Phase |
|---------|-------------------|-------------------|---------------|
| 1 (Fundamental) | 0.5 Hz | 50 | 0 |
| 2 (Second Harmonic) | 1.0 Hz | 30 | π/2 |
| 3 (Third Harmonic) | 1.5 Hz | 20 | π |
| 4 (Fourth Harmonic) | 2.0 Hz | 10 | 3π/2 |

The defaults are deliberately chosen to mimic a natural harmonic series: each successive channel doubles its frequency relative to the previous and progressively reduces amplitude, producing a characteristic sawtooth-like composite when summed.

Each channel can be independently:
- **Enabled or disabled** via a checkbox — disabled channels are hidden from both charts and excluded from the summation.
- **Tuned** across three axes:
  - *Frequency:* 0.1 Hz to 5.0 Hz (step 0.01)
  - *Amplitude:* 0 to 100 (step 1)
  - *Phase shift:* 0 to 2π radians (step 0.01)
- **Switched to discrete sampling mode**, which replaces the continuous line with a set of sampled dots at a user-controlled sampling rate (1 to 50 Hz).

### 2.2 Real-Time Waveform Visualization

Two synchronized Plotly charts update instantly as users manipulate sliders:

1. **Channel Overlay Chart** — Plots each enabled wave individually on the same axes. When a channel is in discrete mode, its waveform is rendered as sample points with hover tooltips showing the sample index, timestamp, and value. The chart uses a light theme for clarity.

2. **Additive Summation Chart** — Plots the composite signal produced by summing all enabled channels. It uses a dark theme (deep navy background) to visually distinguish it as the "result" view. The y-axis title renders the mathematical notation `∑ sin(2πft + φ)`.

Both charts share identical x-axis (0–10 seconds) and y-axis (−100 to 100) ranges, allowing direct visual comparison between individual components and their superposition.

### 2.3 Discrete Sampling Mode

When a channel is switched to "Dots (discrete sampling)" mode, an additional sampling rate slider appears. The app computes:

```
n_samples = floor(DURATION * sampling_rate) + 1
t_s[n]    = n / sampling_rate        (for n = 0, 1, ..., n_samples − 1)
y_s[n]    = A * sin(2π * f * t_s[n] + φ)
```

The resulting discrete vector is displayed beneath the slider as a formatted list of rounded values, each with a hover tooltip showing its index and timestamp. This feature directly illustrates the relationship between sampling rate and signal representation density — a practical demonstration of Nyquist concepts.

### 2.4 Reset

A "Reset" button in the header restores all 24 control values (6 per channel × 4 channels) to their factory defaults in a single callback.

---

## 3. Architecture

### 3.1 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Web Framework | Dash 2.17+ (Flask-based) | App server, layout, callbacks |
| Visualization | Plotly 5.20+ | Interactive, GPU-accelerated charts |
| Numerical Computing | NumPy 1.24+ | Signal generation, array math |
| Client Runtime | JavaScript (inline) | Zero-latency chart updates |

### 3.2 Hybrid Client-Server Design

The app employs a deliberate **hybrid rendering strategy**:

- **Server-side (Python):** Handles layout construction, discrete vector computation, panel visibility toggling, and the reset callback. These operations involve either Python-only logic or relatively infrequent interactions.
- **Client-side (JavaScript):** A single `clientside_callback` receives all 24 control values and computes both Plotly figures entirely in the browser. There is no network round-trip on slider movement — updates are rendered in under 50 ms.

This separation gives the app the full expressiveness of Python and Plotly on the server side, while keeping the interactive experience smooth enough for real-time manipulation.

### 3.3 Key Constants

All simulation parameters are defined as module-level constants, mirrored between Python and the embedded JavaScript:

| Constant | Value | Purpose |
|----------|-------|---------|
| `RESOLUTION` | 500 | Number of points per waveform |
| `DURATION` | 10 | Simulation window in seconds |
| `PI2` | 2π | Angular frequency multiplier |

This ensures mathematical consistency between the server-side discrete calculation and the client-side continuous rendering.

### 3.4 Component Structure

The codebase is organized around two reusable factory functions:

- **`make_slider(id, label, min, max, step, value, marks)`** — Renders a labeled Dash slider component with consistent styling.
- **`wave_panel(i, defaults)`** — Constructs the entire control panel for harmonic channel `i`, including its checkbox, three sliders, discrete mode toggle, sampling rate slider, and vector display. All four channel panels are generated by looping over this function.

Callbacks are also registered in a `for _i in range(4)` loop using a closure variable (`_idx = _i`) to capture the loop index correctly — a common Python gotcha avoided here.

---

## 4. Signal Processing Concepts

### 4.1 Fourier Synthesis

The mathematical backbone of the app is the additive synthesis equation:

```
y(t) = Σ  A_i * sin(2π * f_i * t + φ_i)
        i
```

Where:
- `A_i` is the amplitude of harmonic `i`
- `f_i` is its frequency in Hz
- `φ_i` is its phase offset in radians
- The sum is taken over all enabled channels

By manipulating these three parameters per channel, users can construct square waves, sawtooth waves, triangle waves, and other periodic waveforms — observing in real time how each harmonic contributes to the shape of the composite.

### 4.2 Continuous vs. Discrete Time

The continuous waveform is generated by evaluating the sine function at 500 uniformly spaced time points over 10 seconds:

```
t[k] = (k / RESOLUTION) * DURATION    for k = 0, 1, ..., 499
```

The discrete waveform samples the same underlying signal at the user-specified sampling rate, producing `floor(10 * sr) + 1` points. Comparing the two representations illustrates aliasing effects when the sampling rate is below the Nyquist frequency (2 × signal frequency), and demonstrates how increasing the sampling rate converges toward the continuous signal.

### 4.3 Phase Relationships

Phase shifting a wave slides it forward or backward in time without changing its frequency or amplitude. The app's default configuration places each successive harmonic at a 90° (π/2 radian) phase offset from the previous, which produces a characteristic asymmetric summation. Users can experiment with phase alignment to observe constructive interference (waves reinforce) and destructive interference (waves cancel).

---

## 5. User Interface Design

### 5.1 Layout

The interface is divided into three zones:

1. **Header (60 px, sticky):** Contains the app title "Fourier Synthesis" and the Reset button.
2. **Left Sidebar (300 px, fixed, scrollable):** Hosts all four wave control panels stacked vertically.
3. **Main Content Area (flexible):** Displays the two charts stacked vertically, each 320 px tall.
4. **Footer (36 px):** Shows a status indicator ("Kernel Protocol Loaded // Ready") and the version string "Synthesizer V.05".

### 5.2 Visual Design

The app follows a clean, technical aesthetic:

- **Wave accent colors:** Indigo (#6366f1), Purple (#8b5cf6), Pink (#ec4899), Rose (#f43f5e) — one per channel.
- **Overlay chart:** White/light background for easy comparison of multiple colored lines.
- **Summation chart:** Deep navy (#020617 plot, #0f172a paper) to visually signal this as the final output.
- **Status accent:** Green (#22c55e) for the footer status dot.
- **Typography:** System UI sans-serif stack; monospace font for the footer.
- **Disabled channel panels** reduce to 40% opacity with sliders hidden, providing a clear visual cue that the channel is excluded from the summation.

### 5.3 Interactivity Details

- Sliders use `updatemode='drag'`, meaning values update only on release (not continuously during drag) — preventing excessive re-renders while still feeling responsive.
- Discrete vector values are displayed with hover tooltips showing `[n] @ t=Xs` metadata.
- Wave panels collapse their controls when disabled, keeping the sidebar uncluttered.
- The overlay chart legend labels channels as `CH{i} · {wave_name}` for quick identification.

---

## 6. Dependencies

```
dash>=2.17.0
numpy>=1.24.0
plotly>=5.20.0
```

No database, no authentication, no external API calls. The app is entirely stateless — all state lives in Dash's component values within the current browser session.

---

## 7. Running the App

The application entry point is `app.run(debug=True)`, which starts Flask's development server on `http://localhost:8050` by default. Hot reload is enabled in debug mode, so source changes are reflected without a manual restart.

---

## 8. Educational Value and Use Cases

The Fourier Frequency App is well suited for:

- **Signal Processing courses:** Provide students an interactive complement to lectures on Fourier series, harmonic decomposition, and sampling theory.
- **Audio engineering education:** Demonstrate how musical timbres arise from differing harmonic content (the overtone series).
- **Mathematics visualization:** Illustrate superposition, phase effects, and the convergence of partial sums toward known waveform shapes.
- **Self-directed learning:** Enable anyone curious about wave physics to experiment freely without writing code.

The app intentionally works only in the time domain (no FFT/frequency-domain view), keeping the focus on the synthesis direction of the Fourier framework — building signals up from components rather than decomposing them.

---

## 9. Limitations and Potential Extensions

| Limitation | Possible Extension |
|------------|--------------------|
| Fixed 4 channels | Dynamic add/remove harmonic panels |
| Time-domain only | Add an FFT spectrum analyzer chart |
| No audio output | Synthesize and play audio via Web Audio API |
| No data export | Download waveform as CSV or WAV |
| Single session, no persistence | Save/load presets |
| Fixed 10-second window | Configurable duration |
| No aliasing annotation | Highlight aliasing when `sr < 2f` |

---

## 10. Signal Identification via Machine Learning

### 10.1 Feature Overview

This feature adds a machine-learning layer on top of the existing visualization. The user selects a 1-second window directly on the **Summation Chart** and asks the app to identify which of the four active sine components is the most dominant contributor in that specific window. Two algorithms are offered — RNN and LSTM — both described in the companion documents `RNN.md` and `LSTM.md`. The user may run either algorithm individually or both simultaneously, in which case the app displays both predictions side by side with a computed diff.

The purpose of this feature is to turn the app from a pure synthesis tool into a signal analysis tool, demonstrating how recurrent neural networks can learn to recognize periodic structure in composite waveforms.

---

### 10.2 UI: 1-Second Window Selection on the Summation Chart

#### Graphical Selection Mechanism

A dedicated **window-start slider** is placed immediately below the Summation Chart, spanning the same horizontal extent as the chart (0–9 seconds, step 0.1 s). The slider controls the left edge of a 1-second analysis window; the right edge is always `start + 1.0 s`.

As the user drags the slider, the Summation Chart updates in real time to overlay a semi-transparent **highlight band** (a vertical rectangle / `vrect` shape) spanning the selected 1-second range. The band uses a distinct accent color (e.g., amber `#f59e0b` at 25% opacity) so it is immediately visible against the dark navy chart background without obscuring the waveform underneath.

A text label above or beside the slider reads:

```
Analysis Window: [t_start, t_start + 1.0] s
```

and updates dynamically as the slider moves.

#### Why a Slider (Not Free Drag)

Using a slider rather than Plotly's built-in box-select tool enforces the hard constraint that the window is **always exactly 1 second wide**. Free drag would require additional logic to normalize an arbitrary selection to 1 second and would make it harder for users to align the window to points of interest. The slider approach is also compatible with the existing `updatemode='drag'` convention used throughout the app.

---

### 10.3 Noise Intensity Slider

A **Noise Intensity** slider is placed in the ML identification panel, between the window selector and the algorithm selector. It controls the standard deviation σ of Gaussian noise injected into the extracted window before it is fed to the model.

| Property | Value |
|----------|-------|
| ID | `noise-slider` |
| Range | 0.0 to 0.5 |
| Step | 0.01 |
| Default | 0.0 (no noise) |
| Label | `Noise Intensity (σ)` |

A dynamic text label reads:

```
σ = 0.00  →  Clean signal
σ = 0.15  →  Light noise
σ = 0.30  →  Medium noise
σ = 0.50  →  Heavy noise
```

**Purpose:** The noise slider turns the identification panel into a **robustness tester**. By increasing σ, the user can directly observe at what noise level each model starts making mistakes, and compare RNN vs LSTM degradation curves in the Both mode. Since LSTM has a longer memory (cell state) it is expected to tolerate higher noise levels better than the plain RNN — the slider makes this difference visible interactively.

---

### 10.4 Algorithm Selection UI

Directly below the window slider, a labeled **radio button group** (or segmented button row) offers three options:

| Option | Label | Behavior |
|--------|-------|----------|
| `rnn` | RNN | Run only the RNN classifier |
| `lstm` | LSTM | Run only the LSTM classifier |
| `both` | Both | Run both classifiers and display a comparison |

A **"Identify"** button triggers the analysis. Identification is not automatic on slider drag — the user must explicitly press Identify to avoid expensive model inference on every tick. A loading spinner replaces the button label while inference runs.

---

### 10.4 Data Extraction and Preprocessing

When the user presses Identify, the following steps occur server-side:

1. **Window extraction:** From the summation signal (which is already computed at 500 points over 10 s, i.e., 50 points per second), extract the slice corresponding to the selected 1-second window. This yields exactly **50 data points** (indices `round(t_start * 50)` through `round(t_start * 50) + 49`).

2. **Normalization:** Scale the 50-point vector to the range `[−1, 1]` by dividing by the maximum absolute value observed in that window. This makes the input amplitude-agnostic, so the model focuses on **shape** (frequency and phase pattern) rather than magnitude.

3. **Noise injection (optional):** If the user has set the **Noise Intensity slider** (σ) to a value greater than 0, Gaussian noise with standard deviation σ is added to the normalized window *after* normalization: `window += N(0, σ²)`. This step is controlled entirely by the slider and defaults to σ = 0.0 (no noise). It allows the user to test how robust each model is when the signal is degraded.

4. **Reshape for model input:** The normalized (and optionally noisy) vector is reshaped to `(1, 50, 1)` — batch size 1, sequence length 50, 1 feature per time step — matching the expected input shape `(Batch Size, Sequence Length, Input Features)` described in `RNN.md`.

5. **Label space:** The output target is one of four classes, corresponding to the four harmonic channels:
   - Class 0 → Fundamental (default 0.5 Hz)
   - Class 1 → Second Harmonic (default 1.0 Hz)
   - Class 2 → Third Harmonic (default 1.5 Hz)
   - Class 3 → Fourth Harmonic (default 2.0 Hz)

---

### 10.5 RNN Classifier — Implementation Details

The RNN classifier follows the architecture described in `RNN.md`:

#### Model Architecture

```
Input:  (1, 50, 1)           ← 50 time steps, 1 feature per step
  ↓
RNN Layer (hidden_size=64, activation=tanh)
  — shared weight matrix W applied at every time step
  — hidden state h_t = tanh(W · [x_t, h_{t-1}] + b)
  ↓
Final hidden state h_50      ← shape (1, 64)
  ↓
Fully-Connected Layer (64 → 4)
  ↓
Softmax                      ← shape (1, 4), probabilities sum to 1
Output: class index with highest probability + confidence score
```

#### Forward Pass Logic

The hidden state is initialized to zeros: `h_0 = zeros(1, 64)`. The RNN then iterates through all 50 time steps, updating the hidden state at each step using the shared weight matrix. Only the **final** hidden state `h_50` is passed to the output layer — this encoding captures the temporal pattern of the entire 1-second window.

#### Training Strategy

The model is **pre-trained offline on synthetic data** and the weights are saved to a file (e.g., `models/rnn_classifier.pt`) loaded at app startup. Synthetic training data is generated by:

1. Randomly sampling frequency `f` from the four channel frequencies (with small perturbations ±0.05 Hz to improve generalization).
2. Randomly sampling amplitude `A ∈ [10, 50]` and phase `φ ∈ [0, 2π]`.
3. Computing `y[n] = A · sin(2π · f · n/50 + φ)` for `n = 0, …, 49`.
4. Optionally adding Gaussian noise `σ = 0.05` to simulate real conditions.
5. Labeling each sample with the class index of its frequency.

Training uses cross-entropy loss and the Adam optimizer, run for ~200 epochs over 10,000 synthetic samples (2,500 per class, balanced).

---

### 10.6 LSTM Classifier — Implementation Details

The LSTM classifier follows the four-gate architecture described in `LSTM.md`:

#### Model Architecture

```
Input:  (1, 50, 1)
  ↓
LSTM Layer (hidden_size=128, num_layers=2, dropout=0.3)
  — Forget Gate:   f_t = σ(W_f · [h_{t-1}, x_t] + b_f)
  — Input Gate:    i_t = σ(W_i · [h_{t-1}, x_t] + b_i)
  — Cell Candidate: C̃_t = tanh(W_c · [h_{t-1}, x_t] + b_c)
  — Cell Update:   C_t = f_t ⊙ C_{t-1} + i_t ⊙ C̃_t
  — Output Gate:   o_t = σ(W_o · [h_{t-1}, x_t] + b_o)
  — Hidden State:  h_t = o_t ⊙ tanh(C_t)
  ↓
Final hidden state h_50      ← shape (1, 128)
  ↓
Dropout (p=0.3)
  ↓
Fully-Connected Layer (128 → 4)
  ↓
Softmax
Output: class index + confidence score
```

#### Why LSTM Over Plain RNN for This Task

The four sine waves in the app can have similar shapes over short sub-windows. The LSTM's cell state acts as a long-term memory that accumulates evidence across the full 50-step sequence before making its decision, making it more reliable than a plain RNN when the frequency difference between classes is small (e.g., 0.5 Hz vs. 1.0 Hz over 1 second).

#### Training Strategy

Same synthetic dataset as the RNN, but with a larger hidden size (128 vs. 64) and two stacked LSTM layers. Weights are saved separately to `models/lstm_classifier.pt`. Training uses the Adam optimizer with learning rate 0.001 and dropout 0.3 between layers to prevent overfitting, as recommended in `LSTM.md`.

---

### 10.7 Results Display — Single Algorithm Mode

When either **RNN** or **LSTM** is selected alone, the results panel (rendered below the algorithm selector) shows:

```
┌──────────────────────────────────────────────────────┐
│  Algorithm: RNN                                      │
│  Window analyzed: [2.4 s → 3.4 s]                   │
│                                                      │
│  Identified Component:  CH2 · Second Harmonic        │
│  Frequency:             1.0 Hz                       │
│  Confidence:            87.3%                        │
│                                                      │
│  Class Probabilities:                                │
│  ████████████░░░  CH1 Fundamental    11.2%           │
│  ████████████████ CH2 Second Harm.   87.3%  ← match │
│  ░░░░░░░░░░░░░░░  CH3 Third Harm.     1.1%           │
│  ░░░░░░░░░░░░░░░  CH4 Fourth Harm.    0.4%           │
└──────────────────────────────────────────────────────┘
```

- The identified channel name, default frequency, and confidence are shown prominently.
- A horizontal probability bar chart (4 bars, one per channel) shows the full softmax output so the user can see how certain or uncertain the model was.
- The winning bar is highlighted in the channel's accent color (indigo/purple/pink/rose as defined in the main app).

---

### 10.8 Results Display — Both Algorithms (Comparison and Diff)

When **Both** is selected, two result panels are rendered side by side (flex row layout), followed by a diff summary beneath:

```
┌──────────────────────┐  ┌──────────────────────┐
│  RNN                 │  │  LSTM                │
│  Window: [2.4→3.4 s] │  │  Window: [2.4→3.4 s] │
│                      │  │                      │
│  → CH2 Second Harm.  │  │  → CH2 Second Harm.  │
│  Confidence: 87.3%   │  │  Confidence: 91.6%   │
│  [probability bars]  │  │  [probability bars]  │
└──────────────────────┘  └──────────────────────┘

  ┌─── Diff Summary ───────────────────────────────┐
  │  Agreement:      ✓ Both identified CH2         │
  │  Confidence Δ:   LSTM − RNN = +4.3 pp          │
  │  Top-class diff: CH2: LSTM 91.6% vs RNN 87.3%  │
  │  Runner-up diff: CH1: RNN 11.2% vs LSTM  7.1%  │
  └────────────────────────────────────────────────┘
```

#### Diff Fields Explained

| Diff Field | Description |
|------------|-------------|
| **Agreement** | Whether both algorithms predicted the same class. If they disagree, both predictions are shown in amber with a warning icon. |
| **Confidence Δ** | Signed difference in winning-class confidence (LSTM − RNN), in percentage points. |
| **Top-class diff** | Side-by-side confidence scores for the agreed-upon (or disputed) winning class. |
| **Runner-up diff** | Side-by-side confidence scores for the second-highest class from each model, revealing where each model is "confused". |

If the two algorithms **disagree** on the identified class, the diff panel uses a red accent border and displays both predictions explicitly, e.g.:

```
  Disagreement: RNN → CH2 (64.1%)  |  LSTM → CH1 (78.5%)
```

---

### 10.9 Callback Architecture for This Feature

The new feature integrates into the existing Dash callback graph as follows:

| Trigger | Inputs | Output | Side |
|---------|--------|--------|------|
| Window slider drag | `window-start-slider.value` | Summation chart `figure` (adds vrect shape + updates label) | Client-side JS (extends existing clientside callback) |
| Identify button click | `identify-btn.n_clicks`, `window-start-slider.value`, `algo-selector.value`, all 24 channel controls | `results-panel` children | Server-side Python |

The server-side Identify callback:
1. Reads the current channel states (freq, amp, phase, enabled) to recompute the summation at the exact same points the chart displays.
2. Extracts and normalizes the 50-point window.
3. Runs inference through the selected model(s) (loaded at startup as module-level singletons to avoid reloading on every click).
4. Returns a `dcc.Loading`-wrapped `html.Div` containing the result panel(s).

---

### 10.10 New Dependencies for This Feature

The following packages must be added to `requirements.txt`:

```
torch>=2.0.0        # RNN and LSTM model inference (PyTorch)
```

Or alternatively, if TensorFlow/Keras is preferred:

```
tensorflow>=2.13.0  # RNN and LSTM model inference (Keras)
```

Pre-trained model weight files (`models/rnn_classifier.pt`, `models/lstm_classifier.pt`) must be present in the project directory at startup. A companion training script (`train_models.py`) should be provided to regenerate the weights from scratch if needed.
