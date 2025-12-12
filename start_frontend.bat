@echo off
echo ========================================
echo   DEMARRAGE DU FRONTEND REACT
echo ========================================
echo.

cd /d "%~dp0"

echo Verification des dependances...
if not exist "node_modules" (
    echo Installation des dependances...
    call npm install
)

echo.
echo Demarrage du serveur de developpement...
echo Le frontend sera accessible sur http://localhost:5173
echo.
echo Appuyez sur Ctrl+C pour arreter le serveur
echo.

call npm run dev

pause









