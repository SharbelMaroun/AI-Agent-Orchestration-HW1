from __future__ import annotations

import time
from typing import Any, Callable


class RateLimitError(Exception):
    pass


class ModelGatekeeper:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self._validate_config()
        self._call_log: list[float] = []

    def _validate_config(self) -> None:
        for key in ("max_calls_per_minute", "max_retries", "retry_delay_seconds", "timeout_seconds"):
            if key not in self.config:
                raise KeyError(f"Missing required config key: {key}")

    def _check_rate_limit(self) -> None:
        now = time.time()
        self._call_log = [t for t in self._call_log if now - t < 60.0]
        if len(self._call_log) >= int(self.config["max_calls_per_minute"]):
            raise RateLimitError("Rate limit exceeded: too many calls per minute")
        self._call_log.append(now)

    def _log_call(self, attempt: int, status: str) -> None:
        ts = time.strftime("%H:%M:%S")
        print(f"[{ts}] attempt={attempt} status={status}")

    def _execute_with_retry(self, fn: Callable, *args: Any, **kwargs: Any) -> Any:
        max_retries = int(self.config["max_retries"])
        last_exc: RuntimeError | None = None
        for attempt in range(1, max_retries + 2):
            try:
                result = fn(*args, **kwargs)
                self._log_call(attempt, "success")
                return result
            except RuntimeError as exc:
                last_exc = exc
                self._log_call(attempt, f"retry {attempt}: {exc}")
        print(f"Failed after {max_retries} retries")
        raise last_exc  # type: ignore[misc]

    def call(self, fn: Callable, *args: Any, **kwargs: Any) -> Any:
        self._check_rate_limit()
        return self._execute_with_retry(fn, *args, **kwargs)
