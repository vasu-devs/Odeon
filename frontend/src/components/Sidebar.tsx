import React from 'react';
import { Play, Settings, Activity, FolderClock } from 'lucide-react';

export interface Config {
    api_key: string;
    model_name: string;
    base_prompt: string;
    max_cycles: number;
    batch_size: number;
    threshold: number;
}

export interface SidebarProps {
    config: Config;
    setConfig: React.Dispatch<React.SetStateAction<Config>>;
    onStart: () => void;
    isRunning: boolean;
    onHistory: () => void;
}

export default function Sidebar({ config, setConfig, onStart, isRunning, onHistory }: SidebarProps) {

    const handleChange = (field: keyof Config, value: any) => {
        setConfig(prev => ({ ...prev, [field]: value }));
    };

    return (
        <div className="w-[300px] bg-zinc-50/80 backdrop-blur-md border-r border-zinc-200 flex flex-col h-screen shrink-0 font-sans">
            <div className="p-6 flex items-center gap-3">
                <div className="bg-black p-2 rounded-lg shadow-sm">
                    <Settings className="text-white" size={18} />
                </div>
                <div>
                    <h1 className="font-bold text-zinc-900 tracking-tight text-lg">Odeon</h1>
                    <p className="text-xs text-zinc-500 font-medium">Platform</p>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto px-6 py-2 space-y-8">

                {/* History Button at top for easy access */}
                <div className="space-y-4">
                    <button
                        onClick={onHistory}
                        className="w-full flex items-center justify-center gap-2 bg-white border border-zinc-200 p-3 rounded-xl font-bold text-sm text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900 transition-all shadow-sm group"
                    >
                        <FolderClock size={16} className="text-zinc-400 group-hover:text-blue-500 transition-colors" />
                        View History
                    </button>
                </div>

                {/* API Settings */}
                <div className="space-y-4">
                    <h3 className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest flex items-center gap-2">
                        Configuration
                    </h3>

                    <div className="space-y-3">
                        <div className="space-y-1.5">
                            <label className="text-xs font-medium text-zinc-600">API Key</label>
                            <input
                                type="password"
                                value={config.api_key}
                                onChange={(e) => handleChange('api_key', e.target.value)}
                                className="w-full bg-white border border-zinc-200 rounded-lg p-2.5 text-sm text-zinc-900 focus:outline-none focus:ring-2 focus:ring-zinc-900/10 focus:border-zinc-300 transition-all shadow-sm"
                                placeholder="sk-..."
                            />
                        </div>
                        <div className="space-y-1.5">
                            <label className="text-xs font-medium text-zinc-600">Model Name</label>
                            <input
                                type="text"
                                value={config.model_name}
                                onChange={(e) => handleChange('model_name', e.target.value)}
                                className="w-full bg-white border border-zinc-200 rounded-lg p-2.5 text-sm text-zinc-900 focus:outline-none focus:ring-2 focus:ring-zinc-900/10 focus:border-zinc-300 transition-all shadow-sm"
                                placeholder="llama-3.1-70b-versatile"
                            />
                        </div>
                    </div>
                </div>

                {/* Simulation Settings */}
                <div className="space-y-4">
                    <h3 className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest flex items-center gap-2">
                        Parameters
                    </h3>

                    <div className="grid grid-cols-2 gap-3">
                        <div className="space-y-1.5">
                            <label className="text-xs font-medium text-zinc-600">Max Cycles</label>
                            <input
                                type="number"
                                value={config.max_cycles}
                                onChange={(e) => handleChange('max_cycles', parseInt(e.target.value))}
                                className="w-full bg-white border border-zinc-200 rounded-lg p-2.5 text-sm text-zinc-900 focus:outline-none focus:ring-2 focus:ring-zinc-900/10 focus:border-zinc-300 transition-all shadow-sm"
                            />
                        </div>
                        <div className="space-y-1.5">
                            <label className="text-xs font-medium text-zinc-600">Batch Size</label>
                            <input
                                type="number"
                                value={config.batch_size}
                                onChange={(e) => handleChange('batch_size', parseInt(e.target.value))}
                                className="w-full bg-white border border-zinc-200 rounded-lg p-2.5 text-sm text-zinc-900 focus:outline-none focus:ring-2 focus:ring-zinc-900/10 focus:border-zinc-300 transition-all shadow-sm"
                            />
                        </div>
                    </div>

                    <div className="space-y-1.5">
                        <div className="flex justify-between items-center">
                            <label className="text-xs font-medium text-zinc-600">Success Threshold</label>
                            <span className="text-xs font-mono bg-zinc-100 px-1.5 py-0.5 rounded text-zinc-600 border border-zinc-200">{config.threshold}</span>
                        </div>
                        <input
                            type="range"
                            min="0" max="1" step="0.05"
                            value={config.threshold}
                            onChange={(e) => handleChange('threshold', parseFloat(e.target.value))}
                            className="w-full accent-black h-1 bg-zinc-200 rounded-lg appearance-none cursor-pointer"
                        />
                    </div>
                </div>

                {/* Prompt */}
                <div className="space-y-4 flex-1 flex flex-col min-h-[200px]">
                    <h3 className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest">
                        System Prompt
                    </h3>
                    <textarea
                        value={config.base_prompt}
                        onChange={(e) => handleChange('base_prompt', e.target.value)}
                        className="flex-1 w-full bg-white border border-zinc-200 rounded-lg p-3 text-xs font-mono text-zinc-700 focus:outline-none focus:ring-2 focus:ring-zinc-900/10 focus:border-zinc-300 transition-all resize-none leading-relaxed shadow-sm"
                        placeholder="Enter system prompt here..."
                    />
                </div>

            </div>

            <div className="p-6 border-t border-zinc-200/50 bg-white/50 backdrop-blur-sm">
                <button
                    onClick={onStart}
                    disabled={isRunning}
                    className={`w-full py-3 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all shadow-sm hover:shadow-md active:scale-95 ${isRunning
                        ? 'bg-zinc-100 text-zinc-400 cursor-not-allowed border border-zinc-200'
                        : 'bg-zinc-900 text-white hover:bg-black'
                        }`}
                >
                    {isRunning ? (
                        <>
                            <Activity className="animate-spin" size={16} /> <span className="text-sm">Optimizing...</span>
                        </>
                    ) : (
                        <>
                            <Play size={16} fill="currentColor" /> <span className="text-sm">Start Optimization</span>
                        </>
                    )}
                </button>
            </div>
        </div>
    );
}
