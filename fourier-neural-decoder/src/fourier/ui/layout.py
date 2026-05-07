from __future__ import annotations

import math

from dash import dcc, html

from fourier.shared.constants import COLORS, DEFAULTS, WAVE_NAMES
from fourier.shared.version import VERSION
from fourier.ui.layout_id_mode import (
    build_extract_selector,
    build_id_mode_banner,
    build_id_mode_entry,
)


def make_slider(sid: str, label: str, min_v: float, max_v: float, step: float, default: float,
                unit: str = "") -> html.Div:
    val_text = f"{default} {unit}".strip() if unit else str(default)
    return html.Div([
        html.Label(label, style={"fontSize": "0.75rem", "color": "#64748b"}),
        dcc.Slider(id=sid, min=min_v, max=max_v, step=step, value=default, marks=None, updatemode="drag"),
        html.Div(id=f"{sid}-val", children=val_text,
                 style={"fontSize": "0.72rem", "color": "#1e293b", "fontWeight": "600",
                        "marginTop": "-2px", "paddingLeft": "2px"}),
    ], style={"marginBottom": "6px"})


def _build_wave_panel(i: int) -> html.Div:
    d = DEFAULTS[i]
    return html.Div(id=f"wave-panel-{i}", children=[
        html.Div(
            dcc.Checklist(
                id=f"enabled-{i}",
                options=[{"label": f" {WAVE_NAMES[i]}", "value": "on"}],
                value=["on"],
                style={"fontWeight": "bold", "color": COLORS[i]},
            ),
            id=f"enabled-wrap-{i}",
        ),
        html.Div(id=f"wave-controls-{i}", children=[
            html.Div(id=f"fixed-controls-{i}", children=[
                make_slider(f"freq-{i}", "Frequency (Hz)", 0.1, 5.0, 0.1, d["frequency"], "Hz"),
                make_slider(f"amp-{i}", "Amplitude", 0, 100, 1, d["amplitude"], ""),
                make_slider(f"phase-{i}", "Phase (rad)", 0.0, round(2 * math.pi, 2), 0.01, d["phase"], "rad"),
                dcc.Checklist(id=f"dots-{i}", options=[{"label": " Show discrete", "value": "on"}], value=[]),
                html.Div(id=f"sr-section-{i}", children=[
                    make_slider(f"sr-{i}", "Sampling Rate (Hz)", 1, 50, 1, d["sampling_rate"], "Hz"),
                ], style={"display": "none"}),
                html.Div(id=f"vector-{i}"),
            ]),
            html.Div(id=f"noise-controls-{i}", children=[
                make_slider(f"alpha-{i}", "α — Amp noise (%)", 0, 100, 1, d.get("alpha", 0), "%"),
                make_slider(f"beta-{i}", "β — Phase noise (%)", 0, 100, 1, d.get("beta", 0), "%"),
            ]),
        ]),
    ], style={"padding": "8px", "marginBottom": "4px", "background": "rgba(238,242,255,0.3)", "borderRadius": "6px"})


def _build_sidebar() -> html.Div:
    return html.Div([
        html.Div(id="sidebar-lock-overlay", style={"display": "none"}),
        html.Div([_build_wave_panel(i) for i in range(4)], id="sidebar-panels"),
    ], id="sidebar", style={"width": "300px", "flexShrink": "0", "padding": "8px",
                            "height": "100%", "overflowY": "auto", "overflowX": "hidden",
                            "position": "relative"})


def _build_window_selector() -> html.Div:
    return html.Div([
        html.Label("Window start (s)", style={"fontSize": "0.75rem"}),
        dcc.Slider(id="window-slider", min=0.0, max=9.99, step=0.001, value=0.0, marks=None, updatemode="drag"),
        html.Div(id="window-slider-val", children="0.0 s",
                 style={"fontSize": "0.72rem", "color": "#1e293b", "fontWeight": "600",
                        "marginTop": "-2px", "paddingLeft": "2px"}),
    ], style={"marginBottom": "8px"})


def _build_main_area() -> html.Main:
    return html.Main([
        build_id_mode_entry(),
        build_id_mode_banner(),
        dcc.Graph(id="overlay-chart", style={"height": "260px"}),
        dcc.Graph(id="pure-chart", style={"height": "240px"}),
        dcc.Graph(id="sum-chart", style={"height": "260px"}),
        _build_window_selector(),
        build_extract_selector(),
        html.Div(
            html.Button("Identify", id="identify-btn", style={"marginBottom": "8px"}),
            id="identify-btn-container",
            style={"display": "none"},
        ),
        dcc.Loading(
            id="identify-loading",
            type="circle",
            color="#6366f1",
            children=html.Div(id="result-panel", style={"display": "none"}),
        ),
    ], style={"flex": "1", "minHeight": "0", "padding": "8px", "overflow": "auto"})


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
        dcc.Store(id="active-channels", data=[1, 1, 1, 1]),
        dcc.Store(id="extract-vector", data=[0, 1, 0, 0]),
        dcc.Store(id="id-mode-active", data=False),
        _build_header(),
        html.Div([
            html.Div(id="sidebar-wrapper", children=[_build_sidebar()],
                     style={"width": "300px", "flexShrink": "0", "position": "relative",
                            "height": "100%", "minHeight": "0"}),
            _build_main_area(),
        ], style={"display": "flex", "flex": "1", "minHeight": "0", "overflow": "hidden"}),
        _build_footer(),
    ], style={"display": "flex", "flexDirection": "column", "height": "100vh"})
