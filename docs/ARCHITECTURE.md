# Architecture du projet DNDMaker

## Principes fondamentaux

### Séparation stricte des responsabilités

- **core/** : Logique métier pure, indépendante de l'UI
- **models/** : Structures de données (dataclasses, Pydantic models)
- **services/** : Règles métier, orchestration
- **persistence/** : Sauvegarde, chargement, versionning
- **ui_qt/** : Interface graphique PyQt
- **ui_cli/** : Interface CLI/TUI
- **generators/** : Génération PNJ / créatures
- **exporters/** : Export PDF, JSON, TXT, Markdown
- **plugins/** : Extensions futures

### Règle d'or

**Aucune logique métier dans l'UI.** La GUI et la CLI utilisent exactement les mêmes services.

## Flux de données

```
UI (Qt/CLI) → Services → Models → Persistence
                ↓
            Core (règles métier)
```

## Modèles de données

Voir `docs/MODELS.md` pour le schéma détaillé.

## Services principaux

- `ProjectService` : Gestion du projet (chargement, sauvegarde)
- `SceneService` : Gestion des scènes
- `SessionService` : Gestion des sessions
- `CharacterService` : Gestion PJ/PNJ
- `BankService` : Gestion des banques de données
- `VersionService` : Gestion du versionning

## Persistence

- Format : JSON versionné
- Structure : Un fichier par projet avec historique intégré
- Versionning : Chaque sauvegarde crée une nouvelle version

## Plugins

Système de plugins Python avec chargement dynamique :
- API interne documentée
- Points d'extension définis
- Plugins peuvent ajouter logique métier et vues UI

