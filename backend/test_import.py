#!/usr/bin/env python
"""Test simple pour vérifier l'import MongoDB"""
import sys
import os

print("Test d'import MongoDB...")
print(f"Répertoire actuel: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}")

try:
    from mongodb_service import mongodb_service
    print(f"✅ Import réussi!")
    print(f"   mongodb_service: {mongodb_service}")
    print(f"   Type: {type(mongodb_service)}")
    if mongodb_service:
        print(f"   Collection: {mongodb_service.collection if mongodb_service.collection else 'None (non connecté)'}")
    else:
        print("   ❌ mongodb_service est None")
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

