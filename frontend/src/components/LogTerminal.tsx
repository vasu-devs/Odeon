import { useEffect, useRef } from 'react';
import { IconTerminal } from './Icons';

interface LogTerminalProps {
    logs: string[];
    expanded?: boolean;
}

export default function LogTerminal({ logs }: LogTerminalProps) {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (containerRef.current) {
            containerRef.current.scrollTop = containerRef.current.scrollHeight;
        }
    }, [logs]);

    return (
        <div className="flex flex-col flex-1 min-h-[200px] w-full neu-card p-6 overflow-hidden">
            <div className="flex items-center gap-3 mb-4 pb-4 border-b border-[#E0E0E0]">
                <div className="p-2 bg-[#F7F7F7] rounded shadow-[inset_2px_2px_4px_#bebebe,inset_-2px_-2px_4px_#ffffff]">
                    <IconTerminal size={14} className="text-[#333333]" />
                </div>
                <span className="font-bold uppercase tracking-widest text-[#AAAAAA] text-[11px]">Real-time Logs</span>
            </div>

            <div
                ref={containerRef}
                className="flex-1 overflow-y-auto space-y-2 font-mono text-xs pr-2"
            >
                {logs.length === 0 && (
                    <div className="text-[#AAAAAA] italic flex items-center justify-center h-full opacity-50">
                        Waiting for simulation data...
                    </div>
                )}
                {logs.map((log, i) => {
                    // Simple logic to bold names if they appear at the start (e.g. "Rachel: Hello")
                    const hasSpeaker = log.includes(':');
                    const parts = hasSpeaker ? log.split(':') : [log];
                    const speaker = hasSpeaker ? parts[0] : '';
                    const message = hasSpeaker ? parts.slice(1).join(':') : log;

                    return (
                        <div key={i} className="break-words whitespace-pre-wrap flex gap-3 leading-relaxed">
                            <div className="shrink-0 pt-0.5 text-[#AAAAAA]">
                                <IconTerminal size={10} />
                            </div>
                            <div className="text-[#333333]">
                                {hasSpeaker ? (
                                    <>
                                        <span className="font-bold text-[#111111] uppercase tracking-wide text-[10px] mr-2">{speaker}</span>
                                        <span className="text-[#444444]">{message}</span>
                                    </>
                                ) : (
                                    <span className={log.includes("Error") ? "font-bold text-[#333333]" : "text-[#444444]"}>
                                        {log}
                                        {/* If it's an error, we keep it black/bold per monochrome rules instead of red */}
                                    </span>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
