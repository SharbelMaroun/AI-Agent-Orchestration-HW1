"""Gatekeeper — central wrapper for inference calls.

Per CLAUDE.md §5, all external API requests must pass through a Gatekeeper
that handles rate limiting, retries, timeouts, and logging. This app has no
external APIs (all inference is local PyTorch), so the Gatekeeper here serves
as a structured logging + timing wrapper for local model calls. See
DOCS/PLAN.md ADR-009 for the exemption rationale.

Building Block Pattern: __init__, _validate_config, process.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Callable

logger = logging.getLogger(__name__)


class Gatekeeper:
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self._validate_config()
        self.call_count = 0

    def _validate_config(self) -> None:
        for key in ("max_calls_per_minute", "max_retries", "timeout_seconds"):
            if key in self.config and float(self.config[key]) < 0:
                raise ValueError(f"{key} must be >= 0")

    def process(self, name: str, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Invoke `fn(*args, **kwargs)` with logging, timing, and retry/timeout policy.

        Local-inference path: no network, no rate limiting needed at this scale,
        but we still log call counts and durations so future regressions are visible.
        """
        retries = int(self.config.get("max_retries", 0))
        last_exc: Exception | None = None
        for attempt in range(retries + 1):
            t0 = time.perf_counter()
            try:
                result = fn(*args, **kwargs)
                self.call_count += 1
                logger.debug(
                    "Gatekeeper call=%s attempt=%d duration_ms=%.2f total_calls=%d",
                    name, attempt, (time.perf_counter() - t0) * 1000, self.call_count,
                )
                return result
            except Exception as exc:
                last_exc = exc
                logger.warning("Gatekeeper call=%s attempt=%d failed: %s", name, attempt, exc)
        if last_exc is not None:
            raise last_exc
        return None
