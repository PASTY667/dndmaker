"""
Sérialisation/désérialisation des modèles
"""

from typing import Any, Dict, Set
from datetime import datetime
from enum import Enum
import json


class JSONEncoder(json.JSONEncoder):
    """Encodeur JSON personnalisé pour les types spéciaux"""
    
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Enum):
            return obj.value
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)


def serialize_model(model: Any, visited: Set[int] = None) -> Any:
    """Sérialise un modèle en dictionnaire ou valeur primitive
    
    Args:
        model: Le modèle à sérialiser
        visited: Set des IDs d'objets déjà visités (pour éviter la récursion)
    """
    if visited is None:
        visited = set()
    
    # Gérer les types de base en premier
    if model is None:
        return None
    if isinstance(model, (str, int, float, bool)):
        return model
    if isinstance(model, datetime):
        return model.isoformat()
    if isinstance(model, Enum):
        return model.value
    
    # Éviter la récursion infinie pour les objets complexes
    obj_id = id(model)
    if obj_id in visited:
        return None  # Référence circulaire détectée
    visited.add(obj_id)
    
    try:
        # Gérer les listes
        if isinstance(model, list):
            return [serialize_model(item, visited) for item in model]
        
        # Gérer les tuples
        if isinstance(model, tuple):
            return tuple(serialize_model(item, visited) for item in model)
        
        # Gérer les dictionnaires
        if isinstance(model, dict):
            return {k: serialize_model(v, visited) for k, v in model.items()}
        
        # Gérer les objets avec __dict__ (dataclasses, etc.)
        if hasattr(model, '__dict__'):
            result = {}
            for key, value in model.__dict__.items():
                # Ignorer les attributs privés (sauf __dict__ lui-même)
                if key.startswith('_') and key != '__dict__':
                    continue
                try:
                    serialized_value = serialize_model(value, visited)
                    result[key] = serialized_value
                except (TypeError, ValueError, RecursionError) as e:
                    # En cas d'erreur, essayer de convertir en string
                    result[key] = str(value)
            return result
        
        # Par défaut, convertir en string
        return str(model)
    
    finally:
        visited.discard(obj_id)


def deserialize_model(data: Dict, model_class: type) -> Any:
    """Désérialise un dictionnaire en modèle"""
    # Cette fonction sera implémentée selon les besoins spécifiques
    # Pour l'instant, retourne les données brutes
    return data

