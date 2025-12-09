import { useMemo } from 'react';
import { diffWords } from 'diff';
import { IconCompare } from './Icons';

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
        <div className="neu-card overflow-hidden flex flex-col h-full border-none">
            <div className="bg-[#F7F7F7] px-5 py-4 border-b border-[#E0E0E0] flex items-center justify-between shrink-0 shadow-[inset_0_-1px_2px_#eeeeee]">
                <div className="flex items-center gap-3 text-[#333333] font-bold text-[10px] uppercase tracking-widest">
                    <IconCompare size={14} className="text-[#333333]" /> Prompt Evolution
                </div>
                {displayReason && (
                    <span className="text-[10px] text-[#777777] italic max-w-lg truncate font-medium" title={displayReason}>
                        Reasoning: {displayReason}
                    </span>
                )}
            </div>
            <div className="p-5 text-xs font-mono leading-relaxed text-[#555555] overflow-y-auto whitespace-pre-wrap grow scrollbar-thin scrollbar-thumb-zinc-300">
                {diff.map((part, index) => {
                    const style = part.added ? 'bg-[#333333] text-white font-bold decoration-none px-1 rounded-sm' :
                        part.removed ? 'text-[#AAAAAA] line-throughDecoration decoration-[#AAAAAA] decoration-1 opacity-60' :
                            'text-[#555555]';
                    return (
                        <span key={index} className={style}>
                            {part.value}
                        </span>
                    );
                })}
            </div>
        </div>
    );
}
