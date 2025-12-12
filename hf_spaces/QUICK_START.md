# ⚡ Déploiement Rapide - Hugging Face Spaces

## 🎯 En 3 Étapes

### 1️⃣ Créer le Space

```bash
# Allez sur https://huggingface.co/spaces
# Cliquez "Create new Space"
# Configurez: Docker + CPU Basic (gratuit) ou GPU T4 small (payant)
```

### 2️⃣ Cloner et Copier

```bash
# Cloner votre Space
git clone https://huggingface.co/spaces/VOTRE_USERNAME/fod-detection
cd fod-detection

# Installer Git LFS
git lfs install

# Copier les fichiers
cp ../hf_spaces/* .

# Copier le modèle
mkdir -p yolov8n_fod_final_v7/weights
cp ../../yolov8n_fod_final_v7/weights/best.pt yolov8n_fod_final_v7/weights/
```

### 3️⃣ Push

```bash
git add .
git commit -m "Deploy FOD Detection"
git push
```

**C'est tout !** 🎉 Hugging Face va builder automatiquement votre Space.

## 🌐 Votre API sera à :

```
https://VOTRE_USERNAME-fod-detection.hf.space/api/health
```

## 📝 Modifier le Frontend

Dans `src/services/api.ts` :

```typescript
const API_BASE_URL = 'https://VOTRE_USERNAME-fod-detection.hf.space/api';
```

## ✅ Avantages

- 🆓 CPU Basic gratuit (parfait pour tester)
- 💳 GPU T4 disponible (payant mais très rapide)
- ⚡ Rapide et automatique
- 🌍 Public et partageable
- 💪 Scalable

