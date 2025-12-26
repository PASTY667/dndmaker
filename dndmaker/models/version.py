"""
Modèles de données pour le versionning
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime


@dataclass
class Version:
    """Version d'un projet"""
    version_number: int
    timestamp: datetime = field(default_factory=datetime.now)
    author: Optional[str] = None
    description: Optional[str] = None
    data: Dict = field(default_factory=dict)  # Snapshot complet du projet

