"""
Générateur de PNJ
Génération semi-automatique de PNJ avec cohérence classe/race
"""

import random
from typing import Optional, Dict
from ..models.character import (
    Character, CharacterType, CharacterProfile, Characteristics,
    CombatStats, DefenseStats, CharacterCapabilities, PathCapability
)
from ..models.bank import BankType
from ..core.utils import generate_id
from .stats_generator import StatsGenerator


class NPCGenerator:
    """Générateur de PNJ"""
    
    def __init__(self, bank_service):
        """Initialise le générateur avec le service de banques"""
        self.bank_service = bank_service
    
    def generate_name(self, gender: Optional[str] = None) -> str:
        """Génère un nom aléatoire depuis les banques"""
        names_bank = self.bank_service.get_bank_by_type(BankType.NAMES)
        
        if names_bank and names_bank.entries:
            # Filtrer par genre si spécifié
            if gender:
                filtered_entries = [
                    e for e in names_bank.entries
                    if e.metadata.get('gender', '').upper() == gender.upper()
                ]
                if filtered_entries:
                    return random.choice(filtered_entries).value
            
            # Sinon, prendre un nom aléatoire
            return random.choice(names_bank.entries).value
        
        # Par défaut, générer un nom générique
        return f"PNJ_{random.randint(1000, 9999)}"
    
    def generate_race(self) -> str:
        """Génère une race aléatoire depuis les banques"""
        races_bank = self.bank_service.get_bank_by_type(BankType.RACES)
        
        if races_bank and races_bank.entries:
            return random.choice(races_bank.entries).value
        
        return "Humain"  # Par défaut
    
    def generate_class(self) -> str:
        """Génère une classe aléatoire depuis les banques"""
        classes_bank = self.bank_service.get_bank_by_type(BankType.CLASSES)
        
        if classes_bank and classes_bank.entries:
            return random.choice(classes_bank.entries).value
        
        return "Guerrier"  # Par défaut
    
    def generate_profession(self) -> Optional[str]:
        """Génère un métier aléatoire depuis les banques ou données initiales"""
        # Pour l'instant, retourner None - sera implémenté avec les données initiales
        # L'utilisateur pourra sélectionner un métier dans l'éditeur
        return None
    
    def generate_paths_for_class(self, class_name: str, level: int = 1) -> list[PathCapability]:
        """Génère des voies cohérentes pour une classe donnée"""
        paths_bank = self.bank_service.get_bank_by_type(BankType.PATHS)
        
        paths = []
        if paths_bank and paths_bank.entries:
            # Filtrer les voies compatibles avec la classe
            compatible_paths = [
                e for e in paths_bank.entries
                if class_name.lower() in e.metadata.get('classes', '').lower()
                or e.metadata.get('classes', '') == ''
            ]
            
            if not compatible_paths:
                compatible_paths = paths_bank.entries
            
            # Sélectionner jusqu'à 3 voies
            selected = random.sample(
                compatible_paths,
                min(3, len(compatible_paths))
            )
            
            for entry in selected:
                path = PathCapability(
                    name=entry.value,
                    level=min(level, 3)  # Limiter au niveau 3 pour les voies
                )
                paths.append(path)
        
        # Compléter avec des voies vides si nécessaire
        while len(paths) < 3:
            paths.append(PathCapability())
        
        return paths[:3]
    
    def generate_npc(
        self,
        level: int = 1,
        race: Optional[str] = None,
        class_name: Optional[str] = None,
        gender: Optional[str] = None,
        name: Optional[str] = None,
        stats_method: str = "standard"
    ) -> Character:
        """Génère un PNJ complet
        
        Args:
            level: Niveau du PNJ (1-20)
            race: Race spécifique (None pour aléatoire)
            class_name: Classe spécifique (None pour aléatoire)
            gender: Genre (None pour aléatoire)
            name: Nom spécifique (None pour généré)
            stats_method: Méthode de génération de stats ("standard" ou "heroic")
        """
        # Générer ou utiliser les valeurs fournies
        if name is None:
            name = self.generate_name(gender)
        
        if race is None:
            race = self.generate_race()
        
        if class_name is None:
            class_name = self.generate_class()
        
        if gender is None:
            gender = random.choice(["M", "F", None])
        
        # Générer les stats
        stats = StatsGenerator.generate_stats_by_level(level, stats_method)
        
        # Générer les voies
        paths = self.generate_paths_for_class(class_name, level)
        
        # Créer le profil
        profile = CharacterProfile(
            level=level,
            race=race,
            gender=gender
        )
        
        # Créer les capacités avec les voies
        capabilities = CharacterCapabilities(
            path1=paths[0] if len(paths) > 0 else PathCapability(),
            path2=paths[1] if len(paths) > 1 else PathCapability(),
            path3=paths[2] if len(paths) > 2 else PathCapability()
        )
        
        # Calculer les stats de combat basiques
        combat = CombatStats()
        combat.melee_attack = f"{stats.strength.modifier} + {level}"
        combat.ranged_attack = f"{stats.dexterity.modifier} + {level}"
        combat.magic_attack = str(level)
        combat.initiative = str(stats.dexterity.modifier)
        
        # Calculer la défense basique
        defense = DefenseStats()
        defense.dexterity = stats.dexterity.modifier
        
        # Générer des équipements aléatoires
        equipment = self._generate_random_equipment(class_name, level)
        
        # Créer le personnage
        character = Character(
            id=generate_id(),
            name=name,
            type=CharacterType.PNJ,
            profile=profile,
            characteristics=stats,
            combat=combat,
            defense=defense,
            capabilities=capabilities,
            equipment=equipment
        )
        
        return character
    
    def _generate_random_equipment(self, class_name: str, level: int) -> list[str]:
        """Génère des équipements aléatoires pour un PNJ"""
        from ..core.data_loader import DataLoader
        
        equipment = []
        
        # Charger les équipements disponibles
        weapons = DataLoader.load_weapons()
        armors = DataLoader.load_armors()
        tools = DataLoader.load_tools()
        trinkets = DataLoader.load_trinkets()
        
        # Équipement de base (toujours présent - 1 à 2 items aléatoires)
        if trinkets:
            # Ajouter quelques babioles de base
            basic_items = ["Bourse", "Torche", "Rations (1 jour)", "Sac à dos"]
            # Sélectionner 1 à 2 items aléatoires
            selected_basic = random.sample(basic_items, min(random.randint(1, 2), len(basic_items)))
            for item_name in selected_basic:
                # Chercher dans les babioles
                item = next((t for t in trinkets if t.get('name', '').lower() == item_name.lower()), None)
                if item:
                    equipment.append(item['name'])
        
        # Arme selon la classe
        if weapons:
            # Filtrer les armes selon la classe (simplifié)
            suitable_weapons = []
            if class_name.lower() in ["guerrier", "paladin", "barbare"]:
                # Armes de mêlée
                suitable_weapons = [w for w in weapons if w.get('category') == 'corps_à_corps']
            elif class_name.lower() in ["rôdeur", "roublard"]:
                # Armes légères et à distance
                suitable_weapons = [w for w in weapons if 'légère' in w.get('properties', []) or w.get('category') == 'distance']
            elif class_name.lower() in ["mage", "prêtre", "barde"]:
                # Armes simples
                suitable_weapons = [w for w in weapons if w.get('type') == 'courante']
            else:
                suitable_weapons = weapons
            
            if suitable_weapons:
                weapon = random.choice(suitable_weapons)
                equipment.append(weapon['name'])
        
        # Armure selon le niveau
        if armors:
            # Plus le niveau est élevé, meilleure est l'armure
            if level >= 5:
                suitable_armors = [a for a in armors if a.get('type') in ['moyenne', 'lourde']]
            else:
                suitable_armors = [a for a in armors if a.get('type') in ['légère', 'moyenne']]
            
            if suitable_armors:
                armor = random.choice(suitable_armors)
                equipment.append(armor['name'])
        
        # Outils selon le métier (si présent)
        # Les outils seront ajoutés via le métier dans le profil
        
        return equipment

