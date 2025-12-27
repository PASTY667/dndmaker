"""
Tests pour les modèles de données
"""

import pytest
from datetime import datetime

from dndmaker.models.character import (
    Character,
    CharacterType,
    CharacteristicValue,
    Characteristics,
    CharacterProfile,
    CombatStats,
    DefenseStats,
    Weapon,
    CharacterCapabilities,
    Valuables
)
from dndmaker.models.scene import Scene, Event
from dndmaker.models.session import Session
from dndmaker.models.project import Project
from dndmaker.models.bank import BankEntry, BankType
from dndmaker.models.location import Location
from dndmaker.models.media import Media, MediaType


class TestCharacteristicValue:
    """Tests pour CharacteristicValue"""
    
    def test_default_values(self):
        """Vérifie les valeurs par défaut"""
        char_value = CharacteristicValue()
        assert char_value.value == 10
        assert char_value.modifier == 0
    
    def test_modifier_calculation(self):
        """Vérifie le calcul automatique du modificateur"""
        char_value = CharacteristicValue(value=15)
        assert char_value.value == 15
        assert char_value.modifier == 2  # (15-10)/2 = 2
    
    def test_negative_modifier(self):
        """Vérifie les modificateurs négatifs"""
        char_value = CharacteristicValue(value=8)
        assert char_value.modifier == -1  # (8-10)/2 = -1


class TestCharacter:
    """Tests pour le modèle Character"""
    
    def test_character_creation(self):
        """Vérifie la création d'un personnage"""
        character = Character(
            id="test-1",
            name="Test Character",
            type=CharacterType.PJ
        )
        assert character.id == "test-1"
        assert character.name == "Test Character"
        assert character.type == CharacterType.PJ
        assert character.profile.level == 1
        assert character.combat.life_points == 0
    
    def test_character_with_custom_values(self):
        """Vérifie la création avec des valeurs personnalisées"""
        profile = CharacterProfile(level=5, race="Elfe")
        character = Character(
            id="test-2",
            name="Elf Warrior",
            type=CharacterType.PJ,
            profile=profile
        )
        assert character.profile.level == 5
        assert character.profile.race == "Elf"


class TestScene:
    """Tests pour le modèle Scene"""
    
    def test_scene_creation(self):
        """Vérifie la création d'une scène"""
        scene = Scene(
            id="scene-1",
            title="Test Scene"
        )
        assert scene.id == "scene-1"
        assert scene.title == "Test Scene"
        assert scene.description == ""
        assert len(scene.player_characters) == 0
        assert len(scene.npcs) == 0
        assert len(scene.locations) == 0
    
    def test_scene_with_events(self):
        """Vérifie l'ajout d'événements"""
        scene = Scene(
            id="scene-2",
            title="Scene with Events"
        )
        event = Event(
            id="event-1",
            title="Test Event",
            description="Something happens"
        )
        scene.events.append(event)
        assert len(scene.events) == 1
        assert scene.events[0].title == "Test Event"


class TestSession:
    """Tests pour le modèle Session"""
    
    def test_session_creation(self):
        """Vérifie la création d'une session"""
        session = Session(
            id="session-1",
            title="Test Session"
        )
        assert session.id == "session-1"
        assert session.title == "Test Session"
        assert len(session.scenes) == 0
        assert session.is_preparation is False


class TestBankEntry:
    """Tests pour le modèle BankEntry"""
    
    def test_bank_entry_creation(self):
        """Vérifie la création d'une entrée de banque"""
        entry = BankEntry(
            id="entry-1",
            value="Test Entry",
            bank_type=BankType.NAMES
        )
        assert entry.id == "entry-1"
        assert entry.value == "Test Entry"
        assert entry.bank_type == BankType.NAMES
        assert entry.metadata == {}


class TestLocation:
    """Tests pour le modèle Location"""
    
    def test_location_creation(self):
        """Vérifie la création d'un lieu"""
        location = Location(
            id="loc-1",
            name="Test Location"
        )
        assert location.id == "loc-1"
        assert location.name == "Test Location"
        assert location.description == ""
        assert location.location_type == ""
        assert len(location.bestiary) == 0


class TestMedia:
    """Tests pour le modèle Media"""
    
    def test_media_creation(self):
        """Vérifie la création d'un média"""
        media = Media(
            id="media-1",
            filename="test.jpg",
            filepath="media/images/test.jpg",
            type=MediaType.IMAGE
        )
        assert media.id == "media-1"
        assert media.filename == "test.jpg"
        assert media.type == MediaType.IMAGE
        assert len(media.associated_entities) == 0

