# Arborescence complète du projet DNDMaker

```
dndmaker/
├── __init__.py                    # Package principal
│
├── core/                          # Logique métier pure
│   ├── __init__.py
│   └── utils.py                   # Utilitaires (génération ID, calculs)
│
├── models/                        # Structures de données
│   ├── __init__.py
│   ├── character.py               # Modèles PJ/PNJ/Créatures
│   ├── scene.py                   # Modèles de scènes
│   ├── session.py                 # Modèles de sessions
│   ├── project.py                 # Modèle de projet
│   ├── bank.py                    # Modèles de banques de données
│   ├── media.py                   # Modèles de médias
│   └── version.py                 # Modèles de versionning
│
├── services/                      # Règles métier et orchestration
│   ├── __init__.py
│   ├── project_service.py         # Service de gestion de projet
│   ├── scene_service.py         # Service de gestion de scènes (à créer)
│   ├── session_service.py         # Service de gestion de sessions (à créer)
│   ├── character_service.py       # Service de gestion PJ/PNJ (à créer)
│   ├── bank_service.py            # Service de gestion des banques (à créer)
│   └── version_service.py        # Service de gestion des versions (à créer)
│
├── persistence/                   # Sauvegarde, chargement, versionning
│   ├── __init__.py
│   ├── serializer.py              # Sérialisation/désérialisation
│   ├── project_loader.py          # Chargeur de projet
│   └── version_manager.py         # Gestionnaire de versions
│
├── ui_qt/                         # Interface graphique PyQt
│   ├── __init__.py
│   ├── main.py                    # Point d'entrée Qt
│   ├── main_window.py             # Fenêtre principale (à créer)
│   ├── widgets/                   # Widgets personnalisés (à créer)
│   │   ├── __init__.py
│   │   ├── character_editor.py   # Éditeur de personnage
│   │   ├── scene_editor.py        # Éditeur de scène
│   │   └── session_editor.py      # Éditeur de session
│   └── views/                     # Vues principales (à créer)
│       ├── __init__.py
│       ├── project_view.py        # Vue projet
│       ├── sessions_view.py       # Vue sessions
│       ├── scenes_view.py         # Vue scènes
│       ├── characters_view.py     # Vue PJ/PNJ
│       ├── banks_view.py          # Vue banques
│       └── exports_view.py        # Vue exports
│
├── ui_cli/                        # Interface CLI/TUI
│   ├── __init__.py
│   ├── main.py                    # Point d'entrée CLI
│   ├── commands/                  # Commandes CLI (à créer)
│   │   ├── __init__.py
│   │   ├── project_commands.py
│   │   ├── scene_commands.py
│   │   └── character_commands.py
│   └── formatters/                # Formateurs de sortie (à créer)
│       ├── __init__.py
│       └── table_formatter.py
│
├── generators/                    # Génération PNJ / créatures
│   ├── __init__.py
│   ├── npc_generator.py           # Générateur de PNJ (à créer)
│   ├── creature_generator.py      # Générateur de créatures (à créer)
│   └── stats_generator.py         # Générateur de stats (à créer)
│
├── exporters/                     # Export PDF, JSON, TXT, Markdown
│   ├── __init__.py
│   ├── pdf_exporter.py            # Export PDF (à créer)
│   ├── json_exporter.py           # Export JSON (à créer)
│   ├── txt_exporter.py            # Export TXT (à créer)
│   └── markdown_exporter.py       # Export Markdown (à créer)
│
└── plugins/                       # Extensions futures
    ├── __init__.py
    ├── plugin_manager.py           # Gestionnaire de plugins (à créer)
    └── base_plugin.py              # Classe de base pour plugins (à créer)

tests/                              # Tests unitaires
├── __init__.py
├── test_models.py                  # Tests des modèles (à créer)
├── test_services.py                # Tests des services (à créer)
└── test_persistence.py             # Tests de persistence (à créer)

docs/                               # Documentation
├── ARCHITECTURE.md                 # Architecture du projet
├── MODELS.md                       # Schéma des modèles
└── ARBORESCENCE.md                 # Ce fichier

resources/                          # Ressources (à créer)
├── icons/                          # Icônes
├── templates/                      # Templates de fiches
└── default_banks/                  # Banques de données par défaut
    ├── names.json
    ├── races.json
    ├── classes.json
    └── paths.json

# Fichiers racine
├── README.md                       # Documentation principale
├── requirements.txt                # Dépendances Python
├── setup.py                        # Configuration du package
└── .gitignore                      # Fichiers ignorés par Git
```

## Structure des projets sauvegardés

Chaque projet est sauvegardé dans un répertoire `.dndmaker` :

```
nom_projet.dndmaker/
├── project.json                    # Fichier principal du projet
├── versions/                       # Historique des versions
│   ├── version_0001.json
│   ├── version_0002.json
│   └── ...
├── media/                          # Médias du projet
│   ├── images/
│   ├── maps/
│   └── documents/
└── exports/                        # Exports générés (optionnel)
    ├── pdf/
    ├── json/
    └── markdown/
```

