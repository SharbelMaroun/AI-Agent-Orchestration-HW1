from __future__ import annotations

from dash import Input, Output

CLIENTSIDE_CHART_JS = """
function(en0,en1,en2,en3, freq0,freq1,freq2,freq3, amp0,amp1,amp2,amp3,
         phase0,phase1,phase2,phase3, dots0,dots1,dots2,dots3,
         sr0,sr1,sr2,sr3, windowStart) {

    const N = 501, DUR = 10.0, PI2 = 2 * Math.PI;
    const tCont = Array.from({length: N}, (_, k) => k * DUR / (N - 1));
    const sumY = new Array(N).fill(0);

    const amps   = [amp0,   amp1,   amp2,   amp3];
    const freqs  = [freq0,  freq1,  freq2,  freq3];
    const phases = [phase0, phase1, phase2, phase3];
    const srs    = [sr0,    sr1,    sr2,    sr3];
    const enabled = [en0,   en1,    en2,    en3];
    const dots   = [dots0,  dots1,  dots2,  dots3];
    const colors = ['#38bdf8','#f59e0b','#22c55e','#ef4444'];
    const names  = ['Fundamental','Second Harmonic','Third Harmonic','Fourth Harmonic'];

    const overlayTraces = [];

    for (let i = 0; i < 4; i++) {
        const isEnabled = enabled[i] && enabled[i].length > 0;
        if (!isEnabled) continue;
        const A = Number(amps[i]), f = Number(freqs[i]), ph = Number(phases[i]);
        const yC = tCont.map(t => A * Math.sin(PI2 * f * t + ph));
        for (let k = 0; k < N; k++) sumY[k] += yC[k];

        if (dots[i] && dots[i].length > 0) {
            const sr = Number(srs[i]);
            const nSamples = Math.floor(DUR * sr) + 1;
            const tDisc = Array.from({length: nSamples}, (_, n) => n / sr);
            const yDisc = tDisc.map(t => A * Math.sin(PI2 * f * t + ph));
            overlayTraces.push({x: tDisc, y: yDisc, mode: 'markers', name: names[i],
                marker: {color: colors[i], size: 5}, showlegend: true});
        } else {
            overlayTraces.push({x: tCont, y: yC, mode: 'lines', name: names[i],
                line: {color: colors[i]}, showlegend: true});
        }
    }

    const ws = Number(windowStart || 0);
    const sumTrace = {x: tCont, y: sumY, mode: 'lines', name: 'Σ',
        line: {color: '#ffffff'}, showlegend: false};

    const overlayFig = {
        data: overlayTraces,
        layout: {paper_bgcolor:'#fff', plot_bgcolor:'#fff',
            xaxis:{title:'Time (s)'}, yaxis:{title:'Amplitude', range:[-100,100]},
            margin:{t:20,b:40,l:50,r:10}, legend:{orientation:'h'}}
    };
    const sumFig = {
        data: [...overlayTraces.map(t => ({...t, opacity: 0.3})), sumTrace],
        layout: {paper_bgcolor:'#020617', plot_bgcolor:'#020617',
            xaxis:{title:'Time (s)', color:'#94a3b8', gridcolor:'#1e293b'},
            yaxis:{title:'Σ Amplitude', range:[-150,150], color:'#94a3b8', gridcolor:'#1e293b'},
            font:{color:'#94a3b8'}, margin:{t:20,b:40,l:50,r:10},
            shapes:[{type:'rect', x0: ws, x1: ws + 1.0, y0:-150, y1:150,
                fillcolor:'rgba(251,191,36,0.2)', line:{color:'rgba(251,191,36,0.6)',width:1}}]}
    };
    return [overlayFig, sumFig];
}
"""


def register_clientside_callback(app: object) -> None:
    inputs = (
        [Input(f"enabled-{i}", "value") for i in range(4)] +
        [Input(f"freq-{i}", "value") for i in range(4)] +
        [Input(f"amp-{i}", "value") for i in range(4)] +
        [Input(f"phase-{i}", "value") for i in range(4)] +
        [Input(f"dots-{i}", "value") for i in range(4)] +
        [Input(f"sr-{i}", "value") for i in range(4)] +
        [Input("window-slider", "value")]
    )

    app.clientside_callback(
        CLIENTSIDE_CHART_JS,
        [Output("overlay-chart", "figure"), Output("sum-chart", "figure")],
        inputs,
    )
