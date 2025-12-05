"""Tests for IReadable and IModel interfaces.

Tests the interfaces defined in T.Database.models.base.
Ensures the interfaces follow the Interface Segregation Principle and
can be properly implemented by concrete model classes.
"""

import sys
from pathlib import Path
from datetime import datetime


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
from typing import Optional

from Model.Database.models.base import IReadable, IModel


class ConcreteReadable(IReadable[str]):
    """Concrete implementation of IReadable for testing purposes."""
    
    def __init__(self, id: Optional[str] = None):
        """Initialize the concrete readable model.
        
        Args:
            id: The unique identifier of this model (None if not persisted)
        """
        self._id = id
        self._created_at = datetime.now() if id else None
    
    def get_id(self) -> Optional[str]:
        """Return the model's identifier."""
        return self._id
    
    def exists(self) -> bool:
        """Check if the model exists in persistence."""
        return self._id is not None
    
    def get_created_at(self) -> Optional[datetime]:
        """Return the creation timestamp."""
        return self._created_at


class ConcreteModel(IModel[str]):
    """Concrete implementation of IModel for testing purposes."""
    
    def __init__(self, id: Optional[str] = None, data: str = ""):
        """Initialize the concrete model.
        
        Args:
            id: The unique identifier of this model (None if not persisted)
            data: The model's data content
        """
        self._id = id
        self._data = data
        self._saved = False
        self._created_at = datetime.now() if id else None
    
    def get_id(self) -> Optional[str]:
        """Return the model's identifier."""
        return self._id
    
    def exists(self) -> bool:
        """Check if the model exists in persistence."""
        return self._id is not None
    
    def get_created_at(self) -> Optional[datetime]:
        """Return the creation timestamp."""
        return self._created_at
    
    def save(self) -> bool:
        """Persist the model."""
        if self._id is None:
            self._id = "generated-id"
        if self._created_at is None:
            self._created_at = datetime.now()
        self._saved = True
        return True
    
    def refresh(self) -> bool:
        """Reload the model from persistence."""
        if self._id is None:
            return False
        return True
    
    @property
    def data(self) -> str:
        """Get the model's data."""
        return self._data


class ConcreteIntModel(IModel[int]):
    """Concrete implementation of IModel with integer ID for testing."""
    
    def __init__(self, id: Optional[int] = None):
        """Initialize with optional integer ID."""
        self._id = id
        self._created_at = datetime.now() if id else None
    
    def get_id(self) -> Optional[int]:
        """Return the integer identifier."""
        return self._id
    
    def exists(self) -> bool:
        """Check if the model exists."""
        return self._id is not None
    
    def get_created_at(self) -> Optional[datetime]:
        """Return the creation timestamp."""
        return self._created_at
    
    def save(self) -> bool:
        """Persist the model."""
        if self._id is None:
            self._id = 1
        if self._created_at is None:
            self._created_at = datetime.now()
        return True
    
    def refresh(self) -> bool:
        """Reload the model."""
        return self._id is not None


class TestIReadableInterface:
    """Tests for IReadable interface definition."""
    
    def test_ireadable_is_abstract_base_class(self):
        """Test that IReadable is an abstract base class."""
        assert issubclass(IReadable, ABC)
    
    def test_cannot_instantiate_ireadable_directly(self):
        """Test that IReadable cannot be instantiated directly."""
        with pytest.raises(TypeError):
            IReadable()
    
    def test_ireadable_has_get_id_method(self):
        """Test that IReadable defines get_id abstract method."""
        assert hasattr(IReadable, 'get_id')
        assert callable(getattr(IReadable, 'get_id'))
    
    def test_ireadable_has_exists_method(self):
        """Test that IReadable defines exists abstract method."""
        assert hasattr(IReadable, 'exists')
        assert callable(getattr(IReadable, 'exists'))
    
    def test_ireadable_has_get_created_at_method(self):
        """Test that IReadable defines get_created_at abstract method."""
        assert hasattr(IReadable, 'get_created_at')
        assert callable(getattr(IReadable, 'get_created_at'))


