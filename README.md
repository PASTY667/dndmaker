# DNDMaker - Gestionnaire de campagne Chroniques Oubliées

> **Application locale pour Maître de Jeu** permettant de créer, organiser et maintenir une campagne de jeu de rôle **Chroniques Oubliées**.

## 🎲 Compatibilité

**DNDMaker** est conçu spécifiquement pour le système de jeu de rôle **Chroniques Oubliées**, une version simplifiée de D&D (CO). 

### Système supporté
- ✅ **Chroniques Oubliées** (toutes les éditions)

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

## 📂 Emplacement des sauvegardes

Lors de la création d'une nouvelle campagne, vous pouvez choisir l'emplacement de sauvegarde via le dialogue de sélection de dossier. Les fichiers de campagne sont sauvegardés directement dans le dossier choisi (pas dans un sous-dossier `.dndmaker`).

Le système de versionning conserve automatiquement les 3 dernières versions de votre campagne pour éviter l'encombrement du disque.

> **Note** : La configuration de l'application (dernière campagne ouverte, préférences) est stockée dans `~/.dndmaker/config.json` (ou `%USERPROFILE%\.dndmaker\config.json` sous Windows).

## 🏗️ Architecture

- **Langage** : Python 3
- **GUI** : PyQt6
- **Architecture** : MVC strict
- **Multi-OS** : Windows / Linux / macOS
- **Fonctionnement** : Local uniquement (pas de connexion réseau requise)
- **Sauvegarde** : Fichiers JSON versionnés directement dans le dossier de campagne choisi (3 versions conservées)

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

- ✅ Gestion de campagnes avec versionning (3 versions conservées)
- ✅ Création et gestion de personnages (PJ, PNJ, Créatures)
- ✅ Gestion de scènes et sessions avec timeline visuelle
- ✅ Banques de données (noms, races, classes, créatures, équipements, lieux, factions)
- ✅ Tables personnalisées avec champs définissables
- ✅ Génération semi-automatique de PNJ et créatures
- ✅ Export en PDF, JSON, TXT, Markdown avec prévisualisation
- ✅ Gestion d'images avec drag-and-drop pour personnages, scènes, sessions, lieux, factions
- ✅ Interface CLI complète
- ✅ Import/Export de campagnes
- ✅ Interface multilingue (Français / English)
- ✅ Interface utilisateur améliorée avec sélection par checkboxes

## 📸 Captures d'écran

### Interface principale - Édition de personnage

<img width="1880" height="1627" alt="Capture d&#39;écran 2025-12-27 215301" src="https://github.com/user-attachments/assets/b88c9b9b-7dff-40ce-971d-fcaae1497c34" />


L'interface d'édition de personnage permet de gérer tous les détails d'un personnage (PJ, PNJ ou Créature), incluant :
- Informations de profil (nom, type, niveau, race, classe, faction, etc.)
- Gestion d'images avec support du drag-and-drop
- Caractéristiques, combat, défense et équipement
- Export PDF avec image intégrée

### Banques de données - Gestion des armes
<img width="2002" height="1458" alt="Capture d&#39;écran 2025-12-27 215327" src="https://github.com/user-attachments/assets/b88e0bc2-f56b-4ae9-ab52-dc8d158c6f0b" />



Les banques de données permettent de gérer tous les éléments de votre campagne :
- Noms, races, classes, créatures
- Équipements (armes, armures, outils, trinkets)
- Lieux, factions, sorts
- Tables personnalisées

### Éditeur de scène - Timeline et références

L'éditeur de scène offre une interface améliorée pour gérer vos scènes :
- **Timeline visuelle** : Vue chronologique ou arborescente des scènes
- **Sélection intuitive** : Interface avec checkboxes repliables pour sélectionner PJ, PNJ, lieux et scènes référencées
- **Gestion d'images** : Ajout d'images pour chaque scène avec drag-and-drop
- **Événements** : Création et gestion d'événements liés à la scène

### Export de fiches
<img width="3505" height="424" alt="Capture d&#39;écran 2025-12-27 215337" src="https://github.com/user-attachments/assets/40698119-6a25-40c7-a9ae-c6f103e87856" />



L'interface d'export permet de générer des fiches au format PDF, JSON, TXT ou Markdown :
- **Prévisualisation** : Visualisation du contenu avant génération (JSON, TXT, Markdown)
- **Export PDF** : Génération de fiches PDF avec images intégrées pour personnages, scènes et sessions
- **Export multiple** : Export individuel ou complet de la campagne

## 📄 Licence

Voir le fichier [LICENSE](LICENSE) pour les détails complets.

En résumé : Ce projet est sous licence MIT. Vous êtes libre de l'utiliser, le modifier et le distribuer, y compris à des fins commerciales, sous réserve de conserver la notice de copyright.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📧 Contact

Pour toute question ou suggestion, n'hésitez pas à ouvrir une issue sur le dépôt du projet.
