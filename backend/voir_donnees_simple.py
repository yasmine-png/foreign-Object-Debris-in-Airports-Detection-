"""
Script simple pour voir les données MongoDB - Version simplifiée
"""
from pymongo import MongoClient
import json
from datetime import datetime

print("=" * 60)
print("📊 DONNÉES MONGODB - FOD DETECTION")
print("=" * 60)

try:
    # Connexion SANS authentification (où sont vos données)
    print("\n🔌 Connexion à MongoDB...")
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
    client.server_info()
    print("✅ Connecté à MongoDB")
    
    db = client['fod_detection']
    collection = db['detections']
    count = collection.count_documents({})
    
    print(f"\n📊 Nombre total de documents: {count}")
    
    if count == 0:
        print("\n⚠️ Aucun document trouvé dans la collection 'detections'")
        print("   Les détections seront sauvegardées ici après analyse d'images/vidéos")
    else:
        print(f"\n✅ {count} document(s) trouvé(s) !")
        
        # Statistiques
        images = collection.count_documents({"media_type": "image"})
        videos = collection.count_documents({"media_type": "video"})
        
        print(f"\n📈 Statistiques:")
        print(f"   - Images: {images}")
        print(f"   - Vidéos: {videos}")
        
        # Derniers documents
        print(f"\n📋 Derniers documents (5 plus récents):")
        print("-" * 60)
        for i, doc in enumerate(collection.find().sort("timestamp", -1).limit(5), 1):
            timestamp = doc.get('timestamp', 'N/A')
            if isinstance(timestamp, datetime):
                timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            
            media_type = doc.get('media_type', 'N/A')
            detection_count = doc.get('detection_count', 0)
            
            print(f"\n{i}. {timestamp}")
            print(f"   Type: {media_type}")
            print(f"   Détections: {detection_count}")
            
            if 'image_filename' in doc and doc['image_filename']:
                print(f"   Fichier: {doc['image_filename']}")
            if 'video_filename' in doc and doc['video_filename']:
                print(f"   Fichier: {doc['video_filename']}")
            
            if doc.get('has_danger_alert'):
                print(f"   🚨 ALERTE DANGER détectée !")
        
        # Afficher toutes les détections
        print(f"\n" + "=" * 60)
        print("📋 TOUTES LES DÉTECTIONS")
        print("=" * 60)
        
        for doc in collection.find().sort("timestamp", -1):
            timestamp = doc.get('timestamp', 'N/A')
            if isinstance(timestamp, datetime):
                timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"\n📄 Document ID: {doc.get('_id')}")
            print(f"   Timestamp: {timestamp}")
            print(f"   Type: {doc.get('media_type')}")
            print(f"   Détections: {doc.get('detection_count', 0)}")
            
            if 'image_filename' in doc:
                print(f"   Image: {doc.get('image_filename', 'N/A')}")
            if 'video_filename' in doc:
                print(f"   Vidéo: {doc.get('video_filename', 'N/A')}")
            
            # Afficher quelques détections
            detections = doc.get('detections', [])
            if detections:
                print(f"   Objets détectés:")
                for det in detections[:5]:  # Afficher les 5 premiers
                    label = det.get('label', 'N/A')
                    confidence = det.get('confidence', 0)
                    risk = det.get('riskLevel', 'N/A')
                    print(f"     - {label} (confiance: {confidence:.2f}, risque: {risk})")
                if len(detections) > 5:
                    print(f"     ... et {len(detections) - 5} autres")
    
    client.close()
    
except Exception as e:
    print(f"\n❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✅ TERMINÉ")
print("=" * 60)

