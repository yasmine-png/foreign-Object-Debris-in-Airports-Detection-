import React, { useState, useRef, useEffect } from 'react';
import Header from './components/Header';
import DetectionWorkspace from './components/DetectionWorkspace';
import ResultsPanel from './components/ResultsPanel';
import ProcessingOverlay from './components/ProcessingOverlay';
import type { InputMode, MediaSource, Detection, ModelInfo } from './types';
import { detectObjects, detectVideo, type VideoDetectionResponse } from './services/api';

const mockModelInfo: ModelInfo = {
  name: 'YOLOv8 FOD Detection',
  mode: 'Supervised detection / Object Detection',
  tags: ['Real time ready', 'YOLOv8n', 'FOD Detection'],
};

function App() {
  const [inputMode, setInputMode] = useState<InputMode>('image');
  const [mediaLoaded, setMediaLoaded] = useState(false);
  const [mediaSource, setMediaSource] = useState<MediaSource>(null);
  const [detections, setDetections] = useState<Detection[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [hasDangerAlert, setHasDangerAlert] = useState(false);
  const [videoDetections, setVideoDetections] = useState<VideoDetectionResponse | null>(null);
  const [currentVideoTime, setCurrentVideoTime] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoInputRef = useRef<HTMLInputElement>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const videoUrlRef = useRef<string | null>(null);

  const handleUseCamera = () => {
    // TODO: Implémenter l'accès à la caméra
    setError('Fonctionnalité caméra à venir');
  };

  const handleUploadVideo = async () => {
    videoInputRef.current?.click();
  };

  const handleVideoChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('video/')) {
      setError('Veuillez sélectionner un fichier vidéo');
      return;
    }

    // Nettoyer l'ancienne URL blob si elle existe
    if (videoUrlRef.current) {
      console.log('🧹 Nettoyage de l\'ancienne URL blob:', videoUrlRef.current);
      URL.revokeObjectURL(videoUrlRef.current);
      videoUrlRef.current = null;
    }

    // Réinitialiser l'état
    setImageUrl(null);
    setDetections([]);
    setError(null);
    setVideoDetections(null);
    setHasDangerAlert(false);
    setCurrentVideoTime(0);
    setVideoUrl(null);
    setMediaLoaded(false);

    try {
      // Vérifier que le fichier est valide
      if (file.size === 0) {
        setError('Le fichier vidéo est vide');
        return;
      }
      
      // Vérifier le type MIME
      const supportedTypes = ['video/mp4', 'video/webm', 'video/ogg', 'video/quicktime'];
      const isSupportedType = supportedTypes.some(type => file.type.includes(type.split('/')[1]));
      
      if (!file.type.startsWith('video/')) {
        setError('Le fichier sélectionné n\'est pas une vidéo');
        return;
      }
      
      // Créer une URL pour afficher la vidéo IMMÉDIATEMENT
      const url = URL.createObjectURL(file);
      videoUrlRef.current = url;
      console.log('📹 URL vidéo créée:', url);
      console.log('📹 Fichier vidéo:', {
        name: file.name,
        type: file.type,
        size: file.size,
        lastModified: new Date(file.lastModified).toISOString(),
        isSupportedType: isSupportedType
      });
      
      // Vérifier que l'URL blob est valide
      if (!url || !url.startsWith('blob:')) {
        setError('Erreur lors de la création de l\'URL de la vidéo');
        return;
      }
      
      // Afficher la vidéo IMMÉDIATEMENT avant le traitement
      setVideoUrl(url);
      setMediaLoaded(true);
      setMediaSource('upload');
      
      console.log('✅ État mis à jour: videoUrl et mediaLoaded définis');
      
      // Avertissement si le type n'est pas dans la liste des types supportés
      if (!isSupportedType) {
        console.warn('⚠️ Type de fichier non standard:', file.type, '- Le navigateur pourrait ne pas le supporter');
      }

      // Traiter la vidéo en arrière-plan
      setIsProcessing(true);
      console.log('📹 Envoi de la vidéo pour traitement...');
      const response = await detectVideo(file);
      
      setVideoDetections(response);
      console.log(`✅ Vidéo traitée: ${response.totalFrames} frames, ${response.duration.toFixed(1)}s`);
      console.log(`📊 Frames avec détections: ${response.frames.length}`);

      // Ne pas afficher toutes les détections en même temps
      // Les détections seront affichées selon le temps de la vidéo (frame par frame)
      setVideoDetections(response);
      
      // Initialiser avec les détections de la première frame
      if (response.frames.length > 0) {
        const firstFrameDetections = response.frames[0]?.detections || [];
        setDetections(firstFrameDetections);
        console.log(`🎯 Détections initiales (frame 0): ${firstFrameDetections.length}`);
      }

      if (response.hasDangerAlert) {
        setHasDangerAlert(true);
        playDangerAlarm();
      }
    } catch (err) {
      console.error('Erreur lors du traitement vidéo:', err);
      setError(err instanceof Error ? err.message : 'Erreur lors du traitement de la vidéo');
      // Nettoyer l'URL blob en cas d'erreur
      if (videoUrlRef.current) {
        URL.revokeObjectURL(videoUrlRef.current);
        videoUrlRef.current = null;
      }
      setVideoUrl(null);
      setMediaLoaded(false);
    } finally {
      setIsProcessing(false);
      // Réinitialiser l'input
      if (videoInputRef.current) {
        videoInputRef.current.value = '';
      }
    }
  };

  const getDetectionsAtTime = (time: number): Detection[] => {
    if (!videoDetections || !videoDetections.frames || videoDetections.frames.length === 0) return [];
    
    // Trouver la frame exacte correspondant au temps donné
    const targetFrame = Math.round(time * videoDetections.fps);
    
    // Chercher la frame exacte
    let frameData = videoDetections.frames.find(f => f.frame === targetFrame);
    
    // Si pas trouvé exactement, chercher la frame la plus proche
    if (!frameData) {
      frameData = videoDetections.frames.reduce((closest, current) => {
        const closestDiff = Math.abs(closest.frame - targetFrame);
        const currentDiff = Math.abs(current.frame - targetFrame);
        return currentDiff < closestDiff ? current : closest;
      });
    }
    
    if (!frameData) return [];
    
    // Retourner les détections de la frame (déjà interpolées par le backend)
    // Les trackId garantissent que les mêmes objets sont suivis entre les frames
    return frameData.detections || [];
  };

  // Afficher les détections selon le temps actuel de la vidéo
  // Avec tracking YOLO : les boxes suivent les objets et restent fixes sur eux
  React.useEffect(() => {
    if (videoUrl && videoDetections && videoDetections.frames && videoDetections.frames.length > 0) {
      const currentDetections = getDetectionsAtTime(currentVideoTime);
      
      // Compter les objets trackés uniques
      const trackedObjects = new Set(currentDetections.filter(d => d.trackId !== undefined).map(d => d.trackId));
      
      if (trackedObjects.size > 0) {
        console.log(`⏱️ Time: ${currentVideoTime.toFixed(2)}s - Détections: ${currentDetections.length} (${trackedObjects.size} objets trackés)`);
      } else {
        console.log(`⏱️ Time: ${currentVideoTime.toFixed(2)}s - Détections: ${currentDetections.length}`);
      }
      
      setDetections(currentDetections);
      
      const hasAlert = currentDetections.some(d => d.alertLevel === 3);
      if (hasAlert && !hasDangerAlert) {
        setHasDangerAlert(true);
      }
    }
  }, [currentVideoTime, videoUrl, videoDetections, hasDangerAlert]);

  // Nettoyer les URLs blob lors du démontage du composant
  useEffect(() => {
    return () => {
      if (videoUrlRef.current) {
        console.log('🧹 Nettoyage de l\'URL blob au démontage:', videoUrlRef.current);
        URL.revokeObjectURL(videoUrlRef.current);
        videoUrlRef.current = null;
      }
      if (imageUrl) {
        URL.revokeObjectURL(imageUrl);
      }
    };
  }, [imageUrl]);

  const handleUploadImage = () => {
    fileInputRef.current?.click();
  };

  // Fonction pour jouer l'alarme de danger
  const playDangerAlarm = () => {
    try {
      // Créer un contexte audio pour générer un son d'alarme
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      // Son d'alarme strident (fréquence élevée)
      oscillator.frequency.value = 800;
      oscillator.type = 'sine';
      
      gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
      
      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.5);
      
      // Répéter 3 fois
      setTimeout(() => {
        const osc2 = audioContext.createOscillator();
        const gain2 = audioContext.createGain();
        osc2.connect(gain2);
        gain2.connect(audioContext.destination);
        osc2.frequency.value = 800;
        osc2.type = 'sine';
        gain2.gain.setValueAtTime(0.3, audioContext.currentTime);
        gain2.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
        osc2.start(audioContext.currentTime);
        osc2.stop(audioContext.currentTime + 0.5);
      }, 600);
      
      setTimeout(() => {
        const osc3 = audioContext.createOscillator();
        const gain3 = audioContext.createGain();
        osc3.connect(gain3);
        gain3.connect(audioContext.destination);
        osc3.frequency.value = 800;
        osc3.type = 'sine';
        gain3.gain.setValueAtTime(0.3, audioContext.currentTime);
        gain3.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
        osc3.start(audioContext.currentTime);
        osc3.stop(audioContext.currentTime + 0.5);
      }, 1200);
    } catch (e) {
      console.error('Erreur lors de la lecture de l\'alarme:', e);
    }
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Vérifier que c'est une image
    if (!file.type.startsWith('image/')) {
      setError('Veuillez sélectionner un fichier image');
      return;
    }

    setError(null);
    setDetections([]);
    
    // Créer une URL pour afficher l'image IMMÉDIATEMENT
    const url = URL.createObjectURL(file);
    setImageUrl(url);
    setMediaLoaded(true);
    setMediaSource('upload');
    
    // Ensuite démarrer le traitement
    setIsProcessing(true);

    try {
      // Envoyer l'image au backend pour détection
      const response = await detectObjects(file);
      setDetections(response.detections);
      
      // Vérifier les alertes de danger
      if (response.hasDangerAlert) {
        setHasDangerAlert(true);
        // Jouer l'alarme sonore
        playDangerAlarm();
      } else {
        setHasDangerAlert(false);
      }
    } catch (err) {
      console.error('Erreur lors de la détection:', err);
      setError(err instanceof Error ? err.message : 'Erreur lors de la détection');
      setMediaLoaded(false);
      setImageUrl(null);
    } finally {
      setIsProcessing(false);
      // Réinitialiser l'input pour permettre de sélectionner le même fichier
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 relative overflow-hidden">
      {/* Overlay de chargement */}
      <ProcessingOverlay 
        isProcessing={isProcessing} 
        message="Please wait until we finish, don't click anything"
      />
      
      {/* Subtle background elements - Elegant Nude */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary-600/15 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-float"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-beige-500/15 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-float" style={{ animationDelay: '3s' }}></div>
      </div>
      
      <Header />
      <main className="container mx-auto px-6 py-8 relative z-10">
        {/* Alerte de danger */}
        {hasDangerAlert && (
          <div className="mb-4 p-4 bg-red-600/30 border-2 border-red-500 rounded-xl text-white animate-pulse">
            <div className="flex items-center gap-3">
              <svg className="w-6 h-6 text-red-400 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
                <div>
                  <div className="font-bold text-lg">🚨 ALERTE DANGER - ALERTE 3 🚨</div>
                  <div className="text-sm text-red-200">Objet de grande taille détecté (&gt; 10cm) - Danger critique!</div>
                </div>
            </div>
          </div>
        )}

        {/* Message d'erreur */}
        {error && (
          <div className="mb-4 p-4 bg-red-500/20 border border-red-500/30 rounded-xl text-red-300">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{error}</span>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_0.4fr] gap-8 mb-8">
          {/* Left Column - Detection Workspace */}
          <div>
            <DetectionWorkspace
              inputMode={inputMode}
              onModeChange={setInputMode}
              mediaLoaded={mediaLoaded}
              mediaSource={mediaSource}
              detections={detections}
              isProcessing={isProcessing}
              imageUrl={imageUrl}
              videoUrl={videoUrl}
              onVideoTimeUpdate={setCurrentVideoTime}
              onUseCamera={handleUseCamera}
              onUploadVideo={handleUploadVideo}
              onUploadImage={handleUploadImage}
            />
          </div>

          {/* Right Column - Results Panel */}
          <div>
            <ResultsPanel 
              detections={detections} 
              modelInfo={mockModelInfo}
              mediaType={inputMode}
              filename={inputMode === 'image' ? fileInputRef.current?.files?.[0]?.name : videoInputRef.current?.files?.[0]?.name}
              imageSize={imageUrl ? { width: 0, height: 0 } : undefined}
              videoFrames={videoDetections?.frames}
              videoInfo={videoDetections ? {
                fps: videoDetections.fps,
                duration: videoDetections.duration,
                totalFrames: videoDetections.totalFrames
              } : undefined}
            />
          </div>
        </div>

        {/* Input files cachés */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="hidden"
        />
        <input
          ref={videoInputRef}
          type="file"
          accept="video/*"
          onChange={handleVideoChange}
          className="hidden"
        />
      </main>
    </div>
  );
}

export default App;

