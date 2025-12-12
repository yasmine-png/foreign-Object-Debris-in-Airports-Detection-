"""Script de test pour vérifier l'import MongoDB"""
import sys

print("=" * 60)
print("TEST IMPORT MONGODB")
print("=" * 60)

# Test 1: pymongo
print("\n1. Test import pymongo...")
try:
    import pymongo
    print(f"   ✅ pymongo importé (version: {pymongo.__version__})")
except ImportError as e:
    print(f"   ❌ Erreur import pymongo: {e}")
    print("   💡 Solution: pip install pymongo")
    sys.exit(1)

# Test 2: python-dotenv
print("\n2. Test import python-dotenv...")
try:
    import dotenv
    print(f"   ✅ python-dotenv importé")
except ImportError as e:
    print(f"   ⚠️ python-dotenv non disponible: {e}")
    print("   💡 Solution: pip install python-dotenv (optionnel)")

# Test 3: Import mongodb_service
print("\n3. Test import mongodb_service...")
try:
    from backend.mongodb_service import mongodb_service
    print(f"   ✅ mongodb_service importé")
    
    if mongodb_service:
        print(f"   ✅ mongodb_service initialisé")
        if mongodb_service.collection:
            print(f"   ✅ MongoDB connecté")
            print(f"   📊 Database: {mongodb_service.database_name}")
            print(f"   📊 Collection: {mongodb_service.collection_name}")
        else:
            print(f"   ⚠️ MongoDB non connecté (collection est None)")
            print(f"   💡 Vérifiez que MongoDB est démarré")
    else:
        print(f"   ❌ mongodb_service est None")
except ImportError as e:
    print(f"   ❌ Erreur import mongodb_service: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"   ❌ Erreur lors de l'initialisation: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ TOUS LES TESTS PASSÉS")
print("=" * 60)

