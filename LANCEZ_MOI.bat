@echo off
REM ============================================
REM DNDMaker - Lanceur simple pour Windows
REM ============================================
REM Double-cliquez sur ce fichier pour lancer l'application
REM ============================================

echo.
echo ============================================
echo   DNDMaker - Chroniques Oubliees
echo ============================================
echo.
echo Lancement de l'application...
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installe ou n'est pas dans le PATH.
    echo.
    echo Veuillez installer Python 3.8 ou superieur depuis:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Vérifier si le package est installé
python -c "import dndmaker" >nul 2>&1
if errorlevel 1 (
    echo Installation des dependances...
    pip install -e .
    if errorlevel 1 (
        echo.
        echo ERREUR: Impossible d'installer les dependances.
        echo.
        pause
        exit /b 1
    )
)

REM Lancer l'application
python -m dndmaker.ui_qt.main

if errorlevel 1 (
    echo.
    echo Une erreur s'est produite. Voir les messages ci-dessus.
    echo.
    pause
)

