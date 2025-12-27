"""
Service de gestion des lieux
"""

from typing import List, Optional
from datetime import datetime

from ..models.location import Location
from ..core.utils import generate_id


class LocationService:
    """Service de gestion des lieux"""
    
    def __init__(self, project_service):
        """Initialise le service avec une référence au ProjectService"""
        self.project_service = project_service
        self._locations: dict[str, Location] = {}
    
    def load_locations(self, locations_data: List[dict]) -> None:
        """Charge les lieux depuis les données du projet"""
        self._locations = {}
        for location_data in locations_data:
            location = self._deserialize_location(location_data)
            self._locations[location.id] = location
    
    def create_location(
        self,
        name: str,
        description: str = "",
        location_type: Optional[str] = None,
        parent_location: Optional[str] = None,
        bestiary: Optional[List[str]] = None
    ) -> Location:
        """Crée un nouveau lieu"""
        location = Location(
            id=generate_id(),
            name=name,
            description=description,
            location_type=location_type,
            parent_location=parent_location,
            bestiary=bestiary or [],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self._locations[location.id] = location
        return location
    
    def get_location(self, location_id: str) -> Optional[Location]:
        """Récupère un lieu par son ID"""
        return self._locations.get(location_id)
    
    def get_all_locations(self) -> List[Location]:
        """Récupère tous les lieux"""
        return list(self._locations.values())
    
    def update_location(self, location: Location) -> None:
        """Met à jour un lieu"""
        if location.id not in self._locations:
            raise ValueError(f"Lieu {location.id} introuvable")
        location.updated_at = datetime.now()
        self._locations[location.id] = location
    
    def delete_location(self, location_id: str) -> bool:
        """Supprime un lieu"""
        if location_id not in self._locations:
            return False
        del self._locations[location_id]
        return True
    
    def _deserialize_location(self, data: dict) -> Location:
        """Désérialise un lieu depuis un dictionnaire"""
        location = Location(
            id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            location_type=data.get('location_type'),
            parent_location=data.get('parent_location'),
            bestiary=data.get('bestiary', []),
            notes=data.get('notes', ''),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat()))
        )
        return location
    
    def serialize_locations(self) -> List[dict]:
        """Sérialise tous les lieux"""
        from ..persistence.serializer import serialize_model
        return [serialize_model(location) for location in self._locations.values()]

