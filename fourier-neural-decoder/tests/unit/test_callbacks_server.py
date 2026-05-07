from __future__ import annotations

from fourier.ui.callbacks_server import compute_channel_vector, reset_cb_fn


def test_reset_cb_fn_returns_eight_noise_defaults():
    """Reset must include 4 alpha + 4 beta values appended after 6×4 = 24 prior outputs."""
    out = reset_cb_fn(None)
    assert len(out) == 24 + 8
    assert all(v == 0 for v in out[24:32])


def test_compute_channel_vector_all_enabled():
    assert compute_channel_vector(["on"], ["on"], ["on"], ["on"]) == [1, 1, 1, 1]


def test_compute_channel_vector_all_disabled():
    assert compute_channel_vector([], [], [], []) == [0, 0, 0, 0]


def test_compute_channel_vector_mixed():
    assert compute_channel_vector(["on"], [], ["on"], []) == [1, 0, 1, 0]
