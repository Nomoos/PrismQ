"""Claiming strategies for task queue.

This module implements different strategies for claiming tasks from the queue,
following the Strategy Pattern and SOLID principles.

Following Interface Segregation Principle (ISP) - minimal, focused interface.
Following Open/Closed Principle (OCP) - easily extensible with new strategies.
"""

from abc import ABC, abstractmethod
from typing import Protocol


class ClaimingStrategy(Protocol):
    """Protocol for task claiming strategies.

    Following Interface Segregation Principle - minimal interface.
    Only the essential method needed for strategy selection.
    """

    def get_order_by_clause(self) -> str:
        """Get SQL ORDER BY clause for this strategy.

        Returns:
            SQL ORDER BY clause (without 'ORDER BY' keyword)
        """
        ...


class BaseClaimStrategy(ABC):
    """Base class for claiming strategies with common functionality.

    Following Single Responsibility Principle (SRP):
    - Each strategy defines its own ordering logic
    - Base class provides common interface and utilities
    """

    @abstractmethod
    def get_order_by_clause(self) -> str:
        """Get SQL ORDER BY clause - must be implemented by subclass.

        Returns:
            SQL ORDER BY clause string (without 'ORDER BY' keyword)
        """
        pass

    def __str__(self) -> str:
        """String representation of the strategy."""
        return self.__class__.__name__

    def __repr__(self) -> str:
        """Developer representation of the strategy."""
        return f"<{self.__class__.__name__}>"


class FIFOStrategy(BaseClaimStrategy):
    """First-In-First-Out: Oldest tasks first.

    Use case:
    - Background jobs
    - Batch processing
    - Fair task distribution

    Characteristics:
    - Fairness: High (no starvation)
    - Predictability: High (deterministic order)
    - Latency: Variable (depends on queue depth)
    """

    def get_order_by_clause(self) -> str:
        """Order by creation time ascending, then priority descending.

        Returns oldest tasks first, with priority as tiebreaker.
        """
        return "created_at ASC, priority DESC"


class LIFOStrategy(BaseClaimStrategy):
    """Last-In-First-Out: Newest tasks first.

    Use case:
    - User-initiated actions
    - Interactive work
    - Real-time responsiveness

    Characteristics:
    - Fairness: Low (old tasks may starve)
    - Predictability: Medium (recent tasks processed fast)
    - Latency: Low for new tasks, high for old tasks
    """

    def get_order_by_clause(self) -> str:
        """Order by creation time descending, then priority descending.

        Returns newest tasks first, with priority as tiebreaker.
        """
        return "created_at DESC, priority DESC"


class PriorityStrategy(BaseClaimStrategy):
    """Priority-based: Highest priority first, then FIFO.

    Use case:
    - Time-sensitive tasks
    - SLA requirements
    - Critical path optimization

    Characteristics:
    - Fairness: None (low priority may starve)
    - Predictability: High (priority-based)
    - Latency: Low for high priority, potentially infinite for low priority
    """

    def get_order_by_clause(self) -> str:
        """Order by priority descending, then creation time ascending.

        Returns highest priority tasks first, with FIFO as tiebreaker.
        """
        return "priority DESC, created_at ASC"


class WeightedRandomStrategy(BaseClaimStrategy):
    """Weighted random selection based on priority.

    Use case:
    - Load balancing across priority levels
    - Preventing priority starvation
    - Introducing controlled randomness

    Characteristics:
    - Fairness: Medium (probabilistic fairness)
    - Predictability: Low (random but weighted)
    - Latency: Variable but bounded

    Algorithm:
    - Higher priority tasks have higher probability of selection
    - Random factor prevents complete starvation
    - Still respects priority weights
    """

    def get_order_by_clause(self) -> str:
        """Order by weighted random with priority influence.

        Uses SQLite's RANDOM() function with priority weighting.
        Higher priority = more likely to be selected, but not guaranteed.

        Formula: priority * (1.0 + 0.1 * (10 - RANDOM() % 10))
        - Base weight from priority (1-10)
        - Random multiplier adds 0-90% variation
        - Higher priorities still dominate statistically
        """
        return "priority * (1.0 + 0.1 * (10 - ABS(RANDOM()) % 10)) DESC"


