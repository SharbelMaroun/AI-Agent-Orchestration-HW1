from __future__ import annotations

from dash import Input, Output

CLIENTSIDE_CHART_JS = """
function(activeChannels, freq0,freq1,freq2,freq3, amp0,amp1,amp2,amp3,
         phase0,phase1,phase2,phase3, dots0,dots1,dots2,dots3,
         sr0,sr1,sr2,sr3, windowStart,
         alpha0,alpha1,alpha2,alpha3,
         beta0,beta1,beta2,beta3, idMode) {

    const N = 501, DUR = 10.0, PI2 = 2 * Math.PI;
    const tCont = Array.from({length: N}, (_, k) => k * DUR / (N - 1));
    const sumY = new Array(N).fill(0);

    const amps   = [amp0,   amp1,   amp2,   amp3];
    const freqs  = [freq0,  freq1,  freq2,  freq3];
    const phases = [phase0, phase1, phase2, phase3];
    const srs    = [sr0,    sr1,    sr2,    sr3];
    const alphas = [Number(alpha0||0)/100, Number(alpha1||0)/100,
                    Number(alpha2||0)/100, Number(alpha3||0)/100];
    const betas  = [Number(beta0||0)/100,  Number(beta1||0)/100,
                    Number(beta2||0)/100,  Number(beta3||0)/100];
    const dotsRaw = [dots0, dots1, dots2, dots3];
    const dots = idMode ? [['on'],['on'],['on'],['on']] : dotsRaw;
    const colors = ['#38bdf8','#f59e0b','#22c55e','#ef4444'];
    const names  = ['sin1','sin2','sin3','sin4'];

    // Per-sample ε ~ Uniform(-1, +1): each point gets its own jitter on A and φ.
    function sampleAt(t, A, f, ph, alpha, beta) {
        if (alpha === 0 && beta === 0) return A * Math.sin(PI2 * f * t + ph);
        const eps = 2 * Math.random() - 1;
        return (A + alpha * A * eps) * Math.sin(PI2 * f * t + ph + beta * Math.PI * eps);
    }

    const overlayTraces = [], pureTraces = [];
    for (let i = 0; i < 4; i++) {
        if (!activeChannels || activeChannels[i] !== 1) continue;
        const A = Number(amps[i]), f = Number(freqs[i]), ph = Number(phases[i]);
        const a_i = alphas[i], b_i = betas[i];
        const yCont = tCont.map(t => sampleAt(t, A, f, ph, a_i, b_i));
        for (let k = 0; k < N; k++) sumY[k] += yCont[k];

        const dotsOn = dots[i] && dots[i].length > 0;
        if (dotsOn) {
            const sr = idMode ? 1000 : Number(srs[i]);
            const nSamples = Math.floor(DUR * sr) + 1;
            const tDisc = Array.from({length: nSamples}, (_, n) => n / sr);
            const yDisc = tDisc.map(t => sampleAt(t, A, f, ph, a_i, b_i));
            const yDiscPure = tDisc.map(t => A * Math.sin(PI2 * f * t + ph));
            const markerSize = idMode ? 1.5 : 5;
            overlayTraces.push({x: tDisc, y: yDisc, mode: 'markers', name: names[i],
                marker: {color: colors[i], size: markerSize}, showlegend: true});
            pureTraces.push({x: tDisc, y: yDiscPure, mode: 'markers', name: names[i],
                marker: {color: colors[i], size: markerSize}, showlegend: true});
        } else {
            const yPure = tCont.map(t => A * Math.sin(PI2 * f * t + ph));
            overlayTraces.push({x: tCont, y: yCont, mode: 'lines', name: names[i],
                line: {color: colors[i]}, showlegend: true});
            pureTraces.push({x: tCont, y: yPure, mode: 'lines', name: names[i],
                line: {color: colors[i]}, showlegend: true});
        }
    }

    const ws = Number(windowStart || 0);

    let sumTrace;
    if (idMode) {
        const sumSr = 1000;
        const nSum = Math.floor(DUR * sumSr) + 1;
        const tDisc = Array.from({length: nSum}, (_, n) => n / sumSr);
        // Per-sample, per-channel ε — same model as the overlay.
        const yDisc = tDisc.map(t => {
            let v = 0;
            for (let i = 0; i < 4; i++) {
                if (!activeChannels || activeChannels[i] !== 1) continue;
                v += sampleAt(t, Number(amps[i]), Number(freqs[i]), Number(phases[i]),
                              alphas[i], betas[i]);
            }
            return v;
        });
        sumTrace = {x: tDisc, y: yDisc, mode: 'markers', name: 'Σ',
            marker: {color: '#ffffff', size: 1.5}, showlegend: false};
    } else {
        sumTrace = {x: tCont, y: sumY, mode: 'lines', name: 'Σ',
            line: {color: '#ffffff'}, showlegend: false};
    }

    const sumShapes = [{type:'rect', x0: ws, x1: ws + 0.01, y0:-150, y1:150,
        fillcolor:'rgba(251,191,36,0.45)', line:{color:'rgba(251,191,36,0.9)',width:1}}];
    const sumData = [...overlayTraces.map(t => ({...t, opacity: 0.3})), sumTrace];

    const lightLayout = (title) => ({paper_bgcolor:'#fff', plot_bgcolor:'#fff',
        title:{text: title, font:{size:12, color:'#475569'}, x:0.01, y:0.97},
        xaxis:{title:'Time (s)'}, yaxis:{title:'Amplitude', range:[-100,100]},
        margin:{t:24,b:40,l:50,r:10}, legend:{orientation:'h'}});
    const overlayFig = {data: overlayTraces, layout: lightLayout('With noise (per-channel)')};
    const pureFig = {data: pureTraces, layout: lightLayout('Pure (no noise)')};
    const sumFig = {
        data: sumData,
        layout: {paper_bgcolor:'#020617', plot_bgcolor:'#020617',
            xaxis:{title:'Time (s)', color:'#94a3b8', gridcolor:'#1e293b'},
            yaxis:{title:'Σ Amplitude', range:[-150,150], color:'#94a3b8', gridcolor:'#1e293b'},
            font:{color:'#94a3b8'}, margin:{t:20,b:40,l:50,r:10},
            shapes: sumShapes}
    };
    return [overlayFig, pureFig, sumFig];
}
"""


def register_clientside_callback(app: object) -> None:
    inputs = (
        [Input("active-channels", "data")] +
        [Input(f"freq-{i}", "value") for i in range(4)] +
        [Input(f"amp-{i}", "value") for i in range(4)] +
        [Input(f"phase-{i}", "value") for i in range(4)] +
        [Input(f"dots-{i}", "value") for i in range(4)] +
        [Input(f"sr-{i}", "value") for i in range(4)] +
        [Input("window-slider", "value")] +
        [Input(f"alpha-{i}", "value") for i in range(4)] +
        [Input(f"beta-{i}", "value") for i in range(4)] +
        [Input("id-mode-active", "data")]
    )

    app.clientside_callback(
        CLIENTSIDE_CHART_JS,
        [Output("overlay-chart", "figure"),
         Output("pure-chart", "figure"),
         Output("sum-chart", "figure")],
        inputs,
    )
