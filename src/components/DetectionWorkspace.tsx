import React, { useState, useEffect } from 'react';
import type { InputMode, MediaSource, Detection } from '../types';
import AIScanEffect from './AIScanEffect';
import AIProcessingIndicator from './AIProcessingIndicator';

interface DetectionWorkspaceProps {
  inputMode: InputMode;
  onModeChange: (mode: InputMode) => void;
  mediaLoaded: boolean;
  mediaSource: MediaSource;
  detections: Detection[];
  isProcessing?: boolean;
  imageUrl?: string | null;
  videoUrl?: string | null;
  onVideoTimeUpdate?: (time: number) => void;
  onUseCamera: () => void;
  onUploadVideo: () => void;
  onUploadImage: () => void;
}

const DetectionWorkspace: React.FC<DetectionWorkspaceProps> = ({
  inputMode,
  onModeChange,
  mediaLoaded,
  mediaSource,
  detections,
  isProcessing: externalIsProcessing = false,
  imageUrl,
  videoUrl,
  onVideoTimeUpdate,
  onUseCamera,
  onUploadVideo,
  onUploadImage,
}) => {
  const videoRef = React.useRef<HTMLVideoElement>(null);
  const imageContainerRef = React.useRef<HTMLDivElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [videoError, setVideoError] = useState<string | null>(null);
  const [imageDisplayInfo, setImageDisplayInfo] = useState<{
    naturalWidth: number;
    naturalHeight: number;
    displayedWidth: number;
    displayedHeight: number;
    offsetX: number;
    offsetY: number;
  } | null>(null);

  // Réinitialiser les infos d'affichage quand l'image ou la vidéo change
  useEffect(() => {
    if (!imageUrl && !videoUrl) {
      setImageDisplayInfo(null);
    }
    // Réinitialiser l'erreur vidéo quand la vidéo change
    if (videoUrl) {
      setVideoError(null);
    }
  }, [imageUrl, videoUrl]);

  // Vérifier que la vidéo est bien chargée (juste pour le debug)
  useEffect(() => {
    if (videoUrl && videoRef.current) {
      console.log('📹 videoUrl changé, vidéo devrait s\'afficher:', videoUrl);
      
      // Vérifier après un court délai pour voir l'état
      const checkVideo = setTimeout(() => {
        if (videoRef.current) {
          const v = videoRef.current;
          const errorInfo = v.error ? {
            code: v.error.code,
            message: v.error.message,
            MEDIA_ERR_ABORTED: v.error.MEDIA_ERR_ABORTED,
            MEDIA_ERR_NETWORK: v.error.MEDIA_ERR_NETWORK,
            MEDIA_ERR_DECODE: v.error.MEDIA_ERR_DECODE,
            MEDIA_ERR_SRC_NOT_SUPPORTED: v.error.MEDIA_ERR_SRC_NOT_SUPPORTED,
            codeName: v.error.code === v.error.MEDIA_ERR_ABORTED ? 'MEDIA_ERR_ABORTED' :
                     v.error.code === v.error.MEDIA_ERR_NETWORK ? 'MEDIA_ERR_NETWORK' :
                     v.error.code === v.error.MEDIA_ERR_DECODE ? 'MEDIA_ERR_DECODE' :
                     v.error.code === v.error.MEDIA_ERR_SRC_NOT_SUPPORTED ? 'MEDIA_ERR_SRC_NOT_SUPPORTED' : 'UNKNOWN'
          } : null;
          
          console.log('📊 État de la vidéo (après chargement):', {
            readyState: v.readyState,
            networkState: v.networkState,
            error: errorInfo,
            src: v.src,
            currentSrc: v.currentSrc,
            videoWidth: v.videoWidth,
            videoHeight: v.videoHeight
          });
          
          if (v.readyState >= 2) {
            console.log('✅ Vidéo prête à être affichée');
          } else if (v.error) {
            console.error('❌ Erreur vidéo détectée:', errorInfo);
          } else {
            console.warn('⚠️ Vidéo pas encore prête, readyState:', v.readyState);
          }
        }
      }, 1000);
      
      return () => clearTimeout(checkVideo);
    }
  }, [videoUrl]);

  return (
    <div className="space-y-6 animate-fade-in-up">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="relative group">
            <div className="absolute inset-0 rounded-2xl blur-xl opacity-30 group-hover:opacity-50 transition-opacity" style={{ backgroundColor: '#9d8166' }}></div>
            <div className="relative w-14 h-14 rounded-2xl flex items-center justify-center shadow-xl transform group-hover:scale-105 transition-transform duration-300" style={{ backgroundColor: '#9d8166' }}>
              <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </div>
          </div>
          <div>
            <h2 className="text-3xl font-extrabold text-white drop-shadow-lg">
              Detection Workspace
            </h2>
            <p className="text-sm text-slate-300 mt-1 flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: '#b8a082' }}></span>
              AI-powered FOD detection system
            </p>
          </div>
        </div>
        {mediaLoaded && (
          <div className="flex items-center gap-2 px-5 py-2.5 bg-emerald-500/20 backdrop-blur-md border border-emerald-500/30 rounded-xl">
            <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
            <span className="text-sm font-semibold text-emerald-300">ACTIVE</span>
          </div>
        )}
      </div>

      {/* Input Mode Selector - Premium Design */}
      <div className="flex gap-3 glass-effect p-1.5 rounded-2xl w-fit animate-slide-up premium-shadow">
        <button
          onClick={() => onModeChange('video')}
          className={`px-7 py-3.5 rounded-xl font-bold transition-all duration-300 flex items-center gap-3 relative overflow-hidden ${
            inputMode === 'video'
              ? 'gradient-animated text-white shadow-2xl transform scale-105'
              : 'bg-white/5 text-slate-300 hover:bg-white/10 hover:text-white'
          }`}
        >
          {inputMode === 'video' && <div className="absolute inset-0 shimmer"></div>}
          <svg className="w-6 h-6 relative z-10 drop-shadow-lg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          <span className="relative z-10 text-lg">Video</span>
        </button>
        <button
          onClick={() => onModeChange('image')}
          className={`px-7 py-3.5 rounded-xl font-bold transition-all duration-300 flex items-center gap-3 relative overflow-hidden ${
            inputMode === 'image'
              ? 'gradient-animated text-white shadow-2xl transform scale-105'
              : 'bg-white/5 text-slate-300 hover:bg-white/10 hover:text-white'
          }`}
        >
          {inputMode === 'image' && <div className="absolute inset-0 shimmer"></div>}
          <svg className="w-6 h-6 relative z-10 drop-shadow-lg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <span className="relative z-10 text-lg">Image</span>
        </button>
      </div>

      {/* Action Buttons - Premium Design */}
      <div className="flex gap-4 animate-slide-up">
        {inputMode === 'video' ? (
          <>
            <button
              onClick={onUseCamera}
              className="px-8 py-4 text-white rounded-xl font-semibold shadow-lg transition-all duration-300 transform hover:scale-105 active:scale-95 flex items-center gap-3"
              style={{ backgroundColor: '#9d8166' }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#8b6f57'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#9d8166'}
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Use Camera
            </button>
            <button
              onClick={onUploadVideo}
              className="px-8 py-4 glass-effect text-white rounded-xl font-semibold border border-white/20 hover:bg-white/10 transition-all duration-300 transform hover:scale-105 active:scale-95 flex items-center gap-3"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              Upload Video
            </button>
          </>
        ) : (
          <button
            onClick={onUploadImage}
            className="px-8 py-4 text-white rounded-xl font-semibold shadow-lg transition-all duration-300 transform hover:scale-105 active:scale-95 flex items-center gap-3"
            style={{ backgroundColor: '#9d8166' }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#8b6f57'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#9d8166'}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            Upload Image
          </button>
        )}
      </div>

      {/* Detection Box - Premium Design */}
      <div className="glass-effect rounded-3xl premium-shadow-lg animate-scale-in border border-white/20 overflow-visible">
        <div className="relative bg-gradient-to-br from-slate-800/90 via-slate-800/80 to-slate-900/90 backdrop-blur-xl overflow-visible" style={{ height: '600px' }}>
          
          {/* AI Scan Effect - Only active during processing */}
          {mediaLoaded && <AIScanEffect isActive={externalIsProcessing} />}
          
          {/* AI Processing Indicator */}
          <AIProcessingIndicator isProcessing={externalIsProcessing} model="YOLOv8" />
          
          {!mediaLoaded ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center z-10">
              <div className="relative">
                {/* Glowing background effect */}
                <div className="absolute inset-0 rounded-full blur-3xl opacity-20 animate-pulse" style={{ backgroundColor: '#9d8166' }}></div>
                <div className="relative glass-effect rounded-3xl p-12 shadow-2xl border border-white/20">
                  <div className="flex flex-col items-center">
                    <div className="relative mb-8">
                      <div className="absolute inset-0 rounded-3xl blur-2xl opacity-30" style={{ backgroundColor: '#9d8166' }}></div>
                      <div className="relative w-40 h-40 rounded-3xl flex items-center justify-center shadow-2xl" style={{ backgroundColor: '#9d8166' }}>
                        <svg
                          className="w-20 h-20 text-white drop-shadow-2xl"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2.5}
                            d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
                          />
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2.5}
                            d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
                          />
                        </svg>
                      </div>
                    </div>
                    <p className="text-2xl font-extrabold text-white mb-3">
                      No media loaded yet
                    </p>
                    <p className="text-sm text-slate-300 text-center max-w-md">
                      Choose camera or upload a video/image to start FOD detection.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <>
              {/* Overlay Badge - Premium */}
              <div className="absolute top-6 left-6 z-20">
                <span className={`px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-2 backdrop-blur-md border ${
                  mediaSource === 'camera' 
                    ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' 
                    : ''
                }`} style={mediaSource !== 'camera' ? { backgroundColor: 'rgba(157, 129, 102, 0.2)', color: '#d4c4b0', borderColor: 'rgba(157, 129, 102, 0.3)' } : {}}>
                  {mediaSource === 'camera' ? (
                    <>
                      <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
                      LIVE PREVIEW
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                      UPLOADED FILE
                    </>
                  )}
                </span>
              </div>

              {/* Image/Video Display Area */}
              <div 
                ref={imageContainerRef}
                className="absolute inset-0 bg-gradient-to-br from-slate-700/50 via-slate-800/30 to-slate-800/50 flex items-center justify-center overflow-visible z-0"
                data-image-container
              >
                {videoUrl ? (
                  <div className="relative w-full h-full flex items-center justify-center" style={{ position: 'relative', width: '100%', height: '100%', minHeight: '500px' }}>
                    {videoError && (
                      <div className="absolute inset-0 flex items-center justify-center z-30 bg-red-900/30 backdrop-blur-md rounded-lg border-2 border-red-500/70 p-8 m-4">
                        <div className="text-center max-w-2xl">
                          <svg className="w-20 h-20 text-red-400 mx-auto mb-4 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <p className="text-red-300 font-bold text-xl mb-3">Format vidéo non supporté</p>
                          <p className="text-red-200 text-sm mb-4 leading-relaxed">{videoError}</p>
                          <div className="bg-red-900/40 rounded-lg p-4 mt-4 border border-red-500/30">
                            <p className="text-red-200 text-xs font-semibold mb-2">💡 Solution :</p>
                            <p className="text-red-300 text-xs leading-relaxed">
                              Convertissez votre vidéo en MP4 avec le codec <strong>H.264</strong> (vidéo) et <strong>AAC</strong> (audio).<br/>
                              Vous pouvez utiliser <strong>FFmpeg</strong> ou un convertisseur en ligne comme <strong>CloudConvert</strong>.
                            </p>
                            <p className="text-red-300 text-xs mt-2">
                              Commande FFmpeg : <code className="bg-red-950/50 px-2 py-1 rounded">ffmpeg -i input.mp4 -c:v libx264 -c:a aac output.mp4</code>
                            </p>
                          </div>
                        </div>
                      </div>
                    )}
                    <video
                      key={videoUrl}
                      ref={videoRef}
                      src={videoUrl}
                      className="w-full h-full"
                      style={{ 
                        width: '100%',
                        height: '100%',
                        objectFit: 'contain',
                        backgroundColor: '#000',
                        display: 'block',
                        position: 'relative',
                        zIndex: 1,
                        minHeight: '400px'
                      }}
                      controls
                      playsInline
                      preload="metadata"
                      autoPlay={false}
                      muted={false}
                      onTimeUpdate={(e) => {
                        if (onVideoTimeUpdate && e.currentTarget) {
                          const currentTime = e.currentTarget.currentTime;
                          onVideoTimeUpdate(currentTime);
                        }
                      }}
                      onPlay={() => setIsPlaying(true)}
                      onPause={() => setIsPlaying(false)}
                      onLoadedData={(e) => {
                        const video = e.currentTarget;
                        console.log('✅ Vidéo chargée (onLoadedData):', {
                          width: video.videoWidth,
                          height: video.videoHeight,
                          duration: video.duration,
                          src: video.src,
                          readyState: video.readyState
                        });
                      }}
                      onCanPlay={(e) => {
                        const video = e.currentTarget;
                        console.log('✅ Vidéo peut être lue (onCanPlay):', {
                          width: video.videoWidth,
                          height: video.videoHeight,
                          duration: video.duration,
                          readyState: video.readyState
                        });
                      }}
                      onError={(e) => {
                        const video = e.currentTarget;
                        const error = video.error;
                        if (error) {
                          const errorInfo = {
                            code: error.code,
                            message: error.message,
                            MEDIA_ERR_ABORTED: error.MEDIA_ERR_ABORTED,
                            MEDIA_ERR_NETWORK: error.MEDIA_ERR_NETWORK,
                            MEDIA_ERR_DECODE: error.MEDIA_ERR_DECODE,
                            MEDIA_ERR_SRC_NOT_SUPPORTED: error.MEDIA_ERR_SRC_NOT_SUPPORTED,
                            codeName: error.code === error.MEDIA_ERR_ABORTED ? 'MEDIA_ERR_ABORTED (1)' :
                                     error.code === error.MEDIA_ERR_NETWORK ? 'MEDIA_ERR_NETWORK (2)' :
                                     error.code === error.MEDIA_ERR_DECODE ? 'MEDIA_ERR_DECODE (3)' :
                                     error.code === error.MEDIA_ERR_SRC_NOT_SUPPORTED ? 'MEDIA_ERR_SRC_NOT_SUPPORTED (4)' : `UNKNOWN (${error.code})`
                          };
                          console.error('❌ Erreur lors du chargement de la vidéo:', {
                            error: errorInfo,
                            src: video.src,
                            networkState: video.networkState,
                            readyState: video.readyState,
                            currentSrc: video.currentSrc
                          });
                          
                          // Définir un message d'erreur pour l'utilisateur
                          let errorMessage = 'Erreur lors du chargement de la vidéo';
                          if (error.code === error.MEDIA_ERR_DECODE) {
                            errorMessage = 'Le format vidéo n\'est pas supporté ou le fichier est corrompu. Essayez avec un autre format (MP4 avec codec H.264 recommandé).';
                          } else if (error.code === error.MEDIA_ERR_SRC_NOT_SUPPORTED) {
                            errorMessage = 'Le format vidéo n\'est pas supporté par votre navigateur. Le fichier MP4 doit être encodé avec le codec H.264 (vidéo) et AAC (audio). Utilisez un outil comme FFmpeg pour convertir la vidéo.';
                          } else if (error.code === error.MEDIA_ERR_NETWORK) {
                            errorMessage = 'Erreur réseau lors du chargement de la vidéo.';
                          }
                          setVideoError(errorMessage);
                        } else {
                          console.error('❌ Erreur vidéo mais pas de détails disponibles');
                          setVideoError('Erreur lors du chargement de la vidéo');
                        }
                      }}
                      onLoadedMetadata={(e) => {
                        const video = e.currentTarget;
                        const container = video.parentElement;
                        if (!container) return;
                        
                        const containerWidth = container.clientWidth;
                        const containerHeight = container.clientHeight;
                        const naturalWidth = video.videoWidth;
                        const naturalHeight = video.videoHeight;
                        
                        const imageAspect = naturalWidth / naturalHeight;
                        const containerAspect = containerWidth / containerHeight;
                        
                        let displayedWidth: number;
                        let displayedHeight: number;
                        
                        if (imageAspect > containerAspect) {
                          displayedWidth = containerWidth;
                          displayedHeight = containerWidth / imageAspect;
                        } else {
                          displayedHeight = containerHeight;
                          displayedWidth = containerHeight * imageAspect;
                        }
                        
                        const offsetX = (containerWidth - displayedWidth) / 2;
                        const offsetY = (containerHeight - displayedHeight) / 2;
                        
                        setImageDisplayInfo({
                          naturalWidth,
                          naturalHeight,
                          displayedWidth,
                          displayedHeight,
                          offsetX,
                          offsetY,
                        });
                      }}
                    />
                  </div>
                ) : imageUrl ? (
                  <>
                    <img
                      src={imageUrl}
                      alt="Uploaded for detection"
                      className="w-full h-full object-contain z-0"
                      style={{ 
                        position: 'relative', 
                        zIndex: 0,
                        minWidth: '100%',
                        minHeight: '100%'
                      }}
                      onLoad={(e) => {
                        const img = e.currentTarget;
                        const container = img.parentElement;
                        if (!container) return;
                        
                        const containerWidth = container.clientWidth;
                        const containerHeight = container.clientHeight;
                        const naturalWidth = img.naturalWidth;
                        const naturalHeight = img.naturalHeight;
                        
                        const imageAspect = naturalWidth / naturalHeight;
                        const containerAspect = containerWidth / containerHeight;
                        
                        let displayedWidth: number;
                        let displayedHeight: number;
                        
                        if (imageAspect > containerAspect) {
                          displayedWidth = containerWidth;
                          displayedHeight = containerWidth / imageAspect;
                        } else {
                          displayedHeight = containerHeight;
                          displayedWidth = containerHeight * imageAspect;
                        }
                        
                        const offsetX = (containerWidth - displayedWidth) / 2;
                        const offsetY = (containerHeight - displayedHeight) / 2;
                        
                        setImageDisplayInfo({
                          naturalWidth,
                          naturalHeight,
                          displayedWidth,
                          displayedHeight,
                          offsetX,
                          offsetY,
                        });
                      }}
                    />
                  </>
                ) : (
                  <>
                    {/* Animated runway pattern (fallback) */}
                    <div className="absolute inset-0 opacity-30">
                      <div className="absolute top-1/2 left-0 right-0 h-1.5 bg-gradient-to-r from-transparent via-yellow-400 to-transparent transform -translate-y-1/2 shadow-lg shadow-yellow-400/50"></div>
                      <div className="absolute top-1/2 left-1/4 w-3 h-3 bg-white rounded-full transform -translate-y-1/2 -translate-x-1/2 shadow-lg animate-pulse"></div>
                      <div className="absolute top-1/2 left-1/2 w-3 h-3 bg-white rounded-full transform -translate-y-1/2 -translate-x-1/2 shadow-lg animate-pulse" style={{ animationDelay: '0.5s' }}></div>
                      <div className="absolute top-1/2 left-3/4 w-3 h-3 bg-white rounded-full transform -translate-y-1/2 -translate-x-1/2 shadow-lg animate-pulse" style={{ animationDelay: '1s' }}></div>
                    </div>
                    <div className="relative z-10 text-center glass-effect rounded-2xl p-8 shadow-xl border border-white/20">
                      <div className="relative mb-6">
                        <div className="absolute inset-0 rounded-2xl blur-xl opacity-30" style={{ backgroundColor: '#9d8166' }}></div>
                        <div className="relative w-24 h-24 rounded-2xl flex items-center justify-center mx-auto shadow-xl" style={{ backgroundColor: '#9d8166' }}>
                          <svg
                            className="w-12 h-12 text-white"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                            />
                          </svg>
                        </div>
                      </div>
                      <p className="text-xl font-bold text-white mb-2">
                        Runway View
                      </p>
                      <p className="text-sm text-slate-400 flex items-center justify-center gap-2">
                        <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
                        Detection overlay active
                      </p>
                    </div>
                  </>
                )}
              </div>

              {/* Detection Bounding Boxes - Premium Animated - Au-dessus de la vidéo */}
              {((videoUrl || imageUrl) && detections && detections.length > 0) && detections.map((detection, index) => {
                const riskColors = {
                  High: {
                    border: 'border-red-400',
                    bg: 'bg-red-500/30',
                    glow: 'shadow-red-500/60',
                    corner: 'bg-red-400',
                  },
                  Medium: {
                    border: 'border-yellow-400',
                    bg: 'bg-yellow-500/30',
                    glow: 'shadow-yellow-500/60',
                    corner: 'bg-yellow-400',
                  },
                  Low: {
                    border: 'border-emerald-400',
                    bg: 'bg-emerald-500/30',
                    glow: 'shadow-emerald-500/60',
                    corner: 'bg-emerald-400',
                  },
                };

                const colors = riskColors[detection.riskLevel];

                // Calculer la position réelle en fonction de l'image/vidéo affichée
                let boxStyle: React.CSSProperties;
                
                if (imageDisplayInfo && detection.bbox) {
                  // Convertir les pourcentages en pixels par rapport à l'image originale
                  const boxX = (detection.bbox.x / 100) * imageDisplayInfo.naturalWidth;
                  const boxY = (detection.bbox.y / 100) * imageDisplayInfo.naturalHeight;
                  const boxWidth = (detection.bbox.width / 100) * imageDisplayInfo.naturalWidth;
                  const boxHeight = (detection.bbox.height / 100) * imageDisplayInfo.naturalHeight;
                  
                  // Convertir en pixels par rapport à l'image affichée
                  const scaleX = imageDisplayInfo.displayedWidth / imageDisplayInfo.naturalWidth;
                  const scaleY = imageDisplayInfo.displayedHeight / imageDisplayInfo.naturalHeight;
                  
                  const displayedX = boxX * scaleX + imageDisplayInfo.offsetX;
                  const displayedY = boxY * scaleY + imageDisplayInfo.offsetY;
                  const displayedWidth = boxWidth * scaleX;
                  const displayedHeight = boxHeight * scaleY;
                  
                  boxStyle = {
                    left: `${displayedX}px`,
                    top: `${displayedY}px`,
                    width: `${displayedWidth}px`,
                    height: `${displayedHeight}px`,
                    animationDelay: `${index * 0.15}s`,
                    zIndex: 20,
                  };
                } else {
                  // Fallback: utiliser les pourcentages (ne fonctionnera pas bien avec object-contain)
                  boxStyle = {
                    left: `${detection.bbox.x}%`,
                    top: `${detection.bbox.y}%`,
                    width: `${detection.bbox.width}%`,
                    height: `${detection.bbox.height}%`,
                    animationDelay: `${index * 0.15}s`,
                    zIndex: 20,
                  };
                }

                // Déterminer la position du label (en haut ou en bas selon la position de la box)
                const boxTop = imageDisplayInfo && typeof boxStyle.top === 'string' && boxStyle.top.includes('px')
                  ? parseFloat(boxStyle.top.replace('px', ''))
                  : null;
                const showLabelAtBottom = boxTop !== null && boxTop < 80;

                return (
                  <div
                    key={detection.id}
                    className={`absolute border-2 ${colors.border} ${colors.bg} animate-scale-in shadow-2xl ${colors.glow} backdrop-blur-sm`}
                    style={{
                      ...boxStyle,
                      position: 'absolute',
                      pointerEvents: 'none',
                      zIndex: 10, // Au-dessus de la vidéo
                    }}
                  >
                    {/* Segmentation Mask Overlay - Affiché directement dans la bounding box */}
                    {detection.hasSegmentation && detection.segmentationMask && (
                      <img
                        src={`data:image/png;base64,${detection.segmentationMask}`}
                        alt="Segmentation"
                        className="absolute inset-0 w-full h-full object-cover pointer-events-none"
                        style={{ 
                          zIndex: 1,
                        }}
                      />
                    )}
                    {/* Animated corner indicators */}
                    <div className={`absolute -top-1.5 -left-1.5 w-4 h-4 ${colors.corner} rounded-full animate-pulse shadow-lg`}></div>
                    <div className={`absolute -top-1.5 -right-1.5 w-4 h-4 ${colors.corner} rounded-full animate-pulse shadow-lg`} style={{ animationDelay: '0.2s' }}></div>
                    <div className={`absolute -bottom-1.5 -left-1.5 w-4 h-4 ${colors.corner} rounded-full animate-pulse shadow-lg`} style={{ animationDelay: '0.4s' }}></div>
                    <div className={`absolute -bottom-1.5 -right-1.5 w-4 h-4 ${colors.corner} rounded-full animate-pulse shadow-lg`} style={{ animationDelay: '0.6s' }}></div>
                    
                    {/* Premium label avec alerte et taille - Position adaptative */}
                    <div 
                      className={`absolute left-0 glass-effect text-white px-4 py-2 rounded-xl text-xs font-bold whitespace-nowrap shadow-2xl border border-white/20 backdrop-blur-md z-30`}
                      style={{
                        ...(showLabelAtBottom 
                          ? { bottom: '-3.5rem' }
                          : { top: '-3.5rem' }
                        ),
                        pointerEvents: 'auto',
                        minWidth: 'max-content',
                      }}
                    >
                      <div className="flex flex-col gap-1">
                        <div className="flex items-center gap-2">
                          <span className="w-2 h-2 bg-white rounded-full animate-pulse shadow-lg"></span>
                          <span className="drop-shadow-lg">{detection.label}</span>
                          {detection.alertLevel && (
                            <span className={`px-2 py-0.5 rounded-lg text-[10px] font-extrabold border ${
                              detection.alertLevel === 3 
                                ? 'bg-red-600/80 text-white border-red-400 animate-pulse' 
                                : detection.alertLevel === 2
                                ? 'bg-orange-500/80 text-white border-orange-400'
                                : 'bg-green-500/80 text-white border-green-400'
                            }`}>
                              ALERTE {detection.alertLevel} - {detection.alertType}
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-2 text-[10px]">
                          <span className="px-2 py-0.5 bg-white/20 rounded-lg font-extrabold border border-white/30">
                            {detection.riskLevel} {(detection.confidence * 100).toFixed(0)}%
                          </span>
                          {detection.sizeCm !== undefined && (
                            <span className="px-2 py-0.5 bg-blue-500/30 rounded-lg font-semibold border border-blue-400/30">
                              Taille: {detection.sizeCm} cm ({detection.sizeMeters?.toFixed(3)} m)
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </>
          )}
        </div>
      </div>

      {/* Playback Controls (Video Mode Only) - Premium */}
      {inputMode === 'video' && mediaLoaded && (
        <div className="glass-effect rounded-2xl premium-shadow-lg border border-white/20 p-5 animate-slide-up backdrop-blur-md">
          <div className="flex items-center gap-5">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="w-12 h-12 flex items-center justify-center text-white rounded-xl transition-all duration-300 shadow-lg transform hover:scale-105 active:scale-95"
              style={{ backgroundColor: '#9d8166' }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#8b6f57'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#9d8166'}
            >
              {isPlaying ? (
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z"
                    clipRule="evenodd"
                  />
                </svg>
              ) : (
                <svg className="w-6 h-6 ml-1" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
            </button>
            <div className="flex-1">
              <div className="w-full h-3 glass-effect rounded-full overflow-hidden border border-white/10">
                <div
                  className="h-full transition-all duration-300 relative"
                  style={{ width: '24.8%', backgroundColor: '#9d8166' }}
                >
                  <div className="absolute right-0 top-0 bottom-0 w-1 bg-white"></div>
                </div>
              </div>
            </div>
            <div className="text-sm text-white whitespace-nowrap font-semibold flex items-center gap-3">
              <span className="px-2 py-1 rounded-lg text-xs font-semibold border" style={{ backgroundColor: 'rgba(157, 129, 102, 0.2)', color: '#d4c4b0', borderColor: 'rgba(157, 129, 102, 0.3)' }}>
                AI
              </span>
              <span className="text-slate-300">Frame 124 / 500</span>
              <span className="text-slate-500">·</span>
              <span className="text-emerald-400 font-semibold">~25 FPS</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DetectionWorkspace;

