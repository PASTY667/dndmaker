"""
Chargeur de données initiales pour les banques
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from ..models.bank import DataBank, BankEntry, BankType
from ..core.utils import generate_id


class DataLoader:
    """Chargeur de données initiales"""
    
    @staticmethod
    def _get_resource_path(filename: str) -> Path:
        """Récupère le chemin vers un fichier de ressources"""
        # Chemin relatif depuis le package
        base_path = Path(__file__).parent.parent
        return base_path / "resources" / "initial_data" / filename
    
    @staticmethod
    def load_weapons() -> List[Dict]:
        """Charge la liste des armes depuis le fichier JSON"""
        try:
            path = DataLoader._get_resource_path("weapons.json")
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (IOError, json.JSONDecodeError):
            pass
        return []
    
    @staticmethod
    def load_armors() -> List[Dict]:
        """Charge la liste des armures depuis le fichier JSON"""
        try:
            path = DataLoader._get_resource_path("armors.json")
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (IOError, json.JSONDecodeError):
            pass
        return []
    
    @staticmethod
    def load_tools() -> List[Dict]:
        """Charge la liste des outils depuis le fichier JSON"""
        try:
            path = DataLoader._get_resource_path("tools.json")
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (IOError, json.JSONDecodeError):
            pass
        return []
    
    @staticmethod
    def load_trinkets() -> List[Dict]:
        """Charge la liste des babioles depuis le fichier JSON"""
        try:
            path = DataLoader._get_resource_path("trinkets.json")
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (IOError, json.JSONDecodeError):
            pass
        return []
    
    @staticmethod
    def load_creatures() -> List[Dict]:
        """Charge la liste des créatures depuis le fichier JSON"""
        try:
            path = DataLoader._get_resource_path("creatures.json")
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (IOError, json.JSONDecodeError):
            pass
        return []
    
    @staticmethod
    def load_professions() -> List[Dict]:
        """Charge la liste des métiers depuis le fichier JSON"""
        try:
            path = DataLoader._get_resource_path("professions.json")
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (IOError, json.JSONDecodeError):
            pass
        return []
    
    @staticmethod
    def initialize_banks(bank_service) -> None:
        """Initialise les banques avec les données par défaut si elles sont vides"""
        # Races par défaut (Chroniques Oubliées)
        races_bank = bank_service.get_or_create_bank(BankType.RACES)
        if not races_bank.entries:
            default_races = [
                "Humain", "Elfe", "Nain", "Halfelin", "Orque", "Gobelin",
                "Demi-elfe", "Demi-orque", "Gnome", "Tieffelin"
            ]
            for race in default_races:
                bank_service.add_entry_to_bank(races_bank.id, race)
        
        # Classes par défaut (Chroniques Oubliées)
        classes_bank = bank_service.get_or_create_bank(BankType.CLASSES)
        if not classes_bank.entries:
            default_classes = [
                "Guerrier", "Rôdeur", "Roublard", "Prêtre", "Mage",
                "Barde", "Paladin", "Barbare", "Moine", "Occultiste"
            ]
            for class_name in default_classes:
                bank_service.add_entry_to_bank(classes_bank.id, class_name)
        
        # Noms par défaut (exemples) - avec origine raciale
        names_bank = bank_service.get_or_create_bank(BankType.NAMES)
        if not names_bank.entries:
            default_names = [
                ("Aragorn", {"racial_origin": "Humain"}),
                ("Legolas", {"racial_origin": "Elfe"}),
                ("Gimli", {"racial_origin": "Nain"}),
                ("Gandalf", {"racial_origin": "Humain"}),
                ("Arwen", {"racial_origin": "Elfe"}),
                ("Galadriel", {"racial_origin": "Elfe"}),
                ("Eowyn", {"racial_origin": "Humain"}),
                ("Frodo", {"racial_origin": "Halfelin"}),
                ("Sam", {"racial_origin": "Halfelin"}),
                ("Merry", {"racial_origin": "Halfelin"})
            ]
            for name, metadata in default_names:
                bank_service.add_entry_to_bank(names_bank.id, name, metadata)
        
        # Créatures depuis le fichier JSON
        creatures_bank = bank_service.get_or_create_bank(BankType.CREATURES)
        # Vérifier quelles créatures sont déjà présentes
        existing_creature_names = {entry.value for entry in creatures_bank.entries}
        creatures = DataLoader.load_creatures()
        for creature in creatures:
            creature_name = creature.get('name', '')
            if creature_name and creature_name not in existing_creature_names:
                metadata = {
                    'level': creature.get('level', 1),
                    'type': creature.get('type', ''),
                    'size': creature.get('size', ''),
                    'ac': creature.get('ac', 10),
                    'hp': creature.get('hp', 1),
                    'initiative': creature.get('initiative', 10),
                    'stats': creature.get('stats', {}),
                    'archetype': creature.get('archetype', 'standard'),
                    'challenge': creature.get('challenge', '0')
                }
                bank_service.add_entry_to_bank(creatures_bank.id, creature_name, metadata)
        
        # Professions depuis le fichier JSON
        professions_bank = bank_service.get_or_create_bank(BankType.PROFESSIONS)
        existing_profession_names = {entry.value for entry in professions_bank.entries}
        professions = DataLoader.load_professions()
        for profession in professions:
            profession_name = profession.get('name', '')
            if profession_name and profession_name not in existing_profession_names:
                bank_service.add_entry_to_bank(professions_bank.id, profession_name, profession)
        
        # Armures depuis le fichier JSON
        armors_bank = bank_service.get_or_create_bank(BankType.ARMORS)
        existing_armor_names = {entry.value for entry in armors_bank.entries}
        armors = DataLoader.load_armors()
        for armor in armors:
            armor_name = armor.get('name', '')
            if armor_name and armor_name not in existing_armor_names:
                bank_service.add_entry_to_bank(armors_bank.id, armor_name, armor)
        
        # Outils depuis le fichier JSON
        tools_bank = bank_service.get_or_create_bank(BankType.TOOLS)
        existing_tool_names = {entry.value for entry in tools_bank.entries}
        tools = DataLoader.load_tools()
        for tool in tools:
            tool_name = tool.get('name', '')
            if tool_name and tool_name not in existing_tool_names:
                bank_service.add_entry_to_bank(tools_bank.id, tool_name, tool)
        
        # Babioles depuis le fichier JSON
        trinkets_bank = bank_service.get_or_create_bank(BankType.TRINKETS)
        existing_trinket_names = {entry.value for entry in trinkets_bank.entries}
        trinkets = DataLoader.load_trinkets()
        for trinket in trinkets:
            trinket_name = trinket.get('name', '')
            if trinket_name and trinket_name not in existing_trinket_names:
                bank_service.add_entry_to_bank(trinkets_bank.id, trinket_name, trinket)
        
        # Armes depuis le fichier JSON
        weapons_bank = bank_service.get_or_create_bank(BankType.WEAPONS)
        existing_weapon_names = {entry.value for entry in weapons_bank.entries}
        weapons = DataLoader.load_weapons()
        for weapon in weapons:
            weapon_name = weapon.get('name', '')
            if weapon_name and weapon_name not in existing_weapon_names:
                bank_service.add_entry_to_bank(weapons_bank.id, weapon_name, weapon)

