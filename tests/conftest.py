"""
Configuration pytest et fixtures communes
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock

from dndmaker.services.project_service import ProjectService
from dndmaker.models.character import CharacterType


@pytest.fixture
def temp_project_dir():
    """Crée un répertoire temporaire pour les tests"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def project_service(temp_project_dir):
    """Crée un ProjectService pour les tests"""
    service = ProjectService()
    return service


@pytest.fixture
def sample_character_data():
    """Données d'exemple pour un personnage"""
    return {
        "id": "test-char-1",
        "name": "Test Character",
        "type": "PJ",
        "profile": {
            "level": 1,
            "race": "Humain",
            "character_class": "Guerrier"
        },
        "characteristics": {
            "strength": {"value": 15, "modifier": 2},
            "dexterity": {"value": 12, "modifier": 1},
            "constitution": {"value": 14, "modifier": 2},
            "intelligence": {"value": 10, "modifier": 0},
            "wisdom": {"value": 13, "modifier": 1},
            "charisma": {"value": 11, "modifier": 0}
        },
        "combat": {
            "life_points": 10,
            "current_life_points": 10
        },
        "defense": {
            "base": 10
        },
        "weapons": [],
        "equipment": [],
        "notes": ""
    }

