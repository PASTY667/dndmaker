"""
Modèles de données pour les médias
"""

from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime
from enum import Enum


class MediaType(Enum):
    """Type de média"""
    IMAGE = "IMAGE"
    MAP = "MAP"
    DOCUMENT = "DOCUMENT"


@dataclass
class Media:
    """Média (image, carte, document)"""
    id: str
    filename: str
    filepath: str  # Chemin relatif dans le projet
    type: MediaType
    associated_entities: Dict[str, List[str]] = field(default_factory=dict)  # type_entité -> list[IDs]
    created_at: datetime = field(default_factory=datetime.now)

