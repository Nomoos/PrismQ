"""State helpers module for PrismQ.T workflow.

This module provides centralized utilities for working with Story.state values
following the PrismQ.T naming convention:

    PrismQ.T.<Output>.From.<Input1>.<Input2>...

Components:
    - StateBuilder: Fluent builder for constructing state strings
    - StateParts: Parsed components of a state string
    - build_state: Convenience function for building states
    - parse_state: Parse state string into components
    - validate_state_format: Validate state string format

Usage:
    >>> from T.State.helpers import StateBuilder, build_state, parse_state
    >>> 
    >>> # Build a state
    >>> state = build_state("Title", "From", "Idea")
    >>> 
    >>> # Parse a state
    >>> parts = parse_state("PrismQ.T.Script.From.Idea.Title")
    >>> print(parts.output)  # 'Script'
"""

from T.State.helpers.state_builder import (
    StateBuilder,
    StateParts,
    build_state,
    parse_state,
    validate_state_format,
    get_state_output,
    get_state_inputs,
    is_generation_state,
    is_review_state,
    STATE_PREFIX,
    GENERATION_ACTION,
    REVIEW_ACTION,
)

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
