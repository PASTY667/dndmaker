"""
Modèles de données pour les sessions
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Session:
    """Session de jeu"""
    id: str
    title: str
    date: datetime = field(default_factory=datetime.now)
    scenes: List[str] = field(default_factory=list)  # IDs de scènes, ordonnées
    post_session_notes: str = ""
    image_id: Optional[str] = None  # ID de l'image associée
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_preparation: bool = False  # Préparation vs réel

