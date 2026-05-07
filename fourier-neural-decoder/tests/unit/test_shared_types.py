from fourier.shared.types import ChannelConfig, RegressorResult, WindowSlice


def test_channel_config_typed_dict_keys() -> None:
    expected_keys = {"amplitude", "frequency", "phase", "sampling_rate", "enabled"}
    assert set(ChannelConfig.__annotations__.keys()) == expected_keys


def test_window_slice_typed_dict_keys() -> None:
    expected_keys = {"window_start", "duration", "signal_values"}
    assert set(WindowSlice.__annotations__.keys()) == expected_keys


def test_regressor_result_typed_dict_keys() -> None:
    assert set(RegressorResult.__annotations__.keys()) == {"coordinates", "mae"}
