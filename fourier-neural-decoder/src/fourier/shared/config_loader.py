from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[3]
CONFIG_DIR = ROOT_DIR / "config"

APP_CONFIG_REQUIRED_KEYS = (
    "resolution",
    "duration",
    "debug",
    "host",
    "port",
    "version",
    "window_duration",
    "window_points",
    "noise_default",
    "noise_max",
)

RATE_LIMITS_REQUIRED_KEYS = (
    "max_calls_per_minute",
    "max_retries",
    "retry_delay_seconds",
    "timeout_seconds",
)


def _validate_keys(config: dict[str, Any], required_keys: tuple[str, ...]) -> None:
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise KeyError(f"Missing required config keys: {', '.join(missing_keys)}")


def _load_json_file(file_path: Path) -> dict[str, Any]:
    if not file_path.is_file():
        raise FileNotFoundError(f"Config file not found: {file_path}")

    try:
        with file_path.open("r", encoding="utf-8") as file:
            loaded = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed JSON in config file: {file_path}") from exc

    if not isinstance(loaded, dict):
        raise ValueError(f"Config root must be a JSON object: {file_path}")
    return loaded


def load_app_config(config_path: Path | None = None) -> dict[str, Any]:
    target_path = config_path or (CONFIG_DIR / "app_config.json")
    config = _load_json_file(target_path)
    _validate_keys(config, APP_CONFIG_REQUIRED_KEYS)
    return config


def load_rate_limits(config_path: Path | None = None) -> dict[str, Any]:
    target_path = config_path or (CONFIG_DIR / "rate_limits.json")
    config = _load_json_file(target_path)
    _validate_keys(config, RATE_LIMITS_REQUIRED_KEYS)
    return config
