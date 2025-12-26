"""
Vue des sessions
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt
from datetime import datetime

from ...services.project_service import ProjectService
from ...core.logger import get_logger
from ...core.i18n import tr

logger = get_logger()


class SessionsView(QWidget):
    """Vue des sessions"""
    
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
        self.title_label = QLabel(tr("session.title"))
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.title_label)
        
        # Boutons
        button_layout = QHBoxLayout()
        
        self.new_btn = QPushButton(tr("session.create"))
        self.new_btn.clicked.connect(self._new_session)
        button_layout.addWidget(self.new_btn)
        
        self.edit_btn = QPushButton(tr("character.edit"))
        self.edit_btn.clicked.connect(self._edit_session)
        self.edit_btn.setEnabled(False)
        button_layout.addWidget(self.edit_btn)
        
        self.duplicate_btn = QPushButton(tr("session.duplicate"))
        self.duplicate_btn.clicked.connect(self._duplicate_session)
        self.duplicate_btn.setEnabled(False)
        button_layout.addWidget(self.duplicate_btn)
        
        self.delete_btn = QPushButton(tr("character.delete"))
        self.delete_btn.clicked.connect(self._delete_session)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Liste des sessions
        self.session_list = QListWidget()
        self.session_list.itemSelectionChanged.connect(self._on_selection_changed)
        self.session_list.itemDoubleClicked.connect(self._edit_session)
        layout.addWidget(self.session_list)
    
    def refresh(self):
        """Rafraîchit la vue"""
        self.session_list.clear()
        
        if not self.project_service.session_service:
            return
        
        sessions = self.project_service.session_service.get_all_sessions()
        for session in sessions:
            item_text = f"{session.title}"
            if session.is_preparation:
                item_text += " [Préparation]"
            item_text += f" - {session.date.strftime('%d/%m/%Y')}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, session.id)
            self.session_list.addItem(item)
    
    def _on_selection_changed(self):
        """Gère le changement de sélection"""
        has_selection = len(self.session_list.selectedItems()) > 0
        self.edit_btn.setEnabled(has_selection)
        self.duplicate_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
    
    def _new_session(self):
        """Crée une nouvelle session"""
        from PyQt6.QtWidgets import QInputDialog
        title, ok = QInputDialog.getText(self, "Nouvelle session", "Titre:")
        if ok and title:
            try:
                session = self.project_service.session_service.create_session(title)
                self.project_service.save_project(f"Création de la session '{title}'")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def _edit_session(self):
        """Modifie une session"""
        current_item = self.session_list.currentItem()
        if not current_item:
            logger.log_ui_action("Modification de session - aucune sélection")
            return
        
        session_id = current_item.data(Qt.ItemDataRole.UserRole)
        session = self.project_service.session_service.get_session(session_id)
        
        if session:
            logger.log_session_action("Modification", session_title=session.title, session_id=session_id)
            from ..widgets.session_editor import SessionEditor
            editor = SessionEditor(self.project_service, session, self)
            if editor.exec():
                self.project_service.save_project(f"Modification de la session '{session.title}'")
                logger.log_session_action("Modifiée et sauvegardée", session_title=session.title)
                self.refresh()
            else:
                logger.log_ui_action("Modification de session annulée", session_title=session.title)
    
    def _duplicate_session(self):
        """Duplique une session"""
        current_item = self.session_list.currentItem()
        if not current_item:
            return
        
        session_id = current_item.data(Qt.ItemDataRole.UserRole)
        try:
            new_session = self.project_service.session_service.duplicate_session(session_id)
            self.project_service.save_project(f"Duplication de session")
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def _delete_session(self):
        """Supprime une session"""
        current_item = self.session_list.currentItem()
        if not current_item:
            return
        
        session_id = current_item.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir supprimer cette session ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.project_service.session_service.delete_session(session_id):
                self.project_service.save_project("Suppression de session")
                self.refresh()
            else:
                QMessageBox.warning(self, "Erreur", "Impossible de supprimer la session")
    
    def on_language_changed(self):
        """Met à jour les textes lors du changement de langue"""
        self.title_label.setText(tr("session.title"))
        self.new_btn.setText(tr("session.create"))
        self.edit_btn.setText(tr("character.edit"))
        self.duplicate_btn.setText(tr("session.duplicate"))
        self.delete_btn.setText(tr("character.delete"))
        self.refresh()
    
    def refresh(self):
        """Rafraîchit la vue"""
        self.session_list.clear()
        
        if not self.project_service.session_service:
            return
        
        sessions = self.project_service.session_service.get_all_sessions()
        for session in sessions:
            item = QListWidgetItem(f"{session.title} - {session.date.strftime('%d/%m/%Y')}")
            item.setData(Qt.ItemDataRole.UserRole, session.id)
            self.session_list.addItem(item)

