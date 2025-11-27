"""Tests for IModel interface.

Tests the IModel interface defined in T.Database.models.base.
Ensures the interface follows the Interface Segregation Principle and
can be properly implemented by concrete model classes.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

import pytest
from abc import ABC
from typing import Optional

from T.Database.models.base import IModel


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
        self._deleted = False
    
    def get_id(self) -> Optional[str]:
        """Return the model's identifier."""
        return self._id
    
    def save(self) -> bool:
        """Persist the model."""
        if self._id is None:
            self._id = "generated-id"
        self._saved = True
        return True
    
    def delete(self) -> bool:
        """Remove the model from persistence."""
        if self._id is None:
            return False
        self._deleted = True
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
    
    def get_id(self) -> Optional[int]:
        """Return the integer identifier."""
        return self._id
    
    def save(self) -> bool:
        """Persist the model."""
        if self._id is None:
            self._id = 1
        return True
    
    def delete(self) -> bool:
        """Remove the model."""
        return self._id is not None
    
    def refresh(self) -> bool:
        """Reload the model."""
        return self._id is not None


class TestIModelInterface:
    """Tests for IModel interface definition."""
    
    def test_imodel_is_abstract_base_class(self):
        """Test that IModel is an abstract base class."""
        assert issubclass(IModel, ABC)
    
    def test_cannot_instantiate_imodel_directly(self):
        """Test that IModel cannot be instantiated directly."""
        with pytest.raises(TypeError):
            IModel()
    
    def test_imodel_has_get_id_method(self):
        """Test that IModel defines get_id abstract method."""
        assert hasattr(IModel, 'get_id')
        assert callable(getattr(IModel, 'get_id'))
    
    def test_imodel_has_save_method(self):
        """Test that IModel defines save abstract method."""
        assert hasattr(IModel, 'save')
        assert callable(getattr(IModel, 'save'))
    
    def test_imodel_has_delete_method(self):
        """Test that IModel defines delete abstract method."""
        assert hasattr(IModel, 'delete')
        assert callable(getattr(IModel, 'delete'))
    
    def test_imodel_has_refresh_method(self):
        """Test that IModel defines refresh abstract method."""
        assert hasattr(IModel, 'refresh')
        assert callable(getattr(IModel, 'refresh'))


class TestConcreteModelImplementation:
    """Tests for concrete IModel implementation."""
    
    def test_create_concrete_model(self):
        """Test creating a concrete model instance."""
        model = ConcreteModel()
        
        assert model is not None
        assert isinstance(model, IModel)
    
    def test_get_id_returns_none_for_new_model(self):
        """Test that get_id returns None for a new unsaved model."""
        model = ConcreteModel()
        
        assert model.get_id() is None
    
    def test_get_id_returns_id_for_existing_model(self):
        """Test that get_id returns the correct ID for an existing model."""
        model = ConcreteModel(id="existing-id", data="test data")
        
        assert model.get_id() == "existing-id"
    
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
    
    def test_save_preserves_existing_id(self):
        """Test that save preserves an existing ID."""
        model = ConcreteModel(id="my-id", data="test content")
        
        model.save()
        
        assert model.get_id() == "my-id"
    
    def test_delete_returns_true_for_persisted_model(self):
        """Test that delete returns True for a persisted model."""
        model = ConcreteModel(id="existing-id")
        
        result = model.delete()
        
        assert result is True
    
    def test_delete_returns_false_for_new_model(self):
        """Test that delete returns False for an unsaved model."""
        model = ConcreteModel()
        
        result = model.delete()
        
        assert result is False
    
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
    
    def test_interface_only_defines_crud_methods(self):
        """Test that interface only has CRUD methods."""
        # Get all public methods from IModel (excluding dunder methods)
        imodel_methods = [
            method for method in dir(IModel)
            if not method.startswith('_') and callable(getattr(IModel, method))
        ]
        
        # IModel should only define these four methods for interface segregation
        expected_methods = {'get_id', 'save', 'delete', 'refresh'}
        
        # Note: ABC may add additional methods, so we check that our methods exist
        assert expected_methods.issubset(set(imodel_methods))
    
    def test_interface_does_not_contain_query_methods(self):
        """Test that IModel interface has no query-related methods."""
        # Query methods that should NOT exist in IModel (ISP)
        query_methods = ['find', 'find_all', 'find_by', 'query', 'search', 'filter']
        
        for method in query_methods:
            assert not hasattr(IModel, method), \
                f"IModel should not have '{method}' method (Interface Segregation)"
    
    def test_interface_does_not_contain_relationship_methods(self):
        """Test that IModel interface has no relationship methods."""
        # Relationship methods that should NOT exist in IModel (ISP)
        relationship_methods = ['get_children', 'get_parent', 'add_child', 'join']
        
        for method in relationship_methods:
            assert not hasattr(IModel, method), \
                f"IModel should not have '{method}' method (Interface Segregation)"
    
    def test_interface_does_not_contain_validation_methods(self):
        """Test that IModel interface has no validation methods."""
        # Validation methods that should NOT exist in IModel (ISP)
        validation_methods = ['validate', 'is_valid', 'get_errors']
        
        for method in validation_methods:
            assert not hasattr(IModel, method), \
                f"IModel should not have '{method}' method (Interface Segregation)"
    
    def test_interface_does_not_contain_transaction_methods(self):
        """Test that IModel interface has no transaction methods."""
        # Transaction methods that should NOT exist in IModel (ISP)
        transaction_methods = ['begin_transaction', 'commit', 'rollback']
        
        for method in transaction_methods:
            assert not hasattr(IModel, method), \
                f"IModel should not have '{method}' method (Interface Segregation)"


