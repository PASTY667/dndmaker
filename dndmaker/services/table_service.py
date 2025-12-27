"""
Service de gestion des tables personnalisées
"""

from typing import List, Optional
from datetime import datetime

from ..models.custom_table import CustomTable, TableField
from ..core.utils import generate_id


class TableService:
    """Service de gestion des tables personnalisées"""
    
    def __init__(self, project_service):
        """Initialise le service avec une référence au ProjectService"""
        self.project_service = project_service
        self._tables: dict[str, CustomTable] = {}
    
    def load_tables(self, tables_data: List[dict]) -> None:
        """Charge les tables depuis les données du projet"""
        self._tables = {}
        for table_data in tables_data:
            table = self._deserialize_table(table_data)
            self._tables[table.id] = table
    
    def create_table(self, name: str) -> CustomTable:
        """Crée une nouvelle table"""
        table = CustomTable(
            id=generate_id(),
            name=name,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self._tables[table.id] = table
        return table
    
    def get_table(self, table_id: str) -> Optional[CustomTable]:
        """Récupère une table par son ID"""
        return self._tables.get(table_id)
    
    def get_all_tables(self) -> List[CustomTable]:
        """Récupère toutes les tables"""
        return list(self._tables.values())
    
    def update_table(self, table: CustomTable) -> None:
        """Met à jour une table"""
        if table.id not in self._tables:
            raise ValueError(f"Table {table.id} introuvable")
        table.updated_at = datetime.now()
        self._tables[table.id] = table
    
    def delete_table(self, table_id: str) -> bool:
        """Supprime une table"""
        if table_id not in self._tables:
            return False
        del self._tables[table_id]
        return True
    
    def _deserialize_table(self, data: dict) -> CustomTable:
        """Désérialise une table depuis un dictionnaire"""
        schema = []
        for field_data in data.get('schema', []):
            schema.append(TableField(
                name=field_data.get('name', ''),
                field_type=field_data.get('type', 'string')
            ))
        
        return CustomTable(
            id=data['id'],
            name=data['name'],
            schema=schema,
            rows=data.get('rows', []),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat()))
        )
    
    def serialize_tables(self) -> List[dict]:
        """Sérialise toutes les tables"""
        from ..persistence.serializer import serialize_model
        return [serialize_model(table) for table in self._tables.values()]

