from pathlib import Path

import pytest

from fourier.shared.config_loader import _validate_keys, load_app_config, load_rate_limits


def test_load_app_config_returns_dict() -> None:
    config = load_app_config()
    assert isinstance(config, dict)


def test_load_app_config_has_resolution() -> None:
    assert load_app_config()["resolution"] == 500


def test_load_app_config_has_duration() -> None:
    assert load_app_config()["duration"] == 10


def test_load_app_config_has_debug_false() -> None:
    assert load_app_config()["debug"] is False


def test_load_rate_limits_returns_dict() -> None:
    config = load_rate_limits()
    assert isinstance(config, dict)


def test_load_rate_limits_has_max_retries() -> None:
    assert load_rate_limits()["max_retries"] == 3


def test_missing_config_file_raises_file_not_found(tmp_path: Path) -> None:
    missing_file = tmp_path / "does_not_exist.json"
    with pytest.raises(FileNotFoundError):
        load_app_config(missing_file)


def test_malformed_json_raises_value_error(tmp_path: Path) -> None:
    bad_json = tmp_path / "malformed.json"
    bad_json.write_text("{bad json", encoding="utf-8")
    with pytest.raises(ValueError):
        load_rate_limits(bad_json)


def test_validate_keys_raises_key_error_on_missing_required_keys() -> None:
    with pytest.raises(KeyError):
        _validate_keys({"resolution": 500}, ("resolution", "duration"))


def test_validate_keys_passes_when_all_required_keys_exist() -> None:
    _validate_keys({"resolution": 500, "duration": 10}, ("resolution", "duration"))
