import { useEffect, useState } from 'react';
import { IconArrowLeft, IconTrash, IconCalendar } from './Icons';
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
            <div className="flex flex-col h-screen bg-[#F7F7F7] overflow-hidden relative font-sans text-[#333333]">
                <div className="p-6 z-10 flex items-center gap-4 border-b border-[#E0E0E0] bg-[#F7F7F7] shadow-[0_2px_4px_rgba(0,0,0,0.02)]">
                    <button onClick={() => setSelectedRun(null)} className="p-3 neu-btn hover:text-[#000000] text-[#555555]">
                        <IconArrowLeft size={20} />
                    </button>
                    <div>
                        <h2 className="font-bold text-lg text-[#333333]">Simulation Details</h2>
                        <p className="text-xs text-[#AAAAAA] font-mono">{new Date(selectedRun.timestamp).toLocaleString()}</p>
                    </div>
                    <div className="ml-auto flex gap-4">
                        <div className="flex flex-col items-end">
                            <span className="text-[10px] uppercase font-bold text-[#AAAAAA]">Success Rate</span>
                            <span className="font-bold text-2xl text-[#333333]">{Math.round(selectedRun.success_rate * 100)}%</span>
                        </div>
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto p-8 z-10 space-y-4 scrollbar-thin scrollbar-thumb-[#E0E0E0]">
                    {/* Results List */}
                    {selectedRun.results.map((r: any, i: number) => (
                        <ScenarioCard key={i} result={r} />
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-screen bg-[#F7F7F7] overflow-hidden relative font-sans text-[#333333] animate-fade-in-up">

            <div className="p-8 z-10 flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <button onClick={onBack} className="p-3 neu-btn text-[#555555]">
                        <IconArrowLeft size={20} />
                    </button>
                    <h1 className="text-2xl font-bold tracking-tight text-[#333333]">Run History</h1>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto px-8 pb-8 z-10 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 scrollbar-thin scrollbar-thumb-[#E0E0E0]">
                {history.length === 0 && (
                    <div className="col-span-full h-64 flex items-center justify-center text-[#AAAAAA] italic">
                        No history found. Run a simulation first!
                    </div>
                )}
                {history.map(run => (
                    <div
                        key={run.id}
                        onClick={() => setSelectedRun(run)}
                        className="neu-card p-6 cursor-pointer group relative overflow-hidden transition-all hover:scale-[1.01]"
                    >
                        <div className="flex justify-between items-start mb-6">
                            <div className="flex items-center gap-2 text-[#AAAAAA] text-xs font-bold uppercase tracking-wider">
                                {/* Status Dot moved to Header */}
                                <div className={`w-2.5 h-2.5 rounded-full ${run.success_rate >= (run.config.threshold || 0.8) ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.4)]' : 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.4)]'}`} />
                                <IconCalendar size={14} />
                                {new Date(run.timestamp).toLocaleDateString()}
                            </div>
                            <button
                                onClick={(e) => deleteRun(e, run.id)}
                                className="text-[#AAAAAA] hover:text-[#333333] transition-colors p-1"
                            >
                                <IconTrash size={16} />
                            </button>
                        </div>

                        <div className="mb-6 h-32 overflow-hidden relative">
                            <div className="text-sm font-bold text-[#333333] mb-2">
                                {run.config.model_name}
                            </div>
                            <div className="text-xs text-[#777777] leading-relaxed line-clamp-4">
                                {run.config.base_prompt}
                            </div>
                        </div>

                        <div className="flex items-center justify-between pt-4 border-t border-[#E0E0E0]">
                            <div>
                                <div className="text-[9px] uppercase font-bold text-[#AAAAAA] mb-0.5">Success</div>
                                <div className={`text-xl font-bold ${run.success_rate >= (run.config.threshold || 0.8) ? 'text-[#333333]' : 'text-[#777777]'}`}>
                                    {Math.round(run.success_rate * 100)}%
                                </div>
                            </div>
                            <div className="text-right">
                                <div className="text-[9px] uppercase font-bold text-[#AAAAAA]">Avg Score</div>
                                <div className="text-xl font-bold text-[#333333]">
                                    {Math.round((run.results?.reduce((acc: number, r: any) => acc + (r.score || 0), 0) || 0) / (run.results?.length || 1))}
                                </div>
                            </div>
                            <div className="text-right">
                                <div className="text-[9px] uppercase font-bold text-[#AAAAAA]">Cycles</div>
                                <div className="text-xl font-bold text-[#333333]">
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