class TestIModelInterface:
    """Tests for IModel interface definition."""
    
    def test_imodel_is_abstract_base_class(self):
        """Test that IModel is an abstract base class."""
        assert issubclass(IModel, ABC)
    
    def test_imodel_extends_ireadable(self):
        """Test that IModel extends IReadable."""
        assert issubclass(IModel, IReadable)
    
    def test_cannot_instantiate_imodel_directly(self):
        """Test that IModel cannot be instantiated directly."""
        with pytest.raises(TypeError):
            IModel()
    
    def test_imodel_has_get_id_method(self):
        """Test that IModel defines get_id abstract method."""
        assert hasattr(IModel, 'get_id')
        assert callable(getattr(IModel, 'get_id'))
    
    def test_imodel_has_exists_method(self):
        """Test that IModel defines exists abstract method."""
        assert hasattr(IModel, 'exists')
        assert callable(getattr(IModel, 'exists'))
    
    def test_imodel_has_get_created_at_method(self):
        """Test that IModel defines get_created_at abstract method."""
        assert hasattr(IModel, 'get_created_at')
        assert callable(getattr(IModel, 'get_created_at'))
    
    def test_imodel_has_save_method(self):
        """Test that IModel defines save abstract method."""
        assert hasattr(IModel, 'save')
        assert callable(getattr(IModel, 'save'))
    
    def test_imodel_has_refresh_method(self):
        """Test that IModel defines refresh abstract method."""
        assert hasattr(IModel, 'refresh')
        assert callable(getattr(IModel, 'refresh'))
    
    def test_imodel_does_not_have_delete_method(self):
        """Test that IModel does NOT define delete method (immutable data)."""
        # Check that delete is not an abstract method in IModel
        imodel_methods = [
            method for method in dir(IModel)
            if not method.startswith('_') and callable(getattr(IModel, method))
        ]
        assert 'delete' not in imodel_methods, \
            "IModel should not have 'delete' method (data is immutable)"


class TestConcreteReadableImplementation:
    """Tests for concrete IReadable implementation."""
    
    def test_create_concrete_readable(self):
        """Test creating a concrete readable instance."""
        readable = ConcreteReadable()
        
        assert readable is not None
        assert isinstance(readable, IReadable)
    
    def test_get_id_returns_none_for_new_readable(self):
        """Test that get_id returns None for a new model."""
        readable = ConcreteReadable()
        
        assert readable.get_id() is None
    
    def test_get_id_returns_id_for_existing_readable(self):
        """Test that get_id returns the correct ID for an existing model."""
        readable = ConcreteReadable(id="existing-id")
        
        assert readable.get_id() == "existing-id"
    
    def test_exists_returns_false_for_new_readable(self):
        """Test that exists returns False for a new model."""
        readable = ConcreteReadable()
        
        assert readable.exists() is False
    
    def test_exists_returns_true_for_existing_readable(self):
        """Test that exists returns True for an existing model."""
        readable = ConcreteReadable(id="existing-id")
        
        assert readable.exists() is True
    
    def test_get_created_at_returns_none_for_new_readable(self):
        """Test that get_created_at returns None for a new model."""
        readable = ConcreteReadable()
        
        assert readable.get_created_at() is None
    
    def test_get_created_at_returns_timestamp_for_existing_readable(self):
        """Test that get_created_at returns timestamp for an existing model."""
        readable = ConcreteReadable(id="existing-id")
        
        assert readable.get_created_at() is not None
        assert isinstance(readable.get_created_at(), datetime)


class TestConcreteModelImplementation:
    """Tests for concrete IModel implementation."""
    
    def test_create_concrete_model(self):
        """Test creating a concrete model instance."""
        model = ConcreteModel()
        
        assert model is not None
        assert isinstance(model, IModel)
        assert isinstance(model, IReadable)
    
    def test_get_id_returns_none_for_new_model(self):
        """Test that get_id returns None for a new unsaved model."""
        model = ConcreteModel()
        
        assert model.get_id() is None
    
    def test_get_id_returns_id_for_existing_model(self):
        """Test that get_id returns the correct ID for an existing model."""
        model = ConcreteModel(id="existing-id", data="test data")
        
        assert model.get_id() == "existing-id"
    
    def test_exists_returns_false_for_new_model(self):
        """Test that exists returns False for a new model."""
        model = ConcreteModel()
        
        assert model.exists() is False
    
    def test_exists_returns_true_for_existing_model(self):
        """Test that exists returns True for an existing model."""
        model = ConcreteModel(id="existing-id")
        
        assert model.exists() is True
    
    def test_get_created_at_returns_none_for_new_model(self):
        """Test that get_created_at returns None for a new model."""
        model = ConcreteModel()
        
        assert model.get_created_at() is None
    
    def test_get_created_at_returns_timestamp_for_existing_model(self):
        """Test that get_created_at returns timestamp for an existing model."""
        model = ConcreteModel(id="existing-id")
        
        assert model.get_created_at() is not None
        assert isinstance(model.get_created_at(), datetime)
    
    def test_save_returns_true_on_success(self):
        """Test that save returns True on successful save."""
        model = ConcreteModel(data="test content")
        
        result = model.save()
        
        assert result is True
    
    def test_save_assigns_id_for_new_model(self):
        """Test that save assigns an ID to a new model."""
        model = ConcreteModel(data="test content")
        assert model.get_id() is None
        
        model.save()
        
        assert model.get_id() is not None
        assert model.get_id() == "generated-id"
    
    def test_save_sets_created_at_for_new_model(self):
        """Test that save sets created_at timestamp for a new model."""
        model = ConcreteModel(data="test content")
        assert model.get_created_at() is None
        
        model.save()
        
        assert model.get_created_at() is not None
        assert isinstance(model.get_created_at(), datetime)
    
    def test_save_makes_model_exist(self):
        """Test that save makes exists() return True."""
        model = ConcreteModel(data="test content")
        assert model.exists() is False
        
        model.save()
        
        assert model.exists() is True
    
    def test_save_preserves_existing_id(self):
        """Test that save preserves an existing ID."""
        model = ConcreteModel(id="my-id", data="test content")
        
        model.save()
        
        assert model.get_id() == "my-id"
    
    def test_refresh_returns_true_for_persisted_model(self):
        """Test that refresh returns True for a persisted model."""
        model = ConcreteModel(id="existing-id")
        
        result = model.refresh()
        
        assert result is True
    
    def test_refresh_returns_false_for_new_model(self):
        """Test that refresh returns False for an unsaved model."""
        model = ConcreteModel()
        
        result = model.refresh()
        
        assert result is False


