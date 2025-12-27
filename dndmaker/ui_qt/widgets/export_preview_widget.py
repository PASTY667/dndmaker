"""
Widget de prévisualisation pour les exports
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
from pathlib import Path
import tempfile
from typing import Optional

from ...models.character import Character
from ...models.scene import Scene
from ...models.session import Session
from ...services.project_service import ProjectService
from ...core.i18n import tr


class ExportPreviewWidget(QWidget):
    """Widget de prévisualisation pour les exports"""
    
    def __init__(self, project_service: ProjectService, parent=None):
        super().__init__(parent)
        self.project_service = project_service
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Titre
        title = QLabel("Prévisualisation")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Zone de prévisualisation
        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        self.preview_area.setFontFamily("Courier")
        self.preview_area.setFontPointSize(10)
        layout.addWidget(self.preview_area)
        
        # Message par défaut
        self.preview_area.setPlainText("Sélectionnez un élément et un format pour voir la prévisualisation")
    
    def preview_character(self, character: Character, format_type: str):
        """Prévisualise l'export d'un personnage"""
        if format_type == "PDF":
            self.preview_area.setPlainText(
                "Prévisualisation PDF non disponible.\n"
                "Le PDF sera généré avec la mise en page complète."
            )
        elif format_type == "JSON":
            from ...exporters.json_exporter import JSONExporter
            from ...persistence.serializer import serialize_model
            data = serialize_model(character)
            import json
            preview_text = json.dumps(data, indent=2, ensure_ascii=False)
            self.preview_area.setPlainText(preview_text)
        elif format_type == "TXT":
            self._preview_txt_character(character)
        elif format_type == "Markdown":
            self._preview_markdown_character(character)
    
    def preview_scene(self, scene: Scene, format_type: str):
        """Prévisualise l'export d'une scène"""
        if format_type == "PDF":
            self.preview_area.setPlainText(
                "Prévisualisation PDF non disponible.\n"
                "Le PDF sera généré avec la mise en page complète."
            )
        elif format_type == "JSON":
            from ...exporters.json_exporter import JSONExporter
            from ...persistence.serializer import serialize_model
            data = serialize_model(scene)
            import json
            preview_text = json.dumps(data, indent=2, ensure_ascii=False)
            self.preview_area.setPlainText(preview_text)
        elif format_type == "TXT":
            self._preview_txt_scene(scene)
        elif format_type == "Markdown":
            self._preview_markdown_scene(scene)
    
    def preview_session(self, session: Session, format_type: str):
        """Prévisualise l'export d'une session"""
        if format_type == "PDF":
            self.preview_area.setPlainText(
                "Prévisualisation PDF non disponible.\n"
                "Le PDF sera généré avec la mise en page complète."
            )
        elif format_type == "JSON":
            from ...exporters.json_exporter import JSONExporter
            from ...persistence.serializer import serialize_model
            data = serialize_model(session)
            import json
            preview_text = json.dumps(data, indent=2, ensure_ascii=False)
            self.preview_area.setPlainText(preview_text)
        elif format_type == "TXT":
            self._preview_txt_session(session)
        elif format_type == "Markdown":
            self._preview_markdown_session(session)
    
    def _preview_txt_character(self, character: Character):
        """Génère une prévisualisation TXT pour un personnage"""
        lines = []
        lines.append("=" * 60)
        lines.append(f"FICHE DE PERSONNAGE: {character.name}")
        lines.append("=" * 60)
        lines.append("")
        lines.append("PROFIL")
        lines.append("-" * 60)
        lines.append(f"Type: {character.type.value}")
        lines.append(f"Niveau: {character.profile.level}")
        lines.append(f"Race: {character.profile.race or '-'}")
        lines.append(f"Classe: {character.profile.character_class or '-'}")
        lines.append("")
        lines.append("CARACTÉRISTIQUES")
        lines.append("-" * 60)
        lines.append(f"FOR: {character.characteristics.strength.value} ({character.characteristics.strength.modifier:+d})")
        lines.append(f"DEX: {character.characteristics.dexterity.value} ({character.characteristics.dexterity.modifier:+d})")
        lines.append(f"CON: {character.characteristics.constitution.value} ({character.characteristics.constitution.modifier:+d})")
        lines.append(f"INT: {character.characteristics.intelligence.value} ({character.characteristics.intelligence.modifier:+d})")
        lines.append(f"SAG: {character.characteristics.wisdom.value} ({character.characteristics.wisdom.modifier:+d})")
        lines.append(f"CHA: {character.characteristics.charisma.value} ({character.characteristics.charisma.modifier:+d})")
        lines.append("")
        if character.notes:
            lines.append("NOTES")
            lines.append("-" * 60)
            lines.append(character.notes)
        
        self.preview_area.setPlainText("\n".join(lines))
    
    def _preview_txt_scene(self, scene: Scene):
        """Génère une prévisualisation TXT pour une scène"""
        lines = []
        lines.append("=" * 60)
        lines.append(f"SCÈNE: {scene.title}")
        lines.append("=" * 60)
        lines.append("")
        if scene.description:
            lines.append("DESCRIPTION")
            lines.append("-" * 60)
            lines.append(scene.description)
            lines.append("")
        if scene.notes:
            lines.append("NOTES")
            lines.append("-" * 60)
            lines.append(scene.notes)
        
        self.preview_area.setPlainText("\n".join(lines))
    
    def _preview_txt_session(self, session: Session):
        """Génère une prévisualisation TXT pour une session"""
        lines = []
        lines.append("=" * 60)
        lines.append(f"SESSION: {session.title}")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"Date: {session.date.strftime('%d/%m/%Y')}")
        lines.append("")
        if session.post_session_notes:
            lines.append("NOTES POST-SESSION")
            lines.append("-" * 60)
            lines.append(session.post_session_notes)
        
        self.preview_area.setPlainText("\n".join(lines))
    
    def _preview_markdown_character(self, character: Character):
        """Génère une prévisualisation Markdown pour un personnage"""
        lines = []
        lines.append(f"# {character.name}")
        lines.append("")
        lines.append("## Profil")
        lines.append("")
        lines.append(f"- **Type:** {character.type.value}")
        lines.append(f"- **Niveau:** {character.profile.level}")
        lines.append(f"- **Race:** {character.profile.race or '-'}")
        lines.append(f"- **Classe:** {character.profile.character_class or '-'}")
        lines.append("")
        lines.append("## Caractéristiques")
        lines.append("")
        lines.append(f"- **FOR:** {character.characteristics.strength.value} ({character.characteristics.strength.modifier:+d})")
        lines.append(f"- **DEX:** {character.characteristics.dexterity.value} ({character.characteristics.dexterity.modifier:+d})")
        lines.append(f"- **CON:** {character.characteristics.constitution.value} ({character.characteristics.constitution.modifier:+d})")
        lines.append(f"- **INT:** {character.characteristics.intelligence.value} ({character.characteristics.intelligence.modifier:+d})")
        lines.append(f"- **SAG:** {character.characteristics.wisdom.value} ({character.characteristics.wisdom.modifier:+d})")
        lines.append(f"- **CHA:** {character.characteristics.charisma.value} ({character.characteristics.charisma.modifier:+d})")
        lines.append("")
        if character.notes:
            lines.append("## Notes")
            lines.append("")
            lines.append(character.notes)
        
        self.preview_area.setPlainText("\n".join(lines))
    
    def _preview_markdown_scene(self, scene: Scene):
        """Génère une prévisualisation Markdown pour une scène"""
        lines = []
        lines.append(f"# {scene.title}")
        lines.append("")
        if scene.description:
            lines.append("## Description")
            lines.append("")
            lines.append(scene.description)
            lines.append("")
        if scene.notes:
            lines.append("## Notes")
            lines.append("")
            lines.append(scene.notes)
        
        self.preview_area.setPlainText("\n".join(lines))
    
    def _preview_markdown_session(self, session: Session):
        """Génère une prévisualisation Markdown pour une session"""
        lines = []
        lines.append(f"# {session.title}")
        lines.append("")
        lines.append(f"**Date:** {session.date.strftime('%d/%m/%Y')}")
        lines.append("")
        if session.post_session_notes:
            lines.append("## Notes post-session")
            lines.append("")
            lines.append(session.post_session_notes)
        
        self.preview_area.setPlainText("\n".join(lines))
    
    def clear_preview(self):
        """Efface la prévisualisation"""
        self.preview_area.setPlainText("Sélectionnez un élément et un format pour voir la prévisualisation")

