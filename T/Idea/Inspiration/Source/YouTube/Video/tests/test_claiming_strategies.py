"""Tests for task claiming strategies.

This module tests the claiming strategy implementations, ensuring:
- SOLID principles compliance (Strategy Pattern, ISP, OCP)
- Correct SQL ORDER BY clause generation
- Strategy registry and lookup functions
"""

import pytest

from src.workers.claiming_strategies import (
    STRATEGIES,
    FIFOStrategy,
    LIFOStrategy,
    PriorityStrategy,
    WeightedRandomStrategy,
    get_available_strategies,
    get_strategy,
)


class TestFIFOStrategy:
    """Test First-In-First-Out strategy."""

    def test_fifo_order_by_clause(self):
        """Test FIFO generates correct ORDER BY clause."""
        strategy = FIFOStrategy()
        clause = strategy.get_order_by_clause()

        assert clause == "created_at ASC, priority DESC"
        assert "created_at ASC" in clause  # Oldest first
        assert "priority DESC" in clause  # Higher priority tiebreaker

    def test_fifo_string_representation(self):
        """Test FIFO string representation."""
        strategy = FIFOStrategy()

        assert str(strategy) == "FIFOStrategy"
        assert "FIFOStrategy" in repr(strategy)


class TestLIFOStrategy:
    """Test Last-In-First-Out strategy."""

    def test_lifo_order_by_clause(self):
        """Test LIFO generates correct ORDER BY clause."""
        strategy = LIFOStrategy()
        clause = strategy.get_order_by_clause()

        assert clause == "created_at DESC, priority DESC"
        assert "created_at DESC" in clause  # Newest first
        assert "priority DESC" in clause  # Higher priority tiebreaker

    def test_lifo_string_representation(self):
        """Test LIFO string representation."""
        strategy = LIFOStrategy()

        assert str(strategy) == "LIFOStrategy"
        assert "LIFOStrategy" in repr(strategy)


class TestPriorityStrategy:
    """Test Priority-based strategy."""

    def test_priority_order_by_clause(self):
        """Test Priority generates correct ORDER BY clause."""
        strategy = PriorityStrategy()
        clause = strategy.get_order_by_clause()

        assert clause == "priority DESC, created_at ASC"
        assert "priority DESC" in clause  # Highest priority first
        assert "created_at ASC" in clause  # FIFO tiebreaker

    def test_priority_string_representation(self):
        """Test Priority string representation."""
        strategy = PriorityStrategy()

        assert str(strategy) == "PriorityStrategy"
        assert "PriorityStrategy" in repr(strategy)


class TestWeightedRandomStrategy:
    """Test Weighted Random strategy."""

    def test_weighted_random_order_by_clause(self):
        """Test WeightedRandom generates correct ORDER BY clause."""
        strategy = WeightedRandomStrategy()
        clause = strategy.get_order_by_clause()

        # Should include priority weighting and randomness
        assert "priority" in clause.lower()
        assert "random" in clause.lower()
        assert "DESC" in clause

    def test_weighted_random_string_representation(self):
        """Test WeightedRandom string representation."""
        strategy = WeightedRandomStrategy()

        assert str(strategy) == "WeightedRandomStrategy"
        assert "WeightedRandomStrategy" in repr(strategy)


class TestStrategyRegistry:
    """Test strategy registry and lookup."""

    def test_strategies_registry_contains_all(self):
        """Test that STRATEGIES registry contains all strategy types."""
        assert "FIFO" in STRATEGIES
        assert "LIFO" in STRATEGIES
        assert "PRIORITY" in STRATEGIES
        assert "WEIGHTED_RANDOM" in STRATEGIES

    def test_strategies_registry_instances(self):
        """Test that STRATEGIES contains strategy instances."""
        assert isinstance(STRATEGIES["FIFO"], FIFOStrategy)
        assert isinstance(STRATEGIES["LIFO"], LIFOStrategy)
        assert isinstance(STRATEGIES["PRIORITY"], PriorityStrategy)
        assert isinstance(STRATEGIES["WEIGHTED_RANDOM"], WeightedRandomStrategy)


