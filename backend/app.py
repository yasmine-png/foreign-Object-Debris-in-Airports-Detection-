from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import numpy as np
from PIL import Image
import io
import os
from pathlib import Path
import torch
import cv2
import base64
import json
import tempfile
import time

# Import SAM (Segment Anything Model) - optionnel
try:
    from segment_anything import sam_model_registry, SamPredictor
    SAM_AVAILABLE = True
except ImportError:
    SAM_AVAILABLE = False
    print("⚠️ segment-anything non installé. La segmentation ne sera pas disponible.")

# Fix pour PyTorch 2.6+ : permettre le chargement des modèles ultralytics
try:
    from ultralytics.nn.tasks import DetectionModel
    torch.serialization.add_safe_globals([DetectionModel])
except:
    pass

from ultralytics import YOLO

# Import MongoDB Service
MONGODB_AVAILABLE = False
mongodb_service = None

print("=" * 60)
print("🔌 INITIALISATION MONGODB")
print("=" * 60)

try:
    # Essayer d'abord avec import relatif (si on est dans le dossier backend)
    try:
        print("📦 Tentative d'import: from mongodb_service import mongodb_service")
        from mongodb_service import mongodb_service
        print("✅ Import réussi avec import relatif")
    except ImportError as e1:
        print(f"⚠️ Import relatif échoué: {e1}")
        # Sinon essayer avec backend. (si on est à la racine)
        try:
            print("📦 Tentative d'import: from backend.mongodb_service import mongodb_service")
            from backend.mongodb_service import mongodb_service
            print("✅ Import réussi avec import absolu")
        except ImportError as e2:
            print(f"❌ Import absolu échoué: {e2}")
            raise ImportError(f"Impossible d'importer mongodb_service. Erreurs: {e1}, {e2}")
    
    # Le service est disponible même si pas connecté (on pourra reconnecter plus tard)
    if mongodb_service:
        MONGODB_AVAILABLE = True
        print(f"✅ MongoDB service importé: {type(mongodb_service)}")
        # IMPORTANT: Ne pas utiliser if collection directement (pymongo ne supporte pas)
        if mongodb_service.collection is not None:
            print("✅ MongoDB service disponible et connecté")
        else:
            print("⚠️ MongoDB service disponible mais non connecté (tentative de reconnexion à l'export)")
    else:
        print("❌ MongoDB service est None après import")
        MONGODB_AVAILABLE = False
except ImportError as e:
    MONGODB_AVAILABLE = False
    print(f"❌ Erreur import MongoDB: {e}")
    print("⚠️ Installez pymongo: pip install pymongo python-dotenv")
    print("⚠️ Vérifiez que le fichier mongodb_service.py existe dans le dossier backend")
    mongodb_service = None
except Exception as e:
    MONGODB_AVAILABLE = False
    print(f"❌ Erreur lors de l'initialisation MongoDB: {e}")
    print(f"   Type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    mongodb_service = None

print("=" * 60)

# Import supervision pour DetectionsSmoother et MaskAnnotator
try:
    import supervision as sv
    from supervision.tools.detections import Detections, BoxAnnotator, MaskAnnotator
    from supervision.tracker.byte_tracker import ByteTracker
    from supervision.utils.video import VideoInfo
    SUPERVISION_AVAILABLE = True
except ImportError:
    SUPERVISION_AVAILABLE = False
    print("⚠️ supervision non installé. Installation recommandée pour meilleures performances.")
    print("   pip install supervision>=0.18.0")

app = Flask(__name__)
# Configuration de la taille maximale des fichiers uploadés (500 MB)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB
# Configuration CORS complète pour éviter les erreurs
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    },
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Chemin vers le modèle pré-entraîné (relatif au dossier backend)
# Remonte d'un niveau depuis backend/ pour accéder à la racine du projet
BASE_DIR = Path(__file__).parent.parent
MODEL_PATH = BASE_DIR / "yolov8n_fod_final_v7" / "weights" / "best.pt"

# Si le chemin relatif ne fonctionne pas, utiliser le chemin absolu en fallback
if not MODEL_PATH.exists():
    MODEL_PATH = Path(r"C:\Users\ybouk\OneDrive\Bureau\projet_fod\yolov8n_fod_final_v7\weights\best.pt")

# Chemin vers le modèle auto-encoder pour détection d'anomalies
AUTOENCODER_PATH = Path(__file__).parent / "autoencoder_fod.pth"

# Chemin vers le modèle ONNX
ONNX_MODEL_PATH = Path(__file__).parent / "best.onnx"

# Variable globale pour le type de modèle actuel ('yolo' ou 'onnx')
current_model_type = 'yolo'  # Par défaut: YOLO
onnx_session = None

# Variable globale pour le type de modèle actuel ('yolo' ou 'onnx')
current_model_type = 'yolo'  # Par défaut: YOLO
onnx_model = None
onnx_session = None

        # Charger le modèle une seule fois au démarrage