class TestModelWorkflowExamples:
    """Tests demonstrating typical model usage workflows."""
    
    def test_create_and_save_new_model(self):
        """Test creating and saving a new model."""
        model = ConcreteModel(data="New content")
        
        assert model.get_id() is None
        
        save_result = model.save()
        
        assert save_result is True
        assert model.get_id() is not None
    
    def test_update_existing_model(self):
        """Test updating an existing model."""
        model = ConcreteModel(id="existing-123", data="Original content")
        
        # Simulate updating the model
        model._data = "Updated content"
        save_result = model.save()
        
        assert save_result is True
        assert model.get_id() == "existing-123"
        assert model.data == "Updated content"
    
    def test_delete_existing_model(self):
        """Test deleting an existing model."""
        model = ConcreteModel(id="to-delete-456", data="Content to delete")
        
        delete_result = model.delete()
        
        assert delete_result is True
    
    def test_refresh_model_from_database(self):
        """Test refreshing model data from database."""
        model = ConcreteModel(id="refresh-789", data="Stale content")
        
        refresh_result = model.refresh()
        
        assert refresh_result is True
    
    def test_cannot_delete_unsaved_model(self):
        """Test that deleting an unsaved model returns False."""
        model = ConcreteModel(data="Never saved")
        
        delete_result = model.delete()
        
        assert delete_result is False
    
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
                def save(self) -> bool:
                    return True
                def delete(self) -> bool:
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
                def delete(self) -> bool:
                    return True
                def refresh(self) -> bool:
                    return True
            
            IncompleteModel()
    
    def test_missing_delete_raises_error(self):
        """Test that missing delete implementation raises TypeError."""
        with pytest.raises(TypeError):
            class IncompleteModel(IModel[str]):
                def get_id(self) -> Optional[str]:
                    return None
                def save(self) -> bool:
                    return True
                def refresh(self) -> bool:
                    return True
            
            IncompleteModel()
    
    def test_missing_refresh_raises_error(self):
        """Test that missing refresh implementation raises TypeError."""
        with pytest.raises(TypeError):
            class IncompleteModel(IModel[str]):
                def get_id(self) -> Optional[str]:
                    return None
                def save(self) -> bool:
                    return True
                def delete(self) -> bool:
                    return True
            
            IncompleteModel()
