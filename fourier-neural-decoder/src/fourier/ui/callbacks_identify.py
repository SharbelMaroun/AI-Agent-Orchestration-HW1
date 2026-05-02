from __future__ import annotations

from typing import Any

import numpy as np
from dash import Input, Output, State, html, no_update
from dash.exceptions import PreventUpdate

from fourier.sdk.result_comparator import ResultComparator
from fourier.sdk.window_extractor import WindowExtractor
from fourier.shared.config_loader import load_app_config
from fourier.shared.constants import WAVE_NAMES
from fourier.shared.types import ClassifierResult
from fourier.ui.callbacks_result import _build_diff_summary, _build_single_result_panel


def _mask_disabled_channels(result: ClassifierResult, C: list[int]) -> ClassifierResult:
    """Zero out probabilities for disabled channels and re-normalise."""
    probs = [p if C[i] == 1 else 0.0 for i, p in enumerate(result["probabilities"])]
    total = sum(probs)
    if total > 1e-8:
        probs = [p / total for p in probs]
    predicted_class = int(np.argmax(probs))
    sorted_idx = sorted(range(4), key=lambda i: probs[i], reverse=True)
    return ClassifierResult(
        predicted_class=predicted_class,
        class_name=WAVE_NAMES[predicted_class],
        confidence=round(float(probs[predicted_class]), 6),
        probabilities=[round(float(p), 6) for p in probs],
        runner_up=sorted_idx[1],
    )


def register_identify_callback(app: Any, gatekeeper: Any) -> None:
    @app.callback(
        [Output("result-panel", "children"), Output("result-panel", "style"),
         Output("diff-panel", "children"), Output("diff-panel", "style")],
        Input("identify-btn", "n_clicks"),
        [State("window-slider", "value"), State("noise-slider", "value"),
         State("algo-selector", "value"), State("sum-chart", "figure"),
         State("channel-vector", "data")],
        prevent_initial_call=True,
    )
    def identify_cb(_, window_start, noise_sigma, algo, figure, channel_vector):
        if figure is None:
            raise PreventUpdate
        C = channel_vector if channel_vector else [1, 1, 1, 1]
        return _run_identify(gatekeeper, window_start, noise_sigma, algo, figure, C)


def _run_identify(
    gatekeeper: Any, window_start: Any, noise_sigma: Any,
    algo: str, figure: dict, C: list[int],
) -> tuple:
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
        return _mask_disabled_channels(RNNClassifier(rnn_cfg).process(window), C)

    def run_lstm():
        from fourier.sdk.lstm_classifier import LSTMClassifier
        lstm_cfg = {**app_cfg.get("lstm_config", {}), "weights_path": app_cfg["lstm_model_path"]}
        return _mask_disabled_channels(LSTMClassifier(lstm_cfg).process(window), C)

    if algo == "RNN":
        result = gatekeeper.call(run_rnn)
        return _build_single_result_panel(result, "RNN"), {"display": "block"}, no_update, {"display": "none"}

    if algo == "LSTM":
        result = gatekeeper.call(run_lstm)
        return _build_single_result_panel(result, "LSTM"), {"display": "block"}, no_update, {"display": "none"}

    rnn_r = gatekeeper.call(run_rnn)
    lstm_r = gatekeeper.call(run_lstm)
    diff = ResultComparator().process(rnn_r, lstm_r)
    both = html.Div([_build_single_result_panel(rnn_r, "RNN"), _build_single_result_panel(lstm_r, "LSTM")],
                    style={"display": "flex", "gap": "8px"})
    return both, {"display": "block"}, _build_diff_summary(diff), {"display": "block"}
