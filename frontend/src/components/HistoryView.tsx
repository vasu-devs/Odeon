import { useEffect, useState } from 'react';
import { ArrowLeft, Trash2, Calendar } from 'lucide-react';
import { GridPattern, MeshGradient } from './Backgrounds';
import ScenarioCard from './ScenarioCard';

interface HistoryItem {
    id: string;
    timestamp: string;
    config: any;
    success_rate: number;
    total_cycles: number;
    results: any[];
}

export default function HistoryView({ onBack }: { onBack: () => void }) {
    const [history, setHistory] = useState<HistoryItem[]>([]);
    const [selectedRun, setSelectedRun] = useState<HistoryItem | null>(null);

    useEffect(() => {
        fetch('http://localhost:8000/history')
            .then(res => res.json())
            .then(data => setHistory(data))
            .catch(err => console.error(err));
    }, []);

    const deleteRun = (e: React.MouseEvent, id: string) => {
        e.stopPropagation();
        fetch(`http://localhost:8000/history/${id}`, { method: 'DELETE' })
            .then(() => setHistory(prev => prev.filter(h => h.id !== id)));
    };

    if (selectedRun) {
        return (
            <div className="flex flex-col h-screen bg-zinc-50 overflow-hidden relative font-sans text-zinc-900">
                <GridPattern />
                <MeshGradient />

                <div className="p-6 z-10 flex items-center gap-4 border-b border-zinc-200/50 bg-white/50 backdrop-blur-sm">
                    <button onClick={() => setSelectedRun(null)} className="p-2 hover:bg-zinc-100 rounded-lg transition-colors">
                        <ArrowLeft size={20} />
                    </button>
                    <div>
                        <h2 className="font-bold text-lg">Simulation Details</h2>
                        <p className="text-xs text-zinc-500 font-mono">{new Date(selectedRun.timestamp).toLocaleString()}</p>
                    </div>
                    <div className="ml-auto flex gap-4">
                        <div className="flex flex-col items-end">
                            <span className="text-[10px] uppercase font-bold text-zinc-400">Success Rate</span>
                            <span className="font-bold text-xl">{Math.round(selectedRun.success_rate * 100)}%</span>
                        </div>
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto p-8 z-10 space-y-4">
                    {/* Results List */}
                    {selectedRun.results.map((r: any, i: number) => (
                        <ScenarioCard key={i} result={r} />
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-screen bg-zinc-50 overflow-hidden relative font-sans text-zinc-900 animate-fade-in-up">
            <GridPattern />

            <div className="p-8 z-10 flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <button onClick={onBack} className="p-2 hover:bg-zinc-200 rounded-full transition-colors bg-white border border-zinc-200 shadow-sm">
                        <ArrowLeft size={20} />
                    </button>
                    <h1 className="text-2xl font-bold tracking-tight">Run History</h1>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto px-8 pb-8 z-10 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {history.length === 0 && (
                    <div className="col-span-full h-64 flex items-center justify-center text-zinc-400 italic">
                        No history found. Run a simulation first!
                    </div>
                )}
                {history.map(run => (
                    <div
                        key={run.id}
                        onClick={() => setSelectedRun(run)}
                        className="bg-white rounded-2xl p-5 border border-zinc-200 shadow-sm hover:shadow-md transition-all cursor-pointer group relative overflow-hidden"
                    >
                        <div className="flex justify-between items-start mb-4">
                            <div className="flex items-center gap-2 text-zinc-400 text-xs font-medium">
                                <Calendar size={14} />
                                {new Date(run.timestamp).toLocaleDateString()}
                            </div>
                            <button
                                onClick={(e) => deleteRun(e, run.id)}
                                className="text-zinc-300 hover:text-red-500 transition-colors p-1"
                            >
                                <Trash2 size={16} />
                            </button>
                        </div>

                        <div className="mb-4">
                            <div className="text-sm font-semibold text-zinc-900 mb-1">
                                {run.config.model_name}
                            </div>
                            <div className="text-xs text-zinc-500 line-clamp-2">
                                {run.config.base_prompt}
                            </div>
                        </div>

                        <div className="flex items-center gap-4 pt-4 border-t border-zinc-100">
                            <div>
                                <div className="text-[10px] uppercase font-bold text-zinc-400">Success</div>
                                <div className={`text-lg font-bold ${run.success_rate >= (run.config.threshold || 0.8) ? 'text-green-600' : 'text-zinc-900'}`}>
                                    {Math.round(run.success_rate * 100)}%
                                </div>
                            </div>
                            <div>
                                <div className="text-[10px] uppercase font-bold text-zinc-400">Cycles</div>
                                <div className="text-lg font-bold text-zinc-900">
                                    {run.total_cycles}
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
