from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import torch

from fourier.sdk.rnn_regressor import BookRNNRegressor, RNNRegressor


def test_forward_output_shape_is_10():
    model = BookRNNRegressor(hidden_size=16)
    out = model(torch.randn(3, 10, 1), torch.zeros(3, 4))
    assert out.shape == (3, 10)


def test_explicit_parameters_present():
    model = BookRNNRegressor(hidden_size=8)
    names = {n for n, _ in model.named_parameters()}
    assert {"W_x", "W_h", "b", "W_y", "b_y"} <= names


def test_input_size_includes_c_vector():
    """Input width = 1 (sample) + 4 (C one-hot) = 5."""
    model = BookRNNRegressor(hidden_size=8)
    assert model.W_x.shape == (8, 5)


def test_c_vector_changes_output():
    """Different C vectors must lead to different outputs (NN must use C)."""
    model = BookRNNRegressor(hidden_size=16)
    x = torch.randn(1, 10, 1)
    out_a = model(x, torch.tensor([[1.0, 0, 0, 0]]))
    out_b = model(x, torch.tensor([[0, 0, 0, 1.0]]))
    assert not torch.allclose(out_a, out_b)


def test_validate_config_missing_hidden_size():
    with pytest.raises(KeyError):
        RNNRegressor({})


def test_validate_config_invalid_hidden_size():
    with pytest.raises(ValueError):
        RNNRegressor({"hidden_size": 0})


def test_process_returns_10_coordinates():
    reg = RNNRegressor({"hidden_size": 16})
    r = reg.process(np.zeros(10), [0, 1, 0, 0])
    assert len(r["coordinates"]) == 10
    assert all(isinstance(v, float) for v in r["coordinates"])


def test_tolerates_missing_weights(tmp_path: Path):
    cfg = {"hidden_size": 8, "weights_path": str(tmp_path / "absent.pt")}
    reg = RNNRegressor(cfg)
    r = reg.process(np.zeros(10), [1, 0, 0, 0])
    assert "coordinates" in r


def test_loads_valid_weights(tmp_path: Path):
    model = BookRNNRegressor(hidden_size=8)
    p = tmp_path / "rnn.pt"
    torch.save(model.state_dict(), p)
    reg = RNNRegressor({"hidden_size": 8, "weights_path": str(p)})
    assert reg.model.W_x.shape == model.W_x.shape


def test_rejects_corrupted_weights(tmp_path: Path):
    p = tmp_path / "broken.pt"
    torch.save({"junk": torch.zeros(1)}, p)
    with pytest.raises(ValueError, match="missing keys"):
        RNNRegressor({"hidden_size": 8, "weights_path": str(p)})
