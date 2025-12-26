# DNDMaker - Application de gestion de campagne Chroniques Oubliées

Application locale pour Maître de Jeu permettant de créer, organiser et maintenir une campagne de jeu de rôle Chroniques Oubliées.

## 🚀 Lancement rapide (pour utilisateurs débutants)

### Windows

**Méthode la plus simple** : Double-cliquez sur le fichier **`LANCEZ_MOI.bat`** dans le dossier du projet.

C'est tout ! L'application se lancera automatiquement.

### Linux / Mac

1. Ouvrez un terminal dans le dossier du projet
2. Rendez le script exécutable :
   ```bash
   chmod +x LANCEZ_MOI.sh
   ```
3. Lancez l'application :
   ```bash
   ./LANCEZ_MOI.sh
   ```

### Alternative : Scripts de lancement

- **Windows** : Double-cliquez sur `launch.bat` (interface graphique) ou `launch_cli.bat` (ligne de commande)
- **Linux/Mac** : Utilisez `launch.sh` ou `launch_cli.sh`

## 📦 Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation en mode développement

```bash
# 1. Télécharger ou cloner le projet
cd dndmaker

# 2. Installer le package et ses dépendances
pip install -e .
```

Cela installera automatiquement toutes les dépendances nécessaires (PyQt6, reportlab, etc.).

### Installation des dépendances uniquement

```bash
pip install -r requirements.txt
```

## 💻 Utilisation

### Interface graphique (recommandée)

#### Après installation via pip
```bash
dndmaker-qt
# ou simplement
dndmaker
```

#### Sans installation (depuis le dossier du projet)
```bash
# Windows
python -m dndmaker.ui_qt.main

# Linux/Mac
python3 -m dndmaker.ui_qt.main
```

### Interface en ligne de commande (CLI)

#### Après installation via pip
```bash
dndmaker-cli --help
```

#### Sans installation
```bash
# Windows
launch_cli.bat --help

# Linux/Mac
chmod +x launch_cli.sh
./launch_cli.sh --help
```

Voir [dndmaker/ui_cli/README.md](dndmaker/ui_cli/README.md) pour la documentation complète de la CLI.

## 🏗️ Architecture

- **Langage** : Python 3
- **GUI** : PyQt6
- **Architecture** : MVC strict
- **Multi-OS** : Windows / Linux / macOS
- **Fonctionnement** : Local uniquement
- **Sauvegarde** : Fichiers JSON versionnés

## 📁 Structure du projet

```
dndmaker/
├── core/              # Logique métier pure
├── models/            # Structures de données
├── services/          # Règles métier
├── persistence/       # Sauvegarde, chargement, versionning
├── ui_qt/             # Interface graphique PyQt
├── ui_cli/            # Interface CLI/TUI
├── generators/        # Génération PNJ / créatures
├── exporters/         # PDF, JSON, TXT, Markdown
├── plugins/           # Extensions futures
├── tests/             # Tests unitaires
├── docs/              # Documentation
└── resources/         # Ressources (icônes, templates, données initiales)
```

## 📝 Fonctionnalités

- ✅ Gestion de projets avec versionning
- ✅ Création et gestion de personnages (PJ, PNJ, Créatures)
- ✅ Gestion de scènes et sessions
- ✅ Banques de données (noms, races, classes, créatures, équipements)
- ✅ Génération semi-automatique de PNJ et créatures
- ✅ Export en PDF, JSON, TXT, Markdown
- ✅ Interface CLI complète
- ✅ Import/Export de projets

## 📄 Licence

Usage personnel uniquement.
