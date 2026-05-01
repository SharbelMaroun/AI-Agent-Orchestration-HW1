from __future__ import annotations

from unittest.mock import MagicMock, patch

import dash


def test_create_app_returns_dash_instance():
    from fourier.ui.app import create_app
    app = create_app()
    assert isinstance(app, dash.Dash)


def test_create_app_sets_title():
    from fourier.ui.app import create_app
    app = create_app()
    assert app.title == "Fourier Synthesis"


def test_create_app_layout_is_not_none():
    from fourier.ui.app import create_app
    app = create_app()
    assert app.layout is not None


def test_register_clientside_callback_calls_app():
    from fourier.ui.callbacks_client import register_clientside_callback
    mock_app = MagicMock()
    register_clientside_callback(mock_app)
    mock_app.clientside_callback.assert_called_once()


def test_register_clientside_callback_outputs_two_charts():
    from fourier.ui.callbacks_client import register_clientside_callback
    from dash import Output
    mock_app = MagicMock()
    register_clientside_callback(mock_app)
    call_args = mock_app.clientside_callback.call_args
    outputs = call_args[0][1]
    assert len(outputs) == 2


def test_register_server_callbacks_executes():
    from fourier.ui.callbacks_server import register_server_callbacks
    mock_app = MagicMock()
    mock_gk = MagicMock()
    register_server_callbacks(mock_app, mock_gk)
    assert mock_app.callback.call_count > 0
