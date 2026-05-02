# TODO — Fourier Frequency App (Neural Signal Decoder)
**Version:** 1.00 | **Workflow:** Red → Green → Refactor (TDD)
**Starting from zero — every task below must be completed to ship v1.00**

---

## Phase 0 · Project Scaffold

| # | Task | Definition of Done |
|---|------|--------------------|
| 0.01 | [x] Run `uv init fourier-freq-app` | `pyproject.toml` created by uv |
| 0.02 | [x] Verify `pyproject.toml` was created | File exists at project root |
| 0.03 | [x] Run `uv sync` | `.venv/` directory created |
| 0.04 | [x] Verify `.venv/` exists | Directory present |
| 0.05 | [x] Create `src/` directory | Directory present |
| 0.06 | [x] Create `src/fourier/` package directory | Directory present |
| 0.07 | [x] Create `src/fourier/__init__.py` | File exists and is importable |
| 0.08 | [x] Create `src/fourier/sdk/` directory | Directory present |
| 0.09 | [x] Create `src/fourier/sdk/__init__.py` | File exists |
| 0.10 | [x] Create `src/fourier/services/` directory | Directory present |
| 0.11 | [x] Create `src/fourier/services/__init__.py` | File exists |
| 0.12 | [x] Create `src/fourier/shared/` directory | Directory present |
| 0.13 | [x] Create `src/fourier/shared/__init__.py` | File exists |
| 0.14 | [x] Create `src/fourier/ui/` directory | Directory present |
| 0.15 | [x] Create `src/fourier/ui/__init__.py` | File exists |
| 0.16 | [x] Create `tests/` directory | Directory present |
| 0.17 | [x] Create `tests/__init__.py` | File exists |
| 0.18 | [x] Create `tests/unit/` directory | Directory present |
| 0.19 | [x] Create `tests/unit/__init__.py` | File exists |
| 0.20 | [x] Create `tests/integration/` directory | Directory present |
| 0.21 | [x] Create `tests/integration/__init__.py` | File exists |
| 0.22 | [x] Create `config/` directory | Directory present |
| 0.23 | [x] Create `models/` directory | Directory present |
| 0.24 | [x] Create `notebooks/` directory | Directory present |
| 0.25 | [x] Add `[project]` metadata section to `pyproject.toml` | name, version, description, requires-python present |
| 0.26 | [x] Add runtime dependencies to `pyproject.toml` | dash, plotly, numpy, torch, python-dotenv listed |
| 0.27 | [x] Add dev dependencies to `pyproject.toml` | pytest, pytest-cov, ruff listed |
| 0.28 | [x] Add `[tool.ruff]` section to `pyproject.toml` | line-length=120, select=["E","F","W"] configured |
| 0.29 | [x] Add `[tool.pytest.ini_options]` to `pyproject.toml` | testpaths=["tests"], addopts="--tb=short" configured |
| 0.30 | [x] Add `[tool.coverage.run]` to `pyproject.toml` | source=["src/fourier"], omit=["*/tests/*"] configured |
| 0.31 | [x] Create `.gitignore` | `.env`, `.venv/`, `__pycache__/`, `*.pt`, `.coverage` listed |
| 0.32 | [x] Create `.env-example` with dummy keys | `FOURIER_DEBUG=false`, `FOURIER_HOST=127.0.0.1`, `FOURIER_PORT=8050` |
| 0.33 | [x] Verify `uv run ruff check src/` runs without error on empty package | Exit code 0 |
| 0.34 | [x] Verify `uv run pytest` runs without error on empty test suite | Exit code 0 |

---

## Phase 1 · Shared Layer — Types, Constants, Version

| # | Task | Definition of Done |
|---|------|--------------------|
| 1.01 | [x] Create `src/fourier/shared/version.py` | File contains `VERSION = "1.00"` |
| 1.02 | [x] Write test: `from fourier.shared.version import VERSION` succeeds | Test passes |
| 1.03 | [x] Write test: `VERSION == "1.00"` | Test passes |
| 1.04 | [x] Create `src/fourier/shared/constants.py` — define `RESOLUTION = 500` | Constant present |
| 1.05 | [x] Add `DURATION = 10` to constants.py | Constant present |
| 1.06 | [x] Add `PI2 = 2 * math.pi` to constants.py | Constant present |
| 1.07 | [x] Add `WAVE_NAMES` list of 4 strings to constants.py | List length == 4 |
| 1.08 | [x] Add `COLORS` list of 4 hex strings to constants.py | List length == 4 |
| 1.09 | [x] Add `DEFAULTS` list of 4 dicts (amplitude, frequency, phase, sampling_rate) to constants.py | List length == 4 |
| 1.10 | [x] Write test: `WAVE_NAMES[0] == "Fundamental"` | Test passes |
| 1.11 | [x] Write test: `WAVE_NAMES[3] == "Fourth Harmonic"` | Test passes |
| 1.12 | [x] Write test: each DEFAULTS entry has keys `amplitude`, `frequency`, `phase`, `sampling_rate` | Test passes |
| 1.13 | [x] Write test: `DEFAULTS[0]['amplitude'] == 50` | Test passes |
| 1.14 | [x] Write test: `DEFAULTS[1]['frequency'] == 1.0` | Test passes |
| 1.15 | [x] Write test: `DEFAULTS[3]['sampling_rate'] == 20` | Test passes |
| 1.16 | [x] Create `src/fourier/shared/types.py` — define `ChannelConfig` TypedDict | Keys: amplitude, frequency, phase, sampling_rate, enabled |
| 1.17 | [x] Add `WindowSlice` TypedDict to types.py | Keys: window_start, duration, signal_values |
| 1.18 | [x] Add `ClassifierResult` TypedDict to types.py | Keys: predicted_class, class_name, confidence, probabilities, runner_up |
| 1.19 | [x] Add `DiffResult` TypedDict to types.py | Keys: agreement, rnn_predicted, lstm_predicted, confidence_delta, runner_up_diff |
| 1.20 | [x] Write test: `ClassifierResult` TypedDict has correct keys | Test passes |
| 1.21 | [x] Write test: `DiffResult` TypedDict has correct keys | Test passes |
| 1.22 | [x] Run ruff on `shared/` — zero violations | Exit code 0 |
| 1.23 | [x] Check each file in `shared/` ≤ 150 lines | All files pass |

---

## Phase 2 · Config System

| # | Task | Definition of Done |
|---|------|--------------------|
| 2.01 | [x] Create `config/app_config.json` with key `resolution: 500` | Key present |
| 2.02 | [x] Add `duration: 10` to `app_config.json` | Key present |
| 2.03 | [x] Add `debug: false` to `app_config.json` | Key present |
| 2.04 | [x] Add `host: "127.0.0.1"` to `app_config.json` | Key present |
| 2.05 | [x] Add `port: 8050` to `app_config.json` | Key present |
| 2.06 | [x] Add `version: "1.00"` to `app_config.json` | Key present |
| 2.07 | [x] Add `window_duration: 1.0` to `app_config.json` | Key present |
| 2.08 | [x] Add `window_points: 50` to `app_config.json` | Key present |
| 2.08a | [x] Add `noise_default: 0.0` to `app_config.json` | Key present |
| 2.08b | [x] Add `noise_max: 0.5` to `app_config.json` | Key present |
| 2.09 | [x] Create `config/rate_limits.json` with key `max_calls_per_minute: 60` | Key present |
| 2.10 | [x] Add `max_retries: 3` to `rate_limits.json` | Key present |
| 2.11 | [x] Add `retry_delay_seconds: 0.5` to `rate_limits.json` | Key present |
| 2.12 | [x] Add `timeout_seconds: 10` to `rate_limits.json` | Key present |
| 2.13 | [x] Create `src/fourier/shared/config_loader.py` — skeleton | File exists |
| 2.14 | [x] Write test: `load_app_config()` returns a dict (red — import fails) | Test fails with ImportError |
| 2.15 | [x] Implement `load_app_config()` — reads `config/app_config.json` | Returns dict |
| 2.16 | [x] Write test: `load_app_config()['resolution'] == 500` | Test passes |
| 2.17 | [x] Write test: `load_app_config()['duration'] == 10` | Test passes |
| 2.18 | [x] Write test: `load_app_config()['debug'] == False` | Test passes |
| 2.19 | [x] Write test: `load_rate_limits()` returns a dict | Test passes |
| 2.20 | [x] Implement `load_rate_limits()` — reads `config/rate_limits.json` | Returns dict |
| 2.21 | [x] Write test: `load_rate_limits()['max_retries'] == 3` | Test passes |
| 2.22 | [x] Write test: missing config file raises `FileNotFoundError` | Test passes |
| 2.23 | [x] Write test: malformed JSON raises `ValueError` | Test passes |
| 2.24 | [x] Implement `_validate_keys(config, required_keys)` helper | Raises `KeyError` on missing key |
| 2.25 | [x] Write test: `_validate_keys` raises `KeyError` on missing required key | Test passes |
| 2.26 | [x] Write test: `_validate_keys` passes silently when all keys present | Test passes |
| 2.27 | [x] Run ruff on `config_loader.py` — zero violations | Exit code 0 |
| 2.28 | [x] Check `config_loader.py` ≤ 150 lines | Passes |

