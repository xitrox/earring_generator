import React, { useState, useEffect, useCallback } from 'react';
import Viewer from './components/Viewer';
import Controls from './components/Controls';
import { apiUrl } from './config';

function App() {
  const [params, setParams] = useState({
    diameter: 12.0,
    height: 2.0,
    relief_depth: 0.8,
    seed: Math.random().toString(36).substring(7),
    // Pattern controls
    symmetry: 'random', // 6, 8, 12, or 'random'
    complexity: 4, // 1-5 (number of components)
    pattern_types: ['ring', 'ray', 'petal_curve', 'dot_ring'], // enabled types
    line_thickness: [0.25, 0.5], // [min, max] in mm
  });

  const [heightMapUrl, setHeightMapUrl] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchPreview = useCallback(async () => {
    setLoading(true);
    try {
      // Build URL with all pattern parameters
      const urlParams = new URLSearchParams({
        seed: params.seed,
        diameter: params.diameter,
        symmetry: params.symmetry,
        complexity: params.complexity,
        pattern_types: params.pattern_types.join(','),
        line_thickness: params.line_thickness.join(','),
        t: Date.now(),
      });
      const url = apiUrl(`/api/preview?${urlParams}`);
      const res = await fetch(url);
      const blob = await res.blob();
      const objectUrl = URL.createObjectURL(blob);
      setHeightMapUrl(objectUrl);
    } catch (error) {
      console.error("Failed to load preview", error);
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => {
    fetchPreview();
    // Cleanup URL object
    return () => {
      if (heightMapUrl) URL.revokeObjectURL(heightMapUrl);
    }
  }, [fetchPreview]);

  const [viewMode, setViewMode] = useState('3d'); // '2d' or '3d'

  const handleNext = () => {
    setParams(p => ({ ...p, seed: Math.random().toString(36).substring(7) }));
  };

  const handlePrev = () => {
    // History logic could go here
    console.log("Prev not implemented yet, just keeping seed");
  };

  const handleExport = async () => {
    setLoading(true);
    try {
      const response = await fetch(apiUrl('/api/export'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params),
      });

      if (!response.ok) throw new Error('Export failed');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `earring_${params.seed}.3mf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
    } catch (e) {
      console.error(e);
      alert("Export failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-900 text-white font-sans">
      <Controls
        params={params}
        setParams={setParams}
        onNext={handleNext}
        onPrev={handlePrev}
        onExport={handleExport}
        loading={loading}
        viewMode={viewMode}
        setViewMode={setViewMode}
      />
      <div className="flex-1 h-full relative flex items-center justify-center bg-black">
        {viewMode === '2d' ? (
          heightMapUrl && <img src={heightMapUrl} className="max-h-[80%] max-w-[80%] border-4 border-slate-700 rounded-full" alt="Pattern" />
        ) : (
          <Viewer heightMapUrl={heightMapUrl} params={params} />
        )}
      </div>
    </div>
  );
}

export default App;
