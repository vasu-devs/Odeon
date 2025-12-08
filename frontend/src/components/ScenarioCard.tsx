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
        <div className={`p-5 rounded-2xl border ${result.passed ? 'bg-white border-green-200 shadow-green-500/10 shadow-sm' : 'bg-white border-red-200 shadow-red-500/10 shadow-sm'} transition-all hover:scale-[1.02] duration-300 flex flex-col h-[400px]`}>
            {/* Header */}
            <div className="flex justify-between items-start mb-4 border-b border-zinc-100 pb-3">
                <div>
                    <div className="flex items-center gap-2 mb-1">
                        <span className={`text-lg font-bold ${result.passed ? 'text-green-700' : 'text-red-600'}`}>
                            {personaName}
                        </span>
                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-zinc-100 text-zinc-500 uppercase tracking-widest font-bold">
                            {(personaTraits.split(',')[0] || 'Generic').toUpperCase()}
                        </span>
                    </div>
                    {/* Metrics Row */}
                    <div className="flex gap-2 mt-2">
                        {result.metrics ? (
                            <>
                                <div className="flex flex-col">
                                    <span className="text-[8px] uppercase text-zinc-400 font-bold">Repetition</span>
                                    <span className="text-xs font-mono font-bold">{result.metrics.repetition}</span>
                                </div>
                                <div className="flex flex-col">
                                    <span className="text-[8px] uppercase text-zinc-400 font-bold">Negotiation</span>
                                    <span className="text-xs font-mono font-bold">{result.metrics.negotiation}</span>
                                </div>
                                <div className="flex flex-col">
                                    <span className="text-[8px] uppercase text-zinc-400 font-bold">Empathy</span>
                                    <span className="text-xs font-mono font-bold">{result.metrics.empathy}</span>
                                </div>
                            </>
                        ) : (
                            <p className="text-xs text-zinc-400 line-clamp-1">{personaFinance}</p>
                        )}
                    </div>
                </div>
                <div className="flex flex-col items-end gap-1">
                    <div className={`text-2xl font-black ${result.passed ? 'text-green-600' : 'text-red-500'}`}>
                        {result.score}
                    </div>
                    {result.updated_prompt && (
                        <span className="text-[9px] bg-blue-100 text-blue-600 px-1.5 py-0.5 rounded font-bold uppercase tracking-wider animate-pulse">
                            Prompt Updated
                        </span>
                    )}
                </div>
            </div>

            {/* Transcript Area */}
            <div className="flex-1 overflow-y-auto space-y-3 pr-2 mb-4 scrollbar-thin scrollbar-thumb-zinc-200">
                {transcriptLines.map((line, idx) => {
                    const isAgent = line.startsWith('agent:') || line.startsWith('Agent:');
                    const content = line.split(':').slice(1).join(':').trim();
                    if (!content) return null;

                    return (
                        <div key={idx} className={`flex flex-col ${isAgent ? 'items-end' : 'items-start'}`}>
                            <div className={`max-w-[85%] px-3 py-2 rounded-2xl text-xs leading-relaxed ${isAgent
                                ? 'bg-zinc-900 text-white rounded-br-none'
                                : 'bg-zinc-100 text-zinc-800 rounded-bl-none'
                                }`}>
                                {content}
                            </div>
                            <span className="text-[9px] text-zinc-300 mt-1 uppercase font-bold tracking-wider px-1">
                                {isAgent ? 'Rachel' : personaName.split(' ')[0]}
                            </span>
                        </div>
                    );
                })}
            </div>

            {/* Footer / Feedback */}
            <div className="pt-3 border-t border-zinc-100 mt-auto">
                <div className="bg-amber-50 rounded-lg p-2 border border-amber-100/50">
                    <p className="text-[10px] text-amber-900/70 font-medium leading-tight line-clamp-2">
                        {result.feedback}
                    </p>
                </div>
            </div>
        </div>
    );
}