---

## Phase 3 · SDK — SignalGenerator

| # | Task | Definition of Done |
|---|------|--------------------|
| 3.01 | [x] Create `tests/unit/test_signal_generator.py` | File exists |
| 3.02 | [x] Write test: `from fourier.sdk.signal_generator import SignalGenerator` fails (red) | ImportError confirmed |
| 3.03 | [x] Create `src/fourier/sdk/signal_generator.py` — empty skeleton | File exists |
| 3.04 | [x] Write test: `SignalGenerator.__init__` accepts a config dict | Test passes |
| 3.05 | [x] Write test: `_validate_config` raises `KeyError` on missing `frequency` | Test passes |
| 3.06 | [x] Write test: `_validate_config` raises `KeyError` on missing `amplitude` | Test passes |
| 3.07 | [x] Write test: `_validate_config` raises `KeyError` on missing `phase` | Test passes |
| 3.08 | [x] Write test: `_validate_config` raises `KeyError` on missing `sampling_rate` | Test passes |
| 3.09 | [x] Write test: `_validate_config` raises `ValueError` if amplitude < 0 | Test passes |
| 3.10 | [x] Write test: `_validate_config` raises `ValueError` if frequency <= 0 | Test passes |
| 3.11 | [x] Write test: `_validate_config` raises `ValueError` if sampling_rate < 1 | Test passes |
| 3.12 | [x] Write test: `process()` returns dict with key `continuous` | Test passes |
| 3.13 | [x] Write test: `process()` returns dict with key `discrete` | Test passes |
| 3.14 | [x] Write test: `continuous` signal array has length `RESOLUTION + 1` (501) | Test passes |
| 3.15 | [x] Write test: `continuous` values are floats | Test passes |
| 3.16 | [x] Write test: amplitude=0 produces all-zero continuous signal | Test passes |
| 3.17 | [x] Write test: amplitude=0 produces all-zero discrete signal | Test passes |
| 3.18 | [x] Write test: `discrete` signal length == `floor(DURATION * sampling_rate) + 1` | Test passes |
| 3.19 | [x] Write test: `discrete['y'][0]` matches `amp * sin(phase)` (t=0) | Test passes |
| 3.20 | [x] Write test: phase shift correctly offsets the signal | Test passes |
| 3.21 | [x] Write test: frequency=0.5 Hz — first zero crossing at t=1.0s | Test passes |
| 3.22 | [x] Write test: sampling_rate=1 Hz produces 11 discrete samples | Test passes |
| 3.23 | [x] Write test: sampling_rate=50 Hz produces 501 discrete samples | Test passes |
| 3.24 | [x] Write test: amplitude=100 (max) values stay in [-100, 100] | Test passes |
| 3.25 | [x] Implement `SignalGenerator.__init__` | Stores config |
| 3.26 | [x] Implement `SignalGenerator._validate_config` | Raises on invalid config |
| 3.27 | [x] Implement `SignalGenerator._build_time_axis()` — continuous 0 to DURATION | Returns np.ndarray shape (501,) |
| 3.28 | [x] Implement `SignalGenerator._compute_continuous()` — amp*sin(PI2*freq*t+phase) | Returns np.ndarray |
| 3.29 | [x] Implement `SignalGenerator._build_discrete_times()` — n/sr for n in range | Returns np.ndarray |
| 3.30 | [x] Implement `SignalGenerator._compute_discrete()` — amp*sin(PI2*freq*t+phase) at discrete t | Returns np.ndarray |
| 3.31 | [x] Implement `SignalGenerator.process()` — combines continuous and discrete results | Returns dict |
| 3.32 | [x] Run `pytest tests/unit/test_signal_generator.py` — all pass | Exit code 0 |
| 3.33 | [x] Run ruff on `signal_generator.py` — zero violations | Exit code 0 |
| 3.34 | [x] Check `signal_generator.py` ≤ 150 lines | Passes |

---

## Phase 4 · SDK — WindowExtractor

| # | Task | Definition of Done |
|---|------|--------------------|
| 4.01 | [x] Create `tests/unit/test_window_extractor.py` | File exists |
| 4.02 | [x] Write test: import `WindowExtractor` fails (red) | ImportError confirmed |
| 4.03 | [x] Create `src/fourier/sdk/window_extractor.py` — skeleton | File exists |
| 4.04 | [x] Write test: `WindowExtractor.__init__` accepts config dict | Test passes |
| 4.05 | [x] Write test: `_validate_config` raises `KeyError` on missing `window_start` | Test passes |
| 4.06 | [x] Write test: `_validate_config` raises `ValueError` on `window_start < 0` | Test passes |
| 4.07 | [x] Write test: `_validate_config` raises `ValueError` on `window_start > 9.0` | Test passes |
| 4.08 | [x] Write test: `process()` returns an array of length 50 | Test passes |
| 4.09 | [x] Write test: extracted values match source signal at correct indices | Test passes |
| 4.10 | [x] Write test: `window_start=0.0` extracts first 50 points | Test passes |
| 4.11 | [x] Write test: `window_start=9.0` extracts last 50 points | Test passes |
| 4.12 | [x] Write test: normalized output has mean ≈ 0 (within 1e-6) | Test passes |
| 4.13 | [x] Write test: normalized output has std ≈ 1 (within 1e-6) | Test passes |
| 4.14 | [x] Write test: all-zero signal returns zero vector (std=0 edge case handled) | Test passes — no ZeroDivisionError |
| 4.15 | [x] Write test: output shape after reshape is `(1, 50, 1)` | Test passes |
| 4.16 | [x] Write test: output dtype is float32 (required by PyTorch) | Test passes |
| 4.17 | [x] Implement `WindowExtractor.__init__` | Stores config |
| 4.18 | [x] Implement `WindowExtractor._validate_config` | Raises on invalid config |
| 4.19 | [x] Implement `WindowExtractor._slice_window(signal)` — convert time to index using RESOLUTION/DURATION ratio | Returns 50-point slice |
| 4.20 | [x] Implement `WindowExtractor._normalize(arr)` — z-score, handle std=0 | Returns normalized array |
| 4.21 | [x] Implement `WindowExtractor._reshape(arr)` — reshape to (1, 50, 1) as float32 | Returns np.ndarray |
| 4.22 | [x] Implement `WindowExtractor.process(signal, noise_sigma=0.0)` | Returns shaped, normalized, optionally noisy array |
| 4.23 | [x] Implement `WindowExtractor._inject_noise(arr, sigma)` — adds `N(0, σ²)` noise when sigma > 0 | Noise applied only when sigma > 0 |
| 4.24 | [x] Write test: `_inject_noise(arr, sigma=0.0)` returns identical array | Test passes |
| 4.25 | [x] Write test: `_inject_noise(arr, sigma=0.2)` changes array values | Test passes |
| 4.26 | [x] Write test: `process(signal, noise_sigma=0.3)` output differs from `process(signal, noise_sigma=0.0)` | Test passes |
| 4.27 | [x] Write test: `_inject_noise` uses `numpy.random.normal` (reproducible with seed) | Test passes |
| 4.28 | [x] Write test: `_validate_config` raises `ValueError` if `noise_sigma < 0` | Test passes |
| 4.29 | [x] Write test: `_validate_config` raises `ValueError` if `noise_sigma > 0.5` | Test passes |
| 4.30 | [x] Run `pytest tests/unit/test_window_extractor.py` — all pass | Exit code 0 |
| 4.31 | [x] Run ruff on `window_extractor.py` — zero violations | Exit code 0 |
| 4.32 | [x] Check `window_extractor.py` ≤ 150 lines | Passes |

