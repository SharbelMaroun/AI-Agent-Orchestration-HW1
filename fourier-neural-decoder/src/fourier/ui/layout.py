from __future__ import annotations

import math

from dash import dcc, html

from fourier.shared.constants import COLORS, DEFAULTS, WAVE_NAMES
from fourier.shared.version import VERSION


def make_slider(sid: str, label: str, min_v: float, max_v: float, step: float, default: float) -> html.Div:
    return html.Div([
        html.Label(label, style={"fontSize": "0.75rem", "color": "#64748b"}),
        dcc.Slider(id=sid, min=min_v, max=max_v, step=step, value=default, marks=None, updatemode="drag"),
    ], style={"marginBottom": "6px"})


def _build_wave_panel(i: int) -> html.Div:
    d = DEFAULTS[i]
    return html.Div(id=f"wave-panel-{i}", children=[
        dcc.Checklist(id=f"enabled-{i}", options=[{"label": f" {WAVE_NAMES[i]}", "value": "on"}],
                      value=["on"], style={"fontWeight": "bold", "color": COLORS[i]}),
        html.Div(id=f"wave-controls-{i}", children=[
            make_slider(f"freq-{i}", "Frequency (Hz)", 0.1, 5.0, 0.1, d["frequency"]),
            make_slider(f"amp-{i}", "Amplitude", 0, 100, 1, d["amplitude"]),
            make_slider(f"phase-{i}", "Phase (rad)", 0.0, round(2 * math.pi, 2), 0.01, d["phase"]),
            dcc.Checklist(id=f"dots-{i}", options=[{"label": " Show discrete", "value": "on"}], value=[]),
            html.Div(id=f"sr-section-{i}", children=[
                make_slider(f"sr-{i}", "Sampling Rate (Hz)", 1, 50, 1, d["sampling_rate"]),
            ], style={"display": "none"}),
            html.Div(id=f"vector-{i}"),
        ]),
    ], style={"padding": "8px", "marginBottom": "4px", "background": "rgba(238,242,255,0.3)", "borderRadius": "6px"})


def _build_sidebar() -> html.Div:
    return html.Div([_build_wave_panel(i) for i in range(4)],
                    style={"width": "300px", "flexShrink": "0", "padding": "8px", "overflowY": "auto"})


def _build_window_selector() -> html.Div:
    return html.Div([
        html.Label("Window start (s)", style={"fontSize": "0.75rem"}),
        dcc.Slider(id="window-slider", min=0.0, max=9.0, step=0.1, value=0.0, marks=None, updatemode="drag"),
    ], style={"marginBottom": "8px"})


def _build_noise_slider() -> html.Div:
    return html.Div([
        html.Label("Noise (σ)", style={"fontSize": "0.75rem"}),
        dcc.Slider(id="noise-slider", min=0.0, max=0.5, step=0.01, value=0.0, marks=None, updatemode="drag"),
        html.Div(id="noise-label", children="Clean"),
    ], style={"marginBottom": "8px"})


def _build_algo_selector() -> html.Div:
    return html.Div([
        html.Label("Algorithm", style={"fontSize": "0.75rem"}),
        dcc.RadioItems(id="algo-selector", options=[
            {"label": " RNN", "value": "RNN"},
            {"label": " LSTM", "value": "LSTM"},
            {"label": " Both", "value": "Both"},
        ], value="RNN", inline=True),
    ], style={"marginBottom": "8px"})


def _build_main_area() -> html.Main:
    return html.Main([
        dcc.Graph(id="overlay-chart", style={"height": "300px"}),
        dcc.Graph(id="sum-chart", style={"height": "280px"}),
        _build_window_selector(),
        _build_noise_slider(),
        _build_algo_selector(),
        html.Button("Identify", id="identify-btn", style={"marginBottom": "8px"}),
        html.Div(id="result-panel", style={"display": "none"}),
        html.Div(id="diff-panel", style={"display": "none"}),
    ], style={"flex": "1", "padding": "8px", "overflow": "auto"})


def _build_header() -> html.Header:
    return html.Header([
        html.H1("Fourier Synthesis", style={"margin": "0", "fontSize": "1.2rem"}),
        html.Button("Reset", id="reset-btn"),
    ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center",
              "padding": "8px 12px", "background": "#1e293b", "color": "#fff",
              "position": "sticky", "top": "0", "zIndex": "100"})


def _build_footer() -> html.Footer:
    return html.Footer([html.Span(f"v{VERSION}", style={"fontSize": "0.7rem", "color": "#94a3b8"})],
                       style={"padding": "4px 12px", "background": "#f1f5f9"})


def build_layout() -> html.Div:
    return html.Div([
        dcc.Store(id="channel-vector", data=[1, 1, 1, 1]),
        _build_header(),
        html.Div([_build_sidebar(), _build_main_area()],
                 style={"display": "flex", "flex": "1", "overflow": "hidden"}),
        _build_footer(),
    ], style={"display": "flex", "flexDirection": "column", "height": "100vh"})
