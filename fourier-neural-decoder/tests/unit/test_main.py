from __future__ import annotations

from unittest.mock import MagicMock, patch, patch as mock_patch
import pytest


def test_main_exits_with_1_on_missing_config(tmp_path):
    from fourier.__main__ import main

    with patch("fourier.__main__.load_app_config", side_effect=FileNotFoundError("missing")):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1


def test_main_exits_with_1_on_bad_config_key(tmp_path):
    from fourier.__main__ import main

    with patch("fourier.__main__.load_app_config", side_effect=KeyError("port")):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1


def test_main_exits_with_1_on_missing_ui():
    from fourier.__main__ import main
    import sys

    mock_cfg = {"host": "127.0.0.1", "port": 8050, "debug": False}
    mock_ui_app = MagicMock()
    mock_ui_app.create_app = MagicMock(side_effect=ImportError("no ui"))

    with patch("fourier.__main__.load_app_config", return_value=mock_cfg), \
         patch("fourier.__main__.load_rate_limits", return_value={}), \
         patch.dict(sys.modules, {"fourier.ui.app": mock_ui_app}):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1


def test_main_calls_app_run_with_config():
    from fourier.__main__ import main
    import sys

    mock_cfg = {"host": "127.0.0.1", "port": 8050, "debug": False}
    mock_dash = MagicMock()
    mock_ui_app = MagicMock()
    mock_ui_app.create_app = MagicMock(return_value=mock_dash)

    with patch("fourier.__main__.load_app_config", return_value=mock_cfg), \
         patch("fourier.__main__.load_rate_limits", return_value={}), \
         patch.dict(sys.modules, {"fourier.ui.app": mock_ui_app}):
        main()
    mock_dash.run.assert_called_once_with(host="127.0.0.1", port=8050, debug=False)
