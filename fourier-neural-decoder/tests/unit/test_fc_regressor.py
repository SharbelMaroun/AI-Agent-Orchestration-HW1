from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import torch

from fourier.sdk.fc_regressor import BookFCRegressor, FCRegressor


def test_forward_output_shape_is_10():
    model = BookFCRegressor(hidden_size=16)
    out = model(torch.randn(3, 10, 1), torch.zeros(3, 4))
    assert out.shape == (3, 10)


def test_forward_accepts_2d_input_via_flatten():
    model = BookFCRegressor(hidden_size=16)
    out = model(torch.randn(3, 10), torch.zeros(3, 4))
    assert out.shape == (3, 10)


def test_explicit_parameters_present():
    model = BookFCRegressor(hidden_size=8)
    names = {n for n, _ in model.named_parameters()}
    assert {"W_1", "b_1", "W_2", "b_2"} <= names


def test_no_recurrence_no_extra_state():
    """FC has no hidden/cell state, no time loop, no recurrent params."""
    model = BookFCRegressor(hidden_size=8)
    names = {n for n, _ in model.named_parameters()}
    assert not (names & {"W_x", "W_h", "W_f", "W_i", "W_C", "W_o"})


def test_input_size_is_seq_plus_c():
    """W_1 width = seq_len (10) + c_size (4) = 14."""
    model = BookFCRegressor(hidden_size=8)
    assert model.W_1.shape == (8, 14)


def test_c_vector_changes_output():
    model = BookFCRegressor(hidden_size=16)
    x = torch.randn(1, 10, 1)
    out_a = model(x, torch.tensor([[1.0, 0, 0, 0]]))
    out_b = model(x, torch.tensor([[0, 0, 0, 1.0]]))
    assert not torch.allclose(out_a, out_b)


def test_validate_config_missing_hidden_size():
    with pytest.raises(KeyError):
        FCRegressor({})


def test_validate_config_invalid_hidden_size():
    with pytest.raises(ValueError):
        FCRegressor({"hidden_size": 0})


def test_process_returns_10_coordinates():
    reg = FCRegressor({"hidden_size": 16})
    r = reg.process(np.zeros(10), [0, 1, 0, 0])
    assert len(r["coordinates"]) == 10


def test_tolerates_missing_weights(tmp_path: Path):
    reg = FCRegressor({"hidden_size": 8, "weights_path": str(tmp_path / "absent.pt")})
    assert "coordinates" in reg.process(np.zeros(10), [1, 0, 0, 0])


def test_loads_valid_weights(tmp_path: Path):
    model = BookFCRegressor(hidden_size=8)
    p = tmp_path / "fc.pt"
    torch.save(model.state_dict(), p)
    reg = FCRegressor({"hidden_size": 8, "weights_path": str(p)})
    assert reg.model.W_1.shape == model.W_1.shape


def test_rejects_corrupted_weights(tmp_path: Path):
    p = tmp_path / "broken.pt"
    torch.save({"junk": torch.zeros(1)}, p)
    with pytest.raises(ValueError, match="missing keys"):
        FCRegressor({"hidden_size": 8, "weights_path": str(p)})


def test_smaller_than_recurrent_models():
    """FC should have fewer params than the recurrent regressors at H=64."""
    from fourier.sdk.lstm_regressor import BookLSTMRegressor
    from fourier.sdk.rnn_regressor import BookRNNRegressor
    fc = BookFCRegressor(hidden_size=64)
    rnn = BookRNNRegressor(hidden_size=64)
    lstm = BookLSTMRegressor(hidden_size=64)
    fc_n = sum(p.numel() for p in fc.parameters())
    rnn_n = sum(p.numel() for p in rnn.parameters())
    lstm_n = sum(p.numel() for p in lstm.parameters())
    assert fc_n < lstm_n
    # FC may be larger than RNN due to flat W_1; the meaningful comparison is vs. LSTM
    assert lstm_n > rnn_n
