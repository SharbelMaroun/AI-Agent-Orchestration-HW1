import numpy as np
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

# ── Constants ─────────────────────────────────────────────────────────────────
RESOLUTION = 500
DURATION   = 10
WAVE_NAMES = ["Fundamental", "Second Harmonic", "Third Harmonic", "Fourth Harmonic"]
COLORS     = ["#6366f1", "#8b5cf6", "#ec4899", "#f43f5e"]
PI2        = 2 * np.pi

DEFAULTS = [
    dict(amplitude=50,  frequency=0.5,  phase=0.0,                    sampling_rate=20),
    dict(amplitude=30,  frequency=1.0,  phase=round(np.pi / 2,  2),   sampling_rate=20),
    dict(amplitude=20,  frequency=1.5,  phase=round(np.pi,       2),   sampling_rate=20),
    dict(amplitude=10,  frequency=2.0,  phase=round(3*np.pi / 2, 2),   sampling_rate=20),
]

# ── Clientside JS for instant chart updates (no server round-trip) ────────────
CLIENTSIDE_CHART_JS = """
function(a0,a1,a2,a3, f0,f1,f2,f3, p0,p1,p2,p3, e0,e1,e2,e3, d0,d1,d2,d3, s0,s1,s2,s3) {
    var amps    = [a0,a1,a2,a3];
    var freqs   = [f0,f1,f2,f3];
    var phases  = [p0,p1,p2,p3];
    var enabled = [e0,e1,e2,e3];
    var dotsMod = [d0,d1,d2,d3];
    var srs     = [s0,s1,s2,s3];

    var COLORS     = ["#6366f1","#8b5cf6","#ec4899","#f43f5e"];
    var WAVE_NAMES = ["Fundamental","Second Harmonic","Third Harmonic","Fourth Harmonic"];
    var PI2 = 2 * Math.PI;
    var N   = 500;
    var DUR = 10;

    // Continuous time axis
    var tCont = [];
    for (var k = 0; k <= N; k++) tCont.push(k / N * DUR);

    var overlayTraces = [];
    var sumY = new Array(N + 1).fill(0);

    for (var i = 0; i < 4; i++) {
        var isEnabled = enabled[i] && enabled[i].includes('on');
        if (!isEnabled) continue;

        var amp   = amps[i]   || 0;
        var freq  = freqs[i]  || 0.5;
        var phase = phases[i] || 0;
        var dots  = dotsMod[i] && dotsMod[i].includes('on');
        var sr    = srs[i]    || 20;

        // Always add to sum as continuous
        for (var j = 0; j <= N; j++) {
            sumY[j] += amp * Math.sin(PI2 * freq * tCont[j] + phase);
        }

        if (dots) {
            var nSamples = Math.floor(DUR * sr) + 1;
            var tS = [], yS = [];
            for (var n = 0; n < nSamples; n++) {
                var t = n / sr;
                tS.push(t);
                yS.push(amp * Math.sin(PI2 * freq * t + phase));
            }
            overlayTraces.push({
                x: tS, y: yS, mode: 'markers', type: 'scatter',
                marker: {color: COLORS[i], size: 5},
                name: 'CH' + (i+1) + ' \u00b7 ' + WAVE_NAMES[i]
            });
        } else {
            var yC = tCont.map(function(t) { return amp * Math.sin(PI2 * freq * t + phase); });
            overlayTraces.push({
                x: tCont, y: yC, mode: 'lines', type: 'scatter',
                line: {color: COLORS[i], width: 2},
                name: 'CH' + (i+1) + ' \u00b7 ' + WAVE_NAMES[i]
            });
        }
    }

    var figOverlay = {
        data: overlayTraces,
        layout: {
            title: {text: 'Channel Overlay (Mixed)', font: {size: 13, color: '#1e293b'}},
            xaxis: {range: [0, DUR], tickvals: [0,2,4,6,8,10], gridcolor: '#f1f5f9',
                    title: 'Time (s)', tickfont: {size: 9, color: '#94a3b8'},
                    zerolinecolor: '#e2e8f0'},
            yaxis: {range: [-100, 100], gridcolor: '#f1f5f9',
                    tickfont: {size: 9, color: '#94a3b8'}, zerolinecolor: '#e2e8f0'},
            plot_bgcolor: 'white', paper_bgcolor: 'white',
            height: 320, margin: {l: 50, r: 20, t: 50, b: 40},
            legend: {orientation: 'h', y: 1.12, font: {size: 9}},
            uirevision: 'overlay',
            shapes: [{type: 'line', x0: 0, x1: DUR, y0: 0, y1: 0,
                      line: {color: '#cbd5e1', width: 1}}]
        }
    };

    var figSum = {
        data: [{
            x: tCont, y: sumY, mode: 'lines', type: 'scatter',
            line: {color: '#818cf8', width: 3}, showlegend: false
        }],
        layout: {
            title: {text: 'Additive Summation \u2003\u2211 sin(2\u03c0ft + \u03c6)',
                    font: {size: 13, color: 'white'}},
            xaxis: {range: [0, DUR], tickvals: [0,2,4,6,8,10], gridcolor: '#1e293b',
                    title: 'Time (s)', tickfont: {size: 9, color: '#475569'},
                    linecolor: '#334155', zerolinecolor: '#334155'},
            yaxis: {range: [-150, 150], gridcolor: '#1e293b',
                    tickfont: {size: 9, color: '#475569'},
                    linecolor: '#334155', zerolinecolor: '#334155'},
            plot_bgcolor: '#020617', paper_bgcolor: '#0f172a',
            height: 320, margin: {l: 50, r: 20, t: 50, b: 40},
            font: {color: '#94a3b8'}, uirevision: 'sum',
            shapes: [{type: 'line', x0: 0, x1: DUR, y0: 0, y1: 0,
                      line: {color: '#334155', width: 1}}]
        }
    };

    return [figOverlay, figSum];
}
"""

