from __future__ import annotations

import math
from typing import Any

from dash import Input, Output, State, html, no_update
from dash.exceptions import PreventUpdate

from fourier.shared.constants import COLORS, DEFAULTS, WAVE_NAMES
from fourier.shared.types import ClassifierResult


def _noise_label(sigma: float) -> str:
    if sigma == 0.0:
        return "Clean"
    if sigma <= 0.15:
        return "Light"
    if sigma <= 0.30:
        return "Medium"
    return "Heavy"


def _build_single_result_panel(result: ClassifierResult, label: str = "") -> html.Div:
    bars = [
        html.Div([
            html.Span(WAVE_NAMES[i], style={"width": "140px", "display": "inline-block", "fontSize": "0.75rem"}),
            html.Div(style={"display": "inline-block", "height": "10px",
                            "width": f"{result['probabilities'][i] * 200:.0f}px",
                            "background": COLORS[i], "verticalAlign": "middle"}),
            html.Span(f" {result['probabilities'][i]:.1%}", style={"fontSize": "0.7rem"}),
        ]) for i in range(4)
    ]
    return html.Div([
        html.Strong(label or "Result"),
        html.P(f"Predicted: {result['class_name']} ({result['confidence']:.1%})"),
        *bars,
    ], style={"padding": "8px", "background": "#f8fafc", "borderRadius": "6px", "marginBottom": "6px"})


def _build_diff_summary(diff: dict[str, Any]) -> html.Div:
    color = "#16a34a" if diff["agreement"] else "#dc2626"
    return html.Div([
        html.Strong("Agreement: "),
        html.Span("YES" if diff["agreement"] else "NO", style={"color": color, "fontWeight": "bold"}),
        html.P(f"Confidence delta: {diff['confidence_delta']:.4f}"),
        html.P(f"Runner-up: {diff['runner_up_diff']}"),
    ], style={"padding": "8px", "background": "#f1f5f9", "borderRadius": "6px"})


def register_server_callbacks(app: Any, gatekeeper: Any) -> None:
    for i in range(4):
        _register_toggle_wave(app, i)
        _register_toggle_sr(app, i)
        _register_update_vector(app, i)

    @app.callback(
        Output("noise-label", "children"),
        Input("noise-slider", "value"),
    )
    def noise_label_cb(sigma: float) -> str:
        return _noise_label(float(sigma or 0.0))

    @app.callback(
        [Output(f"freq-{i}", "value") for i in range(4)] +
        [Output(f"amp-{i}", "value") for i in range(4)] +
        [Output(f"phase-{i}", "value") for i in range(4)] +
        [Output(f"enabled-{i}", "value") for i in range(4)] +
        [Output(f"dots-{i}", "value") for i in range(4)] +
        [Output(f"sr-{i}", "value") for i in range(4)],
        Input("reset-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_cb(_: Any) -> list[Any]:
        return (
            [DEFAULTS[i]["frequency"] for i in range(4)] +
            [DEFAULTS[i]["amplitude"] for i in range(4)] +
            [DEFAULTS[i]["phase"] for i in range(4)] +
            [["on"] for _ in range(4)] +
            [[] for _ in range(4)] +
            [DEFAULTS[i]["sampling_rate"] for i in range(4)]
        )

    _register_identify(app, gatekeeper)


def _register_toggle_wave(app: Any, i: int) -> None:
    @app.callback(
        [Output(f"wave-controls-{i}", "style"), Output(f"wave-panel-{i}", "style")],
        Input(f"enabled-{i}", "value"),
    )
    def toggle_wave(enabled: list[str]) -> tuple[dict, dict]:
        on = bool(enabled)
        ctrl = {} if on else {"display": "none"}
        panel = {"padding": "8px", "marginBottom": "4px", "borderRadius": "6px",
                 "opacity": "1" if on else "0.55",
                 "background": "rgba(238,242,255,0.3)" if on else "#f8fafc"}
        return ctrl, panel


def _register_toggle_sr(app: Any, i: int) -> None:
    @app.callback(
        Output(f"sr-section-{i}", "style"),
        Input(f"dots-{i}", "value"),
    )
    def toggle_sr(dots: list[str]) -> dict:
        return {"display": "block"} if dots else {"display": "none"}


def _register_update_vector(app: Any, i: int) -> None:
    @app.callback(
        Output(f"vector-{i}", "children"),
        [Input(f"dots-{i}", "value"), Input(f"sr-{i}", "value"),
         Input(f"freq-{i}", "value"), Input(f"amp-{i}", "value"), Input(f"phase-{i}", "value")],
    )
    def update_vector(dots: list[str], sr: float, freq: float, amp: float, phase: float) -> Any:
        if not dots:
            return []
        sr_i, freq_f, amp_f, phase_f = int(sr or 1), float(freq or 0.5), float(amp or 0), float(phase or 0)
        n_s = sr_i * 10 + 1
        spans = [
            html.Span(f"{amp_f * math.sin(2 * math.pi * freq_f * n / sr_i + phase_f):.1f} ",
                      title=f"n={n} t={n / sr_i:.2f}s",
                      style={"color": COLORS[i], "fontFamily": "monospace", "fontSize": "0.7rem"})
            for n in range(min(n_s, 50))
        ]
        return html.Div([html.P(f"y[n], n = 0…{min(n_s,50)-1}", style={"margin": "0 0 2px"}), *spans],
                        style={"background": "#0f172a", "color": "#e2e8f0", "padding": "4px", "borderRadius": "4px"})


def _register_identify(app: Any, gatekeeper: Any) -> None:
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
        import numpy as np
        from fourier.sdk.window_extractor import WindowExtractor
        from fourier.sdk.result_comparator import ResultComparator
        from fourier.shared.config_loader import load_app_config

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
            clf = RNNClassifier({"hidden_size": 64, "num_layers": 1, "weights_path": app_cfg["rnn_model_path"]})
            return clf.process(window)

        def run_lstm():
            from fourier.sdk.lstm_classifier import LSTMClassifier
            lstm_cfg = {"hidden_size": 128, "num_layers": 2, "dropout": 0.3, "weights_path": app_cfg["lstm_model_path"]}
            return LSTMClassifier(lstm_cfg).process(window)

        if algo == "RNN":
            result = gatekeeper.call(run_rnn)
            panel = _build_single_result_panel(result, "RNN")
            return panel, {"display": "block"}, no_update, {"display": "none"}

        if algo == "LSTM":
            result = gatekeeper.call(run_lstm)
            panel = _build_single_result_panel(result, "LSTM")
            return panel, {"display": "block"}, no_update, {"display": "none"}

        rnn_r = gatekeeper.call(run_rnn)
        lstm_r = gatekeeper.call(run_lstm)
        diff = ResultComparator().process(rnn_r, lstm_r)
        both = html.Div([_build_single_result_panel(rnn_r, "RNN"), _build_single_result_panel(lstm_r, "LSTM")],
                        style={"display": "flex", "gap": "8px"})
        diff_panel = _build_diff_summary(diff)
        return both, {"display": "block"}, diff_panel, {"display": "block"}
