"""
Système de traduction internationalisation (i18n)
"""

from typing import Dict, Optional
from enum import Enum


class Language(Enum):
    """Langues disponibles"""
    FRENCH = "fr"
    ENGLISH = "en"


class Translator:
    """Gestionnaire de traduction"""
    
    _instance: Optional['Translator'] = None
    _current_language: Language = Language.FRENCH
    
    # Dictionnaires de traduction
    _translations: Dict[Language, Dict[str, str]] = {
        Language.FRENCH: {
            # Navigation
            "nav.project": "Projet",
            "nav.sessions": "Sessions",
            "nav.scenes": "Scènes",
            "nav.characters": "PJ",
            "nav.npcs": "PNJ / Créatures",
            "nav.banks": "Banques",
            "nav.exports": "Exports",
            
            # Projet
            "project.title": "Projet",
            "project.new": "Nouveau projet",
            "project.open": "Ouvrir un projet",
            "project.import": "Importer un projet",
            "project.info": "Aucun projet ouvert",
            "project.name": "Nom:",
            "project.created": "Créé le:",
            "project.modified": "Modifié le:",
            "project.version": "Version:",
            "project.history": "Historique des versions:",
            "project.rollback": "Restaurer cette version",
            "project.metadata": "Métadonnées:",
            "project.save_metadata": "Sauvegarder les métadonnées",
            
            # Personnages
            "character.title": "Personnages",
            "character.create": "Créer",
            "character.edit": "Modifier",
            "character.delete": "Supprimer",
            "character.generate": "Générer",
            "character.name": "Nom",
            "character.type": "Type",
            "character.level": "Niveau",
            "character.race": "Race",
            "character.class": "Classe",
            
            # Scènes
            "scene.title": "Scènes",
            "scene.create": "Créer une scène",
            "scene.edit": "Modifier",
            "scene.delete": "Supprimer",
            "scene.title_label": "Titre",
            "scene.description": "Description",
            
            # Sessions
            "session.title": "Sessions",
            "session.create": "Créer une session",
            "session.duplicate": "Dupliquer",
            "session.edit": "Modifier",
            "session.delete": "Supprimer",
            "session.title_label": "Titre",
            "session.date": "Date",
            "session.notes": "Notes post-session",
            
            # Banques
            "bank.title": "Banques de données",
            "bank.add": "Ajouter",
            "bank.edit": "Modifier",
            "bank.delete": "Supprimer",
            
            # Exports
            "export.title": "Exports",
            "export.type": "Type d'export:",
            "export.format": "Format:",
            "export.element": "Élément à exporter:",
            "export.export": "Exporter",
            "export.character": "Fiche PJ",
            "export.npc": "Fiche PNJ/Créature",
            "export.scene": "Scène",
            "export.session": "Session",
            "export.full": "Scénario complet",
            
            # Boutons généraux
            "btn.save": "Sauvegarder",
            "btn.cancel": "Annuler",
            "btn.ok": "OK",
            "btn.yes": "Oui",
            "btn.no": "Non",
            "btn.close": "Fermer",
            "btn.delete": "Supprimer",
            "btn.edit": "Modifier",
            "btn.add": "Ajouter",
            "btn.create": "Créer",
            
            # Messages
            "msg.confirm_delete": "Êtes-vous sûr de vouloir supprimer cet élément ?",
            "msg.success": "Opération réussie",
            "msg.error": "Erreur",
            "msg.warning": "Attention",
            "msg.info": "Information",
            
            # Langue
            "lang.french": "Français",
            "lang.english": "English",
            "lang.change": "Changer la langue",
        },
        Language.ENGLISH: {
            # Navigation
            "nav.project": "Project",
            "nav.sessions": "Sessions",
            "nav.scenes": "Scenes",
            "nav.characters": "PCs",
            "nav.npcs": "NPCs / Creatures",
            "nav.banks": "Banks",
            "nav.exports": "Exports",
            
            # Projet
            "project.title": "Project",
            "project.new": "New project",
            "project.open": "Open a project",
            "project.import": "Import a project",
            "project.info": "No project open",
            "project.name": "Name:",
            "project.created": "Created:",
            "project.modified": "Modified:",
            "project.version": "Version:",
            "project.history": "Version history:",
            "project.rollback": "Restore this version",
            "project.metadata": "Metadata:",
            "project.save_metadata": "Save metadata",
            
            # Personnages
            "character.title": "Characters",
            "character.create": "Create",
            "character.edit": "Edit",
            "character.delete": "Delete",
            "character.generate": "Generate",
            "character.name": "Name",
            "character.type": "Type",
            "character.level": "Level",
            "character.race": "Race",
            "character.class": "Class",
            
            # Scènes
            "scene.title": "Scenes",
            "scene.create": "Create a scene",
            "scene.edit": "Edit",
            "scene.delete": "Delete",
            "scene.title_label": "Title",
            "scene.description": "Description",
            
            # Sessions
            "session.title": "Sessions",
            "session.create": "Create a session",
            "session.duplicate": "Duplicate",
            "session.edit": "Edit",
            "session.delete": "Delete",
            "session.title_label": "Title",
            "session.date": "Date",
            "session.notes": "Post-session notes",
            
            # Banques
            "bank.title": "Data Banks",
            "bank.add": "Add",
            "bank.edit": "Edit",
            "bank.delete": "Delete",
            
            # Exports
            "export.title": "Exports",
            "export.type": "Export type:",
            "export.format": "Format:",
            "export.element": "Element to export:",
            "export.export": "Export",
            "export.character": "PC Sheet",
            "export.npc": "NPC/Creature Sheet",
            "export.scene": "Scene",
            "export.session": "Session",
            "export.full": "Full scenario",
            
            # Boutons généraux
            "btn.save": "Save",
            "btn.cancel": "Cancel",
            "btn.ok": "OK",
            "btn.yes": "Yes",
            "btn.no": "No",
            "btn.close": "Close",
            "btn.delete": "Delete",
            "btn.edit": "Edit",
            "btn.add": "Add",
            "btn.create": "Create",
            
            # Messages
            "msg.confirm_delete": "Are you sure you want to delete this item?",
            "msg.success": "Success",
            "msg.error": "Error",
            "msg.warning": "Warning",
            "msg.info": "Information",
            
            # Langue
            "lang.french": "Français",
            "lang.english": "English",
            "lang.change": "Change language",
        }
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def set_language(cls, language: Language) -> None:
        """Définit la langue actuelle"""
        cls._current_language = language
    
    @classmethod
    def get_language(cls) -> Language:
        """Récupère la langue actuelle"""
        return cls._current_language
    
    @classmethod
    def tr(cls, key: str, default: Optional[str] = None) -> str:
        """
        Traduit une clé
        
        Args:
            key: Clé de traduction
            default: Texte par défaut si la clé n'existe pas
            
        Returns:
            Texte traduit
        """
        translations = cls._translations.get(cls._current_language, {})
        return translations.get(key, default or key)
    
    @classmethod
    def get_available_languages(cls) -> list[Language]:
        """Retourne la liste des langues disponibles"""
        return list(cls._translations.keys())


def tr(key: str, default: Optional[str] = None) -> str:
    """
    Fonction helper pour traduire une clé
    
    Args:
        key: Clé de traduction
        default: Texte par défaut si la clé n'existe pas
        
    Returns:
        Texte traduit
    """
    return Translator.tr(key, default)

