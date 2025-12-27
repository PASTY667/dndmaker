"""
Tests pour les utilitaires du core
"""

import pytest
from dndmaker.core.utils import (
    generate_id,
    validate_characteristic_value,
    calculate_modifier
)


class TestGenerateID:
    """Tests pour la génération d'ID"""
    
    def test_generate_id_returns_string(self):
        """Vérifie que generate_id retourne une chaîne"""
        id_value = generate_id()
        assert isinstance(id_value, str)
        assert len(id_value) > 0
    
    def test_generate_id_unique(self):
        """Vérifie que generate_id génère des IDs uniques"""
        ids = [generate_id() for _ in range(100)]
        assert len(ids) == len(set(ids))  # Tous les IDs sont uniques
    
    def test_generate_id_format(self):
        """Vérifie le format de l'ID (UUID)"""
        id_value = generate_id()
        # UUID format: 8-4-4-4-12 hex digits
        parts = id_value.split('-')
        assert len(parts) == 5
        assert len(parts[0]) == 8
        assert len(parts[1]) == 4
        assert len(parts[2]) == 4
        assert len(parts[3]) == 4
        assert len(parts[4]) == 12


class TestValidateCharacteristicValue:
    """Tests pour la validation des valeurs de caractéristiques"""
    
    def test_valid_values(self):
        """Vérifie que les valeurs valides sont acceptées"""
        assert validate_characteristic_value(1) is True
        assert validate_characteristic_value(10) is True
        assert validate_characteristic_value(20) is True
    
    def test_invalid_values_too_low(self):
        """Vérifie que les valeurs trop basses sont rejetées"""
        assert validate_characteristic_value(0) is False
        assert validate_characteristic_value(-1) is False
    
    def test_invalid_values_too_high(self):
        """Vérifie que les valeurs trop élevées sont rejetées"""
        assert validate_characteristic_value(21) is False
        assert validate_characteristic_value(100) is False


class TestCalculateModifier:
    """Tests pour le calcul des modificateurs"""
    
    def test_modifier_calculation(self):
        """Vérifie le calcul correct des modificateurs"""
        # Valeur 10 = modificateur 0
        assert calculate_modifier(10) == 0
        
        # Valeur 12 = modificateur 1
        assert calculate_modifier(12) == 1
        
        # Valeur 15 = modificateur 2
        assert calculate_modifier(15) == 2
        
        # Valeur 8 = modificateur -1
        assert calculate_modifier(8) == -1
        
        # Valeur 1 = modificateur -5
        assert calculate_modifier(1) == -5
    
    def test_modifier_rounding_down(self):
        """Vérifie que le modificateur est arrondi vers le bas"""
        # Valeur 11 = (11-10)/2 = 0.5 arrondi vers le bas = 0
        assert calculate_modifier(11) == 0
        
        # Valeur 13 = (13-10)/2 = 1.5 arrondi vers le bas = 1
        assert calculate_modifier(13) == 1