class TestGetStrategy:
    """Test get_strategy function."""

    def test_get_fifo_strategy(self):
        """Test getting FIFO strategy."""
        strategy = get_strategy("FIFO")
        assert isinstance(strategy, FIFOStrategy)

    def test_get_lifo_strategy(self):
        """Test getting LIFO strategy."""
        strategy = get_strategy("LIFO")
        assert isinstance(strategy, LIFOStrategy)

    def test_get_priority_strategy(self):
        """Test getting Priority strategy."""
        strategy = get_strategy("PRIORITY")
        assert isinstance(strategy, PriorityStrategy)

    def test_get_weighted_random_strategy(self):
        """Test getting WeightedRandom strategy."""
        strategy = get_strategy("WEIGHTED_RANDOM")
        assert isinstance(strategy, WeightedRandomStrategy)

    def test_get_strategy_case_insensitive(self):
        """Test that get_strategy is case-insensitive."""
        # All these should work
        assert get_strategy("fifo") is not None
        assert get_strategy("FIFO") is not None
        assert get_strategy("Fifo") is not None
        assert get_strategy("FiFo") is not None

    def test_get_strategy_unknown_raises_error(self):
        """Test that unknown strategy raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            get_strategy("UNKNOWN_STRATEGY")

        assert "Unknown strategy" in str(exc_info.value)
        assert "UNKNOWN_STRATEGY" in str(exc_info.value)
        # Should list valid strategies
        assert "FIFO" in str(exc_info.value)


class TestGetAvailableStrategies:
    """Test get_available_strategies function."""

    def test_get_available_strategies_returns_list(self):
        """Test that get_available_strategies returns a list."""
        strategies = get_available_strategies()
        assert isinstance(strategies, list)
        assert len(strategies) > 0

    def test_get_available_strategies_contains_all(self):
        """Test that all strategies are listed."""
        strategies = get_available_strategies()
        assert "FIFO" in strategies
        assert "LIFO" in strategies
        assert "PRIORITY" in strategies
        assert "WEIGHTED_RANDOM" in strategies

    def test_get_available_strategies_count(self):
        """Test that correct number of strategies is returned."""
        strategies = get_available_strategies()
        assert len(strategies) == 4  # FIFO, LIFO, PRIORITY, WEIGHTED_RANDOM


class TestStrategySOLIDCompliance:
    """Test SOLID principles compliance."""

    def test_interface_segregation_principle(self):
        """Test that strategies follow Interface Segregation Principle.

        Each strategy should only need to implement one method:
        get_order_by_clause()
        """
        strategies = [FIFOStrategy(), LIFOStrategy(), PriorityStrategy(), WeightedRandomStrategy()]

        for strategy in strategies:
            # Each strategy must implement get_order_by_clause
            assert hasattr(strategy, "get_order_by_clause")
            assert callable(strategy.get_order_by_clause)

            # Should return a string
            clause = strategy.get_order_by_clause()
            assert isinstance(clause, str)
            assert len(clause) > 0

    def test_open_closed_principle(self):
        """Test that strategy system follows Open/Closed Principle.

        Should be open for extension (new strategies can be added)
        but closed for modification (existing strategies unchanged).
        """
        from src.workers.claiming_strategies import BaseClaimStrategy

        # Define a new strategy without modifying existing code
        class CustomStrategy(BaseClaimStrategy):
            def get_order_by_clause(self) -> str:
                return "custom_field DESC"

        # New strategy should work with the system
        custom = CustomStrategy()
        assert custom.get_order_by_clause() == "custom_field DESC"

        # Existing strategies should still work
        assert get_strategy("FIFO").get_order_by_clause() == "created_at ASC, priority DESC"

    def test_single_responsibility_principle(self):
        """Test that each strategy has single responsibility.

        Each strategy should only be responsible for defining its
        own ordering logic, nothing else.
        """
        # Each strategy should have minimal interface
        fifo = FIFOStrategy()

        # Should have get_order_by_clause method
        assert hasattr(fifo, "get_order_by_clause")

        # Should NOT have database, task processing, or other unrelated methods
        # (excluding inherited __str__, __repr__, etc.)
        strategy_methods = [m for m in dir(fifo) if not m.startswith("_")]
        # Only should have get_order_by_clause and maybe inherited utility methods
        assert "get_order_by_clause" in strategy_methods
        # Should not have unrelated methods like 'process_task', 'connect_db', etc.
        assert "process_task" not in strategy_methods
        assert "connect_db" not in strategy_methods


class TestStrategyComparison:
    """Test comparing different strategies."""

    def test_fifo_vs_lifo_ordering(self):
        """Test that FIFO and LIFO have opposite ordering for created_at."""
        fifo = FIFOStrategy().get_order_by_clause()
        lifo = LIFOStrategy().get_order_by_clause()

        # FIFO should have ASC, LIFO should have DESC for created_at
        assert "created_at ASC" in fifo
        assert "created_at DESC" in lifo

    def test_priority_first_vs_fifo_tiebreaker(self):
        """Test that Priority uses priority first, FIFO uses it as tiebreaker."""
        priority = PriorityStrategy().get_order_by_clause()
        fifo = FIFOStrategy().get_order_by_clause()

        # Priority should start with priority
        assert priority.startswith("priority DESC")

        # FIFO should start with created_at
        assert fifo.startswith("created_at ASC")

    def test_all_strategies_produce_different_clauses(self):
        """Test that all strategies produce unique ORDER BY clauses."""
        clauses = set()

        for strategy_name in get_available_strategies():
            strategy = get_strategy(strategy_name)
            clause = strategy.get_order_by_clause()
            clauses.add(clause)

        # Each strategy should produce unique clause
        assert len(clauses) == len(get_available_strategies())
