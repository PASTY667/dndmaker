"""
Vue des banques de données
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QTabWidget, QDialog, QHeaderView
)
from PyQt6.QtCore import Qt

from ...services.project_service import ProjectService
from ...models.bank import BankType, BankEntry
from ...core.logger import UserActionLogger
from ...core.i18n import tr
from ..widgets.bank_entry_editor import BankEntryEditor
from ..widgets.table_editor import TableEditor

logger = UserActionLogger()


class BanksView(QWidget):
    """Vue des banques de données"""
    
    def __init__(self, project_service: ProjectService, parent=None):
        super().__init__(parent)
        self.project_service = project_service
        self.custom_table_tabs = {}  # {table_id: tab_index}
        self._init_ui()
        # Rafraîchir après l'initialisation pour charger les données
        self.refresh()
    
    def _init_ui(self):
        """Initialise l'interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Titre
        self.title_label = QLabel(tr("bank.title"))
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.title_label)
        
        # Bouton pour ajouter une table personnalisée
        table_btn_layout = QHBoxLayout()
        table_btn_layout.addStretch()
        add_table_btn = QPushButton(tr("table.add_table"))
        add_table_btn.clicked.connect(self._add_custom_table)
        table_btn_layout.addWidget(add_table_btn)
        layout.addLayout(table_btn_layout)
        
        # Onglets pour chaque type de banque
        self.tabs = QTabWidget()
        for bank_type in BankType:
            self.tabs.addTab(self._create_bank_tab(bank_type), bank_type.value)
        layout.addWidget(self.tabs)
        
        # Dictionnaire pour stocker les IDs des tables et leurs index d'onglets
        self.custom_table_tabs = {}  # {table_id: tab_index}
    
    def _get_table_columns(self, bank_type: BankType) -> list[str]:
        """Retourne les colonnes pour un type de banque"""
        if bank_type == BankType.NAMES:
            return ["Nom", "Origine raciale"]
        elif bank_type == BankType.CREATURES:
            return ["Nom", "Niveau", "Type", "Taille", "AC", "PV", "Initiative", "Archétype", "Défi"]
        elif bank_type == BankType.PROFESSIONS:
            return ["Nom", "Description", "Outils", "Compétences"]
        elif bank_type == BankType.ARMORS:
            return ["Nom", "Type", "AC", "Mod. AC", "Prix", "Poids", "Furtivité"]
        elif bank_type == BankType.TOOLS:
            return ["Nom", "Prix", "Poids"]
        elif bank_type == BankType.TRINKETS:
            return ["Nom", "Prix", "Description"]
        elif bank_type == BankType.WEAPONS:
            return ["Nom", "Type", "Catégorie", "Dégâts", "Type dégâts", "Prix", "Poids", "Propriétés", "Portée"]
        elif bank_type == BankType.LOCATIONS:
            return ["Nom", "Type", "Description", "Bestiaire"]
        elif bank_type == BankType.FACTIONS:
            return ["Nom", "Description"]
        else:
            return ["Valeur"]
    
    def _create_bank_tab(self, bank_type: BankType) -> QWidget:
        """Crée un onglet pour un type de banque"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        
        # Bouton Ajouter (ouvre un formulaire)
        add_btn = QPushButton("Ajouter")
        add_btn.clicked.connect(lambda: self._add_entry(bank_type))
        layout.addWidget(add_btn)
        
        # Tableau des entrées
        columns = self._get_table_columns(bank_type)
        table = QTableWidget()
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        table.itemDoubleClicked.connect(lambda: self._edit_entry(bank_type))
        layout.addWidget(table)
        
        # Boutons
        button_layout = QHBoxLayout()
        
        edit_btn = QPushButton("Modifier")
        edit_btn.clicked.connect(lambda: self._edit_entry(bank_type))
        edit_btn.setEnabled(False)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Supprimer")
        delete_btn.clicked.connect(lambda: self._delete_entry(bank_type))
        delete_btn.setEnabled(False)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Stocker les références
        setattr(widget, 'table', table)
        setattr(widget, 'bank_type', bank_type)
        setattr(widget, 'edit_btn', edit_btn)
        setattr(widget, 'delete_btn', delete_btn)
        
        def on_selection_changed():
            has_selection = len(table.selectedItems()) > 0
            edit_btn.setEnabled(has_selection)
            delete_btn.setEnabled(has_selection)
        
        table.itemSelectionChanged.connect(on_selection_changed)
        
        return widget
    
    def refresh(self):
        """Rafraîchit la vue"""
        if not self.project_service.bank_service:
            return
        
        # S'assurer que les banques sont initialisées avec les données JSON
        from ...core.data_loader import DataLoader
        DataLoader.initialize_banks(self.project_service.bank_service)
        
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            table = getattr(widget, 'table', None)
            bank_type = getattr(widget, 'bank_type', None)
            
            if table and bank_type:
                table.setRowCount(0)
                bank = self.project_service.bank_service.get_bank_by_type(bank_type)
                if bank:
                    columns = self._get_table_columns(bank_type)
                    for entry in bank.entries:
                        row = table.rowCount()
                        table.insertRow(row)
                        self._populate_table_row(table, row, entry, bank_type, columns)
        
        # Rafraîchir les tables personnalisées (créer/mettre à jour les onglets)
        if self.project_service.table_service:
            tables = self.project_service.table_service.get_all_tables()
            num_standard_tabs = len(BankType)
            
            # Supprimer tous les onglets de tables existants (en ordre décroissant)
            tabs_to_remove = []
            for i in range(self.tabs.count() - 1, num_standard_tabs - 1, -1):
                tabs_to_remove.append(i)
            for tab_index in tabs_to_remove:
                self.tabs.removeTab(tab_index)
            
            # Réinitialiser le mapping
            self.custom_table_tabs = {}
            
            # Recréer les onglets pour toutes les tables
            for idx, table in enumerate(tables):
                tab_widget = self._create_custom_table_tab(table)
                tab_index = self.tabs.addTab(tab_widget, table.name)
                self.custom_table_tabs[table.id] = tab_index
    
    def _populate_table_row(self, table: QTableWidget, row: int, entry: BankEntry, bank_type: BankType, columns: list[str]):
        """Remplit une ligne du tableau avec les données d'une entrée"""
        metadata = entry.metadata
        
        if bank_type == BankType.NAMES:
            table.setItem(row, 0, QTableWidgetItem(entry.value))
            table.setItem(row, 1, QTableWidgetItem(metadata.get('racial_origin', '')))
        
        elif bank_type == BankType.CREATURES:
            stats = metadata.get('stats', {})
            table.setItem(row, 0, QTableWidgetItem(entry.value))
            table.setItem(row, 1, QTableWidgetItem(str(metadata.get('level', 0))))
            table.setItem(row, 2, QTableWidgetItem(metadata.get('type', '')))
            table.setItem(row, 3, QTableWidgetItem(metadata.get('size', '')))
            table.setItem(row, 4, QTableWidgetItem(str(metadata.get('ac', 10))))
            table.setItem(row, 5, QTableWidgetItem(str(metadata.get('hp', 1))))
            table.setItem(row, 6, QTableWidgetItem(str(metadata.get('initiative', 10))))
            table.setItem(row, 7, QTableWidgetItem(metadata.get('archetype', 'standard')))
            table.setItem(row, 8, QTableWidgetItem(str(metadata.get('challenge', '0'))))
        
        elif bank_type == BankType.PROFESSIONS:
            tools = metadata.get('tools', [])
            skills = metadata.get('skills', [])
            table.setItem(row, 0, QTableWidgetItem(entry.value))
            table.setItem(row, 1, QTableWidgetItem(metadata.get('description', '')))
            table.setItem(row, 2, QTableWidgetItem(', '.join(tools) if isinstance(tools, list) else str(tools)))
            table.setItem(row, 3, QTableWidgetItem(', '.join(skills) if isinstance(skills, list) else str(skills)))
        
        elif bank_type == BankType.ARMORS:
            table.setItem(row, 0, QTableWidgetItem(entry.value))
            table.setItem(row, 1, QTableWidgetItem(metadata.get('type', '')))
            table.setItem(row, 2, QTableWidgetItem(str(metadata.get('ac', 10))))
            table.setItem(row, 3, QTableWidgetItem(metadata.get('ac_modifier', '')))
            table.setItem(row, 4, QTableWidgetItem(metadata.get('price', '')))
            table.setItem(row, 5, QTableWidgetItem(metadata.get('weight', '')))
            table.setItem(row, 6, QTableWidgetItem(metadata.get('stealth', 'normal')))
        
        elif bank_type == BankType.TOOLS:
            table.setItem(row, 0, QTableWidgetItem(entry.value))
            table.setItem(row, 1, QTableWidgetItem(metadata.get('price', '')))
            table.setItem(row, 2, QTableWidgetItem(metadata.get('weight', '')))
        
        elif bank_type == BankType.TRINKETS:
            table.setItem(row, 0, QTableWidgetItem(entry.value))
            table.setItem(row, 1, QTableWidgetItem(metadata.get('price', '')))
            desc = metadata.get('description', '')
            # Tronquer la description si trop longue
            if len(desc) > 50:
                desc = desc[:47] + "..."
            table.setItem(row, 2, QTableWidgetItem(desc))
        
        elif bank_type == BankType.LOCATIONS:
            table.setItem(row, 0, QTableWidgetItem(entry.value))
            table.setItem(row, 1, QTableWidgetItem(metadata.get('type', '')))
            desc = metadata.get('description', '')
            # Tronquer la description si trop longue
            if len(desc) > 50:
                desc = desc[:47] + "..."
            table.setItem(row, 2, QTableWidgetItem(desc))
            # Afficher le nombre de PNJ/créatures dans le bestiaire
            bestiary = metadata.get('bestiary', [])
            bestiary_count = len(bestiary) if isinstance(bestiary, list) else 0
            table.setItem(row, 3, QTableWidgetItem(f"{bestiary_count} PNJ/Créature(s)"))
        
        elif bank_type == BankType.FACTIONS:
            table.setItem(row, 0, QTableWidgetItem(entry.value))
            desc = metadata.get('description', '')
            if len(desc) > 100:
                desc = desc[:97] + "..."
            table.setItem(row, 1, QTableWidgetItem(desc))
        
        elif bank_type == BankType.WEAPONS:
            properties = metadata.get('properties', [])
            table.setItem(row, 0, QTableWidgetItem(entry.value))
            table.setItem(row, 1, QTableWidgetItem(metadata.get('type', '')))
            table.setItem(row, 2, QTableWidgetItem(metadata.get('category', '')))
            table.setItem(row, 3, QTableWidgetItem(metadata.get('damage', '')))
            table.setItem(row, 4, QTableWidgetItem(metadata.get('damage_type', '')))
            table.setItem(row, 5, QTableWidgetItem(metadata.get('price', '')))
            table.setItem(row, 6, QTableWidgetItem(metadata.get('weight', '')))
            table.setItem(row, 7, QTableWidgetItem(', '.join(properties) if isinstance(properties, list) else str(properties)))
            table.setItem(row, 8, QTableWidgetItem(metadata.get('range', '')))
        
        else:
            table.setItem(row, 0, QTableWidgetItem(entry.value))
        
        # Stocker l'ID de l'entrée dans le premier item pour pouvoir le récupérer
        for col in range(len(columns)):
            item = table.item(row, col)
            if item:
                item.setData(Qt.ItemDataRole.UserRole, entry.id)
    
    def _add_entry(self, bank_type: BankType):
        """Ajoute une entrée à une banque via un formulaire"""
        if not self.project_service.get_current_project():
            QMessageBox.warning(self, "Attention", "Veuillez ouvrir ou créer un projet avant d'ajouter une entrée.")
            return
        
        try:
            # Ouvrir le formulaire d'édition
            editor = BankEntryEditor(bank_type, entry=None, parent=self, project_service=self.project_service)
            if editor.exec() == QDialog.DialogCode.Accepted:
                value, metadata = editor.get_entry_data()
                
                # Vérifier qu'il n'existe pas déjà
                bank = self.project_service.bank_service.get_or_create_bank(bank_type)
                existing_values = [e.value for e in bank.entries]
                if value in existing_values:
                    QMessageBox.warning(self, "Attention", f"L'entrée '{value}' existe déjà dans cette banque.")
                    return
                
                # Ajouter l'entrée
                self.project_service.bank_service.add_entry_to_bank(bank.id, value, metadata)
                self.project_service.save_project(f"Ajout d'entrée dans {bank_type.value}")
                self.refresh()
                logger.log_bank_action("Ajoutée", bank_type=bank_type.value, entry_value=value)
        except ValueError as e:
            QMessageBox.warning(self, "Erreur de validation", str(e))
        except Exception as e:
            logger.exception(f"Erreur lors de l'ajout d'entrée: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def _edit_entry(self, bank_type: BankType):
        """Modifie une entrée via un formulaire"""
        if not self.project_service.get_current_project():
            QMessageBox.warning(self, "Attention", "Veuillez ouvrir ou créer un projet avant de modifier une entrée.")
            return
        
        widget = self.tabs.currentWidget()
        table = getattr(widget, 'table', None)
        if not table:
            return
        
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "Information", "Veuillez sélectionner une entrée à modifier.")
            return
        
        try:
            # Récupérer l'ID de l'entrée depuis le premier item de la ligne
            entry_id = table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
            bank = self.project_service.bank_service.get_bank_by_type(bank_type)
            
            if not bank:
                QMessageBox.warning(self, "Erreur", "Banque introuvable")
                return
            
            # Trouver l'entrée
            entry = next((e for e in bank.entries if e.id == entry_id), None)
            if not entry:
                QMessageBox.warning(self, "Erreur", "Entrée introuvable")
                return
            
            # Ouvrir le formulaire d'édition
            editor = BankEntryEditor(bank_type, entry=entry, parent=self, project_service=self.project_service)
            if editor.exec() == QDialog.DialogCode.Accepted:
                new_value, new_metadata = editor.get_entry_data()
                
                # Vérifier qu'il n'existe pas déjà (sauf si c'est la même entrée)
                existing_values = [e.value for e in bank.entries if e.id != entry_id]
                if new_value in existing_values:
                    QMessageBox.warning(self, "Attention", f"L'entrée '{new_value}' existe déjà dans cette banque.")
                    return
                
                # Mettre à jour l'entrée
                entry.value = new_value
                entry.metadata = new_metadata
                
                self.project_service.bank_service.update_bank(bank)
                self.project_service.save_project(f"Modification d'entrée dans {bank_type.value}")
                self.refresh()
                logger.log_bank_action("Modifiée", bank_type=bank_type.value, entry_value=new_value)
        except ValueError as e:
            QMessageBox.warning(self, "Erreur de validation", str(e))
        except Exception as e:
            logger.exception(f"Erreur lors de la modification d'entrée: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def _delete_entry(self, bank_type: BankType):
        """Supprime une entrée"""
        widget = self.tabs.currentWidget()
        table = getattr(widget, 'table', None)
        if not table:
            return
        
        current_row = table.currentRow()
        if current_row < 0:
            return
        
        # Confirmation
        reply = QMessageBox.question(
            self, "Confirmation",
            "Êtes-vous sûr de vouloir supprimer cette entrée ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            # Récupérer l'ID de l'entrée depuis le premier item de la ligne
            entry_id = table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
            bank = self.project_service.bank_service.get_bank_by_type(bank_type)
            
            if bank:
                if self.project_service.bank_service.remove_entry_from_bank(bank.id, entry_id):
                    self.project_service.save_project(f"Suppression d'entrée dans {bank_type.value}")
                    self.refresh()
                    logger.log_bank_action("Supprimée", bank_type=bank_type.value)
        except Exception as e:
            logger.exception(f"Erreur lors de la suppression d'entrée: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def _add_custom_table(self):
        """Ajoute une nouvelle table personnalisée"""
        editor = TableEditor(project_service=self.project_service, parent=self)
        if editor.exec() == QDialog.DialogCode.Accepted:
            self.refresh()
    
    def _create_custom_table_tab(self, table) -> QWidget:
        """Crée un onglet pour une table personnalisée"""
        from ...models.custom_table import CustomTable
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        
        # Boutons
        button_layout = QHBoxLayout()
        
        edit_btn = QPushButton(tr("table.edit"))
        edit_btn.clicked.connect(lambda: self._edit_custom_table_from_tab(table.id))
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton(tr("table.delete"))
        delete_btn.clicked.connect(lambda: self._delete_custom_table_from_tab(table.id))
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Tableau des lignes
        data_table = QTableWidget()
        data_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        data_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        data_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        data_table.setAlternatingRowColors(True)
        data_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(data_table)
        
        # Stocker les références
        setattr(widget, 'data_table', data_table)
        setattr(widget, 'table_id', table.id)
        
        # Remplir le tableau
        self._refresh_custom_table_tab(widget, table)
        
        return widget
    
    def _refresh_custom_table_tab(self, widget: QWidget, table):
        """Rafraîchit le contenu d'un onglet de table personnalisée"""
        data_table = getattr(widget, 'data_table', None)
        if not data_table:
            return
        
        # Définir les colonnes selon le schéma
        columns = [field.name for field in table.schema]
        data_table.setColumnCount(len(columns))
        data_table.setHorizontalHeaderLabels(columns)
        
        # Remplir avec les lignes
        data_table.setRowCount(0)
        for row_data in table.rows:
            row = data_table.rowCount()
            data_table.insertRow(row)
            
            for col, field in enumerate(table.schema):
                value = row_data.get(field.name, '')
                # Convertir selon le type
                if field.field_type == 'boolean':
                    display_value = tr("btn.yes") if value else tr("btn.no")
                else:
                    display_value = str(value)
                
                data_table.setItem(row, col, QTableWidgetItem(display_value))
    
    def _edit_custom_table_from_tab(self, table_id: str):
        """Modifie une table depuis son onglet"""
        if not self.project_service.table_service:
            return
        
        table = self.project_service.table_service.get_table(table_id)
        if not table:
            return
        
        editor = TableEditor(table=table, project_service=self.project_service, parent=self)
        if editor.exec() == QDialog.DialogCode.Accepted:
            self.refresh()
    
    def _delete_custom_table_from_tab(self, table_id: str):
        """Supprime une table depuis son onglet"""
        if not self.project_service.table_service:
            return
        
        table = self.project_service.table_service.get_table(table_id)
        if not table:
            return
        
        # Confirmation
        reply = QMessageBox.question(
            self, tr("msg.confirm"),
            f"Êtes-vous sûr de vouloir supprimer la table '{table.name}' ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        if self.project_service.table_service.delete_table(table_id):
            self.project_service.save_project(f"Suppression de la table '{table.name}'")
            self.refresh()
    
    def on_language_changed(self):
        """Met à jour les textes lors du changement de langue"""
        self.title_label.setText(tr("bank.title"))
        self.refresh()
