# 🚀 Guide : Démarrer l'Interface YOLOv8 FOD

## 📋 Vue d'ensemble

Pour utiliser l'interface, vous devez démarrer **2 services** :
1. **Backend** (Flask + YOLOv8) - Port 5000
2. **Frontend** (React) - Port 5173

## 🎯 Méthode Rapide (2 terminaux)

### Terminal 1 : Backend

```bash
cd C:\Users\ybouk\OneDrive\Bureau\projet_fod\backend
.\venv\Scripts\activate
python app.py
```

Vous devriez voir :
```
Chargement du modèle depuis: C:\Users\ybouk\...\best.pt
Modèle chargé avec succès!
 * Running on http://127.0.0.1:5000
```

### Terminal 2 : Frontend

```bash
cd C:\Users\ybouk\OneDrive\Bureau\projet_fod
npm run dev
```

Vous devriez voir :
```
  VITE v5.0.8  ready in XXX ms

  ➜  Local:   http://localhost:5173/
```

### 🌐 Ouvrir l'interface

Ouvrez votre navigateur et allez sur : **http://localhost:5173**

---

## 📝 Étapes Détaillées

### ÉTAPE 1 : Démarrer le Backend

1. **Ouvrir PowerShell ou CMD**
2. **Naviguer vers le dossier backend** :
   ```powershell
   cd C:\Users\ybouk\OneDrive\Bureau\projet_fod\backend
   ```

3. **Activer l'environnement virtuel** :
   ```powershell
   .\venv\Scripts\activate
   ```
   Vous devriez voir `(venv)` au début de la ligne.

4. **Démarrer le serveur** :
   ```powershell
   python app.py
   ```

5. **Vérifier que ça fonctionne** :
   - Vous devriez voir "Modèle chargé avec succès!"
   - Le serveur écoute sur `http://127.0.0.1:5000`
   - **Laissez ce terminal ouvert**

### ÉTAPE 2 : Démarrer le Frontend

1. **Ouvrir un NOUVEAU terminal** (PowerShell ou CMD)
2. **Naviguer vers le dossier du projet** :
   ```powershell
   cd C:\Users\ybouk\OneDrive\Bureau\projet_fod
   ```

3. **Vérifier que node_modules existe** :
   ```powershell
   dir node_modules
   ```
   Si le dossier n'existe pas, installez les dépendances :
   ```powershell
   npm install
   ```

4. **Démarrer le serveur de développement** :
   ```powershell
   npm run dev
   ```

5. **Vérifier que ça fonctionne** :
   - Vous devriez voir l'URL : `http://localhost:5173/`
   - **Laissez ce terminal ouvert**

### ÉTAPE 3 : Utiliser l'Interface

1. **Ouvrir votre navigateur** (Chrome, Firefox, Edge)
2. **Aller sur** : `http://localhost:5173`
3. **Vous devriez voir l'interface FOD Detection**

---

## 🎨 Utilisation de l'Interface

1. **Cliquez sur "Upload Image"**
2. **Sélectionnez une image** (par exemple depuis `yolov8n_fod_final_v7/image_noramales/`)
3. **L'image est envoyée au backend YOLOv8**
4. **Les détections apparaissent** avec des bounding boxes colorées
5. **Les résultats s'affichent** dans le panneau de droite

---

## ⚠️ Problèmes Courants

### Problème 1 : "Module not found" dans le backend

**Solution** :
```powershell
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Problème 2 : "Port 5000 already in use"

**Solution** : Un autre processus utilise le port. Fermez-le ou changez le port dans `app.py` :
```python
app.run(debug=True, port=5001, host='0.0.0.0')  # Changer 5000 en 5001
```

### Problème 3 : "npm: command not found"

**Solution** : Installez Node.js depuis [nodejs.org](https://nodejs.org/)

### Problème 4 : "Modèle non chargé"

**Solution** : Vérifiez que le chemin du modèle est correct dans `backend/app.py` :
```python
MODEL_PATH = r"C:\Users\ybouk\OneDrive\Bureau\projet_fod\yolov8n_fod_final_v7\weights\best.pt"
```

### Problème 5 : L'interface ne se connecte pas au backend

**Solution** : Vérifiez que :
- Le backend est bien démarré (Terminal 1)
- Le frontend est bien démarré (Terminal 2)
- Les deux services tournent en même temps

---

## 🚀 Scripts de Démarrage Rapide

### Windows : Créer des fichiers .bat

**`start_backend.bat`** :
```batch
@echo off
cd C:\Users\ybouk\OneDrive\Bureau\projet_fod\backend
call venv\Scripts\activate
python app.py
pause
```

**`start_frontend.bat`** :
```batch
@echo off
cd C:\Users\ybouk\OneDrive\Bureau\projet_fod
npm run dev
pause
```

Double-cliquez sur ces fichiers pour démarrer chaque service.

---

## ✅ Checklist de Démarrage

- [ ] Backend démarré (Terminal 1)
- [ ] Message "Modèle chargé avec succès!" visible
- [ ] Frontend démarré (Terminal 2)
- [ ] URL `http://localhost:5173` visible
- [ ] Navigateur ouvert sur `http://localhost:5173`
- [ ] Interface chargée

---

## 🎯 Résultat Attendu

Quand tout fonctionne :
- ✅ Interface web moderne avec design élégant
- ✅ Bouton "Upload Image" fonctionnel
- ✅ Upload d'image possible
- ✅ Détections YOLOv8 affichées avec bounding boxes
- ✅ Résultats dans le panneau de droite

---

## 📞 Besoin d'aide ?

Si vous avez des problèmes :
1. Vérifiez que les deux terminaux sont ouverts
2. Vérifiez les messages d'erreur dans les terminaux
3. Vérifiez que les ports 5000 et 5173 ne sont pas utilisés









