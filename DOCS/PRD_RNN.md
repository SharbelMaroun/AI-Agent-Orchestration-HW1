# Feature PRD — RNN Regressor (Book-Faithful)

**Version:** 1.07
**Status:** Implemented + trained (v1.07: 1 kHz training, parametric α/β noise)
**Reference:** `concepts/RNN-BOOK.pdf` (Dr. Segal Yoram, 2025), Eq. 2.13–2.14

---

## 1. Problem Statement

Given a length-10 window of summation samples and a length-4 one-hot vector `C` indicating which of the 4 known channels to extract, a manual book-faithful Elman RNN shall **regress the 10 coordinates** of the chosen channel's pure wave at the same time points. This is the "neural-network counterpart" of the deterministic Fourier projection: same input, same target, different algorithm.

## 2. Functional Requirements

| ID | Requirement |
|----|-------------|
| RNN-FR-01 | `BookRNNRegressor(nn.Module)` exposes `W_x`, `W_h`, `b`, `W_y`, `b_y` as explicit `nn.Parameter`s. |
| RNN-FR-02 | Input width = 1 (sample) + 4 (C one-hot) = 5. The C vector is concatenated to each timestep. |
| RNN-FR-03 | The recurrence follows book Eq. 2.13–2.14: `z_t = W_x · x_t + W_h · h_{t-1} + b`, `h_t = tanh(z_t)`. |
| RNN-FR-04 | The same `W_x`, `W_h`, `b` are reused at every time step (weight sharing — Ch. 4). |
| RNN-FR-05 | Output: `y = W_y · h_T + b_y` ∈ ℝ^10. **No softmax** — this is a regression head, not a classifier. |
| RNN-FR-06 | Training loss: `nn.MSELoss` on per-sample-amplitude-normalised data. |
| RNN-FR-07 | Inference: input is normalised by its own `max(|samples|)`; the model output is multiplied back to original scale. |
| RNN-FR-08 | If `weights/rnn_regressor.pt` is absent, the model loads with random weights and the UI still renders. |

## 3. Architecture

```
samples ∈ ℝ^(B×10×1) ──┐
                       ├── concat → x_t ∈ ℝ^5  →  for t = 0..9:
C ∈ ℝ^(B×4) (broadcast)│                          z_t = W_x·x_t + W_h·h_{t-1} + b
                       │                          h_t = tanh(z_t)
                       └─                       → y = W_y·h_10 + b_y ∈ ℝ^10  (regression)
```

## 4. Training Setup

- **Sample rate:** `ID_MODE_SR = 1000 Hz`. The full 10-second display contains 10 001 samples; each training example is a **10-sample slice (10 ms)** of the noisy summation.
- **Random window start:** for each example, `n_start ~ Uniform{0, …, 10000−10}`. The model must learn to extract the chosen channel from any 10-sample slice anywhere in the 10 s range — not just at t = 0.
- **Parametric noise (per channel, per example):** independent draws α ~ Uniform(0, `alpha_train_max`), β ~ Uniform(0, `beta_train_max`), ε ~ Uniform(−1, +1). The summation uses the perturbed channels:
  $$y_k(t) = (A_k + \alpha_k A_k \varepsilon_k)\,\sin(2\pi f_k t + \varphi_k + \beta_k\pi\varepsilon_k)$$
- **Target = clean (un-perturbed) chosen channel** at the same `t_grid`. The model therefore learns to *denoise* — recovering the ideal sine even when the input window is parametrically jittered.
- Random `(A_k, φ_k)` per channel (frequencies fixed at the 4 ID_MODE_SIGNALS values).
- Per-sample amplitude normalisation: divide both summation and target by `max(|summed|)`.
- Optimiser: Adam, `lr = 0.005`, gradient-clip at 1.0.
- Hidden size: 64.
- Epochs: 150, batch size 64, 6 000 examples (80/20 train/test).

## 5. Out of Scope

- Bidirectional / multi-layer RNN.
- GRU.
- Per-step output (we use only the final hidden state).
