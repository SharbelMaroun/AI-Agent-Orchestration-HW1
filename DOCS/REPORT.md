# Project Report — Fourier Neural Decoder
**Version:** 1.07 | **Date:** 2026-05-07 | **Author:** Sharbel Maroun

---

## v1.07 Update — Parametric Noise + 1 kHz ID Mode

Two design changes superseded the noise and sample-rate discussion below; treat §3.2 / §3.2a as **historical** for v1.01–1.06.

### Parametric α/β Noise Model
The legacy single-σ Gaussian *output* noise was replaced with a parametric jitter on each sine's parameters, drawn once per channel per evaluation:

$$y_k(t) = (A_k + \alpha_k\!\cdot\!A_k\!\cdot\!\varepsilon)\,\sin\!\big(2\pi f_k t + \varphi_k + \beta_k\!\cdot\!\pi\!\cdot\!\varepsilon\big),\quad \varepsilon\sim\mathrm{Uniform}(-1,+1)$$

- **8 sliders** total: each channel has independent α (amplitude noise %) and β (phase noise %), both 0–100 %.
- Symmetric jitter; at 100 % the swing covers the full natural scale (A_eff ∈ [0, 2A]; φ_eff shift ∈ [−π, +π]).
- Training samples α, β, ε per channel per example; **target = clean (un-perturbed) chosen channel** → models learn to denoise.
- `WindowExtractor` is purely deterministic at inference; noise lives upstream in `SignalGenerator`.

### ID-Mode Sample Rate → 1000 Hz
- `ID_MODE_SR` raised from 20 Hz to **1000 Hz**. The 10-second display now contains **10 001 samples**.
- `EXTRACT_POINTS` stays at 10, so the analysis window is **10 ms** wide (was 0.5 s).
- Window slider: `step = 0.001 s` (1-sample resolution), `max = 9.99 s`. Highlight rect on the Σ-chart is a thin amber line (intentional).
- Training generator now picks `n_start ~ Uniform{0, 10000−10}` per example so the model sees windows from any position in the 10 s range.

### Retrained Test Metrics (v1.07)

Targets are clean chosen-channel coordinates in raw amplitude units (A ∈ [10, 60]):

| Model | MAE | RMSE |
|---|---|---|
| RNN | 1.23 | 3.51 |
| LSTM | 1.23 | 3.39 |
| FC | 1.19 | 3.44 |

MAE rose vs. the 20 Hz baseline (~0.3) because a 10 ms window covers only ≈ 1/200 of a 0.5 Hz cycle — the network sees a near-flat slice and must extrapolate amplitude/phase from minimal curvature. The error is still ≈ 2–3 % of typical channel amplitude. This is an inherent consequence of the sample-rate spec, not a regression.

---

## 0. Development Journey

This project started with me talking to Gemini about the lecture files in Moodle, especially the RNN and LSTM material. I first tried using NotebookLM, but it gave me an error and got stuck, and I never figured out why.

After that, Gemini gave me a description of RNNs and LSTMs, which helped me build a small demo app for my own intuition. I uploaded that demo into this project as the Fourier frequency app, then asked Claude to write a description for it in the project description file.

From there, I explained to Claude the full homework requirements and what the app should do. I also gave it the INSTRUCTIONS.md file, which I had summarized with Gemini from the Moodle instructions for building the required software.

After that, I asked Claude to start building the PRD, PLAN, TODO, and the other supporting files according to INSTRUCTIONS.md and the project description. I then started developing the app with Claude Sonnet 4.6. When some of the harder parts took more than three prompts to get right, I switched to Opus 4.6.

## 1. Project Overview

The Fourier Neural Decoder is an interactive browser-based application built with Dash and PyTorch. It allows users to synthesize composite waveforms from up to 4 harmonic channels and then identify the dominant frequency class of a 1-second signal window using either a Recurrent Neural Network (RNN) or Long Short-Term Memory (LSTM) classifier.

The project was built in 18 phases following a strict TDD (Red-Green-Refactor) workflow, SDK-first architecture, and a 150-line-per-file rule.

