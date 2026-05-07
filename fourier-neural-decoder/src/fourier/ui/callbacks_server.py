from __future__ import annotations

import math
from typing import Any

from dash import Input, Output, html

from fourier.shared.constants import COLORS
from fourier.ui.callbacks_id_mode import register_id_mode_callbacks
from fourier.ui.callbacks_identify import register_identify_callback


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


_SLIDER_UNITS: dict[str, str] = {
    "freq": "Hz", "amp": "", "phase": "rad", "sr": "Hz",
    "alpha": "%", "beta": "%",
}


def register_value_display_callbacks(app: Any) -> None:
    for i in range(4):
        for key, unit in _SLIDER_UNITS.items():
            sid = f"{key}-{i}"
            suffix = f" {unit}" if unit else ""
            app.clientside_callback(
                f"function(v) {{ return v !== null && v !== undefined ? v + '{suffix}' : '—'; }}",
                Output(f"{sid}-val", "children"),
                Input(sid, "value"),
            )
    app.clientside_callback(
        "function(v) { return v !== null && v !== undefined ? v + ' s' : '—'; }",
        Output("window-slider-val", "children"),
        Input("window-slider", "value"),
    )


def register_server_callbacks(app: Any) -> None:
    register_value_display_callbacks(app)
    for i in range(4):
        _register_toggle_wave(app, i)
        _register_toggle_sr(app, i)
        _register_update_vector(app, i)

    @app.callback(
        Output("active-channels", "data"),
        [Input(f"enabled-{i}", "value") for i in range(4)],
    )
    def channel_vector_cb(*enabled_values: list[str]) -> list[int]:
        return compute_channel_vector(*enabled_values)

    # extract-vector is fixed at [0, 1, 0, 0] (Second Harmonic) — no callback needed;
    # the dcc.Store initial value in layout.py provides the constant.
    register_id_mode_callbacks(app)
    register_identify_callback(app)


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