---

## Phase 5 · SDK — RNN Classifier

| # | Task | Definition of Done |
|---|------|--------------------|
| 5.01 | [x] Create `tests/unit/test_rnn_classifier.py` | File exists |
| 5.02 | [x] Write test: import `RNNClassifier` fails (red) | ImportError confirmed |
| 5.03 | [x] Create `src/fourier/sdk/rnn_classifier.py` — skeleton | File exists |
| 5.04 | [x] Write test: `RNNClassifier.__init__` accepts config dict | Test passes |
| 5.05 | [x] Write test: `_validate_config` raises on missing `hidden_size` | Test passes |
| 5.06 | [x] Write test: `_validate_config` raises on missing `num_layers` | Test passes |
| 5.07 | [x] Write test: `_validate_config` raises on missing `weights_path` | Test passes |
| 5.08 | [x] Write test: `RNNModel` is a `torch.nn.Module` subclass | Test passes |
| 5.09 | [x] Write test: `RNNModel` input_size=1 | Test passes |
| 5.10 | [x] Write test: `RNNModel` output_size=4 (4 harmonic classes) | Test passes |
| 5.11 | [x] Write test: `RNNModel.forward()` accepts input of shape `(1, 50, 1)` | No error raised |
| 5.12 | [x] Write test: `RNNModel.forward()` returns tensor of shape `(1, 4)` | Test passes |
| 5.13 | [x] Write test: `RNNModel.forward()` output sums to 1.0 (softmax applied) | Test passes |
| 5.14 | [x] Write test: `RNNModel` hidden state initialized as zeros | Test passes |
| 5.15 | [x] Write test: `RNNModel` uses tanh activation (not sigmoid) | Test passes |
| 5.16 | [x] Write test: `RNNModel` uses shared weights across time steps | Test passes — single nn.RNN layer |
| 5.17 | [x] Write test: `RNNClassifier.process()` returns `ClassifierResult` dict | Test passes |
| 5.18 | [x] Write test: `ClassifierResult['predicted_class']` is int in range 0-3 | Test passes |
| 5.19 | [x] Write test: `ClassifierResult['class_name']` is a string | Test passes |
| 5.20 | [x] Write test: `ClassifierResult['confidence']` is float in [0.0, 1.0] | Test passes |
| 5.21 | [x] Write test: `ClassifierResult['probabilities']` is list of 4 floats summing to 1.0 | Test passes |
| 5.22 | [x] Write test: `ClassifierResult['runner_up']` is second-highest class int | Test passes |
| 5.23 | [x] Write test: `confidence` equals `max(probabilities)` | Test passes |
| 5.24 | [x] Define `RNNModel(nn.Module)` in `rnn_classifier.py` | Class defined |
| 5.25 | [x] Implement `RNNModel.__init__` — `nn.RNN`, `nn.Linear(hidden→4)` | Layers defined |
| 5.26 | [x] Implement `RNNModel.forward()` — unroll RNN, take `h_n[-1]`, FC layer, softmax | Returns (1,4) tensor |
| 5.27 | [x] Implement `RNNClassifier.__init__` — instantiate `RNNModel`, call `_load_weights` | No error if weights_path exists |
| 5.28 | [x] Implement `RNNClassifier._validate_config` | Raises on bad config |
| 5.29 | [x] Implement `RNNClassifier._load_weights()` — `torch.load` weights_path | Weights loaded into model |
| 5.30 | [x] Implement `RNNClassifier._build_result(probs_tensor)` — dict from probabilities | Returns `ClassifierResult` |
| 5.31 | [x] Implement `RNNClassifier.process(window)` — run model, build result | Returns `ClassifierResult` |
| 5.32 | [x] Run `pytest tests/unit/test_rnn_classifier.py` — all pass | Exit code 0 |
| 5.33 | [x] Run ruff on `rnn_classifier.py` — zero violations | Exit code 0 |
| 5.34 | [x] Check `rnn_classifier.py` ≤ 150 lines | Passes — split into `rnn_model.py` if needed |
| 5.35 | [x] Write test: `RNNClassifier` raises `FileNotFoundError` when weights_path is missing | Test passes |

---

## Phase 6 · SDK — LSTM Classifier

| # | Task | Definition of Done |
|---|------|--------------------|
| 6.01 | [x] Create `tests/unit/test_lstm_classifier.py` | File exists |
| 6.02 | [x] Write test: import `LSTMClassifier` fails (red) | ImportError confirmed |
| 6.03 | [x] Create `src/fourier/sdk/lstm_classifier.py` — skeleton | File exists |
| 6.04 | [x] Write test: `LSTMClassifier.__init__` accepts config dict | Test passes |
| 6.05 | [x] Write test: `_validate_config` raises on missing `hidden_size` | Test passes |
| 6.06 | [x] Write test: `_validate_config` raises on missing `num_layers` | Test passes |
| 6.07 | [x] Write test: `_validate_config` raises on missing `dropout` | Test passes |
| 6.08 | [x] Write test: `_validate_config` raises on missing `weights_path` | Test passes |
| 6.09 | [x] Write test: `LSTMModel` is a `torch.nn.Module` subclass | Test passes |
| 6.10 | [x] Write test: `LSTMModel` input_size=1 | Test passes |
| 6.11 | [x] Write test: `LSTMModel` output_size=4 | Test passes |
| 6.12 | [x] Write test: `LSTMModel.forward()` accepts input of shape `(1, 50, 1)` | No error raised |
| 6.13 | [x] Write test: `LSTMModel.forward()` returns tensor of shape `(1, 4)` | Test passes |
| 6.14 | [x] Write test: `LSTMModel.forward()` output sums to 1.0 (softmax applied) | Test passes |
| 6.15 | [x] Write test: `LSTMModel` has 2 stacked LSTM layers (num_layers=2) | Test passes |
| 6.16 | [x] Write test: `LSTMModel` has dropout between layers | Test passes |
| 6.17 | [x] Write test: `LSTMModel` maintains separate cell_state and hidden_state | Test passes |
| 6.18 | [x] Write test: LSTM forget gate output is in [0, 1] (sigmoid) | Test passes |
| 6.19 | [x] Write test: LSTM input gate output is in [0, 1] (sigmoid) | Test passes |
| 6.20 | [x] Write test: LSTM output gate output is in [0, 1] (sigmoid) | Test passes |
| 6.21 | [x] Write test: cell state updated as `f_t * C_prev + i_t * C_tilde` | Test passes |
| 6.22 | [x] Write test: hidden state updated as `o_t * tanh(C_t)` | Test passes |
| 6.23 | [x] Write test: `LSTMClassifier.process()` returns `ClassifierResult` dict | Test passes |
| 6.24 | [x] Write test: `ClassifierResult['predicted_class']` is int in 0-3 | Test passes |
| 6.25 | [x] Write test: `ClassifierResult['class_name']` is a string | Test passes |
| 6.26 | [x] Write test: `ClassifierResult['confidence']` is float in [0.0, 1.0] | Test passes |
| 6.27 | [x] Write test: `ClassifierResult['probabilities']` is list of 4 floats summing to 1.0 | Test passes |
| 6.28 | [x] Write test: `ClassifierResult['runner_up']` is second-highest class int | Test passes |
| 6.29 | [x] Write test: `LSTMModel` parameter count ≈ 132,612 with hidden_size=128, num_layers=2 | Test passes (±5%) |
| 6.30 | [x] Write test: `LSTMClassifier` handles dropout=0.0 without error | Test passes |
| 6.31 | [x] Write test: `LSTMClassifier` handles dropout=0.5 without error | Test passes |
| 6.32 | [x] Write test: `LSTMClassifier` raises `FileNotFoundError` on missing weights | Test passes |
| 6.33 | [x] Define `LSTMModel(nn.Module)` in `lstm_classifier.py` | Class defined |
| 6.34 | [x] Implement `LSTMModel.__init__` — `nn.LSTM(num_layers=2)`, `nn.Dropout`, `nn.Linear(hidden→4)` | Layers defined |
| 6.35 | [x] Implement `LSTMModel.forward()` — run LSTM, take last output, FC, softmax | Returns (1,4) tensor |
| 6.36 | [x] Implement `LSTMClassifier.__init__` — instantiate `LSTMModel`, call `_load_weights` | No error if weights exist |
| 6.37 | [x] Implement `LSTMClassifier._validate_config` | Raises on bad config |
| 6.38 | [x] Implement `LSTMClassifier._load_weights()` — `torch.load` weights_path | Weights loaded |
| 6.39 | [x] Implement `LSTMClassifier._build_result(probs_tensor)` | Returns `ClassifierResult` |
| 6.40 | [x] Implement `LSTMClassifier.process(window)` — run model, build result | Returns `ClassifierResult` |
| 6.41 | [x] Run `pytest tests/unit/test_lstm_classifier.py` — all pass | Exit code 0 |
| 6.42 | [x] Run ruff on `lstm_classifier.py` — zero violations | Exit code 0 |
| 6.43 | [x] Check `lstm_classifier.py` ≤ 150 lines | Passes — split into `lstm_model.py` if needed |

