import { useState, useRef } from 'react';
import Sidebar, { type Config } from './Sidebar';
import LogTerminal from './LogTerminal';
import { type ScenarioResult } from './ScenarioCard';
import CycleGroup from './CycleGroup';
import DiffViewer from './DiffViewer';
import HistoryView from './HistoryView';
import { IconLayers, IconClock, IconActivity, IconGraph, IconCheck } from './Icons';

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
        base_prompt: `CRITICAL OUTPUT RULES:
1. OUTPUT ONLY THE SPOKEN WORDS.
2. DO NOT use headers like "Turn 1:", "Plan B:", or "**Response:**".
3. DO NOT write post-call analysis or evaluations.
4. If you output a header, the system will CRASH.
<strict_constraints>
1. YOU ARE DUMB. Do not be helpful beyond your specific instructions.
2. Do NOT hallucinate legal details, PO Boxes, or websites.
3. Your goal is to follow the user's prompt EXACTLY.
</strict_constraints>

<user_instructions>
  You are 'Rachel', a senior Debt Collector Agent for The Agency.
  Your goal is to collect the $500 debt while being highly empathetic.
  
  **FEE AND INTEREST POLICY (CRITICAL):**
  - The authorized payment plans are **INTEREST-FREE**.
  - The total repayment amount for all plans is exactly **$500** (Principal Only).
  - There are NO additional fees or late charges added by The Agency for these specific plans.
  
  **AUTHORIZED PLANS (Offer immediately if user mentions hardship):**
    1. $50/month for 10 months (Total: $500)
    2. $100/month for 5 months (Total: $500)
    3. $200/month for 2.5 months (Total: $500)
  
  **NEGOTIATION FLOW:**
  1. **EMPATHIZE FIRST:** Validate the customer's hardship (e.g., job loss) before asking for money.
  2. **FEES RESPONSE:** If the user asks about fees/interest, state clearly: "These plans are interest-free, the total amount is exactly $500."
  3. **DENIAL:** If the user proposes a payment **less than $50** (e.g., $25/mo), firmly but politely state: "I cannot authorize a payment below $50 per month, as that is the minimum authorized." Then steer them back to choosing from the authorized list.
</user_instructions>`,
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
        <div className="flex bg-[#F7F7F7] h-screen text-[#333333] font-sans overflow-hidden relative selection:bg-[#E0E0E0]">
            <Sidebar
                config={config}
                setConfig={setConfig}
                onStart={startSimulation}
                onStop={stopSimulation}
                isRunning={isRunning}
            />

            {/* Main Content */}
            <main className="flex-1 flex flex-col h-[100dvh] relative overflow-hidden pl-2">

                {/* Top Bar / Stats */}
                <div className="p-8 pb-4 shrink-0 grid grid-cols-4 gap-6">
                    <div className="neu-card p-6 flex flex-col justify-between h-[120px] relative overflow-hidden group">
                        <div className="flex justify-between items-start z-10">
                            <div>
                                <p className="text-[10px] text-[#AAAAAA] font-bold uppercase tracking-widest mb-1">Total Runs</p>
                                <p className="text-3xl font-bold tracking-tight text-[#333333]">{results.length}</p>
                            </div>
                            <div className="p-2 rounded-lg bg-[#F7F7F7] shadow-[inset_2px_2px_5px_#bebebe,inset_-2px_-2px_5px_#ffffff]">
                                <IconLayers size={18} className="text-[#333333]" />
                            </div>
                        </div>
                        <div className="absolute -bottom-4 -right-4 opacity-[0.03] scale-150 rotate-[-15deg] transition-transform duration-500 group-hover:scale-[1.8] group-hover:rotate-0 text-[#333333]">
                            <IconLayers size={100} />
                        </div>
                    </div>

                    <div className="neu-card p-6 flex flex-col justify-between h-[120px] relative overflow-hidden group">
                        <div className="flex justify-between items-start z-10">
                            <div>
                                <p className="text-[10px] text-[#AAAAAA] font-bold uppercase tracking-widest mb-1">Current Cycle</p>
                                <p className="text-3xl font-bold tracking-tight text-[#333333]">{cycleAvg}</p>
                            </div>
                            <div className="p-2 rounded-lg bg-[#F7F7F7] shadow-[inset_2px_2px_5px_#bebebe,inset_-2px_-2px_5px_#ffffff]">
                                <IconClock size={18} className="text-[#333333]" />
                            </div>
                        </div>
                        <div className="absolute -bottom-2 -right-2 opacity-[0.03] scale-150 transition-transform duration-500 group-hover:scale-[1.8] group-hover:rotate-[20deg] text-[#333333]">
                            <IconClock size={100} />
                        </div>
                    </div>

                    <div className="neu-card p-6 flex flex-col justify-between h-[120px] relative overflow-hidden group cursor-pointer hover:translate-y-[-2px] transition-transform" onClick={() => setViewMode('history')}>
                        <div className="flex justify-between items-start z-10">
                            <div>
                                <p className="text-[10px] text-[#AAAAAA] font-bold uppercase tracking-widest mb-1">History</p>
                                <p className="text-lg font-bold tracking-tight text-[#333333] mt-1 flex items-center gap-2">
                                    View Archives <IconGraph size={14} />
                                </p>
                            </div>
                            <div className="p-2 rounded-lg bg-[#333333] text-white shadow-lg group-hover:bg-black transition-colors">
                                <IconLayers size={18} />
                            </div>
                        </div>
                        <div className="absolute -bottom-4 -right-4 opacity-[0.03] scale-150 rotate-[10deg] transition-transform duration-500 group-hover:scale-[1.8] group-hover:rotate-[-5deg] text-[#333333]">
                            <IconGraph size={100} />
                        </div>
                    </div>

                    <div className="neu-card p-6 flex items-center justify-between h-[120px] relative overflow-hidden group">
                        <div className="z-10">
                            <p className="text-[10px] text-[#AAAAAA] font-bold uppercase tracking-widest mb-2">Pass Rate</p>
                            <div className="flex items-baseline gap-1">
                                <p className="text-4xl font-bold tracking-tight text-[#333333]">
                                    {passRate.toFixed(1)}
                                </p>
                                <span className="text-sm font-medium text-[#AAAAAA]">%</span>
                            </div>
                        </div>

                        {/* Simple visual ring representation */}
                        <div className="relative w-16 h-16 flex items-center justify-center z-10">
                            <svg className="w-full h-full transform -rotate-90">
                                <circle
                                    cx="32"
                                    cy="32"
                                    r="28"
                                    stroke="#E0E0E0"
                                    strokeWidth="4"
                                    fill="none"
                                />
                                <circle
                                    cx="32"
                                    cy="32"
                                    r="28"
                                    stroke="#333333"
                                    strokeWidth="4"
                                    fill="none"
                                    strokeDasharray={176}
                                    strokeDashoffset={176 - (176 * passRate) / 100}
                                    strokeLinecap="round"
                                />
                            </svg>
                            <IconCheck size={16} className="absolute text-[#333333]" />
                        </div>

                        <div className="absolute -left-4 -bottom-4 opacity-[0.03] scale-150 rotate-[-10deg] transition-transform duration-500 group-hover:scale-[1.8] group-hover:rotate-[5deg] text-[#333333]">
                            <IconActivity size={100} />
                        </div>
                    </div>
                </div>

                {/* Content Area */}
                <div className="flex-1 p-8 pt-2 grid grid-cols-12 gap-8 min-h-0 overflow-hidden pb-8">

                    {/* Left: Simulation Feed */}
                    <div className="col-span-8 flex flex-col h-full min-h-0">
                        {/* Header for feed */}
                        <div className="mb-4 flex items-center gap-2 px-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-[#333333]"></div>
                            <span className="text-xs font-bold uppercase tracking-widest text-[#AAAAAA]">Live Results Stream</span>
                        </div>

                        <div className="flex-1 overflow-y-auto pr-4 scrollbar-none pb-4">
                            {results.length === 0 && !isRunning && (
                                <div className="h-full flex flex-col items-center justify-center text-[#AAAAAA] opacity-40">
                                    <IconActivity size={48} className="mb-4" />
                                    <p className="font-medium tracking-wide uppercase text-xs">Ready to Simulate</p>
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
                    <div className="col-span-4 flex flex-col gap-6 h-full min-h-0">
                        <div className={`${optimizationHistory.length > 0 ? 'flex-[2]' : 'flex-1'} min-h-0 flex flex-col transition-all duration-500`}>
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