---

## 2. Why LSTM Reached 100% Accuracy While RNN Struggled

This was the most technically significant challenge encountered during the project.

### 2.1 The Task

The classifiers receive a normalized 50-point window (1 second at 50 Hz) of a sinusoidal signal and must predict which of 4 frequency classes it belongs to:
- Class 0: 0.5 Hz (Fundamental)
- Class 1: 1.0 Hz (Second Harmonic)
- Class 2: 1.5 Hz (Third Harmonic)
- Class 3: 2.0 Hz (Fourth Harmonic)

The signal has random phase and a small amount of Gaussian noise added before normalization.

![Four frequency classes in a 1-second window](images/fig1_four_classes.png)
*Figure 1 — The 4 sinusoidal classes (0.5, 1.0, 1.5, 2.0 Hz) as seen by the classifier in a normalized 1-second window. Note that class 0 (0.5 Hz) shows only half a cycle, making it the hardest to distinguish.*

### 2.2 Why Vanilla RNN Failed

The vanilla RNN update rule is:

$$h_t = \tanh(W \cdot [x_t, h_{t-1}] + b)$$

The gradient must flow **backwards through all 50 time steps** during training. At each step, it is multiplied by the weight matrix $W$ and the derivative of $\tanh$. Since $|\tanh'| \leq 1$, repeated multiplication across 50 steps causes the gradient to shrink exponentially toward zero — the **vanishing gradient problem**.

**In practice we observed:**
- Loss pinned at **1.386** across all epochs — equal to $\ln(4)$, the theoretical loss of a model predicting all 4 classes with equal probability
- Accuracy stuck at **~25%** — identical to random guessing on a 4-class balanced dataset
- No learning signal was reaching the early time steps where frequency information is encoded

A second training run with 2 layers made things worse — stacking RNN layers compounds the vanishing gradient across depth as well as time.

![RNN training curve — stuck at random chance](images/fig2_rnn_stuck.png)
*Figure 2 — RNN training curve showing loss pinned at 1.386 (= ln(4)) and accuracy oscillating around 25% across all 150 epochs. The model never escapes random-chance behaviour.*

### 2.3 Why LSTM Succeeded

The LSTM replaces the single hidden state with a **cell state** $C_t$ that acts as a long-range memory highway, protected by three learned gates:

$$f_t = \sigma(W_f \cdot [h_{t-1}, x_t] + b_f) \quad \text{(forget gate)}$$
$$i_t = \sigma(W_i \cdot [h_{t-1}, x_t] + b_i) \quad \text{(input gate)}$$
$$C_t = f_t \odot C_{t-1} + i_t \odot \tilde{C}_t \quad \text{(cell update)}$$
$$h_t = o_t \odot \tanh(C_t) \quad \text{(output)}$$

The additive update $C_t = f_t \odot C_{t-1} + i_t \odot \tilde{C}_t$ creates a **direct gradient path** back through time that does not multiply through the same matrix repeatedly. This is why the LSTM can learn from all 50 time steps without gradient decay.

**In practice:** LSTM reached **100% accuracy** from epoch 30 onward and stayed stable through epoch 100.

![LSTM architecture — cell state and gates](images/fig3_lstm_architecture.png)
*Figure 3 — LSTM cell showing the forget gate (f), input gate (i), cell state highway (C), and output gate (o). The additive cell update is the key structural difference from vanilla RNN.*

![LSTM training curve — smooth convergence](images/fig4_lstm_convergence.png)
*Figure 4 — LSTM training curve (lr=0.0003) showing smooth loss decrease and accuracy reaching 100% by epoch 30, remaining stable through epoch 100.*

### 2.4 The Instability We Observed in Early LSTM Training

Even LSTM was not without problems. In the first training run with `lr=0.001`:

```
LSTM epoch 50/100  loss=0.7442 acc=100.00%
LSTM epoch 80/100  loss=0.7437 acc=100.00%
LSTM epoch 90/100  loss=1.2409 acc=50.88%   ← sudden collapse
LSTM epoch 100/100 loss=0.7598 acc=97.12%
```

