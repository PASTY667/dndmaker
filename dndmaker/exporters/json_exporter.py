"""
Exporteur JSON
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from ..models.character import Character
from ..models.scene import Scene
from ..models.session import Session
from ..persistence.serializer import serialize_model


class JSONExporter:
    """Exporteur JSON"""
    
    @staticmethod
    def export_character(character: Character, output_path: Path) -> bool:
        """Exporte un personnage en JSON"""
        try:
            data = serialize_model(character)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erreur lors de l'export JSON: {e}")
            return False
    
    @staticmethod
    def export_characters(characters: List[Character], output_path: Path) -> bool:
        """Exporte plusieurs personnages en JSON"""
        try:
            data = [serialize_model(char) for char in characters]
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erreur lors de l'export JSON: {e}")
            return False
    
    @staticmethod
    def export_scene(scene: Scene, output_path: Path) -> bool:
        """Exporte une scène en JSON"""
        try:
            data = serialize_model(scene)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erreur lors de l'export JSON: {e}")
            return False
    
    @staticmethod
    def export_session(session: Session, output_path: Path) -> bool:
        """Exporte une session en JSON"""
        try:
            data = serialize_model(session)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erreur lors de l'export JSON: {e}")
            return False

