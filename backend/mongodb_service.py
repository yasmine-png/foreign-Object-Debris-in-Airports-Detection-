"""
Service MongoDB pour stocker les détections FOD
"""
from pymongo import MongoClient
from datetime import datetime
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class MongoDBService:
    """Service pour gérer les opérations MongoDB"""
    
    def __init__(self):
        # Configuration MongoDB
        # Par défaut: MongoDB Docker (localhost:27017), sinon utiliser les variables d'environnement
        # Pour Docker avec authentification: mongodb://admin:admin123@localhost:27017/
        # Pour Docker sans authentification: mongodb://localhost:27017/
        
        mongo_uri = os.getenv('MONGODB_URI', None)
        mongo_user = os.getenv('MONGODB_USER', 'admin')
        mongo_password = os.getenv('MONGODB_PASSWORD', 'admin123')
        
        # Construire l'URI avec authentification
        # Par défaut, utiliser l'authentification Docker (admin/admin123)
        if mongo_uri:
            # Si URI fournie, l'utiliser telle quelle
            if '@' not in mongo_uri and mongo_user and mongo_password:
                # Ajouter l'authentification si pas déjà présente
                if mongo_uri.startswith('mongodb://'):
                    host = mongo_uri.replace('mongodb://', '').rstrip('/')
                    self.mongo_uri = f'mongodb://{mongo_user}:{mongo_password}@{host}/'
                else:
                    self.mongo_uri = f'mongodb://{mongo_user}:{mongo_password}@localhost:27017/'
            else:
                self.mongo_uri = mongo_uri
        else:
            # Par défaut: MongoDB Docker avec authentification
            # Essayer d'abord avec authentification, puis sans
            self.mongo_uri = f'mongodb://{mongo_user}:{mongo_password}@localhost:27017/'
        
        self.database_name = os.getenv('MONGODB_DATABASE', 'fod_detection')
        self.collection_name = os.getenv('MONGODB_COLLECTION', 'detections')
        
        self.client = None
        self.db = None
        self.collection = None
        
        self._connect()
    
    def _connect(self):
        """Établir la connexion à MongoDB"""
        # Essayer d'abord avec l'URI configurée
        try:
            print(f"🔌 Tentative de connexion MongoDB: {self.mongo_uri.split('@')[-1] if '@' in self.mongo_uri else self.mongo_uri}")
            
            # Timeout de connexion pour Docker
            # Ajouter authSource si authentification présente
            client_kwargs = {
                'serverSelectionTimeoutMS': 5000,  # 5 secondes
                'connectTimeoutMS': 5000
            }
            if '@' in self.mongo_uri:
                # Si authentification présente, spécifier authSource
                client_kwargs['authSource'] = 'admin'
            
            self.client = MongoClient(
                self.mongo_uri,
                **client_kwargs
            )
            
            # Tester la connexion
            self.client.server_info()
            
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            
            # Créer un index sur timestamp pour les requêtes rapides
            try:
                self.collection.create_index([("timestamp", -1)])
                self.collection.create_index([("media_type", 1)])
                self.collection.create_index([("detections.riskLevel", 1)])
            except Exception as idx_error:
                print(f"⚠️ Erreur lors de la création des index (peut être ignoré): {idx_error}")
            
            print(f"✅ MongoDB connecté: {self.database_name}.{self.collection_name}")
            print(f"   URI: {self.mongo_uri.split('@')[-1] if '@' in self.mongo_uri else self.mongo_uri}")
            return
        
        except Exception as e:
            print(f"⚠️ Échec connexion MongoDB avec authentification: {e}")
            
            # Si l'URI contient une authentification, essayer sans
            if '@' in self.mongo_uri:
                try:
                    print("🔄 Tentative de connexion sans authentification...")
                    # Extraire juste l'host
                    if 'mongodb://' in self.mongo_uri:
                        host = self.mongo_uri.split('@')[-1] if '@' in self.mongo_uri else self.mongo_uri.replace('mongodb://', '')
                        fallback_uri = f'mongodb://{host}'
                    else:
                        fallback_uri = 'mongodb://localhost:27017/'
                    
                    self.client = MongoClient(
                        fallback_uri,
                        serverSelectionTimeoutMS=5000,
                        connectTimeoutMS=5000
                    )
                    self.client.server_info()
                    
                    self.db = self.client[self.database_name]
                    self.collection = self.db[self.collection_name]
                    
                    print(f"✅ MongoDB connecté sans authentification: {self.database_name}.{self.collection_name}")
                    print(f"   URI: {fallback_uri}")
                    return
                except Exception as e2:
                    print(f"⚠️ Échec connexion sans authentification: {e2}")
            
            print(f"❌ Erreur connexion MongoDB: {e}")
            print(f"   Type d'erreur: {type(e).__name__}")
            print("⚠️ Vérifiez que MongoDB est démarré:")
            print("   - Docker: docker-compose up -d mongodb")
            print("   - Local: mongod --dbpath C:\\data\\db")
            print("   - Vérifiez les logs: docker logs fod_mongodb")
            print("⚠️ Les détections ne seront pas sauvegardées dans MongoDB")
            self.client = None
            self.db = None
            self.collection = None
    
    def reconnect(self):
        """Tenter de reconnecter à MongoDB"""
        print("🔄 Tentative de reconnexion à MongoDB...")
        self._connect()
        return self.collection is not None
    
    def is_connected(self):
        """Vérifier si MongoDB est connecté"""
        if self.collection is None:
            return False
        try:
            # Tester la connexion
            self.client.server_info()
            return True
        except:
            return False
    
    def save_image_detection(self, 
                            detections: List[Dict],
                            image_filename: Optional[str] = None,
                            image_size: Optional[Dict] = None,
                            metadata: Optional[Dict] = None) -> Optional[str]:
        """
        Sauvegarder les détections d'une image dans MongoDB
        
        Args:
            detections: Liste des détections
            image_filename: Nom du fichier image
            image_size: Taille de l'image {'width': int, 'height': int}
            metadata: Métadonnées supplémentaires
        
        Returns:
            ID du document créé ou None si erreur
        """
        if self.collection is None:
            print("⚠️ MongoDB non connecté - détections non sauvegardées")
            print("   Vérifiez la connexion MongoDB dans les logs de démarrage")
            return None
        
        try:
            # Nettoyer les détections (enlever les objets non sérialisables)
            cleaned_detections = []
            for det in detections:
                cleaned_det = {}
                for key, value in det.items():
                    # Ignorer les champs non sérialisables
                    if key not in ['segmentationMask']:  # Ignorer les masques base64 trop volumineux
                        try:
                            # Tester la sérialisation
                            import json
                            json.dumps(value)
                            cleaned_det[key] = value
                        except (TypeError, ValueError):
                            # Ignorer les valeurs non sérialisables
                            pass
                cleaned_detections.append(cleaned_det)
            
            document = {
                'timestamp': datetime.utcnow(),
                'media_type': 'image',
                'image_filename': image_filename,
                'image_size': image_size,
                'detections': cleaned_detections,
                'detection_count': len(cleaned_detections),
                'has_danger_alert': any(d.get('alertLevel', 0) == 3 for d in cleaned_detections),
                'max_alert_level': max([d.get('alertLevel', 1) for d in cleaned_detections], default=1),
                'metadata': metadata or {}
            }
            
            result = self.collection.insert_one(document)
            print(f"✅ {len(cleaned_detections)} détections sauvegardées dans MongoDB (ID: {result.inserted_id})")
            return str(result.inserted_id)
        
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde MongoDB: {e}")
            print(f"   Type d'erreur: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return None
    
    def save_video_detection(self,
                            frames: List[Dict],
                            video_filename: Optional[str] = None,
                            video_info: Optional[Dict] = None,
                            metadata: Optional[Dict] = None) -> Optional[str]:
        """
        Sauvegarder les détections d'une vidéo dans MongoDB
        TOUTES les détections de toutes les frames sont sauvegardées
        
        Args:
            frames: Liste des frames avec détections
            video_filename: Nom du fichier vidéo
            video_info: Infos vidéo {'fps': float, 'duration': float, 'totalFrames': int}
            metadata: Métadonnées supplémentaires
        
        Returns:
            ID du document créé ou None si erreur
        """
        if self.collection is None:
            print("⚠️ MongoDB non connecté - détections non sauvegardées")
            print("   Vérifiez la connexion MongoDB dans les logs de démarrage")
            return None
        
        try:
            # Compter TOUTES les détections de TOUTES les frames
            all_detections = []
            frames_with_detections = 0
            
            # Nettoyer les frames (enlever les données non sérialisables)
            cleaned_frames = []
            
            for frame_idx, frame in enumerate(frames):
                frame_detections = frame.get('detections', [])
                
                # Nettoyer les détections de cette frame
                cleaned_frame_detections = []
                for det in frame_detections:
                    cleaned_det = {}
                    for key, value in det.items():
                        # Ignorer les champs non sérialisables (masques base64 trop volumineux)
                        if key not in ['segmentationMask', 'hasSegmentation']:
                            try:
                                # Tester la sérialisation
                                import json
                                json.dumps(value)
                                cleaned_det[key] = value
                            except (TypeError, ValueError):
                                # Ignorer les valeurs non sérialisables
                                pass
                    
                    if cleaned_det:
                        cleaned_det['frame_number'] = frame.get('frame', frame_idx)
                        cleaned_det['frame_time'] = frame.get('time', 0)
                        cleaned_frame_detections.append(cleaned_det)
                        all_detections.append(cleaned_det)
                
                if cleaned_frame_detections:
                    frames_with_detections += 1
                
                # Créer une frame nettoyée
                cleaned_frame = {
                    'frame': frame.get('frame', frame_idx),
                    'time': frame.get('time', 0),
                    'detections': cleaned_frame_detections,
                    'count': len(cleaned_frame_detections)
                }
                cleaned_frames.append(cleaned_frame)
            
            print(f"📹 Préparation sauvegarde vidéo: {len(frames)} frames, {frames_with_detections} frames avec détections, {len(all_detections)} détections totales")
            
            document = {
                'timestamp': datetime.utcnow(),
                'media_type': 'video',
                'video_filename': video_filename,
                'video_info': video_info or {},
                'frames': cleaned_frames,  # Frames nettoyées
                'total_frames': len(cleaned_frames),
                'frames_with_detections': frames_with_detections,
                'detections': all_detections,  # TOUTES les détections de toutes les frames
                'detection_count': len(all_detections),
                'has_danger_alert': any(d.get('alertLevel', 0) == 3 for d in all_detections),
                'max_alert_level': max([d.get('alertLevel', 1) for d in all_detections], default=1),
                'metadata': metadata or {}
            }
            
            result = self.collection.insert_one(document)
            print(f"✅ Vidéo sauvegardée dans MongoDB:")
            print(f"   📁 Fichier: {video_filename}")
            print(f"   🎬 Frames: {len(cleaned_frames)} totales, {frames_with_detections} avec détections")
            print(f"   📦 Détections: {len(all_detections)} objets détectés")
            print(f"   🆔 ID MongoDB: {result.inserted_id}")
            
            return str(result.inserted_id)
        
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde MongoDB: {e}")
            print(f"   Type d'erreur: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_recent_detections(self, limit: int = 100):
        """Récupérer les détections récentes"""
        if self.collection is None:
            return []
        
        try:
            return list(self.collection.find().sort('timestamp', -1).limit(limit))
        except Exception as e:
            print(f"❌ Erreur lors de la récupération: {e}")
            return []
    
    def export_to_csv(self, detections: List[Dict]) -> str:
        """
        Exporter les détections en format CSV
        
        Args:
            detections: Liste des détections
        
        Returns:
            Contenu CSV en string
        """
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # En-têtes
        writer.writerow([
            'ID', 'Label', 'Confidence', 'Risk Level', 'Alert Level', 
            'Size (cm)', 'Size (m)', 'Position', 'BBox X (%)', 'BBox Y (%)', 
            'BBox Width (%)', 'BBox Height (%)'
        ])
        
        # Données
        for det in detections:
            writer.writerow([
                det.get('id', ''),
                det.get('label', ''),
                f"{det.get('confidence', 0):.3f}",
                det.get('riskLevel', ''),
                det.get('alertLevel', ''),
                det.get('sizeCm', ''),
                det.get('sizeMeters', ''),
                det.get('position', ''),
                f"{det.get('bbox', {}).get('x', 0):.2f}",
                f"{det.get('bbox', {}).get('y', 0):.2f}",
                f"{det.get('bbox', {}).get('width', 0):.2f}",
                f"{det.get('bbox', {}).get('height', 0):.2f}"
            ])
        
        return output.getvalue()
    
    def close(self):
        """Fermer la connexion MongoDB"""
        if self.client:
            self.client.close()
            print("✅ Connexion MongoDB fermée")

# Instance globale
mongodb_service = MongoDBService()