A learning rate of 0.001 caused the optimizer to overshoot a good local minimum and temporarily collapse. This was fixed by reducing the LSTM learning rate to **0.0003**.

![LSTM instability — LR=0.001 vs LR=0.0003](images/fig5_lstm_instability.png)
*Figure 5 — Comparison of LSTM training with lr=0.001 (sudden accuracy collapse at epoch 90) vs lr=0.0003 (stable convergence). Both runs use the same architecture and data.*

### 2.5 RNN Confidently Wrong — A Real Observed Case

During app testing the following input was used:

| Channel | Frequency | Amplitude | Phase |
|---------|-----------|-----------|-------|
| Fundamental (active) | 0.5 Hz | 82 | 0 |
| Fourth Harmonic (active) | 2.0 Hz | 10 | 4.7 rad |

Window: t=1.0s · Noise: σ=0 · Algorithm: Both

**Results:**
- **LSTM: 100% Fundamental** ✅ — correct, amplitude ratio 8.2:1 is unambiguous
- **RNN: 96% Fourth Harmonic** ❌ — confidently wrong

The signal is completely unambiguous to a human: a large slow U-shape (0.5 Hz) with tiny 2 Hz ripples on top. Yet the RNN fixated on the fast ripple pattern (Fourth Harmonic) and ignored the dominant envelope entirely.

**Why this happens:** The RNN processes 50 time steps sequentially and struggles to separate the slow large envelope from the fast small ripples. With only ~69% test accuracy, the RNN gets roughly 1 in 3 predictions wrong — and when wrong, it tends to be *confidently* wrong because softmax always produces a peak probability regardless of how uncertain the model actually is.

**This is a known architectural limitation of vanilla RNN.** The LSTM's cell state allows it to simultaneously track slow and fast components of the signal. The RNN's single hidden state cannot maintain this multi-scale temporal memory.

**Practical recommendation: always use LSTM for reliable identification.** The RNN is included for educational comparison, not production use.

### 2.6 Summary Table

| Property | RNN | LSTM |
|----------|-----|------|
| Gradient flow | Multiplicative — vanishes over 50 steps | Additive cell state — preserves gradient |
| Final accuracy (composite signals) | ~69% | ~89% |
| Training stability | Oscillates — requires best-checkpoint saving | Stable with LR ≤ 0.0003 |
| Confident wrong predictions | Common (~31% of cases) | Rare |
| Parameters | Fewer | ~4× more (3 gates + cell state) |
| Suitable for production use | No | Yes |

---

## 3. Problems Encountered During Neural Network Training

### 3.1 Exploding Gradients (RNN)

**Problem:** Even with gradient clipping added (`clip_grad_norm_`, max_norm=1.0), the vanilla RNN oscillated between learning and forgetting — reaching 83% at epoch 130 then collapsing back to 24% at epoch 150.

**Root cause:** The learning rate was still high enough to jump out of a good local minimum late in training.

**Fix applied:**
- Added `StepLR` scheduler: LR halves every 40 epochs (`0.001 → 0.0005 → 0.00025 → 0.000125`)
- Added **best model saving**: track the highest validation accuracy during training and save those weights — not the last epoch weights

**Before fix:** saved weights had 24% accuracy despite 83% being reached mid-training.
**After fix:** always saves the best checkpoint.

![RNN oscillation — best checkpoint vs last epoch](images/fig6_rnn_best_checkpoint.png)
*Figure 6 — RNN training curve showing accuracy reaching 83% at epoch 130 then collapsing to 24% at epoch 150. The red marker shows the saved checkpoint before the fix (epoch 150, 24%); the green marker shows the saved checkpoint after the fix (epoch 130, 83%).*

### 3.2 Noise Level — Finding the Right Balance

**Problem:** Training data with `noise_std=0.15` was too noisy for the 1-second window. A 0.5 Hz signal in a 1-second window shows only half a cycle — adding 15% noise on top of that made the frequency nearly indistinguishable.

