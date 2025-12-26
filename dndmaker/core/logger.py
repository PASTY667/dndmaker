"""
Système de logging pour l'application
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class UserActionLogger:
    """Logger spécialisé pour les actions utilisateur"""
    
    _instance: Optional['UserActionLogger'] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._setup_logging()
            UserActionLogger._initialized = True
    
    def _setup_logging(self):
        """Configure le système de logging"""
        # Créer le logger principal
        self.logger = logging.getLogger('dndmaker')
        self.logger.setLevel(logging.DEBUG)
        
        # Éviter la duplication des handlers
        if self.logger.handlers:
            return
        
        # Handler pour la console avec format détaillé
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        # Format détaillé avec timestamp, niveau, module, fonction, ligne
        detailed_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s.%(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(detailed_format)
        
        self.logger.addHandler(console_handler)
        
        # Logger pour les actions utilisateur spécifiquement
        self.user_logger = logging.getLogger('dndmaker.user')
        self.user_logger.setLevel(logging.INFO)
        
        # Format simplifié pour les actions utilisateur
        user_format = logging.Formatter(
            '%(asctime)s | [ACTION] %(message)s',
            datefmt='%H:%M:%S'
        )
        user_handler = logging.StreamHandler(sys.stdout)
        user_handler.setLevel(logging.INFO)
        user_handler.setFormatter(user_format)
        self.user_logger.addHandler(user_handler)
    
    def log_user_action(self, action: str, details: Optional[dict] = None):
        """Enregistre une action utilisateur"""
        message = f"👤 {action}"
        if details:
            details_str = ", ".join([f"{k}={v}" for k, v in details.items()])
            message += f" | {details_str}"
        self.user_logger.info(message)
    
    def log_project_action(self, action: str, project_name: Optional[str] = None, **kwargs):
        """Enregistre une action sur un projet"""
        details = {"project": project_name} if project_name else {}
        details.update(kwargs)
        self.log_user_action(f"PROJECT: {action}", details)
    
    def log_character_action(self, action: str, character_name: Optional[str] = None, 
                            character_type: Optional[str] = None, **kwargs):
        """Enregistre une action sur un personnage"""
        details = {}
        if character_name:
            details["character"] = character_name
        if character_type:
            details["type"] = character_type
        details.update(kwargs)
        self.log_user_action(f"CHARACTER: {action}", details)
    
    def log_scene_action(self, action: str, scene_title: Optional[str] = None, **kwargs):
        """Enregistre une action sur une scène"""
        details = {"scene": scene_title} if scene_title else {}
        details.update(kwargs)
        self.log_user_action(f"SCENE: {action}", details)
    
    def log_session_action(self, action: str, session_title: Optional[str] = None, **kwargs):
        """Enregistre une action sur une session"""
        details = {"session": session_title} if session_title else {}
        details.update(kwargs)
        self.log_user_action(f"SESSION: {action}", details)
    
    def log_bank_action(self, action: str, bank_type: Optional[str] = None, **kwargs):
        """Enregistre une action sur une banque"""
        details = {"bank_type": bank_type} if bank_type else {}
        details.update(kwargs)
        self.log_user_action(f"BANK: {action}", details)
    
    def log_ui_action(self, action: str, **kwargs):
        """Enregistre une action UI"""
        self.log_user_action(f"UI: {action}", kwargs)
    
    def debug(self, message: str, *args, **kwargs):
        """Log de debug"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log d'information"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log d'avertissement"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log d'erreur"""
        self.logger.error(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """Log d'exception avec traceback"""
        self.logger.exception(message, *args, **kwargs)


# Instance globale
_logger_instance: Optional[UserActionLogger] = None


def get_logger() -> UserActionLogger:
    """Récupère l'instance du logger"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = UserActionLogger()
    return _logger_instance

