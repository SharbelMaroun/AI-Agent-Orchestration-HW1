from fourier.shared.types import ClassifierResult, DiffResult


def test_classifier_result_typed_dict_keys() -> None:
    expected_keys = {"predicted_class", "class_name", "confidence", "probabilities", "runner_up"}
    assert set(ClassifierResult.__annotations__.keys()) == expected_keys


def test_diff_result_typed_dict_keys() -> None:
    expected_keys = {"agreement", "rnn_predicted", "lstm_predicted", "confidence_delta", "runner_up_diff"}
    assert set(DiffResult.__annotations__.keys()) == expected_keys
