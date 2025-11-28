"""Task claiming strategies for worker queue.

Implements Strategy pattern for different task claiming behaviors.
Follows Open/Closed Principle - easily extensible for new strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict


class ClaimingStrategy(ABC):
    """Abstract base for task claiming strategies.
    
    Following Open/Closed Principle - open for extension, closed for modification.
    """
    
    @abstractmethod
    def get_order_by_clause(self) -> str:
        """Get SQL ORDER BY clause for this strategy.
        
        Returns:
            SQL ORDER BY clause (without 'ORDER BY' keyword)
        """
        pass


class FIFOStrategy(ClaimingStrategy):
    """First-In-First-Out: Process oldest tasks first."""
    
    def get_order_by_clause(self) -> str:
        return "created_at ASC, priority DESC"


class LIFOStrategy(ClaimingStrategy):
    """Last-In-First-Out: Process newest tasks first."""
    
    def get_order_by_clause(self) -> str:
        return "created_at DESC, priority DESC"


class PriorityStrategy(ClaimingStrategy):
    """Priority-based: Process highest priority tasks first."""
    
    def get_order_by_clause(self) -> str:
        return "priority DESC, created_at ASC"


# Workflow state order mapping for WorkflowStateStrategy
# States earlier in workflow get lower numbers (1-19)
# ORDER BY uses DESC, so higher numbers (later states) get processed first
# Based on T/WORKFLOW_STATE_MACHINE.md stage numbers
WORKFLOW_STATE_ORDER = {
    'PrismQ.T.Idea.Creation': 1,
    'PrismQ.T.Title.From.Idea': 2,
    'PrismQ.T.Script.From.Title.Idea': 3,
    'PrismQ.T.Review.Title.By.Script.Idea': 4,
    'PrismQ.T.Review.Script.By.Title.Idea': 5,
    'PrismQ.T.Review.Title.By.Script': 6,
    'PrismQ.T.Title.From.Script.Review.Title': 7,
    'PrismQ.T.Script.From.Title.Review.Script': 8,
    'PrismQ.T.Review.Script.By.Title': 9,
    'PrismQ.T.Review.Script.Grammar': 10,
    'PrismQ.T.Review.Script.Tone': 11,
    'PrismQ.T.Review.Script.Content': 12,
    'PrismQ.T.Review.Script.Consistency': 13,
    'PrismQ.T.Review.Script.Editing': 14,
    'PrismQ.T.Review.Title.Readability': 15,
    'PrismQ.T.Review.Script.Readability': 16,
    'PrismQ.T.Story.Review': 17,
    'PrismQ.T.Story.Polish': 18,
    'PrismQ.T.Publishing': 19,
}


def _escape_sql_string(value: str) -> str:
    """Escape single quotes in SQL string values."""
    return value.replace("'", "''")


class WorkflowStateStrategy(ClaimingStrategy):
    """Workflow state-based ordering: Tasks further in workflow first.
    
    Use case:
    - Content pipeline processing
    - Prioritizing items closer to completion
    - Balanced workflow progression
    """
    
    def get_order_by_clause(self) -> str:
        """Order by workflow state position (descending), then creation time."""
        # Build CASE expression for state ordering with proper SQL escaping
        case_parts = [f"WHEN state = '{_escape_sql_string(state)}' THEN {order}" 
                      for state, order in WORKFLOW_STATE_ORDER.items()]
        case_expr = "CASE " + " ".join(case_parts) + " ELSE 99 END"
        
        # Order by state position descending (higher stages first), then FIFO
        return f"{case_expr} DESC, created_at ASC"


# Strategy registry
_STRATEGIES: Dict[str, ClaimingStrategy] = {
    "FIFO": FIFOStrategy(),
    "LIFO": LIFOStrategy(),
    "PRIORITY": PriorityStrategy(),
    "WORKFLOW_STATE": WorkflowStateStrategy(),
}


def get_strategy(name: str) -> ClaimingStrategy:
    """Get claiming strategy by name.
    
    Args:
        name: Strategy name (FIFO, LIFO, PRIORITY, WORKFLOW_STATE)
        
    Returns:
        ClaimingStrategy instance
        
    Raises:
        ValueError: If strategy not found
    """
    strategy = _STRATEGIES.get(name.upper())
    if not strategy:
        raise ValueError(
            f"Unknown strategy '{name}'. "
            f"Available: {', '.join(_STRATEGIES.keys())}"
        )
    return strategy


__all__ = ["ClaimingStrategy", "get_strategy", "WorkflowStateStrategy", "WORKFLOW_STATE_ORDER"]
