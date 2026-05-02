from __future__ import annotations

import math
from typing import Any

from dash import Input, Output, html

from fourier.shared.constants import COLORS, DEFAULTS
from fourier.ui.callbacks_identify import register_identify_callback
from fourier.ui.callbacks_result import _build_diff_summary, _build_single_result_panel  # noqa: F401


def _noise_label(sigma: float) -> str:
    if sigma == 0.0:
        return "Clean"
    if sigma <= 0.15:
        return "Light"
    if sigma <= 0.30:
        return "Medium"
    return "Heavy"


def toggle_wave_fn(enabled: list[str]) -> tuple[dict, dict]:
    on = bool(enabled)
    ctrl = {} if on else {"display": "none"}
    panel = {"padding": "8px", "marginBottom": "4px", "borderRadius": "6px",
             "opacity": "1" if on else "0.55",
             "background": "rgba(238,242,255,0.3)" if on else "#f8fafc"}
    return ctrl, panel


def toggle_sr_fn(dots: list[str]) -> dict:
    return {"display": "block"} if dots else {"display": "none"}


def update_vector_fn(i: int, dots: list[str], sr: float, freq: float, amp: float, phase: float) -> Any:
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


def compute_channel_vector(*enabled_values: list[str]) -> list[int]:
    """Convert 4 enabled checklists to binary one-hot vector C = [c0, c1, c2, c3]."""
    return [1 if bool(e) else 0 for e in enabled_values]


def reset_cb_fn(_: Any) -> list[Any]:
    return (
        [DEFAULTS[i]["frequency"] for i in range(4)] +
        [DEFAULTS[i]["amplitude"] for i in range(4)] +
        [DEFAULTS[i]["phase"] for i in range(4)] +
        [["on"] for _ in range(4)] +
        [[] for _ in range(4)] +
        [DEFAULTS[i]["sampling_rate"] for i in range(4)]
    )


def register_server_callbacks(app: Any, gatekeeper: Any) -> None:
    for i in range(4):
        _register_toggle_wave(app, i)
        _register_toggle_sr(app, i)
        _register_update_vector(app, i)

    @app.callback(Output("noise-label", "children"), Input("noise-slider", "value"))
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
    def reset_cb(n: Any) -> list[Any]:
        return reset_cb_fn(n)

    @app.callback(
        Output("channel-vector", "data"),
        [Input(f"enabled-{i}", "value") for i in range(4)],
    )
    def channel_vector_cb(*enabled_values: list[str]) -> list[int]:
        return compute_channel_vector(*enabled_values)

    register_identify_callback(app, gatekeeper)


def _register_toggle_wave(app: Any, i: int) -> None:
    @app.callback(
        [Output(f"wave-controls-{i}", "style"), Output(f"wave-panel-{i}", "style")],
        Input(f"enabled-{i}", "value"),
    )
    def toggle_wave(enabled: list[str]) -> tuple[dict, dict]:
        return toggle_wave_fn(enabled)


def _register_toggle_sr(app: Any, i: int) -> None:
    @app.callback(Output(f"sr-section-{i}", "style"), Input(f"dots-{i}", "value"))
    def toggle_sr(dots: list[str]) -> dict:
        return toggle_sr_fn(dots)


def _register_update_vector(app: Any, i: int) -> None:
    @app.callback(
        Output(f"vector-{i}", "children"),
        [Input(f"dots-{i}", "value"), Input(f"sr-{i}", "value"),
         Input(f"freq-{i}", "value"), Input(f"amp-{i}", "value"), Input(f"phase-{i}", "value")],
    )
    def update_vector(dots: list[str], sr: float, freq: float, amp: float, phase: float) -> Any:
        return update_vector_fn(i, dots, sr, freq, amp, phase)
