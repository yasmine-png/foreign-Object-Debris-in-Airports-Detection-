"""
Script pour démarrer le serveur et tester toutes les routes
"""
import subprocess
import time
import requests
import sys
from pathlib import Path

def test_server():
    """Teste toutes les routes du serveur"""
    base_url = "http://127.0.0.1:5000"
    
    print("\n" + "="*70)
    print("🧪 TEST COMPLET DU BACKEND FOD DETECTION")
    print("="*70 + "\n")
    
    # Test 1: Route racine
    print("1️⃣  Test de la route racine (/)...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ OK - Status: {response.status_code}")
            print(f"   📄 Message: {data.get('message')}")
            print(f"   📦 Version: {data.get('version')}")
            print(f"   🔗 Endpoints: {list(data.get('endpoints', {}).values())}\n")
        else:
            print(f"   ❌ Erreur - Status: {response.status_code}\n")
    except Exception as e:
        print(f"   ❌ Erreur de connexion: {e}\n")
        return False
    
    # Test 2: Route health
    print("2️⃣  Test de la route health (/api/health)...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ OK - Status: {response.status_code}")
            print(f"   📊 Status serveur: {data.get('status')}")
            print(f"   🤖 Modèle chargé: {data.get('model_loaded')}\n")
        else:
            print(f"   ❌ Erreur - Status: {response.status_code}\n")
    except Exception as e:
        print(f"   ❌ Erreur: {e}\n")
        return False
    
    # Test 3: Route detect sans image (doit retourner 400)
    print("3️⃣  Test de la route detect sans image (doit retourner 400)...")
    try:
        response = requests.post(f"{base_url}/api/detect", timeout=5)
        if response.status_code == 400:
            data = response.json()
            print(f"   ✅ OK - Status: {response.status_code} (attendu)")
            print(f"   📝 Message: {data.get('error', 'N/A')}\n")
        else:
            print(f"   ⚠️  Status inattendu: {response.status_code}\n")
    except Exception as e:
        print(f"   ❌ Erreur: {e}\n")
    
    # Test 4: Route inexistante (doit retourner 404)
    print("4️⃣  Test de route inexistante (doit retourner 404)...")
    try:
        response = requests.get(f"{base_url}/api/route-inexistante", timeout=5)
        if response.status_code == 404:
            data = response.json()
            print(f"   ✅ OK - Status: {response.status_code} (attendu)")
            print(f"   📝 Message: {data.get('error', 'N/A')}\n")
        else:
            print(f"   ⚠️  Status inattendu: {response.status_code}\n")
    except Exception as e:
        print(f"   ❌ Erreur: {e}\n")
    
    # Test 5: Favicon
    print("5️⃣  Test de la route favicon (/favicon.ico)...")
    try:
        response = requests.get(f"{base_url}/favicon.ico", timeout=5)
        if response.status_code == 204:
            print(f"   ✅ OK - Status: {response.status_code} (No Content)\n")
        else:
            print(f"   ⚠️  Status: {response.status_code}\n")
    except Exception as e:
        print(f"   ❌ Erreur: {e}\n")
    
    print("="*70)
    print("✅✅✅ TOUS LES TESTS SONT TERMINÉS ✅✅✅")
    print("="*70 + "\n")
    
    return True

if __name__ == "__main__":
    print("\n⏳ Attente de 3 secondes pour que le serveur démarre...\n")
    time.sleep(3)
    test_server()

