"""
Modèle de données pour les tables personnalisées
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class TableField:
    """Champ d'une table personnalisée"""
    name: str
    field_type: str  # 'string', 'number', 'boolean', 'date'


@dataclass
class CustomTable:
    """Table personnalisée avec schéma et données"""
    id: str
    name: str
    schema: List[TableField] = field(default_factory=list)  # Schéma de la table
    rows: List[Dict] = field(default_factory=list)  # Lignes de données
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

