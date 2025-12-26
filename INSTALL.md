# Guide d'installation - DNDMaker

## Pour les utilisateurs débutants

### Étape 1 : Installer Python

Si Python n'est pas déjà installé sur votre ordinateur :

1. **Windows** :
   - Téléchargez Python depuis https://www.python.org/downloads/
   - Lors de l'installation, **cochez la case "Add Python to PATH"** (très important !)
   - Installez Python 3.8 ou supérieur

2. **Linux** :
   ```bash
   sudo apt-get update
   sudo apt-get install python3 python3-pip
   ```

3. **Mac** :
   - Python est généralement déjà installé
   - Sinon, installez-le via Homebrew : `brew install python3`

### Étape 2 : Télécharger le projet

Téléchargez ou clonez le projet DNDMaker dans un dossier de votre choix.

### Étape 3 : Installer les dépendances

Ouvrez un terminal (ou invite de commande) dans le dossier du projet et exécutez :

```bash
pip install -e .
```

Cela installera automatiquement toutes les dépendances nécessaires.

### Étape 4 : Lancer l'application

#### Windows (méthode la plus simple)

**Double-cliquez simplement sur le fichier `LANCEZ_MOI.bat`**

C'est tout ! L'application se lancera automatiquement.

#### Linux / Mac

1. Rendez le script exécutable :
   ```bash
   chmod +x LANCEZ_MOI.sh
   ```

2. Lancez l'application :
   ```bash
   ./LANCEZ_MOI.sh
   ```

## Méthodes alternatives de lancement

### Après installation via pip

Une fois le package installé avec `pip install -e .`, vous pouvez lancer l'application depuis n'importe où :

```bash
# Interface graphique
dndmaker-qt
# ou simplement
dndmaker

# Interface ligne de commande
dndmaker-cli --help
```

### Depuis le dossier du projet

```bash
# Windows
python -m dndmaker.ui_qt.main

# Linux/Mac
python3 -m dndmaker.ui_qt.main
```

## Dépannage

### "Python n'est pas reconnu comme commande"

**Windows** : Python n'est pas dans votre PATH. Réinstallez Python en cochant "Add Python to PATH".

**Linux/Mac** : Utilisez `python3` au lieu de `python`.

### "Module 'dndmaker' introuvable"

Le package n'est pas installé. Exécutez :
```bash
pip install -e .
```

### "Module 'PyQt6' introuvable"

Les dépendances ne sont pas installées. Exécutez :
```bash
pip install -r requirements.txt
```

### L'application ne se lance pas

1. Vérifiez que Python 3.8+ est installé : `python --version`
2. Vérifiez que toutes les dépendances sont installées : `pip list`
3. Consultez les messages d'erreur dans le terminal

## Support

En cas de problème, vérifiez :
1. Que Python 3.8+ est installé
2. Que toutes les dépendances sont installées
3. Que vous êtes dans le bon répertoire
4. Les messages d'erreur dans le terminal

