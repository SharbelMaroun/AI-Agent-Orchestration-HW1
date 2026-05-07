# Feature PRD — Fully Connected (FC) Regressor

**Version:** 1.07
**Status:** Implemented + trained (v1.07: 1 kHz training, parametric α/β noise)
**Reference:** No textbook PDF — standard 2-layer MLP, included as a non-recurrent **baseline** for comparison against the RNN and LSTM regressors.

---

## 1. Problem Statement

Same task as `PRD_RNN.md` and `PRD_LSTM.md`: given a 10-sample summation window and a one-hot C vector, regress the 10 coordinates of the chosen channel's pure wave. The FC is included to test whether recurrence actually helps on this task — it sees the entire window at once as a flat vector, with no notion of temporal order.

## 2. Functional Requirements

| ID | Requirement |
|----|-------------|
| FC-FR-01 | `BookFCRegressor(nn.Module)` exposes `W_1`, `b_1`, `W_2`, `b_2` as explicit `nn.Parameter`s. |
| FC-FR-02 | The forward pass shall flatten the 10-sample window and concatenate the 4-d C one-hot, producing a single 14-d input vector. |
| FC-FR-03 | The FC shall **not** loop over time — no recurrence, no hidden state across timesteps. |
| FC-FR-04 | Activation: **ReLU** (Kaiming-style initialisation appropriate for ReLU). |
| FC-FR-05 | Output: 10 real-valued coordinates (no softmax — regression). |
| FC-FR-06 | Same training pipeline as RNN/LSTM: shared `_generate_dataset`, `nn.MSELoss`, per-sample amplitude normalisation. |
| FC-FR-07 | Inference applies the same per-sample normalisation as the RNN/LSTM regressors. |
| FC-FR-08 | If `weights/fc_regressor.pt` is absent, model loads with random weights and the UI still renders. |

## 3. Architecture

```
samples ∈ ℝ^(B×10)  ──┐
                      ├── concat → x ∈ ℝ^14  →  W_1, b_1 → ReLU
C ∈ ℝ^(B×4)          ──┘                                  ↓
                                            hidden ∈ ℝ^64
                                                          ↓
                                                  W_2, b_2 → output ∈ ℝ^10
```

- 2 layers (1 hidden + 1 output)
- ~1.6 K parameters (vs ~5.1 K for RNN, ~18 K for LSTM at H=64)
- Inference latency: ≪ 1 ms (no time loop)

## 4. Architectural Comparison

| Property | RNN | LSTM | **FC** |
|---|---|---|---|
| Sees input as | sequence of 10 scalars | sequence of 10 scalars | **single 14-D vector** (10 + 4) |
| Recurrence | yes (`h_t ← h_{t-1}`) | yes + cell state | **no** |
| Activation | tanh | sigmoid (gates) + tanh | **ReLU** |
| Layers | 1 recurrent + 1 output | 1 LSTM + 1 output | **1 hidden + 1 output** |
| Parameters (H = 64) | ~5.1 K | ~18 K | **~1.6 K** |
| Sensitive to time-order? | yes | yes | **no — permuting the 10 samples gives same output** |

The FC's permutation-invariance is its weakness for time-series tasks — it cannot use temporal order. That's also exactly what makes it the right baseline: if recurrent models can't beat the FC on this task, recurrence isn't earning its parameters.

## 5. Out of Scope

- Multi-hidden-layer / convolutional variants.
- Dropout or batch normalisation (small enough that overfitting hasn't been observed).
