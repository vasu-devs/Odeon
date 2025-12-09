import { useState } from 'react';
import { IconChevronDown, IconChevronRight, IconLayers, IconPieChart } from './Icons';
import ScenarioCard, { type ScenarioResult } from './ScenarioCard';

interface CycleGroupProps {
    cycle: number;
    results: ScenarioResult[];
    isLast: boolean;
}

export default function CycleGroup({ cycle, results, isLast }: CycleGroupProps) {
    const [isOpen, setIsOpen] = useState(true);

    const passCount = results.filter(r => r.passed).length;
    const passRate = results.length > 0 ? Math.round((passCount / results.length) * 100) : 0;
    const avgScore = results.length > 0 ? Math.round(results.reduce((a, b) => a + b.score, 0) / results.length) : 0;

    return (
        <div className="mb-6 last:mb-0">
            {/* Cycle Header */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="w-full flex items-center justify-between p-5 neu-card transition-all group hover:scale-[1.01]"
            >
                <div className="flex items-center gap-4">
                    <div className={`p-2 rounded-full transition-colors ${isOpen ? 'bg-[#333333] text-white' : 'bg-[#E0E0E0] text-[#555555]'}`}>
                        {isOpen ? <IconChevronDown size={14} /> : <IconChevronRight size={14} />}
                    </div>
                    <div className="flex flex-col items-start gap-1">
                        <span className="font-bold text-lg text-[#333333] flex items-center gap-3">
                            Cycle {cycle}
                            {isLast && <span className="text-[10px] bg-black text-white px-2 py-0.5 rounded-full uppercase tracking-wider font-bold shadow-md">Latest</span>}
                        </span>
                        <span className="text-xs text-[#AAAAAA] font-bold uppercase tracking-widest">
                            {results.length} Scenarios
                        </span>
                    </div>
                </div>

                <div className="flex items-center gap-8 mr-2">
                    <div className="text-right">
                        <div className="text-[10px] uppercase font-bold text-[#AAAAAA] flex items-center justify-end gap-1 mb-1">
                            <IconPieChart size={12} /> Pass Rate
                        </div>
                        <div className={`font-bold text-xl ${passRate >= 80 ? 'text-[#333333]' : 'text-[#777777]'}`}>
                            {passRate}%
                        </div>
                    </div>
                    <div className="text-right border-l border-[#E0E0E0] pl-8">
                        <div className="text-[10px] uppercase font-bold text-[#AAAAAA] flex items-center justify-end gap-1 mb-1">
                            <IconLayers size={12} /> Avg Score
                        </div>
                        <div className="font-bold text-xl text-[#333333]">
                            {avgScore}
                        </div>
                    </div>
                </div>
            </button>

            {/* Cycle Content (Grid of Cards) */}
            {isOpen && (
                <div className="grid grid-cols-1 gap-4 mt-4 pl-4 border-l-2 border-[#E0E0E0] ml-6 animate-fade-in-up">
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
