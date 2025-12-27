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
            "nav.campaign": "Campagne",
            "nav.sessions": "Sessions",
            "nav.scenes": "Scènes",
            "nav.characters": "PJ",
            "nav.npcs": "PNJ / Créatures",
            "nav.banks": "Banques",
            "nav.exports": "Exports",
            
            # Campagne
            "campaign.title": "Campagne",
            "campaign.new": "Nouvelle campagne",
            "campaign.open": "Ouvrir une campagne",
            "campaign.import": "Importer une campagne",
            "campaign.info": "Aucune campagne ouverte",
            "campaign.name": "Nom:",
            "campaign.created": "Créé le:",
            "campaign.modified": "Modifié le:",
            "campaign.version": "Version:",
            "campaign.history": "Historique des versions:",
            "campaign.rollback": "Restaurer cette version",
            "campaign.metadata": "Métadonnées:",
            "campaign.save_metadata": "Sauvegarder les métadonnées",
            
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
            "bank.type_factions": "Factions",
            "bank.type_locations": "Lieux",
            "bank.type_tables": "Tables",
            
            # Tables
            "table.title": "Table",
            "table.name": "Nom de la table:",
            "table.fields": "Champs",
            "table.field_name": "Nom du champ",
            "table.field_type": "Type",
            "table.add_field": "Ajouter un champ",
            "table.remove_field": "Supprimer",
            "table.field_types": "Types de champs",
            "table.string": "Texte",
            "table.number": "Nombre",
            "table.boolean": "Booléen",
            "table.date": "Date",
            "table.rows": "Lignes de données",
            "table.add_row": "Ajouter une ligne",
            "table.edit_row": "Modifier",
            "table.delete_row": "Supprimer",
            "table.no_fields": "Aucun champ défini. Ajoutez au moins un champ pour créer la table.",
            "table.schema_required": "Vous devez définir au moins un champ pour créer la table.",
            "table.add_table": "Ajouter une table",
            "table.edit_table": "Modifier une table",
            "table.new_table": "Nouvelle table",
            "table.edit": "Modifier",
            "table.delete": "Supprimer",
            "table.custom_tables": "Tables personnalisées",
            "table.name_required": "Le nom de la table est obligatoire.",
            
            # Images
            "image.upload": "Télécharger une image",
            "image.remove": "Supprimer",
            "image.no_image": "Aucune image",
            "image.select_file": "Sélectionner une image",
            "image.file_filter": "Images (*.jpg *.jpeg *.png *.gif *.bmp *.webp)",
            "image.invalid_format": "Format d'image non supporté.",
            "image.upload_failed": "Échec du téléchargement de l'image.",
            "image.service_unavailable": "Service de médias non disponible.",
            "image.confirm_remove": "Êtes-vous sûr de vouloir supprimer cette image ?",
            "image.drag_drop_hint": "(Glissez-déposez une image ici)",
            
            # Lieux
            "location.title": "Lieux",
            "location.name": "Nom:",
            "location.description": "Description:",
            "location.type": "Type:",
            "location.parent": "Lieu parent:",
            "location.create": "Créer un lieu",
            "location.edit": "Modifier",
            "location.delete": "Supprimer",
            "location.add_to_scene": "Ajouter à la scène",
            
            # Factions
            "faction.title": "Faction",
            "faction.select": "Sélectionner une faction:",
            "faction.none": "Aucune",
            
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
            "msg.confirm": "Confirmer",
            "msg.confirm_delete": "Êtes-vous sûr de vouloir supprimer cet élément ?",
            "msg.success": "Opération réussie",
            "msg.error": "Erreur",
            "msg.warning": "Attention",
            "msg.info": "Information",
            "msg.save": "Sauvegarder",
            "msg.cancel": "Annuler",
            "msg.about": "À propos",
            "msg.about_title": "À propos de DNDMaker",
            "msg.about_text": "DNDMaker v0.1.0\n\nApplication de gestion de campagne\nChroniques Oubliées\n\nDéveloppé avec Python et PyQt6",
            
            # Menus
            "menu.edit": "Édition",
            "menu.help": "Aide",
            
            # Langue
            "lang.french": "Français",
            "lang.english": "English",
            "lang.change": "Changer la langue",
        },
        Language.ENGLISH: {
            # Navigation
            "nav.campaign": "Campaign",
            "nav.sessions": "Sessions",
            "nav.scenes": "Scenes",
            "nav.characters": "PCs",
            "nav.npcs": "NPCs / Creatures",
            "nav.banks": "Banks",
            "nav.exports": "Exports",
            
            # Campaign
            "campaign.title": "Campaign",
            "campaign.new": "New campaign",
            "campaign.open": "Open a campaign",
            "campaign.import": "Import a campaign",
            "campaign.info": "No campaign open",
            "campaign.name": "Name:",
            "campaign.created": "Created:",
            "campaign.modified": "Modified:",
            "campaign.version": "Version:",
            "campaign.history": "Version history:",
            "campaign.rollback": "Restore this version",
            "campaign.metadata": "Metadata:",
            "campaign.save_metadata": "Save metadata",
            
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
            "bank.type_factions": "Factions",
            "bank.type_locations": "Locations",
            "bank.type_tables": "Tables",
            
            # Tables
            "table.title": "Table",
            "table.name": "Table name:",
            "table.fields": "Fields",
            "table.field_name": "Field name",
            "table.field_type": "Type",
            "table.add_field": "Add field",
            "table.remove_field": "Remove",
            "table.field_types": "Field types",
            "table.string": "Text",
            "table.number": "Number",
            "table.boolean": "Boolean",
            "table.date": "Date",
            "table.rows": "Data rows",
            "table.add_row": "Add row",
            "table.edit_row": "Edit",
            "table.delete_row": "Delete",
            "table.no_fields": "No fields defined. Add at least one field to create the table.",
            "table.schema_required": "You must define at least one field to create the table.",
            "table.add_table": "Add a table",
            "table.edit_table": "Edit table",
            "table.new_table": "New table",
            "table.edit": "Edit",
            "table.delete": "Delete",
            "table.custom_tables": "Custom tables",
            "table.name_required": "The table name is required.",
            
            # Images
            "image.upload": "Upload image",
            "image.remove": "Remove",
            "image.no_image": "No image",
            "image.select_file": "Select an image",
            "image.file_filter": "Images (*.jpg *.jpeg *.png *.gif *.bmp *.webp)",
            "image.invalid_format": "Unsupported image format.",
            "image.upload_failed": "Failed to upload image.",
            "image.service_unavailable": "Media service unavailable.",
            "image.confirm_remove": "Are you sure you want to remove this image?",
            "image.drag_drop_hint": "(Drag and drop an image here)",
            
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
            "msg.confirm": "Confirm",
            "msg.confirm_delete": "Are you sure you want to delete this item?",
            "msg.success": "Success",
            "msg.error": "Error",
            "msg.warning": "Warning",
            "msg.info": "Information",
            "msg.save": "Save",
            "msg.cancel": "Cancel",
            "msg.about": "About",
            "msg.about_title": "About DNDMaker",
            "msg.about_text": "DNDMaker v0.1.0\n\nCampaign management application\nChroniques Oubliées\n\nDeveloped with Python and PyQt6",
            
            # Menus
            "menu.edit": "Edit",
            "menu.help": "Help",
            
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

