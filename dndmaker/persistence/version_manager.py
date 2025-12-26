"""
Gestionnaire de versions
"""

from typing import List, Optional, Dict
from datetime import datetime
from pathlib import Path
import json

from ..models.version import Version
from .serializer import serialize_model, JSONEncoder


class VersionManager:
    """Gestionnaire de versions pour un projet"""
    
    def __init__(self, project_path: Path):
        # S'assurer que project_path est un Path
        if not isinstance(project_path, Path):
            project_path = Path(str(project_path))
        
        self.project_path = project_path
        self.versions_dir = project_path / "versions"
        self.versions_dir.mkdir(exist_ok=True)
    
    def create_version(self, project_data: Dict, description: Optional[str] = None) -> Version:
        """Crée une nouvelle version du projet"""
        # Lire la version actuelle
        current_version = self.get_current_version_number()
        new_version_number = current_version + 1
        
        version = Version(
            version_number=new_version_number,
            timestamp=datetime.now(),
            description=description,
            data=project_data.copy()
        )
        
        # Sauvegarder la version
        version_file = self.versions_dir / f"version_{new_version_number:04d}.json"
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(serialize_model(version), f, cls=JSONEncoder, indent=2, ensure_ascii=False)
        
        return version
    
    def get_current_version_number(self) -> int:
        """Récupère le numéro de version actuel"""
        version_files = sorted(self.versions_dir.glob("version_*.json"))
        if not version_files:
            return 0
        # Extraire le numéro de la dernière version
        last_file = version_files[-1]
        version_num = int(last_file.stem.split('_')[1])
        return version_num
    
    def list_versions(self) -> List[Version]:
        """Liste toutes les versions"""
        versions = []
        version_files = sorted(self.versions_dir.glob("version_*.json"))
        
        for version_file in version_files:
            with open(version_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                version = Version(
                    version_number=data['version_number'],
                    timestamp=datetime.fromisoformat(data['timestamp']),
                    description=data.get('description'),
                    data=data.get('data', {})
                )
                versions.append(version)
        
        return versions
    
    def get_version(self, version_number: int) -> Optional[Version]:
        """Récupère une version spécifique"""
        version_file = self.versions_dir / f"version_{version_number:04d}.json"
        if not version_file.exists():
            return None
        
        with open(version_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return Version(
                version_number=data['version_number'],
                timestamp=datetime.fromisoformat(data['timestamp']),
                description=data.get('description'),
                data=data.get('data', {})
            )
    
    def rollback_to_version(self, version_number: int) -> Dict:
        """Effectue un rollback vers une version spécifique"""
        version = self.get_version(version_number)
        if not version:
            raise ValueError(f"Version {version_number} introuvable")
        
        return version.data

