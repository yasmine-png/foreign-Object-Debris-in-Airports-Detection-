# 🧪 Guide de Test du Backend

## ✅ Vérifications Rapides

### 1. Test dans le Navigateur

Ouvrez votre navigateur et allez sur ces URLs :

#### A. Route racine (Informations API)
```
http://127.0.0.1:5000/
```
**Résultat attendu :**
```json
{
  "message": "FOD Detection API",
  "version": "1.0.0",
  "endpoints": {
    "health": "/api/health",
    "detect": "/api/detect (POST)"
  }
}
```

#### B. Health Check (État du serveur)
```
http://127.0.0.1:5000/api/health
```
**Résultat attendu :**
```json
{
  "status": "ok",
  "model_loaded": true
}
```

### 2. Test avec le Frontend React

1. **Démarrez le frontend** (si pas déjà fait) :
```bash
npm run dev
```

2. **Ouvrez l'interface** dans votre navigateur (généralement http://localhost:5173)

3. **Testez la détection** :
   - Cliquez sur "Upload Image"
   - Sélectionnez une image
   - Vérifiez que les détections apparaissent

### 3. Test avec curl (Optionnel)

Si vous avez curl installé :

```bash
# Test health
curl http://127.0.0.1:5000/api/health

# Test détection (remplacez image.jpg par votre image)
curl -X POST -F "image=@image.jpg" http://127.0.0.1:5000/api/detect
```

## 🔍 Vérifications à Faire

### ✅ Checklist

- [ ] Le serveur répond sur http://127.0.0.1:5000/
- [ ] Le health check retourne `"model_loaded": true`
- [ ] Aucune erreur 404 dans la console du navigateur
- [ ] Le frontend peut se connecter au backend
- [ ] L'upload d'image fonctionne
- [ ] Les détections s'affichent correctement

## 🐛 Dépannage

### Le serveur ne répond pas
- Vérifiez que le serveur est bien démarré
- Vérifiez le port 5000 : `netstat -ano | findstr :5000`

### Erreurs CORS
- Le backend a CORS activé, normalement pas de problème
- Vérifiez que l'URL dans `src/services/api.ts` est correcte

### Le modèle n'est pas chargé
- Vérifiez que le fichier `yolov8n_fod_final_v7/weights/best.pt` existe
- Regardez les logs du serveur au démarrage

## 📊 Logs du Serveur

Dans le terminal où le serveur tourne, vous devriez voir :
- Messages de démarrage
- Requêtes entrantes (GET, POST)
- Erreurs éventuelles