**First fix:** Reduced `noise_std` from 0.15 → 0.05.
**Final value:** Increased back to **0.1** — see section 3.2a below for the full reasoning.

![Effect of noise on a 0.5 Hz signal in a 1-second window](images/fig7_noise_comparison.png)
*Figure 7 — A 0.5 Hz signal (only 0.5 cycles visible) with noise_std=0.0 (clean), noise_std=0.1 (final training value), and noise_std=0.5 (heavy — app slider maximum). At 0.5, the half-cycle shape is unrecognizable to both human and model.*

### 3.2a Why We Train With Noise — But Not Too Much

The app exposes a **Noise slider (σ = 0.0 – 0.5)** that adds Gaussian noise to the window before ML inference. A natural question is: why not train with heavy noise (e.g., `noise_std=0.4`) so the model handles the full slider range?

**The train-inference distribution must match.**

If we train with `noise_std=0.4`, the model learns to classify heavily corrupted signals. But when the user sets the slider to 0.0 (clean signal), the model receives a smooth waveform it was never trained on at that scale — predictions become unreliable on the most common use case.

**The noise slider is for robustness testing, not normal use.**

The slider exists to demonstrate and explore how much noise the model can tolerate before failing. It is not expected to be at 0.5 during normal operation. Training at `noise_std=0.1` means:

| Slider value | Model behaviour |
|-------------|----------------|
| σ = 0.0 (Clean) | Slightly easier than training — very high confidence |
| σ = 0.1 (Light) | Matches training distribution — best accuracy |
| σ = 0.3 (Medium) | Harder than training — accuracy degrades gradually |
| σ = 0.5 (Heavy) | Far outside training distribution — predictions unreliable |

**Why `noise_std=0.1` specifically (not 0.05 or 0.2)?**

- `0.05` is so small it barely acts as regularization — the model can still memorize exact waveform shapes
- `0.1` corrupts the signal enough to force the model to learn the underlying frequency pattern, not individual sample values
- `0.15+` starts destroying the half-cycle shape of the 0.5 Hz class, which is the hardest class to identify

**`noise_std=0.1` is the largest value that keeps the 0.5 Hz class learnable while providing meaningful regularization.**

### 3.3 Dataset Too Small

**Problem:** The original training set of 1,000 samples (250 per class) was insufficient for generalization, especially with random phase.

**Fix:** Increased to **4,000 samples** (1,000 per class).

### 3.4 Non-Reproducible Training

**Problem:** Each training run produced different model weights because the data generation used no fixed seed. Running `train_rnn()` then `train_lstm()` generated two different datasets.

**Fix:** Added `"seed": 42` to `training_config.json`. Both models now train on identical data.

### 3.5 Hardcoded Model Hyperparameters in UI

**Problem:** The `callbacks_identify.py` file contained:
```python
RNNClassifier({"hidden_size": 64, "num_layers": 1, ...})
LSTMClassifier({"hidden_size": 128, "num_layers": 2, "dropout": 0.3, ...})
```
These values were hardcoded in the UI layer, violating the INSTRUCTIONS.md hardcoding ban. Any change to the model architecture required a code edit.

**Fix:** Added `rnn_config` and `lstm_config` to `app_config.json`. The UI now reads:
```python
rnn_cfg = {**app_cfg.get("rnn_config", {}), "weights_path": ...}
```

### 3.6 Stale Weights After Architecture Change

**Problem:** After changing `app_config.json` from `hidden_size=64` to `hidden_size=128`, the old `.pt` files were still on disk. The state dict validation (added during code review) correctly detected the mismatch and raised:
```
ValueError: Corrupted model weights — missing keys: {'rnn.weight_ih_l1', ...}
```
But integration tests were failing because they hardcoded the old architecture.

**Fix:** Updated integration tests to read model architecture from `app_config.json` via `configs["app"]["rnn_config"]`, making them architecture-agnostic.

---

## 4. Problems Encountered During App Development

### 4.1 `callbacks_server.py` Exceeded 150-Line Limit

