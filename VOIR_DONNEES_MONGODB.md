# 📊 Comment voir les données MongoDB

## 🎯 Méthode 1 : Script Python (Recommandé)

### Utilisation
```bash
cd backend
python view_mongodb_data.py
```

Ce script affiche :
- ✅ Toutes les détections avec leurs détails
- ✅ Statistiques (nombre d'images, vidéos, objets détectés)
- ✅ Export en JSON pour analyse

---

## 🎯 Méthode 2 : MongoDB Compass (Interface Graphique)

### Installation
1. Téléchargez MongoDB Compass : https://www.mongodb.com/try/download/compass
2. Installez-le sur votre ordinateur

### Connexion
1. Ouvrez MongoDB Compass
2. Connectez-vous avec :
   - **URI** : `mongodb://localhost:27017`
   - Ou cliquez sur "Fill in connection fields individually" :
     - **Host** : `localhost`
     - **Port** : `27017`
     - **Authentication** : None (ou admin/admin123 si configuré)

### Voir les données
1. Sélectionnez la base de données : `fod_detection`
2. Sélectionnez la collection : `detections`
3. Vous verrez tous les documents avec leurs détections

---

## 🎯 Méthode 3 : Ligne de commande (mongosh)

### Accéder à MongoDB
```bash
docker exec -it fod_mongodb mongosh
```

### Commandes utiles

#### Voir toutes les bases de données
```javascript
show dbs
```

#### Utiliser la base de données
```javascript
use fod_detection
```

#### Voir toutes les détections
```javascript
db.detections.find().pretty()
```

#### Compter les documents
```javascript
db.detections.countDocuments()
```

#### Voir la dernière détection
```javascript
db.detections.findOne().sort({timestamp: -1})
```

#### Voir les détections avec alerte danger
```javascript
db.detections.find({has_danger_alert: true}).pretty()
```

#### Compter les objets par type
```javascript
db.detections.aggregate([
  {$unwind: "$detections"},
  {$group: {_id: "$detections.label", count: {$sum: 1}}},
  {$sort: {count: -1}}
])
```

#### Voir les détections d'une vidéo spécifique
```javascript
db.detections.find({video_filename: "nom_du_fichier.mp4"}).pretty()
```

#### Exporter en JSON
```javascript
db.detections.find().forEach(function(doc) {
    print(JSON.stringify(doc));
})
```

---

## 🎯 Méthode 4 : Via le code Python

### Exemple simple
```python
from mongodb_service import mongodb_service

# Voir toutes les détections
for doc in mongodb_service.collection.find():
    print(f"Date: {doc['timestamp']}")
    print(f"Type: {doc['media_type']}")
    print(f"Fichier: {doc.get('image_filename') or doc.get('video_filename')}")
    print(f"Détections: {doc['detection_count']}")
    print("-" * 50)
```

---

## 📋 Structure des données

Chaque document MongoDB contient :

```json
{
  "_id": "ObjectId",
  "timestamp": "2025-12-10T21:55:43",
  "media_type": "image" ou "video",
  "image_filename": "nom_fichier.jpg" (si image),
  "video_filename": "nom_fichier.mp4" (si vidéo),
  "detections": [
    {
      "id": "0_0",
      "label": "Battery",
      "confidence": 0.95,
      "riskLevel": "High",
      "alertLevel": 3,
      "sizeCm": 12.5,
      "sizeMeters": 0.125,
      "bbox": {"x": 10.5, "y": 20.3, "width": 5.2, "height": 8.1},
      "position": "Zone A1 · 15.2 m from threshold"
    }
  ],
  "detection_count": 1,
  "has_danger_alert": true,
  "max_alert_level": 3
}
```

---

## 🔍 Pour votre professeur

### Démonstration rapide

1. **Montrer que MongoDB fonctionne** :
   ```bash
   docker ps | grep mongodb
   ```

2. **Afficher les données** :
   ```bash
   cd backend
   python view_mongodb_data.py
   ```

3. **Ou utiliser MongoDB Compass** :
   - Ouvrir Compass
   - Se connecter à `mongodb://localhost:27017`
   - Montrer la base `fod_detection` et la collection `detections`

4. **Montrer un exemple de détection** :
   - Ouvrir un document
   - Montrer les détails d'un objet détecté (label, confiance, position, etc.)

---

## 📝 Notes importantes

- **Base de données** : `fod_detection`
- **Collection** : `detections`
- **Port MongoDB** : `27017`
- **Les données sont sauvegardées automatiquement** à chaque analyse
- **Le bouton "Export to MongoDB"** permet une sauvegarde manuelle supplémentaire

---

## ❓ Problèmes courants

### MongoDB non connecté
```bash
docker-compose up -d mongodb
```

### Vérifier que MongoDB tourne
```bash
docker ps | grep mongodb
```

### Voir les logs MongoDB
```bash
docker logs fod_mongodb
```

