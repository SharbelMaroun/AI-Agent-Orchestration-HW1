from fourier.shared.version import VERSION


def test_import_version_constant() -> None:
    assert isinstance(VERSION, str)


def test_version_value() -> None:
    assert VERSION == "1.01"
