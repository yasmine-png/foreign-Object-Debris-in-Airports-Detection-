@echo off
echo Démarrage du serveur Flask pour la détection FOD...
echo.

REM Activer l'environnement virtuel si il existe
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Lancer le serveur
python app.py

pause

