# Résumé de l'architecture DNDMaker

## Vue d'ensemble

DNDMaker est une application locale pour Maître de Jeu permettant de gérer une campagne de jeu de rôle **Chroniques Oubliées**.

### Caractéristiques principales

- ✅ **Architecture MVC stricte** : Séparation complète entre logique métier et interface
- ✅ **Multi-OS** : Windows, Linux, macOS
- ✅ **Local uniquement** : Aucune connexion réseau requise
- ✅ **Versionning automatique** : Chaque sauvegarde crée une version
- ✅ **Double interface** : GUI PyQt et CLI fonctionnelles
- ✅ **Extensible** : Système de plugins

## Structure du projet

### Modules principaux

1. **`core/`** : Logique métier pure, indépendante de l'UI
2. **`models/`** : Structures de données (dataclasses)
3. **`services/`** : Règles métier et orchestration
4. **`persistence/`** : Sauvegarde, chargement, versionning
5. **`ui_qt/`** : Interface graphique PyQt
6. **`ui_cli/`** : Interface ligne de commande
7. **`generators/`** : Génération PNJ/créatures
8. **`exporters/`** : Export PDF, JSON, TXT, Markdown
9. **`plugins/`** : Extensions futures

## Modèles de données

### Entités principales

1. **Project** : Projet de campagne (un seul ouvert à la fois)
2. **Character** : Personnages (PJ/PNJ/Créatures) - Fiche officielle Chroniques Oubliées
3. **Scene** : Scènes (entité centrale du scénario)
4. **Session** : Sessions de jeu (soirées de jeu)
5. **DataBank** : Banques de données (noms, races, classes, voies, stats)
6. **Media** : Médias (images, cartes, documents)
7. **Version** : Versions du projet (historique)

### Fiche de personnage

Reproduction fidèle de la fiche officielle avec :
- Profil (niveau, race, sexe, âge, taille, poids)
- Caractéristiques (FOR, DEX, CON, INT, SAG, CHA) avec modificateurs
- Combat (attaques, initiative, vitalité)
- Défense (armure, bouclier, DEX, divers)
- Armes
- Capacités (3 voies)
- Équipement et objets de valeur

## Flux de données

```
UI (Qt/CLI) 
    ↓
Services (logique métier)
    ↓
Models (structures de données)
    ↓
Persistence (sauvegarde/chargement)
```

**Règle d'or** : Aucune logique métier dans l'UI. GUI et CLI utilisent les mêmes services.

## Sauvegarde

- **Format** : JSON versionné
- **Structure** : Un fichier par projet (`.dndmaker`)
- **Versionning** : Chaque sauvegarde crée une version dans `versions/`
- **Rollback** : Possibilité de revenir à une version antérieure

## État actuel

### ✅ Implémenté

- Arborescence complète du projet
- Schéma des modèles de données
- Modèles de base (Character, Scene, Session, Project, etc.)
- Système de versionning
- Service de projet (création, chargement, sauvegarde)
- Point d'entrée CLI fonctionnel
- Point d'entrée Qt (structure de base)
- Documentation technique

### 🔨 À implémenter

- Services complets (Scene, Session, Character, Bank)
- Interface Qt complète
- Générateurs de PNJ/créatures
- Exporters (PDF, JSON, TXT, Markdown)
- Gestion des médias
- Système de plugins
- Tests unitaires

## Prochaines étapes

1. Implémenter les services manquants
2. Développer l'interface Qt complète
3. Implémenter les générateurs
4. Créer les exporters
5. Ajouter les tests
6. Finaliser la documentation utilisateur

## Documentation

- `ARCHITECTURE.md` : Architecture détaillée
- `MODELS.md` : Schéma des modèles
- `MODEL_RELATIONS.md` : Relations entre modèles
- `ARBORESCENCE.md` : Arborescence complète
- `DEVELOPMENT.md` : Guide de développement