---

## Phase 7 · Gatekeeper

| # | Task | Definition of Done |
|---|------|--------------------|
| 7.01 | [x] Create `tests/unit/test_gatekeeper.py` | File exists |
| 7.02 | [x] Write test: import `ModelGatekeeper` fails (red) | ImportError confirmed |
| 7.03 | [x] Create `src/fourier/gatekeeper.py` — skeleton | File exists |
| 7.04 | [x] Write test: `ModelGatekeeper.__init__` loads rate_limits config | Test passes |
| 7.05 | [x] Write test: `_validate_config` raises on missing `max_calls_per_minute` | Test passes |
| 7.06 | [x] Write test: `_validate_config` raises on missing `max_retries` | Test passes |
| 7.07 | [x] Write test: `_validate_config` raises on missing `retry_delay_seconds` | Test passes |
| 7.08 | [x] Write test: `_validate_config` raises on missing `timeout_seconds` | Test passes |
| 7.09 | [x] Write test: `call(fn, *args)` invokes `fn` with given args | Test passes |
| 7.10 | [x] Write test: `call(fn)` returns the result of `fn` | Test passes |
| 7.11 | [x] Write test: `call(fn)` retries on `RuntimeError` up to `max_retries` times | Test passes |
| 7.12 | [x] Write test: `call(fn)` raises `RuntimeError` after `max_retries` exhausted | Test passes |
| 7.13 | [x] Write test: `call(fn)` logs each attempt to stdout | Test passes (capfd) |
| 7.14 | [x] Write test: `call(fn)` logs retry number on each retry | Test passes |
| 7.15 | [x] Write test: `call(fn)` logs final failure message | Test passes |
| 7.16 | [x] Write test: rate limit — calling more than `max_calls_per_minute` raises `RateLimitError` | Test passes |
| 7.17 | [x] Write test: call count resets after 60 seconds (mock time) | Test passes |
| 7.18 | [x] Write test: `call(fn, *args, **kwargs)` passes kwargs correctly | Test passes |
| 7.19 | [x] Implement `ModelGatekeeper.__init__` — load rate limits, init call log | Done |
| 7.20 | [x] Implement `ModelGatekeeper._validate_config` | Raises on bad config |
| 7.21 | [x] Implement `ModelGatekeeper._check_rate_limit()` — compare call count to limit | Raises `RateLimitError` if exceeded |
| 7.22 | [x] Implement `ModelGatekeeper._log_call(attempt, status)` — print timestamp, attempt, status | Prints to stdout |
| 7.23 | [x] Implement `ModelGatekeeper._execute_with_retry(fn, *args, **kwargs)` — retry loop | Retries up to `max_retries` |
| 7.24 | [x] Implement `ModelGatekeeper.call(fn, *args, **kwargs)` — rate check, then execute | Returns fn result |
| 7.25 | [x] Run `pytest tests/unit/test_gatekeeper.py` — all pass | Exit code 0 |
| 7.26 | [x] Run ruff on `gatekeeper.py` — zero violations | Exit code 0 |
| 7.27 | [x] Check `gatekeeper.py` ≤ 150 lines | Passes |

---

## Phase 8 · Training Service

| # | Task | Definition of Done |
|---|------|--------------------|
| 8.01 | [x] Create `tests/unit/test_training_service.py` | File exists |
| 8.02 | [x] Write test: import `generate_synthetic_data` fails (red) | ImportError confirmed |
| 8.03 | [x] Create `src/fourier/services/train_models.py` — skeleton | File exists |
| 8.04 | [x] Write test: `generate_synthetic_data(n=100)` returns tuple `(X, y)` | Test passes |
| 8.05 | [x] Write test: `X.shape == (100, 50, 1)` | Test passes |
| 8.06 | [x] Write test: `y.shape == (100,)` | Test passes |
| 8.07 | [x] Write test: `y` values are in `{0, 1, 2, 3}` | Test passes |
| 8.08 | [x] Write test: data is balanced — 25 samples per class for n=100 | Test passes |
| 8.09 | [x] Write test: class 0 samples use frequency=0.5 Hz pattern | Test passes |
| 8.10 | [x] Write test: class 1 samples use frequency=1.0 Hz pattern | Test passes |
| 8.11 | [x] Write test: class 2 samples use frequency=1.5 Hz pattern | Test passes |
| 8.12 | [x] Write test: class 3 samples use frequency=2.0 Hz pattern | Test passes |
| 8.13 | [x] Write test: generated `X` values normalized to [-1, 1] range | Test passes |
| 8.14 | [x] Write test: `_add_noise(x, std=0.1)` adds Gaussian noise | Test passes |
| 8.15 | [x] Write test: `_split_data(X, y, test_ratio=0.2)` returns 4 arrays | Test passes |
| 8.16 | [x] Write test: train set is 80% of data after split | Test passes |
| 8.17 | [x] Write test: test set is 20% of data after split | Test passes |
| 8.18 | [x] Implement `generate_synthetic_data(n=1000)` — 4 Fourier-class signals with noise | Returns (X, y) |
| 8.19 | [x] Implement `_add_noise(arr, std)` — adds Gaussian noise via numpy | Returns noisy array |
| 8.20 | [x] Implement `_split_data(X, y, test_ratio)` — random shuffle, split | Returns X_train, X_test, y_train, y_test |
| 8.21 | [x] Implement `_train_epoch(model, loader, optimizer, criterion)` — one training epoch | Returns epoch loss |
| 8.22 | [x] Implement `_eval_model(model, loader)` — compute accuracy on loader | Returns accuracy float |
| 8.23 | [x] Implement `train_rnn(config)` — full training loop for RNNModel | Saves `models/rnn_classifier.pt` |
| 8.24 | [x] Implement training loop with 50 default epochs | Prints loss per epoch |
| 8.25 | [x] Implement Adam optimizer with lr=0.001 for RNN training | Optimizer used |
| 8.26 | [x] Implement `train_lstm(config)` — full training loop for LSTMModel | Saves `models/lstm_classifier.pt` |
| 8.27 | [x] Implement training loop with 50 default epochs for LSTM | Prints loss per epoch |
| 8.28 | [x] Implement Adam optimizer with lr=0.001 for LSTM training | Optimizer used |
| 8.29 | [x] Implement dropout support during LSTM training (model.train() mode) | Dropout active during training |
| 8.30 | [x] Implement `save_weights(model, path)` — `torch.save(model.state_dict(), path)` | File written to models/ |
| 8.31 | [x] Add `if __name__ == "__main__"` block to run both training scripts | `uv run python -m fourier.services.train_models` trains both |
| 8.32 | [x] Run `pytest tests/unit/test_training_service.py` — all pass | Exit code 0 |
| 8.33 | [x] Run ruff on `train_models.py` — zero violations | Exit code 0 |
| 8.34 | [x] Check `train_models.py` ≤ 150 lines | Passes — split into separate files if needed |
| 8.35 | [x] Execute training: `uv run python -m fourier.services.train_models` | Both `.pt` files created in `models/` |
| 8.36 | [x] Verify `models/rnn_classifier.pt` exists | File present |
| 8.37 | [x] Verify `models/lstm_classifier.pt` exists | File present |
| 8.38 | [x] Log RNN accuracy on test set | Accuracy ≥ 90% |
| 8.39 | [x] Log LSTM accuracy on test set | Accuracy ≥ 90% |

