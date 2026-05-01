import { useState, useMemo } from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  ResponsiveContainer,
  Tooltip,
  ReferenceLine
} from 'recharts';
import { 
  Activity, 
  RotateCcw, 
  GripHorizontal,
  Waves,
  Zap,
  MoveHorizontal,
  TrendingUp,
  Settings2
} from 'lucide-react';
import { motion, AnimatePresence, Reorder, useDragControls } from 'motion/react';

interface WaveParams {
  amplitude: number;
  frequency: number;
  phase: number;
  enabled: boolean;
  isDotsMode: boolean;
  samplingRate: number; // Samples per second
}

const RESOLUTION = 500;
const DURATION_SECONDS = 10;

const WAVE_NAMES = ["Fundamental", "Second Harmonic", "Third Harmonic", "Fourth Harmonic"];

function SineWaveChart({ params, color, isDark = false }: { params: WaveParams; color: string; isDark?: boolean }) {
  const data = useMemo(() => {
    const allX = new Set<number>();
    
    // Continuous base
    for (let i = 0; i <= RESOLUTION; i++) {
      allX.add((i / RESOLUTION) * DURATION_SECONDS);
    }
    
    // Sampling base
    if (params.isDotsMode) {
      const Ts = 1 / params.samplingRate;
      for (let n = 0; n <= DURATION_SECONDS * params.samplingRate; n++) {
        allX.add(Number((n * Ts).toFixed(8)));
      }
    }

    const sortedX = Array.from(allX).sort((a, b) => a - b);

    return sortedX.map(x => {
      let y: number | null = null;
      if (params.isDotsMode) {
        const Ts = 1 / params.samplingRate;
        const res = x / Ts;
        if (Math.abs(res - Math.round(res)) < 1e-7) {
          y = params.amplitude * Math.sin(2 * Math.PI * params.frequency * x + params.phase);
        }
      } else {
        y = params.amplitude * Math.sin(2 * Math.PI * params.frequency * x + params.phase);
      }
      return { x, y: y as any };
    });
  }, [params]);

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 10 }}>
        <CartesianGrid 
          strokeDasharray="3 3" 
          vertical={false} 
          stroke={isDark ? "#1e293b" : "#f1f5f9"} 
        />
        <XAxis dataKey="x" hide />
        <YAxis 
          domain={isDark ? [-150, 150] : [-100, 100]} 
          hide
        />
        <Tooltip 
          contentStyle={{ 
            borderRadius: '8px', 
            border: 'none', 
            boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
            fontFamily: 'JetBrains Mono',
            fontSize: '10px',
            backgroundColor: isDark ? '#1e293b' : '#ffffff',
            color: isDark ? '#f8fafc' : '#1e293b'
          }}
          itemStyle={{ color: isDark ? '#818cf8' : color }}
        />
        <Line 
          type="monotone" 
          dataKey="y" 
          stroke={color} 
          strokeWidth={params.isDotsMode ? 0 : (isDark ? 3 : 1.5)} 
          dot={params.isDotsMode ? { r: 2, fill: color, strokeWidth: 0 } : false}
          isAnimationActive={false}
          connectNulls={false}
          className={isDark ? "drop-shadow-[0_0_8px_rgba(129,140,248,0.5)]" : "opacity-80"}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

function ControlSlider({ 
  label, 
  value, 
  min, 
  max, 
  step, 
  icon: Icon,
  onChange 
}: { 
  label: string; 
  value: number; 
  min: number; 
  max: number; 
  step: number;
  icon: any;
  onChange: (val: number) => void;
}) {
  return (
    <div className="flex flex-col gap-1.5 px-0.5 relative z-30">
      <div className="flex justify-between items-center px-1">
        <div className="flex items-center gap-2">
           <Icon size={12} className="text-slate-400 group-hover:text-indigo-500 transition-colors" />
           <label className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">{label}</label>
        </div>
        <span className="text-[10px] font-mono font-bold text-indigo-600 bg-indigo-50 px-1.5 py-0.5 rounded leading-none transition-all group-hover:bg-indigo-100">
          {value.toFixed(2)}
        </span>
      </div>
      <div className="px-1 py-1">
        <input 
          type="range" 
          min={min} 
          max={max} 
          step={step} 
          value={value} 
          onChange={(e) => onChange(parseFloat(e.target.value))}
          className="w-full relative z-40 accent-indigo-600 h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer"
          style={{ pointerEvents: "auto" }}
        />
      </div>
    </div>
  );
}

