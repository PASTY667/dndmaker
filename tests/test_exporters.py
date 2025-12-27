"""
Tests pour les exporters
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

from dndmaker.exporters.pdf_exporter import PDFExporter
from dndmaker.exporters.json_exporter import JSONExporter
from dndmaker.exporters.txt_exporter import TXTExporter
from dndmaker.exporters.markdown_exporter import MarkdownExporter
from dndmaker.models.character import Character, CharacterType, CharacterProfile, Characteristics
from dndmaker.models.scene import Scene
from dndmaker.models.session import Session
from dndmaker.services.project_service import ProjectService


@pytest.fixture
def sample_character():
    """Crée un personnage d'exemple pour les tests"""
    return Character(
        id="test-char-1",
        name="Test Character",
        type=CharacterType.PJ,
        profile=CharacterProfile(
            level=1,
            race="Humain",
            character_class="Guerrier"
        ),
        characteristics=Characteristics()
    )


@pytest.fixture
def sample_scene():
    """Crée une scène d'exemple pour les tests"""
    return Scene(
        id="test-scene-1",
        title="Test Scene",
        description="A test scene description"
    )


@pytest.fixture
def sample_session():
    """Crée une session d'exemple pour les tests"""
    from datetime import datetime
    return Session(
        id="test-session-1",
        title="Test Session",
        date=datetime.now()
    )


@pytest.fixture
def temp_output_file():
    """Crée un fichier temporaire pour les exports"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_file.close()
    yield Path(temp_file.name)
    # Nettoyage
    if Path(temp_file.name).exists():
        Path(temp_file.name).unlink()


class TestPDFExporter:
    """Tests pour PDFExporter"""
    
    def test_export_character_sheet(self, sample_character, temp_output_file):
        """Vérifie l'export d'une fiche de personnage en PDF"""
        exporter = PDFExporter()
        result = exporter.export_character_sheet(sample_character, temp_output_file)
        
        assert result is True
        assert temp_output_file.exists()
        assert temp_output_file.suffix == '.pdf'
    
    def test_export_character_with_image(self, sample_character, temp_output_file, temp_project_dir):
        """Vérifie l'export avec une image"""
        # Créer un project_service mock
        project_service = Mock(spec=ProjectService)
        media_service = Mock()
        media_service.get_image_path = Mock(return_value=None)
        project_service.media_service = media_service
        
        sample_character.image_id = "test-image-id"
        exporter = PDFExporter(project_service)
        result = exporter.export_character_sheet(sample_character, temp_output_file)
        
        assert result is True
    
    def test_export_scene(self, sample_scene, temp_output_file):
        """Vérifie l'export d'une scène en PDF"""
        exporter = PDFExporter()
        result = exporter.export_scene(sample_scene, temp_output_file)
        
        assert result is True
        assert temp_output_file.exists()
    
    def test_export_session(self, sample_session, temp_output_file):
        """Vérifie l'export d'une session en PDF"""
        exporter = PDFExporter()
        result = exporter.export_session(sample_session, temp_output_file)
        
        assert result is True
        assert temp_output_file.exists()


class TestJSONExporter:
    """Tests pour JSONExporter"""
    
    def test_export_character(self, sample_character, temp_output_file):
        """Vérifie l'export d'un personnage en JSON"""
        json_file = temp_output_file.with_suffix('.json')
        result = JSONExporter.export_character(sample_character, json_file)
        
        assert result is True
        assert json_file.exists()
        
        # Vérifier le contenu
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert data['id'] == sample_character.id
        assert data['name'] == sample_character.name
    
    def test_export_scene(self, sample_scene, temp_output_file):
        """Vérifie l'export d'une scène en JSON"""
        json_file = temp_output_file.with_suffix('.json')
        result = JSONExporter.export_scene(sample_scene, json_file)
        
        assert result is True
        assert json_file.exists()
    
    def test_export_session(self, sample_session, temp_output_file):
        """Vérifie l'export d'une session en JSON"""
        json_file = temp_output_file.with_suffix('.json')
        result = JSONExporter.export_session(sample_session, json_file)
        
        assert result is True
        assert json_file.exists()


class TestTXTExporter:
    """Tests pour TXTExporter"""
    
    def test_export_character(self, sample_character, temp_output_file):
        """Vérifie l'export d'un personnage en TXT"""
        txt_file = temp_output_file.with_suffix('.txt')
        result = TXTExporter.export_character(sample_character, txt_file)
        
        assert result is True
        assert txt_file.exists()
        
        # Vérifier le contenu
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        assert sample_character.name in content
    
    def test_export_scene(self, sample_scene, temp_output_file):
        """Vérifie l'export d'une scène en TXT"""
        txt_file = temp_output_file.with_suffix('.txt')
        result = TXTExporter.export_scene(sample_scene, txt_file)
        
        assert result is True
        assert txt_file.exists()
    
    def test_export_session(self, sample_session, temp_output_file):
        """Vérifie l'export d'une session en TXT"""
        txt_file = temp_output_file.with_suffix('.txt')
        result = TXTExporter.export_session(sample_session, txt_file)
        
        assert result is True
        assert txt_file.exists()


class TestMarkdownExporter:
    """Tests pour MarkdownExporter"""
    
    def test_export_character(self, sample_character, temp_output_file):
        """Vérifie l'export d'un personnage en Markdown"""
        md_file = temp_output_file.with_suffix('.md')
        result = MarkdownExporter.export_character(sample_character, md_file)
        
        assert result is True
        assert md_file.exists()
        
        # Vérifier le contenu
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        assert sample_character.name in content
        assert '#' in content  # Markdown utilise # pour les titres
    
    def test_export_scene(self, sample_scene, temp_output_file):
        """Vérifie l'export d'une scène en Markdown"""
        md_file = temp_output_file.with_suffix('.md')
        result = MarkdownExporter.export_scene(sample_scene, md_file)
        
        assert result is True
        assert md_file.exists()
    
    def test_export_session(self, sample_session, temp_output_file):
        """Vérifie l'export d'une session en Markdown"""
        md_file = temp_output_file.with_suffix('.md')
        result = MarkdownExporter.export_session(sample_session, md_file)
        
        assert result is True
        assert md_file.exists()

