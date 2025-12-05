"""State Builder - Centralized helper module for Story.state manipulation.

This module provides utilities for building, parsing, and validating Story.state
values following the PrismQ.T naming convention:

    PrismQ.T.<Output>.From.<Input1>.<Input2>...

State Format:
    - Prefix: "PrismQ.T" (constant)
    - Output: The entity being created/modified (e.g., "Title", "Script", "Review")
    - Action: "From", "By", or action-specific keyword
    - Inputs: One or more input sources (e.g., "Idea", "Title", "Script")

Examples:
    - PrismQ.T.Idea.Creation - Initial state
    - PrismQ.T.Title.From.Idea - Generate title from idea
    - PrismQ.T.Script.From.Idea.Title - Generate script from idea and title
    - PrismQ.T.Review.Script.Grammar - Grammar review of script
    - PrismQ.T.Publishing - Terminal state

Usage:
    >>> from Model.State.helpers.state_builder import StateBuilder, build_state, parse_state
    >>> 
    >>> # Build a state string
    >>> state = build_state("Title", "From", "Idea")
    >>> print(state)
    'PrismQ.T.Title.From.Idea'
    >>> 
    >>> # Parse a state string
    >>> parts = parse_state("PrismQ.T.Script.From.Idea.Title")
    >>> print(parts.output)  # 'Script'
    >>> print(parts.inputs)  # ['Idea', 'Title']
    >>> 
    >>> # Use builder pattern
    >>> state = StateBuilder().output("Review").component("Script").component("Grammar").build()
    >>> print(state)
    'PrismQ.T.Review.Script.Grammar'
"""

from dataclasses import dataclass
from typing import Optional, List, Tuple
import re


# Constants
STATE_PREFIX = "PrismQ.T"
GENERATION_ACTION = "From"
REVIEW_ACTION = "By"

# Valid state component patterns (alphanumeric only)
COMPONENT_PATTERN = re.compile(r'^[A-Za-z][A-Za-z0-9]*$')


@dataclass(frozen=True)
class StateParts:
    """Parsed components of a state string.
    
    Attributes:
        prefix: The state prefix ("PrismQ.T")
        output: The output/target entity (e.g., "Title", "Script", "Review")
        action: The action keyword if present ("From", "By", etc.)
        inputs: Tuple of input sources (e.g., ("Idea", "Title"))
        raw: The original state string
        
    Example:
        >>> parts = parse_state("PrismQ.T.Script.From.Idea.Title")
        >>> parts.output  # 'Script'
        >>> parts.action  # 'From'
        >>> parts.inputs  # ('Idea', 'Title')
    """
    prefix: str
    output: str
    action: Optional[str] = None
    inputs: Tuple[str, ...] = ()
    raw: str = ""
    
    @property
    def is_generation_state(self) -> bool:
        """Check if this is a generation state (has 'From' action)."""
        return self.action == GENERATION_ACTION
    
    @property
    def is_review_state(self) -> bool:
        """Check if this state is a review state.
        
        A state is considered a review state if the output is 'Review'
        (e.g., PrismQ.T.Review.Script.Grammar).
        """
        return self.output == "Review"
    
    @property
    def components_after_output(self) -> Tuple[str, ...]:
        """Get all components after the output (action + inputs)."""
        if self.action:
            return (self.action,) + self.inputs
        return self.inputs


