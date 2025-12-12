# 🐳 MongoDB avec Docker - Configuration FOD Detection

## 🚀 Démarrage Rapide

### 1. Démarrer MongoDB avec Docker

```bash
# Dans le dossier racine du projet
docker-compose up -d mongodb
```

Cela va :
- ✅ Télécharger l'image MongoDB 7.0 (si nécessaire)
- ✅ Créer un conteneur `fod_mongodb`
- ✅ Exposer le port 27017
- ✅ Créer les volumes pour persister les données

### 2. Vérifier que MongoDB fonctionne

```bash
# Vérifier que le conteneur est en cours d'exécution
docker ps | grep mongodb

# Voir les logs
docker logs fod_mongodb

# Tester la connexion
docker exec -it fod_mongodb mongosh --eval "db.version()"
```

### 3. Configuration Backend

#### Option A : Sans authentification (Défaut)

Le backend se connecte automatiquement à `mongodb://localhost:27017/`

#### Option B : Avec authentification

Créer un fichier `backend/.env` :

```env
# MongoDB Docker avec authentification
MONGODB_URI=mongodb://localhost:27017/
MONGODB_USER=admin
MONGODB_PASSWORD=admin123
MONGODB_DATABASE=fod_detection
MONGODB_COLLECTION=detections
```

**Note** : Par défaut, le docker-compose utilise :
- Username: `admin`
- Password: `admin123`

## 📊 Accéder à MongoDB

### Via MongoDB Shell (mongosh)

```bash
# Se connecter au conteneur
docker exec -it fod_mongodb mongosh

# Ou avec authentification
docker exec -it fod_mongodb mongosh -u admin -p admin123 --authenticationDatabase admin
```

### Commandes MongoDB utiles

```javascript
// Utiliser la base de données
use fod_detection

// Voir toutes les collections
show collections

// Voir toutes les détections
db.detections.find().pretty()

// Compter les détections
db.detections.countDocuments()

// Détections récentes (24h)
db.detections.find({
  timestamp: { $gte: new Date(Date.now() - 24*60*60*1000) }
}).sort({ timestamp: -1 })

// Détections avec alerte danger
db.detections.find({ "has_danger_alert": true }).pretty()
```

### Via MongoDB Compass (GUI)

1. **Télécharger MongoDB Compass** : https://www.mongodb.com/try/download/compass
2. **Se connecter** :
   - Connection String: `mongodb://localhost:27017/`
   - Ou avec auth: `mongodb://admin:admin123@localhost:27017/`

## 🔧 Commandes Docker Utiles

### Démarrer MongoDB
```bash
docker-compose up -d mongodb
```

### Arrêter MongoDB
```bash
docker-compose stop mongodb
```

### Redémarrer MongoDB
```bash
docker-compose restart mongodb
```

### Voir les logs
```bash
docker logs -f fod_mongodb
```

### Supprimer le conteneur (⚠️ Supprime les données)
```bash
docker-compose down -v
```

### Sauvegarder les données
```bash
# Les données sont dans le volume Docker
docker volume ls | grep mongodb

# Exporter les données
docker exec fod_mongodb mongodump --out /data/backup
docker cp fod_mongodb:/data/backup ./mongodb_backup
```

## 🛠️ Dépannage

### MongoDB ne démarre pas

```bash
# Vérifier les logs
docker logs fod_mongodb

# Vérifier que le port 27017 n'est pas utilisé
netstat -an | findstr 27017  # Windows
lsof -i :27017               # Linux/Mac
```

### Erreur de connexion

1. **Vérifier que MongoDB est démarré** :
   ```bash
   docker ps | grep mongodb
   ```

2. **Vérifier les logs du backend** :
   - Chercher : `✅ MongoDB connecté (Docker)`
   - Ou : `⚠️ Erreur connexion MongoDB`

3. **Tester la connexion manuellement** :
   ```bash
   docker exec -it fod_mongodb mongosh --eval "db.adminCommand('ping')"
   ```

### Port déjà utilisé

Si le port 27017 est déjà utilisé :

1. **Modifier `docker-compose.yml`** :
   ```yaml
   ports:
     - "27018:27017"  # Utiliser le port 27018 au lieu de 27017
   ```

2. **Mettre à jour `backend/.env`** :
   ```env
   MONGODB_URI=mongodb://localhost:27018/
   ```

### Réinitialiser MongoDB

```bash
# Arrêter et supprimer le conteneur + volumes
docker-compose down -v

# Redémarrer
docker-compose up -d mongodb
```

## 📝 Structure des Données

Les détections sont stockées dans la collection `detections` :

- **Images** : Une entrée par image analysée
- **Vidéos** : Une entrée par vidéo analysée (contient toutes les frames)

Voir `MONGODB_SETUP.md` pour la structure détaillée des documents.

## 🔒 Sécurité

⚠️ **Pour la production**, modifiez les credentials dans `docker-compose.yml` :

```yaml
environment:
  MONGO_INITDB_ROOT_USERNAME: votre_username
  MONGO_INITDB_ROOT_PASSWORD: votre_password_fort
```

Et mettez à jour `backend/.env` en conséquence.

## ✅ Vérification

Après avoir démarré MongoDB, redémarrez votre backend et vérifiez les logs :

```
✅ MongoDB connecté (Docker): fod_detection.detections
```

Les détections seront automatiquement sauvegardées ! 🎉

