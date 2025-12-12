import React from 'react';

interface AIProcessingIndicatorProps {
  isProcessing: boolean;
  model?: string;
}

const AIProcessingIndicator: React.FC<AIProcessingIndicatorProps> = ({ 
  isProcessing, 
  model = 'YOLOv8' 
}) => {
  if (!isProcessing) return null;

  return (
    <div className="absolute top-6 right-6 z-30 glass-effect text-white px-4 py-2 rounded-xl shadow-lg flex items-center gap-3 border border-white/20 backdrop-blur-md">
      <div className="relative">
        <div className="w-3 h-3 rounded-full animate-ping" style={{ backgroundColor: '#b8a082' }}></div>
        <div className="absolute inset-0 w-3 h-3 rounded-full" style={{ backgroundColor: '#b8a082' }}></div>
      </div>
      <div className="flex flex-col">
        <span className="text-xs font-semibold" style={{ color: '#d4c4b0' }}>
          AI PROCESSING
        </span>
        <span className="text-xs text-slate-400 font-medium">{model}</span>
      </div>
      <div className="flex gap-1">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="w-1 h-4 rounded-full"
            style={{
              backgroundColor: '#b8a082',
              animation: `pulseBar 1.2s ease-in-out infinite`,
              animationDelay: `${i * 0.2}s`,
            }}
          />
        ))}
      </div>
    </div>
  );
};

export default AIProcessingIndicator;

