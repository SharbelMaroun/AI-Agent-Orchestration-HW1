from __future__ import annotations

from typing import Any

import numpy as np
from dash import Input, Output, State, no_update
from dash.exceptions import PreventUpdate

from fourier.sdk.result_comparator import ResultComparator
from fourier.sdk.window_extractor import WindowExtractor
from fourier.shared.config_loader import load_app_config
from fourier.ui.callbacks_result import _build_diff_summary, _build_single_result_panel


def register_identify_callback(app: Any, gatekeeper: Any) -> None:
    @app.callback(
        [Output("result-panel", "children"), Output("result-panel", "style"),
         Output("diff-panel", "children"), Output("diff-panel", "style")],
        Input("identify-btn", "n_clicks"),
        [State("window-slider", "value"), State("noise-slider", "value"),
         State("algo-selector", "value"), State("sum-chart", "figure")],
        prevent_initial_call=True,
    )
    def identify_cb(_, window_start, noise_sigma, algo, figure):
        if figure is None:
            raise PreventUpdate
        return _run_identify(gatekeeper, window_start, noise_sigma, algo, figure)


def _run_identify(gatekeeper: Any, window_start: Any, noise_sigma: Any, algo: str, figure: dict) -> tuple:
    app_cfg = load_app_config()
    sum_y = np.array(figure["data"][-1]["y"] if figure["data"] else [0.0] * 501)
    extractor = WindowExtractor({
        "window_start": float(window_start or 0.0),
        "window_points": int(app_cfg["window_points"]),
        "noise_max": float(app_cfg["noise_max"]),
    })
    window = extractor.process(sum_y, noise_sigma=float(noise_sigma or 0.0))

    def run_rnn():
        from fourier.sdk.rnn_classifier import RNNClassifier
        rnn_cfg = {**app_cfg.get("rnn_config", {}), "weights_path": app_cfg["rnn_model_path"]}
        return RNNClassifier(rnn_cfg).process(window)

    def run_lstm():
        from fourier.sdk.lstm_classifier import LSTMClassifier
        lstm_cfg = {**app_cfg.get("lstm_config", {}), "weights_path": app_cfg["lstm_model_path"]}
        return LSTMClassifier(lstm_cfg).process(window)

    if algo == "RNN":
        result = gatekeeper.call(run_rnn)
        return _build_single_result_panel(result, "RNN"), {"display": "block"}, no_update, {"display": "none"}

    if algo == "LSTM":
        result = gatekeeper.call(run_lstm)
        return _build_single_result_panel(result, "LSTM"), {"display": "block"}, no_update, {"display": "none"}

    rnn_r = gatekeeper.call(run_rnn)
    lstm_r = gatekeeper.call(run_lstm)
    diff = ResultComparator().process(rnn_r, lstm_r)
    from dash import html
    both = html.Div([_build_single_result_panel(rnn_r, "RNN"), _build_single_result_panel(lstm_r, "LSTM")],
                    style={"display": "flex", "gap": "8px"})
    return both, {"display": "block"}, _build_diff_summary(diff), {"display": "block"}
