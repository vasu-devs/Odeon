// Icons removed as they were unused

export interface ScenarioResult {
    cycle: number;
    persona: {
        name: string;
        personality_traits: string;
        financial_situation: string;
    } | undefined; // Make persona optional/undefined-safe in type definition just in case
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
    // Defines safe accessors
    const personaName = result.persona?.name || 'Unknown';
    const personaTraits = result.persona?.personality_traits || '';
    const personaFinance = result.persona?.financial_situation || 'N/A';
    const transcriptLines = Array.isArray(result.transcript)
        ? result.transcript.map(t => `${t.role}: ${t.content}`)
        : (result.transcript || '').split('\n');

    return (
        <div className={`p-5 rounded-2xl border transition-all hover:scale-[1.02] duration-300 flex flex-col h-[400px] neu-card ${result.passed ? 'border-[#E0E0E0]' : 'border-[#E0E0E0]'}`}>
            {/* Header */}
            <div className="flex justify-between items-start mb-4 border-b border-[#E0E0E0] pb-3">
                <div>
                    <div className="flex items-center gap-2 mb-1">
                        {/* Status Dot */}
                        <div className={`w-2.5 h-2.5 rounded-full shrink-0 ${result.passed ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.4)]' : 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.4)]'}`} />

                        <span className="text-lg font-bold text-[#333333]">
                            {personaName}
                        </span>
                        <span className="text-[9px] px-2 py-0.5 rounded-full bg-[#E0E0E0] text-[#555555] uppercase tracking-widest font-bold shadow-[inset_1px_1px_2px_#bebebe,inset_-1px_-1px_2px_#ffffff]">
                            {(personaTraits.split(',')[0] || 'Generic').toUpperCase()}
                        </span>
                    </div>
                    {/* Metrics Row */}
                    <div className="flex gap-4 mt-2">
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
                </div>
                <div className="flex flex-col items-end gap-1">
                    <div className={`text-2xl font-black ${result.passed ? 'text-[#333333]' : 'text-[#AAAAAA] line-through decoration-2'}`}>
                        {result.score}
                    </div>
                    {result.updated_prompt && (
                        <span className="text-[9px] bg-[#333333] text-white px-1.5 py-0.5 rounded font-bold uppercase tracking-wider animate-pulse">
                            New Prompt
                        </span>
                    )}
                </div>
            </div>

            {/* Transcript Area */}
            <div className="flex-1 overflow-y-auto space-y-3 pr-2 mb-4 scrollbar-thin scrollbar-thumb-[#E0E0E0]">
                {transcriptLines.map((line, idx) => {
                    const isAgent = line.startsWith('agent:') || line.startsWith('Agent:');
                    const content = line.split(':').slice(1).join(':').trim();
                    if (!content) return null;

                    return (
                        <div key={idx} className={`flex flex-col ${isAgent ? 'items-end' : 'items-start'}`}>
                            <div className={`max-w-[85%] px-3 py-2 rounded-2xl text-xs leading-relaxed ${isAgent
                                ? 'bg-[#333333] text-white rounded-br-none shadow-md'
                                : 'bg-[#F0F0F0] text-[#333333] rounded-bl-none shadow-sm'
                                }`}>
                                {content}
                            </div>
                            <span className="text-[9px] text-[#AAAAAA] mt-1 uppercase font-bold tracking-wider px-1">
                                {isAgent ? 'Rachel' : personaName.split(' ')[0]}
                            </span>
                        </div>
                    );
                })}
            </div>

            {/* Footer / Feedback */}
            <div className="pt-3 border-t border-[#E0E0E0] mt-auto">
                <div className="bg-[#F7F7F7] rounded-lg p-3 border border-[#E0E0E0] shadow-[inset_2px_2px_4px_#bebebe,inset_-2px_-2px_4px_#ffffff]">
                    <p className="text-[10px] text-[#555555] font-medium leading-tight line-clamp-2 italic">
                        "{result.feedback}"
                    </p>
                </div>
            </div>
        </div>
    );
}
