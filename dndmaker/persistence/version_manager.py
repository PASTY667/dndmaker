"""
Gestionnaire de versions
"""

from typing import List, Optional, Dict
from datetime import datetime
from pathlib import Path
import json
import hashlib

from ..models.version import Version
from .serializer import serialize_model, JSONEncoder


class VersionManager:
    """Gestionnaire de versions pour une campagne"""
    
    def __init__(self, project_path: Path):
        # S'assurer que project_path est un Path
        if not isinstance(project_path, Path):
            project_path = Path(str(project_path))
        
        self.project_path = project_path
        self.versions_dir = project_path / "versions"
        self.versions_dir.mkdir(exist_ok=True)
    
    def _compute_data_hash(self, project_data: Dict) -> str:
        """Calcule un hash des données du projet pour détecter les changements"""
        # Sérialiser les données de manière déterministe (tri des clés)
        serialized = json.dumps(project_data, sort_keys=True, cls=JSONEncoder, ensure_ascii=False)
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()
    
    def create_version(self, project_data: Dict, description: Optional[str] = None, force: bool = False) -> Optional[Version]:
        """
        Crée une nouvelle version du projet uniquement si les données ont changé
        
        Args:
            project_data: Données du projet à sauvegarder
            description: Description optionnelle de la version
            force: Si True, crée une version même si les données n'ont pas changé
            
        Returns:
            La nouvelle version créée, ou None si aucune nouvelle version n'était nécessaire
        """
        # Calculer le hash des nouvelles données
        new_hash = self._compute_data_hash(project_data)
        
        # Vérifier si la dernière version existe et comparer les hash
        if not force:
            last_version = self.get_current_version()
            if last_version:
                last_hash = self._compute_data_hash(last_version.data)
                if last_hash == new_hash:
                    # Les données n'ont pas changé, pas besoin de créer une nouvelle version
                    return None
        
        # Les données ont changé ou force=True, créer une nouvelle version
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
        
        # Nettoyer les anciennes versions : ne garder que les 3 dernières
        self._cleanup_old_versions()
        
        return version
    
    def _cleanup_old_versions(self) -> None:
        """Supprime les versions anciennes, ne garde que les 3 dernières"""
        version_files = sorted(self.versions_dir.glob("version_*.json"))
        
        # Si on a plus de 3 versions, supprimer les plus anciennes
        if len(version_files) > 3:
            # Garder les 3 dernières (les plus récentes)
            versions_to_keep = version_files[-3:]
            versions_to_delete = version_files[:-3]
            
            for version_file in versions_to_delete:
                try:
                    version_file.unlink()
                except OSError:
                    # Ignorer les erreurs de suppression (fichier déjà supprimé, permissions, etc.)
                    pass
    
    def get_current_version(self) -> Optional[Version]:
        """Récupère la version actuelle (la plus récente)"""
        current_version_number = self.get_current_version_number()
        if current_version_number == 0:
            return None
        return self.get_version(current_version_number)
    
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

