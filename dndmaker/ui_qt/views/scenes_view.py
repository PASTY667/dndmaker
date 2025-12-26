"""
Vue des scènes
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt

from ...services.project_service import ProjectService
from ...core.logger import get_logger
from ...core.i18n import tr

logger = get_logger()


class ScenesView(QWidget):
    """Vue des scènes"""
    
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
        self.title_label = QLabel(tr("scene.title"))
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.title_label)
        
        # Boutons
        button_layout = QHBoxLayout()
        
        self.new_btn = QPushButton(tr("scene.create"))
        self.new_btn.clicked.connect(self._new_scene)
        button_layout.addWidget(self.new_btn)
        
        self.edit_btn = QPushButton(tr("character.edit"))
        self.edit_btn.clicked.connect(self._edit_scene)
        self.edit_btn.setEnabled(False)
        button_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton(tr("character.delete"))
        self.delete_btn.clicked.connect(self._delete_scene)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Liste des scènes
        self.scene_list = QListWidget()
        self.scene_list.itemSelectionChanged.connect(self._on_selection_changed)
        self.scene_list.itemDoubleClicked.connect(self._edit_scene)
        layout.addWidget(self.scene_list)
    
    def on_language_changed(self):
        """Met à jour les textes lors du changement de langue"""
        self.title_label.setText(tr("scene.title"))
        self.new_btn.setText(tr("scene.create"))
        self.edit_btn.setText(tr("character.edit"))
        self.delete_btn.setText(tr("character.delete"))
        self.refresh()
    
    def refresh(self):
        """Rafraîchit la vue"""
        self.scene_list.clear()
        
        if not self.project_service.scene_service:
            return
        
        scenes = self.project_service.scene_service.get_all_scenes()
        for scene in scenes:
            item = QListWidgetItem(scene.title)
            item.setData(Qt.ItemDataRole.UserRole, scene.id)
            self.scene_list.addItem(item)
    
    def _on_selection_changed(self):
        """Gère le changement de sélection"""
        has_selection = len(self.scene_list.selectedItems()) > 0
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
    
    def _new_scene(self):
        """Crée une nouvelle scène"""
        logger.log_ui_action("Création de scène demandée")
        from PyQt6.QtWidgets import QInputDialog
        title, ok = QInputDialog.getText(self, "Nouvelle scène", "Titre:")
        if ok and title:
            try:
                if not self.project_service.scene_service:
                    logger.warning("Service de scènes non disponible")
                    QMessageBox.warning(self, "Erreur", "Service de scènes non disponible")
                    return
                
                logger.log_scene_action("Création", scene_title=title)
                scene = self.project_service.scene_service.create_scene(title)
                
                # Sauvegarder seulement si un projet est ouvert
                if self.project_service.get_current_project():
                    self.project_service.save_project(f"Création de la scène '{title}'")
                    logger.log_scene_action("Créée et sauvegardée", scene_title=title, scene_id=scene.id)
                else:
                    logger.log_scene_action("Créée (non sauvegardée - pas de projet)", scene_title=title)
                    QMessageBox.information(
                        self,
                        "Information",
                        f"Scène '{title}' créée. Ouvrez ou créez un projet pour la sauvegarder."
                    )
                
                self.refresh()
            except Exception as e:
                logger.exception(f"Erreur lors de la création de la scène: {e}")
                QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
        else:
            logger.log_ui_action("Création de scène annulée")
    
    def _edit_scene(self):
        """Modifie une scène"""
        current_item = self.scene_list.currentItem()
        if not current_item:
            logger.log_ui_action("Modification de scène - aucune sélection")
            return
        
        scene_id = current_item.data(Qt.ItemDataRole.UserRole)
        scene = self.project_service.scene_service.get_scene(scene_id)
        
        if scene:
            logger.log_scene_action("Modification", scene_title=scene.title, scene_id=scene_id)
            from ..widgets.scene_editor import SceneEditor
            editor = SceneEditor(self.project_service, scene, self)
            if editor.exec():
                # Sauvegarder seulement si un projet est ouvert
                if self.project_service.get_current_project():
                    self.project_service.save_project(f"Modification de la scène '{scene.title}'")
                    logger.log_scene_action("Modifiée et sauvegardée", scene_title=scene.title)
                self.refresh()
            else:
                logger.log_ui_action("Modification de scène annulée", scene_title=scene.title)
    
    def _delete_scene(self):
        """Supprime une scène"""
        current_item = self.scene_list.currentItem()
        if not current_item:
            logger.log_ui_action("Suppression de scène - aucune sélection")
            return
        
        scene_id = current_item.data(Qt.ItemDataRole.UserRole)
        scene = self.project_service.scene_service.get_scene(scene_id)
        scene_title = scene.title if scene else "inconnue"
        
        logger.log_ui_action("Suppression de scène demandée", scene_title=scene_title, scene_id=scene_id)
        
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir supprimer cette scène ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.project_service.scene_service.delete_scene(scene_id):
                self.project_service.save_project("Suppression de scène")
                logger.log_scene_action("Supprimée", scene_title=scene_title, scene_id=scene_id)
                self.refresh()
            else:
                logger.warning(f"Impossible de supprimer la scène {scene_id}")
                QMessageBox.warning(self, "Erreur", "Impossible de supprimer la scène")
        else:
            logger.log_ui_action("Suppression de scène annulée", scene_title=scene_title)

