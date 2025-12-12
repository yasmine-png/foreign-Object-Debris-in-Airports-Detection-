import React, { useState, useEffect } from 'react';

interface ProcessingOverlayProps {
  isProcessing: boolean;
  message?: string;
  delayMinutes?: number;
}

const ProcessingOverlay: React.FC<ProcessingOverlayProps> = ({ 
  isProcessing, 
  message = "Please wait until we finish, don't click anything",
  delayMinutes = 4
}) => {
  const [showOverlay, setShowOverlay] = useState(false);

  useEffect(() => {
    if (!isProcessing) {
      setShowOverlay(false);
      return;
    }

    // Afficher l'overlay seulement après le délai spécifié (4 minutes par défaut)
    const timer = setTimeout(() => {
      if (isProcessing) {
        setShowOverlay(true);
      }
    }, delayMinutes * 60 * 1000); // Convertir les minutes en millisecondes

    return () => {
      clearTimeout(timer);
    };
  }, [isProcessing, delayMinutes]);

  if (!isProcessing || !showOverlay) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
      style={{ pointerEvents: 'auto' }}
      onClick={(e) => e.stopPropagation()}
      onMouseDown={(e) => e.preventDefault()}
    >
      <div className="glass-effect rounded-3xl p-8 shadow-2xl border border-white/20 backdrop-blur-md max-w-md mx-4">
        <div className="flex flex-col items-center text-center">
          {/* Spinner animé */}
          <div className="relative mb-6">
            <div className="w-20 h-20 rounded-full border-4 border-slate-700 border-t-transparent animate-spin" style={{ borderTopColor: '#9d8166' }}></div>
            <div className="absolute inset-0 w-20 h-20 rounded-full border-4 border-transparent border-r-transparent animate-spin" style={{ 
              borderRightColor: '#b8a082',
              animationDuration: '0.8s',
              animationDirection: 'reverse'
            }}></div>
          </div>
          
          {/* Message */}
          <h3 className="text-2xl font-bold text-white mb-3">
            Processing...
          </h3>
          <p className="text-slate-300 text-sm mb-4 leading-relaxed">
            {message}
          </p>
          
          {/* Barre de progression animée */}
          <div className="w-full h-2 bg-slate-700/50 rounded-full overflow-hidden mt-2">
            <div 
              className="h-full rounded-full animate-pulse"
              style={{ 
                backgroundColor: '#9d8166',
                width: '100%',
                animation: 'progressBar 2s ease-in-out infinite'
              }}
            ></div>
          </div>
          
          {/* Points animés */}
          <div className="flex gap-2 mt-6">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className="w-2 h-2 rounded-full animate-bounce"
                style={{
                  backgroundColor: '#9d8166',
                  animationDelay: `${i * 0.2}s`,
                  animationDuration: '1s'
                }}
              />
            ))}
          </div>
        </div>
      </div>
      
      <style>{`
        @keyframes progressBar {
          0%, 100% {
            transform: translateX(-100%);
          }
          50% {
            transform: translateX(100%);
          }
        }
      `}</style>
    </div>
  );
};

export default ProcessingOverlay;

