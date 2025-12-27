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
from .image_upload_widget import ImageUploadWidget


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
        
        # Image
        from .image_upload_widget import ImageUploadWidget
        image_label = QLabel("Image:")
        layout.addWidget(image_label)
        self.image_widget = ImageUploadWidget(
            project_service=self.project_service,
            entity_type="scene",
            entity_id=self.scene.id if self.scene else "",
            parent=self
        )
        layout.addWidget(self.image_widget)
        
        # Onglets
        tabs = QTabWidget()
        
        # Onglet Timeline
        from .scene_timeline_widget import SceneTimelineWidget
        timeline_tab = QWidget()
        timeline_layout = QVBoxLayout(timeline_tab)
        self.timeline_widget = SceneTimelineWidget(self.project_service, timeline_tab)
        if self.scene:
            self.timeline_widget.set_current_scene(self.scene.id)
        self.timeline_widget.scene_selected.connect(self._on_timeline_scene_selected)
        timeline_layout.addWidget(self.timeline_widget)
        tabs.addTab(timeline_tab, "Timeline")
        
        # Onglet Références
        ref_tab = QWidget()
        ref_layout = QVBoxLayout(ref_tab)
        ref_layout.setSpacing(10)
        
        # Utiliser les nouveaux widgets de sélection
        from .reference_selector_widget import CompactReferenceSelector
        
        # PJ
        pj_items = []
        if self.project_service.character_service:
            from ...models.character import CharacterType
            pjs = self.project_service.character_service.get_characters_by_type(CharacterType.PJ)
            pj_items = [(pj.id, pj.name if pj.name else "Sans nom") for pj in pjs]
        
        self.pj_selector = CompactReferenceSelector("Personnages Joueurs (PJ)", pj_items, ref_tab)
        self.pj_selector.selection_changed.connect(self._on_pj_selection_changed)
        ref_layout.addWidget(self.pj_selector)
        
        # PNJ/Créatures
        npc_items = []
        if self.project_service.character_service:
            from ...models.character import CharacterType
            npcs = self.project_service.character_service.get_characters_by_type(CharacterType.PNJ)
            creatures = self.project_service.character_service.get_characters_by_type(CharacterType.CREATURE)
            for npc in npcs:
                npc_items.append((npc.id, f"{npc.name if npc.name else 'Sans nom'} (PNJ)"))
            for creature in creatures:
                npc_items.append((creature.id, f"{creature.name if creature.name else 'Sans nom'} (Créature)"))
        
        self.npc_selector = CompactReferenceSelector("PNJ / Créatures", npc_items, ref_tab)
        self.npc_selector.selection_changed.connect(self._on_npc_selection_changed)
        ref_layout.addWidget(self.npc_selector)
        
        # Lieux
        location_items = []
        if self.project_service.bank_service:
            from ...models.bank import BankType
            locations_bank = self.project_service.bank_service.get_bank_by_type(BankType.LOCATIONS)
            if locations_bank:
                location_items = [(entry.id, entry.value) for entry in locations_bank.entries]
        
        location_selector_layout = QVBoxLayout()
        location_selector_layout.setSpacing(5)
        
        self.location_selector = CompactReferenceSelector("Lieux", location_items, ref_tab)
        self.location_selector.selection_changed.connect(self._on_location_selection_changed)
        location_selector_layout.addWidget(self.location_selector)
        
        # Bouton pour créer un nouveau lieu
        self.create_location_btn = QPushButton("Créer un nouveau lieu")
        self.create_location_btn.clicked.connect(self._create_location)
        location_selector_layout.addWidget(self.create_location_btn)
        
        ref_layout.addLayout(location_selector_layout)
        
        # Scènes référencées
        scene_items = []
        if self.project_service.scene_service:
            scenes = self.project_service.scene_service.get_all_scenes()
            # Ne pas inclure la scène actuelle si on est en mode édition
            for scene in scenes:
                if self.is_new or scene.id != (self.scene.id if self.scene else ""):
                    scene_items.append((scene.id, scene.title))
        
        self.scene_ref_selector = CompactReferenceSelector("Scènes référencées", scene_items, ref_tab)
        self.scene_ref_selector.selection_changed.connect(self._on_scene_ref_selection_changed)
        ref_layout.addWidget(self.scene_ref_selector)
        
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
        pj_items = []
        if self.project_service.character_service:
            from ...models.character import CharacterType
            pjs = self.project_service.character_service.get_characters_by_type(CharacterType.PJ)
            pj_items = [(pj.id, pj.name if pj.name else "Sans nom") for pj in pjs]
        if hasattr(self, 'pj_selector'):
            self.pj_selector.update_items(pj_items)
        
        # PNJ/Créatures
        npc_items = []
        if self.project_service.character_service:
            from ...models.character import CharacterType
            npcs = self.project_service.character_service.get_characters_by_type(CharacterType.PNJ)
            creatures = self.project_service.character_service.get_characters_by_type(CharacterType.CREATURE)
            for npc in npcs:
                npc_items.append((npc.id, f"{npc.name if npc.name else 'Sans nom'} (PNJ)"))
            for creature in creatures:
                npc_items.append((creature.id, f"{creature.name if creature.name else 'Sans nom'} (Créature)"))
        if hasattr(self, 'npc_selector'):
            self.npc_selector.update_items(npc_items)
        
        # Lieux (depuis la banque de données)
        location_items = []
        if self.project_service.bank_service:
            from ...models.bank import BankType
            locations_bank = self.project_service.bank_service.get_bank_by_type(BankType.LOCATIONS)
            if locations_bank:
                location_items = [(entry.id, entry.value) for entry in locations_bank.entries]
        if hasattr(self, 'location_selector'):
            self.location_selector.update_items(location_items)
        
        # Scènes
        scene_items = []
        if self.project_service.scene_service:
            scenes = self.project_service.scene_service.get_all_scenes()
            for scene in scenes:
                # Ne pas inclure la scène actuelle si on est en mode édition
                if self.is_new or scene.id != (self.scene.id if self.scene else ""):
                    scene_items.append((scene.id, scene.title))
        if hasattr(self, 'scene_ref_selector'):
            self.scene_ref_selector.update_items(scene_items)
    
    def _load_scene_data(self):
        """Charge les données de la scène"""
        if not self.scene:
            return
        
        self.title_edit.setText(self.scene.title)
        self.description_edit.setPlainText(self.scene.description)
        self.notes_edit.setPlainText(self.scene.notes)
        
        # Image
        if self.scene.image_id:
            self.image_widget.set_image_id(self.scene.image_id)
            # Mettre à jour l'entity_id si nécessaire
            if not self.image_widget.entity_id:
                self.image_widget.entity_id = self.scene.id
        
        # Sélectionner les PJ
        if hasattr(self, 'pj_selector'):
            self.pj_selector.set_selected_ids(self.scene.player_characters)
        
        # Sélectionner les PNJ
        if hasattr(self, 'npc_selector'):
            self.npc_selector.set_selected_ids(self.scene.npcs)
        
        # Sélectionner les lieux
        if hasattr(self, 'location_selector'):
            self.location_selector.set_selected_ids(self.scene.locations)
        
        # Sélectionner les scènes référencées
        if hasattr(self, 'scene_ref_selector'):
            self.scene_ref_selector.set_selected_ids(self.scene.referenced_scenes)
        
        # Charger les événements
        self.events_list.clear()
        for event in self.scene.events:
            item = QListWidgetItem(event.title)
            item.setData(Qt.ItemDataRole.UserRole, event)
            self.events_list.addItem(item)
    
    def _on_pj_selection_changed(self, selected_ids: List[str]):
        """Gère le changement de sélection des PJ"""
        pass  # La sélection est gérée automatiquement par le widget
    
    def _on_npc_selection_changed(self, selected_ids: List[str]):
        """Gère le changement de sélection des PNJ"""
        pass  # La sélection est gérée automatiquement par le widget
    
    def _on_location_selection_changed(self, selected_ids: List[str]):
        """Gère le changement de sélection des lieux"""
        pass  # La sélection est gérée automatiquement par le widget
    
    def _on_scene_ref_selection_changed(self, selected_ids: List[str]):
        """Gère le changement de sélection des scènes référencées"""
        pass  # La sélection est gérée automatiquement par le widget
    
    def _create_location(self):
        """Ouvre l'éditeur de banque pour créer un nouveau lieu"""
        from ...models.bank import BankType
        from .bank_entry_editor import BankEntryEditor
        
        # Ouvrir l'éditeur de banque pour créer un lieu
        editor = BankEntryEditor(
            BankType.LOCATIONS,
            entry=None,
            parent=self,
            project_service=self.project_service
        )
        if editor.exec() == QDialog.DialogCode.Accepted:
            try:
                value, metadata = editor.get_entry_data()
                
                # Ajouter le lieu à la banque
                bank = self.project_service.bank_service.get_or_create_bank(BankType.LOCATIONS)
                existing_values = [e.value for e in bank.entries]
                if value in existing_values:
                    QMessageBox.warning(self, "Attention", f"Le lieu '{value}' existe déjà dans la banque.")
                    return
                
                new_entry = self.project_service.bank_service.add_entry_to_bank(bank.id, value, metadata)
                self.project_service.save_project(f"Ajout du lieu '{value}'")
                
                # Recharger la liste des lieux
                self._load_references()
                
                # Sélectionner le nouveau lieu
                if hasattr(self, 'location_selector'):
                    self.location_selector.set_selected_ids([new_entry.id])
            except ValueError as e:
                QMessageBox.warning(self, "Erreur", str(e))
    
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
    
    def _on_timeline_scene_selected(self, scene_id: str):
        """Gère la sélection d'une scène depuis la timeline"""
        # Optionnel : ouvrir l'éditeur de la scène sélectionnée
        # Pour l'instant, on ne fait rien, mais on pourrait ouvrir un nouvel éditeur
        pass
    
    def showEvent(self, event):
        """Rafraîchit la timeline lors de l'affichage"""
        super().showEvent(event)
        if hasattr(self, 'timeline_widget'):
            self.timeline_widget.refresh()
    
    def _save(self):
        """Sauvegarde la scène"""
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "Erreur", "Le titre est obligatoire")
            return
        
        description = self.description_edit.toPlainText()
        notes = self.notes_edit.toPlainText()
        
        # Récupérer les PJ sélectionnés
        pj_ids = self.pj_selector.get_selected_ids() if hasattr(self, 'pj_selector') else []
        
        # Récupérer les PNJ sélectionnés
        npc_ids = self.npc_selector.get_selected_ids() if hasattr(self, 'npc_selector') else []
        
        # Récupérer les lieux sélectionnés
        location_ids = self.location_selector.get_selected_ids() if hasattr(self, 'location_selector') else []
        
        # Récupérer les scènes référencées
        scene_ref_ids = self.scene_ref_selector.get_selected_ids() if hasattr(self, 'scene_ref_selector') else []
        
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
            self.scene.locations = location_ids
            self.scene.referenced_scenes = scene_ref_ids
            self.scene.events = events
            self.scene.image_id = self.image_widget.get_image_id()
            self.scene.updated_at = datetime.now()
        else:
            # Mettre à jour la scène existante
            self.scene.title = title
            self.scene.description = description
            self.scene.notes = notes
            self.scene.player_characters = pj_ids
            self.scene.npcs = npc_ids
            self.scene.locations = location_ids
            self.scene.image_id = self.image_widget.get_image_id()
            self.scene.referenced_scenes = scene_ref_ids
            self.scene.events = events
            self.scene.updated_at = datetime.now()
            self.project_service.scene_service.update_scene(self.scene)
        
        self.accept()