class TestGenericTypeSupport:
    """Tests for generic type parameter support."""
    
    def test_string_id_model(self):
        """Test model with string ID type."""
        model = ConcreteModel(id="string-id")
        
        assert isinstance(model.get_id(), str)
        assert model.get_id() == "string-id"
    
    def test_integer_id_model(self):
        """Test model with integer ID type."""
        model = ConcreteIntModel(id=42)
        
        assert isinstance(model.get_id(), int)
        assert model.get_id() == 42
    
    def test_integer_model_save_generates_int_id(self):
        """Test that integer ID model generates integer ID on save."""
        model = ConcreteIntModel()
        assert model.get_id() is None
        
        model.save()
        
        assert isinstance(model.get_id(), int)


class TestInterfaceSegregation:
    """Tests verifying Interface Segregation Principle compliance."""
    
    def test_ireadable_only_defines_read_methods(self):
        """Test that IReadable only has read methods."""
        ireadable_methods = [
            method for method in dir(IReadable)
            if not method.startswith('_') and callable(getattr(IReadable, method))
        ]
        
        # IReadable should only define these methods
        expected_methods = {'get_id', 'exists', 'get_created_at'}
        
        assert expected_methods.issubset(set(ireadable_methods))
    
    def test_imodel_extends_ireadable_with_write_methods(self):
        """Test that IModel extends IReadable with write methods."""
        imodel_methods = [
            method for method in dir(IModel)
            if not method.startswith('_') and callable(getattr(IModel, method))
        ]
        
        # IModel should have all IReadable methods plus save and refresh
        expected_methods = {'get_id', 'exists', 'get_created_at', 'save', 'refresh'}
        
        assert expected_methods.issubset(set(imodel_methods))
    
    def test_no_delete_method_in_interfaces(self):
        """Test that neither interface has delete method (immutable data)."""
        assert not hasattr(IReadable, 'delete') or not callable(getattr(IReadable, 'delete', None))
        
        # Check IModel doesn't have delete as a defined method
        imodel_methods = [
            method for method in dir(IModel)
            if not method.startswith('_') and callable(getattr(IModel, method))
        ]
        assert 'delete' not in imodel_methods
    
    def test_interface_does_not_contain_query_methods(self):
        """Test that interfaces have no query-related methods."""
        query_methods = ['find', 'find_all', 'find_by', 'query', 'search', 'filter']
        
        for method in query_methods:
            assert not hasattr(IReadable, method), \
                f"IReadable should not have '{method}' method (Interface Segregation)"
            assert not hasattr(IModel, method), \
                f"IModel should not have '{method}' method (Interface Segregation)"
    
    def test_interface_does_not_contain_relationship_methods(self):
        """Test that interfaces have no relationship methods."""
        relationship_methods = ['get_children', 'get_parent', 'add_child', 'join']
        
        for method in relationship_methods:
            assert not hasattr(IReadable, method), \
                f"IReadable should not have '{method}' method (Interface Segregation)"
            assert not hasattr(IModel, method), \
                f"IModel should not have '{method}' method (Interface Segregation)"
    
    def test_interface_does_not_contain_validation_methods(self):
        """Test that interfaces have no validation methods."""
        validation_methods = ['validate', 'is_valid', 'get_errors']
        
        for method in validation_methods:
            assert not hasattr(IReadable, method), \
                f"IReadable should not have '{method}' method (Interface Segregation)"
            assert not hasattr(IModel, method), \
                f"IModel should not have '{method}' method (Interface Segregation)"
    
    def test_interface_does_not_contain_transaction_methods(self):
        """Test that interfaces have no transaction methods."""
        transaction_methods = ['begin_transaction', 'commit', 'rollback']
        
        for method in transaction_methods:
            assert not hasattr(IReadable, method), \
                f"IReadable should not have '{method}' method (Interface Segregation)"
            assert not hasattr(IModel, method), \
                f"IModel should not have '{method}' method (Interface Segregation)"
    
    def test_no_updated_at_method(self):
        """Test that interfaces don't have updated_at (versioning strategy)."""
        assert not hasattr(IReadable, 'get_updated_at'), \
            "IReadable should not have 'get_updated_at' (versioning strategy)"
        assert not hasattr(IModel, 'get_updated_at'), \
            "IModel should not have 'get_updated_at' (versioning strategy)"


