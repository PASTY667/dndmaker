"""
Tests pour les services
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from dndmaker.services.character_service import CharacterService
from dndmaker.services.scene_service import SceneService
from dndmaker.services.session_service import SessionService
from dndmaker.services.bank_service import BankService
from dndmaker.services.project_service import ProjectService
from dndmaker.models.character import CharacterType
from dndmaker.models.bank import BankType
from dndmaker.models.scene import Event


class TestCharacterService:
    """Tests pour CharacterService"""
    
    def test_create_character(self, project_service):
        """Vérifie la création d'un personnage"""
        service = project_service.character_service
        character = service.create_character(
            name="Test Character",
            character_type=CharacterType.PJ,
            level=1,
            race="Humain"
        )
        assert character.name == "Test Character"
        assert character.type == CharacterType.PJ
        assert character.profile.level == 1
        assert character.profile.race == "Humain"
        assert character.id is not None
    
    def test_get_character(self, project_service):
        """Vérifie la récupération d'un personnage"""
        service = project_service.character_service
        character = service.create_character(
            name="Test",
            character_type=CharacterType.PJ
        )
        retrieved = service.get_character(character.id)
        assert retrieved is not None
        assert retrieved.id == character.id
        assert retrieved.name == "Test"
    
    def test_get_all_characters(self, project_service):
        """Vérifie la récupération de tous les personnages"""
        service = project_service.character_service
        service.create_character("Char1", CharacterType.PJ)
        service.create_character("Char2", CharacterType.PNJ)
        service.create_character("Char3", CharacterType.CREATURE)
        
        all_chars = service.get_all_characters()
        assert len(all_chars) == 3
    
    def test_get_characters_by_type(self, project_service):
        """Vérifie la récupération par type"""
        service = project_service.character_service
        service.create_character("PJ1", CharacterType.PJ)
        service.create_character("PJ2", CharacterType.PJ)
        service.create_character("PNJ1", CharacterType.PNJ)
        
        pjs = service.get_characters_by_type(CharacterType.PJ)
        assert len(pjs) == 2
        assert all(c.type == CharacterType.PJ for c in pjs)
    
    def test_update_character(self, project_service):
        """Vérifie la mise à jour d'un personnage"""
        service = project_service.character_service
        character = service.create_character("Test", CharacterType.PJ)
        character.name = "Updated Name"
        service.update_character(character)
        
        updated = service.get_character(character.id)
        assert updated.name == "Updated Name"
    
    def test_update_nonexistent_character(self, project_service):
        """Vérifie qu'une erreur est levée pour un personnage inexistant"""
        service = project_service.character_service
        character = service.create_character("Test", CharacterType.PJ)
        character.id = "nonexistent"
        
        with pytest.raises(ValueError):
            service.update_character(character)
    
    def test_delete_character(self, project_service):
        """Vérifie la suppression d'un personnage"""
        service = project_service.character_service
        character = service.create_character("Test", CharacterType.PJ)
        char_id = character.id
        
        result = service.delete_character(char_id)
        assert result is True
        assert service.get_character(char_id) is None
    
    def test_delete_nonexistent_character(self, project_service):
        """Vérifie la suppression d'un personnage inexistant"""
        service = project_service.character_service
        result = service.delete_character("nonexistent")
        assert result is False


class TestSceneService:
    """Tests pour SceneService"""
    
    def test_create_scene(self, project_service):
        """Vérifie la création d'une scène"""
        service = project_service.scene_service
        scene = service.create_scene(
            title="Test Scene",
            description="A test scene"
        )
        assert scene.title == "Test Scene"
        assert scene.description == "A test scene"
        assert scene.id is not None
    
    def test_get_scene(self, project_service):
        """Vérifie la récupération d'une scène"""
        service = project_service.scene_service
        scene = service.create_scene("Test", "")
        retrieved = service.get_scene(scene.id)
        assert retrieved is not None
        assert retrieved.id == scene.id
    
    def test_update_scene(self, project_service):
        """Vérifie la mise à jour d'une scène"""
        service = project_service.scene_service
        scene = service.create_scene("Original", "")
        scene.title = "Updated"
        service.update_scene(scene)
        
        updated = service.get_scene(scene.id)
        assert updated.title == "Updated"
    
    def test_delete_scene(self, project_service):
        """Vérifie la suppression d'une scène"""
        service = project_service.scene_service
        scene = service.create_scene("Test", "")
        scene_id = scene.id
        
        result = service.delete_scene(scene_id)
        assert result is True
        assert service.get_scene(scene_id) is None


