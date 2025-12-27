"""
Éditeur de personnage complet
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QSpinBox, QComboBox, QTabWidget,
    QWidget, QFormLayout, QListWidget, QMessageBox, QListWidgetItem
)
from PyQt6.QtCore import Qt

from ...models.character import (
    Character, CharacterType, CharacterProfile, Characteristics,
    CharacteristicValue, CombatStats, DefenseStats, Weapon,
    CharacterCapabilities, PathCapability, Valuables
)
from ...services.project_service import ProjectService
from .image_upload_widget import ImageUploadWidget


class CharacterEditor(QDialog):
    """Éditeur de personnage complet"""
    
    def __init__(self, project_service: ProjectService, character: Character = None, parent=None):
        super().__init__(parent)
        self.project_service = project_service
        self.character = character
        self.is_new = character is None
        
        if self.is_new:
            self.setWindowTitle("Nouveau personnage")
        else:
            self.setWindowTitle(f"Éditer {character.name}")
        
        self._init_ui()
        
        if not self.is_new:
            self._load_character()
    
    def _init_ui(self):
        """Initialise l'interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Onglets
        tabs = QTabWidget()
        
        # Onglet Profil
        tabs.addTab(self._create_profile_tab(), "Profil")
        
        # Onglet Caractéristiques
        tabs.addTab(self._create_characteristics_tab(), "Caractéristiques")
        
        # Onglet Combat
        tabs.addTab(self._create_combat_tab(), "Combat")
        
        # Onglet Défense
        tabs.addTab(self._create_defense_tab(), "Défense")
        
        # Onglet Armes
        tabs.addTab(self._create_weapons_tab(), "Armes")
        
        # Onglet Capacités
        tabs.addTab(self._create_capabilities_tab(), "Capacités")
        
        # Onglet Équipement
        tabs.addTab(self._create_equipment_tab(), "Équipement")
        
        layout.addWidget(tabs)
        
        # Boutons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_btn = QPushButton("Sauvegarder")
        self.save_btn.clicked.connect(self._save)
        button_layout.addWidget(self.save_btn)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _create_profile_tab(self) -> QWidget:
        """Crée l'onglet Profil"""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(10)
        
        # Nom avec recherche pour les créatures
        name_layout = QHBoxLayout()
        self.name_edit = QLineEdit()
        name_layout.addWidget(self.name_edit)
        
        # Barre de recherche de créatures (visible uniquement pour CREATURE)
        self.creature_search = QLineEdit()
        self.creature_search.setPlaceholderText("Rechercher une créature...")
        self.creature_search.setVisible(False)
        self.creature_search.textChanged.connect(self._on_creature_search_changed)
        name_layout.addWidget(self.creature_search)
        
        layout.addRow("Nom:", name_layout)
        
        # Liste de suggestions pour les créatures
        self.creature_suggestions = QListWidget()
        self.creature_suggestions.setMaximumHeight(100)
        self.creature_suggestions.hide()
        # Permettre la sélection avec un simple clic ou un double-clic
        self.creature_suggestions.itemClicked.connect(self._on_creature_suggestion_clicked)
        self.creature_suggestions.itemDoubleClicked.connect(self._on_creature_suggestion_clicked)
        layout.addRow("", self.creature_suggestions)  # Ligne vide pour les suggestions
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["PJ", "PNJ", "CREATURE"])
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        layout.addRow("Type:", self.type_combo)
        
        self.level_spin = QSpinBox()
        self.level_spin.setMinimum(1)
        self.level_spin.setMaximum(20)
        layout.addRow("Niveau:", self.level_spin)
        
        # Race - menu déroulant depuis la banque RACES
        self.race_combo = QComboBox()
        self.race_combo.setEditable(True)  # Permettre la saisie libre aussi
        self._load_races()
        layout.addRow("Race:", self.race_combo)
        
        # Classe - menu déroulant depuis la banque CLASSES
        self.class_combo = QComboBox()
        self.class_combo.setEditable(True)  # Permettre la saisie libre aussi
        self._load_classes()
        layout.addRow("Classe:", self.class_combo)
        
        self.gender_edit = QLineEdit()
        layout.addRow("Sexe:", self.gender_edit)
        
        self.age_spin = QSpinBox()
        self.age_spin.setMinimum(0)
        self.age_spin.setMaximum(1000)
        layout.addRow("Âge:", self.age_spin)
        
        self.height_edit = QLineEdit()
        layout.addRow("Taille:", self.height_edit)
        
        self.weight_edit = QLineEdit()
        layout.addRow("Poids:", self.weight_edit)
        
        self.racial_ability_edit = QTextEdit()
        self.racial_ability_edit.setMaximumHeight(80)
        layout.addRow("Capacité raciale:", self.racial_ability_edit)
        
        # Profession (uniquement pour PNJ)
        self.profession_combo = QComboBox()
        self.profession_combo.setEditable(True)
        self.profession_combo.setEnabled(False)  # Activé seulement pour PNJ
        layout.addRow("Métier:", self.profession_combo)
        
        # Faction (optionnel pour tous les types)
        self.faction_combo = QComboBox()
        self.faction_combo.setEditable(False)
        self.faction_combo.addItem("Aucune", None)  # Option "Aucune"
        self._load_factions()
        layout.addRow("Faction:", self.faction_combo)
        
        # Image
        entity_id = self.character.id if self.character else ""
        self.image_widget = ImageUploadWidget(
            project_service=self.project_service,
            entity_type="character",
            entity_id=entity_id,
            parent=widget
        )
        layout.addRow("Image:", self.image_widget)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(100)
        layout.addRow("Notes:", self.notes_edit)
        
        # Charger les métiers
        self._load_professions()
        
        # Connecter le changement de type pour activer/désactiver le métier
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        
        return widget
    
    def _load_factions(self):
        """Charge la liste des factions depuis la banque de données"""
        self.faction_combo.clear()
        self.faction_combo.addItem("Aucune", None)  # Option "Aucune"
        
        if self.project_service.bank_service:
            from ...models.bank import BankType
            factions_bank = self.project_service.bank_service.get_bank_by_type(BankType.FACTIONS)
            if factions_bank:
                for entry in factions_bank.entries:
                    self.faction_combo.addItem(entry.value, entry.id)
    
    def _load_professions(self):
        """Charge la liste des métiers depuis les données initiales"""
        from ...core.data_loader import DataLoader
        professions = DataLoader.load_professions()
        
        self.profession_combo.clear()
        self.profession_combo.addItem("")  # Option vide
        
        for profession in professions:
            name = profession.get('name', '')
            if name:
                self.profession_combo.addItem(name)
    
    def _load_races(self):
        """Charge la liste des races depuis la banque RACES"""
        from ...models.bank import BankType
        
        self.race_combo.clear()
        self.race_combo.addItem("")  # Option vide
        
        if self.project_service and self.project_service.bank_service:
            # S'assurer que les banques sont initialisées
            from ...core.data_loader import DataLoader
            DataLoader.initialize_banks(self.project_service.bank_service)
            
            races_bank = self.project_service.bank_service.get_bank_by_type(BankType.RACES)
            if races_bank:
                for entry in races_bank.entries:
                    if entry.value and entry.value.strip():
                        self.race_combo.addItem(entry.value)
    
    def _load_classes(self):
        """Charge la liste des classes depuis la banque CLASSES"""
        from ...models.bank import BankType
        
        self.class_combo.clear()
        self.class_combo.addItem("")  # Option vide
        
        if self.project_service and self.project_service.bank_service:
            # S'assurer que les banques sont initialisées
            from ...core.data_loader import DataLoader
            DataLoader.initialize_banks(self.project_service.bank_service)
            
            classes_bank = self.project_service.bank_service.get_bank_by_type(BankType.CLASSES)
            if classes_bank:
                for entry in classes_bank.entries:
                    if entry.value and entry.value.strip():
                        self.class_combo.addItem(entry.value)
    
    def _on_type_changed(self, char_type: str):
        """Active/désactive le champ métier selon le type"""
        # Activer le métier uniquement pour les PNJ
        self.profession_combo.setEnabled(char_type == "PNJ")
        
        # Afficher la recherche de créatures uniquement pour CREATURE
        is_creature = (char_type == "CREATURE")
        self.creature_search.setVisible(is_creature)
        if not is_creature:
            self.creature_suggestions.hide()
            self.creature_search.clear()
    
    def _on_creature_search_changed(self, text: str):
        """Gère le changement dans la barre de recherche de créatures"""
        if not text.strip():
            self.creature_suggestions.hide()
            return
        
        # Charger les créatures depuis le JSON directement (comme dans le générateur)
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
            from ...models.bank import BankType
            creatures_bank = self.project_service.bank_service.get_bank_by_type(BankType.CREATURES)
            if creatures_bank:
                for entry in creatures_bank.entries:
                    if entry.value and entry.value.strip():
                        all_creatures.append({
                            'name': entry.value,
                            'metadata': entry.metadata
                        })
        
        # Filtrer les créatures
        search_text = text.lower()
        matches = [
            c for c in all_creatures
            if search_text in c['name'].lower() and c['name']
        ]
        
        # Limiter à 10 résultats
        matches = matches[:10]
        
        # Afficher les suggestions
        self.creature_suggestions.clear()
        if matches:
            for match in matches:
                creature_name = match['name']
                creature_level = match['metadata'].get('level', 1)
                item_text = f"{creature_name} (Niveau {creature_level})"
                item = QListWidgetItem(item_text)
                # Stocker tout l'objet match pour pouvoir récupérer le niveau
                item.setData(Qt.ItemDataRole.UserRole, match)
                self.creature_suggestions.addItem(item)
            self.creature_suggestions.show()
        else:
            self.creature_suggestions.hide()
    
    def _on_creature_suggestion_clicked(self, item: QListWidgetItem):
        """Gère le clic sur une suggestion de créature"""
        creature_data = item.data(Qt.ItemDataRole.UserRole)
        if creature_data:
            # Si c'est un dictionnaire (nouveau format), extraire le nom et le niveau
            if isinstance(creature_data, dict):
                creature_name = creature_data.get('name', '')
                creature_level = creature_data.get('metadata', {}).get('level', 1)
            else:
                # Ancien format (juste le nom)
                creature_name = creature_data
                creature_level = 1
            
            self.name_edit.setText(creature_name)
            self.level_spin.setValue(creature_level)
            
            self.creature_search.clear()
            self.creature_suggestions.hide()
    
    def _create_characteristics_tab(self) -> QWidget:
        """Crée l'onglet Caractéristiques"""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(10)
        
        self.char_edits = {}
        for char_name in ["FOR", "DEX", "CON", "INT", "SAG", "CHA"]:
            spin = QSpinBox()
            spin.setMinimum(1)
            spin.setMaximum(20)
            spin.setValue(10)
            spin.valueChanged.connect(lambda v, c=char_name: self._update_modifier(c))
            layout.addRow(f"{char_name}:", spin)
            self.char_edits[char_name] = spin
        
        # Labels pour les modificateurs
        self.mod_labels = {}
        for char_name in ["FOR", "DEX", "CON", "INT", "SAG", "CHA"]:
            label = QLabel("+0")
            layout.addRow(f"Mod. {char_name}:", label)
            self.mod_labels[char_name] = label
        
        return widget
    
    def _create_combat_tab(self) -> QWidget:
        """Crée l'onglet Combat"""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(10)
        
        self.melee_attack_edit = QLineEdit()
        layout.addRow("Attaque au contact:", self.melee_attack_edit)
        
        self.ranged_attack_edit = QLineEdit()
        layout.addRow("Attaque à distance:", self.ranged_attack_edit)
        
        self.magic_attack_edit = QLineEdit()
        layout.addRow("Attaque magique:", self.magic_attack_edit)
        
        self.initiative_edit = QLineEdit()
        layout.addRow("Initiative:", self.initiative_edit)
        
        self.life_dice_edit = QLineEdit()
        layout.addRow("Dés de vie (DV):", self.life_dice_edit)
        
        self.life_points_spin = QSpinBox()
        self.life_points_spin.setMinimum(0)
        self.life_points_spin.setMaximum(1000)
        layout.addRow("Points de vie (PV):", self.life_points_spin)
        
        self.current_life_points_spin = QSpinBox()
        self.current_life_points_spin.setMinimum(0)
        self.current_life_points_spin.setMaximum(1000)
        layout.addRow("PV restants:", self.current_life_points_spin)
        
        self.temporary_damage_spin = QSpinBox()
        self.temporary_damage_spin.setMinimum(0)
        self.temporary_damage_spin.setMaximum(1000)
        layout.addRow("Dégâts temporaires:", self.temporary_damage_spin)
        
        return widget
    
    def _create_defense_tab(self) -> QWidget:
        """Crée l'onglet Défense"""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(10)
        
        self.base_defense_label = QLabel("10")
        layout.addRow("Base:", self.base_defense_label)
        
        self.armor_spin = QSpinBox()
        self.armor_spin.setMinimum(0)
        self.armor_spin.setMaximum(50)
        self.armor_spin.valueChanged.connect(self._update_defense_total)
        layout.addRow("Armure:", self.armor_spin)
        
        self.shield_spin = QSpinBox()
        self.shield_spin.setMinimum(0)
        self.shield_spin.setMaximum(50)
        self.shield_spin.valueChanged.connect(self._update_defense_total)
        layout.addRow("Bouclier:", self.shield_spin)
        
        self.dex_defense_label = QLabel("+0")
        layout.addRow("Dextérité:", self.dex_defense_label)
        
        self.misc_defense_spin = QSpinBox()
        self.misc_defense_spin.setMinimum(-50)
        self.misc_defense_spin.setMaximum(50)
        self.misc_defense_spin.valueChanged.connect(self._update_defense_total)
        layout.addRow("Divers:", self.misc_defense_spin)
        
        self.total_defense_label = QLabel("10")
        self.total_defense_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addRow("Défense totale:", self.total_defense_label)
        
        return widget
    
    def _create_weapons_tab(self) -> QWidget:
        """Crée l'onglet Armes"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.weapons_list = QListWidget()
        layout.addWidget(self.weapons_list)
        
        button_layout = QHBoxLayout()
        add_weapon_btn = QPushButton("Ajouter arme")
        add_weapon_btn.clicked.connect(self._add_weapon)
        button_layout.addWidget(add_weapon_btn)
        
        remove_weapon_btn = QPushButton("Supprimer")
        remove_weapon_btn.clicked.connect(self._remove_weapon)
        button_layout.addWidget(remove_weapon_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        return widget
    
    def _create_capabilities_tab(self) -> QWidget:
        """Crée l'onglet Capacités"""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(10)
        
        for i in [1, 2, 3]:
            path_name_edit = QLineEdit()
            layout.addRow(f"Voie {i} - Nom:", path_name_edit)
            setattr(self, f'path{i}_name', path_name_edit)
            
            path_rank_spin = QSpinBox()
            path_rank_spin.setMinimum(0)
            path_rank_spin.setMaximum(3)
            layout.addRow(f"Voie {i} - Rang:", path_rank_spin)
            setattr(self, f'path{i}_rank', path_rank_spin)
            
            for level in [1, 2, 3]:
                level_edit = QLineEdit()
                layout.addRow(f"Voie {i} - Niveau {level}:", level_edit)
                setattr(self, f'path{i}_level{level}', level_edit)
        
        return widget
    
    def _create_equipment_tab(self) -> QWidget:
        """Crée l'onglet Équipement avec barre de recherche"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        
        # Barre de recherche avec autocomplétion
        search_label = QLabel("Rechercher un équipement:")
        layout.addWidget(search_label)
        
        self.equipment_search = QLineEdit()
        self.equipment_search.setPlaceholderText("Tapez pour rechercher...")
        self.equipment_search.textChanged.connect(self._on_equipment_search_changed)
        layout.addWidget(self.equipment_search)
        
        # Liste de suggestions
        self.equipment_suggestions = QListWidget()
        self.equipment_suggestions.setMaximumHeight(150)
        self.equipment_suggestions.itemDoubleClicked.connect(self._add_equipment_from_suggestion)
        self.equipment_suggestions.hide()  # Cachée par défaut
        layout.addWidget(self.equipment_suggestions)
        
        # Liste des équipements du personnage
        equipment_label = QLabel("Équipement du personnage:")
        layout.addWidget(equipment_label)
        
        self.equipment_list = QListWidget()
        layout.addWidget(self.equipment_list)
        
        # Boutons
        button_layout = QHBoxLayout()
        
        add_custom_btn = QPushButton("Ajouter équipement personnalisé")
        add_custom_btn.clicked.connect(self._add_custom_equipment)
        button_layout.addWidget(add_custom_btn)
        
        remove_equipment_btn = QPushButton("Supprimer")
        remove_equipment_btn.clicked.connect(self._remove_equipment)
        button_layout.addWidget(remove_equipment_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        valuables_label = QLabel("Objets de valeur:")
        layout.addWidget(valuables_label)
        
        self.valuables_list = QListWidget()
        layout.addWidget(self.valuables_list)
        
        # Charger tous les équipements disponibles
        self._load_all_equipment()
        
        return widget
    
    def _update_modifier(self, char_name: str):
        """Met à jour le modificateur d'une caractéristique"""
        value = self.char_edits[char_name].value()
        modifier = (value - 10) // 2
        mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
        self.mod_labels[char_name].setText(mod_str)
        
        # Mettre à jour aussi la défense si c'est DEX
        if char_name == "DEX":
            self.dex_defense_label.setText(mod_str)
            self._update_defense_total()
    
    def _update_defense_total(self):
        """Met à jour la défense totale"""
        base = 10
        armor = self.armor_spin.value()
        shield = self.shield_spin.value()
        dex_mod = int(self.dex_defense_label.text().replace("+", ""))
        misc = self.misc_defense_spin.value()
        total = base + armor + shield + dex_mod + misc
        self.total_defense_label.setText(str(total))
    
    def _add_weapon(self):
        """Ajoute une arme"""
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Nouvelle arme", "Nom de l'arme:")
        if ok and name:
            self.weapons_list.addItem(name)
    
    def _remove_weapon(self):
        """Supprime une arme"""
        current = self.weapons_list.currentItem()
        if current:
            self.weapons_list.takeItem(self.weapons_list.row(current))
    
    def _load_all_equipment(self):
        """Charge tous les équipements disponibles depuis les données"""
        from ...core.data_loader import DataLoader
        
        self.all_equipment = []
        
        # Charger depuis les fichiers JSON
        weapons = DataLoader.load_weapons()
        armors = DataLoader.load_armors()
        tools = DataLoader.load_tools()
        trinkets = DataLoader.load_trinkets()
        
        # Ajouter tous les équipements avec leur type
        for weapon in weapons:
            self.all_equipment.append({
                'name': weapon.get('name', ''),
                'type': 'Arme',
                'data': weapon
            })
        
        for armor in armors:
            self.all_equipment.append({
                'name': armor.get('name', ''),
                'type': 'Armure',
                'data': armor
            })
        
        for tool in tools:
            self.all_equipment.append({
                'name': tool.get('name', ''),
                'type': 'Outil',
                'data': tool
            })
        
        for trinket in trinkets:
            self.all_equipment.append({
                'name': trinket.get('name', ''),
                'type': 'Babiole',
                'data': trinket
            })
    
    def _on_equipment_search_changed(self, text: str):
        """Gère le changement dans la barre de recherche"""
        if not text.strip():
            self.equipment_suggestions.hide()
            return
        
        # Filtrer les équipements
        search_text = text.lower()
        matches = [
            eq for eq in self.all_equipment
            if search_text in eq['name'].lower()
        ]
        
        # Limiter à 10 résultats
        matches = matches[:10]
        
        # Afficher les suggestions
        self.equipment_suggestions.clear()
        if matches:
            for match in matches:
                item_text = f"{match['name']} ({match['type']})"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, match['name'])
                self.equipment_suggestions.addItem(item)
            self.equipment_suggestions.show()
        else:
            self.equipment_suggestions.hide()
    
    def _add_equipment_from_suggestion(self, item: QListWidgetItem):
        """Ajoute un équipement depuis la suggestion"""
        equipment_name = item.data(Qt.ItemDataRole.UserRole)
        if equipment_name:
            # Vérifier qu'il n'est pas déjà dans la liste
            existing_items = [
                self.equipment_list.item(i).text()
                for i in range(self.equipment_list.count())
            ]
            if equipment_name not in existing_items:
                self.equipment_list.addItem(equipment_name)
                # Réinitialiser la recherche
                self.equipment_search.clear()
                self.equipment_suggestions.hide()
    
    def _add_custom_equipment(self):
        """Ajoute un équipement personnalisé"""
        from PyQt6.QtWidgets import QInputDialog
        item, ok = QInputDialog.getText(self, "Nouvel équipement", "Nom de l'équipement:")
        if ok and item and item.strip():
            # Vérifier qu'il n'est pas déjà dans la liste
            existing_items = [
                self.equipment_list.item(i).text()
                for i in range(self.equipment_list.count())
            ]
            if item.strip() not in existing_items:
                self.equipment_list.addItem(item.strip())
    
    def _remove_equipment(self):
        """Supprime un équipement"""
        current = self.equipment_list.currentItem()
        if current:
            self.equipment_list.takeItem(self.equipment_list.row(current))
    
    def _load_character(self):
        """Charge les données du personnage"""
        if not self.character:
            return
        
        # Profil
        self.name_edit.setText(self.character.name)
        self.type_combo.setCurrentText(self.character.type.value)
        self.level_spin.setValue(self.character.profile.level)
        
        # Race - chercher dans le combo ou ajouter si absent
        race_text = self.character.profile.race or ""
        index = self.race_combo.findText(race_text)
        if index >= 0:
            self.race_combo.setCurrentIndex(index)
        else:
            self.race_combo.setCurrentText(race_text)
        
        # Classe - chercher dans le combo ou ajouter si absent
        class_text = self.character.profile.character_class or ""
        if class_text:
            index = self.class_combo.findText(class_text)
            if index >= 0:
                self.class_combo.setCurrentIndex(index)
            else:
                self.class_combo.setCurrentText(class_text)
        else:
            self.class_combo.setCurrentIndex(0)
        if self.character.profile.gender:
            self.gender_edit.setText(self.character.profile.gender)
        if self.character.profile.age:
            self.age_spin.setValue(self.character.profile.age)
        if self.character.profile.height:
            self.height_edit.setText(self.character.profile.height)
        if self.character.profile.weight:
            self.weight_edit.setText(self.character.profile.weight)
        self.racial_ability_edit.setPlainText(self.character.profile.racial_ability if self.character.profile.racial_ability else "")
        
        # Profession
        if self.character.profile.profession:
            index = self.profession_combo.findText(self.character.profile.profession)
            if index >= 0:
                self.profession_combo.setCurrentIndex(index)
            else:
                self.profession_combo.setCurrentText(self.character.profile.profession)
        else:
            self.profession_combo.setCurrentIndex(0)
        
        # Activer/désactiver selon le type
        self._on_type_changed(self.character.type.value)
        
        # Faction
        if self.character.faction:
            # Trouver l'index de la faction dans le combo
            for i in range(self.faction_combo.count()):
                if self.faction_combo.itemData(i) == self.character.faction:
                    self.faction_combo.setCurrentIndex(i)
                    break
        else:
            self.faction_combo.setCurrentIndex(0)  # "Aucune"
        
        # Image
        if self.character.image_id:
            self.image_widget.set_image_id(self.character.image_id)
            # Mettre à jour l'entity_id si c'est un nouveau personnage
            if not self.image_widget.entity_id:
                self.image_widget.entity_id = self.character.id
        
        self.notes_edit.setPlainText(self.character.notes if self.character.notes else "")
        
        # Caractéristiques
        char_map = {
            "FOR": self.character.characteristics.strength,
            "DEX": self.character.characteristics.dexterity,
            "CON": self.character.characteristics.constitution,
            "INT": self.character.characteristics.intelligence,
            "SAG": self.character.characteristics.wisdom,
            "CHA": self.character.characteristics.charisma
        }
        for char_name, char_value in char_map.items():
            self.char_edits[char_name].setValue(char_value.value)
            self._update_modifier(char_name)
        
        # Combat
        self.melee_attack_edit.setText(self.character.combat.melee_attack)
        self.ranged_attack_edit.setText(self.character.combat.ranged_attack)
        self.magic_attack_edit.setText(self.character.combat.magic_attack)
        self.initiative_edit.setText(self.character.combat.initiative)
        self.life_dice_edit.setText(self.character.combat.life_dice)
        self.life_points_spin.setValue(self.character.combat.life_points)
        self.current_life_points_spin.setValue(self.character.combat.current_life_points)
        self.temporary_damage_spin.setValue(self.character.combat.temporary_damage)
        
        # Défense
        self.armor_spin.setValue(self.character.defense.armor)
        self.shield_spin.setValue(self.character.defense.shield)
        self.misc_defense_spin.setValue(self.character.defense.misc)
        self._update_defense_total()
        
        # Armes
        for weapon in self.character.weapons:
            self.weapons_list.addItem(weapon.name)
        
        # Capacités
        for i in [1, 2, 3]:
            path = getattr(self.character.capabilities, f'path{i}')
            getattr(self, f'path{i}_name').setText(path.name)
            getattr(self, f'path{i}_rank').setValue(path.rank)
            if path.level1:
                getattr(self, f'path{i}_level1').setText(path.level1)
            if path.level2:
                getattr(self, f'path{i}_level2').setText(path.level2)
            if path.level3:
                getattr(self, f'path{i}_level3').setText(path.level3)
        
        # Équipement
        for item in self.character.equipment:
            self.equipment_list.addItem(item)
        
        # Objets de valeur
        if self.character.valuables.purse:
            self.valuables_list.addItem(f"Bourse: {self.character.valuables.purse}")
        for item in self.character.valuables.items:
            self.valuables_list.addItem(item)
    
    def _save(self):
        """Sauvegarde le personnage"""
        from ...core.utils import generate_id
        
        # Validation minimale - seul le nom est vraiment obligatoire
        name = self.name_edit.text().strip()
        if not name:
            # Si le nom est vide, utiliser un nom par défaut
            name = "Personnage sans nom"
        
        # Déterminer le type de personnage
        type_text = self.type_combo.currentText()
        try:
            char_type = CharacterType(type_text)
        except ValueError:
            # Si le texte ne correspond pas exactement, essayer de trouver la correspondance
            for ct in CharacterType:
                if ct.value.upper() == type_text.upper():
                    char_type = ct
                    break
            else:
                # Par défaut, utiliser PJ
                char_type = CharacterType.PJ
        
        # Créer ou mettre à jour le personnage
        if self.is_new:
            from ...core.utils import generate_id
            char_id = generate_id()
            # Mettre à jour l'entity_id du widget image
            self.image_widget.entity_id = char_id
            self.character = Character(
                id=char_id,
                name=self.name_edit.text().strip(),
                type=char_type,
                profile=CharacterProfile(),
                characteristics=Characteristics(),
                combat=CombatStats(),
                defense=DefenseStats(),
                capabilities=CharacterCapabilities(),
                valuables=Valuables()
            )
        
        # Profil
        self.character.name = name  # Utiliser le nom validé
        self.character.type = char_type  # S'assurer que le type est bien défini
        self.character.profile.level = self.level_spin.value()
        self.character.profile.race = self.race_combo.currentText().strip() or ""
        self.character.profile.character_class = self.class_combo.currentText().strip() or None
        self.character.profile.gender = self.gender_edit.text().strip() or None
        self.character.profile.age = self.age_spin.value() if self.age_spin.value() > 0 else None
        self.character.profile.height = self.height_edit.text().strip() or None
        self.character.profile.weight = self.weight_edit.text().strip() or None
        self.character.profile.racial_ability = self.racial_ability_edit.toPlainText() or ""
        
        # Profession (uniquement pour PNJ)
        if char_type == CharacterType.PNJ:
            profession_text = self.profession_combo.currentText().strip()
            self.character.profile.profession = profession_text if profession_text else None
        else:
            self.character.profile.profession = None
        
        # Faction (optionnel pour tous)
        faction_id = self.faction_combo.currentData()
        self.character.faction = faction_id if faction_id else None
        
        self.character.notes = self.notes_edit.toPlainText() or ""
        
        # Caractéristiques
        char_map = {
            "FOR": "strength",
            "DEX": "dexterity",
            "CON": "constitution",
            "INT": "intelligence",
            "SAG": "wisdom",
            "CHA": "charisma"
        }
        for char_name, attr_name in char_map.items():
            value = self.char_edits[char_name].value()
            setattr(self.character.characteristics, attr_name, CharacteristicValue(value=value))
        
        # Combat
        self.character.combat.melee_attack = self.melee_attack_edit.text()
        self.character.combat.ranged_attack = self.ranged_attack_edit.text()
        self.character.combat.magic_attack = self.magic_attack_edit.text()
        self.character.combat.initiative = self.initiative_edit.text()
        self.character.combat.life_dice = self.life_dice_edit.text()
        self.character.combat.life_points = self.life_points_spin.value()
        self.character.combat.current_life_points = self.current_life_points_spin.value()
        self.character.combat.temporary_damage = self.temporary_damage_spin.value()
        
        # Défense
        self.character.defense.armor = self.armor_spin.value()
        self.character.defense.shield = self.shield_spin.value()
        self.character.defense.dexterity = int(self.dex_defense_label.text().replace("+", ""))
        self.character.defense.misc = self.misc_defense_spin.value()
        
        # Armes
        self.character.weapons = []
        for i in range(self.weapons_list.count()):
            weapon_name = self.weapons_list.item(i).text()
            self.character.weapons.append(Weapon(name=weapon_name))
        
        # Capacités - permettre les champs vides
        for i in [1, 2, 3]:
            path_name = getattr(self, f'path{i}_name').text().strip()
            path = PathCapability(
                name=path_name or "",
                rank=getattr(self, f'path{i}_rank').value(),
                level1=getattr(self, f'path{i}_level1').text().strip() or None,
                level2=getattr(self, f'path{i}_level2').text().strip() or None,
                level3=getattr(self, f'path{i}_level3').text().strip() or None
            )
            setattr(self.character.capabilities, f'path{i}', path)
        
        # Équipement
        self.character.equipment = []
        for i in range(self.equipment_list.count()):
            item = self.equipment_list.item(i)
            if item:
                self.character.equipment.append(item.text())
        
        # Image
        self.character.image_id = self.image_widget.get_image_id()
        
        # Sauvegarder dans le service
        if self.is_new:
            self.project_service.character_service._characters[self.character.id] = self.character
        else:
            self.project_service.character_service.update_character(self.character)
        
        # Sauvegarder le projet
        if self.project_service.get_current_project():
            self.project_service.save_project(f"{'Création' if self.is_new else 'Modification'} du personnage '{self.character.name}'")
        
        self.accept()

