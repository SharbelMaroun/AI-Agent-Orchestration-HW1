from __future__ import annotations

from dash import Input, Output

CLIENTSIDE_CHART_JS = """
function(C, freq0,freq1,freq2,freq3, amp0,amp1,amp2,amp3,
         phase0,phase1,phase2,phase3, dots0,dots1,dots2,dots3,
         sr0,sr1,sr2,sr3, windowStart, noiseSigma) {

    const N = 501, DUR = 10.0, PI2 = 2 * Math.PI;
    const tCont = Array.from({length: N}, (_, k) => k * DUR / (N - 1));
    const sumY = new Array(N).fill(0);

    const amps   = [amp0,   amp1,   amp2,   amp3];
    const freqs  = [freq0,  freq1,  freq2,  freq3];
    const phases = [phase0, phase1, phase2, phase3];
    const srs    = [sr0,    sr1,    sr2,    sr3];
    const dots   = [dots0,  dots1,  dots2,  dots3];
    const colors = ['#38bdf8','#f59e0b','#22c55e','#ef4444'];
    const names  = ['Fundamental','Second Harmonic','Third Harmonic','Fourth Harmonic'];

    const overlayTraces = [];

    for (let i = 0; i < 4; i++) {
        if (!C || C[i] !== 1) continue;
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
    const sigma = Number(noiseSigma || 0);
    const sumTrace = {x: tCont, y: sumY, mode: 'lines', name: 'Σ',
        line: {color: '#ffffff'}, showlegend: false};

    const sumShapes = [{type:'rect', x0: ws, x1: ws + 1.0, y0:-150, y1:150,
        fillcolor:'rgba(251,191,36,0.2)', line:{color:'rgba(251,191,36,0.6)',width:1}}];

    const sumData = [...overlayTraces.map(t => ({...t, opacity: 0.3})), sumTrace];

    if (sigma > 0) {
        const noiseX = [], noiseY = [];
        const maxAbs = Math.max(...sumY.map(Math.abs), 1e-8);
        for (let k = 0; k < N; k++) {
            const u1 = Math.random() + 1e-10, u2 = Math.random();
            const noise = sigma * Math.sqrt(-2 * Math.log(u1)) * Math.cos(PI2 * u2) * maxAbs * 3;
            noiseX.push(tCont[k]);
            noiseY.push(sumY[k] + noise);
        }
        sumData.push({x: noiseX, y: noiseY, mode: 'markers', name: 'noise',
            marker: {color:'rgba(251,191,36,0.85)', size: 3, symbol: 'circle'},
            showlegend: false});
    }

    const overlayFig = {
        data: overlayTraces,
        layout: {paper_bgcolor:'#fff', plot_bgcolor:'#fff',
            xaxis:{title:'Time (s)'}, yaxis:{title:'Amplitude', range:[-100,100]},
            margin:{t:20,b:40,l:50,r:10}, legend:{orientation:'h'}}
    };
    const sumFig = {
        data: sumData,
        layout: {paper_bgcolor:'#020617', plot_bgcolor:'#020617',
            xaxis:{title:'Time (s)', color:'#94a3b8', gridcolor:'#1e293b'},
            yaxis:{title:'Σ Amplitude', range:[-150,150], color:'#94a3b8', gridcolor:'#1e293b'},
            font:{color:'#94a3b8'}, margin:{t:20,b:40,l:50,r:10},
            shapes: sumShapes}
    };
    return [overlayFig, sumFig];
}
"""


def register_clientside_callback(app: object) -> None:
    inputs = (
        [Input("channel-vector", "data")] +
        [Input(f"freq-{i}", "value") for i in range(4)] +
        [Input(f"amp-{i}", "value") for i in range(4)] +
        [Input(f"phase-{i}", "value") for i in range(4)] +
        [Input(f"dots-{i}", "value") for i in range(4)] +
        [Input(f"sr-{i}", "value") for i in range(4)] +
        [Input("window-slider", "value")] +
        [Input("noise-slider", "value")]
    )

    app.clientside_callback(
        CLIENTSIDE_CHART_JS,
        [Output("overlay-chart", "figure"), Output("sum-chart", "figure")],
        inputs,
    )