**Problem:** The file grew to 198 lines as more callbacks were added, violating the INSTRUCTIONS.md 150-line rule.

**Fix:** Split into three files:
- `callbacks_server.py` — registration hub (toggle, reset, noise label, C vector)
- `callbacks_identify.py` — identify callback + pure `_run_identify` logic
- `callbacks_result.py` — rendering helpers (`_build_single_result_panel`, `_build_diff_summary`)

### 4.2 Dash Callbacks Were Untestable

**Problem:** All callback logic was defined inside nested closures within `_register_*` functions. This made it impossible to import and test the logic directly.

**Fix:** Extracted all logic into module-level pure functions (`toggle_wave_fn`, `toggle_sr_fn`, `update_vector_fn`, `reset_cb_fn`, `compute_channel_vector`, `_run_identify`). The registered callbacks delegate to these functions. This allowed direct unit testing without needing a running Dash server.

### 4.3 ThreadPoolExecutor Caused Non-Deterministic PyTorch Inference

**Problem:** The gatekeeper's timeout mechanism was implemented using `concurrent.futures.ThreadPoolExecutor`. Running PyTorch inference in a background thread introduced non-determinism — the same model returned different class predictions depending on thread scheduling.

**Fix:** Replaced with a soft timeout: run inference in the main thread, measure elapsed time, and log a warning if it exceeds the configured `timeout_seconds`. True hard-kill timeout is not cross-platform on Windows without OS-level signals.

### 4.4 Windows Encoding Issue in Tests

**Problem:** `test_version_consistency` failed with `UnicodeDecodeError: 'charmap' codec can't decode byte 0x9c` on Windows. The README.md contains UTF-8 characters (em-dashes) that the Windows default encoding (cp1255) could not read.

**Fix:** Added `encoding="utf-8"` to `readme_path.read_text()`.

### 4.5 `Store` Import Path

**Problem:** Tried to import `Store` directly from `dash`:
```python
from dash import dcc, html, Store  # fails
```
**Fix:** `dcc.Store` is the correct path — `Store` lives under `dash.dcc`, not the top-level `dash` module.

### 4.6 One-Hot Channel Vector C

**Problem:** The clientside JavaScript callback originally took 4 separate `enabled-{i}` checklist values as inputs (25 total inputs). There was no unified representation of which channels were active.

**Solution:** Introduced a binary vector **C = [c₀, c₁, c₂, c₃]** where cᵢ ∈ {0, 1}:
- Stored in `dcc.Store(id="channel-vector", data=[1,1,1,1])`
- Computed server-side by `compute_channel_vector()` from the 4 checklists
- Consumed by the clientside JS as a single input: `if (!C || C[i] !== 1) continue`
- Reduced JS callback inputs from 25 → 22

![Channel vector C data flow](images/fig8_channel_vector_C.png)
*Figure 8 — Data flow of the channel vector C: four enabled-{i} checklists → server callback compute_channel_vector() → dcc.Store("channel-vector") → clientside JS checks C[i] !== 1 to skip disabled channels.*

---

## 5. What Went Well

### 5.1 LSTM Architecture
The 2-layer LSTM with hidden_size=128 and dropout=0.2 achieved 100% accuracy on the synthetic dataset from epoch 30 onward. The gating mechanism makes it inherently well-suited for the frequency classification task.

![App UI screenshot — full layout](images/fig9_app_screenshot.png)
*Figure 9 — The running application: sidebar with 4 wave panels (frequency, amplitude, phase, dots/sampling controls), overlay chart, summation chart with amber window highlight, noise slider, algorithm selector, and ML result panel.*

### 5.2 SDK-First Design
Separating all business logic into `src/fourier/sdk/` made every component independently testable. The UI layer only calls SDK methods. This design decision made the 96% test coverage achievable without needing a running Dash server for most tests.

### 5.3 Config-Driven Everything
Externalizing all hyperparameters, paths, and limits to JSON files (`app_config.json`, `rate_limits.json`, `training_config.json`) meant architectural changes (e.g., switching from 64→128 hidden size) required only a config edit, not source changes.

