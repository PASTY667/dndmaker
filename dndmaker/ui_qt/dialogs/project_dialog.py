"""
Dialogue personnalisé pour ouvrir un projet
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton, QFileDialog,
    QMessageBox, QLineEdit, QComboBox
)
from PyQt6.QtCore import Qt
from pathlib import Path
from typing import Optional, List

from ...core.config import Config


class ProjectOpenDialog(QDialog):
    """Dialogue personnalisé pour ouvrir un projet"""
    
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.selected_project_path: Optional[Path] = None
        self._init_ui()
        self._load_recent_projects()
    
    def _init_ui(self):
        """Initialise l'interface"""
        self.setWindowTitle("Ouvrir un projet")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Titre
        title = QLabel("Sélectionner un projet à ouvrir")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)
        
        # Répertoire de recherche
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Répertoire:"))
        
        self.dir_edit = QLineEdit()
        self.dir_edit.setReadOnly(True)
        dir_layout.addWidget(self.dir_edit, stretch=1)
        
        browse_btn = QPushButton("Parcourir...")
        browse_btn.clicked.connect(self._browse_directory)
        dir_layout.addWidget(browse_btn)
        
        layout.addLayout(dir_layout)
        
        # Liste des projets trouvés
        projects_label = QLabel("Projets trouvés:")
        layout.addWidget(projects_label)
        
        self.projects_list = QListWidget()
        self.projects_list.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.projects_list)
        
        # Informations du projet sélectionné
        self.info_label = QLabel("Sélectionnez un projet pour voir ses informations")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: #888888; padding: 10px;")
        layout.addWidget(self.info_label)
        
        # Boutons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.open_btn = QPushButton("Ouvrir")
        self.open_btn.setEnabled(False)
        self.open_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.open_btn)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Connexions
        self.projects_list.itemSelectionChanged.connect(self._on_selection_changed)
        
        # Initialiser avec le répertoire du dernier projet ou Documents
        self._init_start_directory()
    
    def _init_start_directory(self):
        """Initialise le répertoire de départ"""
        last_project = self.config.get_last_project()
        if last_project and last_project.parent.exists():
            start_dir = last_project.parent
        else:
            try:
                start_dir = Path.home() / "Documents" / "DNDMaker"
                if not start_dir.exists():
                    start_dir = Path.home() / "Documents"
            except (OSError, TypeError, AttributeError):
                start_dir = Path.cwd()
        
        self.current_dir = start_dir
        self.dir_edit.setText(str(start_dir))
        self._scan_directory(start_dir)
    
    def _browse_directory(self):
        """Ouvre un dialogue pour choisir un répertoire"""
        start_dir = self.current_dir if hasattr(self, 'current_dir') else Path.home() / "Documents"
        
        directory = QFileDialog.getExistingDirectory(
            self,
            "Sélectionner un répertoire contenant des projets",
            str(start_dir),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if directory:
            self.current_dir = Path(directory)
            self.dir_edit.setText(directory)
            self._scan_directory(self.current_dir)
    
    def _scan_directory(self, directory: Path):
        """Scanne un répertoire pour trouver les projets .dndmaker"""
        self.projects_list.clear()
        self.info_label.setText("Recherche de projets...")
        
        if not directory.exists() or not directory.is_dir():
            self.info_label.setText(f"Le répertoire n'existe pas ou n'est pas un répertoire: {directory}")
            return
        
        # Chercher les répertoires .dndmaker
        projects = []
        try:
            for item in directory.iterdir():
                if item.is_dir() and item.name.endswith('.dndmaker'):
                    project_file = item / "project.json"
                    if project_file.exists():
                        projects.append(item)
        except (PermissionError, OSError) as e:
            self.info_label.setText(f"Erreur lors de la lecture du répertoire: {e}")
            return
        
        # Trier par nom
        projects.sort(key=lambda p: p.name)
        
        # Afficher les projets
        for project_path in projects:
            # Essayer de charger le nom du projet
            try:
                import json
                with open(project_path / "project.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    project_name = data.get('name', project_path.stem)
            except:
                project_name = project_path.stem
            
            item = QListWidgetItem(f"{project_name} ({project_path.name})")
            item.setData(Qt.ItemDataRole.UserRole, str(project_path))
            self.projects_list.addItem(item)
        
        if not projects:
            self.info_label.setText(
                f"Aucun projet .dndmaker trouvé dans:\n{directory}\n\n"
                f"Naviguez vers un autre répertoire ou créez un nouveau projet."
            )
        else:
            self.info_label.setText(f"{len(projects)} projet(s) trouvé(s)")
    
    def _on_selection_changed(self):
        """Gère le changement de sélection"""
        current_item = self.projects_list.currentItem()
        self.open_btn.setEnabled(current_item is not None)
        
        if current_item:
            project_path_str = current_item.data(Qt.ItemDataRole.UserRole)
            project_path = Path(project_path_str)
            
            # Charger les informations du projet
            try:
                import json
                with open(project_path / "project.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    name = data.get('name', 'Sans nom')
                    version = data.get('version', 1)
                    updated = data.get('updated_at', 'Inconnu')
                    
                    self.info_label.setText(
                        f"<b>Nom:</b> {name}<br>"
                        f"<b>Version:</b> {version}<br>"
                        f"<b>Dernière modification:</b> {updated}<br>"
                        f"<b>Chemin:</b> {project_path}"
                    )
                    self.info_label.setStyleSheet("color: #ffffff; padding: 10px;")
            except Exception as e:
                self.info_label.setText(f"Erreur lors du chargement des informations: {e}")
    
    def _load_recent_projects(self):
        """Charge les projets récents (à implémenter si nécessaire)"""
        pass
    
    def get_selected_project_path(self) -> Optional[Path]:
        """Récupère le chemin du projet sélectionné"""
        return self.selected_project_path
    
    def accept(self):
        """Valide la sélection"""
        current_item = self.projects_list.currentItem()
        if current_item:
            project_path_str = current_item.data(Qt.ItemDataRole.UserRole)
            self.selected_project_path = Path(project_path_str)
            super().accept()
        else:
            QMessageBox.warning(self, "Aucune sélection", "Veuillez sélectionner un projet")

