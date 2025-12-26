#!/bin/bash
# ============================================
# DNDMaker - Lanceur simple pour Linux/Mac
# ============================================
# Double-cliquez sur ce fichier pour lancer l'application
# ============================================

echo ""
echo "============================================"
echo "  DNDMaker - Chroniques Oubliees"
echo "============================================"
echo ""
echo "Lancement de l'application..."
echo ""

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "ERREUR: Python 3 n'est pas installé."
    echo ""
    echo "Veuillez installer Python 3.8 ou supérieur."
    echo ""
    exit 1
fi

# Vérifier si le package est installé
if ! python3 -c "import dndmaker" &> /dev/null; then
    echo "Installation des dépendances..."
    pip3 install -e .
    if [ $? -ne 0 ]; then
        echo ""
        echo "ERREUR: Impossible d'installer les dépendances."
        echo ""
        exit 1
    fi
fi

# Lancer l'application
python3 -m dndmaker.ui_qt.main

