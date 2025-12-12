# 🚀 Démarrer le Backend avec MongoDB

## Étapes

1. **MongoDB est déjà démarré** ✅
   - Conteneur `fod_mongodb` en cours d'exécution
   - Port 27017 disponible

2. **Démarrer le backend** :
   ```bash
   cd backend
   python app.py
   ```

3. **Vérifier la connexion MongoDB** :
   Dans les logs du backend, vous devriez voir :
   ```
   ✅ MongoDB connecté (Docker): fod_detection.detections
   ```

4. **Tester** :
   - Ouvrir l'interface frontend
   - Uploader une image ou vidéo
   - Les détections seront automatiquement sauvegardées dans MongoDB

## Commandes utiles

```bash
# Voir les logs MongoDB
docker logs -f fod_mongodb

# Voir les détections dans MongoDB
docker exec -it fod_mongodb mongosh
# Puis dans mongosh :
use fod_detection
db.detections.find().pretty()
```