# ── Helpers ───────────────────────────────────────────────────────────────────
def make_slider(sid, label, min_v, max_v, step, default):
    return html.Div([
        html.Label(label, style={
            'fontSize': '10px', 'fontWeight': '700', 'textTransform': 'uppercase',
            'letterSpacing': '0.08em', 'color': '#94a3b8', 'display': 'block', 'marginBottom': '2px',
        }),
        dcc.Slider(
            id=sid, min=min_v, max=max_v, step=step, value=default,
            marks=None, updatemode='drag',
            tooltip={'placement': 'bottom', 'always_visible': True},
        ),
    ], style={'marginBottom': '20px'})


def wave_panel(i):
    d = DEFAULTS[i]
    return html.Div([
        html.Div([
            html.Div([
                html.Div(style={
                    'width': '10px', 'height': '10px', 'borderRadius': '50%',
                    'backgroundColor': COLORS[i], 'marginRight': '8px', 'flexShrink': '0',
                }),
                html.Span(WAVE_NAMES[i], style={
                    'fontSize': '11px', 'fontWeight': '700', 'color': '#334155',
                    'textTransform': 'uppercase', 'letterSpacing': '0.05em',
                }),
            ], style={'display': 'flex', 'alignItems': 'center'}),
            dcc.Checklist(
                id=f'enabled-{i}',
                options=[{'label': '', 'value': 'on'}],
                value=['on'],
                inputStyle={'width': '16px', 'height': '16px', 'accentColor': '#6366f1',
                            'cursor': 'pointer', 'marginRight': '0'},
            ),
        ], style={'display': 'flex', 'justifyContent': 'space-between',
                  'alignItems': 'center', 'marginBottom': '14px'}),

        html.Div(id=f'wave-controls-{i}', children=[
            make_slider(f'freq-{i}',  'Frequency (Hz)',    0.1, 5.0,            0.01, d['frequency']),
            make_slider(f'amp-{i}',   'Amplitude',         0,   100,            1,    d['amplitude']),
            make_slider(f'phase-{i}', 'Phase shift (rad)', 0.0, round(PI2, 2),  0.01, d['phase']),

            html.Div([
                html.Label('Visual Mode', style={
                    'fontSize': '10px', 'fontWeight': '700', 'textTransform': 'uppercase',
                    'letterSpacing': '0.08em', 'color': '#94a3b8',
                }),
                dcc.Checklist(
                    id=f'dots-{i}',
                    options=[{'label': ' Dots (discrete sampling)', 'value': 'on'}],
                    value=[],
                    inputStyle={'accentColor': '#6366f1', 'cursor': 'pointer'},
                    labelStyle={'fontSize': '11px', 'color': '#475569'},
                ),
            ], style={'paddingTop': '10px', 'borderTop': '1px solid #e2e8f0', 'marginBottom': '12px'}),

            html.Div(id=f'sr-section-{i}', children=[
                make_slider(f'sr-{i}', 'Sampling Rate (Hz)', 1, 50, 1, d['sampling_rate']),
                html.Div(id=f'vector-{i}'),
            ], style={'display': 'none'}),
        ]),
    ], id=f'wave-panel-{i}', style={
        'padding': '14px', 'borderRadius': '12px', 'marginBottom': '16px',
        'border': '1px solid #e0e7ff', 'background': 'rgba(238,242,255,0.3)',
    })


