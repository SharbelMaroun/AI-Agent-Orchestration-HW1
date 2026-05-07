"""Identification-mode UI builders (entry button, banner, extract selector).

Extracted from layout.py to keep that file under the 150-line cap.
"""
from __future__ import annotations

from dash import html

from fourier.shared.constants import WAVE_NAMES

_ENTRY_BTN_STYLE = {
    "fontSize": "1.25rem", "fontWeight": "800", "padding": "18px 0",
    "background": "linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%)",
    "color": "#fff", "border": "none", "borderRadius": "14px",
    "cursor": "pointer", "width": "100%", "marginBottom": "14px",
    "boxShadow": "0 6px 24px rgba(139,92,246,0.55)",
    "letterSpacing": "0.04em", "textTransform": "uppercase",
}

_BANNER_STYLE = {
    "color": "#fbbf24", "fontWeight": "700", "fontSize": "0.9rem",
    "background": "rgba(251,191,36,0.12)", "borderRadius": "8px",
    "padding": "6px 12px", "border": "1px solid rgba(251,191,36,0.4)",
    "marginBottom": "8px", "textAlign": "center",
}

_EXIT_BTN_STYLE = {
    "background": "#dc2626", "color": "#fff", "border": "none",
    "borderRadius": "8px", "padding": "8px 22px", "cursor": "pointer",
    "marginBottom": "12px", "fontWeight": "600",
}

_EXTRACT_CONTAINER_STYLE = {
    "display": "none", "background": "rgba(251,191,36,0.1)", "borderRadius": "8px",
    "padding": "8px 12px", "border": "1px solid rgba(251,191,36,0.3)", "marginBottom": "8px",
}


def build_extract_selector() -> html.Div:
    """Wave-to-extract is FIXED at the 2nd channel (sin2, 1.0 Hz) for v1.07+."""
    return html.Div([
        html.Label("Wave to extract:", style={"fontSize": "0.75rem", "color": "#fbbf24", "fontWeight": "600"}),
        html.Div(
            f"{WAVE_NAMES[1]}  (locked — C = [0, 1, 0, 0])",
            id="extract-selector",
            style={"color": "#1e293b", "fontSize": "0.8rem", "fontWeight": "600", "marginTop": "4px"},
        ),
    ], id="extract-selector-container", style=_EXTRACT_CONTAINER_STYLE)


def build_id_mode_entry() -> html.Div:
    return html.Div(
        html.Button("Enter Identification Mode", id="enter-id-mode-btn", style=_ENTRY_BTN_STYLE),
        id="enter-id-mode-container",
    )


def build_id_mode_banner() -> html.Div:
    return html.Div([
        html.Div("IDENTIFICATION MODE — signals locked", style=_BANNER_STYLE),
        html.Button("Exit Identification Mode", id="exit-id-mode-btn", style=_EXIT_BTN_STYLE),
    ], id="exit-id-mode-container", style={"display": "none"})
