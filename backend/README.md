# Backend FOD Detection - YOLOv8

Backend Flask pour la détection d'objets FOD (Foreign Object Debris) utilisant un modèle YOLOv8 pré-entraîné.

## Prérequis

- Python 3.8 ou supérieur
- pip

## Installation

1. Créer un environnement virtuel (recommandé) :
```bash
python -m venv venv
```

2. Activer l'environnement virtuel :
- Sur Windows :
```bash
venv\Scripts\activate
```
- Sur Linux/Mac :
```bash
source venv/bin/activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Configuration

Le chemin du modèle est défini dans `app.py` :
```python
MODEL_PATH = r"C:\Users\ybouk\OneDrive\Bureau\projet_fod\yolov8n_fod_final_v7\weights\best.pt"
```

Si votre modèle est à un autre emplacement, modifiez cette variable.

## Démarrage

Lancer le serveur Flask :
```bash
python app.py
```

Le serveur sera accessible sur `http://localhost:5000`

## API Endpoints

### GET /api/health
Vérifie que le serveur fonctionne et que le modèle est chargé.

**Réponse :**
```json
{
  "status": "ok",
  "model_loaded": true
}
```

### POST /api/detect
Effectue une détection d'objets sur une image.

**Requête :**
- Content-Type: `multipart/form-data`
- Body: fichier image dans le champ `image`

**Réponse :**
```json
{
  "detections": [
    {
      "id": "0_0",
      "label": "class_name",
      "confidence": 0.95,
      "riskLevel": "High",
      "position": "Zone A1 · 5.7 m from threshold",
      "bbox": {
        "x": 15.5,
        "y": 20.3,
        "width": 8.2,
        "height": 6.1
      }
    }
  ],
  "count": 1
}
```

## Notes

- Le modèle est chargé une seule fois au démarrage du serveur
- Les images sont traitées avec un seuil de confiance minimum de 0.25
- Les coordonnées des bounding boxes sont retournées en pourcentage de l'image

