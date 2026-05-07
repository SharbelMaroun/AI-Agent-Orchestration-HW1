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


def _project_at_frequency(samples: np.ndarray, t_pts: np.ndarray, chosen_idx: int) -> np.ndarray:
    """Extract the chosen-frequency component from a discrete summation window.

    Fits  samples ≈ Σᵢ [aᵢ·sin(2π·fᵢ·t) + bᵢ·cos(2π·fᵢ·t)]  over all 4 known
    channel frequencies via least squares (10 equations, 8 unknowns), then
    returns only the chosen channel's reconstruction. This isolates the user's
    target frequency cleanly even when the window is too short for the bases
    to be naturally orthogonal.
    """
    columns: list[np.ndarray] = []
    for sig in ID_MODE_SIGNALS:
        f = float(sig["frequency"])
        columns.append(np.sin(2 * np.pi * f * t_pts))
        columns.append(np.cos(2 * np.pi * f * t_pts))
    basis = np.column_stack(columns)
    coeffs, *_ = np.linalg.lstsq(basis, samples, rcond=None)

    f_chosen = float(ID_MODE_SIGNALS[chosen_idx]["frequency"])
    a_i = float(coeffs[2 * chosen_idx])
    b_i = float(coeffs[2 * chosen_idx + 1])
    return (
        a_i * np.sin(2 * np.pi * f_chosen * t_pts)
        + b_i * np.cos(2 * np.pi * f_chosen * t_pts)
    )


def _extract_10_points(
    figure: dict, window_start: float, extract_idx: int,
) -> tuple[list[float], list[float], list[float]]:
    """Take EXTRACT_POINTS discrete samples (at ID_MODE_SR grid) from the summation
    inside the window, then EXTRACT the chosen wave's frequency component using a
    least-squares Fourier projection at that known frequency. The 'result' column
    is the recovered sine; 'real' is the ground-truth sine; 'error' is the gap."""
    sum_trace = figure["data"][-1] if figure.get("data") else {}
    sum_x = np.array(sum_trace.get("x", []), dtype=float)
    sum_y = np.array(sum_trace.get("y", []), dtype=float)

    ws = float(window_start or 0.0)
    n_start = int(math.ceil(ws * ID_MODE_SR))
    t_pts = np.array([(n_start + k) / ID_MODE_SR for k in range(EXTRACT_POINTS)])

    if len(sum_x) > 0:
        window_samples = np.interp(t_pts, sum_x, sum_y)
        sig = ID_MODE_SIGNALS[extract_idx]
        result_arr = _project_at_frequency(window_samples, t_pts, extract_idx)
        result = result_arr.tolist()
    else:
        sig = ID_MODE_SIGNALS[extract_idx]
        result = [0.0] * EXTRACT_POINTS

    real = [
        sig["amplitude"] * math.sin(2 * math.pi * sig["frequency"] * t + sig["phase"])
        for t in t_pts
    ]
    error = [round(result[k] - real[k], 2) for k in range(EXTRACT_POINTS)]
    return result, real, error


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
        # The State input is kept for callback wiring but its value is overridden.
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

    result_pts, real_pts, error_pts = _extract_10_points(figure, float(window_start or 0.0), extract_idx)

    # Get the same 10 mixed samples that fed _extract_10_points to feed the NNs.
    sum_trace = figure["data"][-1] if figure.get("data") else {}
    sum_x = np.array(sum_trace.get("x", []), dtype=float)
    sum_y = np.array(sum_trace.get("y", []), dtype=float)
    ws = float(window_start or 0.0)
    n_start = int(math.ceil(ws * ID_MODE_SR))
    t_pts = np.array([(n_start + k) / ID_MODE_SR for k in range(EXTRACT_POINTS)])
    window_samples = (np.interp(t_pts, sum_x, sum_y) if len(sum_x) > 0
                       else np.zeros(EXTRACT_POINTS))

    rnn_result = _infer("rnn", window_samples, C)
    lstm_result = _infer("lstm", window_samples, C)
    fc_result = _infer("fc", window_samples, C)
    real_arr = np.array(real_pts)
    rnn_result["mae"] = round(float(np.mean(np.abs(np.array(rnn_result["coordinates"]) - real_arr))), 3)
    lstm_result["mae"] = round(float(np.mean(np.abs(np.array(lstm_result["coordinates"]) - real_arr))), 3)
    fc_result["mae"] = round(float(np.mean(np.abs(np.array(fc_result["coordinates"]) - real_arr))), 3)

    panel = _build_extraction_panel(
        result_pts, real_pts, error_pts,
        WAVE_NAMES[extract_idx], COLORS[extract_idx],
        rnn_result=rnn_result, lstm_result=lstm_result, fc_result=fc_result,
    )
    return panel, {"display": "block"}
