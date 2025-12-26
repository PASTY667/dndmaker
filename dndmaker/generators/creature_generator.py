"""
Générateur de créatures
Génération semi-automatique de créatures
"""

import random
from typing import Optional
from ..models.character import (
    Character, CharacterType, CharacterProfile, Characteristics,
    CombatStats, DefenseStats
)
from ..models.bank import BankType
from ..core.utils import generate_id
from .stats_generator import StatsGenerator


class CreatureGenerator:
    """Générateur de créatures"""
    
    def __init__(self, bank_service):
        """Initialise le générateur avec le service de banques"""
        self.bank_service = bank_service
    
    def generate_name(self) -> str:
        """Génère un nom de créature aléatoire"""
        names_bank = self.bank_service.get_bank_by_type(BankType.NAMES)
        
        if names_bank and names_bank.entries:
            # Filtrer les noms de créatures si possible
            creature_names = [
                e for e in names_bank.entries
                if e.metadata.get('type', '').upper() == 'CREATURE'
            ]
            if creature_names:
                return random.choice(creature_names).value
            # Sinon, prendre un nom aléatoire
            return random.choice(names_bank.entries).value
        
        # Par défaut, générer un nom générique
        return f"Créature_{random.randint(1000, 9999)}"
    
    def generate_creature_from_template(
        self,
        template_name: Optional[str] = None,
        level: Optional[int] = None
    ) -> Optional[Character]:
        """Génère une créature depuis un template du bestiaire"""
        from ..core.data_loader import DataLoader
        creatures = DataLoader.load_creatures()
        
        if not creatures:
            return None
        
        # Si un template est spécifié, le chercher
        if template_name:
            template = next((c for c in creatures if c['name'].lower() == template_name.lower()), None)
        else:
            # Sinon, choisir un template aléatoire adapté au niveau
            if level:
                suitable_creatures = [c for c in creatures if c.get('level', 1) <= level + 1]
                if suitable_creatures:
                    template = random.choice(suitable_creatures)
                else:
                    template = random.choice(creatures)
            else:
                template = random.choice(creatures)
        
        if not template:
            return None
        
        # Utiliser le niveau du template ou celui fourni
        creature_level = level if level else template.get('level', 1)
        
        # Créer la créature depuis le template
        name = template['name']
        stats_data = template.get('stats', {})
        
        # Créer les caractéristiques depuis le template
        from ..models.character import CharacteristicValue
        stats = Characteristics(
            strength=CharacteristicValue(value=stats_data.get('strength', 10)),
            dexterity=CharacteristicValue(value=stats_data.get('dexterity', 10)),
            constitution=CharacteristicValue(value=stats_data.get('constitution', 10)),
            intelligence=CharacteristicValue(value=stats_data.get('intelligence', 10)),
            wisdom=CharacteristicValue(value=stats_data.get('wisdom', 10)),
            charisma=CharacteristicValue(value=stats_data.get('charisma', 10))
        )
        
        # Créer le profil
        profile = CharacterProfile(
            level=creature_level,
            race=template.get('type', 'Créature')
        )
        
        # Calculer les stats de combat
        combat = CombatStats()
        combat.melee_attack = f"{stats.strength.modifier} + {creature_level}"
        combat.ranged_attack = f"{stats.dexterity.modifier} + {creature_level}"
        combat.magic_attack = str(creature_level)
        # Utiliser l'initiative du template si disponible, sinon calculer depuis DEX
        if 'initiative' in template:
            combat.initiative = str(template['initiative'])
        else:
            combat.initiative = str(stats.dexterity.modifier)
        
        # Utiliser les PV du template si disponible
        if 'hp' in template:
            hp_value = template['hp']
            if isinstance(hp_value, int):
                combat.life_points = hp_value
                combat.current_life_points = hp_value
            else:
                # Si c'est une chaîne (ex: "2d6"), garder la valeur par défaut
                combat.life_points = creature_level * 5
                combat.current_life_points = creature_level * 5
        
        # Calculer la défense
        defense = DefenseStats()
        defense.base = template.get('ac', 10)
        defense.dexterity = stats.dexterity.modifier
        
        # Créer la créature
        character = Character(
            id=generate_id(),
            name=name,
            type=CharacterType.CREATURE,
            profile=profile,
            characteristics=stats,
            combat=combat,
            defense=defense
        )
        
        return character
    
    def generate_creature(
        self,
        level: int = 1,
        name: Optional[str] = None,
        stats_method: str = "standard",
        use_template: bool = True
    ) -> Character:
        """Génère une créature complète
        
        Args:
            level: Niveau de la créature (1-20)
            name: Nom spécifique (None pour généré)
            stats_method: Méthode de génération de stats ("standard" ou "heroic")
            use_template: Utiliser un template du bestiaire si disponible
        """
        # Essayer d'abord avec un template si demandé
        if use_template:
            template_creature = self.generate_creature_from_template(name, level)
            if template_creature:
                # Si un nom spécifique est fourni, l'utiliser
                if name:
                    template_creature.name = name
                return template_creature
        
        # Sinon, génération standard
        # Générer ou utiliser le nom fourni
        if name is None:
            name = self.generate_name()
        
        # Générer les stats
        stats = StatsGenerator.generate_stats_by_level(level, stats_method)
        
        # Créer le profil (créatures n'ont généralement pas de race/classe au sens classique)
        profile = CharacterProfile(
            level=level,
            race="Créature"
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
        
        # Créer la créature
        character = Character(
            id=generate_id(),
            name=name,
            type=CharacterType.CREATURE,
            profile=profile,
            characteristics=stats,
            combat=combat,
            defense=defense
        )
        
        return character

