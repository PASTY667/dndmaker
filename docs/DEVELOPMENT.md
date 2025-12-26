# Guide de développement

## Principes de développement

### 1. Séparation stricte des responsabilités

- **Aucune logique métier dans l'UI** : La GUI et la CLI utilisent exactement les mêmes services
- **Modèles purs** : Les modèles sont de simples structures de données (dataclasses)
- **Services réutilisables** : Toute la logique métier est dans les services

### 2. Code lisible avant tout

- Typage clair avec type hints
- Documentation des fonctions et classes
- Noms explicites
- Aucun code "magique"

### 3. Testabilité

- Fonctions pures quand c'est possible
- Injection de dépendances
- Services testables indépendamment de l'UI

## Structure des services

Chaque service suit ce pattern :

```python
class ServiceName:
    """Description du service"""
    
    def __init__(self, dependencies):
        """Initialisation avec dépendances"""
        pass
    
    def method(self, params):
        """Méthode avec documentation"""
        # Logique métier pure
        pass
```

## Structure des modèles

Tous les modèles utilisent des dataclasses :

```python
@dataclass
class ModelName:
    """Description du modèle"""
    id: str
    name: str
    # ... autres champs
```

## Gestion des erreurs

- Utiliser des exceptions spécifiques
- Logger les erreurs
- Messages d'erreur clairs pour l'utilisateur

## Logs

- Utiliser le module `logging`
- Niveaux appropriés (DEBUG, INFO, WARNING, ERROR)
- Logs exploitables pour le débogage

## Tests

- Tests unitaires pour chaque service
- Tests d'intégration pour les flux complets
- Utiliser pytest

## Ajout de nouvelles fonctionnalités

1. Définir le modèle de données
2. Créer le service correspondant
3. Implémenter la persistence
4. Ajouter l'interface UI (Qt et CLI)
5. Ajouter les tests
6. Documenter

