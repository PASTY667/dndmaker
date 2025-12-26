# Schéma des modèles de données

## Modèle de projet

### Project
- `id` : str (UUID)
- `name` : str
- `created_at` : datetime
- `updated_at` : datetime
- `version` : int
- `metadata` : dict (informations supplémentaires)

## Modèle de personnage (PJ/PNJ)

Basé sur la fiche officielle Chroniques Oubliées.

### Character
- `id` : str (UUID)
- `name` : str
- `type` : enum (PJ, PNJ, CREATURE)
- `profile` : CharacterProfile
- `characteristics` : Characteristics
- `combat` : CombatStats
- `defense` : DefenseStats
- `weapons` : list[Weapon]
- `capabilities` : CharacterCapabilities
- `equipment` : list[str]
- `valuables` : Valuables
- `notes` : str

### CharacterProfile
- `level` : int
- `race` : str
- `gender` : str (optionnel)
- `age` : int (optionnel)
- `height` : str (optionnel)
- `weight` : str (optionnel)
- `racial_ability` : str
- `known_languages` : list[str]

### Characteristics
- `strength` : CharacteristicValue (FOR)
- `dexterity` : CharacteristicValue (DEX)
- `constitution` : CharacteristicValue (CON)
- `intelligence` : CharacteristicValue (INT)
- `wisdom` : CharacteristicValue (SAG)
- `charisma` : CharacteristicValue (CHA)

### CharacteristicValue
- `value` : int (valeur brute)
- `modifier` : int (modificateur calculé)

### CombatStats
- `melee_attack` : str (FOR + NIV)
- `ranged_attack` : str (DEX + NIV)
- `magic_attack` : str (NIV)
- `initiative` : str (DEX)
- `life_dice` : str (DV)
- `life_points` : int (PV)
- `current_life_points` : int (PV restants)
- `temporary_damage` : int (DM temporaire)

### DefenseStats
- `base` : int (10)
- `armor` : int
- `shield` : int
- `dexterity` : int (DEX)
- `misc` : int (divers)
- `total` : int (calculé)

### Weapon
- `name` : str
- `attack` : str (1d20 + modificateur)
- `damage` : str
- `special` : str (optionnel)

### CharacterCapabilities
- `path1` : PathCapability
- `path2` : PathCapability
- `path3` : PathCapability

### PathCapability
- `name` : str
- `rank` : int (R)
- `level1` : str (optionnel)
- `level2` : str (optionnel)
- `level3` : str (optionnel)

### Valuables
- `purse` : str (bourse)
- `items` : list[str] (objets de valeur)

## Modèle de scène

### Scene
- `id` : str (UUID)
- `title` : str
- `description` : str
- `player_characters` : list[str] (IDs des PJ)
- `npcs` : list[str] (IDs des PNJ/créatures)
- `events` : list[Event]
- `objects` : list[str]
- `cards` : list[str] (IDs de cartes/images)
- `images` : list[str] (IDs d'images)
- `referenced_scenes` : list[str] (IDs de scènes référencées)
- `sessions` : list[str] (IDs de sessions)
- `notes` : str
- `created_at` : datetime
- `updated_at` : datetime

### Event
- `id` : str (UUID)
- `title` : str
- `description` : str
- `timestamp` : datetime (optionnel)

## Modèle de session

### Session
- `id` : str (UUID)
- `title` : str
- `date` : datetime
- `scenes` : list[str] (IDs de scènes, ordonnées)
- `post_session_notes` : str
- `created_at` : datetime
- `updated_at` : datetime
- `is_preparation` : bool (préparation vs réel)

## Modèle de banque de données

### DataBank
- `id` : str (UUID)
- `type` : enum (NAMES, RACES, CLASSES, PATHS, STAT_TABLES)
- `entries` : list[BankEntry]
- `metadata` : dict

### BankEntry
- `id` : str (UUID)
- `value` : str
- `metadata` : dict (informations supplémentaires)

## Modèle de média

### Media
- `id` : str (UUID)
- `filename` : str
- `filepath` : str (chemin relatif dans le projet)
- `type` : enum (IMAGE, MAP, DOCUMENT)
- `associated_entities` : dict (mapping type_entité -> list[IDs])
- `created_at` : datetime

## Modèle de version

### Version
- `version_number` : int
- `timestamp` : datetime
- `author` : str (optionnel)
- `description` : str (optionnel)
- `data` : dict (snapshot complet du projet)

## Relations entre entités

```
Project
  ├── Characters (PJ, PNJ, Créatures)
  ├── Scenes
  │     ├── → Characters (références)
  │     ├── → Scenes (références)
  │     └── → Media (cartes, images)
  ├── Sessions
  │     └── → Scenes (ordonnées)
  ├── DataBanks
  └── Media
        └── → Entities (associations)
```

