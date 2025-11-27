"""Tests for IState interface.

Tests the IState interface defined in T.State.interfaces.state_interface.
Ensures the interface follows the Single Responsibility Principle and
can be properly implemented by concrete state classes.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

import pytest
from abc import ABC
from typing import List

from T.State.interfaces.state_interface import IState


class ConcreteState(IState):
    """Concrete implementation of IState for testing purposes."""
    
    def __init__(self, name: str, next_states: List[str] = None):
        """Initialize the concrete state.
        
        Args:
            name: The name of this state
            next_states: List of valid next state names (default: empty list)
        """
        self._name = name
        self._next_states = next_states or []
    
    def get_name(self) -> str:
        """Return the state name."""
        return self._name
    
    def get_next_states(self) -> List[str]:
        """Return the list of valid next states."""
        return self._next_states
    
    def can_transition_to(self, target_state: str) -> bool:
        """Check if transition to target state is allowed."""
        return target_state in self._next_states


class TestIStateInterface:
    """Tests for IState interface definition."""
    
    def test_istate_is_abstract_base_class(self):
        """Test that IState is an abstract base class."""
        assert issubclass(IState, ABC)
    
    def test_cannot_instantiate_istate_directly(self):
        """Test that IState cannot be instantiated directly."""
        with pytest.raises(TypeError):
            IState()
    
    def test_istate_has_get_name_method(self):
        """Test that IState defines get_name abstract method."""
        assert hasattr(IState, 'get_name')
        assert callable(getattr(IState, 'get_name'))
    
    def test_istate_has_get_next_states_method(self):
        """Test that IState defines get_next_states abstract method."""
        assert hasattr(IState, 'get_next_states')
        assert callable(getattr(IState, 'get_next_states'))
    
    def test_istate_has_can_transition_to_method(self):
        """Test that IState defines can_transition_to abstract method."""
        assert hasattr(IState, 'can_transition_to')
        assert callable(getattr(IState, 'can_transition_to'))


class TestConcreteStateImplementation:
    """Tests for concrete IState implementation."""
    
    def test_create_concrete_state(self):
        """Test creating a concrete state instance."""
        state = ConcreteState(name="TestState")
        
        assert state is not None
        assert isinstance(state, IState)
    
    def test_get_name_returns_state_name(self):
        """Test that get_name returns the correct state name."""
        state = ConcreteState(name="IdeaCreation")
        
        assert state.get_name() == "IdeaCreation"
    
    def test_get_next_states_returns_empty_list_by_default(self):
        """Test that get_next_states returns empty list when none specified."""
        state = ConcreteState(name="Terminal")
        
        assert state.get_next_states() == []
    
    def test_get_next_states_returns_configured_states(self):
        """Test that get_next_states returns configured next states."""
        state = ConcreteState(
            name="IdeaCreation",
            next_states=["TitleFromIdea"]
        )
        
        assert state.get_next_states() == ["TitleFromIdea"]
    
    def test_get_next_states_returns_multiple_states(self):
        """Test that get_next_states can return multiple next states."""
        state = ConcreteState(
            name="ReviewState",
            next_states=["ApprovedState", "RejectedState"]
        )
        
        next_states = state.get_next_states()
        assert len(next_states) == 2
        assert "ApprovedState" in next_states
        assert "RejectedState" in next_states
    
    def test_can_transition_to_valid_state(self):
        """Test that can_transition_to returns True for valid transitions."""
        state = ConcreteState(
            name="IdeaCreation",
            next_states=["TitleFromIdea", "Archived"]
        )
        
        assert state.can_transition_to("TitleFromIdea") is True
        assert state.can_transition_to("Archived") is True
    
    def test_can_transition_to_invalid_state(self):
        """Test that can_transition_to returns False for invalid transitions."""
        state = ConcreteState(
            name="IdeaCreation",
            next_states=["TitleFromIdea"]
        )
        
        assert state.can_transition_to("Publishing") is False
        assert state.can_transition_to("InvalidState") is False
    
    def test_can_transition_to_with_no_next_states(self):
        """Test can_transition_to for terminal state with no next states."""
        state = ConcreteState(name="Publishing")
        
        assert state.can_transition_to("AnyState") is False
        assert state.can_transition_to("") is False


class TestStateSingleResponsibility:
    """Tests verifying Single Responsibility Principle compliance."""
    
    def test_interface_only_defines_identity_methods(self):
        """Test that interface only has identity and transition methods."""
        # Get all public methods from IState (excluding dunder methods)
        istate_methods = [
            method for method in dir(IState)
            if not method.startswith('_') and callable(getattr(IState, method))
        ]
        
        # IState should only define these three methods for single responsibility
        expected_methods = {'get_name', 'get_next_states', 'can_transition_to'}
        
        # Note: ABC may add additional methods, so we check that our methods exist
        assert expected_methods.issubset(set(istate_methods))
    
    def test_state_does_not_contain_execution_logic(self):
        """Test that IState interface has no execution-related methods."""
        # Execution methods that should NOT exist in IState
        execution_methods = ['execute', 'run', 'process', 'handle', 'perform']
        
        for method in execution_methods:
            assert not hasattr(IState, method), \
                f"IState should not have '{method}' method (Single Responsibility)"
    
    def test_state_does_not_contain_persistence_logic(self):
        """Test that IState interface has no persistence-related methods."""
        # Persistence methods that should NOT exist in IState
        persistence_methods = ['save', 'load', 'persist', 'store', 'retrieve']
        
        for method in persistence_methods:
            assert not hasattr(IState, method), \
                f"IState should not have '{method}' method (Single Responsibility)"


class TestWorkflowStateExamples:
    """Tests demonstrating workflow state usage."""
    
    def test_idea_creation_state(self):
        """Test example of IdeaCreation state."""
        state = ConcreteState(
            name="IdeaCreation",
            next_states=["TitleFromIdea"]
        )
        
        assert state.get_name() == "IdeaCreation"
        assert state.can_transition_to("TitleFromIdea") is True
        assert state.can_transition_to("Publishing") is False
    
    def test_title_from_idea_state(self):
        """Test example of TitleFromIdea state."""
        state = ConcreteState(
            name="TitleFromIdea",
            next_states=["ScriptFromTitleIdea"]
        )
        
        assert state.get_name() == "TitleFromIdea"
        assert state.can_transition_to("ScriptFromTitleIdea") is True
    
    def test_review_state_with_branches(self):
        """Test example of review state with multiple next states."""
        state = ConcreteState(
            name="ReviewTitleByScriptIdea",
            next_states=["ReviewScriptByTitleIdea", "TitleFromScriptReviewTitle"]
        )
        
        assert state.get_name() == "ReviewTitleByScriptIdea"
        
        # Review can go to accepted path
        assert state.can_transition_to("ReviewScriptByTitleIdea") is True
        
        # Review can go to refinement path
        assert state.can_transition_to("TitleFromScriptReviewTitle") is True
        
        # Review cannot skip to publishing
        assert state.can_transition_to("Publishing") is False
    
    def test_terminal_publishing_state(self):
        """Test example of terminal Publishing state."""
        state = ConcreteState(
            name="Publishing",
            next_states=[]  # Terminal state has no next states
        )
        
        assert state.get_name() == "Publishing"
        assert state.get_next_states() == []
        assert state.can_transition_to("AnyState") is False
