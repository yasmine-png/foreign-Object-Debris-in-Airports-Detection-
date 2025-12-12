# 🧪 Tester la Sauvegarde MongoDB pour Vidéos

## ✅ Vérification Automatique

La sauvegarde automatique est **déjà activée** ! Quand vous uploadez une vidéo :

1. **Toutes les détections** de **toutes les frames** sont automatiquement sauvegardées dans MongoDB
2. Chaque détection contient :
   - Les informations de l'objet (label, confidence, bbox, etc.)
   - Le numéro de frame
   - Le temps dans la vidéo
   - Le niveau de risque

## 📊 Vérifier les Données Sauvegardées

### 1. Voir toutes les vidéos sauvegardées

```bash
docker exec -it fod_mongodb mongosh
```

Puis dans mongosh :
```javascript
use fod_detection

// Voir toutes les vidéos
db.detections.find({media_type: 'video'}).pretty()

// Compter les vidéos
db.detections.find({media_type: 'video'}).count()

// Voir la dernière vidéo
db.detections.findOne({media_type: 'video'}, {sort: {timestamp: -1}})
```

### 2. Voir toutes les détections d'une vidéo

```javascript
// Récupérer une vidéo
var video = db.detections.findOne({media_type: 'video'})

// Voir le nombre de détections
print("Détections totales: " + video.detection_count)
print("Frames avec détections: " + video.frames_with_detections)
print("Frames totales: " + video.total_frames)

// Voir toutes les détections
video.detections.forEach(function(det, idx) {
    print((idx+1) + ". " + det.label + " - Frame " + det.frame_number + " - Confiance: " + det.confidence)
})
```

### 3. Compter les objets par type

```javascript
var video = db.detections.findOne({media_type: 'video'})
var counts = {}

video.detections.forEach(function(det) {
    var label = det.label
    counts[label] = (counts[label] || 0) + 1
})

for (var label in counts) {
    print(label + ": " + counts[label])
}
```

### 4. Voir les détections par frame

```javascript
var video = db.detections.findOne({media_type: 'video'})

video.frames.forEach(function(frame) {
    if (frame.detections && frame.detections.length > 0) {
        print("Frame " + frame.frame + " (t=" + frame.time + "s): " + frame.detections.length + " détections")
        frame.detections.forEach(function(det) {
            print("  - " + det.label + " (" + det.confidence.toFixed(2) + ")")
        })
    }
})
```

## 🎯 Test Complet

1. **Uploadez une vidéo** via l'interface
2. **Attendez la fin du traitement**
3. **Vérifiez les logs du backend** :
   ```
   ✅ Vidéo sauvegardée dans MongoDB:
      📁 Fichier: votre_video.mp4
      🎬 Frames: X totales, Y avec détections
      📦 Détections: Z objets détectés
      🆔 ID MongoDB: ...
   ```
4. **Vérifiez dans MongoDB** :
   ```bash
   docker exec -it fod_mongodb mongosh --eval "use fod_detection; db.detections.find({media_type: 'video'}).sort({timestamp: -1}).limit(1).pretty()"
   ```

## ✅ Résultat Attendu

Chaque vidéo analysée crée **un document MongoDB** contenant :
- ✅ Toutes les frames avec leurs détections
- ✅ Toutes les détections individuelles (liste plate)
- ✅ Métadonnées (fps, durée, nombre de frames, etc.)
- ✅ Statistiques (nombre total de détections, alertes, etc.)

**Tous les objets détectés dans la vidéo sont sauvegardés !** 🎉

