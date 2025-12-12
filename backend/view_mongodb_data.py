#!/usr/bin/env python
"""
Script pour visualiser les données MongoDB
Utilisation: python view_mongodb_data.py
"""
from mongodb_service import mongodb_service
from datetime import datetime
import json

def print_separator():
    print("=" * 80)

def format_date(date):
    """Formater une date pour l'affichage"""
    if isinstance(date, datetime):
        return date.strftime("%Y-%m-%d %H:%M:%S")
    return str(date)

def view_all_detections():
    """Afficher toutes les détections"""
    if not mongodb_service or mongodb_service.collection is None:
        print("❌ MongoDB non connecté")
        return
    
    print_separator()
    print("📊 TOUTES LES DÉTECTIONS DANS MONGODB")
    print_separator()
    
    try:
        # Récupérer toutes les détections
        detections = mongodb_service.collection.find().sort("timestamp", -1)
        count = mongodb_service.collection.count_documents({})
        
        print(f"\n📦 Nombre total de documents: {count}\n")
        
        for idx, doc in enumerate(detections, 1):
            print(f"\n{'='*80}")
            print(f"📄 Document #{idx} (ID: {doc['_id']})")
            print(f"{'='*80}")
            print(f"📅 Date: {format_date(doc.get('timestamp'))}")
            print(f"📁 Type: {doc.get('media_type', 'unknown')}")
            
            if doc.get('media_type') == 'image':
                print(f"🖼️  Fichier image: {doc.get('image_filename', 'unknown')}")
                size = doc.get('image_size', {})
                if size:
                    print(f"   Dimensions: {size.get('width')}x{size.get('height')} pixels")
            elif doc.get('media_type') == 'video':
                print(f"🎬 Fichier vidéo: {doc.get('video_filename', 'unknown')}")
                video_info = doc.get('video_info', {})
                if video_info:
                    print(f"   FPS: {video_info.get('fps', 'N/A')}")
                    print(f"   Durée: {video_info.get('duration', 'N/A')} secondes")
                    print(f"   Frames totales: {video_info.get('totalFrames', 'N/A')}")
            
            print(f"🔍 Nombre de détections: {doc.get('detection_count', 0)}")
            print(f"🚨 Alerte danger: {'Oui' if doc.get('has_danger_alert') else 'Non'}")
            print(f"⚠️  Niveau d'alerte max: {doc.get('max_alert_level', 0)}")
            
            # Afficher quelques détections d'exemple
            detections_list = doc.get('detections', [])
            if detections_list:
                print(f"\n📋 Exemples d'objets détectés (premiers 5):")
                for i, det in enumerate(detections_list[:5], 1):
                    print(f"   {i}. {det.get('label', 'Unknown')} - Confiance: {det.get('confidence', 0):.2%} - "
                          f"Risque: {det.get('riskLevel', 'N/A')} - Alerte: {det.get('alertLevel', 0)}")
                if len(detections_list) > 5:
                    print(f"   ... et {len(detections_list) - 5} autres objets")
        
        print_separator()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

def view_statistics():
    """Afficher les statistiques"""
    if not mongodb_service or mongodb_service.collection is None:
        print("❌ MongoDB non connecté")
        return
    
    print_separator()
    print("📊 STATISTIQUES MONGODB")
    print_separator()
    
    try:
        total_docs = mongodb_service.collection.count_documents({})
        images = mongodb_service.collection.count_documents({"media_type": "image"})
        videos = mongodb_service.collection.count_documents({"media_type": "video"})
        
        # Compter les objets détectés
        pipeline = [
            {"$unwind": "$detections"},
            {"$group": {
                "_id": "$detections.label",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        
        objects_count = list(mongodb_service.collection.aggregate(pipeline))
        
        print(f"\n📦 Documents totaux: {total_docs}")
        print(f"🖼️  Images: {images}")
        print(f"🎬 Vidéos: {videos}")
        
        if objects_count:
            print(f"\n🔍 Objets détectés (par type):")
            for obj in objects_count:
                print(f"   • {obj['_id']}: {obj['count']} fois")
        
        # Alertes danger
        danger_count = mongodb_service.collection.count_documents({"has_danger_alert": True})
        print(f"\n🚨 Documents avec alerte danger: {danger_count}")
        
        print_separator()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

def export_to_json(filename="mongodb_export.json"):
    """Exporter toutes les données en JSON"""
    if not mongodb_service or mongodb_service.collection is None:
        print("❌ MongoDB non connecté")
        return
    
    try:
        detections = list(mongodb_service.collection.find())
        
        # Convertir ObjectId en string pour JSON
        for doc in detections:
            doc['_id'] = str(doc['_id'])
            if 'timestamp' in doc and isinstance(doc['timestamp'], datetime):
                doc['timestamp'] = doc['timestamp'].isoformat()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(detections, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Données exportées dans: {filename}")
        print(f"   {len(detections)} documents exportés")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'export: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🔍 VISUALISATION DES DONNÉES MONGODB")
    print("="*80)
    
    if not mongodb_service or mongodb_service.collection is None:
        print("❌ MongoDB non connecté")
        print("   Vérifiez que MongoDB est démarré: docker-compose up -d mongodb")
        exit(1)
    
    print("\n1. Statistiques")
    view_statistics()
    
    print("\n2. Toutes les détections")
    view_all_detections()
    
    print("\n3. Export JSON")
    export_to_json()
    
    print("\n✅ Terminé!")

