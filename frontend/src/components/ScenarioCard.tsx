import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { IconChevronDown, IconClose } from './Icons';

export interface ScenarioResult {
    cycle: number;
    persona: {
        name: string;
        personality_traits: string;
        financial_situation: string;
    } | undefined;
    score: number;
    metrics?: {
        repetition: number;
        negotiation: number;
        empathy: number;
        overall: number;
    };
    transcript: string | { role: string; content: string }[];
    feedback: string;
    passed: boolean;
    updated_prompt?: string;
}

export default function ScenarioCard({ result }: { result: ScenarioResult }) {
    const [isExpanded, setIsExpanded] = useState(false);

    // Lock body scroll when modal is open
    useEffect(() => {
        if (isExpanded) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'unset';
        }
        return () => {
            document.body.style.overflow = 'unset';
        };
    }, [isExpanded]);

    // Defines safe accessors
    const personaName = result.persona?.name || 'Unknown';
    const personaTraits = result.persona?.personality_traits || '';
    const personaFinance = result.persona?.financial_situation || 'N/A';
    const transcriptLines = Array.isArray(result.transcript)
        ? result.transcript.map(t => `${t.role}: ${t.content}`)
        : (result.transcript || '').split('\n');

    return (
        <>
            {/* Card Summary - Click to Expand */}
            <div
                className={`p-5 rounded-2xl border transition-all duration-300 flex flex-col h-auto min-h-[140px] neu-card cursor-pointer group hover:scale-[1.01] ${result.passed ? 'border-[#E0E0E0]' : 'border-[#E0E0E0]'}`}
                onClick={() => setIsExpanded(true)}
            >
                {/* Header */}
                <div className="flex justify-between items-start mb-3">
                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            {/* Status Dot */}
                            <div className={`w-2.5 h-2.5 rounded-full shrink-0 ${result.passed ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.4)]' : 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.4)]'}`} />

                            <span className="text-lg font-bold text-[#333333] group-hover:text-black transition-colors">
                                {personaName}
                            </span>
                            <span className="text-[9px] px-2 py-0.5 rounded-full bg-[#E0E0E0] text-[#555555] uppercase tracking-widest font-bold shadow-[inset_1px_1px_2px_#bebebe,inset_-1px_-1px_2px_#ffffff]">
                                {(personaTraits.split(',')[0] || 'Generic').toUpperCase()}
                            </span>
                        </div>
                    </div>
                    <div className="flex flex-col items-end gap-1">
                        <div className={`text-2xl font-black ${result.passed ? 'text-[#333333]' : 'text-[#AAAAAA] line-through decoration-2'}`}>
                            {result.score}
                        </div>
                        {result.updated_prompt && (
                            <span className="text-[9px] bg-[#333333] text-white px-1.5 py-0.5 rounded font-bold uppercase tracking-wider">
                                New Prompt
                            </span>
                        )}
                    </div>
                </div>

                {/* Summary Metrics */}
                <div className="flex gap-4 ml-5">
                    {result.metrics ? (
                        <>
                            <div className="flex flex-col">
                                <span className="text-[9px] uppercase text-[#AAAAAA] font-bold">Repetition</span>
                                <span className="text-xs font-mono font-bold text-[#333333]">{result.metrics.repetition}</span>
                            </div>
                            <div className="flex flex-col">
                                <span className="text-[9px] uppercase text-[#AAAAAA] font-bold">Negotiation</span>
                                <span className="text-xs font-mono font-bold text-[#333333]">{result.metrics.negotiation}</span>
                            </div>
                            <div className="flex flex-col">
                                <span className="text-[9px] uppercase text-[#AAAAAA] font-bold">Empathy</span>
                                <span className="text-xs font-mono font-bold text-[#333333]">{result.metrics.empathy}</span>
                            </div>
                        </>
                    ) : (
                        <p className="text-xs text-[#AAAAAA] line-clamp-1">{personaFinance}</p>
                    )}
                </div>
                <div className="mt-4 text-[10px] text-[#AAAAAA] font-bold uppercase tracking-widest flex items-center gap-1 group-hover:text-[#555555] transition-colors">
                    View Full Transcript <IconChevronDown size={12} />
                </div>
            </div>

            {/* Expanded Modal Overlay - Rendered via Portal */}
            {isExpanded && createPortal(
                <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 sm:p-6 md:p-10 animate-fade-in bg-black/40 backdrop-blur-md" onClick={() => setIsExpanded(false)}>
                    <div
                        className="bg-[#F7F7F7] w-full max-w-7xl h-[85vh] rounded-3xl shadow-2xl flex flex-col overflow-hidden animate-scale-in border border-[#E0E0E0] mx-4 relative"
                        onClick={(e) => e.stopPropagation()}
                    >
                        {/* Modal Header - Fixed */}
                        <div className="px-8 py-6 border-b border-[#E0E0E0] flex items-start justify-between bg-[#F7F7F7] shrink-0 z-20 shadow-sm">
                            <div>
                                <div className="flex items-center gap-4 mb-2">
                                    <div className={`w-3 h-3 rounded-full shrink-0 ${result.passed ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.4)]' : 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.4)]'}`} />
                                    <h2 className="text-3xl font-bold text-[#333333]">{personaName}</h2>
                                    <span className="text-[10px] px-3 py-1 rounded-full bg-[#E0E0E0] text-[#555555] uppercase tracking-widest font-bold">
                                        {(personaTraits.split(',')[0] || 'Generic').toUpperCase()}
                                    </span>
                                </div>
                                <div className="text-sm text-[#777777] font-medium max-w-3xl">
                                    {personaFinance}
                                </div>
                            </div>
                            <div className="flex items-start gap-8">
                                <div className="text-right">
                                    <span className="text-[10px] uppercase font-bold text-[#AAAAAA] block mb-1">Final Score</span>
                                    <span className={`text-5xl font-black ${result.passed ? 'text-[#333333]' : 'text-[#AAAAAA]'}`}>{result.score}</span>
                                </div>
                                <button
                                    onClick={() => setIsExpanded(false)}
                                    className="p-2 rounded-full hover:bg-[#E0E0E0] text-[#555555] transition-colors -mr-2"
                                >
                                    <IconClose size={28} />
                                </button>
                            </div>
                        </div>

                        {/* Modal Content - Two Independent Columns */}
                        <div className="flex-1 overflow-hidden flex flex-col lg:flex-row">

                            {/* Left: Transcript (Scrollable) */}
                            <div className="flex-1 flex flex-col border-b lg:border-b-0 lg:border-r border-[#E0E0E0] bg-[#F7F7F7] min-h-0">
                                <div className="px-8 pt-8 pb-4 shrink-0 z-10 bg-[#F7F7F7]">
                                    <h3 className="text-xs font-bold uppercase tracking-widest text-[#AAAAAA]">Conversation Transcript</h3>
                                </div>
                                <div className="flex-1 overflow-y-auto px-8 pb-8 scrollbar-thin scrollbar-thumb-[#E0E0E0]">
                                    <div className="space-y-6">
                                        {transcriptLines.map((line, idx) => {
                                            const isAgent = line.startsWith('agent:') || line.startsWith('Agent:');
                                            const content = line.split(':').slice(1).join(':').trim();
                                            if (!content) return null;

                                            return (
                                                <div key={idx} className={`flex flex-col ${isAgent ? 'items-end' : 'items-start'}`}>
                                                    <div className={`max-w-[85%] px-6 py-4 rounded-3xl text-sm leading-relaxed shadow-sm ${isAgent
                                                        ? 'bg-[#333333] text-white rounded-br-none'
                                                        : 'bg-white text-[#333333] rounded-bl-none border border-[#E0E0E0]'
                                                        }`}>
                                                        {content}
                                                    </div>
                                                    <span className="text-[10px] text-[#AAAAAA] mt-1.5 uppercase font-bold tracking-wider px-2">
                                                        {isAgent ? 'Rachel' : personaName.split(' ')[0]}
                                                    </span>
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                            </div>

                            {/* Right: Feedback & Metrics (Scrollable) */}
                            <div className="w-full lg:w-[400px] xl:w-[450px] shrink-0 overflow-y-auto p-8 scrollbar-thin scrollbar-thumb-[#E0E0E0] bg-white">
                                <div className="space-y-8">
                                    <div className="bg-[#F7F7F7] p-6 rounded-3xl border border-[#E0E0E0]">
                                        <h3 className="text-xs font-bold uppercase tracking-widest text-[#AAAAAA] mb-6">Metric Breakdown</h3>
                                        <div className="space-y-6">
                                            {result.metrics && Object.entries(result.metrics).map(([key, value]) => (
                                                <div key={key} className="flex flex-col gap-2">
                                                    <div className="flex justify-between items-center px-1">
                                                        <span className="text-[10px] font-bold text-[#555555] uppercase">{key}</span>
                                                        <span className="text-base font-bold text-[#333333]">{value}</span>
                                                    </div>
                                                    <div className="h-3 bg-[#E0E0E0] rounded-full overflow-hidden">
                                                        <div
                                                            className="h-full bg-[#333333] rounded-full"
                                                            style={{ width: `${(value / 10) * 100}%` }}
                                                        />
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    <div className="bg-[#F7F7F7] p-6 rounded-3xl border border-[#E0E0E0]">
                                        <h3 className="text-xs font-bold uppercase tracking-widest text-[#AAAAAA] mb-4">Detailed Feedback</h3>
                                        <p className="text-sm text-[#555555] font-medium leading-relaxed italic">
                                            "{result.feedback}"
                                        </p>
                                    </div>
                                </div>
                            </div>

                        </div>
                    </div>
                </div>,
                document.body
            )}
        </>
    );
}