---

## Phase 9 · SDK — Result Comparator

| # | Task | Definition of Done |
|---|------|--------------------|
| 9.01 | [x] Create `tests/unit/test_result_comparator.py` | File exists |
| 9.02 | [x] Write test: import `ResultComparator` fails (red) | ImportError confirmed |
| 9.03 | [x] Create `src/fourier/sdk/result_comparator.py` — skeleton | File exists |
| 9.04 | [x] Write test: `ResultComparator.__init__` accepts config dict | Test passes |
| 9.05 | [x] Write test: `_validate_config` passes on empty config (no required keys) | Test passes |
| 9.06 | [x] Write test: `process(rnn_result, lstm_result)` returns `DiffResult` dict | Test passes |
| 9.07 | [x] Write test: `DiffResult['agreement']` is `True` when both predict same class | Test passes |
| 9.08 | [x] Write test: `DiffResult['agreement']` is `False` when predictions differ | Test passes |
| 9.09 | [x] Write test: `DiffResult['rnn_predicted']` equals `rnn_result['class_name']` | Test passes |
| 9.10 | [x] Write test: `DiffResult['lstm_predicted']` equals `lstm_result['class_name']` | Test passes |
| 9.11 | [x] Write test: `DiffResult['confidence_delta']` == `abs(rnn_conf - lstm_conf)` | Test passes |
| 9.12 | [x] Write test: `DiffResult['runner_up_diff']` is a descriptive string | Test passes |
| 9.13 | [x] Write test: `confidence_delta` rounds to 4 decimal places | Test passes |
| 9.14 | [x] Implement `ResultComparator.__init__` | Stores config |
| 9.15 | [x] Implement `ResultComparator._validate_config` | No-op — no required keys |
| 9.16 | [x] Implement `ResultComparator._compute_agreement(r, l)` | Returns bool |
| 9.17 | [x] Implement `ResultComparator._compute_confidence_delta(r, l)` | Returns float |
| 9.18 | [x] Implement `ResultComparator._compute_runner_up_diff(r, l)` | Returns descriptive string |
| 9.19 | [x] Implement `ResultComparator.process(rnn, lstm)` | Returns `DiffResult` |
| 9.20 | [x] Run `pytest tests/unit/test_result_comparator.py` — all pass | Exit code 0 |
| 9.21 | [x] Run ruff on `result_comparator.py` — zero violations | Exit code 0 |
| 9.22 | [x] Check `result_comparator.py` ≤ 150 lines | Passes |

---

## Phase 10 · UI — Layout

| # | Task | Definition of Done |
|---|------|--------------------|
| 10.01 | [x] Create `src/fourier/ui/layout.py` — skeleton | File exists |
| 10.02 | [x] Write test: `from fourier.ui.layout import build_layout` fails (red) | ImportError confirmed |
| 10.03 | [x] Write test: `build_layout()` returns `html.Div` | Test passes |
| 10.04 | [x] Implement `build_layout()` — root `html.Div` with flex column | Returns html.Div |
| 10.05 | [x] Implement `_build_header()` — sticky header with title and reset button | Returns html.Header |
| 10.06 | [x] Write test: header contains element with id `reset-btn` | Test passes |
| 10.07 | [x] Write test: header contains text "Fourier Synthesis" | Test passes |
| 10.08 | [x] Implement `_build_sidebar()` — 300px left panel with 4 wave panels | Returns html.Div |
| 10.09 | [x] Write test: sidebar contains 4 wave panel divs | Test passes |
| 10.10 | [x] Implement `_build_wave_panel(i)` for i in 0-3 | Returns html.Div for channel i |
| 10.11 | [x] Write test: wave panel i=0 contains `enabled-0` checklist | Test passes |
| 10.12 | [x] Write test: wave panel i=0 contains `freq-0` slider | Test passes |
| 10.13 | [x] Write test: wave panel i=0 contains `amp-0` slider | Test passes |
| 10.14 | [x] Write test: wave panel i=0 contains `phase-0` slider | Test passes |
| 10.15 | [x] Write test: wave panel i=0 contains `dots-0` checklist | Test passes |
| 10.16 | [x] Write test: wave panel i=0 contains `sr-0` slider | Test passes |
| 10.17 | [x] Write test: wave panel i=0 contains `vector-0` output div | Test passes |
| 10.18 | [x] Implement `make_slider(sid, label, min_v, max_v, step, default)` helper | Returns html.Div with dcc.Slider |
| 10.19 | [x] Write test: `make_slider` has `updatemode='drag'` | Test passes |
| 10.20 | [x] Write test: `make_slider` has `marks=None` | Test passes |
| 10.21 | [x] Write test: `freq-{i}` slider range is 0.1 to 5.0 | Test passes |
| 10.22 | [x] Write test: `amp-{i}` slider range is 0 to 100 | Test passes |
| 10.23 | [x] Write test: `phase-{i}` slider range is 0.0 to 6.28 (2π) | Test passes |
| 10.24 | [x] Write test: `sr-{i}` slider range is 1 to 50 | Test passes |
| 10.25 | [x] Implement `_build_main_area()` — right panel with charts and ML section | Returns html.Main |
| 10.26 | [x] Write test: main area contains `overlay-chart` dcc.Graph | Test passes |
| 10.27 | [x] Write test: main area contains `sum-chart` dcc.Graph | Test passes |
| 10.28 | [x] Implement `_build_window_selector()` — slider 0.0 to 9.0 step 0.1 id `window-slider` | Returns html.Div |
| 10.29 | [x] Write test: window-slider range is 0.0 to 9.0 | Test passes |
| 10.29a | [x] Implement `_build_noise_slider()` — slider 0.0 to 0.5 step 0.01 id `noise-slider` default 0.0 | Returns html.Div |
| 10.29b | [x] Write test: `noise-slider` range is 0.0 to 0.5 | Test passes |
| 10.29c | [x] Write test: `noise-slider` default value is 0.0 | Test passes |
| 10.29d | [x] Implement `_build_noise_label()` — dynamic text: Clean / Light / Medium / Heavy, id `noise-label` | Returns html.Div |
| 10.29e | [x] Write test: noise label div id is `noise-label` | Test passes |
| 10.30 | [x] Implement `_build_algo_selector()` — RadioItems: RNN / LSTM / Both, id `algo-selector` | Returns html.Div |
| 10.31 | [x] Write test: algo-selector has 3 options | Test passes |
| 10.32 | [x] Write test: algo-selector default value is "RNN" | Test passes |
| 10.33 | [x] Implement `_build_identify_button()` — button id `identify-btn` | Returns html.Button |
| 10.34 | [x] Write test: identify-btn text contains "Identify" | Test passes |
| 10.35 | [x] Implement `_build_result_panel()` — hidden div id `result-panel` | Returns html.Div, initially hidden |
| 10.36 | [x] Implement `_build_diff_panel()` — hidden div id `diff-panel` | Returns html.Div, initially hidden |
| 10.37 | [x] Implement `_build_footer()` — version badge, status indicator | Returns html.Footer |
| 10.38 | [x] Write test: footer displays VERSION string | Test passes |
| 10.39 | [x] Run ruff on `layout.py` — zero violations | Exit code 0 |
| 10.40 | [x] Check `layout.py` ≤ 150 lines — split into `layout_sidebar.py`, `layout_main.py` if needed | All files ≤ 150 lines |
| 10.41 | [x] Add `dcc.Store(id="channel-vector", data=[1,1,1,1])` to `build_layout()` | Store present in layout |
| 10.42 | [x] Write test: layout contains `channel-vector` Store id | Test passes |

---

## Phase 11 · UI — Clientside Callback (Charts)

