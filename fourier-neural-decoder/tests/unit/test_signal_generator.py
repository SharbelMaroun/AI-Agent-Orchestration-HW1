import math

import numpy as np
import pytest

from fourier.shared.constants import DURATION, PI2, RESOLUTION
from fourier.sdk.signal_generator import SignalGenerator


def _base_config() -> dict[str, float]:
    return {"frequency": 0.5, "amplitude": 50.0, "phase": 0.0, "sampling_rate": 20.0}


def test_signal_generator_init_accepts_config_dict() -> None:
    generator = SignalGenerator(_base_config())
    assert isinstance(generator.config, dict)


@pytest.mark.parametrize("missing_key", ["frequency", "amplitude", "phase", "sampling_rate"])
def test_validate_config_raises_key_error_for_missing_key(missing_key: str) -> None:
    config = _base_config()
    config.pop(missing_key)
    with pytest.raises(KeyError):
        SignalGenerator(config)


def test_validate_config_raises_value_error_for_negative_amplitude() -> None:
    config = _base_config()
    config["amplitude"] = -1
    with pytest.raises(ValueError):
        SignalGenerator(config)


def test_validate_config_raises_value_error_for_non_positive_frequency() -> None:
    config = _base_config()
    config["frequency"] = 0
    with pytest.raises(ValueError):
        SignalGenerator(config)


def test_validate_config_raises_value_error_for_low_sampling_rate() -> None:
    config = _base_config()
    config["sampling_rate"] = 0.5
    with pytest.raises(ValueError):
        SignalGenerator(config)


def test_process_contains_continuous_key() -> None:
    result = SignalGenerator(_base_config()).process()
    assert "continuous" in result


def test_process_contains_discrete_key() -> None:
    result = SignalGenerator(_base_config()).process()
    assert "discrete" in result


def test_continuous_length_is_resolution_plus_one() -> None:
    continuous = SignalGenerator(_base_config()).process()["continuous"]
    assert len(continuous) == RESOLUTION + 1


def test_continuous_values_are_floats() -> None:
    continuous = SignalGenerator(_base_config()).process()["continuous"]
    assert np.issubdtype(continuous.dtype, np.floating)


def test_zero_amplitude_continuous_is_all_zeros() -> None:
    config = _base_config()
    config["amplitude"] = 0
    continuous = SignalGenerator(config).process()["continuous"]
    assert np.allclose(continuous, 0.0)


def test_zero_amplitude_discrete_is_all_zeros() -> None:
    config = _base_config()
    config["amplitude"] = 0
    discrete = SignalGenerator(config).process()["discrete"]["y"]
    assert np.allclose(discrete, 0.0)


def test_discrete_length_matches_duration_sampling_rate() -> None:
    config = _base_config()
    config["sampling_rate"] = 7
    discrete = SignalGenerator(config).process()["discrete"]["y"]
    expected = int(math.floor(DURATION * config["sampling_rate"])) + 1
    assert len(discrete) == expected


def test_discrete_first_sample_matches_amp_sin_phase() -> None:
    config = _base_config()
    config["phase"] = math.pi / 3
    discrete = SignalGenerator(config).process()["discrete"]["y"]
    assert discrete[0] == pytest.approx(config["amplitude"] * math.sin(config["phase"]))


def test_phase_shift_offsets_signal() -> None:
    config_zero_phase = _base_config()
    config_shifted_phase = _base_config()
    config_shifted_phase["phase"] = math.pi / 2
    y_zero = SignalGenerator(config_zero_phase).process()["continuous"]
    y_shifted = SignalGenerator(config_shifted_phase).process()["continuous"]
    assert y_shifted[0] == pytest.approx(config_shifted_phase["amplitude"])
    assert y_zero[0] == pytest.approx(0.0)


def test_frequency_half_hz_zero_crossing_near_one_second() -> None:
    generator = SignalGenerator(_base_config())
    time = generator._build_time_axis()
    continuous = generator.process()["continuous"]
    index = int(np.argmin(np.abs(time - 1.0)))
    assert time[index] == pytest.approx(1.0)
    assert continuous[index] == pytest.approx(0.0, abs=1e-8)


def test_sampling_rate_one_hz_has_eleven_samples() -> None:
    config = _base_config()
    config["sampling_rate"] = 1
    discrete = SignalGenerator(config).process()["discrete"]["y"]
    assert len(discrete) == 11


def test_sampling_rate_fifty_hz_has_five_hundred_one_samples() -> None:
    config = _base_config()
    config["sampling_rate"] = 50
    discrete = SignalGenerator(config).process()["discrete"]["y"]
    assert len(discrete) == 501


def test_amplitude_hundred_stays_within_range() -> None:
    config = _base_config()
    config["amplitude"] = 100
    result = SignalGenerator(config).process()
    continuous = result["continuous"]
    discrete = result["discrete"]["y"]
    assert np.max(continuous) <= 100.0 + 1e-8
    assert np.min(continuous) >= -100.0 - 1e-8
    assert np.max(discrete) <= 100.0 + 1e-8
    assert np.min(discrete) >= -100.0 - 1e-8


def test_compute_continuous_uses_expected_formula() -> None:
    config = _base_config()
    generator = SignalGenerator(config)
    t = np.array([0.0, 0.25], dtype=float)
    expected = config["amplitude"] * np.sin(PI2 * config["frequency"] * t + config["phase"])
    assert np.allclose(generator._compute_continuous(t), expected)


def test_compute_discrete_uses_expected_formula() -> None:
    config = _base_config()
    generator = SignalGenerator(config)
    t = np.array([0.0, 0.5], dtype=float)
    expected = config["amplitude"] * np.sin(PI2 * config["frequency"] * t + config["phase"])
    assert np.allclose(generator._compute_discrete(t), expected)