# ── App layout ────────────────────────────────────────────────────────────────
app = Dash(__name__)
app.title = "Fourier Synthesis"

app.layout = html.Div([

    html.Header([
        html.Div([
            html.Div('〰️', style={'fontSize': '20px', 'marginRight': '10px'}),
            html.H1('Fourier Synthesis', style={
                'fontSize': '18px', 'fontWeight': '800', 'color': '#0f172a', 'margin': '0',
            }),
        ], style={'display': 'flex', 'alignItems': 'center'}),
        html.Button('↺  Reset Signal', id='reset-btn', n_clicks=0, style={
            'fontSize': '10px', 'fontWeight': '700', 'textTransform': 'uppercase',
            'letterSpacing': '0.1em', 'color': '#64748b', 'background': '#f8fafc',
            'border': '1px solid #e2e8f0', 'borderRadius': '20px',
            'padding': '6px 18px', 'cursor': 'pointer',
        }),
    ], style={
        'height': '60px', 'display': 'flex', 'alignItems': 'center',
        'justifyContent': 'space-between', 'padding': '0 28px',
        'background': 'white', 'borderBottom': '1px solid #e2e8f0',
        'position': 'sticky', 'top': '0', 'zIndex': '100',
        'boxShadow': '0 1px 3px rgba(0,0,0,0.05)',
    }),

    html.Div([
        html.Div([
            html.H2([
                html.Span('● ', style={'color': '#6366f1'}),
                'Signal Configuration',
            ], style={
                'fontSize': '10px', 'fontWeight': '900', 'textTransform': 'uppercase',
                'letterSpacing': '0.18em', 'color': '#94a3b8', 'marginBottom': '20px',
            }),
            *[wave_panel(i) for i in range(4)],
        ], style={
            'width': '300px', 'flexShrink': '0', 'background': 'white',
            'borderRight': '1px solid #e2e8f0', 'padding': '20px 18px',
            'overflowY': 'auto',
        }),

        html.Main([
            dcc.Graph(id='overlay-chart', config={'displayModeBar': False},
                      style={'marginBottom': '24px'}),
            dcc.Graph(id='sum-chart',     config={'displayModeBar': False}),
        ], style={
            'flex': '1', 'padding': '24px 28px', 'overflowY': 'auto', 'background': '#f8fafc',
        }),
    ], style={'display': 'flex', 'flex': '1', 'overflow': 'hidden'}),

    html.Footer([
        html.Span([
            html.Span('● ', style={'color': '#22c55e'}),
            'Kernel Protocol Loaded // Ready',
        ], style={'fontSize': '9px', 'fontFamily': 'monospace', 'color': '#94a3b8',
                  'textTransform': 'uppercase', 'letterSpacing': '0.1em'}),
        html.Span('Synthesizer V.05', style={
            'fontSize': '9px', 'fontFamily': 'monospace', 'color': '#cbd5e1',
            'textTransform': 'uppercase', 'letterSpacing': '0.1em',
        }),
    ], style={
        'height': '36px', 'display': 'flex', 'alignItems': 'center',
        'justifyContent': 'space-between', 'padding': '0 28px',
        'background': 'white', 'borderTop': '1px solid #e2e8f0',
    }),

], style={
    'height': '100vh', 'display': 'flex', 'flexDirection': 'column',
    'fontFamily': 'ui-sans-serif, system-ui, sans-serif', 'color': '#1e293b',
    'overflow': 'hidden',
})


# ── Clientside callback: charts update instantly in the browser (no round-trip)
app.clientside_callback(
    CLIENTSIDE_CHART_JS,
    Output('overlay-chart', 'figure'),
    Output('sum-chart',     'figure'),
    [Input(f'amp-{i}',     'value') for i in range(4)] +
    [Input(f'freq-{i}',    'value') for i in range(4)] +
    [Input(f'phase-{i}',   'value') for i in range(4)] +
    [Input(f'enabled-{i}', 'value') for i in range(4)] +
    [Input(f'dots-{i}',    'value') for i in range(4)] +
    [Input(f'sr-{i}',      'value') for i in range(4)],
)


