# 🚀 Guide de Démarrage Rapide - Backend FOD Detection

## ✅ Problèmes Corrigés

- ✅ Fix PyTorch 2.6+ pour le chargement des modèles
- ✅ Gestion d'erreurs améliorée
- ✅ Chemin du modèle relatif/absolu automatique
- ✅ Messages de démarrage clairs

## 📋 Démarrage du Backend

### Option 1 : Script automatique (Recommandé)

Double-cliquez sur `start_backend.bat` à la racine du projet, ou exécutez :

```bash
.\start_backend.bat
```

### Option 2 : Démarrage manuel

1. Ouvrez un terminal PowerShell
2. Allez dans le dossier backend :
```powershell
cd backend
```

3. Activez l'environnement virtuel :
```powershell
.\venv\Scripts\activate
```

4. Lancez le serveur :
```powershell
python app.py
```

## 🔍 Vérification

Une fois le serveur démarré, vous devriez voir :

```
============================================================
🚀 DÉMARRAGE DU SERVEUR FOD DETECTION
============================================================
📁 Chemin du modèle: ...
✅ Fichier existe: True
⏳ Chargement du modèle YOLOv8...
✅ Modèle chargé avec succès!
📊 Classes détectables: ['Bolt', 'Pliers', ...]
============================================================
```

## 🌐 URLs du Serveur

- **Health Check**: http://localhost:5000/api/health
- **Health Check**: http://127.0.0.1:5000/api/health
- **API Detect**: http://localhost:5000/api/detect (POST)

## 🧪 Test du Serveur

Pour tester que le serveur fonctionne :

```powershell
cd backend
.\venv\Scripts\activate
python test_server.py
```

## ⚠️ Dépannage

### Le modèle ne se charge pas

1. Vérifiez que le fichier existe : `yolov8n_fod_final_v7\weights\best.pt`
2. Vérifiez les permissions du fichier
3. Vérifiez que PyTorch est installé : `pip list | findstr torch`

### Le serveur ne démarre pas

1. Vérifiez que le port 5000 n'est pas utilisé :
```powershell
netstat -ano | findstr :5000
```

2. Vérifiez que toutes les dépendances sont installées :
```powershell
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Erreur de connexion

- Assurez-vous que le serveur est bien démarré
- Vérifiez que vous utilisez la bonne URL (http://localhost:5000 ou http://127.0.0.1:5000)
- Vérifiez votre pare-feu Windows

## 📝 Notes

- Le modèle est chargé une seule fois au démarrage
- Le serveur fonctionne en mode debug (rechargement automatique)
- Pour arrêter le serveur, appuyez sur `Ctrl+C`

