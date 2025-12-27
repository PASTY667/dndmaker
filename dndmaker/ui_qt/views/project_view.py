"""
Vue de la campagne
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QListWidget, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional

from ...services.project_service import ProjectService
from ...models.project import Project
from ...core.i18n import tr


class ProjectView(QWidget):
    """Vue de la campagne"""
    
    # Signaux pour communiquer avec la fenêtre principale
    new_project_requested = pyqtSignal()
    open_project_requested = pyqtSignal()
    import_project_requested = pyqtSignal(str)  # Chemin du fichier JSON
    
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
        self.title_label = QLabel(tr("campaign.title"))
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.title_label)
        
        # Boutons d'action
        action_layout = QHBoxLayout()
        
        self.new_project_btn = QPushButton(tr("campaign.new"))
        self.new_project_btn.clicked.connect(self._on_new_project)
        action_layout.addWidget(self.new_project_btn)
        
        self.open_project_btn = QPushButton(tr("campaign.open"))
        self.open_project_btn.clicked.connect(self._on_open_project)
        action_layout.addWidget(self.open_project_btn)
        
        self.import_project_btn = QPushButton(tr("campaign.import"))
        self.import_project_btn.clicked.connect(self._on_import_project)
        action_layout.addWidget(self.import_project_btn)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        # Informations de la campagne
        self.project_info = QLabel(tr("campaign.info"))
        layout.addWidget(self.project_info)
        
        # Historique des versions
        self.history_label = QLabel(tr("campaign.history"))
        layout.addWidget(self.history_label)
        
        self.version_list = QListWidget()
        layout.addWidget(self.version_list)
        
        # Boutons
        button_layout = QHBoxLayout()
        
        self.rollback_btn = QPushButton(tr("campaign.rollback"))
        self.rollback_btn.clicked.connect(self._rollback_version)
        self.rollback_btn.setEnabled(False)
        button_layout.addWidget(self.rollback_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Métadonnées
        self.metadata_label = QLabel(tr("campaign.metadata"))
        layout.addWidget(self.metadata_label)
        
        self.metadata_edit = QTextEdit()
        self.metadata_edit.setMaximumHeight(100)
        layout.addWidget(self.metadata_edit)
        
        self.save_metadata_btn = QPushButton(tr("campaign.save_metadata"))
        self.save_metadata_btn.clicked.connect(self._save_metadata)
        layout.addWidget(self.save_metadata_btn)
        
        layout.addStretch()
    
    def _on_new_project(self):
        """Émet un signal pour créer une nouvelle campagne"""
        self.new_project_requested.emit()
    
    def _on_open_project(self):
        """Émet un signal pour ouvrir une campagne"""
        self.open_project_requested.emit()
    
    def _on_import_project(self):
        """Ouvre un dialogue pour importer une campagne depuis un JSON"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            tr("campaign.import"),
            "",
            "Fichiers JSON (*.json);;Tous les fichiers (*.*)"
        )
        
        if file_path:
            self.import_project_requested.emit(file_path)
    
    def on_language_changed(self):
        """Met à jour les textes lors du changement de langue"""
        self.title_label.setText(tr("campaign.title"))
        self.new_project_btn.setText(tr("campaign.new"))
        self.open_project_btn.setText(tr("campaign.open"))
        self.import_project_btn.setText(tr("campaign.import"))
        self.history_label.setText(tr("campaign.history"))
        self.rollback_btn.setText(tr("campaign.rollback"))
        self.metadata_label.setText(tr("campaign.metadata"))
        self.save_metadata_btn.setText(tr("campaign.save_metadata"))
        self.refresh()
    
    def refresh(self):
        """Rafraîchit la vue"""
        project = self.project_service.get_current_project()
        if project:
            name_label = tr("campaign.name")
            created_label = tr("campaign.created")
            modified_label = tr("campaign.modified")
            version_label = tr("campaign.version")
            
            self.project_info.setText(
                f"<b>{name_label}</b> {project.name}<br>"
                f"<b>{created_label}</b> {project.created_at.strftime('%d/%m/%Y %H:%M')}<br>"
                f"<b>{modified_label}</b> {project.updated_at.strftime('%d/%m/%Y %H:%M')}<br>"
                f"<b>{version_label}</b> {project.version}"
            )
            
            # Charger l'historique
            self._load_version_history()
            
            # Charger les métadonnées
            import json
            self.metadata_edit.setPlainText(json.dumps(project.metadata, indent=2, ensure_ascii=False))
        else:
            self.project_info.setText(tr("campaign.info"))
            self.version_list.clear()
            self.metadata_edit.clear()
    
    def _load_version_history(self):
        """Charge l'historique des versions"""
        self.version_list.clear()
        if not self.project_service.version_manager:
            return
        
        versions = self.project_service.version_manager.list_versions()
        for version in reversed(versions):  # Plus récent en premier
            item_text = (
                f"Version {version.version_number} - "
                f"{version.timestamp.strftime('%d/%m/%Y %H:%M')}"
            )
            if version.description:
                item_text += f" - {version.description}"
            self.version_list.addItem(item_text)
    
    def _rollback_version(self):
        """Effectue un rollback vers la version sélectionnée"""
        current_item = self.version_list.currentItem()
        if not current_item:
            return
        
        # Extraire le numéro de version
        text = current_item.text()
        version_num = int(text.split()[1])
        
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Êtes-vous sûr de vouloir restaurer la version {version_num} ?\n"
            "Cette action créera une nouvelle version.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.project_service.rollback_to_version(version_num):
                QMessageBox.information(self, "Succès", "Version restaurée avec succès")
                self.refresh()
            else:
                QMessageBox.warning(self, "Erreur", "Impossible de restaurer cette version")
    
    def _save_metadata(self):
        """Sauvegarde les métadonnées"""
        import json
        try:
            metadata_text = self.metadata_edit.toPlainText()
            metadata = json.loads(metadata_text) if metadata_text.strip() else {}
            
            project = self.project_service.get_current_project()
            if project:
                project.metadata = metadata
                self.project_service.save_project("Mise à jour des métadonnées")
                QMessageBox.information(self, "Succès", "Métadonnées sauvegardées")
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Erreur", "JSON invalide")

