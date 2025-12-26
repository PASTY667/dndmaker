# Interface CLI - DNDMaker

Interface en ligne de commande pour DNDMaker, permettant de gérer vos campagnes Chroniques Oubliées sans interface graphique.

## Installation

La CLI est installée automatiquement avec le package :

```bash
pip install -e .
```

## Utilisation

### Aide générale

```bash
dndmaker-cli --help
```

### Gestion de projet

#### Créer un projet
```bash
dndmaker-cli project create --name "Ma Campagne"
```

#### Ouvrir un projet
```bash
dndmaker-cli project open --path ./MaCampagne.dndmaker
```

#### Lister les projets
```bash
dndmaker-cli project list
```

#### Informations du projet
```bash
dndmaker-cli project info
```

#### Importer un projet depuis JSON
```bash
dndmaker-cli project import --json ./export.json --dir ./projets
```

### Gestion des personnages

#### Lister les personnages
```bash
# Tous les personnages
dndmaker-cli character list

# Filtrer par type
dndmaker-cli character list --type PJ
dndmaker-cli character list --type PNJ
dndmaker-cli character list --type CREATURE
```

#### Afficher un personnage
```bash
dndmaker-cli character show --name "Aragorn"
```

#### Créer un personnage
```bash
dndmaker-cli character create --name "Legolas" --type PJ --level 5 --race "Elfe" --class "Rôdeur"
```

#### Supprimer un personnage
```bash
dndmaker-cli character delete --name "Legolas"
```

### Gestion des scènes

#### Lister les scènes
```bash
dndmaker-cli scene list
```

#### Afficher une scène
```bash
dndmaker-cli scene show --title "La Taverne"
```

#### Créer une scène
```bash
dndmaker-cli scene create --title "La Taverne" --description "Une taverne animée au centre du village"
```

#### Supprimer une scène
```bash
dndmaker-cli scene delete --title "La Taverne"
```

### Gestion des sessions

#### Lister les sessions
```bash
dndmaker-cli session list
```

#### Afficher une session
```bash
dndmaker-cli session show --title "Session 1"
```

#### Créer une session
```bash
dndmaker-cli session create --title "Session 1" --date "2024-01-15"
```

#### Supprimer une session
```bash
dndmaker-cli session delete --title "Session 1"
```

### Gestion des banques

#### Lister les entrées d'une banque
```bash
dndmaker-cli bank list --type RACES
dndmaker-cli bank list --type CLASSES
dndmaker-cli bank list --type CREATURES
```

### Exports

#### Exporter un personnage
```bash
# PDF
dndmaker-cli export character --name "Aragorn" --format PDF

# JSON
dndmaker-cli export character --name "Aragorn" --format JSON

# TXT
dndmaker-cli export character --name "Aragorn" --format TXT

# Markdown
dndmaker-cli export character --name "Aragorn" --format Markdown

# Avec fichier de sortie personnalisé
dndmaker-cli export character --name "Aragorn" --format PDF --output ./fiches/aragorn.pdf
```

#### Exporter une scène
```bash
dndmaker-cli export scene --title "La Taverne" --format JSON
dndmaker-cli export scene --title "La Taverne" --format Markdown
```

## Exemples complets

### Workflow complet

```bash
# 1. Créer un projet
dndmaker-cli project create --name "Ma Campagne"

# 2. Créer des personnages
dndmaker-cli character create --name "Aragorn" --type PJ --level 5 --race "Humain" --class "Guerrier"
dndmaker-cli character create --name "Legolas" --type PJ --level 5 --race "Elfe" --class "Rôdeur"

# 3. Créer une scène
dndmaker-cli scene create --title "La Taverne" --description "Une taverne animée"

# 4. Créer une session
dndmaker-cli session create --title "Session 1" --date "2024-01-15"

# 5. Lister tout
dndmaker-cli character list
dndmaker-cli scene list
dndmaker-cli session list

# 6. Exporter
dndmaker-cli export character --name "Aragorn" --format PDF
```

## Notes

- Toutes les commandes nécessitent qu'un projet soit ouvert (sauf `project create`, `project open`, `project list`, `project import`)
- Les noms de personnages et scènes sont recherchés de manière insensible à la casse
- Les exports sont sauvegardés dans le répertoire courant par défaut

