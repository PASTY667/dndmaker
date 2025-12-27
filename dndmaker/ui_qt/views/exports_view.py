"""
Vue des exports
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QFileDialog, QMessageBox,
    QListWidget, QListWidgetItem, QDialog, QDialogButtonBox
)
from pathlib import Path

from ...services.project_service import ProjectService
from ...models.character import Character, CharacterType
from ...models.scene import Scene
from ...models.session import Session
from ...core.logger import UserActionLogger
from ...core.i18n import tr

logger = UserActionLogger()


class SelectionDialog(QDialog):
    """Dialogue de sélection d'éléments à exporter"""
    
    def __init__(self, title: str, items: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        
        layout = QVBoxLayout(self)
        
        label = QLabel(f"Sélectionnez les éléments à exporter:")
        layout.addWidget(label)
        
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        for item in items:
            list_item = QListWidgetItem(str(item))
            list_item.setData(256, item)  # UserRole
            self.list_widget.addItem(list_item)
        
        layout.addWidget(self.list_widget)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_selected_items(self):
        """Retourne les éléments sélectionnés"""
        selected = []
        for item in self.list_widget.selectedItems():
            selected.append(item.data(256))  # UserRole
        return selected


class ExportsView(QWidget):
    """Vue des exports"""
    
    def __init__(self, project_service: ProjectService, parent=None):
        super().__init__(parent)
        self.project_service = project_service
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Titre
        self.title_label = QLabel(tr("export.title"))
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.title_label)
        
        # Type d'export
        self.type_label = QLabel(tr("export.type"))
        layout.addWidget(self.type_label)
        
        self.export_type = QComboBox()
        self._update_export_types()
        self.export_type.currentTextChanged.connect(self._on_export_type_changed)
        layout.addWidget(self.export_type)
        
        # Sélection de l'élément
        self.selection_label = QLabel(tr("export.element"))
        layout.addWidget(self.selection_label)
        
        self.element_combo = QComboBox()
        self.element_combo.setEnabled(False)
        layout.addWidget(self.element_combo)
        
        # Format
        self.format_label = QLabel(tr("export.format"))
        layout.addWidget(self.format_label)
        
        self.export_format = QComboBox()
        self.export_format.addItems(["PDF", "JSON", "TXT", "Markdown"])
        layout.addWidget(self.export_format)
        
        # Bouton de prévisualisation
        self.preview_btn = QPushButton("Prévisualiser")
        self.preview_btn.clicked.connect(self._preview)
        layout.addWidget(self.preview_btn)
        
        # Bouton d'export
        self.export_btn = QPushButton(tr("export.export"))
        self.export_btn.clicked.connect(self._export)
        layout.addWidget(self.export_btn)
        
        # Widget de prévisualisation
        from ..widgets.export_preview_widget import ExportPreviewWidget
        self.preview_widget = ExportPreviewWidget(self.project_service, self)
        layout.addWidget(self.preview_widget)
        
        layout.addStretch()
        
        # Initialiser les éléments
        self._on_export_type_changed(self.export_type.currentText())
    
    def _update_export_types(self):
        """Met à jour les types d'export avec les traductions"""
        current_text = self.export_type.currentText() if self.export_type.count() > 0 else ""
        self.export_type.clear()
        self.export_type.addItems([
            tr("export.character"),
            tr("export.npc"),
            tr("export.scene"),
            tr("export.session"),
            tr("export.full")
        ])
        # Restaurer la sélection si possible
        if current_text:
            index = self.export_type.findText(current_text)
            if index >= 0:
                self.export_type.setCurrentIndex(index)
    
    def on_language_changed(self):
        """Met à jour les textes lors du changement de langue"""
        self.title_label.setText(tr("export.title"))
        self.type_label.setText(tr("export.type"))
        self.selection_label.setText(tr("export.element"))
        self.format_label.setText(tr("export.format"))
        self.export_btn.setText(tr("export.export"))
        self._update_export_types()
        self.refresh()
    
    def refresh(self):
        """Rafraîchit la vue"""
        self._on_export_type_changed(self.export_type.currentText())
    
    def _on_export_type_changed(self, export_type: str):
        """Met à jour la liste des éléments selon le type d'export"""
        self.element_combo.clear()
        self.element_combo.setEnabled(True)
        
        if not self.project_service.get_current_project():
            self.element_combo.setEnabled(False)
            return
        
        if export_type == "Fiche PJ":
            pj_chars = self.project_service.character_service.get_characters_by_type(CharacterType.PJ)
            for char in pj_chars:
                self.element_combo.addItem(char.name, char)
        
        elif export_type == "Fiche PNJ/Créature":
            # Regrouper PNJ et Créatures
            pnjs = self.project_service.character_service.get_characters_by_type(CharacterType.PNJ)
            creatures = self.project_service.character_service.get_characters_by_type(CharacterType.CREATURE)
            all_chars = pnjs + creatures
            for char in all_chars:
                char_type_label = "PNJ" if char.type == CharacterType.PNJ else "Créature"
                self.element_combo.addItem(f"{char.name} ({char_type_label})", char)
        
        elif export_type == "Scène":
            scenes = self.project_service.scene_service.get_all_scenes()
            for scene in scenes:
                self.element_combo.addItem(scene.title, scene)
        
        elif export_type == "Session":
            sessions = self.project_service.session_service.get_all_sessions()
            for session in sessions:
                self.element_combo.addItem(session.title, session)
        
        elif export_type == "Scénario complet":
            # Pour le scénario complet, pas besoin de sélection
            self.element_combo.setEnabled(False)
            self.element_combo.addItem("Tout le projet", None)
    
    def _export(self):
        """Effectue un export"""
        if not self.project_service.get_current_project():
            QMessageBox.warning(self, "Attention", "Veuillez ouvrir ou créer un projet avant d'exporter.")
            return
        
        export_type = self.export_type.currentText()
        export_format = self.export_format.currentText()
        
        # Déterminer le chemin de sortie
        default_name = "export"
        if export_type == "Fiche PJ" or export_type == "Fiche PNJ/Créature":
            selected_index = self.element_combo.currentIndex()
            if selected_index < 0:
                QMessageBox.warning(self, "Attention", "Veuillez sélectionner un élément à exporter.")
                return
            element = self.element_combo.currentData()
            if element:
                default_name = element.name
        elif export_type == "Scène":
            element = self.element_combo.currentData()
            if element:
                default_name = element.title
        elif export_type == "Session":
            element = self.element_combo.currentData()
            if element:
                default_name = element.title
        
        # Extension selon le format
        extensions = {
            "PDF": "pdf",
            "JSON": "json",
            "TXT": "txt",
            "Markdown": "md"
        }
        ext = extensions.get(export_format, "txt")
        
        # Dialogue de sauvegarde
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter",
            f"{default_name}.{ext}",
            f"{export_format} (*.{ext})"
        )
        
        if not file_path:
            return
        
        output_path = Path(file_path)
        
        try:
            # Importer les exporters
            from ...exporters.pdf_exporter import PDFExporter
            from ...exporters.json_exporter import JSONExporter
            from ...exporters.txt_exporter import TXTExporter
            from ...exporters.markdown_exporter import MarkdownExporter
            
            success = False
            
            if export_type == "Fiche PJ":
                element = self.element_combo.currentData()
                if not element:
                    QMessageBox.warning(self, "Erreur", "Aucun personnage sélectionné.")
                    return
                
                if export_format == "PDF":
                    exporter = PDFExporter(self.project_service)
                    success = exporter.export_character_sheet(element, output_path)
                elif export_format == "JSON":
                    success = JSONExporter.export_character(element, output_path)
                elif export_format == "TXT":
                    success = TXTExporter.export_character(element, output_path)
                elif export_format == "Markdown":
                    success = MarkdownExporter.export_character(element, output_path)
            
            elif export_type == "Fiche PNJ/Créature":
                element = self.element_combo.currentData()
                if not element:
                    QMessageBox.warning(self, "Erreur", "Aucun personnage sélectionné.")
                    return
                
                if export_format == "PDF":
                    exporter = PDFExporter(self.project_service)
                    success = exporter.export_character_sheet(element, output_path)
                elif export_format == "JSON":
                    success = JSONExporter.export_character(element, output_path)
                elif export_format == "TXT":
                    success = TXTExporter.export_character(element, output_path)
                elif export_format == "Markdown":
                    success = MarkdownExporter.export_character(element, output_path)
            
            elif export_type == "Scène":
                element = self.element_combo.currentData()
                if not element:
                    QMessageBox.warning(self, "Erreur", "Aucune scène sélectionnée.")
                    return
                
                if export_format == "PDF":
                    exporter = PDFExporter(self.project_service)
                    success = exporter.export_scene(element, output_path)
                elif export_format == "JSON":
                    success = JSONExporter.export_scene(element, output_path)
                elif export_format == "TXT":
                    success = TXTExporter.export_scene(element, output_path)
                elif export_format == "Markdown":
                    success = MarkdownExporter.export_scene(element, output_path)
            
            elif export_type == "Session":
                element = self.element_combo.currentData()
                if not element:
                    QMessageBox.warning(self, "Erreur", "Aucune session sélectionnée.")
                    return
                
                if export_format == "PDF":
                    exporter = PDFExporter(self.project_service)
                    success = exporter.export_session(element, output_path)
                elif export_format == "JSON":
                    success = JSONExporter.export_session(element, output_path)
                elif export_format == "TXT":
                    success = TXTExporter.export_session(element, output_path)
                elif export_format == "Markdown":
                    success = MarkdownExporter.export_session(element, output_path)
            
            elif export_type == "Scénario complet":
                # Export de tout le projet
                if export_format == "JSON":
                    # Exporter tout en JSON
                    from ...persistence.serializer import serialize_model
                    project = self.project_service.get_current_project()
                    
                    characters = self.project_service.character_service.get_all_characters()
                    scenes = self.project_service.scene_service.get_all_scenes()
                    sessions = self.project_service.session_service.get_all_sessions()
                    
                    data = {
                        "project": serialize_model(project) if project else {},
                        "characters": [serialize_model(char) for char in characters],
                        "scenes": [serialize_model(scene) for scene in scenes],
                        "sessions": [serialize_model(session) for session in sessions]
                    }
                    import json
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                    success = True
                else:
                    QMessageBox.warning(self, "Attention", "Le scénario complet n'est disponible qu'en JSON pour le moment.")
                    return
            
            if success:
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Export réussi vers:\n{output_path}"
                )
                logger.log_ui_action("Export réussi", export_type=export_type, format=export_format, path=str(output_path))
            else:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    "Une erreur est survenue lors de l'export."
                )
        
        except Exception as e:
            logger.exception(f"Erreur lors de l'export: {e}")
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de l'export:\n{str(e)}"
            )
    
    def _preview(self):
        """Affiche la prévisualisation de l'export"""
        self._update_preview()
    
    def _update_preview(self):
        """Met à jour la prévisualisation automatiquement"""
        export_type = self.export_type.currentText()
        export_format = self.export_format.currentText()
        
        if not self.project_service.get_current_project():
            self.preview_widget.clear_preview()
            return
        
        selected_index = self.element_combo.currentIndex()
        if selected_index < 0:
            self.preview_widget.clear_preview()
            return
        
        element = self.element_combo.currentData()
        if not element:
            self.preview_widget.clear_preview()
            return
        
        # Générer la prévisualisation selon le type
        if export_type == "Fiche PJ" or export_type == "Fiche PNJ/Créature":
            from ...models.character import Character
            if isinstance(element, Character):
                self.preview_widget.preview_character(element, export_format)
        elif export_type == "Scène":
            from ...models.scene import Scene
            if isinstance(element, Scene):
                self.preview_widget.preview_scene(element, export_format)
        elif export_type == "Session":
            from ...models.session import Session
            if isinstance(element, Session):
                self.preview_widget.preview_session(element, export_format)
        else:
            self.preview_widget.clear_preview()
