# Tests unitaires DNDMaker

Ce dossier contient la suite de tests unitaires pour DNDMaker.

## Structure

- `conftest.py` - Configuration pytest et fixtures communes
- `test_utils.py` - Tests pour les utilitaires du core
- `test_models.py` - Tests pour les modèles de données
- `test_services.py` - Tests pour les services
- `test_exporters.py` - Tests pour les exporters (PDF, JSON, TXT, Markdown)
- `test_persistence.py` - Tests pour la sauvegarde et le chargement

## Installation

Les dépendances de test sont incluses dans `requirements.txt` :
- `pytest>=7.0.0` - Framework de test
- `pytest-cov>=4.0.0` - Couverture de code

Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Exécution des tests

### Tous les tests
```bash
pytest
```

### Tests avec couverture de code
```bash
pytest --cov=dndmaker --cov-report=html
```

### Tests spécifiques
```bash
# Un fichier de test
pytest tests/test_models.py

# Une classe de test
pytest tests/test_services.py::TestCharacterService

# Une fonction de test
pytest tests/test_utils.py::TestGenerateID::test_generate_id_returns_string
```

### Mode verbeux
```bash
pytest -v
```

## Couverture de code

Après avoir exécuté les tests avec `--cov-report=html`, un rapport HTML est généré dans `htmlcov/index.html`.

Pour voir la couverture dans le terminal :
```bash
pytest --cov=dndmaker --cov-report=term-missing
```

## Écriture de nouveaux tests

### Structure d'un test

```python
import pytest
from dndmaker.models.character import Character, CharacterType

class TestCharacter:
    """Tests pour le modèle Character"""
    
    def test_character_creation(self):
        """Vérifie la création d'un personnage"""
        character = Character(
            id="test-1",
            name="Test",
            type=CharacterType.PJ
        )
        assert character.name == "Test"
```

### Utilisation des fixtures

Les fixtures définies dans `conftest.py` peuvent être utilisées :

```python
def test_with_project_service(project_service):
    """Utilise la fixture project_service"""
    service = project_service.character_service
    # ...
```

### Tests avec mocks

```python
from unittest.mock import Mock, patch

def test_with_mock():
    """Exemple avec mock"""
    mock_service = Mock()
    mock_service.method.return_value = "test"
    # ...
```

## Bonnes pratiques

1. **Nommage** : Les fonctions de test doivent commencer par `test_`
2. **Documentation** : Chaque test doit avoir une docstring explicative
3. **Isolation** : Chaque test doit être indépendant
4. **Assertions claires** : Utiliser des messages d'assertion explicites
5. **Fixtures** : Réutiliser les fixtures pour éviter la duplication

## Marqueurs pytest

Des marqueurs sont disponibles pour catégoriser les tests :

- `@pytest.mark.unit` - Tests unitaires
- `@pytest.mark.integration` - Tests d'intégration
- `@pytest.mark.slow` - Tests lents

Exemple :
```python
@pytest.mark.slow
def test_long_running_operation():
    # ...
```

Exécuter seulement les tests unitaires :
```bash
pytest -m unit
```

