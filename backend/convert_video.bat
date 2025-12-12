@echo off
REM Script pour convertir une vidéo en format compatible navigateur
REM Usage: convert_video.bat [input_video] [output_video]

if "%1"=="" (
    echo Usage: convert_video.bat ^<input_video^> [output_video]
    echo.
    echo Exemple:
    echo   convert_video.bat test_video.mp4
    echo   convert_video.bat test_video.mp4 test_video_converted.mp4
    exit /b 1
)

python convert_video.py %1 %2

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Conversion réussie!
    echo Vous pouvez maintenant utiliser la vidéo convertie dans l'interface.
) else (
    echo.
    echo ❌ Erreur lors de la conversion
    exit /b 1
)

