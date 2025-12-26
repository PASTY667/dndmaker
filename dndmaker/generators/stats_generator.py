"""
Générateur de statistiques pour personnages
Selon les règles Chroniques Oubliées
"""

import random
from typing import Dict, Optional
from ..models.character import CharacteristicValue, Characteristics


class StatsGenerator:
    """Générateur de statistiques pour personnages"""
    
    # Méthodes de génération de stats selon Chroniques Oubliées
    # Méthode standard : 4d6, garder les 3 meilleurs
    # Méthode héroïque : 5d6, garder les 3 meilleurs
    # Méthode point buy : points à répartir
    
    @staticmethod
    def roll_dice(num_dice: int, dice_size: int = 6) -> int:
        """Lance des dés"""
        return sum(random.randint(1, dice_size) for _ in range(num_dice))
    
    @staticmethod
    def roll_4d6_drop_lowest() -> int:
        """Lance 4d6 et garde les 3 meilleurs (méthode standard)"""
        rolls = [random.randint(1, 6) for _ in range(4)]
        rolls.sort(reverse=True)
        return sum(rolls[:3])
    
    @staticmethod
    def roll_5d6_drop_lowest() -> int:
        """Lance 5d6 et garde les 3 meilleurs (méthode héroïque)"""
        rolls = [random.randint(1, 6) for _ in range(5)]
        rolls.sort(reverse=True)
        return sum(rolls[:3])
    
    @staticmethod
    def generate_standard_stats() -> Characteristics:
        """Génère des stats avec la méthode standard (4d6, garder 3 meilleurs)"""
        stats = Characteristics(
            strength=CharacteristicValue(value=StatsGenerator.roll_4d6_drop_lowest()),
            dexterity=CharacteristicValue(value=StatsGenerator.roll_4d6_drop_lowest()),
            constitution=CharacteristicValue(value=StatsGenerator.roll_4d6_drop_lowest()),
            intelligence=CharacteristicValue(value=StatsGenerator.roll_4d6_drop_lowest()),
            wisdom=CharacteristicValue(value=StatsGenerator.roll_4d6_drop_lowest()),
            charisma=CharacteristicValue(value=StatsGenerator.roll_4d6_drop_lowest())
        )
        return stats
    
    @staticmethod
    def generate_heroic_stats() -> Characteristics:
        """Génère des stats avec la méthode héroïque (5d6, garder 3 meilleurs)"""
        stats = Characteristics(
            strength=CharacteristicValue(value=StatsGenerator.roll_5d6_drop_lowest()),
            dexterity=CharacteristicValue(value=StatsGenerator.roll_5d6_drop_lowest()),
            constitution=CharacteristicValue(value=StatsGenerator.roll_5d6_drop_lowest()),
            intelligence=CharacteristicValue(value=StatsGenerator.roll_5d6_drop_lowest()),
            wisdom=CharacteristicValue(value=StatsGenerator.roll_5d6_drop_lowest()),
            charisma=CharacteristicValue(value=StatsGenerator.roll_5d6_drop_lowest())
        )
        return stats
    
    @staticmethod
    def generate_stats_by_level(level: int, method: str = "standard") -> Characteristics:
        """Génère des stats adaptées au niveau
        
        Args:
            level: Niveau du personnage (1-20)
            method: Méthode de génération ("standard" ou "heroic")
        """
        if method == "heroic":
            base_stats = StatsGenerator.generate_heroic_stats()
        else:
            base_stats = StatsGenerator.generate_standard_stats()
        
        # Ajuster selon le niveau (les stats peuvent être améliorées au niveau)
        # Pour l'instant, on génère simplement des stats de base
        # L'utilisateur pourra les ajuster manuellement
        
        return base_stats
    
    @staticmethod
    def generate_stats_from_table(stat_table: Optional[Dict] = None) -> Characteristics:
        """Génère des stats depuis une table de stats personnalisée
        
        Args:
            stat_table: Dictionnaire avec des plages de valeurs par caractéristique
        """
        if not stat_table:
            return StatsGenerator.generate_standard_stats()
        
        def get_stat_value(stat_name: str) -> int:
            """Récupère une valeur depuis la table ou génère aléatoirement"""
            if stat_name in stat_table:
                stat_range = stat_table[stat_name]
                if isinstance(stat_range, dict):
                    min_val = stat_range.get('min', 8)
                    max_val = stat_range.get('max', 18)
                    return random.randint(min_val, max_val)
                elif isinstance(stat_range, list):
                    return random.choice(stat_range)
            # Par défaut, utiliser 4d6
            return StatsGenerator.roll_4d6_drop_lowest()
        
        stats = Characteristics(
            strength=CharacteristicValue(value=get_stat_value('strength')),
            dexterity=CharacteristicValue(value=get_stat_value('dexterity')),
            constitution=CharacteristicValue(value=get_stat_value('constitution')),
            intelligence=CharacteristicValue(value=get_stat_value('intelligence')),
            wisdom=CharacteristicValue(value=get_stat_value('wisdom')),
            charisma=CharacteristicValue(value=get_stat_value('charisma'))
        )
        return stats

