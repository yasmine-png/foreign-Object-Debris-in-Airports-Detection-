# 🚀 Démarrer l'Application en Local

## ✅ Configuration Actuelle

- ✅ **Frontend** : Configuré pour utiliser `http://localhost:5000/api`
- ✅ **Backend** : Flask avec YOLOv8 dans le dossier `backend/`
- ✅ **Modèle** : `yolov8n_fod_final_v7/weights/best.pt`

## 🎯 Démarrer l'Application

### Option 1 : Script Automatique (Recommandé)

Double-cliquez sur **`start_all.bat`** dans le dossier racine.

Cela va démarrer :
- ✅ Backend Flask sur http://localhost:5000
- ✅ Frontend React sur http://localhost:5173

### Option 2 : Manuel (2 Terminaux)

#### Terminal 1 : Backend

```powershell
cd backend
.\venv\Scripts\activate
python app.py
```

Vous devriez voir :
```
Modèle chargé avec succès!
 * Running on http://127.0.0.1:5000
```

#### Terminal 2 : Frontend

```powershell
npm run dev
```

Vous devriez voir :
```
  VITE v5.0.8  ready in XXX ms
  ➜  Local:   http://localhost:5173/
```

## 🌐 Utiliser l'Interface

1. Ouvrez votre navigateur sur : **http://localhost:5173**
2. Uploadez une image
3. La détection fonctionnera avec votre modèle local !

## ✅ Vérification

### Tester l'API Backend

```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/health" | Select-Object -ExpandProperty Content
```

Vous devriez voir :
```json
{
  "status": "ok",
  "model_loaded": true
}
```

## 🆘 Dépannage

### Le backend ne démarre pas
- Vérifiez que le modèle existe : `yolov8n_fod_final_v7/weights/best.pt`
- Vérifiez que l'environnement virtuel est activé
- Vérifiez les logs dans le terminal

### Le frontend ne se connecte pas au backend
- Vérifiez que le backend est bien démarré sur le port 5000
- Vérifiez la console du navigateur (F12) pour les erreurs
- Vérifiez que `src/services/api.ts` pointe vers `http://localhost:5000/api`

### Erreur CORS
- Le backend a déjà CORS configuré, ça devrait fonctionner
- Si problème, vérifiez que le backend écoute sur `0.0.0.0` ou `127.0.0.1`

## 🎉 C'est Tout !

Votre application fonctionne maintenant entièrement en local sur votre PC !

