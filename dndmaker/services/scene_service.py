"""
Service de gestion des scènes
"""

from typing import List, Optional
from datetime import datetime

from ..models.scene import Scene, Event
from ..core.utils import generate_id


class SceneService:
    """Service de gestion des scènes"""
    
    def __init__(self, project_service):
        """Initialise le service avec une référence au ProjectService"""
        self.project_service = project_service
        self._scenes: dict[str, Scene] = {}
    
    def load_scenes(self, scenes_data: List[dict]) -> None:
        """Charge les scènes depuis les données du projet"""
        self._scenes = {}
        for scene_data in scenes_data:
            scene = self._deserialize_scene(scene_data)
            self._scenes[scene.id] = scene
    
    def create_scene(self, title: str, description: str = "") -> Scene:
        """Crée une nouvelle scène"""
        scene = Scene(
            id=generate_id(),
            title=title,
            description=description,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self._scenes[scene.id] = scene
        return scene
    
    def get_scene(self, scene_id: str) -> Optional[Scene]:
        """Récupère une scène par son ID"""
        return self._scenes.get(scene_id)
    
    def get_all_scenes(self) -> List[Scene]:
        """Récupère toutes les scènes"""
        return list(self._scenes.values())
    
    def update_scene(self, scene: Scene) -> None:
        """Met à jour une scène"""
        if scene.id not in self._scenes:
            raise ValueError(f"Scène {scene.id} introuvable")
        scene.updated_at = datetime.now()
        self._scenes[scene.id] = scene
    
    def delete_scene(self, scene_id: str) -> bool:
        """Supprime une scène"""
        if scene_id not in self._scenes:
            return False
        del self._scenes[scene_id]
        return True
    
    def add_event_to_scene(self, scene_id: str, title: str, description: str = "") -> Event:
        """Ajoute un événement à une scène"""
        scene = self.get_scene(scene_id)
        if not scene:
            raise ValueError(f"Scène {scene_id} introuvable")
        
        event = Event(
            id=generate_id(),
            title=title,
            description=description,
            timestamp=datetime.now()
        )
        scene.events.append(event)
        scene.updated_at = datetime.now()
        return event
    
    def remove_event_from_scene(self, scene_id: str, event_id: str) -> bool:
        """Supprime un événement d'une scène"""
        scene = self.get_scene(scene_id)
        if not scene:
            return False
        
        scene.events = [e for e in scene.events if e.id != event_id]
        scene.updated_at = datetime.now()
        return True
    
    def _deserialize_scene(self, data: dict) -> Scene:
        """Désérialise une scène depuis un dictionnaire"""
        events = []
        for event_data in data.get('events', []):
            events.append(Event(
                id=event_data['id'],
                title=event_data['title'],
                description=event_data.get('description', ''),
                timestamp=datetime.fromisoformat(event_data['timestamp']) if event_data.get('timestamp') else None
            ))
        
        scene = Scene(
            id=data['id'],
            title=data['title'],
            description=data.get('description', ''),
            player_characters=data.get('player_characters', []),
            npcs=data.get('npcs', []),
            locations=data.get('locations', []),
            events=events,
            objects=data.get('objects', []),
            cards=data.get('cards', []),
            images=data.get('images', []),
            image_id=data.get('image_id'),
            referenced_scenes=data.get('referenced_scenes', []),
            sessions=data.get('sessions', []),
            notes=data.get('notes', ''),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat()))
        )
        
        return scene
    
    def serialize_scenes(self) -> List[dict]:
        """Sérialise toutes les scènes"""
        from ..persistence.serializer import serialize_model
        return [serialize_model(scene) for scene in self._scenes.values()]

