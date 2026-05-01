# Feature PRD — LSTM Classifier
**Version:** 1.00 | **Parent PRD:** PRD.md (FR-07) | **Owner:** sharbelm

---

## 1. Problem

Same task as the RNN classifier (FR-06): given a normalized 50-point, 1-second window from the composite summation signal, identify the dominant harmonic channel (1 of 4). The LSTM is offered as a second, stronger algorithm because its gated cell state can better capture the periodic structure of sine waves over the 50-step sequence, especially when harmonic frequencies are close together (e.g., 0.5 Hz vs. 1.0 Hz).

---

## 2. Algorithm Description

Based on `LSTM.md`. At every time step $t$, four gates operate on the input $x_t$ and previous hidden state $h_{t-1}$:

$$f_t = \sigma(W_f \cdot [h_{t-1}, x_t] + b_f) \quad \text{(Forget Gate)}$$
$$i_t = \sigma(W_i \cdot [h_{t-1}, x_t] + b_i) \quad \text{(Input Gate)}$$
$$\tilde{C}_t = \tanh(W_c \cdot [h_{t-1}, x_t] + b_c) \quad \text{(Cell Candidate)}$$
$$C_t = f_t \odot C_{t-1} + i_t \odot \tilde{C}_t \quad \text{(Cell State Update)}$$
$$o_t = \sigma(W_o \cdot [h_{t-1}, x_t] + b_o) \quad \text{(Output Gate)}$$
$$h_t = o_t \odot \tanh(C_t) \quad \text{(Hidden State)}$$

Two LSTM layers are stacked; dropout is applied between layers.

---

## 3. Functional Requirements

| ID | Requirement |
|----|-------------|
| LSTM-FR-01 | `LSTMClassifier.__init__` loads weights from path in `config/app_config.json` (key: `lstm_model_path`). No hardcoded path. |
| LSTM-FR-02 | `LSTMClassifier.process(window: np.ndarray) -> dict` accepts shape `(50,)`, returns `{"class": int, "confidence": float, "probabilities": list[float]}`. |
| LSTM-FR-03 | `LSTMClassifier._validate_config()` raises `ValueError` if model file is missing or config key absent. |
| LSTM-FR-04 | Both cell state $C_0$ and hidden state $h_0$ initialized to zeros per call (stateless per request). |
| LSTM-FR-05 | Normalization to `[−1, 1]` handled upstream by `WindowExtractor`. |
| LSTM-FR-06 | All inference calls routed through `ModelGatekeeper`. |
| LSTM-FR-07 | File `src/fourier/sdk/lstm_classifier.py` must not exceed 150 lines. |

---

## 4. Model Architecture

```
Input  →  (1, 50, 1)
LSTM Layer 1  hidden_size=128, num_layers=1
Dropout(p=0.3)
LSTM Layer 2  hidden_size=128, num_layers=1
Final h_50  →  (1, 128)
Dropout(p=0.3)
Linear(128 → 4)
Softmax
Output  →  (4,) probabilities
```

**Parameter count per LSTM layer:**
$$4 \times (d_{input} \times d_{hidden} + d_{hidden}^2 + d_{hidden})$$

- Layer 1: $4 \times (1 \times 128 + 128^2 + 128) = 4 \times 16,512 = 66,048$
- Layer 2: $4 \times (128 \times 128 + 128^2 + 128) = 4 \times 16,512 = 66,048$
- FC: $128 \times 4 + 4 = 516$
- **Total: ~132,612 parameters**

---

## 5. Training

| Setting | Value |
|---------|-------|
| Framework | PyTorch |
| Optimizer | Adam, lr=0.001 |
| Loss | CrossEntropyLoss |
| Epochs | 200 |
| Batch size | 64 |
| Dropout | 0.3 between LSTM layers |
| Training samples | 10,000 (2,500 per class, balanced) |
| Data generation | Same synthetic dataset as RNN (shared `DatasetGenerator` class) |
| Train/val/test split | 70 / 15 / 15 |
| Weight output | `models/lstm_classifier.pt` |

**Tuning guidance (from `LSTM.md`):**
- Hidden size: 128 (per recommendation: start at 128–256)
- Layers: 2 stacked LSTM layers (within the 1–3 recommendation)
- Regularization: Dropout 0.3 between layers (within 0.2–0.5 range)

---

## 6. Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| LSTM-NFR-01 | Inference latency (CPU) | < 1,000 ms |
| LSTM-NFR-02 | Test accuracy on held-out set | ≥ 93% |
| LSTM-NFR-03 | Accuracy improvement over RNN | ≥ +3 pp |
| LSTM-NFR-04 | Unit test coverage for this module | ≥ 85% |
| LSTM-NFR-05 | Zero Ruff violations | 0 errors |

---

## 7. Failure Modes & Mitigations

| Failure | Mitigation |
|---------|-----------|
| Model file missing at startup | `_validate_config()` raises with clear message; app shows error banner |
| Input window length ≠ 50 | `process()` raises `ValueError` |
| Overfitting (val loss diverges from train loss) | Increase dropout to 0.5; add weight decay 1e-4 to Adam |
| Low confidence (< 40% max probability) | Result panel flags "Low Confidence" warning |
| Inference too slow on CPU | Reduce hidden_size to 64; reduce to 1 LSTM layer |

---

## 8. Comparison with RNN (Diff Display — FR-08)

When Both mode is selected, `ResultComparator.process()` computes and returns:

| Field | Computation |
|-------|-------------|
| `agreement` | `lstm_class == rnn_class` |
| `confidence_delta` | `lstm_confidence − rnn_confidence` (percentage points) |
| `top_class_diff` | Side-by-side probabilities for the winning class |
| `runner_up_diff` | Second-highest class from each model |
| `disagreement_warning` | True if `agreement == False` |

---

## 9. Definition of Done

- [ ] `tests/test_lstm_classifier.py` covers `__init__`, `process()`, `_validate_config()`, and edge cases.
- [ ] `uv run pytest tests/test_lstm_classifier.py` passes with ≥ 85% coverage.
- [ ] `uv run ruff check src/fourier/sdk/lstm_classifier.py` exits 0.
- [ ] `models/lstm_classifier.pt` committed with ≥ 93% test-set accuracy.
- [ ] File length ≤ 150 lines.
- [ ] LSTM accuracy ≥ RNN accuracy + 3 pp on shared test set.