print("=" * 60)
print("🚀 DÉMARRAGE DU SERVEUR FOD DETECTION")
print("=" * 60)
print(f"📁 Chemin du modèle: {MODEL_PATH}")
print(f"✅ Fichier existe: {MODEL_PATH.exists()}")
# Vérifier la disponibilité du GPU
device_info = 'CUDA (GPU)' if torch.cuda.is_available() else 'CPU'
if torch.cuda.is_available():
    print(f"🚀 GPU disponible: {torch.cuda.get_device_name(0)}")
    print(f"💾 Mémoire GPU: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
else:
    print(f"⚠️  GPU non disponible - utilisation du CPU (plus lent)")
print(f"⚡ Device par défaut: {device_info}")

if not MODEL_PATH.exists():
    print(f"❌ ERREUR: Le fichier modèle n'existe pas à: {MODEL_PATH}")
    print("Veuillez vérifier le chemin du modèle dans app.py")
    model = None
else:
    try:
        print("⏳ Chargement du modèle YOLOv8...")
        # Fix pour PyTorch 2.6+ : désactiver weights_only pour le chargement
        import torch.serialization
        original_load = torch.load
        def patched_load(*args, **kwargs):
            kwargs.setdefault('weights_only', False)
            return original_load(*args, **kwargs)
        torch.load = patched_load
        
        model = YOLO(str(MODEL_PATH))
        
        # Restaurer le torch.load original
        torch.load = original_load
        
        print("✅ Modèle chargé avec succès!")
        print(f"📊 Classes détectables: {list(model.names.values())}")
    except Exception as e:
        print(f"❌ Erreur lors du chargement du modèle: {e}")
        import traceback
        traceback.print_exc()
        model = None

print("=" * 60)

# Charger SAM si disponible
sam_model = None
sam_predictor = None
if SAM_AVAILABLE:
    try:
        # Chercher le modèle SAM d'abord dans backend/, puis à la racine
        SAM_CHECKPOINT_PATH = Path(__file__).parent / "sam_vit_b_01ec64.pth"
        if not SAM_CHECKPOINT_PATH.exists():
            SAM_CHECKPOINT_PATH = BASE_DIR / "sam_vit_b_01ec64.pth"
        if not SAM_CHECKPOINT_PATH.exists():
            # Télécharger le modèle si nécessaire
            print("⚠️ Modèle SAM non trouvé. Téléchargez-le depuis:")
            print("https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth")
            print(f"Et placez-le dans: {SAM_CHECKPOINT_PATH}")
        else:
            print("⏳ Chargement du modèle SAM...")
            sam_model = sam_model_registry["vit_b"](checkpoint=str(SAM_CHECKPOINT_PATH))
            sam_predictor = SamPredictor(sam_model)
            print("✅ Modèle SAM chargé avec succès!")
    except Exception as e:
        print(f"⚠️ Erreur lors du chargement de SAM: {e}")
        sam_predictor = None

print("=" * 60)

# Charger le modèle auto-encoder pour détection d'anomalies
autoencoder_model = None
AUTOENCODER_AVAILABLE = False

if AUTOENCODER_PATH.exists():
    try:
        print("⏳ Chargement du modèle auto-encoder pour détection d'anomalies...")
        device_ae = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Charger le checkpoint
        checkpoint = torch.load(str(AUTOENCODER_PATH), map_location=device_ae, weights_only=False)
        
        # Gérer différents formats de sauvegarde
        if isinstance(checkpoint, dict):
            if 'model' in checkpoint:
                autoencoder_model = checkpoint['model']
            elif 'state_dict' in checkpoint:
                # Si seulement state_dict, on stocke le checkpoint pour utilisation ultérieure
                autoencoder_model = checkpoint
            else:
                autoencoder_model = checkpoint
        else:
            autoencoder_model = checkpoint
        
        # Mettre en mode évaluation si c'est un modèle
        if isinstance(autoencoder_model, torch.nn.Module):
            autoencoder_model.eval()
            autoencoder_model = autoencoder_model.to(device_ae)
        elif isinstance(autoencoder_model, dict) and 'model' in autoencoder_model:
            if isinstance(autoencoder_model['model'], torch.nn.Module):
                autoencoder_model['model'].eval()
                autoencoder_model['model'] = autoencoder_model['model'].to(device_ae)
        
        AUTOENCODER_AVAILABLE = True
        print(f"✅ Modèle auto-encoder chargé avec succès sur {device_ae.upper()}")
    except Exception as e:
        print(f"⚠️ Erreur lors du chargement de l'auto-encoder: {e}")
        import traceback
        traceback.print_exc()
        autoencoder_model = None
        AUTOENCODER_AVAILABLE = False
else:
    print(f"⚠️ Modèle auto-encoder non trouvé à: {AUTOENCODER_PATH}")
    print("   La détection d'anomalies ne sera pas disponible")

print("=" * 60)

# Utiliser DetectionsSmoother de supervision si disponible, sinon utiliser notre implémentation
if SUPERVISION_AVAILABLE:
    print("✅ Supervision disponible - utilisation de DetectionsSmoother professionnel")
else:
    print("⚠️ Supervision non disponible - utilisation du smoother personnalisé")
    class BBoxSmoother:
        """
        Smoother pour réduire le jitter des bounding boxes avec tracking
        Utilise un filtre exponentiel pour lisser les positions
        """
        def __init__(self, alpha=0.7, max_age=5):
            """
            alpha: facteur de lissage (0-1), plus proche de 1 = moins de lissage
            max_age: nombre de frames sans détection avant suppression
            """
            self.alpha = alpha
            self.max_age = max_age
            self.tracks = {}  # {track_id: {'bbox': [...], 'age': 0, 'last_frame': 0}}
        
        def update(self, track_id, bbox, frame_number):
            """
            Met à jour ou crée une track avec lissage
            bbox: {'x': float, 'y': float, 'width': float, 'height': float}
            """
            if track_id not in self.tracks:
                # Nouvelle détection
                self.tracks[track_id] = {
                    'bbox': bbox.copy(),
                    'age': 0,
                    'last_frame': frame_number
                }
                return bbox.copy()
            else:
                # Mise à jour avec lissage exponentiel
                old_bbox = self.tracks[track_id]['bbox']
                smoothed_bbox = {
                    'x': self.alpha * bbox['x'] + (1 - self.alpha) * old_bbox['x'],
                    'y': self.alpha * bbox['y'] + (1 - self.alpha) * old_bbox['y'],
                    'width': self.alpha * bbox['width'] + (1 - self.alpha) * old_bbox['width'],
                    'height': self.alpha * bbox['height'] + (1 - self.alpha) * old_bbox['height']
                }
                self.tracks[track_id]['bbox'] = smoothed_bbox
                self.tracks[track_id]['age'] = 0
                self.tracks[track_id]['last_frame'] = frame_number
                return smoothed_bbox
        
        def get_active_tracks(self, current_frame):
            """
            Retourne les tracks actives (non expirées)
            """
            active = {}
            for track_id, track_data in self.tracks.items():
                frames_since_last = current_frame - track_data['last_frame']
                if frames_since_last <= self.max_age:
                    active[track_id] = track_data
            return active
        
        def cleanup(self, current_frame):
            """
            Supprime les tracks expirées
            """
            expired = []
            for track_id, track_data in self.tracks.items():
                frames_since_last = current_frame - track_data['last_frame']
                if frames_since_last > self.max_age:
                    expired.append(track_id)
            
            for track_id in expired:
                del self.tracks[track_id]
            
            return len(expired)

def calculate_real_size(bbox_width_px: float, bbox_height_px: float, img_width: int, img_height: int, mask_area_px: float = None) -> float:
    """
    Calcule la taille réelle de l'objet en mètres
    Utilise la segmentation si disponible (plus précis), sinon utilise la bounding box
    
    Args:
        bbox_width_px: Largeur de la bounding box en pixels
        bbox_height_px: Hauteur de la bounding box en pixels
        img_width: Largeur de l'image en pixels
        img_height: Hauteur de l'image en pixels
        mask_area_px: Surface du masque en pixels (si segmentation disponible)
    
    Returns:
        Taille réelle en mètres
    """
    # Estimation réaliste : pour une caméra de surveillance aéroportuaire
    # La largeur de l'image représente généralement 3-5 mètres de piste (pas 50m!)
    # Cette estimation est plus réaliste pour des objets FOD (quelques cm)
    PISTE_WIDTH_METERS = 3.0  # 3 mètres au lieu de 50m (beaucoup plus réaliste)
    
    # Si on a la segmentation, utiliser la surface du masque (plus précis)
    if mask_area_px is not None and mask_area_px > 0:
        # Calculer le diamètre équivalent basé sur la surface
        # Surface = π * (diamètre/2)², donc diamètre = 2 * sqrt(surface / π)
        import math
        equivalent_diameter_px = 2 * math.sqrt(mask_area_px / math.pi)
        size_px = equivalent_diameter_px
    else:
        # Sinon, utiliser la moyenne de la largeur et hauteur de la bbox
        # (plus précis que max pour des objets non carrés)
        size_px = (bbox_width_px + bbox_height_px) / 2.0
    
    # Convertir en mètres (basé sur la largeur de l'image)
    # Utiliser la moyenne de largeur/hauteur de l'image pour être plus précis
    img_size_avg = (img_width + img_height) / 2.0
    size_meters = (size_px / img_size_avg) * PISTE_WIDTH_METERS
    
    # Limiter à une taille maximale réaliste (pas plus de 30cm pour un FOD)
    size_meters = min(size_meters, 0.30)
    
    return size_meters

def determine_risk_level_by_size(size_meters: float, confidence: float) -> dict:
    """
    Détermine le niveau de risque basé sur la taille réelle de l'objet
    
    Alerte 3 (Danger) : > 10cm (0.1m) - Objet de grande taille, danger critique
    Alerte 2 (Moyen) : 5-10cm (0.05-0.1m) - Objet moyen, attention requise
    Alerte 1 (Normal) : < 5cm (< 0.05m) - Petite taille, risque faible
    
    Returns:
        dict avec 'level', 'alert', 'size_meters', 'size_cm'
    """
    size_cm = size_meters * 100
    
    if size_meters > 0.10:  # > 10cm
        alert_level = 3
        risk = "High"
        alert_type = "DANGER"
    elif size_meters >= 0.05:  # 5-10cm
        alert_level = 2
        risk = "Medium"
        alert_type = "ATTENTION"
    else:  # < 5cm
        alert_level = 1
        risk = "Low"
        alert_type = "NORMAL"
    
    # Ajuster selon la confiance
    if confidence < 0.5 and alert_level > 1:
        alert_level -= 1
        if alert_level == 2:
            risk = "Medium"
            alert_type = "ATTENTION"
        else:
            risk = "Low"
            alert_type = "NORMAL"
    
    return {
        'level': alert_level,
        'risk': risk,
        'alert': alert_type,
        'size_meters': round(size_meters, 3),
        'size_cm': round(size_cm, 1)
    }

def determine_risk_level(confidence: float, class_name: str) -> str:
    """Détermine le niveau de risque basé sur la confiance et la classe (ancienne méthode)"""
    if confidence >= 0.8:
        return "High"
    elif confidence >= 0.6:
        return "Medium"
    else:
        return "Low"

def format_position(bbox, img_width: int, img_height: int) -> str:
    """Formate la position de la détection"""
    center_x = (bbox[0] + bbox[2]) / 2
    center_y = (bbox[1] + bbox[3]) / 2
    
    # Calculer la zone approximative
    zone_x = int(center_x / (img_width / 4)) + 1
    zone_y = int(center_y / (img_height / 4)) + 1
    zone = f"{chr(64 + zone_y)}{zone_x}"
    
    # Distance approximative depuis le seuil (bas de l'image)
    distance = img_height - center_y
    distance_m = (distance / img_height) * 30  # Approximation
    
    return f"Zone {zone} · {distance_m:.1f} m from threshold"

def detect_with_onnx(img_array, onnx_session, conf_threshold=0.2, imgsz=640):
    """
    Détecte des objets avec le modèle ONNX
    
    Args:
        img_array: Image numpy array (H, W, 3)
        onnx_session: Session ONNX
        conf_threshold: Seuil de confiance
        imgsz: Taille d'image
    
    Returns:
        Liste de détections au format YOLO
    """
    try:
        import onnxruntime as ort
        
        # Préparer l'image
        img_resized = cv2.resize(img_array, (imgsz, imgsz))
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        
        # Normaliser [0, 255] -> [0, 1]
        img_normalized = img_rgb.astype(np.float32) / 255.0
        
        # Convertir en tensor: (H, W, C) -> (1, C, H, W)
        img_tensor = img_normalized.transpose(2, 0, 1)[np.newaxis, ...]
        
        # Obtenir les noms d'entrée et de sortie
        input_name = onnx_session.get_inputs()[0].name
        output_name = onnx_session.get_outputs()[0].name
        
        # Inférence
        outputs = onnx_session.run([output_name], {input_name: img_tensor})
        output = outputs[0]  # Shape: (1, num_detections, 85) ou similaire
        
        # Parser les résultats ONNX (format peut varier selon le modèle)
        # Pour YOLO ONNX, généralement: (batch, num_detections, 85)
        # 85 = 4 (bbox) + 1 (objectness) + 80 (classes)
        
        # Créer un objet mock pour compatibilité avec le code YOLO existant
        class MockBox:
            def __init__(self, xyxy, conf, cls):
                self.xyxy = torch.tensor([xyxy])
                self.conf = torch.tensor([conf])
                self.cls = torch.tensor([cls])
        
        class MockResult:
            def __init__(self, boxes_list):
                self.boxes = type('Boxes', (), {
                    '__iter__': lambda self: iter(boxes_list),
                    '__len__': lambda self: len(boxes_list)
                })()
                for i, box in enumerate(boxes_list):
                    setattr(self.boxes, str(i), box)
        
        # Parser les détections ONNX
        detections_list = []
        if len(output.shape) == 3:  # (1, N, 85)
            detections = output[0]  # (N, 85)
            for det in detections:
                # Format: [x_center, y_center, width, height, objectness, class_scores...]
                x_center, y_center, width, height = det[0:4]
                objectness = det[4]
                class_scores = det[5:]
                
                # Convertir en xyxy
                x1 = (x_center - width/2) * imgsz
                y1 = (y_center - height/2) * imgsz
                x2 = (x_center + width/2) * imgsz
                y2 = (y_center + height/2) * imgsz
                
                # Trouver la classe avec le score max
                class_id = np.argmax(class_scores)
                confidence = objectness * class_scores[class_id]
                
                if confidence > conf_threshold:
                    box = MockBox([x1, y1, x2, y2], confidence, class_id)
                    detections_list.append(box)
        
        return [MockResult(detections_list)]
    
    except Exception as e:
        print(f"⚠️ Erreur détection ONNX: {e}")
        import traceback
        traceback.print_exc()
        return []

def detect_anomaly_with_autoencoder(img_array, autoencoder_model, device='cpu', threshold=0.1):
    """
    Détecte une anomalie dans l'image en utilisant l'auto-encoder
    
    Args:
        img_array: Image numpy array (H, W, 3)
        autoencoder_model: Modèle auto-encoder chargé
        device: Device ('cpu' ou 'cuda')
        threshold: Seuil d'erreur de reconstruction pour considérer une anomalie
    
    Returns:
        dict avec 'is_anomaly' (bool), 'reconstruction_error' (float), 'anomaly_score' (float)
    """
    try:
        # Préparer l'image pour l'auto-encoder
        # Redimensionner à 224x224 (taille standard) ou utiliser la taille du modèle
        img_resized = cv2.resize(img_array, (224, 224))
        
        # Normaliser [0, 255] -> [0, 1]
        img_normalized = img_resized.astype(np.float32) / 255.0
        
        # Convertir en tensor: (H, W, C) -> (1, C, H, W)
        img_tensor = torch.from_numpy(img_normalized).permute(2, 0, 1).unsqueeze(0).to(device)
        
        # Obtenir le modèle réel
        model = autoencoder_model
        if isinstance(autoencoder_model, dict):
            if 'model' in autoencoder_model:
                model = autoencoder_model['model']
            elif 'state_dict' in autoencoder_model:
                # Si seulement state_dict, on ne peut pas faire d'inférence directement
                return {
                    'is_anomaly': False,
                    'reconstruction_error': 0.0,
                    'anomaly_score': 0.0,
                    'error': 'Modèle avec seulement state_dict - architecture nécessaire'
                }
        
        # Inférence avec l'auto-encoder
        with torch.no_grad():
            # Reconstruire l'image
            reconstructed = model(img_tensor)
            
            # Calculer l'erreur de reconstruction (MSE)
            mse = torch.nn.functional.mse_loss(img_tensor, reconstructed)
            reconstruction_error = mse.item()
            
            # Normaliser le score d'anomalie (0-1)
            anomaly_score = min(reconstruction_error / threshold, 1.0)
            is_anomaly = reconstruction_error > threshold
        
        return {
            'is_anomaly': is_anomaly,
            'reconstruction_error': reconstruction_error,
            'anomaly_score': anomaly_score
        }
    
    except Exception as e:
        print(f"⚠️ Erreur lors de la détection d'anomalie: {e}")
        import traceback
        traceback.print_exc()
        return {
            'is_anomaly': False,
            'reconstruction_error': 0.0,
            'anomaly_score': 0.0,
            'error': str(e)
        }

@app.route('/', methods=['GET'])
def root():
    """Route racine"""
    return jsonify({
        'message': 'FOD Detection API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'detect': '/api/detect (POST)'
        }
    })

