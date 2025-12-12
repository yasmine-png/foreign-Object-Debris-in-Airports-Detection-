import React from 'react';

interface AIScanEffectProps {
  isActive: boolean;
}

const AIScanEffect: React.FC<AIScanEffectProps> = ({ isActive }) => {
  if (!isActive) return null;

  return (
    <>
      {/* Clean scanning line effect */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden z-10">
        <div 
          className="absolute w-full h-1 opacity-40"
          style={{
            backgroundColor: '#b8a082',
            animation: 'scanLine 1.5s linear infinite',
            top: '0%',
            boxShadow: '0 0 10px rgba(184, 160, 130, 0.5)',
          }}
        />
      </div>

      {/* Clean corner detection indicators */}
      <div className="absolute top-0 left-0 w-10 h-10 border-t-2 border-l-2" style={{ borderColor: 'rgba(184, 160, 130, 0.6)' }}>
        <div className="absolute top-0 left-0 w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: '#b8a082' }}></div>
      </div>
      <div className="absolute top-0 right-0 w-10 h-10 border-t-2 border-r-2" style={{ borderColor: 'rgba(184, 160, 130, 0.6)' }}>
        <div className="absolute top-0 right-0 w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: '#b8a082' }}></div>
      </div>
      <div className="absolute bottom-0 left-0 w-10 h-10 border-b-2 border-l-2" style={{ borderColor: 'rgba(184, 160, 130, 0.6)' }}>
        <div className="absolute bottom-0 left-0 w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: '#b8a082' }}></div>
      </div>
      <div className="absolute bottom-0 right-0 w-10 h-10 border-b-2 border-r-2" style={{ borderColor: 'rgba(184, 160, 130, 0.6)' }}>
        <div className="absolute bottom-0 right-0 w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: '#b8a082' }}></div>
      </div>
    </>
  );
};

export default AIScanEffect;

