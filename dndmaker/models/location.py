"""
Modèles de données pour les lieux
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class Location:
    """Lieu"""
    id: str
    name: str
    description: str = ""
    location_type: Optional[str] = None  # Type de lieu (ville, forêt, donjon, etc.)
    parent_location: Optional[str] = None  # ID du lieu parent (pour hiérarchie)
    bestiary: List[str] = field(default_factory=list)  # IDs des PNJ/créatures présents dans ce lieu
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