# ── Python callbacks: show/hide panels + discrete vector (sidebar only) ───────
for _i in range(4):
    @app.callback(
        Output(f'wave-controls-{_i}', 'style'),
        Output(f'wave-panel-{_i}',    'style'),
        Input(f'enabled-{_i}', 'value'),
    )
    def toggle_wave(enabled_val):
        active = bool(enabled_val and 'on' in enabled_val)
        return (
            {} if active else {'display': 'none'},
            {
                'padding': '14px', 'borderRadius': '12px', 'marginBottom': '16px',
                'border': '1px solid #e0e7ff',
                'background': 'rgba(238,242,255,0.3)' if active else '#f8fafc',
                'opacity': '1' if active else '0.55',
            },
        )

    @app.callback(
        Output(f'sr-section-{_i}', 'style'),
        Input(f'dots-{_i}', 'value'),
    )
    def toggle_sr(dots_val):
        return {'display': 'block'} if (dots_val and 'on' in dots_val) else {'display': 'none'}

    @app.callback(
        Output(f'vector-{_i}', 'children'),
        Input(f'dots-{_i}',    'value'),
        Input(f'sr-{_i}',      'value'),
        Input(f'freq-{_i}',    'value'),
        Input(f'amp-{_i}',     'value'),
        Input(f'phase-{_i}',   'value'),
    )
    def update_vector(dots_val, sr, freq, amp, phase, _idx=_i):
        if not (dots_val and 'on' in dots_val):
            return []
        sr    = sr    or DEFAULTS[_idx]['sampling_rate']
        freq  = freq  or DEFAULTS[_idx]['frequency']
        amp   = amp   or DEFAULTS[_idx]['amplitude']
        phase = phase or DEFAULTS[_idx]['phase']

        n_s = int(DURATION * sr) + 1
        t_s = np.arange(n_s) / sr
        y_s = amp * np.sin(PI2 * freq * t_s + phase)

        spans = []
        for n_idx, (t_val, y_val) in enumerate(zip(t_s, y_s)):
            spans.append(html.Span(
                f"{y_val:.1f}",
                title=f"n={n_idx}, t={t_val:.2f}s",
                style={'color': '#34d399', 'cursor': 'default'},
            ))
            if n_idx < n_s - 1:
                spans.append(html.Span(", ", style={'color': '#475569'}))

        return html.Div([
            html.Div(
                f"Discrete Vector y[n]   n = 0…{n_s - 1}",
                style={'fontSize': '9px', 'fontWeight': '700', 'color': '#94a3b8',
                       'textTransform': 'uppercase', 'letterSpacing': '0.08em', 'marginBottom': '6px'},
            ),
            html.Div([
                html.Span("[", style={'color': '#64748b', 'fontWeight': 'bold'}),
                *spans,
                html.Span("]", style={'color': '#64748b', 'fontWeight': 'bold'}),
            ], style={
                'background': '#0f172a', 'border': '1px solid #1e293b', 'borderRadius': '8px',
                'padding': '10px 12px', 'fontFamily': 'monospace', 'fontSize': '0.72rem',
                'maxHeight': '96px', 'overflowY': 'auto', 'lineHeight': '1.6', 'wordBreak': 'break-all',
            }),
        ])


# ── Reset ─────────────────────────────────────────────────────────────────────
@app.callback(
    [Output(f'amp-{i}',     'value') for i in range(4)] +
    [Output(f'freq-{i}',    'value') for i in range(4)] +
    [Output(f'phase-{i}',   'value') for i in range(4)] +
    [Output(f'enabled-{i}', 'value') for i in range(4)] +
    [Output(f'dots-{i}',    'value') for i in range(4)] +
    [Output(f'sr-{i}',      'value') for i in range(4)],
    Input('reset-btn', 'n_clicks'),
    prevent_initial_call=True,
)
def reset(_):
    return (
        [d['amplitude']     for d in DEFAULTS] +
        [d['frequency']     for d in DEFAULTS] +
        [d['phase']         for d in DEFAULTS] +
        [['on']             for _  in DEFAULTS] +
        [[]                 for _  in DEFAULTS] +
        [d['sampling_rate'] for d in DEFAULTS]
    )


if __name__ == '__main__':
    app.run(debug=True)
