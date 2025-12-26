"""
Service de gestion de projet
"""

from pathlib import Path
from typing import Optional
from datetime import datetime

from ..models.project import Project
from ..core.utils import generate_id
from ..persistence.project_loader import ProjectLoader
from ..persistence.version_manager import VersionManager
from .character_service import CharacterService
from .scene_service import SceneService
from .session_service import SessionService
from .bank_service import BankService


class ProjectService:
    """Service de gestion de projet"""
    
    def __init__(self):
        self.current_project: Optional[Project] = None
        self.project_path: Optional[Path] = None
        self.version_manager: Optional[VersionManager] = None
        
        # Services associés - initialisés dès le départ
        self.character_service = CharacterService(self)
        self.scene_service = SceneService(self)
        self.session_service = SessionService(self)
        self.bank_service = BankService(self)
    
    def create_project(self, name: str, project_dir: Path) -> Project:
        """Crée un nouveau projet"""
        # S'assurer que project_dir est un Path
        if not isinstance(project_dir, Path):
            project_dir = Path(str(project_dir))
        
        project = Project(
            id=generate_id(),
            name=name,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1
        )
        
        self.project_path = project_dir / f"{name}.dndmaker"
        self.project_path.mkdir(parents=True, exist_ok=True)
        
        self.version_manager = VersionManager(self.project_path)
        self.current_project = project
        
        # Les services sont déjà initialisés dans __init__
        # Réinitialiser pour s'assurer qu'ils sont liés au bon projet
        self._reinit_services()
        
        # Initialiser les banques avec les données par défaut
        from ..core.data_loader import DataLoader
        DataLoader.initialize_banks(self.bank_service)
        
        # Sauvegarder le projet initial
        self.save_project()
        
        return project
    
    def load_project(self, project_path: Path) -> Optional[Project]:
        """Charge un projet existant"""
        # S'assurer que project_path est un Path
        if not isinstance(project_path, Path):
            project_path = Path(str(project_path))
        
        print(f"DEBUG: Tentative de chargement du projet depuis: {project_path}")
        
        data = ProjectLoader.load_project(project_path)
        if not data:
            print("DEBUG: ProjectLoader.load_project a retourné None")
            return None
        
        try:
            project = Project(
                id=data.get('id', ''),
                name=data.get('name', ''),
                created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
                updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat())),
                version=data.get('version', 1),
                metadata=data.get('metadata', {})
            )
            
            self.project_path = project_path
            self.version_manager = VersionManager(self.project_path)
            self.current_project = project
            
            # Les services sont déjà initialisés dans __init__
            # Réinitialiser pour s'assurer qu'ils sont liés au bon projet
            self._reinit_services()
            
            # Initialiser les banques avec les données par défaut si nécessaire
            from ..core.data_loader import DataLoader
            DataLoader.initialize_banks(self.bank_service)
            
            # Charger les données du projet
            self._load_project_data(data)
            
            print(f"DEBUG: Projet '{project.name}' chargé avec succès")
            return project
        except (KeyError, ValueError, TypeError) as e:
            print(f"DEBUG: Erreur lors de la création du projet: {e}")
            import traceback
            print(traceback.format_exc())
            return None
    
    def save_project(self, description: Optional[str] = None) -> None:
        """Sauvegarde le projet actuel"""
        if not self.current_project or not self.project_path:
            raise ValueError("Aucun projet ouvert")
        
        # Mettre à jour la date de modification
        self.current_project.updated_at = datetime.now()
        
        # Sérialiser le projet avec toutes les données
        project_data = {
            'id': self.current_project.id,
            'name': self.current_project.name,
            'created_at': self.current_project.created_at.isoformat(),
            'updated_at': self.current_project.updated_at.isoformat(),
            'version': self.current_project.version,
            'metadata': self.current_project.metadata,
            'characters': self.character_service.serialize_characters() if self.character_service else [],
            'scenes': self.scene_service.serialize_scenes() if self.scene_service else [],
            'sessions': self.session_service.serialize_sessions() if self.session_service else [],
            'data_banks': self.bank_service.serialize_banks() if self.bank_service else [],
            'media': []  # À implémenter
        }
        
        # Sauvegarder
        ProjectLoader.save_project(self.project_path, project_data)
        
        # Créer une version
        if self.version_manager:
            self.version_manager.create_version(project_data, description)
            self.current_project.version = self.version_manager.get_current_version_number()
    
    def import_project_from_json(self, json_path: Path, project_dir: Path) -> Optional[Project]:
        """
        Importe un projet depuis un fichier JSON
        
        Args:
            json_path: Chemin vers le fichier JSON à importer
            project_dir: Répertoire où créer le nouveau projet
            
        Returns:
            Le projet importé ou None en cas d'erreur
        """
        import json
        
        # S'assurer que les chemins sont des Path
        if not isinstance(json_path, Path):
            json_path = Path(str(json_path))
        if not isinstance(project_dir, Path):
            project_dir = Path(str(project_dir))
        
        # Vérifier que le fichier JSON existe
        if not json_path.exists():
            print(f"DEBUG: Le fichier JSON n'existe pas: {json_path}")
            return None
        
        try:
            # Charger le JSON
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extraire le nom du projet (depuis les données ou le nom du fichier)
            project_name = data.get('name', json_path.stem)
            
            # Créer un nouveau projet avec ce nom
            project = self.create_project(project_name, project_dir)
            
            # Charger les données dans le projet
            self._load_project_data(data)
            
            # Sauvegarder le projet importé
            self.save_project(f"Import depuis {json_path.name}")
            
            print(f"DEBUG: Projet '{project_name}' importé avec succès depuis {json_path}")
            return project
            
        except json.JSONDecodeError as e:
            print(f"DEBUG: Erreur de décodage JSON: {e}")
            return None
        except Exception as e:
            print(f"DEBUG: Erreur lors de l'import: {e}")
            import traceback
            print(traceback.format_exc())
            return None
    
    def get_current_project(self) -> Optional[Project]:
        """Récupère le projet actuel"""
        return self.current_project
    
    def rollback_to_version(self, version_number: int) -> bool:
        """Effectue un rollback vers une version spécifique"""
        if not self.version_manager:
            return False
        
        try:
            project_data = self.version_manager.rollback_to_version(version_number)
            
            # Mettre à jour le projet avec les données de la version
            if 'id' in project_data:
                self.current_project.id = project_data['id']
            if 'name' in project_data:
                self.current_project.name = project_data['name']
            if 'created_at' in project_data:
                self.current_project.created_at = datetime.fromisoformat(project_data['created_at'])
            if 'metadata' in project_data:
                self.current_project.metadata = project_data.get('metadata', {})
            
            # Recharger toutes les données du projet depuis la version
            self._load_project_data(project_data)
            
            # Mettre à jour la date et la version
            self.current_project.updated_at = datetime.now()
            self.current_project.version = version_number
            
            # Sauvegarder le rollback (cela créera une nouvelle version)
            self.save_project(f"Rollback vers version {version_number}")
            return True
        except (ValueError, KeyError, TypeError) as e:
            print(f"Erreur lors du rollback: {e}")
            return False
    
    def _reinit_services(self) -> None:
        """Réinitialise les services associés (appelé lors du chargement/création d'un projet)"""
        # Les services sont déjà initialisés dans __init__
        # Cette méthode peut être utilisée pour réinitialiser si nécessaire
        pass
    
    def _load_project_data(self, data: dict) -> None:
        """Charge les données du projet dans les services"""
        if self.character_service:
            self.character_service.load_characters(data.get('characters', []))
        if self.scene_service:
            self.scene_service.load_scenes(data.get('scenes', []))
        if self.session_service:
            self.session_service.load_sessions(data.get('sessions', []))
        if self.bank_service:
            self.bank_service.load_banks(data.get('data_banks', []))

