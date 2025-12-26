"""
Éditeur de scène
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QListWidget,
    QListWidgetItem, QTabWidget, QWidget, QMessageBox
)
from PyQt6.QtCore import Qt, QDateTime
from datetime import datetime
from typing import Optional, List

from ...models.scene import Scene, Event
from ...services.project_service import ProjectService
from ...core.utils import generate_id


class SceneEditor(QDialog):
    """Éditeur de scène"""
    
    def __init__(self, project_service: ProjectService, scene: Optional[Scene] = None, parent=None):
        super().__init__(parent)
        self.project_service = project_service
        self.scene = scene
        self.is_new = scene is None
        
        if self.is_new:
            self.setWindowTitle("Nouvelle scène")
        else:
            self.setWindowTitle(f"Modifier: {scene.title}")
        
        self._init_ui()
        
        if not self.is_new:
            self._load_scene_data()
    
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
        
        # Description
        desc_label = QLabel("Description:")
        layout.addWidget(desc_label)
        self.description_edit = QTextEdit()
        self.description_edit.setMinimumHeight(100)
        layout.addWidget(self.description_edit)
        
        # Onglets
        tabs = QTabWidget()
        
        # Onglet Références
        ref_tab = QWidget()
        ref_layout = QVBoxLayout(ref_tab)
        
        # PJ
        pj_label = QLabel("Personnages Joueurs (PJ):")
        ref_layout.addWidget(pj_label)
        self.pj_list = QListWidget()
        self.pj_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        ref_layout.addWidget(self.pj_list)
        
        pj_btn_layout = QHBoxLayout()
        self.add_pj_btn = QPushButton("Ajouter PJ")
        self.add_pj_btn.clicked.connect(self._add_pj)
        pj_btn_layout.addWidget(self.add_pj_btn)
        self.remove_pj_btn = QPushButton("Retirer")
        self.remove_pj_btn.clicked.connect(self._remove_pj)
        pj_btn_layout.addWidget(self.remove_pj_btn)
        ref_layout.addLayout(pj_btn_layout)
        
        # PNJ/Créatures
        npc_label = QLabel("PNJ / Créatures:")
        ref_layout.addWidget(npc_label)
        self.npc_list = QListWidget()
        self.npc_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        ref_layout.addWidget(self.npc_list)
        
        npc_btn_layout = QHBoxLayout()
        self.add_npc_btn = QPushButton("Ajouter PNJ/Créature")
        self.add_npc_btn.clicked.connect(self._add_npc)
        npc_btn_layout.addWidget(self.add_npc_btn)
        self.remove_npc_btn = QPushButton("Retirer")
        self.remove_npc_btn.clicked.connect(self._remove_npc)
        npc_btn_layout.addWidget(self.remove_npc_btn)
        ref_layout.addLayout(npc_btn_layout)
        
        # Scènes référencées
        scene_label = QLabel("Scènes référencées:")
        ref_layout.addWidget(scene_label)
        self.scene_ref_list = QListWidget()
        self.scene_ref_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        ref_layout.addWidget(self.scene_ref_list)
        
        scene_btn_layout = QHBoxLayout()
        self.add_scene_ref_btn = QPushButton("Ajouter scène")
        self.add_scene_ref_btn.clicked.connect(self._add_scene_ref)
        scene_btn_layout.addWidget(self.add_scene_ref_btn)
        self.remove_scene_ref_btn = QPushButton("Retirer")
        self.remove_scene_ref_btn.clicked.connect(self._remove_scene_ref)
        scene_btn_layout.addWidget(self.remove_scene_ref_btn)
        ref_layout.addLayout(scene_btn_layout)
        
        tabs.addTab(ref_tab, "Références")
        
        # Onglet Événements
        events_tab = QWidget()
        events_layout = QVBoxLayout(events_tab)
        
        events_label = QLabel("Événements:")
        events_layout.addWidget(events_label)
        self.events_list = QListWidget()
        events_layout.addWidget(self.events_list)
        
        events_btn_layout = QHBoxLayout()
        self.add_event_btn = QPushButton("Ajouter événement")
        self.add_event_btn.clicked.connect(self._add_event)
        events_btn_layout.addWidget(self.add_event_btn)
        self.edit_event_btn = QPushButton("Modifier")
        self.edit_event_btn.clicked.connect(self._edit_event)
        events_btn_layout.addWidget(self.edit_event_btn)
        self.remove_event_btn = QPushButton("Supprimer")
        self.remove_event_btn.clicked.connect(self._remove_event)
        events_btn_layout.addWidget(self.remove_event_btn)
        events_layout.addLayout(events_btn_layout)
        
        tabs.addTab(events_tab, "Événements")
        
        # Onglet Notes
        notes_tab = QWidget()
        notes_layout = QVBoxLayout(notes_tab)
        
        notes_label = QLabel("Notes:")
        notes_layout.addWidget(notes_label)
        self.notes_edit = QTextEdit()
        notes_layout.addWidget(self.notes_edit)
        
        tabs.addTab(notes_tab, "Notes")
        
        layout.addWidget(tabs)
        
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
        
        # Charger les listes de référence
        self._load_references()
    
    def _load_references(self):
        """Charge les listes de références disponibles"""
        # PJ
        self.pj_list.clear()
        if self.project_service.character_service:
            from ...models.character import CharacterType
            pjs = self.project_service.character_service.get_characters_by_type(
                CharacterType.PJ
            )
            for pj in pjs:
                item = QListWidgetItem(pj.name if pj.name else "Sans nom")
                item.setData(Qt.ItemDataRole.UserRole, pj.id)
                self.pj_list.addItem(item)
        
        # PNJ/Créatures
        self.npc_list.clear()
        if self.project_service.character_service:
            from ...models.character import CharacterType
            npcs = self.project_service.character_service.get_characters_by_type(
                CharacterType.PNJ
            )
            creatures = self.project_service.character_service.get_characters_by_type(
                CharacterType.CREATURE
            )
            for npc in npcs + creatures:
                name = npc.name if npc.name else "Sans nom"
                char_type = "PNJ" if npc.type == CharacterType.PNJ else "Créature"
                item = QListWidgetItem(f"{name} ({char_type})")
                item.setData(Qt.ItemDataRole.UserRole, npc.id)
                self.npc_list.addItem(item)
        
        # Scènes
        self.scene_ref_list.clear()
        if self.project_service.scene_service:
            scenes = self.project_service.scene_service.get_all_scenes()
            for scene in scenes:
                # Ne pas inclure la scène actuelle si on est en mode édition
                if not self.is_new and scene.id == self.scene.id:
                    continue
                item = QListWidgetItem(scene.title)
                item.setData(Qt.ItemDataRole.UserRole, scene.id)
                self.scene_ref_list.addItem(item)
    
    def _load_scene_data(self):
        """Charge les données de la scène"""
        if not self.scene:
            return
        
        self.title_edit.setText(self.scene.title)
        self.description_edit.setPlainText(self.scene.description)
        self.notes_edit.setPlainText(self.scene.notes)
        
        # Sélectionner les PJ
        for i in range(self.pj_list.count()):
            item = self.pj_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) in self.scene.player_characters:
                item.setSelected(True)
        
        # Sélectionner les PNJ
        for i in range(self.npc_list.count()):
            item = self.npc_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) in self.scene.npcs:
                item.setSelected(True)
        
        # Sélectionner les scènes référencées
        for i in range(self.scene_ref_list.count()):
            item = self.scene_ref_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) in self.scene.referenced_scenes:
                item.setSelected(True)
        
        # Charger les événements
        self.events_list.clear()
        for event in self.scene.events:
            item = QListWidgetItem(event.title)
            item.setData(Qt.ItemDataRole.UserRole, event)
            self.events_list.addItem(item)
    
    def _add_pj(self):
        """Ajoute un PJ (déjà géré par la sélection multiple)"""
        pass
    
    def _remove_pj(self):
        """Retire les PJ sélectionnés"""
        for item in self.pj_list.selectedItems():
            item.setSelected(False)
    
    def _add_npc(self):
        """Ajoute un PNJ (déjà géré par la sélection multiple)"""
        pass
    
    def _remove_npc(self):
        """Retire les PNJ sélectionnés"""
        for item in self.npc_list.selectedItems():
            item.setSelected(False)
    
    def _add_scene_ref(self):
        """Ajoute une scène référencée (déjà géré par la sélection multiple)"""
        pass
    
    def _remove_scene_ref(self):
        """Retire les scènes référencées sélectionnées"""
        for item in self.scene_ref_list.selectedItems():
            item.setSelected(False)
    
    def _add_event(self):
        """Ajoute un événement"""
        from PyQt6.QtWidgets import QInputDialog
        title, ok = QInputDialog.getText(self, "Nouvel événement", "Titre:")
        if ok and title:
            description, ok = QInputDialog.getMultiLineText(
                self, "Description", "Description:", ""
            )
            if ok:
                event = Event(
                    id=generate_id(),
                    title=title,
                    description=description if description else ""
                )
                item = QListWidgetItem(event.title)
                item.setData(Qt.ItemDataRole.UserRole, event)
                self.events_list.addItem(item)
    
    def _edit_event(self):
        """Modifie un événement"""
        current_item = self.events_list.currentItem()
        if not current_item:
            return
        
        event = current_item.data(Qt.ItemDataRole.UserRole)
        from PyQt6.QtWidgets import QInputDialog
        title, ok = QInputDialog.getText(self, "Modifier événement", "Titre:", text=event.title)
        if ok and title:
            description, ok = QInputDialog.getMultiLineText(
                self, "Description", "Description:", event.description
            )
            if ok:
                event.title = title
                event.description = description if description else ""
                current_item.setText(event.title)
    
    def _remove_event(self):
        """Supprime un événement"""
        current_item = self.events_list.currentItem()
        if current_item:
            self.events_list.takeItem(self.events_list.row(current_item))
    
    def _save(self):
        """Sauvegarde la scène"""
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "Erreur", "Le titre est obligatoire")
            return
        
        description = self.description_edit.toPlainText()
        notes = self.notes_edit.toPlainText()
        
        # Récupérer les PJ sélectionnés
        pj_ids = []
        for i in range(self.pj_list.count()):
            item = self.pj_list.item(i)
            if item.isSelected():
                pj_ids.append(item.data(Qt.ItemDataRole.UserRole))
        
        # Récupérer les PNJ sélectionnés
        npc_ids = []
        for i in range(self.npc_list.count()):
            item = self.npc_list.item(i)
            if item.isSelected():
                npc_ids.append(item.data(Qt.ItemDataRole.UserRole))
        
        # Récupérer les scènes référencées
        scene_ref_ids = []
        for i in range(self.scene_ref_list.count()):
            item = self.scene_ref_list.item(i)
            if item.isSelected():
                scene_ref_ids.append(item.data(Qt.ItemDataRole.UserRole))
        
        # Récupérer les événements
        events = []
        for i in range(self.events_list.count()):
            item = self.events_list.item(i)
            event = item.data(Qt.ItemDataRole.UserRole)
            events.append(event)
        
        if self.is_new:
            # Créer une nouvelle scène
            self.scene = self.project_service.scene_service.create_scene(title, description)
            self.scene.notes = notes
            self.scene.player_characters = pj_ids
            self.scene.npcs = npc_ids
            self.scene.referenced_scenes = scene_ref_ids
            self.scene.events = events
            self.scene.updated_at = datetime.now()
        else:
            # Mettre à jour la scène existante
            self.scene.title = title
            self.scene.description = description
            self.scene.notes = notes
            self.scene.player_characters = pj_ids
            self.scene.npcs = npc_ids
            self.scene.referenced_scenes = scene_ref_ids
            self.scene.events = events
            self.scene.updated_at = datetime.now()
            self.project_service.scene_service.update_scene(self.scene)
        
        self.accept()

