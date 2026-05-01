from __future__ import annotations

from typing import Any

from dash import html

from fourier.shared.constants import COLORS, WAVE_NAMES
from fourier.shared.types import ClassifierResult


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
