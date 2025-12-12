"""
Script de test pour vérifier que le serveur backend fonctionne correctement
"""
import requests
import time
import sys

def test_server():
    """Teste que le serveur répond correctement"""
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Test du serveur backend...")
    print(f"📍 URL: {base_url}\n")
    
    # Test 1: Health check
    print("1️⃣ Test du endpoint /api/health...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Serveur répond: {data}")
            if data.get('model_loaded'):
                print("   ✅ Modèle chargé correctement")
            else:
                print("   ⚠️  Modèle non chargé")
        else:
            print(f"   ❌ Erreur HTTP: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Impossible de se connecter au serveur")
        print("   💡 Assurez-vous que le serveur est démarré avec: python app.py")
        return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False
    
    print("\n✅ Tous les tests sont passés!")
    return True

if __name__ == "__main__":
    # Attendre un peu que le serveur démarre si nécessaire
    if len(sys.argv) > 1 and sys.argv[1] == "--wait":
        print("⏳ Attente de 3 secondes pour que le serveur démarre...")
        time.sleep(3)
    
    success = test_server()
    sys.exit(0 if success else 1)

