import React, { useState } from 'react';
import type { Detection, ModelInfo } from '../types';
import { exportToCSV, exportToMongoDB } from '../services/api';
import type { FrameDetection } from '../services/api';

interface ResultsPanelProps {
  detections: Detection[];
  modelInfo: ModelInfo;
  mediaType?: 'image' | 'video';
  filename?: string;
  imageSize?: { width: number; height: number };
  videoFrames?: FrameDetection[];
  videoInfo?: { fps: number; duration: number; totalFrames: number };
}

const ResultsPanel: React.FC<ResultsPanelProps> = ({ 
  detections, 
  modelInfo,
  mediaType = 'image',
  filename,
  imageSize,
  videoFrames,
  videoInfo
}) => {
  const [sortBy, setSortBy] = useState<'risk' | 'confidence'>('risk');
  const [showOnlyCritical, setShowOnlyCritical] = useState(false);
  const [isExportingCSV, setIsExportingCSV] = useState(false);
  const [isExportingMongoDB, setIsExportingMongoDB] = useState(false);
  const [exportMessage, setExportMessage] = useState<string | null>(null);

  const riskColors = {
    High: 'bg-red-100 text-red-800 border-red-300',
    Medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    Low: 'bg-green-100 text-green-800 border-green-300',
  };

  const filteredDetections = showOnlyCritical
    ? detections.filter((d) => d.riskLevel === 'High')
    : detections;

  const sortedDetections = [...filteredDetections].sort((a, b) => {
    if (sortBy === 'risk') {
      const riskOrder = { High: 3, Medium: 2, Low: 1 };
      return riskOrder[b.riskLevel] - riskOrder[a.riskLevel];
    } else {
      return b.confidence - a.confidence;
    }
  });

  const handleExportCSV = async () => {
    if (detections.length === 0) {
      setExportMessage('Aucune détection à exporter');
      setTimeout(() => setExportMessage(null), 3000);
      return;
    }

    setIsExportingCSV(true);
    setExportMessage(null);

    try {
      const blob = await exportToCSV(detections);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `detections_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      setExportMessage('✅ CSV exporté avec succès');
    } catch (error) {
      console.error('Erreur export CSV:', error);
      setExportMessage('❌ Erreur lors de l\'export CSV');
    } finally {
      setIsExportingCSV(false);
      setTimeout(() => setExportMessage(null), 3000);
    }
  };

  const handleExportMongoDB = async () => {
    if (detections.length === 0) {
      setExportMessage('Aucune détection à exporter');
      setTimeout(() => setExportMessage(null), 3000);
      return;
    }

    setIsExportingMongoDB(true);
    setExportMessage(null);

    try {
      const result = await exportToMongoDB({
        detections,
        mediaType,
        filename: filename || 'unknown',
        imageSize,
        frames: videoFrames,
        videoInfo,
        metadata: {
          exportedAt: new Date().toISOString(),
          detectionCount: detections.length
        }
      });

      if (result.success) {
        setExportMessage(`✅ ${result.message}`);
      } else {
        setExportMessage('❌ Erreur lors de l\'export MongoDB');
      }
    } catch (error) {
      console.error('Erreur export MongoDB:', error);
      setExportMessage('❌ Erreur lors de l\'export MongoDB');
    } finally {
      setIsExportingMongoDB(false);
      setTimeout(() => setExportMessage(null), 5000);
    }
  };

  return (
    <div className="space-y-6 animate-slide-up">
      {/* Detected Objects Card - Premium */}
      <div className="glass-effect rounded-3xl premium-shadow-lg border border-white/20 p-6 hover:shadow-2xl transition-all duration-300">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="relative w-10 h-10 rounded-xl flex items-center justify-center shadow-lg" style={{ backgroundColor: '#9d8166' }}>
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <h3 className="text-xl font-extrabold text-white">
              Detected objects
            </h3>
          </div>
          <span className="px-4 py-2 text-white rounded-lg text-sm font-bold shadow-lg" style={{ backgroundColor: '#9d8166' }}>
            {filteredDetections.length}
          </span>
        </div>

        {/* Filter Bar - Premium */}
        <div className="flex gap-3 mb-5 pb-5 border-b border-white/10">
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'risk' | 'confidence')}
            className="flex-1 px-4 py-2 glass-effect border border-white/20 rounded-xl text-sm text-white font-semibold focus:outline-none transition-all backdrop-blur-md"
            style={{ '--tw-ring-color': '#9d8166' } as React.CSSProperties}
            onFocus={(e) => { e.currentTarget.style.outline = '2px solid #9d8166'; e.currentTarget.style.outlineOffset = '2px'; }}
            onBlur={(e) => { e.currentTarget.style.outline = 'none'; }}
          >
            <option value="risk" className="text-slate-900">Sort by: Risk level</option>
            <option value="confidence" className="text-slate-900">Sort by: Confidence</option>
          </select>
          <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer font-semibold">
            <input
              type="checkbox"
              checked={showOnlyCritical}
              onChange={(e) => setShowOnlyCritical(e.target.checked)}
              className="w-5 h-5 border-white/20 rounded bg-white/10"
              style={{ accentColor: '#9d8166' }}
            />
            <span>Critical</span>
          </label>
        </div>

        {/* Detections List - Premium */}
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {sortedDetections.length === 0 ? (
            <div className="text-center py-10">
              <div className="relative w-20 h-20 mx-auto mb-4">
                <div className="relative w-20 h-20 glass-effect rounded-full flex items-center justify-center border border-white/20">
                  <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{ color: '#d4c4b0' }}>
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <p className="text-sm text-slate-300 font-semibold">No detections to display</p>
            </div>
          ) : (
            sortedDetections.map((detection, index) => (
              <div
                key={detection.id}
                className="p-4 glass-effect rounded-2xl border border-white/20 hover:shadow-xl transition-all duration-300 animate-scale-in group backdrop-blur-md"
                onMouseEnter={(e) => e.currentTarget.style.borderColor = 'rgba(184, 160, 130, 0.5)'}
                onMouseLeave={(e) => e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.2)'}
                style={{ animationDelay: `${index * 0.08}s` }}
              >
                <div className="flex items-start gap-3">
                  <div className="mt-1 relative">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center backdrop-blur-sm border-2 ${
                      detection.riskLevel === 'High' ? 'bg-red-500/20 border-red-400/50' :
                      detection.riskLevel === 'Medium' ? 'bg-yellow-500/20 border-yellow-400/50' :
                      'bg-emerald-500/20 border-emerald-400/50'
                    } group-hover:scale-110 transition-transform shadow-lg`}>
                      <svg
                        className={`w-6 h-6 ${
                          detection.riskLevel === 'High' ? 'text-red-400' :
                          detection.riskLevel === 'Medium' ? 'text-yellow-400' :
                          'text-emerald-400'
                        } drop-shadow-lg`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2.5}
                          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                        />
                      </svg>
                    </div>
                    {detection.riskLevel === 'High' && (
                      <div className="absolute -top-1 -right-1 w-4 h-4 bg-red-400 rounded-full animate-pulse border-2 border-slate-900 shadow-lg"></div>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-2">
                      <p className="font-bold text-white truncate drop-shadow-lg">
                        {detection.label}
                      </p>
                      <div className="flex items-center gap-1 ml-2 px-2 py-1 bg-white/10 rounded-lg border border-white/20">
                        <span className="text-xs font-semibold" style={{ color: '#d4c4b0' }}>AI:</span>
                        <span className="text-sm font-bold" style={{ color: '#d4c4b0' }}>
                          {(detection.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span
                        className={`px-3 py-1 rounded-xl text-xs font-bold border-2 shadow-lg backdrop-blur-sm ${riskColors[detection.riskLevel]}`}
                      >
                        {detection.riskLevel}
                      </span>
                      <span className="text-xs text-slate-300 flex items-center gap-1 font-semibold">
                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                        {detection.position}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Runway & Model Summary Card - Premium */}
      <div className="glass-effect rounded-3xl premium-shadow-lg border border-white/20 p-6 hover:shadow-2xl transition-all duration-300">
        <div className="flex items-center gap-3 mb-5">
          <div className="relative">
            <div className="relative w-10 h-10 rounded-xl flex items-center justify-center shadow-lg" style={{ backgroundColor: '#9d8166' }}>
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
          </div>
          <h3 className="text-xl font-extrabold text-white">
            Runway & model summary
          </h3>
        </div>
        <div className="space-y-4">
          <div>
            <p className="text-xs text-slate-400 mb-2 font-semibold uppercase tracking-wide">Selected model</p>
            <p className="font-bold text-white text-lg">{modelInfo.name}</p>
          </div>
          <div>
            <p className="text-xs text-slate-400 mb-2 font-semibold uppercase tracking-wide">Mode</p>
            <p className="font-semibold text-slate-300">{modelInfo.mode}</p>
          </div>
          <div className="flex flex-wrap gap-2 pt-3">
            {modelInfo.tags.map((tag, index) => (
              <span
                key={index}
                className="px-3 py-1.5 glass-effect text-white rounded-xl text-xs font-bold border border-white/20 backdrop-blur-md shadow-lg"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Export Card - Premium */}
      <div className="glass-effect rounded-3xl premium-shadow-lg border border-white/20 p-6">
        <h3 className="text-xl font-extrabold text-white mb-5">
          Export
        </h3>
        <div className="space-y-3">
          {exportMessage && (
            <div className={`px-4 py-2 rounded-lg text-sm font-semibold ${
              exportMessage.includes('✅') 
                ? 'bg-green-500/20 text-green-300 border border-green-500/30' 
                : 'bg-red-500/20 text-red-300 border border-red-500/30'
            }`}>
              {exportMessage}
            </div>
          )}
          <button
            onClick={handleExportCSV}
            disabled={isExportingCSV || detections.length === 0}
            className="w-full px-5 py-3 glass-effect text-white rounded-xl font-semibold hover:bg-white/10 transition-all duration-300 border border-white/20 backdrop-blur-md transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center gap-2"
          >
            {isExportingCSV ? (
              <>
                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Export en cours...
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Export detections as CSV
              </>
            )}
          </button>
          <button
            onClick={handleExportMongoDB}
            disabled={isExportingMongoDB || detections.length === 0}
            className="w-full px-5 py-3 text-white rounded-xl font-semibold shadow-lg transition-all duration-300 transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center gap-2"
            style={{ backgroundColor: '#9d8166' }}
            onMouseEnter={(e) => !isExportingMongoDB && (e.currentTarget.style.backgroundColor = '#8b6f57')}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#9d8166'}
          >
            {isExportingMongoDB ? (
              <>
                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Export en cours...
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
                </svg>
                Export to MongoDB
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ResultsPanel;