| # | Task | Definition of Done |
|---|------|--------------------|
| 11.01 | [x] Create `src/fourier/ui/callbacks_client.py` — skeleton | File exists |
| 11.02 | [x] Define `CLIENTSIDE_CHART_JS` constant (JS string) | Constant defined |
| 11.03 | [x] Write test: JS string is non-empty | Test passes |
| 11.04 | [x] Write test: JS string contains `function(` keyword | Test passes |
| 11.05 | [x] Write test: JS string contains `overlayTraces` variable | Test passes |
| 11.06 | [x] Write test: JS string contains `sumY` variable | Test passes |
| 11.07 | [x] Write test: JS string contains `tCont` variable | Test passes |
| 11.08 | [x] Write test: JS function accepts 22 parameters (C + 5 per channel × 4 + window-slider) | Test passes (count function params) |
| 11.08a | [x] Implement JS: accept `C` binary vector as first parameter (replaces 4 separate enabled inputs) | JS param `C` present |
| 11.08b | [x] Write test: JS uses `C[i] !== 1` to skip disabled channels | Test passes |
| 11.08c | [x] Write test: JS uses `C[i]` variable | Test passes |
| 11.09 | [x] Implement JS: continuous time axis `tCont` (0 to 10s, 501 points) | JS block present |
| 11.10 | [x] Implement JS: `sumY` array initialized to zeros (length 501) | JS block present |
| 11.11 | [x] Implement JS: loop over 4 channels (i=0 to 3) | JS block present |
| 11.12 | [x] Implement JS: channel enabled check via `C[i] !== 1` — skip disabled channels | JS block present |
| 11.13 | [x] Implement JS: accumulate `sumY` for enabled channels (continuous) | JS block present |
| 11.14 | [x] Implement JS: dots mode — scatter markers at `n/sr` sample points | JS block present |
| 11.15 | [x] Implement JS: line mode — continuous trace with `mode: 'lines'` | JS block present |
| 11.16 | [x] Implement JS: overlay chart layout — white background, labeled axes | JS block present |
| 11.17 | [x] Implement JS: overlay chart y-axis range [-100, 100] | JS block present |
| 11.18 | [x] Implement JS: summation chart layout — dark background `#020617` | JS block present |
| 11.19 | [x] Implement JS: summation chart y-axis range [-150, 150] | JS block present |
| 11.20 | [x] Implement JS: `vrect` amber shape on summation chart for selected window | JS block present |
| 11.21 | [x] Write test: vrect shape has `x0 = window_start` and `x1 = window_start + 1` | Test passes |
| 11.22 | [x] Write test: vrect color is amber / semi-transparent | Test passes |
| 11.23 | [x] Implement `register_clientside_callback(app)` function | Registers callback on app |
| 11.24 | [x] Write test: callback outputs `overlay-chart.figure` | Test passes |
| 11.25 | [x] Write test: callback outputs `sum-chart.figure` | Test passes |
| 11.26 | [x] Write test: callback has 23 inputs (C store + 20 channel controls + window-slider + noise-slider) | Test passes |
| 11.27 | [x] Run ruff on `callbacks_client.py` — zero violations | Exit code 0 |
| 11.28 | [x] Check `callbacks_client.py` ≤ 150 lines | Passes |

---

## Phase 12 · UI — Server Callbacks

| # | Task | Definition of Done |
|---|------|--------------------|
| 12.01 | [x] Create `src/fourier/ui/callbacks_server.py` — skeleton | File exists |
| 12.02 | [x] Write test: import `register_server_callbacks` fails (red) | ImportError confirmed |
| 12.03 | [x] Define `register_server_callbacks(app, gatekeeper)` function | Function defined |
| 12.04 | [x] Write test: `toggle_wave` callback registered for `enabled-{i}` input | Tested via `toggle_wave_fn` pure function |
| 12.05 | [x] Implement `toggle_wave` callback — returns wave-controls style + wave-panel style | Registered on app |
| 12.06 | [x] Write test: wave-controls style is `{}` when channel enabled | Test passes |
| 12.07 | [x] Write test: wave-controls style is `{'display':'none'}` when disabled | Test passes |
| 12.08 | [x] Write test: wave-panel opacity `'1'` when enabled | Test passes |
| 12.09 | [x] Write test: wave-panel opacity `'0.55'` when disabled | Test passes |
| 12.10 | [x] Write test: wave-panel background `rgba(238,242,255,0.3)` when enabled | Test passes |
| 12.11 | [x] Write test: wave-panel background `#f8fafc` when disabled | Test passes |
| 12.12 | [x] Write test: `toggle_sr` callback registered for `dots-{i}` input | Tested via `toggle_sr_fn` |
| 12.13 | [x] Implement `toggle_sr` callback — shows/hides `sr-section-{i}` | Registered on app |
| 12.14 | [x] Write test: `sr-section` style is `{'display':'block'}` when dots enabled | Test passes |
| 12.15 | [x] Write test: `sr-section` style is `{'display':'none'}` when dots disabled | Test passes |
| 12.16 | [x] Write test: `update_vector` callback registered for dots, sr, freq, amp, phase inputs | Tested via `update_vector_fn` |
| 12.17 | [x] Implement `update_vector` callback — computes discrete y[n] and renders | Registered on app |
| 12.18 | [x] Write test: `update_vector` returns `[]` when dots not enabled | Test passes |
| 12.19 | [x] Write test: `update_vector` returns `html.Div` when dots enabled | Test passes |
| 12.20 | [x] Write test: vector div title shows `"n = 0…{n_s-1}"` format | Test passes |
| 12.21 | [x] Write test: span values match `amp*sin(2π*freq*t+phase)` rounded to 1 decimal | Test passes |
| 12.22 | [x] Write test: span `title` attribute contains `n=` and `t=` info | Test passes |
| 12.23 | [x] Write test: vector displayed in dark monospace box style | Test passes |
| 12.24 | [x] Write test: `reset` callback registered for `reset-btn` input | Tested via `reset_cb_fn` |
| 12.25 | [x] Implement `reset` callback — returns 24 default values (6 × 4 channels) | Registered on app |
| 12.26 | [x] Write test: reset returns default amplitudes `[50, 30, 20, 10]` | Test passes |
| 12.27 | [x] Write test: reset returns default frequencies `[0.5, 1.0, 1.5, 2.0]` | Test passes |
| 12.28 | [x] Write test: reset returns default phases `[0.0, π/2, π, 3π/2]` | Test passes |
| 12.29 | [x] Write test: reset returns `enabled=['on']` for all 4 channels | Test passes |
| 12.30 | [x] Write test: reset returns `dots=[]` for all 4 channels | Test passes |
| 12.31 | [x] Write test: reset returns default sampling rates `[20, 20, 20, 20]` | Test passes |
| 12.31a | [x] Write test: `noise_label` callback registered for `noise-slider` input | Tested via `_noise_label` |
| 12.31b | [x] Implement `noise_label` callback — maps σ value to text: 0.0→"Clean", ≤0.15→"Light", ≤0.30→"Medium", >0.30→"Heavy" | Registered on app |
| 12.31c | [x] Write test: σ=0.0 → label text contains "Clean" | Test passes |
| 12.31d | [x] Write test: σ=0.15 → label text contains "Light" | Test passes |
| 12.31e | [x] Write test: σ=0.30 → label text contains "Medium" | Test passes |
| 12.31f | [x] Write test: σ=0.50 → label text contains "Heavy" | Test passes |
| 12.32 | [x] Write test: `identify` callback registered for `identify-btn` input | Tested via `_run_identify` |
| 12.33 | [x] Implement `identify` callback — reads window-slider, noise-slider, and algo-selector | Registered on app |
| 12.34 | [x] Write test: identify callback passes `noise_sigma` to `WindowExtractor.process()` | Test passes |
| 12.34a | [x] Write test: identify with noise_sigma=0.0 and noise_sigma=0.3 produce different windows | Test passes |
| 12.35 | [x] Write test: identify with `algo='RNN'` calls gatekeeper with RNN classifier | Test passes |
| 12.36 | [x] Write test: identify with `algo='LSTM'` calls gatekeeper with LSTM classifier | Test passes |
| 12.37 | [x] Write test: identify with `algo='Both'` calls gatekeeper for both classifiers | Test passes |
| 12.38 | [x] Write test: identify with `algo='Both'` calls `ResultComparator.process()` | Test passes |
| 12.39 | [x] Implement `_build_single_result_panel(result)` — renders class name, confidence, prob bars | Returns html.Div |
| 12.40 | [x] Write test: single result panel shows class name | Test passes |
| 12.41 | [x] Write test: single result panel shows confidence as percentage | Test passes |
| 12.42 | [x] Write test: single result panel shows 4 probability bars | Test passes |
| 12.43 | [x] Implement `_build_both_results_panel(rnn_r, lstm_r)` — side-by-side panels | Returns html.Div |
| 12.44 | [x] Write test: both-results panel has two sub-panels (RNN and LSTM) | Test passes |
| 12.45 | [x] Implement `_build_diff_summary(diff)` — renders DiffResult fields | Returns html.Div |
| 12.46 | [x] Write test: diff panel shows agreement badge (green when True, red when False) | Test passes |
| 12.47 | [x] Write test: diff panel shows confidence_delta value | Test passes |
| 12.48 | [x] Write test: diff panel shows runner_up_diff description | Test passes |
| 12.49 | [x] Write test: result-panel is shown after identify (style updated) | Test passes |
| 12.50 | [x] Run ruff on `callbacks_server.py` — zero violations | Exit code 0 |
| 12.51 | [x] Check `callbacks_server.py` ≤ 150 lines — split into `callbacks_identify.py` if needed | All files ≤ 150 lines |
| 12.52 | [x] Implement `compute_channel_vector(*enabled)` — converts 4 checklists to C = [0/1, …] | Returns `list[int]` of length 4 |
| 12.53 | [x] Register `channel_vector_cb` callback — writes C to `channel-vector` Store on any enabled change | Registered on app |
| 12.54 | [x] Write test: `compute_channel_vector(["on"],["on"],["on"],["on"])` returns `[1,1,1,1]` | Test passes |
| 12.55 | [x] Write test: `compute_channel_vector([],[],[],[])` returns `[0,0,0,0]` | Test passes |
| 12.56 | [x] Write test: `compute_channel_vector(["on"],[],["on"],[])` returns `[1,0,1,0]` | Test passes |

