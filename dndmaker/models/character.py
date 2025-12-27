"""
Modèles de données pour les personnages (PJ/PNJ/Créatures)
Basés sur la fiche officielle Chroniques Oubliées
"""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum


class CharacterType(Enum):
    """Type de personnage"""
    PJ = "PJ"
    PNJ = "PNJ"
    CREATURE = "CREATURE"


@dataclass
class CharacteristicValue:
    """Valeur d'une caractéristique avec son modificateur"""
    value: int = 10
    modifier: int = 0

    def calculate_modifier(self) -> int:
        """Calcule le modificateur selon les règles Chroniques Oubliées"""
        # Modificateur = (valeur - 10) / 2, arrondi vers le bas
        return (self.value - 10) // 2

    def __post_init__(self):
        """Recalcule le modificateur après initialisation"""
        self.modifier = self.calculate_modifier()


@dataclass
class Characteristics:
    """Caractéristiques du personnage"""
    strength: CharacteristicValue = field(default_factory=lambda: CharacteristicValue())
    dexterity: CharacteristicValue = field(default_factory=lambda: CharacteristicValue())
    constitution: CharacteristicValue = field(default_factory=lambda: CharacteristicValue())
    intelligence: CharacteristicValue = field(default_factory=lambda: CharacteristicValue())
    wisdom: CharacteristicValue = field(default_factory=lambda: CharacteristicValue())
    charisma: CharacteristicValue = field(default_factory=lambda: CharacteristicValue())


@dataclass
class CharacterProfile:
    """Profil du personnage"""
    level: int = 1
    race: str = ""
    character_class: Optional[str] = None  # Classe du personnage
    gender: Optional[str] = None
    age: Optional[int] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    racial_ability: str = ""
    known_languages: List[str] = field(default_factory=list)
    profession: Optional[str] = None  # Métier du PNJ


@dataclass
class CombatStats:
    """Statistiques de combat"""
    melee_attack: str = ""  # FOR + NIV
    ranged_attack: str = ""  # DEX + NIV
    magic_attack: str = ""  # NIV
    initiative: str = ""  # DEX
    life_dice: str = ""  # DV
    life_points: int = 0  # PV
    current_life_points: int = 0  # PV restants
    temporary_damage: int = 0  # DM temporaire


@dataclass
class DefenseStats:
    """Statistiques de défense"""
    base: int = 10
    armor: int = 0
    shield: int = 0
    dexterity: int = 0  # Modificateur DEX
    misc: int = 0  # Divers

    def calculate_total(self) -> int:
        """Calcule la défense totale"""
        return self.base + self.armor + self.shield + self.dexterity + self.misc


@dataclass
class Weapon:
    """Arme"""
    name: str = ""
    attack: str = ""  # 1d20 + modificateur
    damage: str = ""
    special: Optional[str] = None


@dataclass
class PathCapability:
    """Capacité d'une voie"""
    name: str = ""
    rank: int = 0  # R
    level1: Optional[str] = None
    level2: Optional[str] = None
    level3: Optional[str] = None


@dataclass
class CharacterCapabilities:
    """Capacités du personnage (voies)"""
    path1: PathCapability = field(default_factory=PathCapability)
    path2: PathCapability = field(default_factory=PathCapability)
    path3: PathCapability = field(default_factory=PathCapability)


@dataclass
class Valuables:
    """Objets de valeur"""
    purse: str = ""  # Bourse
    items: List[str] = field(default_factory=list)


@dataclass
class Character:
    """Personnage complet (PJ/PNJ/Créature)"""
    id: str
    name: str
    type: CharacterType
    profile: CharacterProfile = field(default_factory=CharacterProfile)
    characteristics: Characteristics = field(default_factory=Characteristics)
    combat: CombatStats = field(default_factory=CombatStats)
    defense: DefenseStats = field(default_factory=DefenseStats)
    weapons: List[Weapon] = field(default_factory=list)
    capabilities: CharacterCapabilities = field(default_factory=CharacterCapabilities)
    equipment: List[str] = field(default_factory=list)
    valuables: Valuables = field(default_factory=Valuables)
    faction: Optional[str] = None  # ID de la faction (optionnel)
    image_id: Optional[str] = None  # ID de l'image associée
    notes: str = ""

