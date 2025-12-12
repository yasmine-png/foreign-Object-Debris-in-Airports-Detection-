# 🗄️ Configuration MongoDB pour FOD Detection

## 📋 Prérequis

1. **Installer Docker** :
   - Windows : https://www.docker.com/products/docker-desktop
   - Ou utiliser MongoDB Atlas (cloud gratuit) : https://www.mongodb.com/cloud/atlas

2. **Installer les dépendances Python** :
```bash
cd backend
pip install -r requirements.txt
```

## ⚙️ Configuration

### Option 1 : MongoDB avec Docker (Recommandé) 🐳

1. **Démarrer MongoDB** :
   ```bash
   docker-compose up -d mongodb
   ```

2. **Configuration par défaut** :
   - URI : `mongodb://localhost:27017/`
   - Database : `fod_detection`
   - Collection : `detections`
   - Username : `admin` (optionnel)
   - Password : `admin123` (optionnel)

**Voir `MONGODB_DOCKER.md` pour les détails complets.**

### Option 2 : MongoDB Local (Sans Docker)

1. **Installer MongoDB** :
   - Windows : Télécharger depuis https://www.mongodb.com/try/download/community
   - Ou manuellement : `mongod --dbpath C:\data\db`

2. **Configuration par défaut** :
   - URI : `mongodb://localhost:27017/`
   - Database : `fod_detection`
   - Collection : `detections`

### Option 3 : MongoDB Atlas (Cloud)

1. **Créer un compte** sur https://www.mongodb.com/cloud/atlas
2. **Créer un cluster gratuit** (M0)
3. **Obtenir la connection string** : `mongodb+srv://username:password@cluster.mongodb.net/`
4. **Créer un fichier `.env`** dans le dossier `backend/` :
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=fod_detection
MONGODB_COLLECTION=detections
```

## 🚀 Utilisation

### Sauvegarde Automatique

Les détections sont **automatiquement sauvegardées** dans MongoDB à chaque :
- ✅ Détection sur une image (`/api/detect`)
- ✅ Détection sur une vidéo (`/api/detect-video`)

### Export Manuel

1. **Export CSV** : Bouton "Export detections as CSV"
   - Télécharge un fichier CSV avec toutes les détections

2. **Export MongoDB** : Bouton "Export to MongoDB"
   - Sauvegarde manuellement les détections dans MongoDB
   - Utile si la sauvegarde automatique a échoué

## 📊 Structure des Données

### Image Detection
```json
{
  "_id": "ObjectId",
  "timestamp": "2025-12-10T...",
  "media_type": "image",
  "image_filename": "test.jpg",
  "image_size": { "width": 1920, "height": 1080 },
  "detections": [
    {
      "id": "0_0",
      "label": "Bolt",
      "confidence": 0.95,
      "riskLevel": "High",
      "alertLevel": 3,
      "bbox": { "x": 10.5, "y": 20.3, "width": 5.2, "height": 8.1 },
      ...
    }
  ],
  "detection_count": 1,
  "has_danger_alert": true,
  "max_alert_level": 3
}
```

### Video Detection
```json
{
  "_id": "ObjectId",
  "timestamp": "2025-12-10T...",
  "media_type": "video",
  "video_filename": "test.mp4",
  "video_info": {
    "fps": 30.0,
    "duration": 10.5,
    "totalFrames": 315,
    "processedFrames": 105
  },
  "frames": [
    {
      "frame": 0,
      "time": 0.0,
      "detections": [...],
      "count": 2
    }
  ],
  "total_frames": 105,
  "detections": [...],
  "detection_count": 210,
  "has_danger_alert": false,
  "max_alert_level": 2
}
```

## 🔍 Requêtes MongoDB Utiles

### Voir toutes les détections
```javascript
db.detections.find().pretty()
```

### Détections avec alerte danger
```javascript
db.detections.find({ "has_danger_alert": true }).pretty()
```

### Détections récentes (24h)
```javascript
db.detections.find({
  "timestamp": { $gte: new Date(Date.now() - 24*60*60*1000) }
}).sort({ "timestamp": -1 })
```

### Compter les détections par type
```javascript
db.detections.aggregate([
  { $unwind: "$detections" },
  { $group: { _id: "$detections.label", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])
```

## ⚠️ Dépannage

### MongoDB non connecté
- Vérifier que MongoDB est démarré
- Vérifier l'URI dans `.env` ou le code
- Vérifier les logs du backend : `✅ MongoDB connecté`

### Erreur de connexion
- Vérifier le firewall
- Vérifier les credentials (Atlas)
- Vérifier que le port 27017 est ouvert (local)

### Les détections ne sont pas sauvegardées
- Vérifier les logs du backend
- Vérifier que `MONGODB_AVAILABLE = True`
- Utiliser le bouton "Export to MongoDB" manuellement

## 📝 Notes

- Les détections sont sauvegardées **automatiquement** à chaque analyse
- Le bouton "Export to MongoDB" permet une sauvegarde **manuelle** supplémentaire
- Le CSV peut être ouvert dans Excel ou Google Sheets
- MongoDB conserve toutes les métadonnées (timestamps, tailles, positions, etc.)

