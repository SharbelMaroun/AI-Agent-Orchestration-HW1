from __future__ import annotations

from dash import html

from fourier.shared.constants import EXTRACT_POINTS, WAVE_NAMES


def _build_extraction_panel(
    real: list[float], wave_name: str, wave_color: str,
    rnn_result: dict | None = None,
    lstm_result: dict | None = None,
    fc_result: dict | None = None,
) -> html.Div:
    rnn_coords = rnn_result["coordinates"] if rnn_result else [None] * EXTRACT_POINTS
    lstm_coords = lstm_result["coordinates"] if lstm_result else [None] * EXTRACT_POINTS
    fc_coords = fc_result["coordinates"] if fc_result else [None] * EXTRACT_POINTS

    def _err_cell(pred: float | None, truth: float) -> html.Td:
        if pred is None:
            return html.Td("—", style={"fontFamily": "monospace", "fontSize": "0.7rem",
                                        "color": "#94a3b8", "paddingRight": "8px"})
        e = round(pred - truth, 2)
        return html.Td(f"{e:+.2f}", style={"fontFamily": "monospace", "fontSize": "0.7rem",
                                            "paddingRight": "8px",
                                            "color": "#ef4444" if abs(e) > 1 else "#22c55e"})

    rows = []
    for k in range(EXTRACT_POINTS):
        rows.append(html.Tr([
            html.Td(f"[{k}]", style={"fontFamily": "monospace", "fontSize": "0.7rem",
                                     "color": "#94a3b8", "paddingRight": "6px"}),
            html.Td(f"{rnn_coords[k]:8.2f}" if rnn_coords[k] is not None else "—",
                    style={"fontFamily": "monospace", "color": "#a78bfa",
                           "fontSize": "0.7rem", "paddingRight": "8px"}),
            html.Td(f"{lstm_coords[k]:8.2f}" if lstm_coords[k] is not None else "—",
                    style={"fontFamily": "monospace", "color": "#34d399",
                           "fontSize": "0.7rem", "paddingRight": "8px"}),
            html.Td(f"{fc_coords[k]:8.2f}" if fc_coords[k] is not None else "—",
                    style={"fontFamily": "monospace", "color": "#f472b6",
                           "fontSize": "0.7rem", "paddingRight": "8px"}),
            html.Td(f"{real[k]:8.2f}", style={"fontFamily": "monospace", "color": wave_color,
                                               "fontSize": "0.7rem", "paddingRight": "8px"}),
            _err_cell(rnn_coords[k], real[k]),
            _err_cell(lstm_coords[k], real[k]),
            _err_cell(fc_coords[k], real[k]),
        ]))
    table = html.Table([
        html.Thead(html.Tr([
            html.Th("n", style={"fontSize": "0.65rem", "color": "#64748b", "paddingRight": "6px"}),
            html.Th("RNN", style={"fontSize": "0.65rem", "color": "#a78bfa", "paddingRight": "8px"}),
            html.Th("LSTM", style={"fontSize": "0.65rem", "color": "#34d399", "paddingRight": "8px"}),
            html.Th("FC", style={"fontSize": "0.65rem", "color": "#f472b6", "paddingRight": "8px"}),
            html.Th("real", style={"fontSize": "0.65rem", "color": wave_color, "paddingRight": "8px"}),
            html.Th("err(R)", style={"fontSize": "0.65rem", "color": "#a78bfa", "paddingRight": "8px"}),
            html.Th("err(L)", style={"fontSize": "0.65rem", "color": "#34d399", "paddingRight": "8px"}),
            html.Th("err(F)", style={"fontSize": "0.65rem", "color": "#f472b6"}),
        ])),
        html.Tbody(rows),
    ], style={"borderCollapse": "collapse"})

    summary_bits = []
    if rnn_result is not None:
        summary_bits.append(html.Span(f"RNN MAE = {rnn_result.get('mae', 0.0):.2f}",
                                       style={"color": "#a78bfa", "marginRight": "12px"}))
    if lstm_result is not None:
        summary_bits.append(html.Span(f"LSTM MAE = {lstm_result.get('mae', 0.0):.2f}",
                                       style={"color": "#34d399", "marginRight": "12px"}))
    if fc_result is not None:
        summary_bits.append(html.Span(f"FC MAE = {fc_result.get('mae', 0.0):.2f}",
                                       style={"color": "#f472b6"}))
    summary = html.Div(summary_bits, style={"fontFamily": "monospace", "fontSize": "0.7rem",
                                              "marginTop": "6px"}) if summary_bits else None

    children = [
        html.Strong(f"Extracting: {wave_name}", style={"color": wave_color}),
        html.P(f"C = {[1 if w == wave_name else 0 for w in WAVE_NAMES]}  |  "
               f"RNN vs. LSTM vs. FC regressor",
               style={"fontSize": "0.7rem", "color": "#94a3b8", "margin": "2px 0 6px"}),
        table,
    ]
    if summary is not None:
        children.append(summary)
    return html.Div(children, style={"padding": "8px", "background": "#0f172a", "borderRadius": "6px",
                                       "border": f"1px solid {wave_color}40"})
