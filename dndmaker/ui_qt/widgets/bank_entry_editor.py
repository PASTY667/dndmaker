"""
Éditeur d'entrée de banque de données
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QSpinBox, QComboBox, QFormLayout,
    QWidget, QMessageBox, QListWidget, QListWidgetItem,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox
)
from PyQt6.QtCore import Qt

from ...models.bank import BankType, BankEntry
from ...core.logger import get_logger
from .image_upload_widget import ImageUploadWidget

logger = get_logger()


class BankEntryEditor(QDialog):
    """Éditeur d'entrée de banque de données"""
    
    def __init__(self, bank_type: BankType, entry: BankEntry = None, parent=None, project_service=None):
        """
        Crée un éditeur d'entrée
        
        Args:
            bank_type: Type de banque
            entry: Entrée existante (None pour une nouvelle entrée)
            parent: Widget parent
            project_service: Service de projet (nécessaire pour les lieux avec bestiaire)
        """
        super().__init__(parent)
        self.bank_type = bank_type
        self.entry = entry
        self.is_new = entry is None
        self.project_service = project_service
        
        # Si project_service n'est pas fourni, essayer de le récupérer depuis le parent
        if not self.project_service and parent:
            if hasattr(parent, 'project_service'):
                self.project_service = parent.project_service
        
        if self.is_new:
            self.setWindowTitle(f"Nouvelle entrée - {bank_type.value}")
        else:
            self.setWindowTitle(f"Modifier entrée - {bank_type.value}")
        
        self.setMinimumWidth(500)
        self._init_ui()
        
        if not self.is_new:
            self._load_entry()
    
    def _init_ui(self):
        """Initialise l'interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Formulaire selon le type de banque
        if self.bank_type == BankType.CREATURES:
            self._create_creature_form(layout)
        elif self.bank_type == BankType.PROFESSIONS:
            self._create_profession_form(layout)
        elif self.bank_type == BankType.ARMORS:
            self._create_armor_form(layout)
        elif self.bank_type == BankType.TOOLS:
            self._create_tool_form(layout)
        elif self.bank_type == BankType.TRINKETS:
            self._create_trinket_form(layout)
        elif self.bank_type == BankType.WEAPONS:
            self._create_weapon_form(layout)
        elif self.bank_type == BankType.NAMES:
            self._create_name_form(layout)
        elif self.bank_type == BankType.LOCATIONS:
            self._create_location_form(layout)
        elif self.bank_type == BankType.FACTIONS:
            self._create_faction_form(layout)
        else:
            self._create_simple_form(layout)
        
        # Boutons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("Enregistrer")
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _create_simple_form(self, layout: QVBoxLayout):
        """Crée un formulaire simple pour les banques basiques"""
        form = QFormLayout()
        
        self.value_edit = QLineEdit()
        form.addRow("Valeur:", self.value_edit)
        
        layout.addLayout(form)
    
    def _create_name_form(self, layout: QVBoxLayout):
        """Crée un formulaire pour les noms avec origine raciale"""
        form = QFormLayout()
        
        self.name_edit = QLineEdit()
        form.addRow("Nom:", self.name_edit)
        
        self.racial_origin_edit = QLineEdit()
        self.racial_origin_edit.setPlaceholderText("Humain, Elfe, Nain, etc.")
        form.addRow("Origine raciale:", self.racial_origin_edit)
        
        layout.addLayout(form)
    
    def _create_profession_form(self, layout: QVBoxLayout):
        """Crée un formulaire pour les professions"""
        form = QFormLayout()
        
        self.name_edit = QLineEdit()
        form.addRow("Nom:", self.name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        form.addRow("Description:", self.description_edit)
        
        self.tools_edit = QLineEdit()
        self.tools_edit.setPlaceholderText("Séparés par des virgules")
        form.addRow("Outils:", self.tools_edit)
        
        self.skills_edit = QLineEdit()
        self.skills_edit.setPlaceholderText("Séparés par des virgules")
        form.addRow("Compétences:", self.skills_edit)
        
        layout.addLayout(form)
    
    def _create_armor_form(self, layout: QVBoxLayout):
        """Crée un formulaire pour les armures"""
        form = QFormLayout()
        
        self.name_edit = QLineEdit()
        form.addRow("Nom:", self.name_edit)
        
        self.type_combo = QComboBox()
        self.type_combo.setEditable(True)
        self.type_combo.addItems(["légère", "moyenne", "lourde"])
        form.addRow("Type:", self.type_combo)
        
        self.ac_spin = QSpinBox()
        self.ac_spin.setMinimum(0)
        self.ac_spin.setMaximum(30)
        form.addRow("Classe d'armure (AC):", self.ac_spin)
        
        self.ac_modifier_edit = QLineEdit()
        self.ac_modifier_edit.setPlaceholderText("DEX, CON, etc.")
        form.addRow("Modificateur AC:", self.ac_modifier_edit)
        
        self.price_edit = QLineEdit()
        form.addRow("Prix:", self.price_edit)
        
        self.weight_edit = QLineEdit()
        self.weight_edit.setPlaceholderText("5 kg")
        form.addRow("Poids:", self.weight_edit)
        
        self.stealth_combo = QComboBox()
        self.stealth_combo.addItems(["normal", "désavantage"])
        form.addRow("Furtivité:", self.stealth_combo)
        
        layout.addLayout(form)
    
    def _create_tool_form(self, layout: QVBoxLayout):
        """Crée un formulaire pour les outils"""
        form = QFormLayout()
        
        self.name_edit = QLineEdit()
        form.addRow("Nom:", self.name_edit)
        
        self.price_edit = QLineEdit()
        form.addRow("Prix:", self.price_edit)
        
        self.weight_edit = QLineEdit()
        self.weight_edit.setPlaceholderText("2.5 kg")
        form.addRow("Poids:", self.weight_edit)
        
        layout.addLayout(form)
    
    def _create_trinket_form(self, layout: QVBoxLayout):
        """Crée un formulaire pour les babioles"""
        form = QFormLayout()
        
        self.name_edit = QLineEdit()
        form.addRow("Nom:", self.name_edit)
        
        self.price_edit = QLineEdit()
        form.addRow("Prix:", self.price_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        form.addRow("Description:", self.description_edit)
        
        layout.addLayout(form)
    
    def _create_faction_form(self, layout: QVBoxLayout):
        """Crée un formulaire pour les factions"""
        form = QFormLayout()
        
        # Nom
        self.name_edit = QLineEdit()
        form.addRow("Nom:", self.name_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(150)
        form.addRow("Description:", self.description_edit)
        
        layout.addLayout(form)
        
        # Image
        image_label = QLabel("Image:")
        layout.addWidget(image_label)
        # L'entry_id sera défini dans __init__ si c'est une nouvelle entrée
        entry_id = self.entry.id if self.entry else ""
        self.image_widget = ImageUploadWidget(
            project_service=self.project_service,
            entity_type="faction",
            entity_id=entry_id,
            parent=self
        )
        layout.addWidget(self.image_widget)
    
    def _create_table_form(self, layout: QVBoxLayout):
        """Crée un formulaire pour les tables personnalisées"""
        from ...core.i18n import tr
        
        # Nom de la table
        form = QFormLayout()
        self.table_name_edit = QLineEdit()
        form.addRow(tr("table.name"), self.table_name_edit)
        layout.addLayout(form)
        
        # Section des champs (schéma)
        fields_group = QGroupBox(tr("table.fields"))
        fields_layout = QVBoxLayout(fields_group)
        
        # Tableau des champs
        self.fields_table = QTableWidget()
        self.fields_table.setColumnCount(3)
        self.fields_table.setHorizontalHeaderLabels([
            tr("table.field_name"),
            tr("table.field_type"),
            ""
        ])
        self.fields_table.horizontalHeader().setStretchLastSection(False)
        self.fields_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.fields_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.fields_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.fields_table.setMaximumHeight(200)
        fields_layout.addWidget(self.fields_table)
        
        # Bouton pour ajouter un champ
        add_field_btn = QPushButton(tr("table.add_field"))
        add_field_btn.clicked.connect(self._add_table_field)
        fields_layout.addWidget(add_field_btn)
        
        layout.addWidget(fields_group)
        
        # Section des lignes de données
        rows_group = QGroupBox(tr("table.rows"))
        rows_layout = QVBoxLayout(rows_group)
        
        # Tableau des lignes
        self.rows_table = QTableWidget()
        self.rows_table.setMaximumHeight(300)
        rows_layout.addWidget(self.rows_table)
        
        # Boutons pour gérer les lignes
        rows_btn_layout = QHBoxLayout()
        add_row_btn = QPushButton(tr("table.add_row"))
        add_row_btn.clicked.connect(self._add_table_row)
        rows_btn_layout.addWidget(add_row_btn)
        
        delete_row_btn = QPushButton(tr("table.delete_row"))
        delete_row_btn.clicked.connect(self._delete_table_row)
        rows_btn_layout.addWidget(delete_row_btn)
        
        rows_btn_layout.addStretch()
        rows_layout.addLayout(rows_btn_layout)
        
        layout.addWidget(rows_group)
        self.rows_group = rows_group
    
    def _add_table_field(self):
        """Ajoute un nouveau champ au schéma de la table"""
        from ...core.i18n import tr
        
        row = self.fields_table.rowCount()
        self.fields_table.insertRow(row)
        
        # Nom du champ
        name_edit = QLineEdit()
        name_edit.setPlaceholderText(tr("table.field_name"))
        self.fields_table.setCellWidget(row, 0, name_edit)
        
        # Type du champ
        type_combo = QComboBox()
        type_combo.addItems([
            tr("table.string"),
            tr("table.number"),
            tr("table.boolean"),
            tr("table.date")
        ])
        self.fields_table.setCellWidget(row, 1, type_combo)
        
        # Bouton supprimer
        remove_btn = QPushButton(tr("table.remove_field"))
        remove_btn.clicked.connect(lambda: self._remove_table_field(row))
        self.fields_table.setCellWidget(row, 2, remove_btn)
    
    def _remove_table_field(self, row: int):
        """Supprime un champ du schéma"""
        self.fields_table.removeRow(row)
        # Réindexer les boutons de suppression
        for i in range(self.fields_table.rowCount()):
            remove_btn = self.fields_table.cellWidget(i, 2)
            if remove_btn:
                remove_btn.clicked.disconnect()
                remove_btn.clicked.connect(lambda checked, r=i: self._remove_table_field(r))
    
    def _add_table_row(self):
        """Ajoute une nouvelle ligne de données à la table"""
        if not self.rows_table:
            return
        
        # Récupérer le schéma depuis les champs définis
        from ...core.i18n import tr
        
        schema = []
        type_map = {
            tr("table.string"): 'string',
            tr("table.number"): 'number',
            tr("table.boolean"): 'boolean',
            tr("table.date"): 'date'
        }
        
        for row_idx in range(self.fields_table.rowCount()):
            name_widget = self.fields_table.cellWidget(row_idx, 0)
            type_widget = self.fields_table.cellWidget(row_idx, 1)
            
            if name_widget and type_widget:
                field_name = name_widget.text().strip()
                if field_name:
                    field_type_text = type_widget.currentText()
                    field_type = type_map.get(field_type_text, 'string')
                    schema.append({
                        'name': field_name,
                        'type': field_type
                    })
        
        if not schema:
            QMessageBox.warning(self, tr("msg.warning"), tr("table.no_fields"))
            return
        
        # Mettre à jour les colonnes du tableau si nécessaire
        if self.rows_table.columnCount() != len(schema):
            self.rows_table.setColumnCount(len(schema))
            self.rows_table.setHorizontalHeaderLabels([f.get('name', '') for f in schema])
        
        row = self.rows_table.rowCount()
        self.rows_table.insertRow(row)
        
        # Créer un widget d'édition pour chaque champ
        for col, field in enumerate(schema):
            field_type = field.get('type', 'string')
            
            if field_type == 'number':
                widget = QSpinBox()
                widget.setMinimum(-999999)
                widget.setMaximum(999999)
            elif field_type == 'boolean':
                widget = QComboBox()
                widget.addItems(['False', 'True'])
            else:  # string ou date
                widget = QLineEdit()
                if field_type == 'date':
                    widget.setPlaceholderText("YYYY-MM-DD")
            
            self.rows_table.setCellWidget(row, col, widget)
    
    def _delete_table_row(self):
        """Supprime la ligne sélectionnée du tableau"""
        if not self.rows_table:
            return
        
        current_row = self.rows_table.currentRow()
        if current_row >= 0:
            self.rows_table.removeRow(current_row)
        else:
            from ...core.i18n import tr
            QMessageBox.information(self, tr("msg.info"), "Sélectionnez une ligne à supprimer")
    
    def _create_weapon_form(self, layout: QVBoxLayout):
        """Crée un formulaire pour les armes"""
        form = QFormLayout()
        
        self.name_edit = QLineEdit()
        form.addRow("Nom:", self.name_edit)
        
        self.type_combo = QComboBox()
        self.type_combo.setEditable(True)
        self.type_combo.addItems(["courante", "guerre", "exotique"])
        form.addRow("Type:", self.type_combo)
        
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.addItems(["corps_à_corps", "distance"])
        form.addRow("Catégorie:", self.category_combo)
        
        self.price_edit = QLineEdit()
        form.addRow("Prix:", self.price_edit)
        
        self.damage_edit = QLineEdit()
        self.damage_edit.setPlaceholderText("1d6")
        form.addRow("Dégâts:", self.damage_edit)
        
        self.damage_type_combo = QComboBox()
        self.damage_type_combo.setEditable(True)
        self.damage_type_combo.addItems(["contondant", "perforant", "tranchant"])
        form.addRow("Type de dégâts:", self.damage_type_combo)
        
        self.weight_edit = QLineEdit()
        self.weight_edit.setPlaceholderText("1 kg")
        form.addRow("Poids:", self.weight_edit)
        
        self.properties_edit = QLineEdit()
        self.properties_edit.setPlaceholderText("finesse, lancer, légère (séparés par des virgules)")
        form.addRow("Propriétés:", self.properties_edit)
        
        self.range_edit = QLineEdit()
        self.range_edit.setPlaceholderText("6/18")
        form.addRow("Portée:", self.range_edit)
        
        layout.addLayout(form)
    
    def _create_creature_form(self, layout: QVBoxLayout):
        """Crée un formulaire complet pour les créatures"""
        form = QFormLayout()
        
        # Nom
        self.name_edit = QLineEdit()
        form.addRow("Nom:", self.name_edit)
        
        # Niveau
        self.level_spin = QSpinBox()
        self.level_spin.setMinimum(0)
        self.level_spin.setMaximum(20)
        form.addRow("Niveau:", self.level_spin)
        
        # Type
        self.type_combo = QComboBox()
        self.type_combo.setEditable(True)
        self.type_combo.addItems(["vivante", "humanoid", "non-vivante", "végétative", "fiélon", "céleste", "dragon"])
        form.addRow("Type:", self.type_combo)
        
        # Taille
        self.size_combo = QComboBox()
        self.size_combo.setEditable(True)
        self.size_combo.addItems(["minuscule", "très petite", "petit", "moyen", "grand", "très grand"])
        form.addRow("Taille:", self.size_combo)
        
        # Classe d'armure
        self.ac_spin = QSpinBox()
        self.ac_spin.setMinimum(0)
        self.ac_spin.setMaximum(30)
        form.addRow("Classe d'armure (AC):", self.ac_spin)
        
        # Points de vie
        self.hp_spin = QSpinBox()
        self.hp_spin.setMinimum(1)
        self.hp_spin.setMaximum(1000)
        form.addRow("Points de vie (PV):", self.hp_spin)
        
        # Initiative
        self.initiative_spin = QSpinBox()
        self.initiative_spin.setMinimum(0)
        self.initiative_spin.setMaximum(30)
        form.addRow("Initiative:", self.initiative_spin)
        
        # Caractéristiques
        stats_label = QLabel("Caractéristiques:")
        stats_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        form.addRow(stats_label, QWidget())
        
        self.stats_edits = {}
        for stat_name in ["FOR", "DEX", "CON", "INT", "SAG", "CHA"]:
            spin = QSpinBox()
            spin.setMinimum(1)
            spin.setMaximum(30)
            spin.setValue(10)
            form.addRow(f"{stat_name}:", spin)
            self.stats_edits[stat_name] = spin
        
        # Archétype
        self.archetype_combo = QComboBox()
        self.archetype_combo.addItems(["inférieur", "standard", "rapide", "puissant"])
        form.addRow("Archétype:", self.archetype_combo)
        
        # Défi
        self.challenge_edit = QLineEdit()
        self.challenge_edit.setPlaceholderText("0, 1/2, 1, 2, etc.")
        form.addRow("Niveau de défi:", self.challenge_edit)
        
        layout.addLayout(form)
    
    def _create_location_form(self, layout: QVBoxLayout):
        """Crée un formulaire pour les lieux"""
        form = QFormLayout()
        
        # Nom
        self.name_edit = QLineEdit()
        form.addRow("Nom:", self.name_edit)
        
        # Type
        self.type_combo = QComboBox()
        self.type_combo.setEditable(True)
        self.type_combo.addItems([
            "Ville", "Forêt", "Donjon", "Temple", "Marché", "Château",
            "Caverne", "Port", "Bibliothèque", "Cimetière", "Tour", "Gouffre",
            "Taverne", "Maison", "Boutique", "Autre"
        ])
        form.addRow("Type:", self.type_combo)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        form.addRow("Description:", self.description_edit)
        
        layout.addLayout(form)
        
        # Image
        image_label = QLabel("Image:")
        layout.addWidget(image_label)
        entry_id = self.entry.id if self.entry else ""
        self.image_widget = ImageUploadWidget(
            project_service=self.project_service,
            entity_type="location",
            entity_id=entry_id,
            parent=self
        )
        layout.addWidget(self.image_widget)
        
        # Bestiaire (liste de PNJ/créatures)
        bestiary_group = QWidget()
        bestiary_layout = QVBoxLayout(bestiary_group)
        bestiary_layout.setContentsMargins(0, 0, 0, 0)
        
        bestiary_label = QLabel("Bestiaire (PNJ/Créatures):")
        bestiary_layout.addWidget(bestiary_label)
        
        # Liste des PNJ/créatures disponibles
        available_label = QLabel("Disponibles:")
        bestiary_layout.addWidget(available_label)
        
        self.available_npcs = QListWidget()
        self.available_npcs.setMaximumHeight(150)
        self.available_npcs.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        bestiary_layout.addWidget(self.available_npcs)
        
        # Boutons pour ajouter/retirer
        bestiary_btn_layout = QHBoxLayout()
        self.add_to_bestiary_btn = QPushButton("→ Ajouter")
        self.add_to_bestiary_btn.clicked.connect(self._add_to_bestiary)
        bestiary_btn_layout.addWidget(self.add_to_bestiary_btn)
        
        self.remove_from_bestiary_btn = QPushButton("← Retirer")
        self.remove_from_bestiary_btn.clicked.connect(self._remove_from_bestiary)
        bestiary_btn_layout.addWidget(self.remove_from_bestiary_btn)
        bestiary_layout.addLayout(bestiary_btn_layout)
        
        # Liste des PNJ/créatures dans le bestiaire
        selected_label = QLabel("Dans le bestiaire:")
        bestiary_layout.addWidget(selected_label)
        
        self.bestiary_list = QListWidget()
        self.bestiary_list.setMaximumHeight(150)
        self.bestiary_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        bestiary_layout.addWidget(self.bestiary_list)
        
        layout.addWidget(bestiary_group)
        
        # Charger les PNJ/créatures disponibles
        self._load_available_npcs()
    
    def _load_available_npcs(self):
        """Charge la liste des PNJ/créatures disponibles"""
        self.available_npcs.clear()
        
        if self.project_service and self.project_service.character_service:
            from ...models.character import CharacterType
            # Récupérer tous les PNJ et créatures
            npcs = self.project_service.character_service.get_characters_by_type(CharacterType.PNJ)
            creatures = self.project_service.character_service.get_characters_by_type(CharacterType.CREATURE)
            
            for char in npcs + creatures:
                char_type = "PNJ" if char.type == CharacterType.PNJ else "Créature"
                item = QListWidgetItem(f"{char.name} ({char_type})")
                item.setData(Qt.ItemDataRole.UserRole, char.id)
                self.available_npcs.addItem(item)
    
    def _add_to_bestiary(self):
        """Ajoute les PNJ/créatures sélectionnés au bestiaire"""
        selected_items = self.available_npcs.selectedItems()
        for item in selected_items:
            char_id = item.data(Qt.ItemDataRole.UserRole)
            # Vérifier qu'il n'est pas déjà dans le bestiaire
            existing_ids = [
                self.bestiary_list.item(i).data(Qt.ItemDataRole.UserRole)
                for i in range(self.bestiary_list.count())
            ]
            if char_id not in existing_ids:
                bestiary_item = QListWidgetItem(item.text())
                bestiary_item.setData(Qt.ItemDataRole.UserRole, char_id)
                self.bestiary_list.addItem(bestiary_item)
    
    def _remove_from_bestiary(self):
        """Retire les PNJ/créatures sélectionnés du bestiaire"""
        selected_items = self.bestiary_list.selectedItems()
        for item in selected_items:
            row = self.bestiary_list.row(item)
            self.bestiary_list.takeItem(row)
    
    def _load_entry(self):
        """Charge les données de l'entrée"""
        if not self.entry:
            return
        
        metadata = self.entry.metadata
        
        if self.bank_type == BankType.NAMES:
            self.name_edit.setText(self.entry.value)
            self.racial_origin_edit.setText(metadata.get('racial_origin', ''))
        
        elif self.bank_type == BankType.PROFESSIONS:
            self.name_edit.setText(self.entry.value)
            self.description_edit.setPlainText(metadata.get('description', ''))
            tools = metadata.get('tools', [])
            self.tools_edit.setText(', '.join(tools) if isinstance(tools, list) else str(tools))
            skills = metadata.get('skills', [])
            self.skills_edit.setText(', '.join(skills) if isinstance(skills, list) else str(skills))
        
        elif self.bank_type == BankType.ARMORS:
            self.name_edit.setText(self.entry.value)
            self.type_combo.setCurrentText(metadata.get('type', ''))
            self.ac_spin.setValue(metadata.get('ac', 10))
            self.ac_modifier_edit.setText(metadata.get('ac_modifier', ''))
            self.price_edit.setText(metadata.get('price', ''))
            self.weight_edit.setText(metadata.get('weight', ''))
            self.stealth_combo.setCurrentText(metadata.get('stealth', 'normal'))
        
        elif self.bank_type == BankType.TOOLS:
            self.name_edit.setText(self.entry.value)
            self.price_edit.setText(metadata.get('price', ''))
            self.weight_edit.setText(metadata.get('weight', ''))
        
        elif self.bank_type == BankType.TRINKETS:
            self.name_edit.setText(self.entry.value)
            self.price_edit.setText(metadata.get('price', ''))
            self.description_edit.setPlainText(metadata.get('description', ''))
        
        elif self.bank_type == BankType.WEAPONS:
            self.name_edit.setText(self.entry.value)
            self.type_combo.setCurrentText(metadata.get('type', ''))
            self.category_combo.setCurrentText(metadata.get('category', ''))
            self.price_edit.setText(metadata.get('price', ''))
            self.damage_edit.setText(metadata.get('damage', ''))
            self.damage_type_combo.setCurrentText(metadata.get('damage_type', ''))
            self.weight_edit.setText(metadata.get('weight', ''))
            properties = metadata.get('properties', [])
            self.properties_edit.setText(', '.join(properties) if isinstance(properties, list) else str(properties))
            self.range_edit.setText(metadata.get('range', ''))
        
        elif self.bank_type == BankType.CREATURES:
            self.name_edit.setText(self.entry.value)
            self.level_spin.setValue(metadata.get('level', 1))
            self.type_combo.setCurrentText(metadata.get('type', ''))
            self.size_combo.setCurrentText(metadata.get('size', ''))
            self.ac_spin.setValue(metadata.get('ac', 10))
            self.hp_spin.setValue(metadata.get('hp', 1))
            self.initiative_spin.setValue(metadata.get('initiative', 10))
            
            stats = metadata.get('stats', {})
            stat_map = {
                'FOR': 'strength',
                'DEX': 'dexterity',
                'CON': 'constitution',
                'INT': 'intelligence',
                'SAG': 'wisdom',
                'CHA': 'charisma'
            }
            for stat_key, stat_attr in stat_map.items():
                if stat_key in self.stats_edits:
                    self.stats_edits[stat_key].setValue(stats.get(stat_attr, 10))
            
            self.archetype_combo.setCurrentText(metadata.get('archetype', 'standard'))
            self.challenge_edit.setText(str(metadata.get('challenge', '0')))
        
        elif self.bank_type == BankType.LOCATIONS:
            self.name_edit.setText(self.entry.value)
            self.type_combo.setCurrentText(metadata.get('type', ''))
            self.description_edit.setPlainText(metadata.get('description', ''))
            
            # Charger le bestiaire
            self.bestiary_list.clear()
            bestiary_ids = metadata.get('bestiary', [])
            
            if self.project_service and self.project_service.character_service:
                from ...models.character import CharacterType
                for char_id in bestiary_ids:
                    char = self.project_service.character_service.get_character(char_id)
                    if char:
                        char_type = "PNJ" if char.type == CharacterType.PNJ else "Créature"
                        item = QListWidgetItem(f"{char.name} ({char_type})")
                        item.setData(Qt.ItemDataRole.UserRole, char_id)
                        self.bestiary_list.addItem(item)
            
            # Charger l'image
            image_id = metadata.get('image_id')
            if image_id and hasattr(self, 'image_widget'):
                self.image_widget.set_image_id(image_id)
                if not self.image_widget.entity_id:
                    self.image_widget.entity_id = self.entry.id
        
        elif self.bank_type == BankType.FACTIONS:
            self.name_edit.setText(self.entry.value)
            self.description_edit.setPlainText(metadata.get('description', ''))
            
            # Charger l'image
            image_id = metadata.get('image_id')
            if image_id and hasattr(self, 'image_widget'):
                self.image_widget.set_image_id(image_id)
                if not self.image_widget.entity_id:
                    self.image_widget.entity_id = self.entry.id
        
        else:
            self.value_edit.setText(self.entry.value)
    
    def get_entry_data(self) -> tuple[str, dict]:
        """
        Récupère les données de l'entrée
        
        Returns:
            Tuple (value, metadata)
        """
        if self.bank_type == BankType.NAMES:
            value = self.name_edit.text().strip()
            if not value:
                raise ValueError("Le nom est obligatoire")
            metadata = {
                'racial_origin': self.racial_origin_edit.text().strip()
            }
            return value, metadata
        
        elif self.bank_type == BankType.PROFESSIONS:
            value = self.name_edit.text().strip()
            if not value:
                raise ValueError("Le nom de la profession est obligatoire")
            tools_str = self.tools_edit.text().strip()
            tools = [t.strip() for t in tools_str.split(',') if t.strip()] if tools_str else []
            skills_str = self.skills_edit.text().strip()
            skills = [s.strip() for s in skills_str.split(',') if s.strip()] if skills_str else []
            metadata = {
                'description': self.description_edit.toPlainText().strip(),
                'tools': tools,
                'skills': skills
            }
            return value, metadata
        
        elif self.bank_type == BankType.ARMORS:
            value = self.name_edit.text().strip()
            if not value:
                raise ValueError("Le nom de l'armure est obligatoire")
            metadata = {
                'type': self.type_combo.currentText().strip(),
                'ac': self.ac_spin.value(),
                'ac_modifier': self.ac_modifier_edit.text().strip(),
                'price': self.price_edit.text().strip(),
                'weight': self.weight_edit.text().strip(),
                'stealth': self.stealth_combo.currentText()
            }
            return value, metadata
        
        elif self.bank_type == BankType.TOOLS:
            value = self.name_edit.text().strip()
            if not value:
                raise ValueError("Le nom de l'outil est obligatoire")
            metadata = {
                'price': self.price_edit.text().strip(),
                'weight': self.weight_edit.text().strip()
            }
            return value, metadata
        
        elif self.bank_type == BankType.TRINKETS:
            value = self.name_edit.text().strip()
            if not value:
                raise ValueError("Le nom de la babiole est obligatoire")
            metadata = {
                'price': self.price_edit.text().strip(),
                'description': self.description_edit.toPlainText().strip()
            }
            return value, metadata
        
        elif self.bank_type == BankType.WEAPONS:
            value = self.name_edit.text().strip()
            if not value:
                raise ValueError("Le nom de l'arme est obligatoire")
            properties_str = self.properties_edit.text().strip()
            properties = [p.strip() for p in properties_str.split(',') if p.strip()] if properties_str else []
            metadata = {
                'type': self.type_combo.currentText().strip(),
                'category': self.category_combo.currentText().strip(),
                'price': self.price_edit.text().strip(),
                'damage': self.damage_edit.text().strip(),
                'damage_type': self.damage_type_combo.currentText().strip(),
                'weight': self.weight_edit.text().strip(),
                'properties': properties,
                'range': self.range_edit.text().strip()
            }
            return value, metadata
        
        elif self.bank_type == BankType.CREATURES:
            value = self.name_edit.text().strip()
            if not value:
                raise ValueError("Le nom de la créature est obligatoire")
            
            metadata = {
                'level': self.level_spin.value(),
                'type': self.type_combo.currentText().strip(),
                'size': self.size_combo.currentText().strip(),
                'ac': self.ac_spin.value(),
                'hp': self.hp_spin.value(),
                'initiative': self.initiative_spin.value(),
                'stats': {
                    'strength': self.stats_edits['FOR'].value(),
                    'dexterity': self.stats_edits['DEX'].value(),
                    'constitution': self.stats_edits['CON'].value(),
                    'intelligence': self.stats_edits['INT'].value(),
                    'wisdom': self.stats_edits['SAG'].value(),
                    'charisma': self.stats_edits['CHA'].value()
                },
                'archetype': self.archetype_combo.currentText(),
                'challenge': self.challenge_edit.text().strip() or '0'
            }
            return value, metadata
        
        elif self.bank_type == BankType.LOCATIONS:
            value = self.name_edit.text().strip()
            if not value:
                raise ValueError("Le nom du lieu est obligatoire")
            
            # Récupérer les IDs du bestiaire
            bestiary_ids = [
                self.bestiary_list.item(i).data(Qt.ItemDataRole.UserRole)
                for i in range(self.bestiary_list.count())
            ]
            
            metadata = {
                'type': self.type_combo.currentText().strip(),
                'description': self.description_edit.toPlainText().strip(),
                'bestiary': bestiary_ids
            }
            # Ajouter l'image_id si le widget existe
            if hasattr(self, 'image_widget'):
                image_id = self.image_widget.get_image_id()
                if image_id:
                    metadata['image_id'] = image_id
            return value, metadata
        
        elif self.bank_type == BankType.FACTIONS:
            value = self.name_edit.text().strip()
            if not value:
                raise ValueError("Le nom de la faction est obligatoire")
            metadata = {
                'description': self.description_edit.toPlainText().strip()
            }
            # Ajouter l'image_id si le widget existe
            if hasattr(self, 'image_widget'):
                image_id = self.image_widget.get_image_id()
                if image_id:
                    metadata['image_id'] = image_id
            return value, metadata
        
        else:
            value = self.value_edit.text().strip()
            if not value:
                raise ValueError("La valeur est obligatoire")
            return value, {}
