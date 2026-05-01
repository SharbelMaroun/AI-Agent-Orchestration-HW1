import numpy as np
import pytest

from fourier.sdk.window_extractor import WindowExtractor


def _base_config(window_start: float = 0.0) -> dict[str, float]:
    return {"window_start": window_start, "window_points": 50, "max_window_start": 9.0}


def _signal() -> np.ndarray:
    return np.arange(501, dtype=float)


def test_window_extractor_init_accepts_config_dict() -> None:
    extractor = WindowExtractor(_base_config())
    assert isinstance(extractor.config, dict)


def test_validate_config_raises_key_error_on_missing_window_start() -> None:
    with pytest.raises(KeyError):
        WindowExtractor({"window_points": 50})


def test_validate_config_raises_value_error_on_window_start_below_zero() -> None:
    with pytest.raises(ValueError):
        WindowExtractor(_base_config(window_start=-0.1))


def test_validate_config_raises_value_error_on_window_start_above_nine() -> None:
    with pytest.raises(ValueError):
        WindowExtractor(_base_config(window_start=9.1))


def test_process_returns_array_with_fifty_values() -> None:
    result = WindowExtractor(_base_config(window_start=0.0)).process(_signal())
    assert result.reshape(-1).size == 50


def test_slice_window_matches_correct_indices() -> None:
    extractor = WindowExtractor(_base_config(window_start=2.0))
    sliced = extractor._slice_window(_signal())
    assert np.array_equal(sliced, np.arange(100, 150, dtype=float))


def test_window_start_zero_extracts_first_fifty_points() -> None:
    extractor = WindowExtractor(_base_config(window_start=0.0))
    sliced = extractor._slice_window(_signal())
    assert np.array_equal(sliced, np.arange(0, 50, dtype=float))


def test_window_start_nine_extracts_last_fifty_points() -> None:
    extractor = WindowExtractor(_base_config(window_start=9.0))
    sliced = extractor._slice_window(_signal())
    assert np.array_equal(sliced, np.arange(451, 501, dtype=float))


def test_normalized_output_has_zero_mean() -> None:
    result = WindowExtractor(_base_config(window_start=0.0)).process(_signal())
    assert float(np.mean(result)) == pytest.approx(0.0, abs=1e-6)


def test_normalized_output_has_unit_std() -> None:
    result = WindowExtractor(_base_config(window_start=0.0)).process(_signal())
    assert float(np.std(result)) == pytest.approx(1.0, abs=1e-6)


def test_all_zero_signal_returns_zero_vector() -> None:
    signal = np.zeros(501, dtype=float)
    result = WindowExtractor(_base_config(window_start=0.0)).process(signal)
    assert np.allclose(result, 0.0)


def test_output_shape_is_one_fifty_one() -> None:
    result = WindowExtractor(_base_config(window_start=0.0)).process(_signal())
    assert result.shape == (1, 50, 1)


def test_output_dtype_is_float32() -> None:
    result = WindowExtractor(_base_config(window_start=0.0)).process(_signal())
    assert result.dtype == np.float32


def test_inject_noise_with_zero_sigma_returns_identical_array() -> None:
    extractor = WindowExtractor(_base_config(window_start=0.0))
    arr = np.linspace(-1.0, 1.0, 50, dtype=float)
    assert np.array_equal(extractor._inject_noise(arr, sigma=0.0), arr)


def test_inject_noise_with_positive_sigma_changes_values() -> None:
    extractor = WindowExtractor(_base_config(window_start=0.0))
    arr = np.linspace(-1.0, 1.0, 50, dtype=float)
    np.random.seed(1)
    noisy = extractor._inject_noise(arr, sigma=0.2)
    assert not np.array_equal(noisy, arr)


def test_process_with_noise_differs_from_clean_process() -> None:
    extractor = WindowExtractor(_base_config(window_start=0.0))
    np.random.seed(7)
    noisy = extractor.process(_signal(), noise_sigma=0.3)
    clean = extractor.process(_signal(), noise_sigma=0.0)
    assert not np.array_equal(noisy, clean)


def test_inject_noise_is_reproducible_with_seed() -> None:
    extractor = WindowExtractor(_base_config(window_start=0.0))
    arr = np.linspace(-1.0, 1.0, 50, dtype=float)
    np.random.seed(123)
    noisy_a = extractor._inject_noise(arr, sigma=0.2)
    np.random.seed(123)
    noisy_b = extractor._inject_noise(arr, sigma=0.2)
    assert np.array_equal(noisy_a, noisy_b)


def test_validate_config_raises_value_error_for_negative_noise_sigma() -> None:
    extractor = WindowExtractor(_base_config(window_start=0.0))
    with pytest.raises(ValueError):
        extractor._validate_config(noise_sigma=-0.1)


def test_validate_config_raises_value_error_for_noise_sigma_above_half() -> None:
    extractor = WindowExtractor(_base_config(window_start=0.0))
    with pytest.raises(ValueError):
        extractor._validate_config(noise_sigma=0.51)
