# 📋 Requêtes MongoDB avec Authentification

## 🔐 Connexion MongoDB

### ⚠️ IMPORTANT : Votre MongoDB fonctionne SANS authentification

Vos données (27 documents) sont accessibles **SANS authentification**. Utilisez ces commandes :

### Méthode 1 : Connexion simple (SANS authentification) ✅ RECOMMANDÉ
```bash
docker exec -it fod_mongodb mongosh fod_detection
```

### Méthode 2 : Connexion directe
```bash
docker exec -it fod_mongodb mongosh
```
Puis dans mongosh :
```javascript
use fod_detection
```

### Méthode 3 : Avec authentification (si configuré)
```bash
docker exec -it fod_mongodb mongosh -u admin -p admin123 --authenticationDatabase admin fod_detection
```

---

## 📊 Requêtes MongoDB

### 1. Voir toutes les détections en JSON (SANS authentification)
```bash
docker exec -it fod_mongodb mongosh fod_detection --quiet --eval "JSON.stringify(db.detections.find().toArray(), null, 2)"
```

### 2. Exporter toutes les détections dans un fichier JSON
```bash
docker exec -it fod_mongodb mongosh fod_detection --quiet --eval "JSON.stringify(db.detections.find().toArray(), null, 2)" > export_mongodb.json
```

### 3. Voir la dernière détection
```bash
docker exec -it fod_mongodb mongosh fod_detection --quiet --eval "JSON.stringify(db.detections.findOne().sort({timestamp: -1}), null, 2)"
```

### 4. Compter les documents ✅
```bash
docker exec -it fod_mongodb mongosh fod_detection --quiet --eval "db.detections.countDocuments()"
```
**Résultat attendu : 27 documents**

---

## 🎯 Mode interactif (mongosh)

### Se connecter (SANS authentification) ✅
```bash
docker exec -it fod_mongodb mongosh fod_detection
```

### Puis dans mongosh, exécuter :
```javascript
// Voir toutes les détections en JSON
db.detections.find().forEach(function(doc) {
    print(JSON.stringify(doc, null, 2));
})

// Ou voir une seule
print(JSON.stringify(db.detections.findOne(), null, 2))

// Compter
db.detections.countDocuments()

// Statistiques
{
    total: db.detections.countDocuments(),
    images: db.detections.countDocuments({media_type: "image"}),
    videos: db.detections.countDocuments({media_type: "video"})
}
```

---

## 💾 Export en fichier JSON (avec auth)

```bash
docker exec -it fod_mongodb mongosh -u admin -p admin123 --authenticationDatabase admin fod_detection --quiet --eval "JSON.stringify(db.detections.find().toArray(), null, 2)" > export_mongodb.json
```

---

## 🔑 Identifiants MongoDB

- **Username** : `admin`
- **Password** : `admin123`
- **Database** : `fod_detection`
- **Collection** : `detections`
- **Auth Database** : `admin`

## ⚠️ IMPORTANT : Si vous voyez "Command requires authentication"

Si vous êtes déjà connecté à mongosh mais que vous voyez l'erreur "Command requires authentication", vous devez :

1. **Quitter la session actuelle** : Tapez `exit` ou `Ctrl+C`
2. **Vous reconnecter avec authentification** :
   ```bash
   docker exec -it fod_mongodb mongosh -u admin -p admin123 --authenticationDatabase admin fod_detection
   ```

3. **Vérifier que vous êtes bien authentifié** :
   ```javascript
   // Cette commande devrait fonctionner sans erreur
   db.detections.countDocuments()
   ```

## 🔧 Configuration Backend

Pour que le backend sauvegarde les détections, créez un fichier `backend/.env` avec :
```env
MONGODB_URI=mongodb://localhost:27017/
MONGODB_USER=admin
MONGODB_PASSWORD=admin123
MONGODB_DATABASE=fod_detection
MONGODB_COLLECTION=detections
```

Puis **redémarrez le backend** pour que les changements prennent effet.

