# 📋 Requêtes MongoDB pour obtenir les données en JSON

## 🔌 Connexion à MongoDB

```bash
docker exec -it fod_mongodb mongosh fod_detection
```

---

## 📊 Requêtes principales

### 1. Voir TOUTES les détections en JSON
```javascript
db.detections.find().forEach(function(doc) {
    print(JSON.stringify(doc, null, 2));
})
```

### 2. Voir la dernière détection en JSON
```javascript
print(JSON.stringify(db.detections.findOne().sort({timestamp: -1}), null, 2))
```

### 3. Voir toutes les détections (format compact)
```javascript
db.detections.find().forEach(function(doc) {
    print(JSON.stringify(doc));
})
```

### 4. Exporter toutes les détections dans un fichier JSON
```bash
docker exec -it fod_mongodb mongosh fod_detection --quiet --eval "JSON.stringify(db.detections.find().toArray())" > export.json
```

### 5. Voir les détections d'une vidéo spécifique
```javascript
db.detections.find({video_filename: "nom_fichier.mp4"}).forEach(function(doc) {
    print(JSON.stringify(doc, null, 2));
})
```

### 6. Voir les détections d'une image spécifique
```javascript
db.detections.find({image_filename: "nom_fichier.jpg"}).forEach(function(doc) {
    print(JSON.stringify(doc, null, 2));
})
```

### 7. Voir les détections avec alerte danger
```javascript
db.detections.find({has_danger_alert: true}).forEach(function(doc) {
    print(JSON.stringify(doc, null, 2));
})
```

### 8. Compter les objets par type (format JSON)
```javascript
print(JSON.stringify(
    db.detections.aggregate([
        {$unwind: "$detections"},
        {$group: {_id: "$detections.label", count: {$sum: 1}}},
        {$sort: {count: -1}}
    ]).toArray(),
    null, 2
))
```

### 9. Voir les statistiques en JSON
```javascript
print(JSON.stringify({
    total: db.detections.countDocuments(),
    images: db.detections.countDocuments({media_type: "image"}),
    videos: db.detections.countDocuments({media_type: "video"}),
    danger_alerts: db.detections.countDocuments({has_danger_alert: true})
}, null, 2))
```

---

## 💾 Export direct en fichier JSON

### Méthode 1 : Via mongosh
```bash
docker exec -it fod_mongodb mongosh fod_detection --quiet --eval "JSON.stringify(db.detections.find().toArray(), null, 2)" > toutes_les_detections.json
```

### Méthode 2 : Via mongoexport (si disponible)
```bash
docker exec -it fod_mongodb mongoexport --db=fod_detection --collection=detections --out=export.json --jsonArray --pretty
```

---

## 🎯 Requêtes rapides (une ligne)

### Toutes les détections
```bash
docker exec -it fod_mongodb mongosh fod_detection --quiet --eval "JSON.stringify(db.detections.find().toArray(), null, 2)"
```

### Dernière détection
```bash
docker exec -it fod_mongodb mongosh fod_detection --quiet --eval "JSON.stringify(db.detections.findOne().sort({timestamp: -1}), null, 2)"
```

### Compter les documents
```bash
docker exec -it fod_mongodb mongosh fod_detection --quiet --eval "db.detections.countDocuments()"
```

---

## 📝 Pour votre professeur

**Commande la plus simple pour voir toutes les données en JSON :**

```bash
docker exec -it fod_mongodb mongosh fod_detection --quiet --eval "JSON.stringify(db.detections.find().toArray(), null, 2)"
```

Ou pour sauvegarder dans un fichier :

```bash
docker exec -it fod_mongodb mongosh fod_detection --quiet --eval "JSON.stringify(db.detections.find().toArray(), null, 2)" > export_mongodb.json
```