function ReorderItemComponent({ value, children, isDark, isDraggable = true }: { value: string; children: React.ReactNode, isDark?: boolean, isDraggable?: boolean }) {
  const controls = useDragControls();

  return (
    <Reorder.Item 
      value={value} 
      as="div" 
      className={`relative ${isDraggable ? 'z-10' : ''}`} 
      dragListener={false} 
      dragControls={isDraggable ? controls : undefined}
    >
      {isDraggable && (
        <div className="absolute top-6 left-6 z-20" onPointerDown={(e) => controls.start(e)} style={{ touchAction: "none" }}>
          <div className={`p-2 rounded-lg cursor-grab active:cursor-grabbing backdrop-blur-md border shadow-sm transition-colors ${
            isDark 
              ? 'bg-slate-800/80 border-slate-700 text-slate-400 hover:text-slate-200' 
              : 'bg-white/80 border-slate-200 text-slate-400 hover:text-slate-600'
          }`}>
            <GripHorizontal size={24} />
          </div>
        </div>
      )}
      {children}
    </Reorder.Item>
  );
}

export default function App() {
  const [waves, setWaves] = useState<WaveParams[]>([
    { amplitude: 50, frequency: 0.5, phase: 0, enabled: true, isDotsMode: false, samplingRate: 20 },
    { amplitude: 30, frequency: 1.0, phase: Math.PI / 2, enabled: true, isDotsMode: false, samplingRate: 20 },
    { amplitude: 20, frequency: 1.5, phase: Math.PI, enabled: true, isDotsMode: false, samplingRate: 20 },
    { amplitude: 10, frequency: 2.0, phase: (3 * Math.PI) / 2, enabled: true, isDotsMode: false, samplingRate: 20 },
  ]);

  const [graphOrder, setGraphOrder] = useState(['mixed', 'sum']);

  const colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e'];

  const updateWave = (index: number, partial: Partial<WaveParams>) => {
    setWaves(prev => prev.map((w, i) => i === index ? { ...w, ...partial } : w));
  };

  const resetAll = () => {
    setWaves([
      { amplitude: 50, frequency: 0.5, phase: 0, enabled: true, isDotsMode: false, samplingRate: 20 },
      { amplitude: 30, frequency: 1.0, phase: Math.PI / 2, enabled: true, isDotsMode: false, samplingRate: 20 },
      { amplitude: 20, frequency: 1.5, phase: Math.PI, enabled: true, isDotsMode: false, samplingRate: 20 },
      { amplitude: 10, frequency: 2.0, phase: (3 * Math.PI) / 2, enabled: true, isDotsMode: false, samplingRate: 20 },
    ]);
  };

  const overlayData = useMemo(() => {
    const allX = new Set<number>();
    
    // 1. Continuous grid for lines (ensures smoothness)
    for (let i = 0; i <= RESOLUTION; i++) {
      allX.add((i / RESOLUTION) * DURATION_SECONDS);
    }
    
    // 2. Discrete points for dots (exact sampling times)
    waves.forEach(w => {
      if (w.enabled && w.isDotsMode) {
        const Ts = 1 / w.samplingRate;
        const totalSamples = Math.floor(DURATION_SECONDS * w.samplingRate);
        for (let n = 0; n <= totalSamples; n++) {
          const t = n * Ts;
          if (t <= DURATION_SECONDS) {
            allX.add(Number(t.toFixed(8))); // Prevent floating point jitter
          }
        }
      }
    });

    const sortedX = Array.from(allX).sort((a, b) => a - b);

    return sortedX.map(x => {
      const point: any = { x };
      waves.forEach((w, idx) => {
        if (w.enabled) {
          if (w.isDotsMode) {
            const Ts = 1 / w.samplingRate;
            const res = x / Ts;
            // Precision check: is this x exactly a sample point?
            if (Math.abs(res - Math.round(res)) < 1e-7) {
              point[`ch${idx}`] = w.amplitude * Math.sin(2 * Math.PI * w.frequency * x + w.phase);
            }
          } else {
            point[`ch${idx}`] = w.amplitude * Math.sin(2 * Math.PI * w.frequency * x + w.phase);
          }
        }
      });
      return point;
    });
  }, [waves]);

  const compositeData = useMemo(() => {
    const points: { x: number; y: number }[] = [];
    for (let i = 0; i <= RESOLUTION; i++) {
      const x = (i / RESOLUTION) * DURATION_SECONDS;
      let y = 0;
      waves.forEach(w => {
        if (w.enabled) {
          // For the summation, we always treat the signal as continuous/reconstructed
          // to show the "theoretical" resulting wave.
          y += w.amplitude * Math.sin(2 * Math.PI * w.frequency * x + w.phase);
        }
      });
      points.push({ x, y });
    }
    return points;
  }, [waves]);

  return (
    <div className="h-screen flex flex-col bg-slate-50 font-sans text-slate-800">

      {/* Header Bar */}
      <header className="h-16 shrink-0 px-8 flex items-center justify-between bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-indigo-600 rounded flex items-center justify-center shadow-lg shadow-indigo-100">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900">Fourier Synthesis</h1>
        </div>
        <div className="flex items-center gap-4">
          <button 
            onClick={resetAll}
            className="flex items-center gap-2 group text-[10px] font-bold uppercase tracking-widest text-slate-500 hover:text-indigo-600 transition-colors bg-slate-50 py-2 px-4 rounded-full border border-slate-200"
          >
            <RotateCcw size={14} className="group-hover:rotate-[-45deg] transition-transform" />
            Reset Signal
          </button>
        </div>
      </header>

      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        {/* Sidebar Controls */}
        <aside className="w-full lg:w-80 bg-white border-r border-slate-200 overflow-y-auto p-6 space-y-8 shadow-inner">
          <div>
            <h2 className="text-[11px] font-black uppercase tracking-[0.2em] text-slate-400 mb-6 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full"></div>
                Signal Configuration
              </div>
              <Settings2 size={14} className="text-slate-300" />
            </h2>
            
            <div className="space-y-6">
              {waves.map((wave, index) => (
                <div key={index} className={`p-4 rounded-xl border transition-all ${wave.enabled ? 'bg-indigo-50/30 border-indigo-100' : 'bg-slate-50 opacity-60 border-slate-100'}`}>
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                       <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: colors[index] }}></div>
                       <span className="text-xs font-bold text-slate-700 uppercase tracking-tight">{WAVE_NAMES[index]}</span>
                    </div>
                    <button
                      onClick={() => updateWave(index, { enabled: !wave.enabled })}
                      className={`w-10 h-5 rounded-full transition-colors relative flex items-center px-1 ${wave.enabled ? 'bg-indigo-500' : 'bg-slate-300'}`}
                    >
                      <motion.div
                        animate={{ x: wave.enabled ? 20 : 0 }}
                        className="w-3 h-3 bg-white rounded-full shadow-md"
                        transition={{ type: "spring", stiffness: 500, damping: 30 }}
                      />
                    </button>
                  </div>
                  
                  {wave.enabled && (
                    <div className="space-y-4 group">
                      <ControlSlider 
                        label="Frequency (Hz)" 
                        icon={TrendingUp}
                        value={wave.frequency} 
                        min={0.1} 
                        max={5} 
                        step={0.01} 
                        onChange={(val) => updateWave(index, { frequency: val })} 
                      />
                      <ControlSlider 
                        label="Amplitude" 
                        icon={Zap}
                        value={wave.amplitude} 
                        min={0} 
                        max={100} 
                        step={1} 
                        onChange={(val) => updateWave(index, { amplitude: val })} 
                      />
                      <ControlSlider 
                        label="Phase shift" 
                        icon={MoveHorizontal}
                        value={wave.phase} 
                        min={0} 
                        max={Math.PI * 2} 
                        step={0.01} 
                        onChange={(val) => updateWave(index, { phase: val })} 
                      />
                      <div className="pt-2 border-t border-indigo-100/30">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-1.5">
                            <Activity size={10} className="text-slate-400" />
                            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Visual Mode</span>
                          </div>
                          <button
                            onClick={() => updateWave(index, { isDotsMode: !wave.isDotsMode })}
                            className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full border transition-all text-[9px] font-bold uppercase tracking-tighter ${
                              wave.isDotsMode 
                                ? 'bg-indigo-600 border-indigo-500 text-white shadow-sm' 
                                : 'bg-white border-slate-200 text-slate-500'
                            }`}
                          >
                            {wave.isDotsMode ? 'Dots' : 'Line'}
                          </button>
                        </div>
                        {wave.isDotsMode && (
                          <>
                            <ControlSlider 
                              label="Sampling rate (Hz)" 
                              icon={Waves}
                              value={wave.samplingRate} 
                              min={1} 
                              max={50} 
                              step={1} 
                              onChange={(val) => updateWave(index, { samplingRate: val })} 
                            />
                            <div className="mt-4 px-1">
                              <div className="flex items-center justify-between mb-2">
                                <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">Discrete Vector y[n]</span>
                                <span className="text-[8px] font-mono text-slate-400">n = 0...{Math.floor(DURATION_SECONDS * wave.samplingRate)}</span>
                              </div>
                              <div className="h-24 bg-slate-900 rounded-lg p-3 font-mono text-[10px] text-indigo-300 overflow-y-auto border border-slate-800 shadow-inner custom-scrollbar relative">
                                <div className="leading-relaxed break-all">
                                  <span className="text-slate-500 font-bold">[</span>
                                  {Array.from({ length: Math.floor(DURATION_SECONDS * wave.samplingRate) + 1 }).map((_, i) => {
                                    const t = i / wave.samplingRate;
                                    if (t > DURATION_SECONDS) return null;
                                    const val = wave.amplitude * Math.sin(2 * Math.PI * wave.frequency * t + wave.phase);
                                    return (
                                      <span key={i}>
                                        <span 
                                          className="text-emerald-400 hover:text-white transition-colors cursor-default" 
                                          title={`n=${i}, t=${t.toFixed(2)}s`}
                                        >
                                          {val.toFixed(1)}
                                        </span>
                                        {i < Math.floor(DURATION_SECONDS * wave.samplingRate) && <span className="text-slate-600">, </span>}
                                      </span>
                                    );
                                  })}
                                  <span className="text-slate-500 font-bold">]</span>
                                </div>
                              </div>
                            </div>
                          </>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </aside>

        {/* Display Area */}
        <main className="flex-1 overflow-y-auto p-4 md:p-8">
          <div className="max-w-5xl mx-auto space-y-8">
            <Reorder.Group axis="y" values={graphOrder} onReorder={setGraphOrder} className="space-y-8">
              {graphOrder.map((id) => (
                <ReorderItemComponent key={id} value={id} isDark={id === 'sum'}>
                  {id === 'mixed' ? (
                    <motion.section 
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden h-[340px] flex flex-col"
                    >
                      <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
                        <div className="flex items-center gap-3">
                          <div className="w-1.5 h-4 bg-slate-300 rounded-full"></div>
                          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-800">Channel Overlay (Mixed)</h3>
                        </div>
                        <div className="flex gap-4">
                           {waves.map((w, i) => w.enabled && (
                             <div key={i} className="flex items-center gap-1.5">
                                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: colors[i] }}></div>
                                <span className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">CH{i+1}</span>
                             </div>
                           ))}
                        </div>
                      </div>
                      <div className="flex-1 relative bg-[radial-gradient(#e2e8f0_1px,transparent_1px)] [background-size:20px_20px] p-6">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={overlayData} margin={{ top: 10, right: 10, left: 10, bottom: 10 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                            <ReferenceLine y={0} stroke="#cbd5e1" strokeWidth={1} />
                            <XAxis 
                              dataKey="x" 
                              type="number"
                              domain={[0, DURATION_SECONDS]}
                              axisLine={{ stroke: '#e2e8f0', strokeWidth: 1 }} 
                              ticks={[0, 2, 4, 6, 8, 10]}
                              tick={{ fontSize: 9, fill: '#94a3b8' }}
                              label={{ value: 'Time (s)', position: 'insideBottomRight', offset: -5, fontSize: 10, fill: '#64748b', fontWeight: 'bold' }}
                            />
                            <YAxis 
                              domain={[-100, 100]} 
                              axisLine={{ stroke: '#e2e8f0', strokeWidth: 1 }} 
                              tick={{ fontSize: 9, fill: '#94a3b8' }}
                              width={25}
                            />
                            <Tooltip 
                               contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', fontSize: '10px' }}
                            />
                            {waves.map((w, i) => w.enabled && (
                               <Line 
                                 key={i}
                                 type="monotone" 
                                 dataKey={`ch${i}`} 
                                 stroke={colors[i]} 
                                 strokeWidth={w.isDotsMode ? 0 : 2} 
                                 dot={w.isDotsMode ? { r: 3, fill: colors[i], strokeWidth: 0 } : false}
                                 isAnimationActive={false}
                                 connectNulls={false}
                               />
                            ))}
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    </motion.section>
                  ) : (
                    <motion.section 
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="bg-slate-900 rounded-2xl border border-slate-800 shadow-2xl overflow-hidden h-[340px] flex flex-col"
                    >
                      <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-900/50 backdrop-blur-md">
                        <div className="flex items-center gap-3">
                          <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 shadow-[0_0_8px_rgba(99,102,241,0.6)]"></div>
                          <h3 className="text-sm font-bold uppercase tracking-wider text-white">Additive Summation</h3>
                        </div>
                        <span className="text-[9px] font-mono text-slate-500 tracking-widest leading-none">∑ sin(2πft + φ)</span>
                      </div>
                      <div className="flex-1 relative bg-slate-950 p-6">
                        <div className="absolute inset-0 grid grid-cols-12 opacity-[0.03] pointer-events-none">
                           {[...Array(13)].map((_, i) => <div key={i} className="border-r border-white h-full"></div>)}
                        </div>
                        <ResponsiveContainer width="100%" height="100%">
                           <LineChart data={compositeData} margin={{ top: 10, right: 10, left: 10, bottom: 10 }}>
                              <CartesianGrid strokeDasharray="4 4" stroke="#1e293b" />
                              <ReferenceLine y={0} stroke="#334155" strokeWidth={1} />
                              <XAxis 
                                dataKey="x" 
                                type="number"
                                domain={[0, DURATION_SECONDS]}
                                axisLine={{ stroke: '#334155', strokeWidth: 1 }} 
                                ticks={[0, 2, 4, 6, 8, 10]}
                                tick={{ fontSize: 9, fill: '#475569' }}
                                label={{ value: 'Time (s)', position: 'insideBottomRight', offset: -5, fontSize: 10, fill: '#94a3b8', fontWeight: 'bold' }}
                              />
                              <YAxis 
                                domain={[-150, 150]} 
                                axisLine={{ stroke: '#334155', strokeWidth: 1 }} 
                                tick={{ fontSize: 9, fill: '#475569' }}
                                width={30}
                              />
                              <Line 
                                type="monotone" 
                                dataKey="y" 
                                stroke="#818cf8" 
                                strokeWidth={4} 
                                dot={false}
                                isAnimationActive={false}
                                className="drop-shadow-[0_0_12px_rgba(129,140,248,0.8)]"
                              />
                           </LineChart>
                        </ResponsiveContainer>
                      </div>
                    </motion.section>
                  )}
                </ReorderItemComponent>
              ))}
            </Reorder.Group>
          </div>
        </main>
      </div>

      {/* Bottom Status Bar */}
      <footer className="h-10 shrink-0 bg-white border-t border-slate-200 flex items-center px-8 justify-between z-50">
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
          <span className="text-[9px] font-mono text-slate-400 tracking-widest uppercase">Kernel Protocol Loaded // Ready</span>
        </div>
        <div className="text-[9px] font-mono text-slate-300 tracking-widest uppercase">
          Synthesizer V.05
        </div>
      </footer>
    </div>
  );
}