@app.route('/favicon.ico', methods=['GET'])
def favicon():
    """Gère les requêtes favicon pour éviter les 404"""
    return '', 204  # No Content

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health():
    """Endpoint de santé pour vérifier que le serveur fonctionne"""
    if request.method == 'OPTIONS':
        return '', 200
    
    return jsonify({
        'status': 'ok',
        'model_loaded': model is not None,
        'sam_available': sam_predictor is not None,
        'autoencoder_available': AUTOENCODER_AVAILABLE,
        'current_model_type': current_model_type,
        'onnx_available': ONNX_MODEL_PATH.exists()
    })

@app.route('/api/model/switch', methods=['POST', 'OPTIONS'])
def switch_model():
    """Endpoint pour changer de modèle (YOLO ou ONNX)"""
    global current_model_type, onnx_session
    
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        model_type = data.get('modelType', 'yolo').lower()
        
        if model_type not in ['yolo', 'onnx']:
            return jsonify({'error': 'Type invalide. Utilisez "yolo" ou "onnx"'}), 400
        
        if model_type == 'onnx':
            if not ONNX_MODEL_PATH.exists():
                return jsonify({'error': 'Modèle ONNX non trouvé'}), 404
            
            try:
                import onnxruntime as ort
                providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if torch.cuda.is_available() else ['CPUExecutionProvider']
                onnx_session = ort.InferenceSession(str(ONNX_MODEL_PATH), providers=providers)
                current_model_type = 'onnx'
                print(f"✅ Modèle ONNX chargé")
                return jsonify({'success': True, 'modelType': 'onnx'})
            except ImportError:
                return jsonify({'error': 'Installez onnxruntime: pip install onnxruntime'}), 500
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            if model is None:
                return jsonify({'error': 'Modèle YOLO non disponible'}), 500
            current_model_type = 'yolo'
            onnx_session = None
            print(f"✅ Modèle YOLO activé")
            return jsonify({'success': True, 'modelType': 'yolo'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/model/current', methods=['GET', 'OPTIONS'])
def get_current_model():
    """Obtenir le modèle actuellement utilisé"""
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({
        'modelType': current_model_type,
        'yolo_available': model is not None,
        'onnx_available': ONNX_MODEL_PATH.exists()
    })

@app.route('/api/detect', methods=['POST', 'OPTIONS'])
def detect():
    """Endpoint pour la détection d'objets sur une image"""
    global current_model_type, onnx_session
    
    if request.method == 'OPTIONS':
        return '', 200
    
    # Vérifier que le modèle est disponible
    if current_model_type == 'yolo' and model is None:
        return jsonify({
            'error': 'Modèle YOLO non chargé'
        }), 500
    elif current_model_type == 'onnx' and onnx_session is None:
        return jsonify({
            'error': 'Modèle ONNX non chargé. Utilisez /api/model/switch pour charger le modèle ONNX'
        }), 500
    
    if 'image' not in request.files:
        return jsonify({
            'error': 'Aucune image fournie'
        }), 400
    
    try:
        # Récupérer l'image
        file = request.files['image']
        if file.filename == '':
            return jsonify({
                'error': 'Fichier vide'
            }), 400
        
        print(f"\n📥 Réception d'une image: {file.filename}")
        
        # Lire l'image
        image_bytes = file.read()
        image_size_mb = len(image_bytes) / (1024 * 1024)
        print(f"📊 Taille de l'image: {image_size_mb:.2f} MB")
        
        image = Image.open(io.BytesIO(image_bytes))
        print(f"🖼️  Dimensions: {image.size[0]}x{image.size[1]} pixels")
        
        # Convertir en RGB si nécessaire
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convertir en numpy array
        img_array = np.array(image)
        img_height, img_width = img_array.shape[:2]
        print(f"📐 Dimensions de l'image numpy: {img_width}x{img_height}")
        
        # Effectuer la détection avec le modèle sélectionné
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        conf_threshold = 0.2
        
        if current_model_type == 'onnx' and onnx_session is not None:
            print("🔍 Démarrage de la détection ONNX...")
            print(f"⚡ Device utilisé: {device.upper()}")
            print(f"📊 Seuil de confiance utilisé: {conf_threshold}")
            results = detect_with_onnx(img_array, onnx_session, conf_threshold=conf_threshold, imgsz=640)
        else:
            print("🔍 Démarrage de la détection YOLOv8...")
            print(f"⚡ Device utilisé: {device.upper()}")
            print(f"📊 Seuil de confiance utilisé: {conf_threshold}")
            # YOLOv8 retourne les coordonnées dans le système de l'image originale
            results = model(img_array, conf=conf_threshold, imgsz=640, device=device)
        
        # Configurer SAM avec l'image UNE SEULE FOIS (optimisation)
        if sam_predictor is not None:
            print("🎨 Configuration de SAM pour la segmentation...")
            img_rgb = img_array.copy()
            sam_predictor.set_image(img_rgb)
        
        # Parser les résultats
        print("📋 Analyse des résultats...")
        detections = []
        
        # Vérifier si des résultats ont été trouvés
        total_boxes = 0
        for idx, result in enumerate(results):
            if result.boxes is not None:
                total_boxes += len(result.boxes)
        
        print(f"📊 Nombre de détections brutes trouvées: {total_boxes}")
        
        # Si YOLO ne trouve rien, afficher "Anomalie détectée"
        if total_boxes == 0:
            print("⚠️ Aucune détection YOLO trouvée")
            print("🚨 ANOMALIE DÉTECTÉE")
            
            # Créer une détection d'anomalie (sans alerte, juste "Anomalie")
            anomaly_detection_obj = {
                'id': 'anomaly_0',
                'label': 'Anomalie',
                'confidence': 0.5,
                'riskLevel': 'Low',
                'alertLevel': 1,
                'alertType': 'NORMAL',
                'sizeMeters': 0.0,
                'sizeCm': 0.0,
                'position': 'Zone inconnue - Anomalie détectée',
                'bbox': {'x': 0, 'y': 0, 'width': 100, 'height': 100},
                'hasSegmentation': False,
                'segmentationMask': None,
                'isAnomaly': True
            }
            detections.append(anomaly_detection_obj)
        
        for idx, result in enumerate(results):
            boxes = result.boxes
            if boxes is None or len(boxes) == 0:
                continue
            for i, box in enumerate(boxes):
                # Coordonnées de la bounding box (x1, y1, x2, y2)
                # YOLOv8 retourne les coordonnées dans le système de l'image d'entrée
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                
                # Vérifier que les coordonnées sont dans les limites
                x1 = max(0, min(x1, img_width))
                y1 = max(0, min(y1, img_height))
                x2 = max(x1, min(x2, img_width))
                y2 = max(y1, min(y2, img_height))
                
                # Confiance
                confidence = float(box.conf[0].cpu().numpy())
                
                # Classe
                class_id = int(box.cls[0].cpu().numpy())
                # Utiliser les noms de classes du modèle YOLO (même si on utilise ONNX)
                if model is not None and hasattr(model, 'names'):
                    class_name = model.names[class_id]
                else:
                    class_name = f"Class_{class_id}"  # Fallback si pas de noms disponibles
                
                # Calculer les coordonnées en pourcentage pour le frontend
                bbox_width_px = x2 - x1
                bbox_height_px = y2 - y1
                
                # Debug: afficher les coordonnées brutes (désactivé pour performance)
                # print(f"📍 Box {i}: raw=({x1:.1f}, {y1:.1f}, {x2:.1f}, {y2:.1f}) img_size=({img_width}, {img_height})")
                
                bbox_percent = {
                    'x': (x1 / img_width) * 100,
                    'y': (y1 / img_height) * 100,
                    'width': (bbox_width_px / img_width) * 100,
                    'height': (bbox_height_px / img_height) * 100
                }
                
                # print(f"   → Pourcent: x={bbox_percent['x']:.2f}% y={bbox_percent['y']:.2f}% w={bbox_percent['width']:.2f}% h={bbox_percent['height']:.2f}%")
                
                # Segmentation SAM (si disponible) - FAIRE AVANT le calcul de taille
                # Note: sam_predictor.set_image() a déjà été appelé avant la boucle
                mask_base64 = None
                segmentation_available = False
                mask_area_px = None
                
                if sam_predictor is not None:
                    try:
                        # Créer la bounding box pour SAM [x1, y1, x2, y2]
                        box_sam = np.array([x1, y1, x2, y2])
                        
                        # Prédire le masque (SAM est déjà configuré avec l'image)
                        masks, scores, logits = sam_predictor.predict(
                            box=box_sam,
                            multimask_output=False
                        )
                        
                        if len(masks) > 0:
                            mask = masks[0]  # Masque complet de l'image (img_height x img_width)
                            segmentation_available = True
                            
                            # Calculer la surface du masque en pixels (pour calcul de taille précis)
                            mask_area_px = float(np.sum(mask.astype(np.uint8)))
                            
                            # Convertir les coordonnées en entiers
                            x1_int, y1_int, x2_int, y2_int = int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))
                            
                            # S'assurer que les coordonnées sont dans les limites de l'image
                            x1_int = max(0, min(x1_int, img_width - 1))
                            y1_int = max(0, min(y1_int, img_height - 1))
                            x2_int = max(x1_int + 1, min(x2_int, img_width))
                            y2_int = max(y1_int + 1, min(y2_int, img_height))
                            
                            # Dimensions de la région de la bounding box
                            bbox_w = x2_int - x1_int
                            bbox_h = y2_int - y1_int
                            
                            # Extraire la région du masque correspondant à la bounding box
                            mask_region = mask[y1_int:y2_int, x1_int:x2_int]
                            
                            # Vérifier que la taille correspond
                            if mask_region.shape[0] != bbox_h or mask_region.shape[1] != bbox_w:
                                print(f"⚠️  Taille du masque incompatible: {mask_region.shape} vs ({bbox_h}, {bbox_w})")
                                mask_region = mask[y1_int:y2_int, x1_int:x2_int].copy()
                            
                            # Calculer la taille AVANT d'utiliser risk_info pour les couleurs
                            size_meters_for_color = calculate_real_size(bbox_width_px, bbox_height_px, img_width, img_height, mask_area_px)
                            risk_info_for_color = determine_risk_level_by_size(size_meters_for_color, confidence)
                            
                            # Couleur selon le niveau d'alerte (RGBA) - 40% d'opacité
                            if risk_info_for_color['level'] == 3:
                                color_rgba = [255, 0, 0, 102]  # Rouge
                            elif risk_info_temp['level'] == 2:
                                color_rgba = [255, 165, 0, 102]  # Orange
                            else:
                                color_rgba = [0, 255, 0, 102]  # Vert
                            
                            # Créer un masque RGBA pour la région de la bounding box
                            seg_mask_rgba = np.zeros((bbox_h, bbox_w, 4), dtype=np.uint8)
                            
                            # Appliquer la couleur uniquement là où le masque est True
                            seg_mask_rgba[mask_region] = color_rgba
                            
                            # Ajouter le contour sur le masque
                            mask_uint8 = mask_region.astype(np.uint8) * 255
                            contours, _ = cv2.findContours(
                                mask_uint8, 
                                cv2.RETR_EXTERNAL, 
                                cv2.CHAIN_APPROX_SIMPLE
                            )
                            # Dessiner le contour en couleur opaque (2px d'épaisseur)
                            contour_color = tuple(color_rgba[:3]) + (255,)  # Même couleur mais opaque
                            cv2.drawContours(seg_mask_rgba, contours, -1, contour_color, 2)
                            
                            # Convertir en base64 pour l'envoyer au frontend (format PNG avec transparence)
                            seg_img_pil = Image.fromarray(seg_mask_rgba, 'RGBA')
                            buffer = io.BytesIO()
                            seg_img_pil.save(buffer, format='PNG')
                            mask_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                            
                            print(f"✅ Segmentation créée pour {class_name} (Alerte {risk_info_for_color['level']}) - Box: [{x1_int},{y1_int}→{x2_int},{y2_int}] Masque: {mask_region.shape}")
                    except Exception as e:
                        print(f"⚠️ Erreur lors de la segmentation SAM: {e}")
                        import traceback
                        traceback.print_exc()
                        segmentation_available = False
                
                # Calculer la taille réelle en mètres (utiliser la surface du masque si disponible)
                size_meters = calculate_real_size(bbox_width_px, bbox_height_px, img_width, img_height, mask_area_px)
                risk_info = determine_risk_level_by_size(size_meters, confidence)
                
                # Formater la position
                position = format_position([x1, y1, x2, y2], img_width, img_height)
                
                detection = {
                    'id': f"{idx}_{i}",
                    'label': class_name,
                    'confidence': confidence,
                    'riskLevel': risk_info['risk'],
                    'alertLevel': risk_info['level'],
                    'alertType': risk_info['alert'],
                    'sizeMeters': risk_info['size_meters'],
                    'sizeCm': risk_info['size_cm'],
                    'position': position,
                    'bbox': bbox_percent,
                    'hasSegmentation': segmentation_available,
                    'segmentationMask': mask_base64
                }
                
                detections.append(detection)
        
        # Vérifier s'il y a des alertes de niveau 3 (danger)
        has_danger_alert = any(d.get('alertLevel', 0) == 3 for d in detections)
        max_alert = max([d.get('alertLevel', 1) for d in detections], default=1)
        
        print(f"✅ Détection terminée: {len(detections)} objet(s) détecté(s)")
        seg_count = sum(1 for d in detections if d.get('hasSegmentation', False))
        if seg_count > 0:
            print(f"🎨 Segmentation: {seg_count} objet(s) segmenté(s)")
        if sam_predictor is None:
            print("⚠️  SAM non disponible - segmentation désactivée")
        if has_danger_alert:
            print("🚨 ALERTE DANGER détectée (Alerte 3)!")
        elif max_alert == 2:
            print("⚠️  Alerte Attention détectée (Alerte 2)")
        else:
            print("✓ Aucune alerte critique")
        
        # Sauvegarder automatiquement dans MongoDB
        mongo_id = None
        if MONGODB_AVAILABLE and mongodb_service:
            mongo_id = mongodb_service.save_image_detection(
                detections=detections,
                image_filename=file.filename,
                image_size={'width': img_width, 'height': img_height},
                metadata={
                    'has_danger_alert': has_danger_alert,
                    'max_alert_level': max_alert,
                    'segmentation_count': seg_count
                }
            )
        
        return jsonify({
            'detections': detections,
            'count': len(detections),
            'hasDangerAlert': has_danger_alert,
            'maxAlertLevel': max_alert,
            'mongoId': mongo_id  # ID MongoDB si sauvegardé
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Erreur lors de la détection: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Erreur lors du traitement: {error_msg}',
            'detections': [],
            'count': 0
        }), 500


