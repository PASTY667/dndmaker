# Relations entre modèles de données

## Diagramme des relations

```
Project (1)
│
├── Characters (N) ──────────────┐
│   ├── PJ                       │
│   ├── PNJ                      │
│   └── Créatures                │
│                                │
├── Scenes (N)                   │
│   ├── → Characters (références)│
│   ├── → Scenes (références)    │
│   ├── → Media (cartes/images)  │
│   ├── Events (N)               │
│   └── Objects (N)              │
│                                │
├── Sessions (N)                 │
│   └── → Scenes (ordonnées)     │
│                                │
├── DataBanks (N)                │
│   ├── NAMES                    │
│   ├── RACES                    │
│   ├── CLASSES                  │
│   ├── PATHS                    │
│   └── STAT_TABLES              │
│                                │
└── Media (N)                    │
    ├── Images                   │
    ├── Maps                     │
    └── Documents                │
        └── → Entities (associations)
```

## Détails des relations

### Project → Characters
- **Relation** : 1-N (un projet contient plusieurs personnages)
- **Stockage** : Liste d'IDs dans le projet
- **Types** : PJ, PNJ, Créatures

### Project → Scenes
- **Relation** : 1-N (un projet contient plusieurs scènes)
- **Stockage** : Liste d'IDs dans le projet
- **Caractéristiques** :
  - Une scène peut référencer plusieurs PJ/PNJ
  - Une scène peut référencer d'autres scènes
  - Une scène peut appartenir à plusieurs sessions

### Project → Sessions
- **Relation** : 1-N (un projet contient plusieurs sessions)
- **Stockage** : Liste d'IDs dans le projet
- **Caractéristiques** :
  - Une session contient une liste ordonnée de scènes
  - Possibilité de dupliquer une session (préparation → réel)

### Scene → Characters
- **Relation** : N-N (une scène peut référencer plusieurs personnages, un personnage peut être dans plusieurs scènes)
- **Stockage** : Liste d'IDs dans la scène
- **Séparation** : PJ et PNJ stockés séparément

### Scene → Scene
- **Relation** : N-N (une scène peut référencer d'autres scènes)
- **Stockage** : Liste d'IDs dans `referenced_scenes`
- **Usage** : Liens narratifs entre scènes

### Scene → Session
- **Relation** : N-N (une scène peut appartenir à plusieurs sessions, une session contient plusieurs scènes)
- **Stockage** :
  - Dans Scene : liste d'IDs de sessions
  - Dans Session : liste ordonnée d'IDs de scènes

### Media → Entities
- **Relation** : N-N (un média peut être associé à plusieurs entités, une entité peut avoir plusieurs médias)
- **Stockage** : Dictionnaire dans Media (`associated_entities`)
- **Types d'entités** : Scene, Character, Session

### DataBanks
- **Relation** : 1-N avec Project (un projet contient plusieurs banques)
- **Types** : NAMES, RACES, CLASSES, PATHS, STAT_TABLES
- **Usage** : Utilisées par les générateurs pour créer des PNJ/créatures

## Contraintes

1. **Un seul projet ouvert à la fois** : Application locale, pas de multi-projets simultanés
2. **Pas d'ordre global pour les scènes** : L'ordre est défini uniquement dans les sessions
3. **Pas de suppression en cascade** : Les références sont des IDs, la suppression doit être gérée explicitement
4. **Versionning global** : Chaque sauvegarde crée une version complète du projet

## Flux de données typique

### Création d'une session
1. Créer une Session
2. Ajouter des Scenes (existantes ou nouvelles)
3. Ordre défini par la liste `scenes` dans Session
4. Sauvegarder → nouvelle version

### Génération d'un PNJ
1. Utiliser les DataBanks (noms, races, classes, stats)
2. Générer un Character avec stats randomisées
3. Le Character devient éditable
4. Peut être associé à des Scenes

### Export d'une session
1. Récupérer la Session
2. Pour chaque Scene dans l'ordre :
   - Récupérer les Characters référencés
   - Récupérer les Media associés
   - Récupérer les Events
3. Générer le format d'export (PDF, JSON, etc.)

