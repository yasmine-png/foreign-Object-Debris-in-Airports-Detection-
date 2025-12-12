@echo off
echo ========================================
echo   DEMARRAGE COMPLET - FOD DETECTION
echo ========================================
echo.
echo Ce script va demarrer:
echo   1. Backend (Flask + YOLOv8) sur http://localhost:5000
echo   2. Frontend (React) sur http://localhost:5173
echo.
echo Deux fenetres vont s'ouvrir.
echo Fermez-les pour arreter les serveurs.
echo.
pause

echo.
echo Demarrage du Backend...
start "Backend YOLOv8" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && python app.py"

timeout /t 3 /nobreak >nul

echo.
echo Demarrage du Frontend...
start "Frontend React" cmd /k "cd /d %~dp0 && npm run dev"

echo.
echo ========================================
echo   SERVEURS DEMARRES!
echo ========================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:5173
echo.
echo Ouvrez votre navigateur sur: http://localhost:5173
echo.
pause









