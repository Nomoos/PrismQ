"""State name constants for PrismQ.T workflow state machine.

This module defines all state name constants following the pattern:
    PrismQ.T.<Output>.From.<Input>

The design is extensible - new states can be added without modifying existing code
by adding new class attributes or creating new state categories.

State Categories:
    - Creation: Initial content creation states
    - Generation: Content generation from inputs
    - Review: Quality review and validation states
    - Refinement: Content improvement states
    - Publishing: Final output and publishing states

Example Usage:
    >>> from T.State.constants.state_names import StateNames
    >>> StateNames.IDEA_CREATION
    'PrismQ.T.Idea.Creation'
    >>> StateNames.TITLE_FROM_IDEA
    'PrismQ.T.Title.From.Idea'
"""

from enum import Enum
from typing import Dict, List, Set, Optional


class StateCategory(Enum):
    """Categories for grouping workflow states.
    
    Allows for logical organization and filtering of states.
    New categories can be added without modifying existing code.
    """
    CREATION = "creation"
    GENERATION = "generation"
    REVIEW = "review"
    REFINEMENT = "refinement"
    PUBLISHING = "publishing"


class StateNames:
    """State name constants for the PrismQ.T workflow.
    
    All state names follow the naming convention:
        PrismQ.T.<Output>.From.<Input> - for generation states
        PrismQ.T.<Action>.<Target> - for other states
    
    This class is designed to be extensible:
        - New states can be added as class attributes
        - The registry automatically includes all state constants
        - Helper methods allow querying states by category or pattern
    
    Attributes:
        STATE_PREFIX: The common prefix for all state names
    """
    
    # Common prefix for all states
    STATE_PREFIX = "PrismQ.T"
    
    # =========================================================================
    # Stage 1: Initial Creation
    # =========================================================================
    IDEA_CREATION = f"{STATE_PREFIX}.Idea.Creation"
    
    # =========================================================================
    # Stage 2-3: Initial Content Generation
    # =========================================================================
    TITLE_FROM_IDEA = f"{STATE_PREFIX}.Title.From.Idea"
    SCRIPT_FROM_TITLE_IDEA = f"{STATE_PREFIX}.Script.From.Title.Idea"
    
    # =========================================================================
    # Stages 4-6: Initial Review Cycle
    # =========================================================================
    REVIEW_TITLE_BY_SCRIPT_IDEA = f"{STATE_PREFIX}.Review.Title.By.Script.Idea"
    REVIEW_SCRIPT_BY_TITLE_IDEA = f"{STATE_PREFIX}.Review.Script.By.Title.Idea"
    REVIEW_TITLE_BY_SCRIPT = f"{STATE_PREFIX}.Review.Title.By.Script"
    
    # =========================================================================
    # Stages 7-9: Refinement and Re-review
    # =========================================================================
    TITLE_FROM_SCRIPT_REVIEW_TITLE = f"{STATE_PREFIX}.Title.From.Script.Review.Title"
    SCRIPT_FROM_TITLE_REVIEW_SCRIPT = f"{STATE_PREFIX}.Script.From.Title.Review.Script"
    REVIEW_SCRIPT_BY_TITLE = f"{STATE_PREFIX}.Review.Script.By.Title"
    
    # =========================================================================
    # Stages 10-16: Quality Review States
    # =========================================================================
    REVIEW_SCRIPT_GRAMMAR = f"{STATE_PREFIX}.Review.Script.Grammar"
    REVIEW_SCRIPT_TONE = f"{STATE_PREFIX}.Review.Script.Tone"
    REVIEW_SCRIPT_CONTENT = f"{STATE_PREFIX}.Review.Script.Content"
    REVIEW_SCRIPT_CONSISTENCY = f"{STATE_PREFIX}.Review.Script.Consistency"
    REVIEW_SCRIPT_EDITING = f"{STATE_PREFIX}.Review.Script.Editing"
    REVIEW_TITLE_READABILITY = f"{STATE_PREFIX}.Review.Title.Readability"
    REVIEW_SCRIPT_READABILITY = f"{STATE_PREFIX}.Review.Script.Readability"
    
    # =========================================================================
    # Stages 17-18: Expert Review Loop
    # =========================================================================
    STORY_REVIEW = f"{STATE_PREFIX}.Story.Review"
    STORY_POLISH = f"{STATE_PREFIX}.Story.Polish"
    
    # =========================================================================
    # Terminal State
    # =========================================================================
    PUBLISHING = f"{STATE_PREFIX}.Publishing"
    
    # =========================================================================
    # State Category Mappings (for extensible categorization)
    # =========================================================================
    _CATEGORY_MAPPINGS: Dict[StateCategory, List[str]] = {
        StateCategory.CREATION: [
            IDEA_CREATION,
        ],
        StateCategory.GENERATION: [
            TITLE_FROM_IDEA,
            SCRIPT_FROM_TITLE_IDEA,
            TITLE_FROM_SCRIPT_REVIEW_TITLE,
            SCRIPT_FROM_TITLE_REVIEW_SCRIPT,
        ],
        StateCategory.REVIEW: [
            REVIEW_TITLE_BY_SCRIPT_IDEA,
            REVIEW_SCRIPT_BY_TITLE_IDEA,
            REVIEW_TITLE_BY_SCRIPT,
            REVIEW_SCRIPT_BY_TITLE,
            REVIEW_SCRIPT_GRAMMAR,
            REVIEW_SCRIPT_TONE,
            REVIEW_SCRIPT_CONTENT,
            REVIEW_SCRIPT_CONSISTENCY,
            REVIEW_SCRIPT_EDITING,
            REVIEW_TITLE_READABILITY,
            REVIEW_SCRIPT_READABILITY,
            STORY_REVIEW,
        ],
        StateCategory.REFINEMENT: [
            STORY_POLISH,
        ],
        StateCategory.PUBLISHING: [
            PUBLISHING,
        ],
    }
    
    @classmethod
    def get_all_states(cls) -> List[str]:
        """Get all defined state names.
        
        Returns:
            List of all state name strings.
            
        Example:
            >>> states = StateNames.get_all_states()
            >>> 'PrismQ.T.Idea.Creation' in states
            True
        """
        states = []
        for attr_name in dir(cls):
            if (not attr_name.startswith('_') and 
                attr_name.isupper() and 
                attr_name != 'STATE_PREFIX' and
                isinstance(getattr(cls, attr_name), str) and
                getattr(cls, attr_name).startswith(cls.STATE_PREFIX)):
                states.append(getattr(cls, attr_name))
        return states
    
    @classmethod
    def get_states_by_category(cls, category: StateCategory) -> List[str]:
        """Get all states belonging to a specific category.
        
        Args:
            category: The StateCategory to filter by.
            
        Returns:
            List of state names in the specified category.
            
        Example:
            >>> review_states = StateNames.get_states_by_category(StateCategory.REVIEW)
            >>> 'PrismQ.T.Review.Script.Grammar' in review_states
            True
        """
        return cls._CATEGORY_MAPPINGS.get(category, [])
    
    @classmethod
    def get_state_category(cls, state_name: str) -> Optional[StateCategory]:
        """Get the category of a specific state.
        
        Args:
            state_name: The full state name string.
            
        Returns:
            The StateCategory or None if not found.
            
        Example:
            >>> StateNames.get_state_category('PrismQ.T.Idea.Creation')
            <StateCategory.CREATION: 'creation'>
        """
        for category, states in cls._CATEGORY_MAPPINGS.items():
            if state_name in states:
                return category
        return None
    
    @classmethod
    def is_valid_state(cls, state_name: str) -> bool:
        """Check if a state name is a valid defined state.
        
        Args:
            state_name: The state name to validate.
            
        Returns:
            True if the state is defined, False otherwise.
            
        Example:
            >>> StateNames.is_valid_state('PrismQ.T.Idea.Creation')
            True
            >>> StateNames.is_valid_state('PrismQ.T.Invalid.State')
            False
        """
        return state_name in cls.get_all_states()
    
    @classmethod
    def get_review_states(cls) -> List[str]:
        """Get all review-related states.
        
        Convenience method for getting all states in the REVIEW category.
        
        Returns:
            List of review state names.
        """
        return cls.get_states_by_category(StateCategory.REVIEW)
    
    @classmethod
    def get_generation_states(cls) -> List[str]:
        """Get all content generation states.
        
        Convenience method for getting all states in the GENERATION category.
        
        Returns:
            List of generation state names.
        """
        return cls.get_states_by_category(StateCategory.GENERATION)
    
    @classmethod
    def get_quality_review_states(cls) -> List[str]:
        """Get all quality review states (stages 10-16).
        
        These are the local AI review states for grammar, tone, content,
        consistency, editing, and readability.
        
        Returns:
            List of quality review state names.
        """
        return [
            cls.REVIEW_SCRIPT_GRAMMAR,
            cls.REVIEW_SCRIPT_TONE,
            cls.REVIEW_SCRIPT_CONTENT,
            cls.REVIEW_SCRIPT_CONSISTENCY,
            cls.REVIEW_SCRIPT_EDITING,
            cls.REVIEW_TITLE_READABILITY,
            cls.REVIEW_SCRIPT_READABILITY,
        ]
    
    @classmethod
    def count_states(cls) -> int:
        """Get the total count of defined states.
        
        Returns:
            Total number of state constants.
        """
        return len(cls.get_all_states())
    
    @classmethod
    def parse_state_name(cls, state_name: str) -> Dict[str, str]:
        """Parse a state name into its components.
        
        Args:
            state_name: The full state name string.
            
        Returns:
            Dictionary with parsed components:
                - prefix: The PrismQ.T prefix
                - output: The output/target of the state
                - action: Optional action (e.g., 'From', 'By')
                - input: Optional input/source
                
        Example:
            >>> StateNames.parse_state_name('PrismQ.T.Title.From.Idea')
            {'prefix': 'PrismQ.T', 'output': 'Title', 'action': 'From', 'input': 'Idea'}
        """
        if not state_name.startswith(cls.STATE_PREFIX):
            raise ValueError(f"Invalid state name: {state_name}")
        
        parts = state_name.split('.')
        result = {
            'prefix': f"{parts[0]}.{parts[1]}",
            'output': parts[2] if len(parts) > 2 else '',
        }
        
        if len(parts) > 3:
            # Check for action patterns like 'From' or 'By'
            if parts[3] in ('From', 'By'):
                result['action'] = parts[3]
                result['input'] = '.'.join(parts[4:]) if len(parts) > 4 else ''
            else:
                # Handle cases like Review.Script.Grammar
                result['action'] = parts[3]
                result['input'] = '.'.join(parts[4:]) if len(parts) > 4 else ''
        
        return result


# Convenience aliases for common state groups
INITIAL_STATES = [StateNames.IDEA_CREATION]
TERMINAL_STATES = [StateNames.PUBLISHING]
EXPERT_REVIEW_STATES = [StateNames.STORY_REVIEW, StateNames.STORY_POLISH]
