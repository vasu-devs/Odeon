import { useMemo, useState } from 'react';
import { diffWords } from 'diff';
import { IconCompare, IconCopy, IconCheck } from './Icons';

interface DiffViewerProps {
    oldText?: string;
    newText?: string;
    reasoning?: string;
    history?: { cycle: number, old_prompt: string, new_prompt: string, reasoning: string }[];
}

export default function DiffViewer({ oldText, newText, reasoning, history }: DiffViewerProps) {
    const [isCopied, setIsCopied] = useState(false);

    // Determine what to display: provided props or latest history
    // history is expected to be newest-first, so history[0] is the latest
    const latest = history && history.length > 0 ? history[0] : null;

    const displayOld = latest ? latest.old_prompt : oldText;
    const displayNew = latest ? latest.new_prompt : newText;
    const displayReason = latest ? latest.reasoning : reasoning;

    const diff = useMemo(() => {
        if (!displayOld || !displayNew) return null;
        return diffWords(displayOld, displayNew);
    }, [displayOld, displayNew]);

    const handleCopy = () => {
        if (!displayNew) return;
        navigator.clipboard.writeText(displayNew);
        setIsCopied(true);
        setTimeout(() => setIsCopied(false), 2000);
    };

    if (!diff) return null;

    return (
        <div className="neu-card overflow-hidden flex flex-col h-full border-none">
            <div className="bg-[#F7F7F7] px-5 py-4 border-b border-[#E0E0E0] shrink-0 shadow-[inset_0_-1px_2px_#eeeeee]">
                <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2 text-[#333333] font-bold text-[10px] uppercase tracking-widest">
                        <IconCompare size={14} className="text-[#333333]" /> Prompt Evolution
                    </div>
                    <button
                        onClick={handleCopy}
                        className="flex items-center gap-1.5 px-2 py-1 rounded hover:bg-[#E5E5E5] text-[#555555] transition-colors text-[9px] font-bold uppercase tracking-wider"
                        title="Copy New Prompt"
                    >
                        {isCopied ? <IconCheck size={12} className="text-green-600" /> : <IconCopy size={12} />}
                        {isCopied ? 'Copied' : 'Copy'}
                    </button>
                </div>
                {displayReason && (
                    <div className="flex items-start gap-2 mt-2 bg-white/50 p-2 rounded border border-[#E0E0E0]/50">
                        <span className="text-[10px] text-[#777777] font-medium leading-relaxed italic">
                            <span className="font-bold not-italic text-[#555555] mr-1">Update Reason:</span>
                            {displayReason}
                        </span>
                    </div>
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
