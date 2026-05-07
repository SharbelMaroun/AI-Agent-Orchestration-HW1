from __future__ import annotations

import math
from typing import Any

import numpy as np
from dash import Input, Output, State, html
from dash.exceptions import PreventUpdate

from fourier.gatekeeper import Gatekeeper
from fourier.sdk.fc_regressor import FCRegressor
from fourier.sdk.lstm_regressor import LSTMRegressor
from fourier.sdk.rnn_regressor import RNNRegressor
from fourier.shared.config_loader import load_training_config
from fourier.shared.constants import COLORS, EXTRACT_POINTS, ID_MODE_SIGNALS, ID_MODE_SR, WAVE_NAMES
from fourier.ui.callbacks_result import _build_extraction_panel

_REGRESSOR_CLASSES = {"rnn": RNNRegressor, "lstm": LSTMRegressor, "fc": FCRegressor}
_regressors: dict[str, Any] = {}
_gatekeeper = Gatekeeper({"max_retries": 1, "timeout_seconds": 5})


def _get(kind: str) -> Any:
    if kind not in _regressors:
        _regressors[kind] = _REGRESSOR_CLASSES[kind](load_training_config().get(kind, {}))
    return _regressors[kind]


def _infer(kind: str, window: np.ndarray, c_vec: list[int]) -> dict[str, Any]:
    return _gatekeeper.process(kind, _get(kind).process, window, c_vec)


def _window_and_truth(figure: dict, window_start: float, extract_idx: int,
                      ) -> tuple[np.ndarray, list[float]]:
    """Return (10 noisy summation samples, 10 ground-truth pure-channel samples)."""
    sum_trace = figure["data"][-1] if figure.get("data") else {}
    sum_x = np.array(sum_trace.get("x", []), dtype=float)
    sum_y = np.array(sum_trace.get("y", []), dtype=float)

    n_start = int(math.ceil(float(window_start) * ID_MODE_SR))
    t_pts = np.array([(n_start + k) / ID_MODE_SR for k in range(EXTRACT_POINTS)])
    window_samples = (np.interp(t_pts, sum_x, sum_y) if len(sum_x) > 0
                      else np.zeros(EXTRACT_POINTS))

    sig = ID_MODE_SIGNALS[extract_idx]
    real = [
        sig["amplitude"] * math.sin(2 * math.pi * sig["frequency"] * t + sig["phase"])
        for t in t_pts
    ]
    return window_samples, real


def register_identify_callback(app: Any) -> None:
    @app.callback(
        [Output("result-panel", "children"), Output("result-panel", "style")],
        Input("identify-btn", "n_clicks"),
        [State("window-slider", "value"), State("sum-chart", "figure"),
         State("extract-vector", "data")],
        prevent_initial_call=True,
    )
    def identify_cb(_, window_start, figure, extract_vector):
        if figure is None:
            raise PreventUpdate
        # v1.07: extraction target is locked to channel 1 (Second Harmonic).
        C = [0, 1, 0, 0]
        try:
            return _run_identify(window_start, figure, C)
        except Exception as exc:
            err = html.Div(f"Error: {exc}", style={"color": "#ef4444", "padding": "8px",
                                                    "fontFamily": "monospace", "fontSize": "0.8rem"})
            return err, {"display": "block"}


def _run_identify(window_start: Any, figure: dict, C: list[int]) -> tuple:
    extract_idx = next((i for i, v in enumerate(C) if v == 1), None)
    if extract_idx is None:
        msg = html.Div("Select a wave to extract using the radio buttons above.",
                       style={"color": "#f59e0b", "padding": "8px", "fontStyle": "italic"})
        return msg, {"display": "block"}

    window_samples, real_pts = _window_and_truth(figure, float(window_start or 0.0), extract_idx)

    rnn_result = _infer("rnn", window_samples, C)
    lstm_result = _infer("lstm", window_samples, C)
    fc_result = _infer("fc", window_samples, C)
    real_arr = np.array(real_pts)
    for r in (rnn_result, lstm_result, fc_result):
        r["mae"] = round(float(np.mean(np.abs(np.array(r["coordinates"]) - real_arr))), 3)

    panel = _build_extraction_panel(
        real_pts, WAVE_NAMES[extract_idx], COLORS[extract_idx],
        rnn_result=rnn_result, lstm_result=lstm_result, fc_result=fc_result,
    )
    return panel, {"display": "block"}
