@echo off
echo ========================================
echo   DEMARRAGE DU BACKEND YOLOv8
echo ========================================
echo.

cd /d "%~dp0backend"

echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo.
echo Demarrage du serveur Flask...
echo Le backend sera accessible sur http://localhost:5000
echo.
echo Appuyez sur Ctrl+C pour arreter le serveur
echo.

python app.py