---

## Phase 13 · App Entry Point

| # | Task | Definition of Done |
|---|------|--------------------|
| 13.01 | [x] Create `src/fourier/ui/app.py` — Dash app initialization | File exists |
| 13.02 | [x] Write test: `from fourier.ui.app import create_app` returns Dash instance | Test passes |
| 13.03 | [x] Implement `create_app()` — creates `Dash(__name__)`, sets title, builds layout, registers callbacks | Returns app |
| 13.04 | [x] Write test: `app.title == "Fourier Synthesis"` | Test passes |
| 13.05 | [x] Write test: `app.layout` is not None | Test passes |
| 13.06 | [x] Create `src/fourier/__main__.py` — entry point | File exists |
| 13.07 | [x] Implement `__main__.py` — calls `create_app()`, reads host/port/debug from config, runs | `uv run python -m fourier` launches app |
| 13.08 | [x] Add script entry `fourier-app = "fourier.__main__:main"` to `pyproject.toml` | `uv run fourier-app` works |
| 13.09 | [x] Write test: debug mode read from `app_config.json['debug']` | Test passes |
| 13.10 | [x] Write test: port read from `app_config.json['port']` | Test passes |
| 13.11 | [x] Write test: host read from `app_config.json['host']` | Test passes |
| 13.12 | [x] Run ruff on `app.py` and `__main__.py` — zero violations | Exit code 0 |
| 13.13 | [x] Check both files ≤ 150 lines | Passes |

---

## Phase 14 · Integration Tests

| # | Task | Definition of Done |
|---|------|--------------------|
| 14.01 | [x] Create `tests/integration/test_full_identify_flow.py` | File exists |
| 14.02 | [x] Write integration test: RNN end-to-end — generate signal → extract window → classify → get ClassifierResult | Test passes |
| 14.03 | [x] Write integration test: LSTM end-to-end — same pipeline | Test passes |
| 14.04 | [x] Write integration test: Both mode — two ClassifierResults + DiffResult produced | Test passes |
| 14.05 | [x] Write integration test: window at `t=0.0` (left boundary) — no index error | Test passes |
| 14.06 | [x] Write integration test: window at `t=9.0` (right boundary) — no index error | Test passes |
| 14.07 | [x] Write integration test: all channels disabled — identify on zero signal — no crash | Test passes |
| 14.08 | [x] Write integration test: single channel enabled — classifier returns valid result | Test passes |
| 14.09 | [x] Write integration test: reset restores all default slider values | Test passes |
| 14.10 | [x] Write integration test: enabling dots mode shows sr slider | Test passes |
| 14.11 | [x] Write integration test: disabling dots mode hides sr slider | Test passes |
| 14.12 | [x] Write integration test: disabling channel hides wave controls | Test passes |
| 14.13 | [x] Write integration test: re-enabling channel shows wave controls | Test passes |
| 14.14 | [x] Write integration test: gatekeeper retries once on transient failure | Test passes |
| 14.15 | [x] Write integration test: gatekeeper raises after max_retries failures | Test passes |
| 14.16 | [x] Write integration test: agreement=True when both classifiers match | Test passes |
| 14.17 | [x] Write integration test: agreement=False when classifiers disagree | Test passes |
| 14.18 | [x] Write integration test: confidence_delta=0 when both have same confidence | Test passes |
| 14.19 | [x] Write integration test: app startup fails with clear error on missing config key | Test passes |
| 14.20 | [x] Write integration test: VERSION in README matches `version.py` | Test passes |
| 14.21 | [x] Write integration test: no hardcoded values in `src/` (grep scan in test) | Test passes |
| 14.22 | [x] Write integration test: noise_sigma=0.0 and noise_sigma=0.3 produce different classifier inputs | Test passes |
| 14.23 | [x] Write integration test: noise label updates to "Heavy" when noise-slider set to 0.5 | Test passes |
| 14.24 | [x] Write integration test: noise_sigma > 0.5 raises `ValueError` in `WindowExtractor` | Test passes |

---

## Phase 15 · Quality Gates

| # | Task | Definition of Done |
|---|------|--------------------|
| 15.01 | [x] Run `uv run ruff check src/` — zero violations | Exit code 0 |
| 15.02 | [x] Fix any Ruff violations in `sdk/` | Exit code 0 |
| 15.03 | [x] Fix any Ruff violations in `services/` | Exit code 0 |
| 15.04 | [x] Fix any Ruff violations in `ui/` | Exit code 0 |
| 15.05 | [x] Fix any Ruff violations in `gatekeeper.py` | Exit code 0 |
| 15.06 | [x] Fix any Ruff violations in `shared/` | Exit code 0 |
| 15.07 | [x] Run `uv run pytest --cov=src --cov-fail-under=85` | Exit code 0 |
| 15.08 | [x] Identify any module below 85% coverage | `callbacks_server.py` split — total 93.37% |
| 15.09 | [x] Add missing unit tests for `sdk/` coverage gaps | Coverage ≥ 85% |
| 15.10 | [x] Add missing unit tests for `ui/` coverage gaps | Coverage ≥ 85% |
| 15.11 | [x] Add missing unit tests for `gatekeeper.py` coverage gaps | Coverage ≥ 85% |
| 15.12 | [x] Verify all `src/` files are ≤ 150 lines (line count scan) | `callbacks_server.py` split into `callbacks_identify.py` + `callbacks_result.py` |
| 15.13 | [x] Verify zero hardcoded URLs in `src/` | Grep scan clean |
| 15.14 | [x] Verify zero hardcoded timeouts in `src/` | Grep scan clean |
| 15.15 | [x] Verify zero hardcoded port/host values in `src/` | Grep scan clean |
| 15.16 | [x] Verify `.env` is in `.gitignore` and not tracked by git | `git status` clean |
| 15.17 | [x] Run full test suite — all tests green | 226 passed, 0 failures |
| 15.18 | [x] Generate coverage HTML report | `htmlcov/` directory created |

---

## Phase 16 · Research Notebook

