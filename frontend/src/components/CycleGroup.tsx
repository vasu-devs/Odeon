import { useState } from 'react';
import { ChevronDown, ChevronRight, Layers, PieChart } from 'lucide-react';
import ScenarioCard, { type ScenarioResult } from './ScenarioCard';

interface CycleGroupProps {
    cycle: number;
    results: ScenarioResult[];
    isLast: boolean;
}

export default function CycleGroup({ cycle, results, isLast }: CycleGroupProps) {
    const [isOpen, setIsOpen] = useState(true); // Default to open for now, or maybe only latest?

    const passCount = results.filter(r => r.passed).length;
    const passRate = results.length > 0 ? Math.round((passCount / results.length) * 100) : 0;
    const avgScore = results.length > 0 ? Math.round(results.reduce((a, b) => a + b.score, 0) / results.length) : 0;

    return (
        <div className="mb-4 last:mb-0">
            {/* Cycle Header */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="w-full flex items-center justify-between p-4 bg-white border border-zinc-200 rounded-xl shadow-sm hover:shadow-md transition-all group"
            >
                <div className="flex items-center gap-3">
                    <div className={`p-1.5 rounded-lg transition-colors ${isOpen ? 'bg-zinc-100 text-zinc-600' : 'bg-white text-zinc-400'}`}>
                        {isOpen ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
                    </div>
                    <div className="flex flex-col items-start">
                        <span className="font-bold text-lg text-zinc-800 flex items-center gap-2">
                            Cycle {cycle}
                            {isLast && <span className="text-[10px] bg-blue-100 text-blue-600 px-2 py-0.5 rounded-full uppercase tracking-wider font-bold">Latest</span>}
                        </span>
                        <span className="text-xs text-zinc-400 font-medium">
                            {results.length} Scenarios
                        </span>
                    </div>
                </div>

                <div className="flex items-center gap-6">
                    <div className="text-right">
                        <div className="text-[10px] uppercase font-bold text-zinc-400 flex items-center justify-end gap-1">
                            <PieChart size={12} /> Pass Rate
                        </div>
                        <div className={`font-bold text-lg ${passRate >= 80 ? 'text-green-600' : 'text-zinc-700'}`}>
                            {passRate}%
                        </div>
                    </div>
                    <div className="text-right border-l border-zinc-100 pl-6">
                        <div className="text-[10px] uppercase font-bold text-zinc-400 flex items-center justify-end gap-1">
                            <Layers size={12} /> Avg Score
                        </div>
                        <div className="font-bold text-lg text-zinc-700">
                            {avgScore}
                        </div>
                    </div>
                </div>
            </button>

            {/* Cycle Content (Grid of Cards) */}
            {isOpen && (
                <div className="grid grid-cols-1 gap-3 mt-3 pl-2 border-l-2 border-zinc-100 ml-4 animate-fade-in-up">
                    {results.map((result, idx) => (
                        <div key={idx}>
                            <ScenarioCard result={result} />
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
