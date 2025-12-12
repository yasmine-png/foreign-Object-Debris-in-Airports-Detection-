#!/bin/bash

echo "Démarrage du serveur Flask pour la détection FOD..."
echo ""

# Activer l'environnement virtuel si il existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Lancer le serveur
python app.py

