"""Identification-mode callbacks — entry/exit toggle and UI lock/unlock.

Extracted from callbacks_server.py to keep both files under the 150-line cap.
"""
from __future__ import annotations

from typing import Any

from dash import Input, Output, ctx, no_update

from fourier.shared.constants import ID_MODE_SIGNALS

_LOCK_STYLE = {"pointerEvents": "none", "userSelect": "none", "opacity": "0.6"}
_UNLOCKED: dict[str, str] = {}
_EXTRACT_VISIBLE = {
    "display": "block", "background": "rgba(251,191,36,0.1)", "borderRadius": "8px",
    "padding": "8px 12px", "border": "1px solid rgba(251,191,36,0.3)", "marginBottom": "8px",
}


def _toggle_outputs() -> list[Output]:
    return (
        [Output("id-mode-active", "data")] +
        [Output(f"freq-{i}", "value") for i in range(4)] +
        [Output(f"amp-{i}", "value") for i in range(4)] +
        [Output(f"phase-{i}", "value") for i in range(4)] +
        [Output(f"enabled-{i}", "value") for i in range(4)] +
        [Output(f"dots-{i}", "value") for i in range(4)] +
        [Output(f"sr-{i}", "value") for i in range(4)]
    )


def _enter_id_mode_values() -> list[Any]:
    return (
        [True] +
        [ID_MODE_SIGNALS[i]["frequency"] for i in range(4)] +
        [ID_MODE_SIGNALS[i]["amplitude"] for i in range(4)] +
        [ID_MODE_SIGNALS[i]["phase"] for i in range(4)] +
        [["on"] for _ in range(4)] +
        [["on"] for _ in range(4)] +
        [20 for _ in range(4)]
    )


def _sync_outputs() -> list[Output]:
    return (
        [Output("enter-id-mode-container", "style"),
         Output("exit-id-mode-container", "style"),
         Output("identify-btn-container", "style"),
         Output("sidebar-lock-overlay", "style"),
         Output("sidebar-panels", "style"),
         Output("extract-selector-container", "style")] +
        [Output(f"enabled-wrap-{i}", "style") for i in range(4)] +
        [Output(f"fixed-controls-{i}", "style") for i in range(4)]
    )


def _sync_styles(active: bool) -> list[dict]:
    if active:
        return (
            [{"display": "none"}, {"display": "block"}, {"display": "block"},
             {"display": "none"}, {}, _EXTRACT_VISIBLE] +
            [_LOCK_STYLE for _ in range(8)]
        )
    return (
        [{"display": "block"}, {"display": "none"}, {"display": "none"},
         {"display": "none"}, {}, {"display": "none"}] +
        [_UNLOCKED for _ in range(8)]
    )


def register_id_mode_callbacks(app: Any) -> None:
    @app.callback(
        _toggle_outputs(),
        [Input("enter-id-mode-btn", "n_clicks"), Input("exit-id-mode-btn", "n_clicks")],
        prevent_initial_call=True,
    )
    def toggle_id_mode(_enter: Any, _exit: Any) -> list[Any]:
        if ctx.triggered_id == "enter-id-mode-btn":
            return _enter_id_mode_values()
        return [False] + [no_update] * 24

    @app.callback(_sync_outputs(), Input("id-mode-active", "data"))
    def sync_id_mode_ui(active: bool) -> list[dict]:
        return _sync_styles(active)
