"""
Service de gestion des personnages (PJ/PNJ/Créatures)
"""

from typing import List, Optional
from datetime import datetime

from ..models.character import Character, CharacterType
from ..core.utils import generate_id


class CharacterService:
    """Service de gestion des personnages"""
    
    def __init__(self, project_service):
        """Initialise le service avec une référence au ProjectService"""
        self.project_service = project_service
        self._characters: dict[str, Character] = {}
    
    def load_characters(self, characters_data: List[dict]) -> None:
        """Charge les personnages depuis les données du projet"""
        self._characters = {}
        for char_data in characters_data:
            character = self._deserialize_character(char_data)
            self._characters[character.id] = character
    
    def create_character(
        self,
        name: str,
        character_type: CharacterType,
        level: int = 1,
        race: str = ""
    ) -> Character:
        """Crée un nouveau personnage"""
        from ..models.character import CharacterProfile, Characteristics
        
        character = Character(
            id=generate_id(),
            name=name,
            type=character_type,
            profile=CharacterProfile(level=level, race=race),
            characteristics=Characteristics()
        )
        
        self._characters[character.id] = character
        return character
    
    def get_character(self, character_id: str) -> Optional[Character]:
        """Récupère un personnage par son ID"""
        return self._characters.get(character_id)
    
    def get_all_characters(self) -> List[Character]:
        """Récupère tous les personnages"""
        return list(self._characters.values())
    
    def get_characters_by_type(self, character_type: CharacterType) -> List[Character]:
        """Récupère les personnages d'un type spécifique"""
        result = []
        target_value = character_type.value if isinstance(character_type, CharacterType) else str(character_type)
        
        for c in self._characters.values():
            char_type_value = c.type.value if isinstance(c.type, CharacterType) else str(c.type)
            
            # Comparaison robuste : comparer les valeurs de l'Enum
            if char_type_value == target_value:
                result.append(c)
        
        return result
    
    def update_character(self, character: Character) -> None:
        """Met à jour un personnage"""
        if character.id not in self._characters:
            raise ValueError(f"Personnage {character.id} introuvable")
        self._characters[character.id] = character
    
    def delete_character(self, character_id: str) -> bool:
        """Supprime un personnage"""
        if character_id not in self._characters:
            return False
        del self._characters[character_id]
        return True
    
    def _deserialize_character(self, data: dict) -> Character:
        """Désérialise un personnage depuis un dictionnaire"""
        from ..models.character import (
            CharacterProfile, Characteristics, CombatStats, DefenseStats,
            Weapon, CharacterCapabilities, PathCapability, Valuables
        )
        
        # Désérialiser le profil
        profile_data = data.get('profile', {})
        profile = CharacterProfile(
            level=profile_data.get('level', 1),
            race=profile_data.get('race', ''),
            character_class=profile_data.get('character_class'),
            gender=profile_data.get('gender'),
            age=profile_data.get('age'),
            height=profile_data.get('height'),
            weight=profile_data.get('weight'),
            racial_ability=profile_data.get('racial_ability', ''),
            known_languages=profile_data.get('known_languages', []),
            profession=profile_data.get('profession')
        )
        
        # Désérialiser les caractéristiques
        char_data = data.get('characteristics', {})
        characteristics = Characteristics()
        for attr in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']:
            if attr in char_data:
                from ..models.character import CharacteristicValue
                val_data = char_data[attr]
                setattr(characteristics, attr, CharacteristicValue(
                    value=val_data.get('value', 10),
                    modifier=val_data.get('modifier', 0)
                ))
        
        # Désérialiser le combat
        combat_data = data.get('combat', {})
        combat = CombatStats(
            melee_attack=combat_data.get('melee_attack', ''),
            ranged_attack=combat_data.get('ranged_attack', ''),
            magic_attack=combat_data.get('magic_attack', ''),
            initiative=combat_data.get('initiative', ''),
            life_dice=combat_data.get('life_dice', ''),
            life_points=combat_data.get('life_points', 0),
            current_life_points=combat_data.get('current_life_points', 0),
            temporary_damage=combat_data.get('temporary_damage', 0)
        )
        
        # Désérialiser la défense
        defense_data = data.get('defense', {})
        defense = DefenseStats(
            base=defense_data.get('base', 10),
            armor=defense_data.get('armor', 0),
            shield=defense_data.get('shield', 0),
            dexterity=defense_data.get('dexterity', 0),
            misc=defense_data.get('misc', 0)
        )
        
        # Désérialiser les armes
        weapons = []
        for weapon_data in data.get('weapons', []):
            weapons.append(Weapon(
                name=weapon_data.get('name', ''),
                attack=weapon_data.get('attack', ''),
                damage=weapon_data.get('damage', ''),
                special=weapon_data.get('special')
            ))
        
        # Désérialiser les capacités
        caps_data = data.get('capabilities', {})
        capabilities = CharacterCapabilities()
        for i in [1, 2, 3]:
            path_data = caps_data.get(f'path{i}', {})
            path_cap = PathCapability(
                name=path_data.get('name', ''),
                rank=path_data.get('rank', 0),
                level1=path_data.get('level1'),
                level2=path_data.get('level2'),
                level3=path_data.get('level3')
            )
            setattr(capabilities, f'path{i}', path_cap)
        
        # Désérialiser les objets de valeur
        valuables_data = data.get('valuables', {})
        valuables = Valuables(
            purse=valuables_data.get('purse', ''),
            items=valuables_data.get('items', [])
        )
        
        # Gérer le type de personnage (peut être string ou CharacterType)
        char_type = data.get('type')
        if isinstance(char_type, str):
            try:
                char_type = CharacterType(char_type)
            except ValueError:
                # Essayer de trouver une correspondance
                for ct in CharacterType:
                    if ct.value.upper() == char_type.upper():
                        char_type = ct
                        break
                else:
                    char_type = CharacterType.PJ  # Par défaut
        elif not isinstance(char_type, CharacterType):
            char_type = CharacterType.PJ
        
        character = Character(
            id=data['id'],
            name=data['name'],
            type=char_type,
            profile=profile,
            characteristics=characteristics,
            combat=combat,
            defense=defense,
            weapons=weapons,
            capabilities=capabilities,
            equipment=data.get('equipment', []),
            valuables=valuables,
            notes=data.get('notes', '')
        )
        
        return character
    
    def serialize_characters(self) -> List[dict]:
        """Sérialise tous les personnages"""
        from ..persistence.serializer import serialize_model
        return [serialize_model(char) for char in self._characters.values()]

