# Feature PRD — LSTM Regressor (Book-Faithful)

**Version:** 1.07
**Status:** Implemented + trained (v1.07: 1 kHz training, parametric α/β noise)
**Reference:** `concepts/LSTM-book.pdf` §6.1

---

## 1. Problem Statement

Same task as `PRD_RNN.md`: given a 10-sample summation window and a one-hot C vector, regress the 10 coordinates of the chosen channel's pure wave. The LSTM is the "gated recurrence" counterpart that the textbook introduces as the solution to vanilla-RNN gradient problems. Running both lets the user compare a simple recurrent regressor against a gated one on the same task.

## 2. Functional Requirements

| ID | Requirement |
|----|-------------|
| LSTM-FR-01 | `BookLSTMRegressor(nn.Module)` exposes `W_f`, `W_i`, `W_C`, `W_o` and biases `b_f`, `b_i`, `b_C`, `b_o` as **separate** `nn.Parameter`s (no fused tensor). |
| LSTM-FR-02 | Input per timestep = `[sample_t, C_0, C_1, C_2, C_3]`. The concatenated input to gates is `z_t = [h_{t-1}, x_t]`. |
| LSTM-FR-03 | Gate equations follow book §6.1: `f_t = σ(W_f·z + b_f)`, `i_t = σ(W_i·z + b_i)`, `C̃_t = tanh(W_C·z + b_C)`, `o_t = σ(W_o·z + b_o)`. |
| LSTM-FR-04 | Cell-state update by **addition** (Eq. 4.3): `C_t = f_t ⊙ C_{t-1} + i_t ⊙ C̃_t`. Hidden state: `h_t = o_t ⊙ tanh(C_t)`. |
| LSTM-FR-05 | Forget-gate bias initialised to **1.0**; other gate biases at 0.0. |
| LSTM-FR-06 | Output: `y = W_y · h_T + b_y` ∈ ℝ^10. **No softmax** (regression). |
| LSTM-FR-07 | Same training and inference normalisation pipeline as the RNN regressor. |
| LSTM-FR-08 | `nn.LSTM` is forbidden in this codebase. |

## 3. Architecture (concatenated form)

```
For each t = 0..9:
    z = [h_{t-1}, sample_t, C_0..C_3]                       ∈ ℝ^(H+5)
    f = σ(W_f · z + b_f)                                    forget gate
    i = σ(W_i · z + b_i)                                    input gate
    C̃ = tanh(W_C · z + b_C)                                 candidate values
    o = σ(W_o · z + b_o)                                    output gate
    C_t = f ⊙ C_{t-1} + i ⊙ C̃                               cell-state highway (addition!)
    h_t = o ⊙ tanh(C_t)                                     hidden state
y = W_y · h_T + b_y                                          regression output ∈ ℝ^10
```

## 4. Training Setup

Identical to the RNN regressor (same `_generate_dataset`, same MSE, same normalisation, same hyperparameters in `config/training_config.json["lstm"]`). See `PRD_RNN.md §4` for the full training spec — 1 kHz sample rate, random window start in [0, 9.99 s), parametric α/β noise per channel, clean target. Apples-to-apples: any prediction divergence reflects only the architectural difference (gated vs. plain recurrence).

## 5. Out of Scope

- GRU, multi-layer stacks, dropout, bidirectional variants.
- Per-step regression outputs.