@app.route('/api/detect-video', methods=['POST', 'OPTIONS'])
def detect_video():
    """Endpoint pour la détection d'objets sur une vidéo avec tracking YOLO"""
    if request.method == 'OPTIONS':
        return '', 200
    
    if model is None:
        return jsonify({
            'error': 'Modèle non chargé'
        }), 500
    
    # Debug : afficher les fichiers reçus
    print(f"🔍 DEBUG - Fichiers reçus: {list(request.files.keys())}")
    print(f"🔍 DEBUG - Content-Type: {request.content_type}")
    print(f"🔍 DEBUG - Form data keys: {list(request.form.keys())}")
    
    if 'video' not in request.files:
        # Vérifier si c'est peut-être 'file' au lieu de 'video'
        if 'file' in request.files:
            print("⚠️ 'video' non trouvé, mais 'file' trouvé - utilisation de 'file'")
            file = request.files['file']
        else:
            print("❌ Erreur: Aucun fichier 'video' ou 'file' trouvé")
            return jsonify({
                'error': 'Aucune vidéo fournie. Utilisez le champ "video" dans le FormData.'
            }), 400
    else:
        file = request.files['video']
    
    try:
        if file.filename == '' or file.filename is None:
            print("❌ Erreur: Nom de fichier vide")
            return jsonify({
                'error': 'Fichier vide ou nom de fichier manquant'
            }), 400
        
        print(f"\n📥 Réception d'une vidéo: {file.filename}")
        
        # Lire le contenu pour vérifier la taille
        file_content = file.read()
        file_size_mb = len(file_content) / (1024*1024)
        print(f"📊 Taille du fichier: {file_size_mb:.2f} MB")
        
        if file_size_mb == 0:
            return jsonify({
                'error': 'Le fichier vidéo est vide (0 bytes)'
            }), 400
        
        # Réinitialiser le pointeur du fichier après la lecture
        file.seek(0)
        
        # Sauvegarder temporairement la vidéo
        # Déterminer l'extension du fichier
        file_ext = os.path.splitext(file.filename)[1] if file.filename else '.mp4'
        if not file_ext:
            file_ext = '.mp4'
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            file.save(tmp_file.name)
            video_path = tmp_file.name
            print(f"💾 Vidéo sauvegardée temporairement: {video_path}")
        
        # Ouvrir la vidéo avec OpenCV
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            os.unlink(video_path)
            return jsonify({
                'error': 'Impossible d\'ouvrir la vidéo'
            }), 400
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"📹 Vidéo: {width}x{height}, {fps:.2f} FPS, {total_frames} frames")
        print(f"🎯 Utilisation du tracking YOLO (ByteTrack) pour suivre les objets")
        
        # Vérifier si le modèle supporte la segmentation
        model_has_segmentation = hasattr(model.model, 'seg') or 'seg' in str(type(model.model)).lower()
        print(f"🎨 Segmentation du modèle: {'✅ Activée' if model_has_segmentation else '❌ Non disponible'}")
        
        # OPTIMISATION PERFORMANCE : Traiter seulement 1 frame sur plusieurs pour accélérer
        # Augmenter frame_skip réduit drastiquement le temps de traitement
        # frame_skip = 1 : toutes les frames (très lent, 20+ min)
        # frame_skip = 3 : 1 frame sur 3 (3x plus rapide)
        # frame_skip = 5 : 1 frame sur 5 (5x plus rapide)
        device_check = 'cuda' if torch.cuda.is_available() else 'cpu'
        frame_skip = 5 if device_check == 'cpu' else 3  # Plus de frames sautées pour vitesse maximale
        print(f"⚡ Traitement de 1 frame sur {frame_skip} pour optimiser les performances")
        print(f"   (Temps estimé réduit de {frame_skip}x)")
        
        # Initialiser ByteTrack de supervision (comme dans Colab) - MÊME SUR CPU
        # C'est crucial pour éviter les boxes qui flottent et améliorer la stabilité
        tracker_sv = None
        smoother = None
        
        if SUPERVISION_AVAILABLE:
            # Utiliser ByteTrack de supervision avec les mêmes paramètres que Colab
            fps_video = fps if fps > 0 else 30
            tracker_sv = sv.ByteTracker(
                track_activation_threshold=0.4,
                lost_track_buffer=30,
                minimum_matching_threshold=0.8,
                frame_rate=fps_video
            )
            print(f"🎯 ByteTrack de supervision activé (même sur CPU) - paramètres comme Colab")
            print(f"   track_activation_threshold=0.4, lost_track_buffer=30, minimum_matching_threshold=0.8")
        else:
            # Fallback sur notre smoother personnalisé si supervision n'est pas disponible
            smoother = BBoxSmoother(alpha=0.7, max_age=5)
            print(f"⚠️ Supervision non disponible - utilisation du smoother personnalisé - {device_check.upper()}")
        
        # OPTIMISATION PERFORMANCE : SAM désactivé par défaut (très coûteux en temps)
        # Activer SAM ralentit considérablement le traitement (peut doubler le temps)
        # Décommenter les lignes ci-dessous pour activer SAM si nécessaire
        USE_SAM_SEGMENTATION = False  # Désactivé pour performance (était True)
        sam_model_video = None
        if USE_SAM_SEGMENTATION:
            try:
                from ultralytics import SAM
                sam_model_video = SAM("mobile_sam.pt")  # Téléchargera automatiquement si nécessaire
                print(f"✅ SAM initialisé pour la vidéo (ATTENTION: ralentit le traitement)")
            except Exception as e:
                print(f"⚠️ Erreur lors de l'initialisation SAM: {e}")
                sam_model_video = None
        else:
            print(f"⚡ SAM désactivé pour optimiser les performances (peut être activé si nécessaire)")
        
        # Initialiser les annotateurs pour l'affichage (si supervision disponible)
        if SUPERVISION_AVAILABLE:
            box_annotator = sv.BoxAnnotator()
            mask_annotator = sv.MaskAnnotator() if model_has_segmentation else None
            print(f"🎨 MaskAnnotator: {'✅ Activé' if mask_annotator else '❌ Désactivé (pas de segmentation)'}")
        
        # Traiter chaque frame avec tracking (mais seulement certaines frames)
        processed_frames_data = []  # Stocker seulement les frames traitées avec leurs détections
        frame_number = 0
        processed_frame_count = 0
        start_time = time.time()  # Chronomètre pour estimer le temps restant
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_number += 1
            
            # Traiter seulement 1 frame sur frame_skip pour optimiser
            if frame_number % frame_skip != 0:
                continue
            
            # OPTIMISATION PERFORMANCE : Résolution optimisée pour détecter les petits objets
            # Plus la résolution est élevée, mieux on détecte les petits objets
            # 320 : très rapide mais moins précis pour petits objets
            # 416 : équilibré (CPU) - bon pour petits objets
            # 512 : plus précis mais plus lent (GPU) - excellent pour petits objets
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            # Résolution augmentée pour mieux détecter les petits objets
            imgsz_video = 416 if device == 'cpu' else 512  # Meilleure détection des petits objets
            scale_factor = 1.0  # Résolution originale pour les coordonnées finales
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # IMPORTANT : Utiliser model() au lieu de model.track() (comme dans Colab)
            # Détection YOLO séparée du tracking pour utiliser ByteTrack de supervision
            conf_threshold = 0.2  # Seuil réduit pour détecter plus de petits objets (était 0.25)
            iou_threshold = 0.5    # IOU réduit pour mieux détecter les petits objets proches (était 0.6)
            
            # Détection YOLO (sans tracking intégré - comme dans Colab)
            if tracker_sv is not None:
                # Utiliser model() pour la détection, puis ByteTrack de supervision pour le tracking
                results = model(frame_rgb, conf=conf_threshold, iou=iou_threshold, imgsz=imgsz_video, device=device, verbose=False)
            else:
                # Fallback : utiliser model.track() si supervision n'est pas disponible
                try:
                    results = model.track(frame_rgb, conf=conf_threshold, persist=True, tracker="bytetrack.yaml", imgsz=imgsz_video, device=device, verbose=False)
                except:
                    results = model.track(frame_rgb, conf=conf_threshold, persist=True, imgsz=imgsz_video, device=device, verbose=False)
            
            # Conversion en format supervision et application de ByteTrack (comme dans Colab)
            detections_sv = None
            if SUPERVISION_AVAILABLE and tracker_sv is not None:
                try:
                    # Convertir les résultats YOLO en format supervision (comme dans Colab)
                    result = results[0] if isinstance(results, list) else results
                    
                    if result.boxes is not None and len(result.boxes) > 0:
                        bboxes = result.boxes.xyxy.cpu().numpy()
                        confidences = result.boxes.conf.cpu().numpy()
                        class_ids = result.boxes.cls.cpu().numpy().astype(int)
                        
                        # OPTIMISATION PERFORMANCE : SAM désactivé par défaut (très coûteux)
                        # Activer SAM seulement si USE_SAM_SEGMENTATION = True
                        masks = None
                        
                        if USE_SAM_SEGMENTATION and sam_model_video is not None:
                            try:
                                # Utiliser SAM comme dans Colab (déjà initialisé avant la boucle)
                                # ATTENTION: Cela ralentit considérablement le traitement
                                sam_results = sam_model_video(frame_rgb, bboxes=bboxes, verbose=False)
                                if sam_results[0].masks is not None:
                                    masks = sam_results[0].masks.data.cpu().numpy()
                            except Exception as e:
                                # Désactiver les logs pour performance
                                # print(f"⚠️ Erreur SAM frame {frame_number}: {e}")
                                masks = None
                        
                        # Créer les détections supervision (comme dans Colab)
                        detections_sv = Detections(
                            xyxy=bboxes,
                            confidence=confidences,
                            class_id=class_ids,
                            mask=masks.astype(bool) if masks is not None else None
                        )
                        
                        # CRUCIAL : Appliquer ByteTrack de supervision (comme dans Colab)
                        # C'est cette étape qui évite les boxes qui flottent et améliore la stabilité
                        detections_sv = tracker_sv.update_with_detections(detections_sv)
                except Exception as e:
                    print(f"⚠️ Erreur supervision frame {frame_number}: {e}")
                    detections_sv = None
            
            detections = []
            
            # IMPORTANT : Utiliser ByteTrack de supervision si disponible (comme dans Colab)
            # Cela évite les boxes qui flottent et améliore la stabilité
            if detections_sv is not None and len(detections_sv) > 0:
                # Utiliser les détections de supervision (déjà trackées par ByteTrack - comme dans Colab)
                for i in range(len(detections_sv)):
                    x1, y1, x2, y2 = detections_sv.xyxy[i]
                    confidence = float(detections_sv.confidence[i])
                    class_id = int(detections_sv.class_id[i])
                    track_id = int(detections_sv.tracker_id[i]) if detections_sv.tracker_id is not None and i < len(detections_sv.tracker_id) else None
                    
                    # Vérifier les limites
                    x1 = max(0, min(x1, width))
                    y1 = max(0, min(y1, height))
                    x2 = max(x1, min(x2, width))
                    y2 = max(y1, min(y2, height))
                    
                    class_name = model.names[class_id]
                    detection_id = f"track_{track_id}" if track_id is not None else f"frame_{frame_number}_{i}"
                    
                    bbox_width_px = x2 - x1
                    bbox_height_px = y2 - y1
                    
                    # Les coordonnées sont déjà trackées et stables grâce à ByteTrack
                    bbox_percent = {
                        'x': (x1 / width) * 100,
                        'y': (y1 / height) * 100,
                        'width': (bbox_width_px / width) * 100,
                        'height': (bbox_height_px / height) * 100
                    }
                    
                    # Calculer la taille réelle en mètres (utiliser la surface du masque si disponible)
                    size_meters = calculate_real_size(bbox_width_px, bbox_height_px, width, height, mask_area_px)
                    risk_info = determine_risk_level_by_size(size_meters, confidence)
                    position = format_position([x1, y1, x2, y2], width, height)
                    
                    # OPTIMISATION PERFORMANCE : Segmentation masquée désactivée par défaut
                    # La conversion base64 des masques est coûteuse en CPU
                    # Activer seulement si USE_SAM_SEGMENTATION = True
                    mask_base64 = None
                    segmentation_available = False
                    
                    if USE_SAM_SEGMENTATION and detections_sv.mask is not None and i < len(detections_sv.mask):
                        try:
                            mask = detections_sv.mask[i]
                            
                            # Extraire la région de la bounding box
                            x1_int, y1_int, x2_int, y2_int = int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))
                            x1_int = max(0, min(x1_int, width - 1))
                            y1_int = max(0, min(y1_int, height - 1))
                            x2_int = max(x1_int + 1, min(x2_int, width))
                            y2_int = max(y1_int + 1, min(y2_int, height))
                            
                            bbox_w = x2_int - x1_int
                            bbox_h = y2_int - y1_int
                            
                            # Redimensionner le masque si nécessaire
                            if mask.shape[0] != height or mask.shape[1] != width:
                                mask_resized = cv2.resize(mask.astype(np.uint8), (width, height), interpolation=cv2.INTER_NEAREST).astype(bool)
                            else:
                                mask_resized = mask
                            
                            mask_region = mask_resized[y1_int:y2_int, x1_int:x2_int]
                            
                            if mask_region.shape[0] == bbox_h and mask_region.shape[1] == bbox_w:
                                # Couleur selon le niveau d'alerte (RGBA)
                                if risk_info['level'] == 3:
                                    color_rgba = [255, 0, 0, 102]  # Rouge
                                elif risk_info['level'] == 2:
                                    color_rgba = [255, 165, 0, 102]  # Orange
                                else:
                                    color_rgba = [0, 255, 0, 102]  # Vert
                                
                                # Créer un masque RGBA
                                seg_mask_rgba = np.zeros((bbox_h, bbox_w, 4), dtype=np.uint8)
                                seg_mask_rgba[mask_region] = color_rgba
                                
                                # Ajouter le contour
                                mask_uint8 = mask_region.astype(np.uint8) * 255
                                contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                                contour_color = tuple(color_rgba[:3]) + (255,)
                                cv2.drawContours(seg_mask_rgba, contours, -1, contour_color, 2)
                                
                                # Convertir en base64
                                seg_img_pil = Image.fromarray(seg_mask_rgba, 'RGBA')
                                buffer = io.BytesIO()
                                seg_img_pil.save(buffer, format='PNG')
                                mask_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                                segmentation_available = True
                        except Exception as e:
                            segmentation_available = False
                    
                    # Désactiver les logs détaillés pour performance (trop de prints ralentissent)
                    # if processed_frame_count < 5:  # Limiter les logs pour ne pas surcharger
                    #     track_info = f" (Track ID: {track_id})" if track_id is not None else ""
                    #     print(f"   📍 Frame {frame_number}: {class_name} ({confidence*100:.1f}%) - Alerte {risk_info['level']}{track_info}")
                    
                    detection = {
                        'id': detection_id,
                        'trackId': track_id,  # ID de tracking pour maintenir la continuité
                        'label': class_name,
                        'confidence': confidence,
                        'riskLevel': risk_info['risk'],
                        'alertLevel': risk_info['level'],
                        'alertType': risk_info['alert'],
                        'sizeMeters': risk_info['size_meters'],
                        'sizeCm': risk_info['size_cm'],
                        'position': position,
                        'bbox': bbox_percent,
                        'hasSegmentation': segmentation_available,
                        'segmentationMask': mask_base64
                    }
                    
                    detections.append(detection)
            else:
                # Fallback : utiliser les résultats YOLO directement (si supervision n'est pas disponible)
                for idx, result in enumerate(results):
                    boxes = result.boxes
                    
                    if boxes is None or len(boxes) == 0:
                        continue
                    
                    for i, box in enumerate(boxes):
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        
                        # Vérifier les limites
                        x1 = max(0, min(x1, width))
                        y1 = max(0, min(y1, height))
                        x2 = max(x1, min(x2, width))
                        y2 = max(y1, min(y2, height))
                        
                        confidence = float(box.conf[0].cpu().numpy())
                        class_id = int(box.cls[0].cpu().numpy())
                        class_name = model.names[class_id]
                        
                        # Récupérer l'ID de tracking (si disponible)
                        track_id = None
                        if box.id is not None and len(box.id) > 0:
                            track_id = int(box.id[0].cpu().numpy())
                        
                        detection_id = f"track_{track_id}" if track_id is not None else f"frame_{frame_number}_{i}"
                        
                        bbox_width_px = x2 - x1
                        bbox_height_px = y2 - y1
                        
                        # Utiliser notre smoother personnalisé si disponible
                        bbox_percent_raw = {
                            'x': (x1 / width) * 100,
                            'y': (y1 / height) * 100,
                            'width': (bbox_width_px / width) * 100,
                            'height': (bbox_height_px / height) * 100
                        }
                        
                        if smoother is not None and track_id is not None:
                            bbox_percent = smoother.update(track_id, bbox_percent_raw, frame_number - 1)
                        else:
                            bbox_percent = bbox_percent_raw
                        
                        # Segmentation désactivée pour performance (pas de masque disponible)
                        mask_area_px = None
                        
                        # Calculer la taille réelle en mètres (sans masque)
                        size_meters = calculate_real_size(bbox_width_px, bbox_height_px, width, height, mask_area_px)
                        risk_info = determine_risk_level_by_size(size_meters, confidence)
                        position = format_position([x1, y1, x2, y2], width, height)
                        
                        # Segmentation désactivée pour performance
                        mask_base64 = None
                        segmentation_available = False
                        
                        detection = {
                            'id': detection_id,
                            'trackId': track_id,
                            'label': class_name,
                            'confidence': confidence,
                            'riskLevel': risk_info['risk'],
                            'alertLevel': risk_info['level'],
                            'alertType': risk_info['alert'],
                            'sizeMeters': risk_info['size_meters'],
                            'sizeCm': risk_info['size_cm'],
                            'position': position,
                            'bbox': bbox_percent,
                            'hasSegmentation': segmentation_available,
                            'segmentationMask': mask_base64
                        }
                        
                        detections.append(detection)
            
            # Stocker les données de la frame traitée
            processed_frames_data.append({
                'frame': frame_number - 1,
                'time': (frame_number - 1) / fps if fps > 0 else 0,
                'detections': detections,
                'count': len(detections)
            })
            
            processed_frame_count += 1
            
            # Nettoyer les tracks expirées (seulement pour notre smoother personnalisé) - moins souvent pour performance
            if smoother is not None and processed_frame_count % 50 == 0:  # Moins souvent (50 au lieu de 10)
                expired_count = smoother.cleanup(frame_number - 1)
                # Désactiver le log pour performance
                # if expired_count > 0:
                #     print(f"   🧹 {expired_count} tracks expirées supprimées")
            
            # Afficher la progression (réduit pour performance)
            if processed_frame_count % 20 == 0:  # Afficher plus souvent pour suivre la progression
                progress_pct = (processed_frame_count / (total_frames // frame_skip)) * 100 if total_frames > 0 else 0
                elapsed_time = time.time() - start_time if 'start_time' in locals() else 0
                if elapsed_time > 0:
                    fps_processing = processed_frame_count / elapsed_time
                    remaining_frames = (total_frames // frame_skip) - processed_frame_count
                    eta_seconds = remaining_frames / fps_processing if fps_processing > 0 else 0
                    eta_min = int(eta_seconds // 60)
                    eta_sec = int(eta_seconds % 60)
                    if smoother is not None:
                        active_tracks = len(smoother.get_active_tracks(frame_number - 1))
                        print(f"   ⏳ {processed_frame_count} frames ({progress_pct:.1f}%) - {active_tracks} tracks - ETA: {eta_min}m{eta_sec}s")
                    else:
                        print(f"   ⏳ {processed_frame_count} frames ({progress_pct:.1f}%) - ETA: {eta_min}m{eta_sec}s")
                else:
                    if smoother is not None:
                        active_tracks = len(smoother.get_active_tracks(frame_number - 1))
                        print(f"   ⏳ Traité {processed_frame_count} frames - {progress_pct:.1f}% - {active_tracks} tracks")
                    else:
                        print(f"   ⏳ Traité {processed_frame_count} frames - {progress_pct:.1f}%")
        
        cap.release()
        os.unlink(video_path)
        
        # Nettoyer les tracks restantes avant interpolation (seulement pour notre smoother)
        if smoother is not None:
            smoother.cleanup(total_frames)
        
        # OPTIMISATION : Option pour désactiver l'interpolation complète (beaucoup plus rapide)
        # Mettre USE_FULL_INTERPOLATION = False pour retourner seulement les frames traitées
        USE_FULL_INTERPOLATION = False  # False = plus rapide, True = interpolation complète mais plus lent
        
        if not USE_FULL_INTERPOLATION:
            # Mode rapide : retourner seulement les frames traitées (pas d'interpolation)
            print(f"⚡ Mode rapide : retour des {processed_frame_count} frames traitées uniquement")
            frame_detections = processed_frames_data
        else:
            # Mode complet : interpolation de toutes les frames (plus lent mais plus fluide)
            print(f"🔄 Interpolation des positions pour suivi fluide...")
            frame_detections = []
            
            # Créer un dictionnaire pour suivre les objets par trackId
            tracked_objects = {}  # {trackId: {frame: detection, ...}}
            
            # Remplir le dictionnaire avec les frames traitées (déjà lissées par le smoother)
            for frame_data in processed_frames_data:
                for detection in frame_data['detections']:
                    track_id = detection.get('trackId')
                    if track_id is not None:
                        if track_id not in tracked_objects:
                            tracked_objects[track_id] = {}
                        tracked_objects[track_id][frame_data['frame']] = detection
            
            # Interpoler pour toutes les frames
            for frame_idx in range(total_frames):
                current_time = frame_idx / fps if fps > 0 else 0
            
            # Trouver les frames traitées avant et après
            prev_frame_data = None
            next_frame_data = None
            
            for pf in processed_frames_data:
                if pf['frame'] <= frame_idx:
                    prev_frame_data = pf
                elif pf['frame'] > frame_idx and next_frame_data is None:
                    next_frame_data = pf
                    break
            
            interpolated_detections = []
            
            # Si on a une frame traitée exacte, utiliser ses détections
            if prev_frame_data and prev_frame_data['frame'] == frame_idx:
                interpolated_detections = prev_frame_data['detections']
            else:
                # Interpoler les positions entre les frames traitées
                for track_id, frames_dict in tracked_objects.items():
                    # Trouver les frames traitées les plus proches
                    prev_frame = None
                    next_frame = None
                    
                    sorted_frames = sorted(frames_dict.keys())
                    for fnum in sorted_frames:
                        if fnum <= frame_idx:
                            prev_frame = fnum
                        elif fnum > frame_idx and next_frame is None:
                            next_frame = fnum
                            break
                    
                    # Trouver la première et dernière frame où l'objet apparaît
                    first_frame = sorted_frames[0] if sorted_frames else None
                    last_frame = sorted_frames[-1] if sorted_frames else None
                    
                    # Ne pas afficher l'objet avant sa première apparition
                    # Mais permettre l'affichage jusqu'à max_age frames après la dernière détection
                    max_age_frames = 5  # Correspond au max_age du smoother
                    if first_frame is not None and last_frame is not None:
                        if frame_idx < first_frame:
                            continue
                        # Permettre l'affichage jusqu'à max_age frames après la dernière détection
                        if frame_idx > last_frame + max_age_frames:
                            continue
                    
                    # Si on a une détection avant et après, interpoler
                    if prev_frame is not None and next_frame is not None:
                        prev_det = frames_dict[prev_frame]
                        next_det = frames_dict[next_frame]
                        
                        # Calculer le ratio d'interpolation
                        total_frames_between = next_frame - prev_frame
                        frames_from_prev = frame_idx - prev_frame
                        ratio = frames_from_prev / total_frames_between if total_frames_between > 0 else 0
                        
                        # Interpoler les positions de la bounding box
                        interpolated_bbox = {
                            'x': prev_det['bbox']['x'] + (next_det['bbox']['x'] - prev_det['bbox']['x']) * ratio,
                            'y': prev_det['bbox']['y'] + (next_det['bbox']['y'] - prev_det['bbox']['y']) * ratio,
                            'width': prev_det['bbox']['width'] + (next_det['bbox']['width'] - prev_det['bbox']['width']) * ratio,
                            'height': prev_det['bbox']['height'] + (next_det['bbox']['height'] - prev_det['bbox']['height']) * ratio
                        }
                        
                        # Créer une détection interpolée (utiliser les données de la frame précédente)
                        interpolated_detection = prev_det.copy()
                        interpolated_detection['bbox'] = interpolated_bbox
                        interpolated_detections.append(interpolated_detection)
                    elif prev_frame is not None:
                        # Utiliser la dernière détection connue (objet toujours visible)
                        interpolated_detections.append(frames_dict[prev_frame].copy())
                    elif next_frame is not None:
                        # Utiliser la prochaine détection connue (objet vient d'apparaître)
                        interpolated_detections.append(frames_dict[next_frame].copy())
                
                # Ajouter aussi les objets sans trackId de la frame traitée la plus proche
                if prev_frame_data:
                    for detection in prev_frame_data['detections']:
                        if detection.get('trackId') is None:
                            # Objet sans tracking - seulement si on est proche de la frame traitée
                            if abs(frame_idx - prev_frame_data['frame']) <= frame_skip:
                                interpolated_detections.append(detection.copy())
            
            frame_detections.append({
                'frame': frame_idx,
                'time': current_time,
                'detections': interpolated_detections,
                'count': len(interpolated_detections)
            })
        
        # Vérifier les alertes
        all_detections = [d for fd in frame_detections for d in fd['detections']]
        has_danger_alert = any(d.get('alertLevel', 0) == 3 for d in all_detections)
        max_alert = max([d.get('alertLevel', 1) for d in all_detections], default=1)
        
        # Compter les objets trackés uniques
        unique_tracks = set()
        for d in all_detections:
            if d.get('trackId') is not None:
                unique_tracks.add(d['trackId'])
        
        print(f"✅ Vidéo traitée: {processed_frame_count} frames analysées, {total_frames} frames interpolées")
        print(f"📊 Détections totales: {len(all_detections)}")
        print(f"🎯 Objets trackés uniques: {len(unique_tracks)}")
        
        # Afficher un résumé des classes détectées
        if all_detections:
            class_counts = {}
            for d in all_detections:
                label = d.get('label', 'unknown')
                class_counts[label] = class_counts.get(label, 0) + 1
            print(f"📋 Classes détectées: {class_counts}")
        
        # Sauvegarder automatiquement dans MongoDB
        mongo_id = None
        if MONGODB_AVAILABLE and mongodb_service:
            mongo_id = mongodb_service.save_video_detection(
                frames=frame_detections,
                video_filename=file.filename,
                video_info={
                    'fps': fps,
                    'duration': total_frames / fps if fps > 0 else 0,
                    'totalFrames': total_frames,
                    'processedFrames': processed_frame_count,
                    'width': width,
                    'height': height
                },
                metadata={
                    'has_danger_alert': has_danger_alert,
                    'max_alert_level': max_alert,
                    'unique_tracks': len(unique_tracks),
                    'class_counts': class_counts if all_detections else {}
                }
            )
        
        return jsonify({
            'frames': frame_detections,
            'totalFrames': total_frames,
            'processedFrames': processed_frame_count,
            'fps': fps,
            'duration': total_frames / fps if fps > 0 else 0,
            'hasDangerAlert': has_danger_alert,
            'maxAlertLevel': max_alert,
            'uniqueTracks': len(unique_tracks),
            'mongoId': mongo_id  # ID MongoDB si sauvegardé
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Erreur lors du traitement vidéo: {error_msg}")
        import traceback
        traceback.print_exc()
        
        # Nettoyer le fichier temporaire en cas d'erreur
        if 'video_path' in locals() and os.path.exists(video_path):
            os.unlink(video_path)
        
        return jsonify({
            'error': f'Erreur lors du traitement vidéo: {error_msg}',
            'frames': [],
            'totalFrames': 0
        }), 500

@app.route('/api/export-csv', methods=['POST', 'OPTIONS'])
def export_csv():
    """Endpoint pour exporter les détections en CSV"""
    if request.method == 'OPTIONS':
        return '', 200
    
    if not MONGODB_AVAILABLE or not mongodb_service:
        return jsonify({'error': 'MongoDB non disponible'}), 500
    
    try:
        data = request.get_json()
        detections = data.get('detections', [])
        
        if not detections:
            return jsonify({'error': 'Aucune détection fournie'}), 400
        
        csv_content = mongodb_service.export_to_csv(detections)
        
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=detections.csv'}
        )
    
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'export CSV: {str(e)}'}), 500

@app.route('/api/export-mongodb', methods=['POST', 'OPTIONS'])
def export_mongodb():
    """Endpoint pour exporter manuellement les détections vers MongoDB"""
    if request.method == 'OPTIONS':
        return '', 200
    
    # Vérifier si MongoDB est disponible
    if not MONGODB_AVAILABLE or not mongodb_service:
        error_details = "Module MongoDB non importé"
        if mongodb_service is None:
            error_details = "Module mongodb_service non disponible. Installez pymongo: pip install pymongo python-dotenv"
        
        print(f"❌ MongoDB non disponible pour l'export: {error_details}")
        return jsonify({
            'error': 'MongoDB non disponible',
            'details': error_details,
            'help': 'Installez pymongo: pip install pymongo python-dotenv, puis redémarrez le serveur'
        }), 500
    
    # Vérifier si la connexion MongoDB est active, sinon tenter de reconnecter
    # IMPORTANT: Utiliser is not None au lieu de if collection (pymongo ne supporte pas le test de vérité)
    if mongodb_service.collection is None:
        print("⚠️ MongoDB non connecté, tentative de reconnexion...")
        if hasattr(mongodb_service, 'reconnect'):
            if mongodb_service.reconnect():
                print("✅ Reconnexion MongoDB réussie")
            else:
                print("❌ Échec de la reconnexion MongoDB")
                return jsonify({
                    'error': 'MongoDB non connecté. Impossible de se connecter à MongoDB.',
                    'details': 'Vérifiez que MongoDB est démarré et accessible. Consultez les logs du serveur pour plus de détails.',
                    'help': 'Pour démarrer MongoDB: docker-compose up -d mongodb (si vous utilisez Docker)'
                }), 500
        else:
            # Si pas de méthode reconnect, essayer de reconnecter manuellement
            print("⚠️ Tentative de reconnexion manuelle...")
            try:
                mongodb_service._connect()
                if mongodb_service.collection:
                    print("✅ Reconnexion MongoDB réussie")
                else:
                    print("❌ Échec de la reconnexion MongoDB")
                    return jsonify({
                        'error': 'MongoDB non connecté',
                        'details': 'La connexion MongoDB a échoué. Vérifiez que MongoDB est démarré.',
                        'help': 'Pour démarrer MongoDB: docker-compose up -d mongodb (si vous utilisez Docker)'
                    }), 500
            except Exception as e:
                print(f"❌ Erreur lors de la reconnexion: {e}")
                return jsonify({
                    'error': 'MongoDB non connecté',
                    'details': f'Erreur de connexion: {str(e)}',
                    'help': 'Pour démarrer MongoDB: docker-compose up -d mongodb (si vous utilisez Docker)'
                }), 500
    
    try:
        # Récupérer les données JSON
        data = request.get_json()
        if not data:
            print("❌ Aucune donnée JSON reçue")
            print(f"   Content-Type: {request.content_type}")
            print(f"   Data reçue: {request.data[:200] if request.data else 'Aucune'}")
            return jsonify({'error': 'Aucune donnée fournie. Vérifiez le format JSON.'}), 400
        
        # Extraire les données avec valeurs par défaut
        media_type = data.get('mediaType', data.get('media_type', 'image'))  # Support des deux formats
        filename = data.get('filename', data.get('image_filename', data.get('video_filename', 'unknown')))
        
        print(f"📤 Export MongoDB:")
        print(f"   Type: {media_type}")
        print(f"   Fichier: {filename}")
        print(f"   Clés disponibles: {list(data.keys())}")
        
        if media_type == 'video':
            # Gestion vidéo
            frames = data.get('frames', [])
            video_info = data.get('videoInfo', data.get('video_info', {}))
            
            if not frames:
                print("⚠️ Aucune frame fournie pour la vidéo")
                return jsonify({'error': 'Aucune frame fournie pour la vidéo'}), 400
            
            # Compter les détections dans toutes les frames
            total_detections = sum(len(frame.get('detections', [])) for frame in frames)
            
            print(f"   📹 Vidéo: {len(frames)} frames")
            print(f"   Détections totales: {total_detections}")
            print(f"   Info vidéo: {video_info}")
            
            mongo_id = mongodb_service.save_video_detection(
                frames=frames,
                video_filename=filename,
                video_info=video_info,
                metadata=data.get('metadata', {})
            )
        else:
            # Gestion image
            detections = data.get('detections', [])
            image_size = data.get('imageSize', data.get('image_size', {}))
            
            if not detections:
                print("⚠️ Aucune détection fournie pour l'image")
                return jsonify({'error': 'Aucune détection fournie pour l\'image'}), 400
            
            print(f"   🖼️ Image: {len(detections)} détections")
            print(f"   Taille image: {image_size}")
            
            # Afficher un exemple de détection pour debug
            if detections:
                print(f"   Exemple détection: {list(detections[0].keys())}")
            
            mongo_id = mongodb_service.save_image_detection(
                detections=detections,
                image_filename=filename,
                image_size=image_size,
                metadata=data.get('metadata', {})
            )
        
        if mongo_id:
            print(f"✅ Export MongoDB réussi: {mongo_id}")
            detection_count = len(detections) if media_type == 'image' else total_detections
            return jsonify({
                'success': True,
                'message': f'{detection_count} détection(s) exportée(s) vers MongoDB avec succès',
                'mongoId': mongo_id,
                'mediaType': media_type,
                'filename': filename,
                'detectionCount': detection_count
            })
        else:
            print("❌ Échec de la sauvegarde MongoDB (mongo_id est None)")
            print("   Vérifiez les logs MongoDB ci-dessus pour plus de détails")
            return jsonify({
                'error': 'Erreur lors de la sauvegarde MongoDB. Vérifiez la connexion et les logs du serveur.',
                'details': 'mongo_id est None - vérifiez les logs du serveur'
            }), 500
    
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        print(f"❌ Erreur lors de l'export MongoDB:")
        print(f"   Type: {error_type}")
        print(f"   Message: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Erreur lors de l\'export MongoDB: {error_msg}',
            'errorType': error_type
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Gestion des erreurs 404"""
    return jsonify({
        'error': 'Route non trouvée',
        'message': f'La route {request.path} n\'existe pas',
        'available_routes': ['/', '/api/health', '/api/detect', '/api/detect-video', '/api/export-csv', '/api/export-mongodb']
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Gestion des erreurs 500"""
    return jsonify({
        'error': 'Erreur interne du serveur',
        'message': str(error)
    }), 500

@app.before_request
def handle_preflight():
    """Gère les requêtes OPTIONS (CORS preflight)"""
    if request.method == "OPTIONS":
        response = jsonify({'status': 'ok'})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response

if __name__ == '__main__':
    if model is None:
        print("\n⚠️  ATTENTION: Le modèle n'est pas chargé!")
        print("Le serveur démarrera mais les détections ne fonctionneront pas.")
        print("Vérifiez que le fichier best.pt existe dans yolov8n_fod_final_v7/weights/\n")
    
    print("\n🌐 Démarrage du serveur Flask...")
    print("📍 URL: http://localhost:5000")
    print("📍 URL: http://127.0.0.1:5000")
    print("🔍 Health check: http://localhost:5000/api/health")
    print("\nAppuyez sur Ctrl+C pour arrêter le serveur\n")
    
    try:
        app.run(debug=True, port=5000, host='0.0.0.0')
    except Exception as e:
        print(f"\n❌ Erreur lors du démarrage du serveur: {e}")
        import traceback
        traceback.print_exc()

