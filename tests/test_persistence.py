"""
Tests pour la persistence (sauvegarde/chargement)
"""

import pytest
import tempfile
import json
import shutil
from pathlib import Path
from datetime import datetime

from dndmaker.persistence.project_loader import ProjectLoader
from dndmaker.persistence.version_manager import VersionManager
from dndmaker.models.project import Project
from dndmaker.models.character import Character, CharacterType


class TestProjectLoader:
    """Tests pour ProjectLoader"""
    
    def test_save_project(self, temp_project_dir):
        """Vérifie la sauvegarde d'un projet"""
        project = Project(
            id="test-project-1",
            name="Test Project",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1
        )
        
        loader = ProjectLoader()
        project_file = temp_project_dir / "project.json"
        loader.save_project(project, project_file, {})
        
        assert project_file.exists()
        
        # Vérifier le contenu
        with open(project_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert data['id'] == project.id
        assert data['name'] == project.name
    
    def test_load_project(self, temp_project_dir):
        """Vérifie le chargement d'un projet"""
        # Créer un fichier de projet
        project_data = {
            "id": "test-project-1",
            "name": "Test Project",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": 1,
            "characters": [],
            "scenes": [],
            "sessions": [],
            "banks": {},
            "locations": [],
            "custom_tables": [],
            "media": []
        }
        
        project_file = temp_project_dir / "project.json"
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f)
        
        loader = ProjectLoader()
        project = loader.load_project(project_file)
        
        assert project is not None
        assert project.id == "test-project-1"
        assert project.name == "Test Project"


class TestVersionManager:
    """Tests pour VersionManager"""
    
    def test_create_version(self, temp_project_dir):
        """Vérifie la création d'une version"""
        manager = VersionManager(temp_project_dir)
        project = Project(
            id="test-1",
            name="Test",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1
        )
        
        version_path = manager.create_version(project, {})
        assert version_path.exists()
        assert "version" in version_path.name.lower()
    
    def test_get_versions(self, temp_project_dir):
        """Vérifie la récupération des versions"""
        manager = VersionManager(temp_project_dir)
        project = Project(
            id="test-1",
            name="Test",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1
        )
        
        # Créer quelques versions
        manager.create_version(project, {})
        project.version = 2
        manager.create_version(project, {})
        
        versions = manager.get_versions()
        assert len(versions) >= 2
    
    def test_limit_versions(self, temp_project_dir):
        """Vérifie que le nombre de versions est limité à 3"""
        manager = VersionManager(temp_project_dir)
        project = Project(
            id="test-1",
            name="Test",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1
        )
        
        # Créer plus de 3 versions
        for i in range(5):
            project.version = i + 1
            manager.create_version(project, {})
        
        versions = manager.get_versions()
        # Le manager devrait garder seulement les 3 dernières versions
        assert len(versions) <= 3

