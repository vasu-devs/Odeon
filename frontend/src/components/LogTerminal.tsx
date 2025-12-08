import { useEffect, useRef } from 'react';
import { Terminal } from 'lucide-react';

interface LogTerminalProps {
    logs: string[];
    expanded?: boolean;
}

export default function LogTerminal({ logs }: LogTerminalProps) {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // Auto-scroll to bottom using scrollTop to avoid whole-page jumping
        if (containerRef.current) {
            containerRef.current.scrollTop = containerRef.current.scrollHeight;
        }
    }, [logs]);

    return (
        <div className="flex flex-col flex-1 min-h-[200px] w-full bg-zinc-900 text-zinc-300 font-mono text-[11px] p-4">
            <div className="flex items-center gap-2 mb-3 pb-3 border-b border-zinc-800/50">
                <div className="p-1 bg-zinc-800 rounded">
                    <Terminal size={12} className="text-zinc-400" />
                </div>
                <span className="font-bold uppercase tracking-widest text-zinc-500 text-[10px]">Real-time Logs</span>
            </div>
            <div
                ref={containerRef}
                className="flex-1 overflow-y-auto space-y-1.5 scrollbar-thin scrollbar-thumb-zinc-700"
            >
                {logs.length === 0 && (
                    <div className="text-zinc-700 italic">Waiting for connection...</div>
                )}
                {logs.map((log, i) => (
                    <div key={i} className="break-words whitespace-pre-wrap flex gap-2">
                        <span className="text-zinc-700 shrink-0 select-none">{`>`}</span>
                        <span className={log.includes("Error") ? "text-red-400" : "text-zinc-300"}>{log}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}
