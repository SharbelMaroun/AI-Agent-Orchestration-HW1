# Feature PRD — RNN Classifier
**Version:** 1.00 | **Parent PRD:** PRD.md (FR-06) | **Owner:** sharbelm

---

## 1. Problem

Given a 1-second window of a composite signal (sum of up to 4 sine waves), identify which of the 4 harmonic channels is the **most dominant** contributor in that window. A plain RNN is the first candidate algorithm due to its simplicity and suitability for short fixed-length sequences.

---

## 2. Algorithm Description

Based on `RNN.md`. At every time step $t$:

$$h_t = \tanh(W \cdot [x_t,\ h_{t-1}] + b)$$

- $x_t$: normalized amplitude at sample $t$ (scalar, 1 feature)
- $h_{t-1}$: previous hidden state vector (size 64)
- $W$: shared weight matrix — identical for every step
- $b$: bias vector
- Activation: **Tanh** (zero-centered, stable gradients)

The final hidden state $h_{50}$ is passed through a fully-connected layer to produce 4 logits, then softmax to get class probabilities.

---

## 3. Functional Requirements

| ID | Requirement |
|----|-------------|
| RNN-FR-01 | `RNNClassifier.__init__` loads weights from path specified in `config/app_config.json` (key: `rnn_model_path`). No hardcoded path. |
| RNN-FR-02 | `RNNClassifier.process(window: np.ndarray) -> dict` accepts a shape `(50,)` float array, returns `{"class": int, "confidence": float, "probabilities": list[float]}`. |
| RNN-FR-03 | `RNNClassifier._validate_config()` raises `ValueError` if model file is missing or config key is absent. |
| RNN-FR-04 | Hidden state initialized to zeros at every call (stateless per request). |
| RNN-FR-05 | Input is normalized to `[−1, 1]` before being fed to the model (handled by `WindowExtractor`, not the classifier). |
| RNN-FR-06 | All inference calls are routed through `ModelGatekeeper` for rate limiting and logging. |
| RNN-FR-07 | File `src/fourier/sdk/rnn_classifier.py` must not exceed 150 lines. |

---

## 4. Model Architecture

```
Input  →  (1, 50, 1)
RNN Layer  hidden_size=64, activation=tanh, weight-shared
Final h_50  →  (1, 64)
Linear(64 → 4)
Softmax
Output  →  (4,) probabilities
```

**Parameter count:**
- $W$: shape $(64, 64 + 1)$ = 4,160 weights
- $b$: 64 biases
- FC: $64 \times 4 + 4 = 260$
- **Total: ~4,484 parameters**

---

## 5. Training

| Setting | Value |
|---------|-------|
| Framework | PyTorch |
| Optimizer | Adam, lr=0.001 |
| Loss | CrossEntropyLoss |
| Epochs | 200 |
| Batch size | 64 |
| Training samples | 10,000 (2,500 per class, balanced) |
| Data generation | Synthetic sine waves ± 0.05 Hz frequency jitter + Gaussian noise σ=0.05 |
| Train/val/test split | 70 / 15 / 15 |
| Weight output | `models/rnn_classifier.pt` |

---

## 6. Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| RNN-NFR-01 | Inference latency (CPU) | < 500 ms |
| RNN-NFR-02 | Test accuracy on held-out set | ≥ 90% |
| RNN-NFR-03 | Unit test coverage for this module | ≥ 85% |
| RNN-NFR-04 | Zero Ruff violations | 0 errors |

---

## 7. Failure Modes & Mitigations

| Failure | Mitigation |
|---------|-----------|
| Model file missing at startup | `_validate_config()` raises with clear message; app shows error banner |
| Input window length ≠ 50 | `process()` raises `ValueError` with expected vs. actual shape |
| All classes near equal probability (< 40% max) | Result panel flags "Low Confidence — result may be unreliable" |
| Gradient vanishing during training | Use Tanh (zero-centered); if accuracy < 80% after 200 epochs, fall back to LSTM |

---

## 8. Definition of Done

- [ ] `tests/test_rnn_classifier.py` covers `__init__`, `process()`, `_validate_config()`, and edge cases.
- [ ] `uv run pytest tests/test_rnn_classifier.py` passes with ≥ 85% coverage.
- [ ] `uv run ruff check src/fourier/sdk/rnn_classifier.py` exits 0.
- [ ] `models/rnn_classifier.pt` committed with ≥ 90% test-set accuracy.
- [ ] File length ≤ 150 lines.
