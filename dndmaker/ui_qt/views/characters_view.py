"""
Vue des personnages (PJ/PNJ/Créatures)
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QMessageBox,
    QTabWidget
)
from PyQt6.QtCore import Qt

from ...services.project_service import ProjectService
from ...core.logger import get_logger
from ...core.i18n import tr

logger = get_logger()
from ...models.character import CharacterType
from ...models.bank import BankType


class CharactersView(QWidget):
    """Vue des personnages"""
    
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
        self.title_label = QLabel(tr("character.title"))
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.title_label)
        
        # Onglets pour PJ / PNJ / Créatures
        self.tabs = QTabWidget()
        self._update_tabs()
        layout.addWidget(self.tabs)
    
    def _update_tabs(self):
        """Met à jour les onglets avec les traductions"""
        self.tabs.clear()
        self.tabs.addTab(self._create_character_tab(CharacterType.PJ), tr("nav.characters"))
        self.tabs.addTab(self._create_character_tab(CharacterType.PNJ), tr("nav.npcs").split(" / ")[0])
        self.tabs.addTab(self._create_character_tab(CharacterType.CREATURE), tr("nav.npcs").split(" / ")[1] if " / " in tr("nav.npcs") else "Créatures")
    
    def _create_character_tab(self, char_type: CharacterType) -> QWidget:
        """Crée un onglet pour un type de personnage"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        
        # Boutons
        button_layout = QHBoxLayout()
        
        new_btn = QPushButton(tr("character.create"))
        new_btn.clicked.connect(lambda: self._new_character(char_type))
        button_layout.addWidget(new_btn)
        
        # Bouton "Générer" pour PNJ et Créatures
        if char_type in [CharacterType.PNJ, CharacterType.CREATURE]:
            generate_btn = QPushButton(tr("character.generate"))
            generate_btn.clicked.connect(lambda: self._generate_character(char_type))
            button_layout.addWidget(generate_btn)
        
        edit_btn = QPushButton(tr("character.edit"))
        edit_btn.clicked.connect(lambda: self._edit_character(char_type))
        edit_btn.setEnabled(False)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton(tr("character.delete"))
        delete_btn.clicked.connect(lambda: self._delete_character(char_type))
        delete_btn.setEnabled(False)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Liste des personnages
        char_list = QListWidget()
        char_list.itemSelectionChanged.connect(
            lambda: self._on_selection_changed(char_type, edit_btn, delete_btn)
        )
        char_list.itemDoubleClicked.connect(lambda: self._edit_character(char_type))
        layout.addWidget(char_list)
        
        # Stocker la référence - utiliser setProperty pour Qt
        widget.setProperty('char_list', char_list)
        widget.setProperty('char_type', char_type)
        widget.setProperty('edit_btn', edit_btn)
        widget.setProperty('delete_btn', delete_btn)
        
        # Aussi avec setattr pour compatibilité
        setattr(widget, 'char_list', char_list)
        setattr(widget, 'char_type', char_type)
        setattr(widget, 'edit_btn', edit_btn)
        setattr(widget, 'delete_btn', delete_btn)
        
        return widget
    
    def on_language_changed(self):
        """Met à jour les textes lors du changement de langue"""
        self.title_label.setText(tr("character.title"))
        self._update_tabs()
        self.refresh()
    
    def refresh(self):
        """Rafraîchit la vue"""
        if not self.project_service.character_service:
            return
        
        # Debug: afficher tous les personnages
        all_chars = self.project_service.character_service.get_all_characters()
        print(f"DEBUG: Total personnages: {len(all_chars)}")
        for char in all_chars:
            print(f"  - {char.name} (type: {char.type}, value: {char.type.value if hasattr(char.type, 'value') else char.type})")
        
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            # Essayer getattr d'abord, puis property
            char_list = getattr(widget, 'char_list', None) or widget.property('char_list')
            char_type = getattr(widget, 'char_type', None) or widget.property('char_type')
            
            # Vérification explicite (les objets Qt peuvent être évalués comme False même s'ils existent)
            if char_list is not None and char_type is not None:
                char_list.clear()
                characters = self.project_service.character_service.get_characters_by_type(char_type)
                for char in characters:
                    item = QListWidgetItem(char.name)
                    item.setData(Qt.ItemDataRole.UserRole, char.id)
                    char_list.addItem(item)
    
    def _on_selection_changed(self, char_type: CharacterType, edit_btn, delete_btn):
        """Gère le changement de sélection"""
        widget = self.tabs.currentWidget()
        char_list = getattr(widget, 'char_list', None)
        if char_list:
            has_selection = len(char_list.selectedItems()) > 0
            edit_btn.setEnabled(has_selection)
            delete_btn.setEnabled(has_selection)
    
    def _new_character(self, char_type: CharacterType):
        """Crée un nouveau personnage"""
        from ..widgets.character_editor import CharacterEditor
        
        # Ouvrir l'éditeur avec None pour créer un nouveau personnage
        editor = CharacterEditor(self.project_service, None, self)
        # Définir le type par défaut
        editor.type_combo.setCurrentText(char_type.value)
        if editor.exec():
            self.refresh()
    
    def _edit_character(self, char_type: CharacterType):
        """Modifie un personnage"""
        widget = self.tabs.currentWidget()
        char_list = getattr(widget, 'char_list', None)
        if not char_list:
            return
        
        current_item = char_list.currentItem()
        if not current_item:
            return
        
        char_id = current_item.data(Qt.ItemDataRole.UserRole)
        character = self.project_service.character_service.get_character(char_id)
        
        if character:
            from ..widgets.character_editor import CharacterEditor
            editor = CharacterEditor(self.project_service, character, self)
            if editor.exec():
                self.refresh()
    
    def _delete_character(self, char_type: CharacterType):
        """Supprime un personnage"""
        widget = self.tabs.currentWidget()
        char_list = getattr(widget, 'char_list', None)
        if not char_list:
            return
        
        current_item = char_list.currentItem()
        if not current_item:
            return
        
        char_id = current_item.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir supprimer ce personnage ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.project_service.character_service.delete_character(char_id):
                self.project_service.save_project("Suppression de personnage")
                self.refresh()
            else:
                QMessageBox.warning(self, "Erreur", "Impossible de supprimer le personnage")
    
    def _generate_character(self, char_type: CharacterType):
        """Génère un personnage (PNJ ou Créature)"""
        from PyQt6.QtWidgets import (
            QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QComboBox, 
            QPushButton, QLineEdit, QListWidget, QListWidgetItem
        )
        from PyQt6.QtCore import Qt
        
        logger.log_ui_action("Génération de personnage demandée", character_type=char_type.value)
        
        # Dialogue de génération
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Générer un {char_type.value}")
        dialog.setMinimumWidth(400)
        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)
        
        # Interface différente pour les créatures
        if char_type == CharacterType.CREATURE:
            # Barre de recherche pour les créatures
            search_label = QLabel("Rechercher une créature:")
            layout.addWidget(search_label)
            
            creature_search = QLineEdit()
            creature_search.setPlaceholderText("Tapez pour rechercher...")
            layout.addWidget(creature_search)
            
            # Liste de suggestions
            suggestions_list = QListWidget()
            suggestions_list.setMaximumHeight(150)
            suggestions_list.hide()
            layout.addWidget(suggestions_list)
            
            # Affichage de la créature sélectionnée
            selected_info = QLabel("Aucune créature sélectionnée")
            selected_info.setStyleSheet("font-weight: bold; padding: 10px; background-color: #2b2b2b; border-radius: 5px;")
            layout.addWidget(selected_info)
            
            # Charger toutes les créatures depuis le JSON directement
            from ...core.data_loader import DataLoader
            creatures_data = DataLoader.load_creatures()
            all_creatures = []
            
            # Charger depuis le JSON
            for creature in creatures_data:
                creature_name = creature.get('name', '').strip()
                if creature_name:  # Ne garder que les créatures avec un nom
                    all_creatures.append({
                        'name': creature_name,
                        'metadata': {
                            'level': creature.get('level', 1),
                            'type': creature.get('type', ''),
                            'size': creature.get('size', ''),
                            'ac': creature.get('ac', 10),
                            'hp': creature.get('hp', 1),
                            'initiative': creature.get('initiative', 10),
                            'stats': creature.get('stats', {}),
                            'archetype': creature.get('archetype', 'standard'),
                            'challenge': creature.get('challenge', '0')
                        }
                    })
            
            # Si aucune créature n'a été chargée depuis le JSON, essayer depuis la banque
            if not all_creatures:
                # S'assurer que la banque est initialisée
                DataLoader.initialize_banks(self.project_service.bank_service)
                creatures_bank = self.project_service.bank_service.get_bank_by_type(BankType.CREATURES)
                if creatures_bank:
                    for entry in creatures_bank.entries:
                        if entry.value and entry.value.strip():
                            all_creatures.append({
                                'name': entry.value,
                                'metadata': entry.metadata
                            })
            
            selected_creature = None
            
            def on_search_changed(text: str):
                """Gère le changement dans la barre de recherche"""
                if not text.strip():
                    suggestions_list.hide()
                    return
                
                # Filtrer les créatures
                search_text = text.lower()
                matches = [
                    c for c in all_creatures
                    if search_text in c['name'].lower() and c['name']  # Filtrer les noms vides
                ]
                
                # Limiter à 10 résultats
                matches = matches[:10]
                
                # Afficher les suggestions
                suggestions_list.clear()
                if matches:
                    for match in matches:
                        creature_name = match['name']
                        creature_level = match['metadata'].get('level', 1)
                        item_text = f"{creature_name} (Niveau {creature_level})"
                        item = QListWidgetItem(item_text)
                        item.setData(Qt.ItemDataRole.UserRole, match)
                        suggestions_list.addItem(item)
                    suggestions_list.show()
                else:
                    suggestions_list.hide()
            
            def on_suggestion_clicked(item: QListWidgetItem):
                """Gère le clic sur une suggestion"""
                nonlocal selected_creature
                selected_creature = item.data(Qt.ItemDataRole.UserRole)
                if selected_creature:
                    creature_name = selected_creature['name']
                    creature_level = selected_creature['metadata'].get('level', 1)
                    selected_info.setText(f"Créature sélectionnée: {creature_name}\nNiveau: {creature_level}")
                    level_spin.setValue(creature_level)
                    level_spin.setEnabled(True)
                    creature_search.clear()
                    suggestions_list.hide()
            
            creature_search.textChanged.connect(on_search_changed)
            # Permettre la sélection avec un simple clic ou un double-clic
            suggestions_list.itemClicked.connect(on_suggestion_clicked)
            suggestions_list.itemDoubleClicked.connect(on_suggestion_clicked)
            
            # Niveau (peut être modifié si une créature est sélectionnée)
            level_layout = QHBoxLayout()
            level_layout.addWidget(QLabel("Niveau:"))
            level_spin = QSpinBox()
            level_spin.setMinimum(1)
            level_spin.setMaximum(20)
            level_spin.setValue(1)
            level_spin.setEnabled(False)  # Désactivé par défaut
            level_layout.addWidget(level_spin)
            layout.addLayout(level_layout)
            
            # Méthode de stats (pour créatures)
            stats_layout = QHBoxLayout()
            stats_layout.addWidget(QLabel("Méthode de stats:"))
            stats_method_combo = QComboBox()
            stats_method_combo.addItems(["standard", "heroic"])
            stats_layout.addWidget(stats_method_combo)
            layout.addLayout(stats_layout)
            
        else:
            # Interface pour PNJ (inchangée)
            # Niveau
            level_layout = QHBoxLayout()
            level_layout.addWidget(QLabel("Niveau:"))
            level_spin = QSpinBox()
            level_spin.setMinimum(1)
            level_spin.setMaximum(20)
            level_spin.setValue(1)
            level_layout.addWidget(level_spin)
            layout.addLayout(level_layout)
            
            # Méthode de stats (pour PNJ)
            stats_layout = QHBoxLayout()
            stats_layout.addWidget(QLabel("Méthode de stats:"))
            stats_method_combo = QComboBox()
            stats_method_combo.addItems(["standard", "heroic"])
            stats_layout.addWidget(stats_method_combo)
            layout.addLayout(stats_layout)
            
            # Sélection de métier (pour PNJ uniquement)
            profession_combo = None
            from ...core.data_loader import DataLoader
            professions = DataLoader.load_professions()
            
            profession_layout = QHBoxLayout()
            profession_layout.addWidget(QLabel("Métier (optionnel):"))
            profession_combo = QComboBox()
            profession_combo.addItem("")  # Option vide
            for profession in professions:
                name = profession.get('name', '')
                if name:
                    profession_combo.addItem(name)
            profession_layout.addWidget(profession_combo)
            layout.addLayout(profession_layout)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        generate_btn = QPushButton("Générer")
        cancel_btn = QPushButton("Annuler")
        
        btn_layout.addWidget(generate_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        generate_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        if dialog.exec() != QDialog.DialogCode.Accepted:
            logger.log_ui_action("Génération de personnage annulée")
            return
        
        level = level_spin.value()
        stats_method = stats_method_combo.currentText() if stats_method_combo else "standard"
        
        try:
            if char_type == CharacterType.PNJ:
                from ...generators.npc_generator import NPCGenerator
                generator = NPCGenerator(self.project_service.bank_service)
                character = generator.generate_npc(
                    level=level,
                    stats_method=stats_method
                )
                # Ajouter le métier si sélectionné
                profession = profession_combo.currentText().strip() if profession_combo else None
                if profession:
                    character.profile.profession = profession
            elif char_type == CharacterType.CREATURE:
                from ...generators.creature_generator import CreatureGenerator
                generator = CreatureGenerator(self.project_service.bank_service)
                
                # Si une créature a été sélectionnée, utiliser son template
                if selected_creature:
                    creature_name = selected_creature['name']
                    character = generator.generate_creature_from_template(
                        template_name=creature_name,
                        level=level
                    )
                    if not character:
                        # Si le template n'a pas fonctionné, générer normalement
                        character = generator.generate_creature(
                            level=level,
                            stats_method=stats_method,
                            use_template=False
                        )
                else:
                    # Générer une créature aléatoire
                    character = generator.generate_creature(
                        level=level,
                        stats_method=stats_method,
                        use_template=True
                    )
            else:
                QMessageBox.warning(self, "Erreur", "La génération n'est disponible que pour PNJ et Créatures")
                return
            
            if not character:
                QMessageBox.warning(self, "Erreur", "Impossible de générer le personnage")
                return
            
            # Ajouter le personnage au service
            self.project_service.character_service._characters[character.id] = character
            
            # Sauvegarder si un projet est ouvert
            if self.project_service.get_current_project():
                logger.log_character_action("Généré et sauvegardé", character_name=character.name, 
                                          character_type=char_type.value, level=level)
                self.project_service.save_project(f"Génération d'un {char_type.value}: {character.name}")
            else:
                logger.log_character_action("Généré (non sauvegardé - pas de projet)", 
                                          character_name=character.name, character_type=char_type.value)
            
            # Ouvrir l'éditeur pour permettre l'édition
            from ..widgets.character_editor import CharacterEditor
            editor = CharacterEditor(self.project_service, character, self)
            editor.exec()
            
            self.refresh()
            
        except Exception as e:
            logger.exception(f"Erreur lors de la génération: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la génération: {str(e)}")