class StateBuilder:
    """Fluent builder for constructing state strings.
    
    Provides a fluent interface for building state strings following
    the PrismQ.T naming convention.
    
    Example:
        >>> state = StateBuilder() \\
        ...     .output("Title") \\
        ...     .from_inputs("Idea") \\
        ...     .build()
        >>> print(state)
        'PrismQ.T.Title.From.Idea'
        
        >>> state = StateBuilder() \\
        ...     .output("Script") \\
        ...     .from_inputs("Idea", "Title") \\
        ...     .build()
        >>> print(state)
        'PrismQ.T.Script.From.Idea.Title'
        
        >>> # For non-From states
        >>> state = StateBuilder() \\
        ...     .output("Review") \\
        ...     .component("Script") \\
        ...     .component("Grammar") \\
        ...     .build()
        >>> print(state)
        'PrismQ.T.Review.Script.Grammar'
    """
    
    def __init__(self):
        """Initialize the builder."""
        self._output: Optional[str] = None
        self._action: Optional[str] = None
        self._inputs: List[str] = []
        self._components: List[str] = []
    
    def output(self, output: str) -> "StateBuilder":
        """Set the output/target entity.
        
        Args:
            output: The entity being created (e.g., "Title", "Script")
            
        Returns:
            Self for method chaining.
            
        Raises:
            ValueError: If output is invalid.
        """
        if not _is_valid_component(output):
            raise ValueError(f"Invalid output component: {output}")
        self._output = output
        return self
    
    def from_inputs(self, *inputs: str) -> "StateBuilder":
        """Set inputs with 'From' action.
        
        Args:
            *inputs: Input sources (e.g., "Idea", "Title")
            
        Returns:
            Self for method chaining.
            
        Raises:
            ValueError: If any input is invalid.
        """
        for inp in inputs:
            if not _is_valid_component(inp):
                raise ValueError(f"Invalid input component: {inp}")
        self._action = GENERATION_ACTION
        self._inputs = list(inputs)
        return self
    
    def by_source(self, *sources: str) -> "StateBuilder":
        """Set sources with 'By' action (for review states).
        
        Args:
            *sources: Source entities for the review.
            
        Returns:
            Self for method chaining.
        """
        for src in sources:
            if not _is_valid_component(src):
                raise ValueError(f"Invalid source component: {src}")
        self._action = REVIEW_ACTION
        self._inputs = list(sources)
        return self
    
    def component(self, component: str) -> "StateBuilder":
        """Add a generic component (for non-From/By states).
        
        Args:
            component: A state component (e.g., "Grammar", "Script")
            
        Returns:
            Self for method chaining.
        """
        if not _is_valid_component(component):
            raise ValueError(f"Invalid component: {component}")
        self._components.append(component)
        return self
    
    def build(self) -> str:
        """Build the final state string.
        
        Returns:
            The complete state string.
            
        Raises:
            ValueError: If output is not set.
        """
        if not self._output:
            raise ValueError("Output must be set before building")
        
        parts = [STATE_PREFIX, self._output]
        
        # Add components (for non-action states like Review.Script.Grammar)
        if self._components:
            parts.extend(self._components)
        
        # Add action and inputs
        if self._action:
            parts.append(self._action)
            parts.extend(self._inputs)
        
        return ".".join(parts)


def build_state(output: str, action: Optional[str] = None, *inputs: str) -> str:
    """Build a state string from components.
    
    A convenience function for building state strings without using
    the builder pattern.
    
    Args:
        output: The output/target entity (e.g., "Title", "Script")
        action: Optional action keyword ("From", "By", etc.)
        *inputs: Input sources (e.g., "Idea", "Title")
        
    Returns:
        The complete state string.
        
    Example:
        >>> build_state("Title", "From", "Idea")
        'PrismQ.T.Title.From.Idea'
        >>> build_state("Script", "From", "Idea", "Title")
        'PrismQ.T.Script.From.Idea.Title'
        >>> build_state("Idea", "Creation")
        'PrismQ.T.Idea.Creation'
    """
    parts = [STATE_PREFIX, output]
    
    if action:
        parts.append(action)
    
    parts.extend(inputs)
    
    return ".".join(parts)