| # | Task | Definition of Done |
|---|------|--------------------|
| 16.01 | [x] Create `notebooks/analysis.ipynb` — blank notebook | File exists |
| 16.02 | [x] Add import cell: numpy, plotly, torch, json, pathlib | Cell runs without error |
| 16.03 | [x] Add config cell: load and display `app_config.json` | Cell runs, config printed |
| 16.04 | [x] Add markdown cell: Section 1 title — "Fourier Synthesis: Mathematical Foundation" | Cell rendered |
| 16.05 | [x] Add LaTeX cell: continuous signal formula $y(t) = A \cdot \sin(2\pi f t + \varphi)$ | LaTeX renders correctly |
| 16.06 | [x] Add LaTeX cell: discrete sampling formula $y[n] = A \cdot \sin(2\pi f \tfrac{n}{sr} + \varphi)$ | LaTeX renders |
| 16.07 | [x] Add LaTeX cell: summation formula $Y(t) = \sum_{i=1}^{4} y_i(t)$ | LaTeX renders |
| 16.08 | [x] Add code cell: generate and plot all 4 default channels | Plot displayed |
| 16.09 | [x] Add code cell: plot summation signal | Plot displayed |
| 16.10 | [x] Add markdown cell: Section 2 — "RNN Architecture" | Cell rendered |
| 16.11 | [x] Add LaTeX cell: RNN forward equation $h_t = \tanh(W \cdot [x_t, h_{t-1}] + b)$ | LaTeX renders |
| 16.12 | [x] Add LaTeX cell: Vanishing gradient explanation $\|\partial L / \partial h_0\| \to 0$ | LaTeX renders |
| 16.13 | [x] Add markdown cell: Section 3 — "LSTM Architecture" | Cell rendered |
| 16.14 | [x] Add LaTeX cell: Forget gate $f_t = \sigma(W_f \cdot [h_{t-1}, x_t] + b_f)$ | LaTeX renders |
| 16.15 | [x] Add LaTeX cell: Input gate $i_t = \sigma(W_i \cdot [h_{t-1}, x_t] + b_i)$ | LaTeX renders |
| 16.16 | [x] Add LaTeX cell: Cell state update $C_t = f_t \odot C_{t-1} + i_t \odot \tilde{C}_t$ | LaTeX renders |
| 16.17 | [x] Add LaTeX cell: Output gate $h_t = o_t \odot \tanh(C_t)$ | LaTeX renders |
| 16.18 | [x] Add markdown cell: Section 4 — "Sensitivity Analysis" | Cell rendered |
| 16.19 | [x] Add code cell: sensitivity — vary amplitude (0 to 100), plot max signal value | Plot displayed |
| 16.20 | [x] Add code cell: sensitivity — vary frequency (0.1 to 5.0 Hz), overlay plots | Plot displayed |
| 16.21 | [x] Add code cell: sensitivity — vary phase (0 to 2π), overlay plots | Plot displayed |
| 16.22 | [x] Add code cell: sensitivity — vary sampling rate, show aliasing artifacts | Plot displayed |
| 16.23 | [x] Add code cell: high-resolution overlay chart (1200×600 px, publication quality) | Saved as `overlay_hires.html` |
| 16.24 | [x] Add code cell: high-resolution summation chart | Saved as `summation_hires.html` |
| 16.25 | [x] Add code cell: windowed segment highlighted on summation chart | Saved as `summation_windowed.html` |
| 16.26 | [x] Add markdown cell: Section 5 — "Cost Analysis" | Cell rendered |
| 16.27 | [x] Add table cell: token usage table (Input tokens, Output tokens, Estimated cost) | Table rendered |
| 16.28 | [x] Run entire notebook end-to-end — all cells execute without error | No exceptions |
| 16.29 | [x] Save notebook with all output cells populated | File saved with outputs |

---

## Phase 17 · Documentation Finalization

| # | Task | Definition of Done |
|---|------|--------------------|
| 17.01 | [x] Update `README.md` Section 1 — project identity, tagline, VERSION = "1.00" | Written |
| 17.02 | [x] Update `README.md` Section 2 — tech stack (Dash, Plotly, PyTorch, NumPy, uv, Ruff, pytest) | Written |
| 17.03 | [x] Update `README.md` Section 3 — Installation (uv only; pip is forbidden) | Written |
| 17.04 | [x] Document install step: `git clone <repo>` | Written |
| 17.05 | [x] Document install step: `uv sync` | Written |
| 17.06 | [x] Document install step: `cp .env-example .env` | Written |
| 17.07 | [x] Document run step: `uv run fourier-app` | Written |
| 17.08 | [x] Update `README.md` Section 4 — Configuration guide | Written |
| 17.09 | [x] Document every `app_config.json` key, type, and valid value range | Written |
| 17.10 | [x] Document every `rate_limits.json` key, type, and valid value range | Written |
| 17.11 | [x] Update `README.md` Section 5 — Usage: Signal Synthesis | Written |
| 17.12 | [x] Document: how to enable/disable individual channels | Written |
| 17.13 | [x] Document: how to adjust frequency, amplitude, phase sliders | Written |
| 17.14 | [x] Document: how to enable dots (discrete sampling) mode | Written |
| 17.15 | [x] Document: how to read the discrete vector `y[n]` display | Written |
| 17.16 | [x] Update `README.md` Section 6 — Usage: ML Identification | Written |
| 17.17 | [x] Document: how to select a 1-second window on the summation chart | Written |
| 17.18 | [x] Document: how to choose RNN vs LSTM vs Both | Written |
| 17.19 | [x] Document: how to read the single-algorithm results panel | Written |
| 17.20 | [x] Document: how to read the Both-mode diff summary panel | Written |
| 17.21 | [x] Update `README.md` Section 7 — Documentation map (links to all DOCS/ files) | Written |
| 17.22 | [x] Update `README.md` Section 8 — Directory blueprint matching PLAN.md | Written |
| 17.23 | [x] Update `README.md` Section 9 — Contributing (uv, ruff, pytest, 150-line rule) | Written |
| 17.24 | [x] Add `ENTRY-005` to `DOCS/Prompt_Log.md` — Training scripts | Already present as ENTRY-004 |
| 17.25 | [x] Add `ENTRY-006` to `DOCS/Prompt_Log.md` — UI server callbacks | Already present as ENTRY-004 |
| 17.26 | [x] Add `ENTRY-007` to `DOCS/Prompt_Log.md` — Research notebook | Added as ENTRY-011 |
| 17.27 | [x] Add `ENTRY-008` to `DOCS/Prompt_Log.md` — Quality gates and final fixes | Added as ENTRY-010 |

---

## Phase 18 · Deployment Hardening & Final Checks

| # | Task | Definition of Done |
|---|------|--------------------|
| 18.01 | [x] Verify debug mode is read from `app_config.json` — not hardcoded | Grep scan clean |
| 18.02 | [x] Verify host is read from `app_config.json` — not hardcoded | Grep scan clean |
| 18.03 | [x] Verify port is read from `app_config.json` — not hardcoded | Grep scan clean |
| 18.04 | [x] Add startup config validation call in `__main__.py` | Exits `SystemExit(1)` on missing key |
| 18.05 | [x] Write test: app exits with `SystemExit` if `app_config.json` is missing at startup | Test passes |
| 18.06 | [x] Write test: app exits with `SystemExit` if `rate_limits.json` is missing at startup | Test passes |
| 18.07 | [x] Verify all `torch.load` calls use `weights_only=True` (PyTorch security best practice) | Confirmed in `rnn_classifier.py` and `lstm_classifier.py` |
| 18.08 | [x] Verify no `eval()` or `exec()` calls in `src/` | `model.eval()` is PyTorch API — not Python `eval()` |
| 18.09 | [x] Verify no secrets or API keys committed to repo | `.env` in `.gitignore`, no keys in source |
| 18.10 | [x] Check `models/` directory is in `.gitignore` if weight files are large (>50 MB) | `*.pt` in `.gitignore`; files are < 1 MB |
| 18.11 | [x] Run full test suite one final time — all tests green | 227 passed, 0 failures |
| 18.12 | [x] Run `uv run ruff check src/` final pass — zero violations | Exit code 0 |
| 18.13 | [x] Run `uv run pytest --cov=src --cov-report=term-missing` — coverage ≥ 85% | 93.37% |
| 18.14 | [x] Verify every INSTRUCTIONS.md requirement is satisfied | All requirements met |
| 18.15 | [x] Bump VERSION to "1.01" in `version.py` and `app_config.json` after all features complete | Both files updated |
| 18.16 | [x] Git tag `v1.00` release commit | Tag present in git log |

---

*Total tasks: 507 — all must pass before the project is considered complete.*
