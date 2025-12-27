"""
Service de gestion des médias (images)
"""

from pathlib import Path
from typing import Optional, List
from datetime import datetime
import shutil

from ..models.media import Media, MediaType
from ..core.utils import generate_id


class MediaService:
    """Service de gestion des médias"""
    
    def __init__(self, project_service):
        """Initialise le service avec une référence au ProjectService"""
        self.project_service = project_service
        self._media: dict[str, Media] = {}
        self.media_dir: Optional[Path] = None
    
    def initialize_media_dir(self, project_path: Path) -> None:
        """Initialise le répertoire de stockage des médias"""
        if not isinstance(project_path, Path):
            project_path = Path(str(project_path))
        
        self.media_dir = project_path / "media" / "images"
        self.media_dir.mkdir(parents=True, exist_ok=True)
    
    def upload_image(self, source_path: Path, entity_type: str, entity_id: str) -> Optional[str]:
        """
        Upload une image et l'associe à une entité
        
        Args:
            source_path: Chemin du fichier source
            entity_type: Type d'entité ('character', 'scene', 'session', 'location', 'faction', etc.)
            entity_id: ID de l'entité
            
        Returns:
            ID du média créé ou None en cas d'erreur
        """
        if not self.media_dir:
            if self.project_service and self.project_service.project_path:
                self.initialize_media_dir(self.project_service.project_path)
            else:
                return None
        
        if not source_path.exists():
            return None
        
        # Générer un nom de fichier unique
        file_extension = source_path.suffix
        unique_filename = f"{generate_id()}{file_extension}"
        dest_path = self.media_dir / unique_filename
        
        try:
            # Copier le fichier
            shutil.copy2(source_path, dest_path)
            
            # Créer l'entrée média
            media = Media(
                id=generate_id(),
                filename=unique_filename,
                filepath=f"media/images/{unique_filename}",
                type=MediaType.IMAGE,
                created_at=datetime.now()
            )
            
            # Associer à l'entité
            if entity_type not in media.associated_entities:
                media.associated_entities[entity_type] = []
            if entity_id not in media.associated_entities[entity_type]:
                media.associated_entities[entity_type].append(entity_id)
            
            self._media[media.id] = media
            return media.id
            
        except Exception as e:
            print(f"Erreur lors de l'upload d'image: {e}")
            return None
    
    def get_image_path(self, media_id: str) -> Optional[Path]:
        """Récupère le chemin complet d'une image"""
        media = self._media.get(media_id)
        if not media or not self.project_service or not self.project_service.project_path:
            return None
        
        return self.project_service.project_path / media.filepath
    
    def get_media(self, media_id: str) -> Optional[Media]:
        """Récupère un média par son ID"""
        return self._media.get(media_id)
    
    def delete_media(self, media_id: str) -> bool:
        """Supprime un média et son fichier"""
        media = self._media.get(media_id)
        if not media:
            return False
        
        # Supprimer le fichier
        if self.project_service and self.project_service.project_path:
            file_path = self.project_service.project_path / media.filepath
            if file_path.exists():
                try:
                    file_path.unlink()
                except Exception:
                    pass
        
        # Supprimer l'entrée
        del self._media[media_id]
        return True
    
    def load_media(self, media_data: List[dict]) -> None:
        """Charge les médias depuis les données du projet"""
        self._media = {}
        for media_dict in media_data:
            media = self._deserialize_media(media_dict)
            self._media[media.id] = media
    
    def _deserialize_media(self, data: dict) -> Media:
        """Désérialise un média depuis un dictionnaire"""
        return Media(
            id=data['id'],
            filename=data['filename'],
            filepath=data['filepath'],
            type=MediaType(data['type']),
            associated_entities=data.get('associated_entities', {}),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat()))
        )
    
    def serialize_media(self) -> List[dict]:
        """Sérialise tous les médias"""
        from ..persistence.serializer import serialize_model
        return [serialize_model(media) for media in self._media.values()]

