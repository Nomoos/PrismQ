"""Tests for IRepository and IVersionedRepository interfaces.

Tests the repository interfaces defined in T.Database.repositories.base.
Ensures the interfaces follow the Interface Segregation Principle and
can be properly implemented by concrete repository classes.
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict


def _find_project_root() -> Path:
    """Find project root by looking for pytest.ini marker file."""
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        if (parent / 'pytest.ini').exists():
            return parent
    # Fallback to parents[5] for compatibility
    return Path(__file__).resolve().parents[5]


# Add project root to path
project_root = _find_project_root()
sys.path.insert(0, str(project_root))

import pytest
from abc import ABC
from datetime import datetime

from T.Database.repositories.base import IRepository, IVersionedRepository


# === Test Entity Classes ===

class SimpleEntity:
    """Simple entity for testing IRepository."""
    
    def __init__(self, id: Optional[str] = None, name: str = ""):
        self.id = id
        self.name = name
        self.created_at: Optional[datetime] = None


class VersionedEntity:
    """Versioned entity for testing IVersionedRepository."""
    
    def __init__(self, id: Optional[str] = None, name: str = "", version: int = 0):
        self.id = id
        self.name = name
        self.version = version
        self.created_at: Optional[datetime] = None


# === Concrete Repository Implementations for Testing ===

class ConcreteRepository(IRepository[SimpleEntity, str]):
    """Concrete implementation of IRepository for testing."""
    
    def __init__(self):
        self._storage: Dict[str, SimpleEntity] = {}
        self._id_counter = 0
    
    def find_by_id(self, id: str) -> Optional[SimpleEntity]:
        return self._storage.get(id)
    
    def find_all(self) -> List[SimpleEntity]:
        return list(self._storage.values())
    
    def exists(self, id: str) -> bool:
        return id in self._storage
    
    def insert(self, entity: SimpleEntity) -> SimpleEntity:
        if entity.id is None:
            self._id_counter += 1
            entity.id = f"entity-{self._id_counter}"
        entity.created_at = datetime.now()
        self._storage[entity.id] = entity
        return entity


class ConcreteVersionedRepository(IVersionedRepository[VersionedEntity, str]):
    """Concrete implementation of IVersionedRepository for testing."""
    
    def __init__(self):
        # Storage: {entity_id: {version: entity}}
        self._storage: Dict[str, Dict[int, VersionedEntity]] = {}
        self._id_counter = 0
    
    def find_by_id(self, id: str) -> Optional[VersionedEntity]:
        """Find by exact ID (returns latest version)."""
        return self.find_latest_version(id)
    
    def find_all(self) -> List[VersionedEntity]:
        """Return all latest versions."""
        result = []
        for entity_id in self._storage:
            latest = self.find_latest_version(entity_id)
            if latest:
                result.append(latest)
        return result
    
    def exists(self, id: str) -> bool:
        return id in self._storage and len(self._storage[id]) > 0
    
    def insert(self, entity: VersionedEntity) -> VersionedEntity:
        if entity.id is None:
            self._id_counter += 1
            entity.id = f"entity-{self._id_counter}"
        
        if entity.id not in self._storage:
            self._storage[entity.id] = {}
        
        # Assign next version number
        existing_versions = self._storage[entity.id]
        new_version = max(existing_versions.keys(), default=0) + 1
        entity.version = new_version
        entity.created_at = datetime.now()
        
        self._storage[entity.id][new_version] = entity
        return entity
    
    def find_latest_version(self, id: str) -> Optional[VersionedEntity]:
        if id not in self._storage or not self._storage[id]:
            return None
        latest_version = max(self._storage[id].keys())
        return self._storage[id][latest_version]
    
    def find_versions(self, id: str) -> List[VersionedEntity]:
        if id not in self._storage:
            return []
        return [self._storage[id][v] for v in sorted(self._storage[id].keys())]
    
    def find_version(self, id: str, version: int) -> Optional[VersionedEntity]:
        if id not in self._storage:
            return None
        return self._storage[id].get(version)


# === Test Classes ===

class TestIRepositoryInterface:
    """Tests for IRepository interface definition."""
    
    def test_irepository_is_abstract_base_class(self):
        """Test that IRepository is an abstract base class."""
        assert issubclass(IRepository, ABC)
    
    def test_cannot_instantiate_irepository_directly(self):
        """Test that IRepository cannot be instantiated directly."""
        with pytest.raises(TypeError):
            IRepository()
    
    def test_irepository_has_find_by_id_method(self):
        """Test that IRepository defines find_by_id abstract method."""
        assert hasattr(IRepository, 'find_by_id')
        assert callable(getattr(IRepository, 'find_by_id'))
    
    def test_irepository_has_find_all_method(self):
        """Test that IRepository defines find_all abstract method."""
        assert hasattr(IRepository, 'find_all')
        assert callable(getattr(IRepository, 'find_all'))
    
    def test_irepository_has_exists_method(self):
        """Test that IRepository defines exists abstract method."""
        assert hasattr(IRepository, 'exists')
        assert callable(getattr(IRepository, 'exists'))
    
    def test_irepository_has_insert_method(self):
        """Test that IRepository defines insert abstract method."""
        assert hasattr(IRepository, 'insert')
        assert callable(getattr(IRepository, 'insert'))
    
    def test_irepository_does_not_have_update_method(self):
        """Test that IRepository does NOT have update method (Insert+Read only)."""
        irepository_methods = [
            method for method in dir(IRepository)
            if not method.startswith('_') and callable(getattr(IRepository, method))
        ]
        assert 'update' not in irepository_methods
    
    def test_irepository_does_not_have_delete_method(self):
        """Test that IRepository does NOT have delete method (Insert+Read only)."""
        irepository_methods = [
            method for method in dir(IRepository)
            if not method.startswith('_') and callable(getattr(IRepository, method))
        ]
        assert 'delete' not in irepository_methods


class TestIVersionedRepositoryInterface:
    """Tests for IVersionedRepository interface definition."""
    
    def test_iversionedrepository_is_abstract_base_class(self):
        """Test that IVersionedRepository is an abstract base class."""
        assert issubclass(IVersionedRepository, ABC)
    
    def test_iversionedrepository_extends_irepository(self):
        """Test that IVersionedRepository extends IRepository."""
        assert issubclass(IVersionedRepository, IRepository)
    
    def test_cannot_instantiate_iversionedrepository_directly(self):
        """Test that IVersionedRepository cannot be instantiated directly."""
        with pytest.raises(TypeError):
            IVersionedRepository()
    
    def test_iversionedrepository_has_find_latest_version_method(self):
        """Test that IVersionedRepository defines find_latest_version."""
        assert hasattr(IVersionedRepository, 'find_latest_version')
        assert callable(getattr(IVersionedRepository, 'find_latest_version'))
    
    def test_iversionedrepository_has_find_versions_method(self):
        """Test that IVersionedRepository defines find_versions."""
        assert hasattr(IVersionedRepository, 'find_versions')
        assert callable(getattr(IVersionedRepository, 'find_versions'))
    
    def test_iversionedrepository_has_find_version_method(self):
        """Test that IVersionedRepository defines find_version."""
        assert hasattr(IVersionedRepository, 'find_version')
        assert callable(getattr(IVersionedRepository, 'find_version'))


class TestConcreteRepositoryImplementation:
    """Tests for concrete IRepository implementation."""
    
    def test_create_concrete_repository(self):
        """Test creating a concrete repository instance."""
        repo = ConcreteRepository()
        assert repo is not None
        assert isinstance(repo, IRepository)
    
    def test_insert_returns_entity_with_id(self):
        """Test that insert assigns an ID to new entity."""
        repo = ConcreteRepository()
        entity = SimpleEntity(name="Test")
        
        result = repo.insert(entity)
        
        assert result.id is not None
        assert result.id.startswith("entity-")
    
    def test_insert_sets_created_at(self):
        """Test that insert sets created_at timestamp."""
        repo = ConcreteRepository()
        entity = SimpleEntity(name="Test")
        
        result = repo.insert(entity)
        
        assert result.created_at is not None
        assert isinstance(result.created_at, datetime)
    
    def test_find_by_id_returns_entity(self):
        """Test that find_by_id returns inserted entity."""
        repo = ConcreteRepository()
        entity = repo.insert(SimpleEntity(name="Test"))
        
        result = repo.find_by_id(entity.id)
        
        assert result is not None
        assert result.id == entity.id
        assert result.name == "Test"
    
    def test_find_by_id_returns_none_for_missing(self):
        """Test that find_by_id returns None for missing ID."""
        repo = ConcreteRepository()
        
        result = repo.find_by_id("nonexistent")
        
        assert result is None
    
    def test_find_all_returns_all_entities(self):
        """Test that find_all returns all inserted entities."""
        repo = ConcreteRepository()
        repo.insert(SimpleEntity(name="First"))
        repo.insert(SimpleEntity(name="Second"))
        
        result = repo.find_all()
        
        assert len(result) == 2
        names = [e.name for e in result]
        assert "First" in names
        assert "Second" in names
    
    def test_find_all_returns_empty_list_when_empty(self):
        """Test that find_all returns empty list when no entities."""
        repo = ConcreteRepository()
        
        result = repo.find_all()
        
        assert result == []
    
    def test_exists_returns_true_for_existing(self):
        """Test that exists returns True for existing ID."""
        repo = ConcreteRepository()
        entity = repo.insert(SimpleEntity(name="Test"))
        
        result = repo.exists(entity.id)
        
        assert result is True
    
    def test_exists_returns_false_for_missing(self):
        """Test that exists returns False for missing ID."""
        repo = ConcreteRepository()
        
        result = repo.exists("nonexistent")
        
        assert result is False


class TestConcreteVersionedRepositoryImplementation:
    """Tests for concrete IVersionedRepository implementation."""
    
    def test_create_versioned_repository(self):
        """Test creating a versioned repository instance."""
        repo = ConcreteVersionedRepository()
        assert repo is not None
        assert isinstance(repo, IVersionedRepository)
        assert isinstance(repo, IRepository)
    
    def test_insert_creates_version_1(self):
        """Test that first insert creates version 1."""
        repo = ConcreteVersionedRepository()
        entity = VersionedEntity(name="Test")
        
        result = repo.insert(entity)
        
        assert result.version == 1
    
    def test_insert_increments_version(self):
        """Test that subsequent inserts increment version."""
        repo = ConcreteVersionedRepository()
        entity1 = repo.insert(VersionedEntity(id="test-1", name="V1"))
        entity2 = repo.insert(VersionedEntity(id="test-1", name="V2"))
        
        assert entity1.version == 1
        assert entity2.version == 2
    
    def test_find_latest_version_returns_newest(self):
        """Test that find_latest_version returns the newest version."""
        repo = ConcreteVersionedRepository()
        repo.insert(VersionedEntity(id="test-1", name="V1"))
        repo.insert(VersionedEntity(id="test-1", name="V2"))
        repo.insert(VersionedEntity(id="test-1", name="V3"))
        
        result = repo.find_latest_version("test-1")
        
        assert result is not None
        assert result.version == 3
        assert result.name == "V3"
    
    def test_find_latest_version_returns_none_for_missing(self):
        """Test that find_latest_version returns None for missing ID."""
        repo = ConcreteVersionedRepository()
        
        result = repo.find_latest_version("nonexistent")
        
        assert result is None
    
    def test_find_versions_returns_all_in_order(self):
        """Test that find_versions returns all versions in ascending order."""
        repo = ConcreteVersionedRepository()
        repo.insert(VersionedEntity(id="test-1", name="V1"))
        repo.insert(VersionedEntity(id="test-1", name="V2"))
        repo.insert(VersionedEntity(id="test-1", name="V3"))
        
        result = repo.find_versions("test-1")
        
        assert len(result) == 3
        assert result[0].version == 1
        assert result[1].version == 2
        assert result[2].version == 3
    
    def test_find_versions_returns_empty_for_missing(self):
        """Test that find_versions returns empty list for missing ID."""
        repo = ConcreteVersionedRepository()
        
        result = repo.find_versions("nonexistent")
        
        assert result == []
    
    def test_find_version_returns_specific_version(self):
        """Test that find_version returns the specific version."""
        repo = ConcreteVersionedRepository()
        repo.insert(VersionedEntity(id="test-1", name="V1"))
        repo.insert(VersionedEntity(id="test-1", name="V2"))
        repo.insert(VersionedEntity(id="test-1", name="V3"))
        
        result = repo.find_version("test-1", 2)
        
        assert result is not None
        assert result.version == 2
        assert result.name == "V2"
    
    def test_find_version_returns_none_for_missing_version(self):
        """Test that find_version returns None for missing version."""
        repo = ConcreteVersionedRepository()
        repo.insert(VersionedEntity(id="test-1", name="V1"))
        
        result = repo.find_version("test-1", 99)
        
        assert result is None
    
    def test_find_version_returns_none_for_missing_id(self):
        """Test that find_version returns None for missing ID."""
        repo = ConcreteVersionedRepository()
        
        result = repo.find_version("nonexistent", 1)
        
        assert result is None


class TestInterfaceSegregation:
    """Tests verifying Interface Segregation Principle compliance."""
    
    def test_irepository_only_defines_insert_read_methods(self):
        """Test that IRepository only has Insert+Read methods."""
        irepository_methods = [
            method for method in dir(IRepository)
            if not method.startswith('_') and callable(getattr(IRepository, method))
        ]
        
        expected_methods = {'find_by_id', 'find_all', 'exists', 'insert'}
        assert expected_methods.issubset(set(irepository_methods))
    
    def test_iversionedrepository_adds_version_methods(self):
        """Test that IVersionedRepository adds version-specific methods."""
        iversioned_methods = [
            method for method in dir(IVersionedRepository)
            if not method.startswith('_') and callable(getattr(IVersionedRepository, method))
        ]
        
        version_methods = {'find_latest_version', 'find_versions', 'find_version'}
        assert version_methods.issubset(set(iversioned_methods))
    
    def test_no_update_methods(self):
        """Test that neither interface has update methods (Insert+Read only)."""
        update_methods = ['update', 'save', 'upsert', 'modify']
        
        for method in update_methods:
            assert not hasattr(IRepository, method) or not callable(getattr(IRepository, method, None))
            assert not hasattr(IVersionedRepository, method) or not callable(getattr(IVersionedRepository, method, None))
    
    def test_no_delete_methods(self):
        """Test that neither interface has delete methods (Insert+Read only)."""
        delete_methods = ['delete', 'remove', 'destroy', 'soft_delete']
        
        for method in delete_methods:
            assert not hasattr(IRepository, method) or not callable(getattr(IRepository, method, None))
            assert not hasattr(IVersionedRepository, method) or not callable(getattr(IVersionedRepository, method, None))


class TestPartialImplementation:
    """Tests ensuring partial implementations fail correctly."""
    
    def test_missing_find_by_id_raises_error(self):
        """Test that missing find_by_id raises TypeError."""
        with pytest.raises(TypeError):
            class IncompleteRepo(IRepository[SimpleEntity, str]):
                def find_all(self) -> List[SimpleEntity]:
                    return []
                def exists(self, id: str) -> bool:
                    return False
                def insert(self, entity: SimpleEntity) -> SimpleEntity:
                    return entity
            
            IncompleteRepo()
    
    def test_missing_insert_raises_error(self):
        """Test that missing insert raises TypeError."""
        with pytest.raises(TypeError):
            class IncompleteRepo(IRepository[SimpleEntity, str]):
                def find_by_id(self, id: str) -> Optional[SimpleEntity]:
                    return None
                def find_all(self) -> List[SimpleEntity]:
                    return []
                def exists(self, id: str) -> bool:
                    return False
            
            IncompleteRepo()
    
    def test_missing_versioned_method_raises_error(self):
        """Test that missing versioned method raises TypeError."""
        with pytest.raises(TypeError):
            class IncompleteVersionedRepo(IVersionedRepository[VersionedEntity, str]):
                def find_by_id(self, id: str) -> Optional[VersionedEntity]:
                    return None
                def find_all(self) -> List[VersionedEntity]:
                    return []
                def exists(self, id: str) -> bool:
                    return False
                def insert(self, entity: VersionedEntity) -> VersionedEntity:
                    return entity
                def find_latest_version(self, id: str) -> Optional[VersionedEntity]:
                    return None
                def find_versions(self, id: str) -> List[VersionedEntity]:
                    return []
                # Missing find_version
            
            IncompleteVersionedRepo()


class TestRepositoryWorkflowExamples:
    """Tests demonstrating typical repository usage workflows."""
    
    def test_insert_and_retrieve_workflow(self):
        """Test basic insert and retrieve workflow."""
        repo = ConcreteRepository()
        
        # Insert new entity
        entity = SimpleEntity(name="Test Content")
        inserted = repo.insert(entity)
        
        # Verify it exists
        assert repo.exists(inserted.id) is True
        
        # Retrieve it
        retrieved = repo.find_by_id(inserted.id)
        assert retrieved is not None
        assert retrieved.name == "Test Content"
    
    def test_versioned_content_workflow(self):
        """Test versioned content workflow (like Title or Script)."""
        repo = ConcreteVersionedRepository()
        
        # Create initial version
        v1 = repo.insert(VersionedEntity(id="content-1", name="Original Title"))
        assert v1.version == 1
        
        # Create updated version (instead of update)
        v2 = repo.insert(VersionedEntity(id="content-1", name="Improved Title"))
        assert v2.version == 2
        
        # Latest version should be v2
        latest = repo.find_latest_version("content-1")
        assert latest.name == "Improved Title"
        
        # But v1 is still accessible
        original = repo.find_version("content-1", 1)
        assert original.name == "Original Title"
        
        # All versions are available
        all_versions = repo.find_versions("content-1")
        assert len(all_versions) == 2
    
    def test_list_all_latest_versions(self):
        """Test listing all latest versions of entities."""
        repo = ConcreteVersionedRepository()
        
        # Create multiple entities with versions
        repo.insert(VersionedEntity(id="title-1", name="Title 1 v1"))
        repo.insert(VersionedEntity(id="title-1", name="Title 1 v2"))
        repo.insert(VersionedEntity(id="title-2", name="Title 2 v1"))
        
        # find_all returns latest versions only
        all_entities = repo.find_all()
        
        assert len(all_entities) == 2
        names = [e.name for e in all_entities]
        assert "Title 1 v2" in names
        assert "Title 2 v1" in names
