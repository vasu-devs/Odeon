import { useMemo } from 'react';
import { diffWords } from 'diff';
import { GitCompare } from 'lucide-react';

interface DiffViewerProps {
    oldText?: string;
    newText?: string;
    reasoning?: string;
    history?: { cycle: number, old_prompt: string, new_prompt: string, reasoning: string }[];
}

export default function DiffViewer({ oldText, newText, reasoning, history }: DiffViewerProps) {
    // Determine what to display: provided props or latest history
    const latest = history && history.length > 0 ? history[0] : null;

    const displayOld = latest ? latest.old_prompt : oldText;
    const displayNew = latest ? latest.new_prompt : newText;
    const displayReason = latest ? latest.reasoning : reasoning;

    const diff = useMemo(() => {
        if (!displayOld || !displayNew) return null;
        return diffWords(displayOld, displayNew);
    }, [displayOld, displayNew]);

    if (!diff) return null;

    return (
        <div className="bg-white border border-zinc-200 rounded-xl overflow-hidden shadow-sm flex flex-col h-full">
            <div className="bg-zinc-50/50 px-4 py-3 border-b border-zinc-200 flex items-center justify-between shrink-0">
                <div className="flex items-center gap-2 text-zinc-900 font-bold text-xs uppercase tracking-wide">
                    <GitCompare size={14} className="text-zinc-400" /> Prompt Evolution
                </div>
                {displayReason && (
                    <span className="text-xs text-zinc-500 italic max-w-lg truncate" title={displayReason}>
                        Reasoning: {displayReason}
                    </span>
                )}
            </div>
            <div className="p-4 text-xs font-mono leading-relaxed text-zinc-600 overflow-y-auto whitespace-pre-wrap grow scrollbar-thin scrollbar-thumb-zinc-200">
                {diff.map((part, index) => {
                    const color = part.added ? 'bg-green-100 text-green-800 decoration-green-500 underline decoration-2 underline-offset-2' :
                        part.removed ? 'bg-red-50 text-red-300 line-through decoration-red-200' :
                            'text-zinc-500';
                    return (
                        <span key={index} className={color}>
                            {part.value}
                        </span>
                    );
                })}
            </div>
        </div>
    );
}