def parse_state(state: str) -> StateParts:
    """Parse a state string into its components.
    
    Args:
        state: The state string to parse.
        
    Returns:
        StateParts object with parsed components.
        
    Raises:
        ValueError: If state format is invalid.
        
    Example:
        >>> parts = parse_state("PrismQ.T.Title.From.Idea")
        >>> parts.output  # 'Title'
        >>> parts.action  # 'From'
        >>> parts.inputs  # ('Idea',)
    """
    if not state:
        raise ValueError("State cannot be empty")
    
    if not state.startswith(STATE_PREFIX + "."):
        raise ValueError(f"State must start with '{STATE_PREFIX}.': {state}")
    
    # Remove prefix and split
    rest = state[len(STATE_PREFIX) + 1:]  # +1 for the dot
    parts = rest.split(".")
    
    if not parts or not parts[0]:
        raise ValueError(f"State must have at least an output component: {state}")
    
    output = parts[0]
    action = None
    inputs: List[str] = []
    
    # Check for action keyword
    if len(parts) > 1:
        if parts[1] in (GENERATION_ACTION, REVIEW_ACTION):
            action = parts[1]
            inputs = parts[2:]
        else:
            # No action keyword, treat remaining parts as additional components
            inputs = parts[1:]
    
    return StateParts(
        prefix=STATE_PREFIX,
        output=output,
        action=action,
        inputs=tuple(inputs),
        raw=state
    )


def validate_state_format(state: str) -> Tuple[bool, Optional[str]]:
    """Validate that a state string follows the correct format.
    
    Args:
        state: The state string to validate.
        
    Returns:
        Tuple of (is_valid, error_message).
        error_message is None if valid.
        
    Example:
        >>> validate_state_format("PrismQ.T.Title.From.Idea")
        (True, None)
        >>> validate_state_format("Invalid.State")
        (False, "State must start with 'PrismQ.T.': Invalid.State")
    """
    if not state:
        return False, "State cannot be empty"
    
    if not state.startswith(STATE_PREFIX + "."):
        return False, f"State must start with '{STATE_PREFIX}.': {state}"
    
    # Check components after prefix
    rest = state[len(STATE_PREFIX) + 1:]
    parts = rest.split(".")
    
    if not parts or not parts[0]:
        return False, f"State must have at least an output component: {state}"
    
    # Validate each component
    for part in parts:
        if not _is_valid_component(part):
            return False, f"Invalid component '{part}' in state: {state}"
    
    return True, None


def get_state_output(state: str) -> str:
    """Get the output/target entity from a state string.
    
    Args:
        state: The state string.
        
    Returns:
        The output entity (e.g., "Title", "Script").
        
    Raises:
        ValueError: If state format is invalid.
    """
    return parse_state(state).output


def get_state_inputs(state: str) -> List[str]:
    """Get the input sources from a state string.
    
    Args:
        state: The state string.
        
    Returns:
        List of input sources (may be empty).
    """
    return list(parse_state(state).inputs)


def is_generation_state(state: str) -> bool:
    """Check if a state is a generation state (has 'From' action).
    
    Args:
        state: The state string.
        
    Returns:
        True if state is a generation state.
    """
    try:
        return parse_state(state).is_generation_state
    except ValueError:
        return False


def is_review_state(state: str) -> bool:
    """Check if a state is a review state.
    
    Args:
        state: The state string.
        
    Returns:
        True if state is a review state.
    """
    try:
        return parse_state(state).is_review_state
    except ValueError:
        return False


def _is_valid_component(component: str) -> bool:
    """Check if a component is valid (alphanumeric, starts with letter).
    
    Args:
        component: The component to validate.
        
    Returns:
        True if component is valid.
    """
    if not component:
        return False
    return bool(COMPONENT_PATTERN.match(component))


__all__ = [
    "StateBuilder",
    "StateParts",
    "build_state",
    "parse_state",
    "validate_state_format",
    "get_state_output",
    "get_state_inputs",
    "is_generation_state",
    "is_review_state",
    "STATE_PREFIX",
    "GENERATION_ACTION",
    "REVIEW_ACTION",
]
