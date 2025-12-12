import type { Detection } from '../types';

// Configuration pour utiliser le backend local
const API_BASE_URL = 'http://localhost:5000/api';

export interface DetectionResponse {
  detections: Detection[];
  count: number;
  hasDangerAlert?: boolean;
  maxAlertLevel?: number;
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  sam_available?: boolean;
  current_model_type?: string;
  onnx_available?: boolean;
}

export interface ModelInfo {
  modelType: string;
  yolo_available: boolean;
  onnx_available: boolean;
  onnx_loaded?: boolean;
}

export interface SwitchModelResponse {
  success: boolean;
  message: string;
  modelType: string;
  providers?: string[];
}

export interface VideoDetectionResponse {
  frames: FrameDetection[];
  totalFrames: number;
  fps: number;
  duration: number;
  hasDangerAlert?: boolean;
  maxAlertLevel?: number;
}

export interface FrameDetection {
  frame: number;
  time: number;
  detections: Detection[];
  count: number;
}

/**
 * Vérifie que le backend est accessible et que le modèle est chargé
 */
export async function checkHealth(): Promise<HealthResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) {
      throw new Error('Backend non accessible');
    }
    return await response.json();
  } catch (error) {
    console.error('Erreur lors de la vérification du backend:', error);
    throw error;
  }
}

/**
 * Envoie une image au backend pour détection
 */
export async function detectObjects(imageFile: File): Promise<DetectionResponse> {
  try {
    const formData = new FormData();
    formData.append('image', imageFile);

    const response = await fetch(`${API_BASE_URL}/detect`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Erreur inconnue' }));
      throw new Error(errorData.error || `Erreur HTTP: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Erreur lors de la détection:', error);
    throw error;
  }
}

/**
 * Envoie une vidéo au backend pour détection frame par frame
 */
export async function detectVideo(videoFile: File): Promise<VideoDetectionResponse & { mongoId?: string }> {
  try {
    const formData = new FormData();
    formData.append('video', videoFile);

    const response = await fetch(`${API_BASE_URL}/detect-video`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Erreur inconnue' }));
      throw new Error(errorData.error || `Erreur HTTP: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Erreur lors de la détection vidéo:', error);
    throw error;
  }
}

/**
 * Exporte les détections en CSV
 */
export async function exportToCSV(detections: Detection[]): Promise<Blob> {
  try {
    const response = await fetch(`${API_BASE_URL}/export-csv`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ detections }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Erreur inconnue' }));
      throw new Error(errorData.error || `Erreur HTTP: ${response.status}`);
    }

    return await response.blob();
  } catch (error) {
    console.error('Erreur lors de l\'export CSV:', error);
    throw error;
  }
}

/**
 * Exporte les détections vers MongoDB
 */
export async function exportToMongoDB(data: {
  detections: Detection[];
  mediaType: 'image' | 'video';
  filename?: string;
  imageSize?: { width: number; height: number };
  frames?: FrameDetection[];
  videoInfo?: { fps: number; duration: number; totalFrames: number };
  metadata?: Record<string, any>;
}): Promise<{ success: boolean; message: string; mongoId?: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/export-mongodb`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Erreur inconnue' }));
      throw new Error(errorData.error || `Erreur HTTP: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Erreur lors de l\'export MongoDB:', error);
    throw error;
  }
}

/**
 * Obtient le modèle actuellement utilisé
 */
export async function getCurrentModel(): Promise<ModelInfo> {
  try {
    const response = await fetch(`${API_BASE_URL}/model/current`);
    if (!response.ok) {
      throw new Error('Erreur lors de la récupération du modèle');
    }
    return await response.json();
  } catch (error) {
    console.error('Erreur lors de la récupération du modèle:', error);
    throw error;
  }
}

/**
 * Change le modèle utilisé (YOLO ou ONNX)
 */
export async function switchModel(modelType: 'yolo' | 'onnx'): Promise<SwitchModelResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/model/switch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ modelType }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Erreur inconnue' }));
      throw new Error(errorData.error || `Erreur HTTP: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Erreur lors du changement de modèle:', error);
    throw error;
  }
}

