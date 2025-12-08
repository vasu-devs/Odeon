import { useState, useRef } from 'react';
import Sidebar, { type Config } from './Sidebar';
import LogTerminal from './LogTerminal';
import { type ScenarioResult } from './ScenarioCard';
import CycleGroup from './CycleGroup';
import DiffViewer from './DiffViewer';
import HistoryView from './HistoryView';
import { Activity, Layers, Clock } from 'lucide-react';
import { GridPattern, MeshGradient } from './Backgrounds';

interface OptimizationEntry {
    cycle: number;
    old_prompt: string;
    new_prompt: string;
    reasoning: string;
}

export default function Dashboard() {
    const [viewMode, setViewMode] = useState<'dashboard' | 'history'>('dashboard');
    const [config, setConfig] = useState<Config>({
        api_key: '',
        model_name: 'llama-3.1-8b-instant',
        base_prompt: `You are a Debt Collector Agent named Rachel.
Your goal is to collect a $500 debt.
Be professional but firm.`,
        max_cycles: 5,
        batch_size: 5,
        thresholds: {
            repetition: 8,
            negotiation: 8,
            empathy: 8,
            overall: 8
        }
    });

    const [logs, setLogs] = useState<string[]>([]);
    const [results, setResults] = useState<ScenarioResult[]>([]);
    const [optimizationHistory, setOptimizationHistory] = useState<OptimizationEntry[]>([]);
    const [isRunning, setIsRunning] = useState(false);
    const wsRef = useRef<WebSocket | null>(null);

    // Stats
    const passRate = results.length > 0
        ? (results.filter(r => r.passed).length / results.length) * 100
        : 0;
    const cycleAvg = results.length > 0 ? results[results.length - 1].cycle : 0;

    const stopSimulation = () => {
        if (wsRef.current) {
            wsRef.current.close();
            setLogs(prev => [...prev, "Simulation Stopped by User."]);
            setIsRunning(false);
            wsRef.current = null;
        }
    };

    const startSimulation = () => {
        // Close existing if any
        if (wsRef.current) {
            wsRef.current.close();
        }

        setIsRunning(true);
        setLogs([]);
        setResults([]);
        setOptimizationHistory([]);

        const ws = new WebSocket('ws://localhost:8000/ws/simulate');
        wsRef.current = ws;

        ws.onopen = () => {
            ws.send(JSON.stringify(config));
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.type === 'log') {
                setLogs(prev => [...prev, data.message]);
                if (data.message.includes("Optimization Complete")) {
                    setIsRunning(false);
                    wsRef.current = null;
                }
            } else if (data.type === 'result') {
                setResults(prev => [...prev, {
                    cycle: data.cycle,
                    persona: data.persona,
                    score: data.score,
                    metrics: data.metrics,
                    transcript: data.transcript,
                    feedback: data.feedback,
                    passed: data.passed,
                    updated_prompt: data.updated_prompt
                }]);
            } else if (data.type === 'optimization') {
                setOptimizationHistory(prev => [...prev, {
                    cycle: data.cycle,
                    old_prompt: data.old_prompt,
                    new_prompt: data.new_prompt,
                    reasoning: data.reasoning
                }]);
            } else if (data.type === 'error') {
                setLogs(prev => [...prev, `ERROR: ${data.message}`]);
                setIsRunning(false);
                ws.close();
                wsRef.current = null;
            }
        };

        ws.onclose = () => {
            setIsRunning(false);
            wsRef.current = null;
        };
    };

    if (viewMode === 'history') {
        return <HistoryView onBack={() => setViewMode('dashboard')} />;
    }

    return (
        <div className="flex bg-zinc-50 min-h-screen text-zinc-900 font-sans selection:bg-blue-500/20 overflow-hidden relative">
            <Sidebar
                config={config}
                setConfig={setConfig}
                onStart={startSimulation}
                onStop={stopSimulation}
                isRunning={isRunning}
                onHistory={() => setViewMode('history')}
            />

            {/* Main Content */}
            <main className="flex-1 flex flex-col h-[100dvh] relative overflow-hidden">
                <GridPattern />
                <MeshGradient />

                {/* Top Bar / Stats */}
                <div className="p-6 shrink-0 z-10 grid grid-cols-4 gap-4 pb-2">
                    <div className="bg-white/50 backdrop-blur-md p-4 rounded-2xl border border-zinc-200/50 shadow-sm flex items-center gap-4">
                        <div className="p-3 bg-zinc-900 text-white rounded-xl">
                            <Layers size={20} />
                        </div>
                        <div>
                            <p className="text-xs text-zinc-500 font-bold uppercase tracking-wider">Total Runs</p>
                            <p className="text-2xl font-bold">{results.length}</p>
                        </div>
                    </div>

                    <div className="bg-white/50 backdrop-blur-md p-4 rounded-2xl border border-zinc-200/50 shadow-sm flex items-center gap-4">
                        <div className="p-3 bg-zinc-900 text-white rounded-xl">
                            <Clock size={20} />
                        </div>
                        <div>
                            <p className="text-xs text-zinc-500 font-bold uppercase tracking-wider">Current Cycle</p>
                            <p className="text-2xl font-bold">{cycleAvg}</p>
                        </div>
                    </div>

                    <div className="bg-white/50 backdrop-blur-md p-4 rounded-2xl border border-zinc-200/50 shadow-sm flex items-center gap-4">
                        <div className="p-3 bg-zinc-900 text-white rounded-xl">
                            <Activity size={20} />
                        </div>
                        <div>
                            <p className="text-xs text-zinc-500 font-bold uppercase tracking-wider">Pass Rate</p>
                            <p className={`text-2xl font-bold ${passRate > 80 ? 'text-green-600' : 'text-zinc-900'}`}>
                                {passRate.toFixed(1)}%
                            </p>
                        </div>
                    </div>

                    {/* Placeholder for future Stat */}
                </div>

                {/* Content Area - Uses min-h-0 to prevent overflow logic issues */}
                <div className="flex-1 p-6 pt-2 grid grid-cols-12 gap-6 min-h-0 overflow-hidden z-10">

                    {/* Left: Simulation Feed */}
                    <div className="col-span-8 flex flex-col h-full min-h-0">
                        <div className="flex-1 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-zinc-300 scrollbar-track-transparent pb-4">
                            {results.length === 0 && !isRunning && (
                                <div className="h-full flex flex-col items-center justify-center text-zinc-400 opacity-50">
                                    <Layers size={48} className="mb-4 text-zinc-300" />
                                    <p className="font-medium">Ready to Simulate</p>
                                </div>
                            )}

                            {Array.from(new Set(results.map(r => r.cycle))).map((cycle) => {
                                const cycleResults = results.filter(r => r.cycle === cycle);
                                const isLast = cycle === results[results.length - 1]?.cycle;
                                return (
                                    <CycleGroup
                                        key={cycle}
                                        cycle={cycle}
                                        results={cycleResults}
                                        isLast={isLast}
                                    />
                                );
                            })}
                        </div>
                    </div>

                    {/* Right: Terminal & Diff */}
                    <div className="col-span-4 flex flex-col gap-4 h-full min-h-0 pb-4">
                        <div className={`${optimizationHistory.length > 0 ? 'flex-[2]' : 'flex-1'} min-h-0 bg-zinc-900 rounded-2xl shadow-lg border border-zinc-800 overflow-hidden flex flex-col transition-all duration-500`}>
                            <div className="bg-zinc-800/50 px-4 py-2 text-xs font-mono text-zinc-400 border-b border-zinc-800 flex items-center gap-2 shrink-0">
                                <div className="w-2 h-2 rounded-full bg-red-500" />
                                <div className="w-2 h-2 rounded-full bg-yellow-500" />
                                <div className="w-2 h-2 rounded-full bg-green-500" />
                                <span className="ml-2">Real-time Logs</span>
                            </div>
                            <LogTerminal logs={logs} />
                        </div>

                        {optimizationHistory.length > 0 && (
                            <div className="flex-1 min-h-0 animate-fade-in-up">
                                <DiffViewer history={optimizationHistory} />
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
}
