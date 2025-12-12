export type InputMode = 'video' | 'image';

export type MediaSource = 'camera' | 'upload' | null;

export type RiskLevel = 'Low' | 'Medium' | 'High';

export interface Detection {
  id: string;
  trackId?: number; // ID de tracking pour maintenir la continuité entre les frames
  label: string;
  confidence: number;
  riskLevel: RiskLevel;
  alertLevel?: number; // 1, 2, ou 3
  alertType?: string; // "NORMAL", "ATTENTION", "DANGER"
  sizeMeters?: number;
  sizeCm?: number;
  position: string;
  bbox: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  hasSegmentation?: boolean;
  segmentationMask?: string; // Base64 image
}

export interface ModelInfo {
  name: string;
  mode: string;
  tags: string[];
}

