from __future__ import annotations

from unittest.mock import patch

import pytest

from fourier.gatekeeper import ModelGatekeeper, RateLimitError


def _base_config(**overrides):
    cfg = {
        "max_calls_per_minute": 60,
        "max_retries": 3,
        "retry_delay_seconds": 0.0,
        "timeout_seconds": 10,
    }
    cfg.update(overrides)
    return cfg


def test_init_loads_config():
    gk = ModelGatekeeper(_base_config())
    assert gk.config["max_calls_per_minute"] == 60


def test_validate_config_raises_on_missing_max_calls():
    with pytest.raises(KeyError):
        ModelGatekeeper({"max_retries": 3, "retry_delay_seconds": 0.5, "timeout_seconds": 10})


def test_validate_config_raises_on_missing_max_retries():
    with pytest.raises(KeyError):
        ModelGatekeeper({"max_calls_per_minute": 60, "retry_delay_seconds": 0.5, "timeout_seconds": 10})


def test_validate_config_raises_on_missing_retry_delay():
    with pytest.raises(KeyError):
        ModelGatekeeper({"max_calls_per_minute": 60, "max_retries": 3, "timeout_seconds": 10})


def test_validate_config_raises_on_missing_timeout():
    with pytest.raises(KeyError):
        ModelGatekeeper({"max_calls_per_minute": 60, "max_retries": 3, "retry_delay_seconds": 0.5})


def test_call_invokes_fn_with_args():
    gk = ModelGatekeeper(_base_config())
    result = gk.call(lambda a, b: a + b, 3, 4)
    assert result == 7


def test_call_returns_fn_result():
    gk = ModelGatekeeper(_base_config())
    assert gk.call(lambda: 42) == 42


def test_call_passes_kwargs():
    gk = ModelGatekeeper(_base_config())
    result = gk.call(lambda x, y=0: x * y, 5, y=3)
    assert result == 15


def test_call_retries_on_runtime_error():
    gk = ModelGatekeeper(_base_config(max_retries=2))
    calls = {"count": 0}

    def flaky():
        calls["count"] += 1
        if calls["count"] < 3:
            raise RuntimeError("transient")
        return "ok"

    assert gk.call(flaky) == "ok"
    assert calls["count"] == 3


def test_call_raises_after_max_retries_exhausted():
    gk = ModelGatekeeper(_base_config(max_retries=2))

    def always_fails():
        raise RuntimeError("always")

    with pytest.raises(RuntimeError):
        gk.call(always_fails)


def test_call_logs_each_attempt(capsys):
    gk = ModelGatekeeper(_base_config(max_retries=1))
    calls = {"n": 0}

    def fails_once():
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("fail")
        return "ok"

    gk.call(fails_once)
    out = capsys.readouterr().out
    assert "attempt=" in out


def test_call_logs_retry_number(capsys):
    gk = ModelGatekeeper(_base_config(max_retries=2))
    calls = {"n": 0}

    def fails_twice():
        calls["n"] += 1
        if calls["n"] <= 2:
            raise RuntimeError("fail")
        return "ok"

    gk.call(fails_twice)
    out = capsys.readouterr().out
    assert "retry" in out


def test_call_logs_final_failure_message(capsys):
    gk = ModelGatekeeper(_base_config(max_retries=1))

    with pytest.raises(RuntimeError):
        gk.call(lambda: (_ for _ in ()).throw(RuntimeError("x")))

    out = capsys.readouterr().out
    assert "Failed" in out or "retry" in out


def test_rate_limit_raises_rate_limit_error():
    gk = ModelGatekeeper(_base_config(max_calls_per_minute=2))
    gk.call(lambda: None)
    gk.call(lambda: None)
    with pytest.raises(RateLimitError):
        gk.call(lambda: None)


def test_call_count_resets_after_60_seconds():
    with patch("fourier.gatekeeper.time.time", return_value=1000.0):
        gk = ModelGatekeeper(_base_config(max_calls_per_minute=1))
        gk.call(lambda: None)
    with patch("fourier.gatekeeper.time.time", return_value=1062.0):
        gk.call(lambda: None)
