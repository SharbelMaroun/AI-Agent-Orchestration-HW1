from __future__ import annotations

import pytest

from fourier.gatekeeper import Gatekeeper


def test_gatekeeper_passes_through_successful_call():
    gk = Gatekeeper()
    assert gk.process("add", lambda a, b: a + b, 2, 3) == 5
    assert gk.call_count == 1


def test_gatekeeper_validates_negative_config():
    with pytest.raises(ValueError):
        Gatekeeper({"max_retries": -1})


def test_gatekeeper_retries_then_succeeds():
    state = {"attempts": 0}

    def flaky():
        state["attempts"] += 1
        if state["attempts"] < 2:
            raise RuntimeError("transient")
        return "ok"

    gk = Gatekeeper({"max_retries": 2})
    assert gk.process("flaky", flaky) == "ok"
    assert state["attempts"] == 2


def test_gatekeeper_reraises_after_exhausting_retries():
    def always_fails():
        raise RuntimeError("permanent")

    gk = Gatekeeper({"max_retries": 1})
    with pytest.raises(RuntimeError, match="permanent"):
        gk.process("fail", always_fails)


def test_gatekeeper_call_count_increments():
    gk = Gatekeeper()
    for _ in range(3):
        gk.process("noop", lambda: None)
    assert gk.call_count == 3
