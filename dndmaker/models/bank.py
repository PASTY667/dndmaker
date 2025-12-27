"""
Modèles de données pour les banques de données
"""

from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum


class BankType(Enum):
    """Type de banque de données"""
    NAMES = "NAMES"
    RACES = "RACES"
    CLASSES = "CLASSES"
    PATHS = "PATHS"
    STAT_TABLES = "STAT_TABLES"
    CREATURES = "CREATURES"
    PROFESSIONS = "PROFESSIONS"
    ARMORS = "ARMORS"
    TOOLS = "TOOLS"
    TRINKETS = "TRINKETS"
    WEAPONS = "WEAPONS"
    FACTIONS = "FACTIONS"
    LOCATIONS = "LOCATIONS"


@dataclass
class BankEntry:
    """Entrée dans une banque de données"""
    id: str
    value: str
    metadata: Dict = field(default_factory=dict)


@dataclass
class DataBank:
    """Banque de données"""
    id: str
    type: BankType
    entries: List[BankEntry] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

