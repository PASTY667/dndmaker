"""
Widget amélioré pour la sélection de références (PJ, PNJ, Lieux, etc.)
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QComboBox, QCheckBox,
    QGroupBox, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import List, Optional

from ...core.i18n import tr


class ReferenceSelectorWidget(QWidget):
    """Widget amélioré pour sélectionner des références avec une interface plus claire"""
    
    selection_changed = pyqtSignal(list)  # Émet la liste des IDs sélectionnés
    
    def __init__(self, title: str, items: List[tuple], parent=None):
        """
        Crée un widget de sélection de références
        
        Args:
            title: Titre du widget
            items: Liste de tuples (id, label) pour les éléments disponibles
        """
        super().__init__(parent)
        self.title = title
        self.all_items = items
        self.selected_ids = set()
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Groupe
        group = QGroupBox(self.title)
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(5)
        
        # Zone de sélection avec checkboxes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(150)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.checkbox_container = QWidget()
        self.checkbox_layout = QVBoxLayout(self.checkbox_container)
        self.checkbox_layout.setContentsMargins(5, 5, 5, 5)
        self.checkbox_layout.setSpacing(2)
        
        scroll.setWidget(self.checkbox_container)
        group_layout.addWidget(scroll)
        
        # Boutons d'action rapide
        button_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("Tout sélectionner")
        self.select_all_btn.clicked.connect(self._select_all)
        button_layout.addWidget(self.select_all_btn)
        
        self.deselect_all_btn = QPushButton("Tout désélectionner")
        self.deselect_all_btn.clicked.connect(self._deselect_all)
        button_layout.addWidget(self.deselect_all_btn)
        
        button_layout.addStretch()
        group_layout.addLayout(button_layout)
        
        layout.addWidget(group)
        
        # Créer les checkboxes
        self._create_checkboxes()
    
    def _create_checkboxes(self):
        """Crée les checkboxes pour tous les éléments"""
        # Nettoyer le layout
        while self.checkbox_layout.count():
            child = self.checkbox_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Créer une checkbox pour chaque élément
        self.checkboxes = {}
        for item_id, label in self.all_items:
            checkbox = QCheckBox(label)
            checkbox.setChecked(item_id in self.selected_ids)
            checkbox.stateChanged.connect(
                lambda state, id=item_id: self._on_checkbox_changed(id, state)
            )
            self.checkboxes[item_id] = checkbox
            self.checkbox_layout.addWidget(checkbox)
        
        self.checkbox_layout.addStretch()
    
    def _on_checkbox_changed(self, item_id: str, state: int):
        """Gère le changement d'état d'une checkbox"""
        if state == Qt.CheckState.Checked.value:
            self.selected_ids.add(item_id)
        else:
            self.selected_ids.discard(item_id)
        self.selection_changed.emit(list(self.selected_ids))
    
    def _select_all(self):
        """Sélectionne tous les éléments"""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(True)
    
    def _deselect_all(self):
        """Désélectionne tous les éléments"""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)
    
    def set_selected_ids(self, ids: List[str]):
        """Définit les IDs sélectionnés"""
        self.selected_ids = set(ids)
        for item_id, checkbox in self.checkboxes.items():
            checkbox.setChecked(item_id in self.selected_ids)
    
    def get_selected_ids(self) -> List[str]:
        """Retourne la liste des IDs sélectionnés"""
        return list(self.selected_ids)
    
    def update_items(self, items: List[tuple]):
        """Met à jour la liste des éléments disponibles"""
        self.all_items = items
        self._create_checkboxes()
        # Conserver les sélections existantes si possible
        current_selected = self.selected_ids.copy()
        self.selected_ids.clear()
        for item_id in current_selected:
            if item_id in [id for id, _ in items]:
                self.selected_ids.add(item_id)
        self.set_selected_ids(list(self.selected_ids))


class CompactReferenceSelector(QWidget):
    """Widget compact avec menu déroulant pour les références"""
    
    selection_changed = pyqtSignal(list)
    
    def __init__(self, title: str, items: List[tuple], parent=None):
        super().__init__(parent)
        self.title = title
        self.all_items = items
        self.selected_ids = set()
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface avec menu déroulant"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # En-tête avec bouton pour ouvrir/fermer
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(self.title_label)
        
        self.toggle_btn = QPushButton("▼")
        self.toggle_btn.setMaximumWidth(30)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(True)
        self.toggle_btn.clicked.connect(self._toggle_expanded)
        header_layout.addWidget(self.toggle_btn)
        
        header_layout.addStretch()
        
        # Compteur de sélection
        self.count_label = QLabel("(0 sélectionné)")
        header_layout.addWidget(self.count_label)
        
        layout.addLayout(header_layout)
        
        # Zone de sélection (expandable)
        self.selection_frame = QFrame()
        self.selection_frame.setFrameShape(QFrame.Shape.Box)
        self.selection_layout = QVBoxLayout(self.selection_frame)
        self.selection_layout.setContentsMargins(5, 5, 5, 5)
        self.selection_layout.setSpacing(5)
        
        # Zone scrollable avec checkboxes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(120)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.checkbox_container = QWidget()
        self.checkbox_layout = QVBoxLayout(self.checkbox_container)
        self.checkbox_layout.setContentsMargins(5, 5, 5, 5)
        self.checkbox_layout.setSpacing(2)
        
        scroll.setWidget(self.checkbox_container)
        self.selection_layout.addWidget(scroll)
        
        # Boutons d'action
        button_layout = QHBoxLayout()
        select_all_btn = QPushButton("Tout")
        select_all_btn.clicked.connect(self._select_all)
        button_layout.addWidget(select_all_btn)
        
        deselect_all_btn = QPushButton("Rien")
        deselect_all_btn.clicked.connect(self._deselect_all)
        button_layout.addWidget(deselect_all_btn)
        
        button_layout.addStretch()
        self.selection_layout.addLayout(button_layout)
        
        layout.addWidget(self.selection_frame)
        
        # Créer les checkboxes
        self._create_checkboxes()
    
    def _toggle_expanded(self, checked: bool):
        """Ouvre ou ferme la zone de sélection"""
        self.selection_frame.setVisible(checked)
        self.toggle_btn.setText("▼" if checked else "▶")
    
    def _create_checkboxes(self):
        """Crée les checkboxes"""
        while self.checkbox_layout.count():
            child = self.checkbox_layout.takeAt(0)
            if child.widget() and isinstance(child.widget(), QCheckBox):
                child.widget().deleteLater()
        
        self.checkboxes = {}
        for item_id, label in self.all_items:
            checkbox = QCheckBox(label)
            checkbox.setChecked(item_id in self.selected_ids)
            checkbox.stateChanged.connect(
                lambda state, id=item_id: self._on_checkbox_changed(id, state)
            )
            self.checkboxes[item_id] = checkbox
            self.checkbox_layout.addWidget(checkbox)
        
        self.checkbox_layout.addStretch()
        self._update_count()
    
    def _on_checkbox_changed(self, item_id: str, state: int):
        """Gère le changement d'état"""
        if state == Qt.CheckState.Checked.value:
            self.selected_ids.add(item_id)
        else:
            self.selected_ids.discard(item_id)
        self._update_count()
        self.selection_changed.emit(list(self.selected_ids))
    
    def _update_count(self):
        """Met à jour le compteur de sélection"""
        count = len(self.selected_ids)
        self.count_label.setText(f"({count} sélectionné{'s' if count > 1 else ''})")
    
    def _select_all(self):
        """Sélectionne tout"""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(True)
    
    def _deselect_all(self):
        """Désélectionne tout"""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)
    
    def set_selected_ids(self, ids: List[str]):
        """Définit les IDs sélectionnés"""
        self.selected_ids = set(ids)
        for item_id, checkbox in self.checkboxes.items():
            checkbox.setChecked(item_id in self.selected_ids)
        self._update_count()
    
    def get_selected_ids(self) -> List[str]:
        """Retourne les IDs sélectionnés"""
        return list(self.selected_ids)
    
    def update_items(self, items: List[tuple]):
        """Met à jour les éléments"""
        self.all_items = items
        current_selected = self.selected_ids.copy()
        self.selected_ids.clear()
        for item_id in current_selected:
            if item_id in [id for id, _ in items]:
                self.selected_ids.add(item_id)
        self._create_checkboxes()
        self.set_selected_ids(list(self.selected_ids))

