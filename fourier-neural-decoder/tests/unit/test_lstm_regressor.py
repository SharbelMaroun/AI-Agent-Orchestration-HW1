from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import torch

from fourier.sdk.lstm_regressor import BookLSTMRegressor, LSTMRegressor


def test_forward_output_shape_is_10():
    model = BookLSTMRegressor(hidden_size=16)
    out = model(torch.randn(3, 10, 1), torch.zeros(3, 4))
    assert out.shape == (3, 10)


def test_four_separate_gate_parameters():
    model = BookLSTMRegressor(hidden_size=8)
    names = {n for n, _ in model.named_parameters()}
    assert {"W_f", "W_i", "W_C", "W_o"} <= names
    assert {"b_f", "b_i", "b_C", "b_o"} <= names


def test_forget_bias_initialised_to_one():
    model = BookLSTMRegressor(hidden_size=8)
    assert torch.allclose(model.b_f, torch.ones(8))
    assert torch.allclose(model.b_i, torch.zeros(8))


def test_concatenated_input_dimensions():
    """z_t = [h_{t-1}, sample_t, C₀..C₃]; gate width = H + 1 + 4."""
    H = 8
    model = BookLSTMRegressor(hidden_size=H)
    assert model.W_f.shape == (H, H + 1 + 4)


def test_c_vector_changes_output():
    model = BookLSTMRegressor(hidden_size=16)
    x = torch.randn(1, 10, 1)
    out_a = model(x, torch.tensor([[1.0, 0, 0, 0]]))
    out_b = model(x, torch.tensor([[0, 0, 1.0, 0]]))
    assert not torch.allclose(out_a, out_b)


def test_validate_config_missing_hidden_size():
    with pytest.raises(KeyError):
        LSTMRegressor({})


def test_validate_config_invalid_hidden_size():
    with pytest.raises(ValueError):
        LSTMRegressor({"hidden_size": -1})


def test_process_returns_10_coordinates():
    reg = LSTMRegressor({"hidden_size": 16})
    r = reg.process(np.zeros(10), [0, 0, 1, 0])
    assert len(r["coordinates"]) == 10


def test_tolerates_missing_weights(tmp_path: Path):
    cfg = {"hidden_size": 8, "weights_path": str(tmp_path / "absent.pt")}
    reg = LSTMRegressor(cfg)
    assert "coordinates" in reg.process(np.zeros(10), [0, 1, 0, 0])


def test_loads_valid_weights(tmp_path: Path):
    model = BookLSTMRegressor(hidden_size=8)
    p = tmp_path / "lstm.pt"
    torch.save(model.state_dict(), p)
    reg = LSTMRegressor({"hidden_size": 8, "weights_path": str(p)})
    assert reg.model.W_f.shape == model.W_f.shape


def test_rejects_corrupted_weights(tmp_path: Path):
    p = tmp_path / "broken.pt"
    torch.save({"junk": torch.zeros(1)}, p)
    with pytest.raises(ValueError, match="missing keys"):
        LSTMRegressor({"hidden_size": 8, "weights_path": str(p)})