class TestSessionService:
    """Tests pour SessionService"""
    
    def test_create_session(self, project_service):
        """Vérifie la création d'une session"""
        service = project_service.session_service
        from datetime import datetime
        session = service.create_session(
            title="Test Session",
            date=datetime.now(),
            is_preparation=False
        )
        assert session.title == "Test Session"
        assert session.is_preparation is False
        assert session.id is not None
    
    def test_get_session(self, project_service):
        """Vérifie la récupération d'une session"""
        service = project_service.session_service
        from datetime import datetime
        session = service.create_session("Test", datetime.now())
        retrieved = service.get_session(session.id)
        assert retrieved is not None
        assert retrieved.id == session.id
    
    def test_add_scene_to_session(self, project_service):
        """Vérifie l'ajout d'une scène à une session"""
        session_service = project_service.session_service
        scene_service = project_service.scene_service
        from datetime import datetime
        
        session = session_service.create_session("Test", datetime.now())
        scene = scene_service.create_scene("Scene 1", "")
        
        session_service.add_scene(session.id, scene.id)
        updated_session = session_service.get_session(session.id)
        assert scene.id in updated_session.scenes


class TestBankService:
    """Tests pour BankService"""
    
    def test_add_entry(self, project_service):
        """Vérifie l'ajout d'une entrée à une banque"""
        service = project_service.bank_service
        entry_id = service.add_entry(
            bank_type=BankType.NAMES,
            value="Test Name",
            metadata={}
        )
        assert entry_id is not None
    
    def test_get_entries(self, project_service):
        """Vérifie la récupération des entrées d'une banque"""
        service = project_service.bank_service
        service.add_entry(BankType.NAMES, "Name1", {})
        service.add_entry(BankType.NAMES, "Name2", {})
        
        entries = service.get_entries(BankType.NAMES)
        assert len(entries) == 2
    
    def test_delete_entry(self, project_service):
        """Vérifie la suppression d'une entrée"""
        service = project_service.bank_service
        entry_id = service.add_entry(BankType.NAMES, "Test", {})
        
        result = service.delete_entry(BankType.NAMES, entry_id)
        assert result is True
        entries = service.get_entries(BankType.NAMES)
        assert len(entries) == 0
    
    def test_get_random_entry(self, project_service):
        """Vérifie la récupération aléatoire d'une entrée"""
        service = project_service.bank_service
        service.add_entry(BankType.NAMES, "Name1", {})
        service.add_entry(BankType.NAMES, "Name2", {})
        
        random_entry = service.get_random_entry(BankType.NAMES)
        assert random_entry is not None
        assert random_entry.value in ["Name1", "Name2"]


class TestProjectService:
    """Tests pour ProjectService"""
    
    def test_create_project(self, temp_project_dir):
        """Vérifie la création d'un projet"""
        service = ProjectService()
        project = service.create_project(
            name="Test Campaign",
            project_dir=temp_project_dir
        )
        assert project.name == "Test Campaign"
        assert service.current_project is not None
        assert service.project_path == temp_project_dir
    
    def test_project_has_services(self, temp_project_dir):
        """Vérifie que le projet a tous les services"""
        service = ProjectService()
        service.create_project("Test", temp_project_dir)
        
        assert service.character_service is not None
        assert service.scene_service is not None
        assert service.session_service is not None
        assert service.bank_service is not None
        assert service.location_service is not None
        assert service.table_service is not None
        assert service.media_service is not None

