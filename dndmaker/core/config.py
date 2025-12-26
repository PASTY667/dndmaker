"""
Gestion de la configuration de l'application
"""

from pathlib import Path
from typing import Optional
import json
import os


class Config:
    """Gestionnaire de configuration"""
    
    def __init__(self, config_file: Optional[Path] = None):
        """Initialise le gestionnaire de configuration"""
        if config_file is None:
            # Utiliser un fichier de config dans le répertoire utilisateur
            try:
                home = Path.home()
                if not isinstance(home, Path):
                    raise TypeError("Path.home() ne retourne pas un Path")
                config_dir = home / ".dndmaker"
                config_dir.mkdir(exist_ok=True)
                config_file = config_dir / "config.json"
            except (OSError, TypeError, AttributeError) as e:
                # En cas d'erreur, utiliser un fichier temporaire dans le répertoire courant
                config_file = Path(".dndmaker_config.json")
        
        # S'assurer que config_file est un Path
        if not isinstance(config_file, Path):
            config_file = Path(str(config_file))
        
        self.config_file = config_file
        self._config = self._load_config()
    
    def _load_config(self) -> dict:
        """Charge la configuration depuis le fichier"""
        try:
            # S'assurer que config_file est un Path
            if not isinstance(self.config_file, Path):
                self.config_file = Path(str(self.config_file))
            
            if self.config_file.exists():
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except (json.JSONDecodeError, IOError, TypeError):
                    return {}
        except (TypeError, AttributeError, OSError):
            pass
        return {}
    
    def _save_config(self) -> None:
        """Sauvegarde la configuration dans le fichier"""
        try:
            # S'assurer que config_file est un Path
            if not isinstance(self.config_file, Path):
                self.config_file = Path(str(self.config_file))
            
            # Vérifier que parent existe avant d'utiliser /
            if self.config_file.parent:
                self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except (IOError, TypeError, OSError, AttributeError):
            pass  # Ignorer les erreurs d'écriture
    
    def get_last_project(self) -> Optional[Path]:
        """Récupère le chemin du dernier projet ouvert"""
        project_path = self._config.get('last_project')
        if project_path and isinstance(project_path, str):
            try:
                path = Path(project_path)
                # Vérifier que le projet existe toujours
                if path.exists() and path.is_dir() and (path / "project.json").exists():
                    return path
            except (TypeError, ValueError, OSError):
                # Si le chemin est invalide, l'ignorer
                pass
        return None
    
    def set_last_project(self, project_path: Path) -> None:
        """Définit le chemin du dernier projet ouvert"""
        try:
            # S'assurer que project_path est un Path
            if not isinstance(project_path, Path):
                project_path = Path(project_path)
            self._config['last_project'] = str(project_path.absolute())
            self._save_config()
        except (TypeError, ValueError, OSError):
            # Ignorer les erreurs
            pass
    
    def clear_last_project(self) -> None:
        """Efface le dernier projet ouvert"""
        if 'last_project' in self._config:
            del self._config['last_project']
            self._save_config()
    
    def get_language(self) -> str:
        """Récupère la langue préférée (fr ou en)"""
        return self._config.get('language', 'fr')
    
    def set_language(self, language: str) -> None:
        """Définit la langue préférée"""
        self._config['language'] = language
        self._save_config()

