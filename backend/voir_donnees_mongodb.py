"""
Script simple pour voir les données MongoDB
"""
from pymongo import MongoClient

print("=" * 60)
print("📊 DONNÉES MONGODB")
print("=" * 60)

# Essayer d'abord sans authentification (où sont les données)
try:
    print("\n1️⃣ Connexion SANS authentification...")
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
    client.server_info()
    print("✅ Connecté")
    
    db = client['fod_detection']
    collection = db['detections']
    count = collection.count_documents({})
    
    print(f"\n📊 Nombre de documents: {count}")
    
    if count > 0:
        print("\n📋 Derniers documents:")
        for doc in collection.find().sort("timestamp", -1).limit(5):
            print(f"  - {doc.get('timestamp')} | {doc.get('media_type')} | {doc.get('detection_count', 0)} détections")
            if 'image_filename' in doc:
                print(f"    Fichier: {doc.get('image_filename')}")
            if 'video_filename' in doc:
                print(f"    Fichier: {doc.get('video_filename')}")
    else:
        print("⚠️ Aucun document trouvé")
    
    client.close()
    
except Exception as e:
    print(f"❌ Erreur: {e}")

# Essayer avec authentification
try:
    print("\n2️⃣ Connexion AVEC authentification...")
    client = MongoClient(
        "mongodb://admin:admin123@localhost:27017/",
        serverSelectionTimeoutMS=3000,
        authSource='admin'
    )
    client.server_info()
    print("✅ Connecté")
    
    db = client['fod_detection']
    collection = db['detections']
    count = collection.count_documents({})
    
    print(f"\n📊 Nombre de documents: {count}")
    
    if count > 0:
        print("\n📋 Derniers documents:")
        for doc in collection.find().sort("timestamp", -1).limit(5):
            print(f"  - {doc.get('timestamp')} | {doc.get('media_type')} | {doc.get('detection_count', 0)} détections")
    else:
        print("⚠️ Aucun document trouvé (base vide avec authentification)")
    
    client.close()
    
except Exception as e:
    print(f"❌ Erreur: {e}")

print("\n" + "=" * 60)

