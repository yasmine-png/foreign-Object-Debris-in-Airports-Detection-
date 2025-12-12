# 📦 Instructions de Déploiement - Hugging Face Spaces

## 🎯 Option 1 : Hugging Face Spaces (Recommandé - GPU Gratuit)

### Étapes Détaillées

#### 1. Créer un compte et un Space

1. Allez sur https://huggingface.co/join
2. Créez un compte (gratuit)
3. Allez sur https://huggingface.co/spaces
4. Cliquez sur **"Create new Space"**

#### 2. Configurer le Space

- **Space name** : `fod-detection` (ou votre choix)
- **SDK** : Sélectionnez **`Docker`**
- **Hardware** : Sélectionnez **`GPU T4 small`** (GRATUIT)
- **Visibility** : Public ou Private

#### 3. Cloner votre Space

```bash
# Remplacez VOTRE_USERNAME par votre nom d'utilisateur HF
git clone https://huggingface.co/spaces/VOTRE_USERNAME/fod-detection
cd fod-detection
```

#### 4. Copier les fichiers nécessaires

Copiez ces fichiers dans le dossier `fod-detection` :

```bash
# Depuis le dossier hf_spaces/
cp hf_spaces/app.py .
cp hf_spaces/Dockerfile .
cp hf_spaces/requirements.txt .
cp hf_spaces/README.md .
cp hf_spaces/.gitattributes .
```

#### 5. Uploader votre modèle avec Git LFS

```bash
# Installer Git LFS (une seule fois)
git lfs install

# Créer le dossier pour le modèle
mkdir -p yolov8n_fod_final_v7/weights

# Copier votre modèle
cp ../yolov8n_fod_final_v7/weights/best.pt yolov8n_fod_final_v7/weights/

# Configurer Git LFS pour les fichiers .pt
echo "*.pt filter=lfs diff=lfs merge=lfs -text" >> .gitattributes
echo "*.pth filter=lfs diff=lfs merge=lfs -text" >> .gitattributes

# Ajouter tous les fichiers
git add .
git commit -m "Initial commit: FOD Detection with YOLOv8"
git push
```

#### 6. Attendre le Build

- Hugging Face va automatiquement builder votre Docker
- Cela peut prendre 5-10 minutes la première fois
- Vous pouvez voir les logs dans l'onglet "Logs" de votre Space

#### 7. Tester votre API

Une fois déployé, votre API sera accessible à :
```
https://VOTRE_USERNAME-fod-detection.hf.space/api/health
```

### ⚙️ Configuration du Frontend

Modifiez `src/services/api.ts` pour pointer vers votre Space :

```typescript
// Pour Hugging Face Spaces
const API_BASE_URL = 'https://VOTRE_USERNAME-fod-detection.hf.space/api';

// Ou gardez localhost pour développement local
// const API_BASE_URL = 'http://localhost:5000/api';
```

## 🆚 Option 2 : Google Colab (Alternative Gratuite)

### Avantages
- GPU T4 gratuit
- Notebook interactif
- Facile à partager

### Inconvénients
- Limite de temps (12h max)
- Doit être relancé manuellement
- Pas de service permanent

### Utilisation

1. Créez un nouveau notebook Colab
2. Sélectionnez GPU : Runtime → Change runtime type → GPU T4
3. Installez les dépendances
4. Uploadez votre modèle
5. Lancez le serveur Flask

## 🆚 Option 3 : Kaggle Notebooks

### Avantages
- GPU P100 gratuit
- 30h/semaine de GPU
- Environnement Jupyter

### Inconvénients
- Limite de temps
- Pas de service permanent

## 📊 Comparaison des Options

| Plateforme | GPU | Gratuit | Permanent | Facile |
|------------|-----|---------|-----------|--------|
| **Hugging Face Spaces** | T4 | ✅ | ✅ | ✅✅✅ |
| Google Colab | T4 | ✅ | ❌ | ✅✅ |
| Kaggle | P100 | ✅ | ❌ | ✅✅ |
| Replicate | T4/A100 | ❌* | ✅ | ✅✅✅ |

*Replicate : Payant après crédits gratuits

## 🔧 Dépannage

### Le modèle ne se charge pas

1. Vérifiez que `best.pt` est bien uploadé avec Git LFS
2. Vérifiez les logs dans HF Spaces
3. Vérifiez le chemin du modèle dans `app.py`

### Erreur de mémoire GPU

- Réduisez la taille des images
- Utilisez `yolov8n` (nano) au lieu de `yolov8s` ou plus grand
- Traitez moins de frames pour les vidéos

### Le build échoue

- Vérifiez que `requirements.txt` est correct
- Vérifiez que `Dockerfile` est valide
- Consultez les logs de build dans HF Spaces

## 📝 Notes Importantes

1. **Git LFS est obligatoire** pour les fichiers `.pt` (modèles)
2. **Le GPU T4 est gratuit** mais peut être partagé avec d'autres utilisateurs
3. **Les vidéos longues** peuvent prendre du temps même avec GPU
4. **Le modèle est chargé une fois** au démarrage (gain de temps)

## 🚀 Après le Déploiement

Votre API sera accessible publiquement et vous pourrez :
- Partager le lien avec d'autres
- Intégrer dans d'autres applications
- Utiliser gratuitement avec GPU







