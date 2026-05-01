from fourier.shared.constants import DEFAULTS, WAVE_NAMES


def test_first_wave_name() -> None:
    assert WAVE_NAMES[0] == "Fundamental"


def test_fourth_wave_name() -> None:
    assert WAVE_NAMES[3] == "Fourth Harmonic"


def test_defaults_entries_have_required_keys() -> None:
    expected_keys = {"amplitude", "frequency", "phase", "sampling_rate"}
    for channel_defaults in DEFAULTS:
        assert set(channel_defaults.keys()) == expected_keys


def test_first_default_amplitude() -> None:
    assert DEFAULTS[0]["amplitude"] == 50


def test_second_default_frequency() -> None:
    assert DEFAULTS[1]["frequency"] == 1.0


def test_fourth_default_sampling_rate() -> None:
    assert DEFAULTS[3]["sampling_rate"] == 20