### 5.4 Gatekeeper Pattern
Routing all ML inference through `ModelGatekeeper` gave centralized rate limiting, retry logic, and logging with no changes required in the classifiers or UI. When the timeout mechanism was initially broken (ThreadPoolExecutor), it was fixed in one place.

### 5.5 State Dict Validation
Adding key validation before `load_state_dict()` caught the architecture mismatch immediately with a clear error message instead of a cryptic PyTorch RuntimeError. This saved significant debugging time when the model architecture was changed.

### 5.6 Best Model Checkpoint
Saving the best validation checkpoint (`copy.deepcopy` of weights at peak accuracy) rather than the final epoch proved critical — the RNN reached 83% at epoch 130 then collapsed to 24% at epoch 150. Without this fix the saved model would have been the useless 24% version.

---

## 6. Lessons Learned

| # | Lesson |
|---|--------|
| 1 | **Vanilla RNN is practically unusable for sequences longer than ~20 steps** — always prefer LSTM or GRU for real tasks |
| 2 | **Save the best checkpoint, not the last epoch** — training loss/accuracy can oscillate and the final state is often not the best |
| 3 | **Learning rate schedulers are not optional for RNN training** — a fixed LR will eventually overshoot a good minimum |
| 4 | **Noise level must match window length** — a 0.5 Hz signal in a 1-second window shows only half a cycle; 15% noise destroys frequency information |
| 5 | **ThreadPoolExecutor + PyTorch = non-determinism on Windows** — CPU-bound ML inference should stay in the main thread |
| 6 | **Testability requires pure functions** — Dash callback closures cannot be imported or called directly; always extract the logic |
| 7 | **Config-driven hyperparameters pay off immediately** — the first time you need to change an architecture, you're glad the values are in JSON |
| 8 | **Integration tests should be architecture-agnostic** — hardcoding `hidden_size=64` in tests means every model update breaks them |

---

## 7. Design Decision (v1.06): Network Depth — Why We Stayed at 1 Hidden Layer

After all three regressors (RNN, LSTM, FC) were trained and showed they had hit an accuracy floor at normalised MAE ≈ 0.19, I asked whether we should add more layers to push accuracy higher. The recommendation was **no**, and we agreed to stop at 1 hidden layer + 1 output layer for each model.

The reasoning, recorded here so the choice is defensible:

1. **The bottleneck is not capacity.** All three models reach the same plateau despite very different parameter counts (FC ~1.6 K, RNN ~5.1 K, LSTM ~18 K). If capacity were the limit, the LSTM would beat the FC — instead it slightly loses. The signal-extraction problem is information-bound, not parameter-bound.

2. **An earlier capacity bump produced *worse* results.** Pass 3 of the regressor training (H=128, 250 epochs, 12 K samples) finished with a higher LSTM MAE (0.232) than the smaller Pass 4 (H=64, 150 epochs, 6 K samples → MAE 0.203). Adding parameters had already been tried in spirit and made things worse, presumably from over-regularisation and harder optimisation.

3. **Comparison cleanliness.** Keeping all three models at identical depth (2 layers — one hidden, one output) means any accuracy difference reflects only the cell type (RNN cell vs LSTM cell vs ReLU perceptron). Stacking would muddy that comparison.

4. **The "loss" to Fourier is the educational point.** No matter how many layers we stack, a closed-form projection that knows the channel frequencies will keep winning. Showing that 1-layer recurrent networks already plateau against the closed-form baseline is a stronger lesson than showing that a tuned 3-layer model gets marginally closer.

5. **Real performance gains live elsewhere.** The honest list of changes that *would* help — more training data, longer windows, predicting (amplitude, phase) instead of 10 raw coordinates, exposing channel frequencies as input features — none of these are about depth.

The depth decision was made deliberately, with all three models at depth 2, hidden width 64, and the same training pipeline. The trade-off (slightly higher MAE in exchange for clean comparability and faithfulness to the textbooks) is documented here so a future reader doesn't read "1 layer" as carelessness.
