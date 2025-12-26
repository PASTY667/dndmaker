"""
Éditeur de session
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QListWidget,
    QListWidgetItem, QCheckBox, QMessageBox, QDateTimeEdit
)
from PyQt6.QtCore import Qt, QDateTime
from datetime import datetime
from typing import Optional

from ...models.session import Session
from ...services.project_service import ProjectService


class SessionEditor(QDialog):
    """Éditeur de session"""
    
    def __init__(self, project_service: ProjectService, session: Optional[Session] = None, parent=None):
        super().__init__(parent)
        self.project_service = project_service
        self.session = session
        self.is_new = session is None
        
        if self.is_new:
            self.setWindowTitle("Nouvelle session")
        else:
            self.setWindowTitle(f"Modifier: {session.title}")
        
        self._init_ui()
        
        if not self.is_new:
            self._load_session_data()
    
    def _init_ui(self):
        """Initialise l'interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Titre
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Titre:"))
        self.title_edit = QLineEdit()
        title_layout.addWidget(self.title_edit, stretch=1)
        layout.addLayout(title_layout)
        
        # Date et préparation
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date:"))
        self.date_edit = QDateTimeEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDateTime(QDateTime.currentDateTime())
        date_layout.addWidget(self.date_edit)
        
        self.preparation_check = QCheckBox("Session de préparation")
        date_layout.addWidget(self.preparation_check)
        date_layout.addStretch()
        layout.addLayout(date_layout)
        
        # Scènes
        scenes_label = QLabel("Scènes (dans l'ordre):")
        layout.addWidget(scenes_label)
        
        scenes_layout = QHBoxLayout()
        
        # Liste des scènes disponibles
        available_label = QLabel("Disponibles:")
        scenes_layout.addWidget(available_label)
        
        available_layout = QVBoxLayout()
        self.available_scenes = QListWidget()
        available_layout.addWidget(self.available_scenes)
        
        available_btn_layout = QHBoxLayout()
        self.add_scene_btn = QPushButton("→")
        self.add_scene_btn.clicked.connect(self._add_scene)
        available_btn_layout.addWidget(self.add_scene_btn)
        available_layout.addLayout(available_btn_layout)
        scenes_layout.addLayout(available_layout)
        
        # Liste des scènes de la session
        session_label = QLabel("Scènes de la session:")
        scenes_layout.addWidget(session_label)
        
        session_layout = QVBoxLayout()
        self.session_scenes = QListWidget()
        session_layout.addWidget(self.session_scenes)
        
        session_btn_layout = QHBoxLayout()
        self.remove_scene_btn = QPushButton("←")
        self.remove_scene_btn.clicked.connect(self._remove_scene)
        session_btn_layout.addWidget(self.remove_scene_btn)
        
        move_up_btn = QPushButton("↑")
        move_up_btn.clicked.connect(self._move_scene_up)
        session_btn_layout.addWidget(move_up_btn)
        
        move_down_btn = QPushButton("↓")
        move_down_btn.clicked.connect(self._move_scene_down)
        session_btn_layout.addWidget(move_down_btn)
        
        session_layout.addLayout(session_btn_layout)
        scenes_layout.addLayout(session_layout)
        
        layout.addLayout(scenes_layout)
        
        # Notes post-session
        notes_label = QLabel("Notes post-session:")
        layout.addWidget(notes_label)
        self.notes_edit = QTextEdit()
        self.notes_edit.setMinimumHeight(150)
        layout.addWidget(self.notes_edit)
        
        # Boutons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("Enregistrer")
        save_btn.clicked.connect(self._save)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Charger les scènes disponibles
        self._load_available_scenes()
    
    def _load_available_scenes(self):
        """Charge les scènes disponibles"""
        self.available_scenes.clear()
        
        if not self.project_service.scene_service:
            return
        
        all_scenes = self.project_service.scene_service.get_all_scenes()
        session_scene_ids = self.session.scenes if self.session else []
        
        for scene in all_scenes:
            # Ne pas afficher les scènes déjà dans la session
            if scene.id not in session_scene_ids:
                item = QListWidgetItem(scene.title)
                item.setData(Qt.ItemDataRole.UserRole, scene.id)
                self.available_scenes.addItem(item)
    
    def _load_session_data(self):
        """Charge les données de la session"""
        if not self.session:
            return
        
        self.title_edit.setText(self.session.title)
        self.date_edit.setDateTime(QDateTime.fromSecsSinceEpoch(
            int(self.session.date.timestamp())
        ))
        self.preparation_check.setChecked(self.session.is_preparation)
        self.notes_edit.setPlainText(self.session.post_session_notes)
        
        # Charger les scènes de la session
        self.session_scenes.clear()
        if self.project_service.scene_service:
            for scene_id in self.session.scenes:
                scene = self.project_service.scene_service.get_scene(scene_id)
                if scene:
                    item = QListWidgetItem(scene.title)
                    item.setData(Qt.ItemDataRole.UserRole, scene_id)
                    self.session_scenes.addItem(item)
        
        # Recharger les scènes disponibles
        self._load_available_scenes()
    
    def _add_scene(self):
        """Ajoute une scène à la session"""
        current_item = self.available_scenes.currentItem()
        if not current_item:
            return
        
        scene_id = current_item.data(Qt.ItemDataRole.UserRole)
        scene = self.project_service.scene_service.get_scene(scene_id)
        
        if scene:
            item = QListWidgetItem(scene.title)
            item.setData(Qt.ItemDataRole.UserRole, scene_id)
            self.session_scenes.addItem(item)
            
            # Retirer de la liste disponible
            self.available_scenes.takeItem(self.available_scenes.row(current_item))
    
    def _remove_scene(self):
        """Retire une scène de la session"""
        current_item = self.session_scenes.currentItem()
        if not current_item:
            return
        
        scene_id = current_item.data(Qt.ItemDataRole.UserRole)
        scene = self.project_service.scene_service.get_scene(scene_id)
        
        if scene:
            # Remettre dans la liste disponible
            item = QListWidgetItem(scene.title)
            item.setData(Qt.ItemDataRole.UserRole, scene_id)
            self.available_scenes.addItem(item)
            
            # Retirer de la session
            self.session_scenes.takeItem(self.session_scenes.row(current_item))
    
    def _move_scene_up(self):
        """Déplace une scène vers le haut"""
        current_row = self.session_scenes.currentRow()
        if current_row > 0:
            item = self.session_scenes.takeItem(current_row)
            self.session_scenes.insertItem(current_row - 1, item)
            self.session_scenes.setCurrentRow(current_row - 1)
    
    def _move_scene_down(self):
        """Déplace une scène vers le bas"""
        current_row = self.session_scenes.currentRow()
        if current_row < self.session_scenes.count() - 1:
            item = self.session_scenes.takeItem(current_row)
            self.session_scenes.insertItem(current_row + 1, item)
            self.session_scenes.setCurrentRow(current_row + 1)
    
    def _save(self):
        """Sauvegarde la session"""
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "Erreur", "Le titre est obligatoire")
            return
        
        date = self.date_edit.dateTime().toPyDateTime()
        is_preparation = self.preparation_check.isChecked()
        notes = self.notes_edit.toPlainText()
        
        # Récupérer l'ordre des scènes
        scene_ids = []
        for i in range(self.session_scenes.count()):
            item = self.session_scenes.item(i)
            scene_ids.append(item.data(Qt.ItemDataRole.UserRole))
        
        if self.is_new:
            # Créer une nouvelle session
            self.session = self.project_service.session_service.create_session(
                title, date, is_preparation
            )
            self.session.scenes = scene_ids
            self.session.post_session_notes = notes
            self.session.updated_at = datetime.now()
        else:
            # Mettre à jour la session existante
            self.session.title = title
            self.session.date = date
            self.session.is_preparation = is_preparation
            self.session.scenes = scene_ids
            self.session.post_session_notes = notes
            self.session.updated_at = datetime.now()
            self.project_service.session_service.update_session(self.session)
        
        self.accept()

