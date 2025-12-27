"""
Éditeur de table personnalisée
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QSpinBox, QComboBox, QFormLayout,
    QWidget, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox
)
from PyQt6.QtCore import Qt

from ...models.custom_table import CustomTable, TableField
from ...core.logger import get_logger
from ...core.i18n import tr

logger = get_logger()


class TableEditor(QDialog):
    """Éditeur de table personnalisée"""
    
    def __init__(self, table: CustomTable = None, project_service=None, parent=None):
        """
        Crée un éditeur de table
        
        Args:
            table: Table existante (None pour une nouvelle table)
            project_service: Service de projet
            parent: Widget parent
        """
        super().__init__(parent)
        self.table = table
        self.project_service = project_service
        self.is_new = table is None
        
        if self.is_new:
            self.setWindowTitle(tr("table.new_table"))
        else:
            self.setWindowTitle(tr("table.edit_table"))
        
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        self._init_ui()
        
        if not self.is_new:
            self._load_table()
    
    def _init_ui(self):
        """Initialise l'interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
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
        add_field_btn.clicked.connect(self._add_field)
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
        add_row_btn.clicked.connect(self._add_row)
        rows_btn_layout.addWidget(add_row_btn)
        
        delete_row_btn = QPushButton(tr("table.delete_row"))
        delete_row_btn.clicked.connect(self._delete_row)
        rows_btn_layout.addWidget(delete_row_btn)
        
        rows_btn_layout.addStretch()
        rows_layout.addLayout(rows_btn_layout)
        
        layout.addWidget(rows_group)
        
        # Boutons de dialogue
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton(tr("msg.save"))
        save_btn.clicked.connect(self._save)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton(tr("msg.cancel"))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _add_field(self):
        """Ajoute un nouveau champ au schéma"""
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
        remove_btn.clicked.connect(lambda: self._remove_field(row))
        self.fields_table.setCellWidget(row, 2, remove_btn)
    
    def _remove_field(self, row: int):
        """Supprime un champ du schéma"""
        self.fields_table.removeRow(row)
        # Réindexer les boutons de suppression
        for i in range(self.fields_table.rowCount()):
            remove_btn = self.fields_table.cellWidget(i, 2)
            if remove_btn:
                remove_btn.clicked.disconnect()
                remove_btn.clicked.connect(lambda checked, r=i: self._remove_field(r))
    
    def _add_row(self):
        """Ajoute une nouvelle ligne de données"""
        # Récupérer le schéma depuis les champs définis
        schema = self._get_schema()
        
        if not schema:
            QMessageBox.warning(self, tr("msg.warning"), tr("table.no_fields"))
            return
        
        # Mettre à jour les colonnes du tableau si nécessaire
        if self.rows_table.columnCount() != len(schema):
            self.rows_table.setColumnCount(len(schema))
            self.rows_table.setHorizontalHeaderLabels([f.name for f in schema])
        
        row = self.rows_table.rowCount()
        self.rows_table.insertRow(row)
        
        # Créer un widget d'édition pour chaque champ
        for col, field in enumerate(schema):
            if field.field_type == 'number':
                widget = QSpinBox()
                widget.setMinimum(-999999)
                widget.setMaximum(999999)
            elif field.field_type == 'boolean':
                widget = QComboBox()
                widget.addItems(['False', 'True'])
            else:  # string ou date
                widget = QLineEdit()
                if field.field_type == 'date':
                    widget.setPlaceholderText("YYYY-MM-DD")
            
            self.rows_table.setCellWidget(row, col, widget)
    
    def _delete_row(self):
        """Supprime la ligne sélectionnée"""
        current_row = self.rows_table.currentRow()
        if current_row >= 0:
            self.rows_table.removeRow(current_row)
        else:
            QMessageBox.information(self, tr("msg.info"), "Sélectionnez une ligne à supprimer")
    
    def _get_schema(self) -> list[TableField]:
        """Récupère le schéma depuis l'interface"""
        schema = []
        type_map = {
            tr("table.string"): 'string',
            tr("table.number"): 'number',
            tr("table.boolean"): 'boolean',
            tr("table.date"): 'date'
        }
        
        for row in range(self.fields_table.rowCount()):
            name_widget = self.fields_table.cellWidget(row, 0)
            type_widget = self.fields_table.cellWidget(row, 1)
            
            if name_widget and type_widget:
                field_name = name_widget.text().strip()
                if field_name:
                    field_type_text = type_widget.currentText()
                    field_type = type_map.get(field_type_text, 'string')
                    schema.append(TableField(name=field_name, field_type=field_type))
        
        return schema
    
    def _load_table(self):
        """Charge les données de la table"""
        if not self.table:
            return
        
        self.table_name_edit.setText(self.table.name)
        
        # Charger le schéma
        type_map = {
            'string': tr("table.string"),
            'number': tr("table.number"),
            'boolean': tr("table.boolean"),
            'date': tr("table.date")
        }
        
        for field in self.table.schema:
            row = self.fields_table.rowCount()
            self.fields_table.insertRow(row)
            
            name_edit = QLineEdit()
            name_edit.setText(field.name)
            self.fields_table.setCellWidget(row, 0, name_edit)
            
            type_combo = QComboBox()
            type_combo.addItems([tr("table.string"), tr("table.number"), tr("table.boolean"), tr("table.date")])
            field_type_text = type_map.get(field.field_type, tr("table.string"))
            type_combo.setCurrentText(field_type_text)
            self.fields_table.setCellWidget(row, 1, type_combo)
            
            remove_btn = QPushButton(tr("table.remove_field"))
            remove_btn.clicked.connect(lambda checked, r=row: self._remove_field(r))
            self.fields_table.setCellWidget(row, 2, remove_btn)
        
        # Charger les lignes
        if self.table.schema:
            self.rows_table.setColumnCount(len(self.table.schema))
            self.rows_table.setHorizontalHeaderLabels([f.name for f in self.table.schema])
            
            for row_data in self.table.rows:
                row = self.rows_table.rowCount()
                self.rows_table.insertRow(row)
                
                for col, field in enumerate(self.table.schema):
                    value = row_data.get(field.name, '')
                    
                    if field.field_type == 'number':
                        widget = QSpinBox()
                        widget.setMinimum(-999999)
                        widget.setMaximum(999999)
                        try:
                            widget.setValue(int(value))
                        except (ValueError, TypeError):
                            widget.setValue(0)
                    elif field.field_type == 'boolean':
                        widget = QComboBox()
                        widget.addItems(['False', 'True'])
                        widget.setCurrentIndex(1 if value else 0)
                    else:  # string ou date
                        widget = QLineEdit()
                        widget.setText(str(value))
                        if field.field_type == 'date':
                            widget.setPlaceholderText("YYYY-MM-DD")
                    
                    self.rows_table.setCellWidget(row, col, widget)
    
    def _save(self):
        """Sauvegarde la table"""
        from datetime import datetime
        from ...core.utils import generate_id
        
        name = self.table_name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, tr("msg.warning"), tr("table.name_required"))
            return
        
        schema = self._get_schema()
        if not schema:
            QMessageBox.warning(self, tr("msg.warning"), tr("table.schema_required"))
            return
        
        # Récupérer les lignes
        rows = []
        for row_idx in range(self.rows_table.rowCount()):
            row_data = {}
            for col_idx, field in enumerate(schema):
                widget = self.rows_table.cellWidget(row_idx, col_idx)
                if widget:
                    if field.field_type == 'number':
                        value = widget.value()
                    elif field.field_type == 'boolean':
                        value = widget.currentIndex() == 1
                    else:  # string ou date
                        value = widget.text().strip()
                    
                    row_data[field.name] = value
            if row_data:  # Ne pas ajouter de lignes vides
                rows.append(row_data)
        
        # Créer ou mettre à jour la table
        if self.is_new:
            self.table = CustomTable(
                id=generate_id(),
                name=name,
                schema=schema,
                rows=rows,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            if self.project_service and self.project_service.table_service:
                self.project_service.table_service._tables[self.table.id] = self.table
        else:
            self.table.name = name
            self.table.schema = schema
            self.table.rows = rows
            self.table.updated_at = datetime.now()
            if self.project_service and self.project_service.table_service:
                self.project_service.table_service.update_table(self.table)
        
        # Sauvegarder le projet
        if self.project_service:
            self.project_service.save_project()
        
        self.accept()

