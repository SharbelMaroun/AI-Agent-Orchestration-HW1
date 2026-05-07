from __future__ import annotations

from fourier.ui.callbacks_server import compute_channel_vector


def test_compute_channel_vector_all_enabled():
    assert compute_channel_vector(["on"], ["on"], ["on"], ["on"]) == [1, 1, 1, 1]


def test_compute_channel_vector_all_disabled():
    assert compute_channel_vector([], [], [], []) == [0, 0, 0, 0]


def test_compute_channel_vector_mixed():
    assert compute_channel_vector(["on"], [], ["on"], []) == [1, 0, 1, 0]
