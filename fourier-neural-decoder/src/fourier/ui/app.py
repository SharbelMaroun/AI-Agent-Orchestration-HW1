from __future__ import annotations

import dash

from fourier.gatekeeper import ModelGatekeeper
from fourier.shared.config_loader import load_rate_limits
from fourier.ui.callbacks_client import register_clientside_callback
from fourier.ui.callbacks_server import register_server_callbacks
from fourier.ui.layout import build_layout


def create_app() -> dash.Dash:
    app = dash.Dash(__name__, title="Fourier Synthesis")
    app.layout = build_layout()

    rate_cfg = load_rate_limits()
    gatekeeper = ModelGatekeeper(rate_cfg)

    register_clientside_callback(app)
    register_server_callbacks(app, gatekeeper)

    return app
