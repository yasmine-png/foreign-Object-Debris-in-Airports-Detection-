"""
Script de diagnostic MongoDB pour FOD Detection
Vérifie la connexion et l'état de MongoDB
"""
import sys
import os

print("=" * 60)
print("🔍 DIAGNOSTIC MONGODB")
print("=" * 60)

# 1. Vérifier si MongoDB est démarré (Docker)
print("\n1️⃣ Vérification Docker MongoDB...")
try:
    import subprocess
    result = subprocess.run(
        ["docker", "ps", "--filter", "name=fod_mongodb", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
        timeout=5
    )
    if "fod_mongodb" in result.stdout:
        print("✅ Conteneur MongoDB Docker est en cours d'exécution")
    else:
        print("❌ Conteneur MongoDB Docker n'est PAS en cours d'exécution")
        print("   💡 Solution: docker-compose up -d mongodb")
        sys.exit(1)
except FileNotFoundError:
    print("⚠️ Docker n'est pas installé ou pas dans le PATH")
except Exception as e:
    print(f"⚠️ Erreur lors de la vérification Docker: {e}")

# 2. Tester la connexion MongoDB
print("\n2️⃣ Test de connexion MongoDB...")
try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    
    # Essayer avec authentification
    client = None
    auth_required = None
    try:
        print("   Tentative avec authentification (admin/admin123)...")
        client = MongoClient(
            "mongodb://admin:admin123@localhost:27017/",
            serverSelectionTimeoutMS=3000,
            authSource='admin'
        )
        client.server_info()
        print("✅ Connexion réussie avec authentification")
        auth_required = True
    except Exception as e:
        print(f"   ⚠️ Échec avec authentification: {str(e)[:100]}")
        # Essayer sans authentification
        try:
            print("   Tentative sans authentification...")
            client = MongoClient(
                "mongodb://localhost:27017/",
                serverSelectionTimeoutMS=3000
            )
            client.server_info()
            print("✅ Connexion réussie sans authentification")
            auth_required = False
        except Exception as e2:
            print(f"❌ Échec de connexion: {e2}")
            print("   💡 Vérifiez que MongoDB est démarré: docker-compose up -d mongodb")
            sys.exit(1)
    
    # 3. Vérifier la base de données
    print("\n3️⃣ Vérification de la base de données...")
    db = client['fod_detection']
    collections = db.list_collection_names()
    print(f"   Collections trouvées: {collections}")
    
    # 4. Vérifier la collection detections
    print("\n4️⃣ Vérification de la collection 'detections'...")
    collection = db['detections']
    count = collection.count_documents({})
    print(f"   📊 Nombre de documents: {count}")
    
    if count == 0:
        print("\n⚠️ Aucune détection trouvée dans MongoDB")
        print("\n📋 Raisons possibles:")
        print("   1. Aucune détection n'a été effectuée depuis le démarrage du backend")
        print("   2. Le backend n'est pas connecté à MongoDB")
        print("   3. Les détections n'ont pas été sauvegardées (erreur silencieuse)")
        print("\n💡 Solutions:")
        print("   1. Vérifiez les logs du backend au démarrage:")
        print("      - Cherchez: '✅ MongoDB connecté'")
        print("      - Ou: '❌ Erreur connexion MongoDB'")
        print("   2. Effectuez une détection (image ou vidéo) via l'interface")
        print("   3. Vérifiez les logs du backend après une détection:")
        print("      - Cherchez: '✅ X détections sauvegardées dans MongoDB'")
    else:
        print(f"✅ {count} document(s) trouvé(s)")
        
        # Afficher un exemple
        print("\n5️⃣ Exemple de document:")
        sample = collection.find_one()
        if sample:
            print(f"   Timestamp: {sample.get('timestamp', 'N/A')}")
            print(f"   Type média: {sample.get('media_type', 'N/A')}")
            print(f"   Nombre de détections: {sample.get('detection_count', 0)}")
            if 'image_filename' in sample:
                print(f"   Fichier image: {sample.get('image_filename', 'N/A')}")
            if 'video_filename' in sample:
                print(f"   Fichier vidéo: {sample.get('video_filename', 'N/A')}")
    
    # 5. Vérifier le service MongoDB du backend
    print("\n6️⃣ Vérification du service MongoDB du backend...")
    try:
        # Changer vers le répertoire backend
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(backend_dir)
        
        from mongodb_service import mongodb_service
        
        if mongodb_service:
            if mongodb_service.is_connected():
                print("✅ Service MongoDB du backend est connecté")
                print(f"   URI: {mongodb_service.mongo_uri.split('@')[-1] if '@' in mongodb_service.mongo_uri else mongodb_service.mongo_uri}")
                print(f"   Database: {mongodb_service.database_name}")
                print(f"   Collection: {mongodb_service.collection_name}")
            else:
                print("❌ Service MongoDB du backend n'est PAS connecté")
                print("   💡 Le backend doit être redémarré après avoir démarré MongoDB")
        else:
            print("❌ Service MongoDB du backend n'est pas disponible")
    except Exception as e:
        print(f"⚠️ Erreur lors de la vérification du service: {e}")
        import traceback
        traceback.print_exc()
    
    client.close()
    
except ImportError:
    print("❌ pymongo n'est pas installé")
    print("   💡 Solution: pip install pymongo")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ DIAGNOSTIC TERMINÉ")
print("=" * 60)

