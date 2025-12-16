import React from 'react';
import { ArrowLeft, ArrowRight, Save, Download, RefreshCw } from 'lucide-react';

export default function Controls({ params, setParams, onNext, onPrev, onSave, onExport, loading, viewMode, setViewMode }) {
    const handleChange = (e) => {
        const { name, value } = e.target;
        setParams(prev => ({ ...prev, [name]: parseFloat(value) }));
    };

    return (
        <div className="w-80 bg-slate-800 p-6 flex flex-col gap-6 border-r border-slate-700 h-full overflow-y-auto">
            <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-blue-500">
                Mandala Gen
            </h1>

            {/* Navigation */}
            <div className="flex gap-2 justify-between">
                <button onClick={onPrev} className="p-2 rounded bg-slate-700 hover:bg-slate-600 transition">
                    <ArrowLeft size={20} />
                </button>
                <div className="flex-1 text-center font-mono text-xs flex items-center justify-center bg-slate-900 rounded select-all py-1 px-2 truncate">
                    {params.seed || "random"}
                </div>
                <button onClick={onNext} className="p-2 rounded bg-slate-700 hover:bg-slate-600 transition">
                    <ArrowRight size={20} />
                </button>
            </div>

            <div className="flex bg-slate-900 p-1 rounded-lg">
                <button
                    onClick={() => setViewMode('2d')}
                    className={`flex-1 py-1 text-xs font-semibold rounded ${viewMode === '2d' ? 'bg-slate-700 text-white' : 'text-slate-500 hover:text-slate-300'}`}
                >
                    2D Pattern
                </button>
                <button
                    onClick={() => setViewMode('3d')}
                    className={`flex-1 py-1 text-xs font-semibold rounded ${viewMode === '3d' ? 'bg-teal-600 text-white' : 'text-slate-500 hover:text-slate-300'}`}
                >
                    3D Preview
                </button>
            </div>

            <div className="flex flex-col gap-4">
                {/* Dimensions */}
                <div className="space-y-2">
                    <label className="text-xs text-slate-400 uppercase font-semibold">Diameter (mm)</label>
                    <input
                        type="range" name="diameter" min="8" max="25" step="0.5"
                        value={params.diameter} onChange={handleChange}
                        className="w-full accent-teal-500 h-1 bg-slate-600 rounded-lg appearance-none cursor-pointer"
                    />
                    <div className="text-right text-sm text-slate-300">{params.diameter} mm</div>
                </div>

                <div className="space-y-2">
                    <label className="text-xs text-slate-400 uppercase font-semibold">Total Height (mm)</label>
                    <input
                        type="range" name="height" min="1.0" max="4.0" step="0.1"
                        value={params.height} onChange={handleChange}
                        className="w-full accent-teal-500 h-1 bg-slate-600 rounded-lg appearance-none cursor-pointer"
                    />
                    <div className="text-right text-sm text-slate-300">{params.height} mm</div>
                </div>

                <div className="space-y-2">
                    <label className="text-xs text-slate-400 uppercase font-semibold">Relief Depth (mm)</label>
                    <input
                        type="range" name="relief_depth" min="0.2" max="2.0" step="0.1"
                        value={params.relief_depth} onChange={handleChange}
                        className="w-full accent-teal-500 h-1 bg-slate-600 rounded-lg appearance-none cursor-pointer"
                    />
                    <div className="text-right text-sm text-slate-300">{params.relief_depth} mm</div>
                </div>

                <hr className="border-slate-700" />

                {/* Pattern Controls */}
                <div className="space-y-2">
                    <label className="text-xs text-slate-400 uppercase font-semibold">Symmetry</label>
                    <select
                        name="symmetry"
                        value={params.symmetry}
                        onChange={(e) => setParams(prev => ({ ...prev, symmetry: e.target.value }))}
                        className="w-full bg-slate-700 text-white rounded px-3 py-2 text-sm"
                    >
                        <option value="random">Random</option>
                        <option value="6">6-fold</option>
                        <option value="8">8-fold</option>
                        <option value="12">12-fold</option>
                    </select>
                </div>

                <div className="space-y-2">
                    <label className="text-xs text-slate-400 uppercase font-semibold">
                        Complexity <span className="text-slate-500">(elements)</span>
                    </label>
                    <input
                        type="range" name="complexity" min="1" max="5" step="1"
                        value={params.complexity}
                        onChange={(e) => setParams(prev => ({ ...prev, complexity: parseInt(e.target.value) }))}
                        className="w-full accent-teal-500 h-1 bg-slate-600 rounded-lg appearance-none cursor-pointer"
                    />
                    <div className="text-right text-sm text-slate-300">
                        {params.complexity} {params.complexity === 1 ? 'element' : 'elements'}
                    </div>
                </div>

                <div className="space-y-2">
                    <label className="text-xs text-slate-400 uppercase font-semibold">Pattern Types</label>
                    <div className="grid grid-cols-2 gap-2">
                        {['ring', 'ray', 'petal_curve', 'dot_ring'].map(type => (
                            <label key={type} className="flex items-center gap-2 text-xs cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={params.pattern_types.includes(type)}
                                    onChange={(e) => {
                                        const newTypes = e.target.checked
                                            ? [...params.pattern_types, type]
                                            : params.pattern_types.filter(t => t !== type);
                                        // Ensure at least one type is selected
                                        if (newTypes.length > 0) {
                                            setParams(prev => ({ ...prev, pattern_types: newTypes }));
                                        }
                                    }}
                                    className="accent-teal-500"
                                />
                                <span className="text-slate-300 capitalize">
                                    {type === 'petal_curve' ? 'Petals' : type === 'dot_ring' ? 'Dots' : type}
                                </span>
                            </label>
                        ))}
                    </div>
                </div>
            </div>

            {/* Actions */}
            <div className="mt-auto space-y-3">
                {onSave && (
                    <button onClick={onSave} className="w-full flex items-center justify-center gap-2 py-2 px-4 rounded border border-slate-600 hover:bg-slate-700 transition text-sm">
                        <Save size={16} /> Save Design
                    </button>
                )}

                <button
                    onClick={onExport}
                    disabled={loading}
                    className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded bg-gradient-to-r from-teal-500 to-blue-600 hover:from-teal-400 hover:to-blue-500 transition font-semibold text-white shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {loading ? <RefreshCw className="animate-spin" size={20} /> : <Download size={20} />}
                    Export STL
                </button>
            </div>
        </div>
    );
}
