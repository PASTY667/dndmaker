"""
Service de gestion des banques de données
"""

from typing import List, Optional
from ..models.bank import DataBank, BankEntry, BankType
from ..core.utils import generate_id


class BankService:
    """Service de gestion des banques de données"""
    
    def __init__(self, project_service):
        """Initialise le service avec une référence au ProjectService"""
        self.project_service = project_service
        self._banks: dict[str, DataBank] = {}
    
    def load_banks(self, banks_data: List[dict]) -> None:
        """Charge les banques depuis les données du projet"""
        self._banks = {}
        for bank_data in banks_data:
            bank = self._deserialize_bank(bank_data)
            self._banks[bank.id] = bank
    
    def create_bank(self, bank_type: BankType) -> DataBank:
        """Crée une nouvelle banque de données"""
        bank = DataBank(
            id=generate_id(),
            type=bank_type
        )
        self._banks[bank.id] = bank
        return bank
    
    def get_bank(self, bank_id: str) -> Optional[DataBank]:
        """Récupère une banque par son ID"""
        return self._banks.get(bank_id)
    
    def get_bank_by_type(self, bank_type: BankType) -> Optional[DataBank]:
        """Récupère une banque par son type"""
        for bank in self._banks.values():
            if bank.type == bank_type:
                return bank
        return None
    
    def get_or_create_bank(self, bank_type: BankType) -> DataBank:
        """Récupère une banque ou la crée si elle n'existe pas"""
        bank = self.get_bank_by_type(bank_type)
        if bank is None:
            bank = self.create_bank(bank_type)
        return bank
    
    def get_all_banks(self) -> List[DataBank]:
        """Récupère toutes les banques"""
        return list(self._banks.values())
    
    def update_bank(self, bank: DataBank) -> None:
        """Met à jour une banque"""
        if bank.id not in self._banks:
            raise ValueError(f"Banque {bank.id} introuvable")
        self._banks[bank.id] = bank
    
    def delete_bank(self, bank_id: str) -> bool:
        """Supprime une banque"""
        if bank_id not in self._banks:
            return False
        del self._banks[bank_id]
        return True
    
    def add_entry_to_bank(self, bank_id: str, value: str, metadata: Optional[dict] = None) -> BankEntry:
        """Ajoute une entrée à une banque"""
        bank = self.get_bank(bank_id)
        if not bank:
            raise ValueError(f"Banque {bank_id} introuvable")
        
        entry = BankEntry(
            id=generate_id(),
            value=value,
            metadata=metadata or {}
        )
        bank.entries.append(entry)
        return entry
    
    def remove_entry_from_bank(self, bank_id: str, entry_id: str) -> bool:
        """Supprime une entrée d'une banque"""
        bank = self.get_bank(bank_id)
        if not bank:
            return False
        
        bank.entries = [e for e in bank.entries if e.id != entry_id]
        return True
    
    def update_entry(self, bank_id: str, entry_id: str, value: str, metadata: Optional[dict] = None) -> bool:
        """Met à jour une entrée d'une banque"""
        bank = self.get_bank(bank_id)
        if not bank:
            return False
        
        entry = next((e for e in bank.entries if e.id == entry_id), None)
        if not entry:
            return False
        
        entry.value = value
        if metadata is not None:
            entry.metadata = metadata
        
        return True
    
    def get_random_entry(self, bank_type: BankType) -> Optional[str]:
        """Récupère une entrée aléatoire d'une banque"""
        import random
        bank = self.get_bank_by_type(bank_type)
        if not bank or not bank.entries:
            return None
        return random.choice(bank.entries).value
    
    def _deserialize_bank(self, data: dict) -> DataBank:
        """Désérialise une banque depuis un dictionnaire"""
        entries = []
        for entry_data in data.get('entries', []):
            entries.append(BankEntry(
                id=entry_data['id'],
                value=entry_data['value'],
                metadata=entry_data.get('metadata', {})
            ))
        
        bank = DataBank(
            id=data['id'],
            type=BankType(data['type']),
            entries=entries,
            metadata=data.get('metadata', {})
        )
        return bank
    
    def serialize_banks(self) -> List[dict]:
        """Sérialise toutes les banques"""
        from ..persistence.serializer import serialize_model
        return [serialize_model(bank) for bank in self._banks.values()]

