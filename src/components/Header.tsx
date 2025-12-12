import React, { useState, useEffect } from 'react';
import { getCurrentModel, switchModel } from '../services/api';

const Header: React.FC = () => {
  const [currentModel, setCurrentModel] = useState<'yolo' | 'onnx'>('yolo');
  const [onnxAvailable, setOnnxAvailable] = useState(false);
  const [isSwitching, setIsSwitching] = useState(false);

  // Charger le modèle actuel au démarrage
  useEffect(() => {
    loadCurrentModel();
  }, []);

  const loadCurrentModel = async () => {
    try {
      const modelInfo = await getCurrentModel();
      setCurrentModel(modelInfo.modelType as 'yolo' | 'onnx');
      setOnnxAvailable(modelInfo.onnx_available || false);
    } catch (error) {
      console.error('Erreur lors du chargement du modèle:', error);
    }
  };

  const handleModelChange = async (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newModel = event.target.value as 'yolo' | 'onnx';
    
    if (newModel === currentModel) return;

    setIsSwitching(true);
    try {
      await switchModel(newModel);
      setCurrentModel(newModel);
      console.log(`✅ Modèle changé vers: ${newModel.toUpperCase()}`);
    } catch (error) {
      console.error('Erreur lors du changement de modèle:', error);
      alert(`Erreur: ${error instanceof Error ? error.message : 'Impossible de changer de modèle'}`);
      // Recharger le modèle actuel en cas d'erreur
      await loadCurrentModel();
    } finally {
      setIsSwitching(false);
    }
  };

  return (
    <header className="glass-effect border-b border-white/10 px-6 py-5 shadow-2xl relative overflow-hidden">
      {/* Animated gradient background */}
      <div className="absolute inset-0 gradient-animated opacity-10"></div>
      
      <div className="flex items-center justify-between relative z-10">
        <div className="flex items-center gap-5">
          {/* AI Icon - Elegant Nude */}
          <div className="relative group">
            <div className="absolute inset-0 rounded-2xl blur-lg opacity-50 group-hover:opacity-70 transition-opacity" style={{ backgroundColor: '#9d8166' }}></div>
            <div className="relative w-14 h-14 rounded-2xl flex items-center justify-center shadow-xl transform group-hover:scale-105 transition-transform duration-300" style={{ backgroundColor: '#9d8166' }}>
              <svg className="w-8 h-8 text-white drop-shadow-lg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div className="absolute -top-1 -right-1 w-4 h-4 bg-emerald-400 rounded-full border-2 border-slate-900 shadow-lg">
              <div className="absolute inset-0 bg-emerald-400 rounded-full animate-ping opacity-75"></div>
            </div>
          </div>
          
          <div>
            <h1 className="text-3xl font-extrabold text-white drop-shadow-lg">
              FOD Detection on Airport Runway
            </h1>
            <p className="text-sm text-slate-300 mt-2 flex items-center gap-3">
              <span className="px-3 py-1 backdrop-blur-sm rounded-lg text-xs font-semibold border" style={{ backgroundColor: 'rgba(157, 129, 102, 0.2)', color: '#d4c4b0', borderColor: 'rgba(157, 129, 102, 0.3)' }}>
                AI POWERED
              </span>
              <span className="text-slate-400">YOLOv8 · EfficientDet · Mask R-CNN · Anomaly Detection</span>
            </p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className="px-5 py-2 bg-emerald-500/20 backdrop-blur-md text-emerald-300 rounded-xl text-sm font-semibold flex items-center gap-2 border border-emerald-500/30">
            <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
            LIVE DEMO
          </span>
          <div className="relative group">
            <select 
              value={currentModel}
              onChange={handleModelChange}
              disabled={isSwitching}
              className="px-5 py-2.5 bg-white/10 backdrop-blur-md border-2 border-white/20 rounded-xl text-sm text-white font-semibold focus:outline-none transition-all shadow-lg hover:bg-white/20 cursor-pointer appearance-none pr-10 disabled:opacity-50 disabled:cursor-not-allowed" 
              style={{ '--tw-ring-color': '#9d8166' } as React.CSSProperties} 
              onFocus={(e) => { e.currentTarget.style.outline = '2px solid #9d8166'; e.currentTarget.style.outlineOffset = '2px'; }} 
              onBlur={(e) => { e.currentTarget.style.outline = 'none'; }}
            >
              <option value="yolo" className="text-slate-900">YOLOv8</option>
              {onnxAvailable && (
                <option value="onnx" className="text-slate-900">ONNX</option>
              )}
            </select>
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none">
              {isSwitching ? (
                <div className="w-5 h-5 border-2 border-slate-400 border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;

