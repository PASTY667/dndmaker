"""
Éditeur d'entrée de banque de données
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QSpinBox, QComboBox, QFormLayout,
    QWidget, QMessageBox, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt

from ...models.bank import BankType, BankEntry
from ...core.logger import get_logger

logger = get_logger()


class BankEntryEditor(QDialog):
    """Éditeur d'entrée de banque de données"""
    
    def __init__(self, bank_type: BankType, entry: BankEntry = None, parent=None):
        """
        Crée un éditeur d'entrée
        
        Args:
            bank_type: Type de banque
            entry: Entrée existante (None pour une nouvelle entrée)
            parent: Widget parent
        """
        super().__init__(parent)
        self.bank_type = bank_type
        self.entry = entry
        self.is_new = entry is None
        
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
        
        else:
            value = self.value_edit.text().strip()
            if not value:
                raise ValueError("La valeur est obligatoire")
            return value, {}