# Workflow state order mapping for WorkflowStateStrategy
# States earlier in workflow get lower numbers (1-19)
# ORDER BY uses DESC, so higher numbers (later states) get processed first
# Based on T/WORKFLOW_STATE_MACHINE.md stage numbers
WORKFLOW_STATE_ORDER = {
    "PrismQ.T.Idea.Creation": 1,
    "PrismQ.T.Title.From.Idea": 2,
    "PrismQ.T.Content.From.Title.Idea": 3,
    "PrismQ.T.Review.Title.By.Content.Idea": 4,
    "PrismQ.T.Review.Content.By.Title.Idea": 5,
    "PrismQ.T.Review.Title.By.Content": 6,
    "PrismQ.T.Title.From.Content.Review.Title": 7,
    "PrismQ.T.Content.From.Title.Review.Content": 8,
    "PrismQ.T.Review.Content.By.Title": 9,
    "PrismQ.T.Review.Content.Grammar": 10,
    "PrismQ.T.Review.Content.Tone": 11,
    "PrismQ.T.Review.Content.Content": 12,
    "PrismQ.T.Review.Content.Consistency": 13,
    "PrismQ.T.Review.Content.Editing": 14,
    "PrismQ.T.Review.Title.Readability": 15,
    "PrismQ.T.Review.Content.Readability": 16,
    "PrismQ.T.Story.Review": 17,
    "PrismQ.T.Story.Polish": 18,
    "PrismQ.T.Publishing": 19,
}


def _escape_sql_string(value: str) -> str:
    """Escape single quotes in SQL string values.

    Args:
        value: The string value to escape.

    Returns:
        Escaped string safe for SQL string literals.
    """
    return value.replace("'", "''")


class WorkflowStateStrategy(BaseClaimStrategy):
    """Workflow state-based ordering: Tasks further in workflow first.

    Use case:
    - Content pipeline processing
    - Prioritizing items closer to completion
    - Balanced workflow progression

    Characteristics:
    - Fairness: High (workflow position determines order)
    - Predictability: High (deterministic based on state)
    - Latency: Low for items near completion, higher for early-stage items

    Algorithm:
    - Tasks are ordered by their current workflow state position
    - Tasks further in the workflow (higher stage number) are processed first
    - This ensures items closer to completion get priority
    - FIFO is used as tiebreaker within the same state
    """

    def get_order_by_clause(self) -> str:
        """Order by workflow state position (descending), then creation time.

        Uses a CASE expression to map state names to their workflow order.
        Tasks further in the workflow (higher stage number) are prioritized
        to push items toward completion.

        Returns:
            SQL ORDER BY clause that orders by workflow state position DESC,
            then by created_at ASC as tiebreaker.
        """
        # Build CASE expression for state ordering with proper SQL escaping
        case_parts = [
            f"WHEN state = '{_escape_sql_string(state)}' THEN {order}"
            for state, order in WORKFLOW_STATE_ORDER.items()
        ]
        case_expr = "CASE " + " ".join(case_parts) + " ELSE 99 END"

        # Order by state position descending (higher stages first), then FIFO
        return f"{case_expr} DESC, created_at ASC"


# Strategy registry for easy lookup
STRATEGIES = {
    "FIFO": FIFOStrategy(),
    "LIFO": LIFOStrategy(),
    "PRIORITY": PriorityStrategy(),
    "WEIGHTED_RANDOM": WeightedRandomStrategy(),
    "WORKFLOW_STATE": WorkflowStateStrategy(),
}


def get_strategy(name: str) -> BaseClaimStrategy:
    """Get a claiming strategy by name.

    Args:
        name: Strategy name (FIFO, LIFO, PRIORITY, WEIGHTED_RANDOM, WORKFLOW_STATE)

    Returns:
        Strategy instance

    Raises:
        ValueError: If strategy name is unknown

    Example:
        >>> strategy = get_strategy('FIFO')
        >>> print(strategy.get_order_by_clause())
        created_at ASC, priority DESC
    """
    name_upper = name.upper()
    if name_upper not in STRATEGIES:
        raise ValueError(
            f"Unknown strategy: {name}. " f"Valid strategies: {', '.join(STRATEGIES.keys())}"
        )
    return STRATEGIES[name_upper]


def get_available_strategies() -> list[str]:
    """Get list of available strategy names.

    Returns:
        List of strategy names in uppercase

    Example:
        >>> strategies = get_available_strategies()
        >>> print(strategies)
        ['FIFO', 'LIFO', 'PRIORITY', 'WEIGHTED_RANDOM', 'WORKFLOW_STATE']
    """
    return list(STRATEGIES.keys())


__all__ = [
    "ClaimingStrategy",
    "BaseClaimStrategy",
    "FIFOStrategy",
    "LIFOStrategy",
    "PriorityStrategy",
    "WeightedRandomStrategy",
    "WorkflowStateStrategy",
    "WORKFLOW_STATE_ORDER",
    "get_strategy",
    "get_available_strategies",
    "STRATEGIES",
]
