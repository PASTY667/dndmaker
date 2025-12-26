"""
Utilitaires pour le core
"""

import uuid
from typing import Any


def generate_id() -> str:
    """Génère un ID unique (UUID)"""
    return str(uuid.uuid4())


def validate_characteristic_value(value: int) -> bool:
    """Valide une valeur de caractéristique (généralement 1-20)"""
    return 1 <= value <= 20


def calculate_modifier(value: int) -> int:
    """Calcule le modificateur d'une caractéristique"""
    return (value - 10) // 2

