"""
Modèles de données pour les scènes
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Event:
    """Événement dans une scène"""
    id: str
    title: str
    description: str = ""
    timestamp: Optional[datetime] = None


@dataclass
class Scene:
    """Scène"""
    id: str
    title: str
    description: str = ""
    player_characters: List[str] = field(default_factory=list)  # IDs des PJ
    npcs: List[str] = field(default_factory=list)  # IDs des PNJ/créatures
    events: List[Event] = field(default_factory=list)
    objects: List[str] = field(default_factory=list)
    cards: List[str] = field(default_factory=list)  # IDs de cartes/images
    images: List[str] = field(default_factory=list)  # IDs d'images
    referenced_scenes: List[str] = field(default_factory=list)  # IDs de scènes référencées
    sessions: List[str] = field(default_factory=list)  # IDs de sessions
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

