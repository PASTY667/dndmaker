"""
Service de gestion des sessions
"""

from typing import List, Optional
from datetime import datetime

from ..models.session import Session
from ..core.utils import generate_id


class SessionService:
    """Service de gestion des sessions"""
    
    def __init__(self, project_service):
        """Initialise le service avec une référence au ProjectService"""
        self.project_service = project_service
        self._sessions: dict[str, Session] = {}
    
    def load_sessions(self, sessions_data: List[dict]) -> None:
        """Charge les sessions depuis les données du projet"""
        self._sessions = {}
        for session_data in sessions_data:
            session = self._deserialize_session(session_data)
            self._sessions[session.id] = session
    
    def create_session(
        self,
        title: str,
        date: Optional[datetime] = None,
        is_preparation: bool = False
    ) -> Session:
        """Crée une nouvelle session"""
        if date is None:
            date = datetime.now()
        
        session = Session(
            id=generate_id(),
            title=title,
            date=date,
            is_preparation=is_preparation,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self._sessions[session.id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Récupère une session par son ID"""
        return self._sessions.get(session_id)
    
    def get_all_sessions(self) -> List[Session]:
        """Récupère toutes les sessions"""
        return list(self._sessions.values())
    
    def update_session(self, session: Session) -> None:
        """Met à jour une session"""
        if session.id not in self._sessions:
            raise ValueError(f"Session {session.id} introuvable")
        session.updated_at = datetime.now()
        self._sessions[session.id] = session
    
    def delete_session(self, session_id: str) -> bool:
        """Supprime une session"""
        if session_id not in self._sessions:
            return False
        del self._sessions[session_id]
        return True
    
    def add_scene_to_session(self, session_id: str, scene_id: str, position: Optional[int] = None) -> None:
        """Ajoute une scène à une session"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} introuvable")
        
        if scene_id in session.scenes:
            return  # Déjà présente
        
        if position is None:
            session.scenes.append(scene_id)
        else:
            session.scenes.insert(position, scene_id)
        
        session.updated_at = datetime.now()
    
    def remove_scene_from_session(self, session_id: str, scene_id: str) -> bool:
        """Retire une scène d'une session"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        if scene_id not in session.scenes:
            return False
        
        session.scenes.remove(scene_id)
        session.updated_at = datetime.now()
        return True
    
    def reorder_scenes_in_session(self, session_id: str, scene_ids: List[str]) -> None:
        """Réordonne les scènes dans une session"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} introuvable")
        
        session.scenes = scene_ids
        session.updated_at = datetime.now()
    
    def duplicate_session(self, session_id: str, new_title: Optional[str] = None) -> Session:
        """Duplique une session (préparation → réel)"""
        original = self.get_session(session_id)
        if not original:
            raise ValueError(f"Session {session_id} introuvable")
        
        new_title = new_title or f"{original.title} (Copie)"
        new_session = Session(
            id=generate_id(),
            title=new_title,
            date=datetime.now(),
            scenes=original.scenes.copy(),
            post_session_notes="",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_preparation=False  # La copie est toujours "réelle"
        )
        
        self._sessions[new_session.id] = new_session
        return new_session
    
    def _deserialize_session(self, data: dict) -> Session:
        """Désérialise une session depuis un dictionnaire"""
        session = Session(
            id=data['id'],
            title=data['title'],
            date=datetime.fromisoformat(data.get('date', datetime.now().isoformat())),
            scenes=data.get('scenes', []),
            post_session_notes=data.get('post_session_notes', ''),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat())),
            is_preparation=data.get('is_preparation', False)
        )
        return session
    
    def serialize_sessions(self) -> List[dict]:
        """Sérialise toutes les sessions"""
        from ..persistence.serializer import serialize_model
        return [serialize_model(session) for session in self._sessions.values()]

