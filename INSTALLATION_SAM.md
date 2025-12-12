# Installation de SAM (Segment Anything Model)

## 📋 Prérequis

Le backend nécessite maintenant SAM pour la segmentation pixel-level.

## 🔧 Installation

### 1. Installer les dépendances Python

```bash
cd backend
.\venv\Scripts\activate
pip install segment-anything matplotlib
```

### 2. Télécharger le modèle SAM

Téléchargez le modèle SAM depuis le lien officiel :

**Windows PowerShell :**
```powershell
cd backend
Invoke-WebRequest -Uri "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth" -OutFile "sam_vit_b_01ec64.pth"
```

**Ou manuellement :**
1. Allez sur : https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth
2. Téléchargez le fichier `sam_vit_b_01ec64.pth`
3. Placez-le dans le dossier `backend/`

## ✅ Vérification

Après installation, redémarrez le backend. Vous devriez voir :

```
⏳ Chargement du modèle SAM...
✅ Modèle SAM chargé avec succès!
```

## 📊 Niveaux d'Alerte

Le système calcule automatiquement la taille réelle des objets et assigne un niveau d'alerte :

- **Alerte 3 (DANGER)** : Objet > 10 cm (0.1 m) - Danger critique
- **Alerte 2 (ATTENTION)** : Objet entre 5-10 cm (0.05-0.1 m) - Attention requise
- **Alerte 1 (NORMAL)** : Objet < 5 cm (< 0.05 m) - Risque faible

## 🚨 Alarme Sonore

Quand une **Alerte 3 (DANGER)** est détectée :
- Une alarme sonore se déclenche automatiquement
- Une bannière d'alerte rouge apparaît en haut de l'interface
- L'objet est segmenté en rouge semi-transparent

## 🎨 Segmentation

La segmentation SAM affiche :
- **Rouge** : Alerte 3 (Danger)
- **Orange** : Alerte 2 (Attention)
- **Vert** : Alerte 1 (Normal)

La segmentation est semi-transparente (40% d'opacité) avec un contour net.

