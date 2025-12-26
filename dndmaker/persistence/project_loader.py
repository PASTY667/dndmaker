"""
Chargeur de projet
"""

from pathlib import Path
from typing import Optional, Dict
import json

from ..models.project import Project
from .serializer import JSONEncoder


class ProjectLoader:
    """Chargeur de projet"""
    
    @staticmethod
    def load_project(project_path: Path) -> Optional[Dict]:
        """Charge un projet depuis un fichier"""
        # S'assurer que project_path est un Path
        if not isinstance(project_path, Path):
            project_path = Path(str(project_path))
        
        # Vérifier que le chemin existe et est un répertoire
        if not project_path.exists():
            print(f"DEBUG: Le chemin du projet n'existe pas: {project_path}")
            return None
        
        if not project_path.is_dir():
            print(f"DEBUG: Le chemin du projet n'est pas un répertoire: {project_path}")
            return None
        
        project_file = project_path / "project.json"
        if not project_file.exists():
            print(f"DEBUG: Le fichier project.json n'existe pas dans: {project_path}")
            return None
        
        try:
            with open(project_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"DEBUG: Projet chargé avec succès depuis: {project_file}")
                return data
        except json.JSONDecodeError as e:
            print(f"DEBUG: Erreur de décodage JSON: {e}")
            return None
        except IOError as e:
            print(f"DEBUG: Erreur d'IO: {e}")
            return None
    
    @staticmethod
    def save_project(project_path: Path, project_data: Dict) -> None:
        """Sauvegarde un projet dans un fichier"""
        # S'assurer que project_path est un Path
        if not isinstance(project_path, Path):
            project_path = Path(str(project_path))
        
        project_path.mkdir(parents=True, exist_ok=True)
        project_file = project_path / "project.json"
        
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, cls=JSONEncoder, indent=2, ensure_ascii=False)

