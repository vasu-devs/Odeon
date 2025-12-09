import React from 'react';
import { IconPlay, IconStop, IconOdeon } from './Icons';

export interface Config {
    api_key: string;
    model_name: string;
    base_prompt: string;
    max_cycles: number;
    batch_size: number;
    thresholds: {
        repetition: number;
        negotiation: number;
        empathy: number;
        overall: number;
    };
}

export interface SidebarProps {
    config: Config;
    setConfig: React.Dispatch<React.SetStateAction<Config>>;
    onStart: () => void;
    onStop: () => void;
    isRunning: boolean;
}

export default function Sidebar({ config, setConfig, onStart, onStop, isRunning }: SidebarProps) {

    const handleChange = (field: keyof Config, value: any) => {
        setConfig(prev => ({ ...prev, [field]: value }));
    };

    const handleThresholdChange = (metric: keyof Config['thresholds'], value: number) => {
        setConfig(prev => ({
            ...prev,
            thresholds: {
                ...prev.thresholds,
                [metric]: value
            }
        }));
    };

    return (
        <div className="w-[320px] p-6 bg-[#F7F7F7] flex flex-col border-r border-[#E0E0E0] h-full shadow-[6px_0_12px_rgba(0,0,0,0.02)] shrink-0 overflow-y-auto scrollbar-thin scrollbar-thumb-[#E0E0E0] z-20">
            {/* Header */}
            <div className="flex items-center gap-4 mb-10">
                <div className="p-3 bg-[#F7F7F7] rounded-xl shadow-[6px_6px_12px_#bebebe,-6px_-6px_12px_#ffffff]">
                    <IconOdeon size={28} className="text-[#333333]" />
                </div>
                <div>
                    <h1 className="text-xl font-bold tracking-tight text-[#333333]">ODEON</h1>
                    <p className="text-[10px] text-[#AAAAAA] font-bold uppercase tracking-widest">Simulation Platform</p>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto px-8 py-4 space-y-10 scrollbar-none">

                {/* API Settings */}
                <div className="space-y-5">
                    <h3 className="text-[11px] font-bold text-[#AAAAAA] uppercase tracking-widest flex items-center gap-2 pl-1">
                        Configuration
                    </h3>

                    <div className="space-y-5">
                        <div className="space-y-2">
                            <label className="text-xs font-semibold text-[#555555] ml-1">API Key</label>
                            <input
                                type="password"
                                value={config.api_key}
                                onChange={(e) => handleChange('api_key', e.target.value)}
                                className="neu-input w-full p-3.5 text-sm text-[#333333] placeholder-[#AAAAAA]"
                                placeholder="sk-..."
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs font-semibold text-[#555555] ml-1">Model Name</label>
                            <input
                                type="text"
                                value={config.model_name}
                                onChange={(e) => handleChange('model_name', e.target.value)}
                                className="neu-input w-full p-3.5 text-sm text-[#333333] placeholder-[#AAAAAA]"
                                placeholder="llama-3.1-70b-versatile"
                            />
                        </div>
                    </div>
                </div>

                {/* Simulation Settings */}
                <div className="space-y-5">
                    <h3 className="text-[11px] font-bold text-[#AAAAAA] uppercase tracking-widest flex items-center gap-2 pl-1">
                        Parameters
                    </h3>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="text-xs font-semibold text-[#555555] ml-1">Max Cycles</label>
                            <input
                                type="number"
                                value={config.max_cycles}
                                onChange={(e) => handleChange('max_cycles', parseInt(e.target.value))}
                                className="neu-input w-full p-3 text-sm text-[#333333] text-center"
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs font-semibold text-[#555555] ml-1">Batch Size</label>
                            <input
                                type="number"
                                value={config.batch_size}
                                onChange={(e) => handleChange('batch_size', parseInt(e.target.value))}
                                className="neu-input w-full p-3 text-sm text-[#333333] text-center"
                            />
                        </div>
                    </div>

                    <div className="space-y-6 pt-2">
                        <div className="space-y-1.5">
                            <div className="flex justify-between items-center px-1">
                                <label className="text-[10px] font-bold text-[#AAAAAA] uppercase tracking-widest">Strict Metric Targets</label>
                            </div>
                        </div>

                        {/* Metric Sliders */}
                        {[
                            { label: 'Overall Score', key: 'overall', min: 1, max: 10, step: 0.5 },
                            { label: 'Repetition', key: 'repetition', min: 1, max: 10, step: 1 },
                            { label: 'Negotiation', key: 'negotiation', min: 1, max: 10, step: 1 },
                            { label: 'Empathy', key: 'empathy', min: 1, max: 10, step: 1 }
                        ].map((metric) => (
                            <div key={metric.key} className="space-y-3">
                                <div className="flex justify-between items-center px-1">
                                    <label className="text-xs font-semibold text-[#555555]">{metric.label}</label>
                                    <span className="text-xs font-mono font-bold text-[#333333]">{config.thresholds[metric.key as keyof typeof config.thresholds]}</span>
                                </div>
                                <div className="h-4 relative flex items-center">
                                    <input
                                        type="range"
                                        min={metric.min} max={metric.max} step={metric.step}
                                        value={config.thresholds[metric.key as keyof typeof config.thresholds]}
                                        onChange={(e) => handleThresholdChange(metric.key as keyof typeof config.thresholds, parseFloat(e.target.value))}
                                        className="w-full relative z-10"
                                    />
                                    <div className="absolute inset-0 h-2 bg-[#F7F7F7] shadow-[inset_2px_2px_5px_#bebebe,inset_-2px_-2px_5px_#ffffff] rounded-full top-1"></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Prompt */}
                <div className="space-y-4 flex-1 flex flex-col min-h-[200px]">
                    <h3 className="text-[11px] font-bold text-[#AAAAAA] uppercase tracking-widest pl-1">
                        System Prompt
                    </h3>
                    <textarea
                        value={config.base_prompt}
                        onChange={(e) => handleChange('base_prompt', e.target.value)}
                        className="neu-input flex-1 w-full p-4 textxs font-mono text-[#444] leading-relaxed resize-none text-[11px]"
                        placeholder="Enter system prompt here..."
                    />
                </div>

            </div>

            <div className="p-8 pt-0 bg-[#F7F7F7]">
                <button
                    onClick={isRunning ? onStop : onStart}
                    className={`w-full py-4 rounded-xl font-bold flex items-center justify-center gap-3 transition-all duration-300 ${isRunning
                        ? 'bg-black text-white hover:scale-95 active:scale-90 shadow-[4px_4px_10px_#bebebe,-4px_-4px_10px_#ffffff]'
                        : 'neu-btn hover:text-black text-[#333]'
                        }`}
                >
                    {isRunning ? (
                        <>
                            <IconStop size={18} className="animate-pulse" /> <span className="text-sm tracking-wide uppercase">Stop Optimization</span>
                        </>
                    ) : (
                        <>
                            <IconPlay size={18} fill="currentColor" /> <span className="text-sm tracking-wide uppercase">Start Optimization</span>
                        </>
                    )}
                </button>
            </div>
        </div>
    );
}