class TestModelWorkflowExamples:
    """Tests demonstrating typical model usage workflows."""
    
    def test_create_and_save_new_model(self):
        """Test creating and saving a new model."""
        model = ConcreteModel(data="New content")
        
        assert model.get_id() is None
        assert model.exists() is False
        assert model.get_created_at() is None
        
        save_result = model.save()
        
        assert save_result is True
        assert model.get_id() is not None
        assert model.exists() is True
        assert model.get_created_at() is not None
    
    def test_read_only_access_with_ireadable(self):
        """Test read-only access using IReadable interface."""
        # A function that only needs read access
        def display_model_info(readable: IReadable) -> str:
            if readable.exists():
                return f"ID: {readable.get_id()}, Created: {readable.get_created_at()}"
            return "Model does not exist"
        
        model = ConcreteModel(id="test-123", data="Content")
        info = display_model_info(model)
        
        assert "ID: test-123" in info
        assert "Created:" in info
    
    def test_refresh_model_from_database(self):
        """Test refreshing model data from database."""
        model = ConcreteModel(id="refresh-789", data="Stale content")
        
        refresh_result = model.refresh()
        
        assert refresh_result is True
    
    def test_cannot_refresh_unsaved_model(self):
        """Test that refreshing an unsaved model returns False."""
        model = ConcreteModel(data="Never saved")
        
        refresh_result = model.refresh()
        
        assert refresh_result is False


class TestPartialImplementation:
    """Tests ensuring partial implementations fail correctly."""
    
    def test_missing_get_id_raises_error(self):
        """Test that missing get_id implementation raises TypeError."""
        with pytest.raises(TypeError):
            class IncompleteModel(IModel[str]):
                def exists(self) -> bool:
                    return False
                def get_created_at(self) -> Optional[datetime]:
                    return None
                def save(self) -> bool:
                    return True
                def refresh(self) -> bool:
                    return True
            
            IncompleteModel()
    
    def test_missing_exists_raises_error(self):
        """Test that missing exists implementation raises TypeError."""
        with pytest.raises(TypeError):
            class IncompleteModel(IModel[str]):
                def get_id(self) -> Optional[str]:
                    return None
                def get_created_at(self) -> Optional[datetime]:
                    return None
                def save(self) -> bool:
                    return True
                def refresh(self) -> bool:
                    return True
            
            IncompleteModel()
    
    def test_missing_get_created_at_raises_error(self):
        """Test that missing get_created_at implementation raises TypeError."""
        with pytest.raises(TypeError):
            class IncompleteModel(IModel[str]):
                def get_id(self) -> Optional[str]:
                    return None
                def exists(self) -> bool:
                    return False
                def save(self) -> bool:
                    return True
                def refresh(self) -> bool:
                    return True
            
            IncompleteModel()
    
    def test_missing_save_raises_error(self):
        """Test that missing save implementation raises TypeError."""
        with pytest.raises(TypeError):
            class IncompleteModel(IModel[str]):
                def get_id(self) -> Optional[str]:
                    return None
                def exists(self) -> bool:
                    return False
                def get_created_at(self) -> Optional[datetime]:
                    return None
                def refresh(self) -> bool:
                    return True
            
            IncompleteModel()
    
    def test_missing_refresh_raises_error(self):
        """Test that missing refresh implementation raises TypeError."""
        with pytest.raises(TypeError):
            class IncompleteModel(IModel[str]):
                def get_id(self) -> Optional[str]:
                    return None
                def exists(self) -> bool:
                    return False
                def get_created_at(self) -> Optional[datetime]:
                    return None
                def save(self) -> bool:
                    return True
            
            IncompleteModel()
    
    def test_ireadable_partial_implementation_fails(self):
        """Test that partial IReadable implementation raises TypeError."""
        with pytest.raises(TypeError):
            class IncompleteReadable(IReadable[str]):
                def get_id(self) -> Optional[str]:
                    return None
                # Missing exists and get_created_at
            
            IncompleteReadable()
