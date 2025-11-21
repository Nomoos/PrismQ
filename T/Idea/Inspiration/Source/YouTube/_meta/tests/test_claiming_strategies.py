"""Unit tests for claiming strategies.

Tests the Strategy Pattern implementation for task claiming.
"""

import pytest
from src.workers.claiming_strategies import (
    get_strategy,
    get_available_strategies,
    FIFOStrategy,
    LIFOStrategy,
    PriorityStrategy,
    WeightedRandomStrategy,
    BaseClaimStrategy,
    STRATEGIES,
)


class TestStrategyInstantiation:
    """Test strategy object creation and properties."""
    
    def test_fifo_strategy_instantiation(self):
        """Test FIFOStrategy can be instantiated."""
        strategy = FIFOStrategy()
        assert isinstance(strategy, BaseClaimStrategy)
        assert str(strategy) == "FIFOStrategy"
    
    def test_lifo_strategy_instantiation(self):
        """Test LIFOStrategy can be instantiated."""
        strategy = LIFOStrategy()
        assert isinstance(strategy, BaseClaimStrategy)
        assert str(strategy) == "LIFOStrategy"
    
    def test_priority_strategy_instantiation(self):
        """Test PriorityStrategy can be instantiated."""
        strategy = PriorityStrategy()
        assert isinstance(strategy, BaseClaimStrategy)
        assert str(strategy) == "PriorityStrategy"
    
    def test_weighted_random_strategy_instantiation(self):
        """Test WeightedRandomStrategy can be instantiated."""
        strategy = WeightedRandomStrategy()
        assert isinstance(strategy, BaseClaimStrategy)
        assert str(strategy) == "WeightedRandomStrategy"


class TestOrderByClauses:
    """Test ORDER BY clause generation for each strategy."""
    
    def test_fifo_order_by(self):
        """Test FIFO generates correct ORDER BY clause."""
        strategy = FIFOStrategy()
        order_by = strategy.get_order_by_clause()
        assert order_by == "created_at ASC, priority DESC"
        assert "ASC" in order_by
        assert "created_at" in order_by
    
    def test_lifo_order_by(self):
        """Test LIFO generates correct ORDER BY clause."""
        strategy = LIFOStrategy()
        order_by = strategy.get_order_by_clause()
        assert order_by == "created_at DESC, priority DESC"
        assert "DESC" in order_by
        assert "created_at" in order_by
    
    def test_priority_order_by(self):
        """Test PRIORITY generates correct ORDER BY clause."""
        strategy = PriorityStrategy()
        order_by = strategy.get_order_by_clause()
        assert order_by == "priority DESC, created_at ASC"
        assert "priority DESC" in order_by
        assert "created_at ASC" in order_by
    
    def test_weighted_random_order_by(self):
        """Test WEIGHTED_RANDOM generates correct ORDER BY clause."""
        strategy = WeightedRandomStrategy()
        order_by = strategy.get_order_by_clause()
        assert "priority" in order_by
        assert "RANDOM()" in order_by
        assert "DESC" in order_by


class TestStrategyRegistry:
    """Test strategy registry and lookup."""
    
    def test_strategies_registry_contains_all(self):
        """Test STRATEGIES contains all four strategies."""
        assert len(STRATEGIES) == 4
        assert 'FIFO' in STRATEGIES
        assert 'LIFO' in STRATEGIES
        assert 'PRIORITY' in STRATEGIES
        assert 'WEIGHTED_RANDOM' in STRATEGIES
    
    def test_strategies_are_correct_types(self):
        """Test registry contains correct strategy instances."""
        assert isinstance(STRATEGIES['FIFO'], FIFOStrategy)
        assert isinstance(STRATEGIES['LIFO'], LIFOStrategy)
        assert isinstance(STRATEGIES['PRIORITY'], PriorityStrategy)
        assert isinstance(STRATEGIES['WEIGHTED_RANDOM'], WeightedRandomStrategy)


class TestGetStrategy:
    """Test get_strategy() function."""
    
    def test_get_strategy_fifo(self):
        """Test getting FIFO strategy."""
        strategy = get_strategy('FIFO')
        assert isinstance(strategy, FIFOStrategy)
    
    def test_get_strategy_lifo(self):
        """Test getting LIFO strategy."""
        strategy = get_strategy('LIFO')
        assert isinstance(strategy, LIFOStrategy)
    
    def test_get_strategy_priority(self):
        """Test getting PRIORITY strategy."""
        strategy = get_strategy('PRIORITY')
        assert isinstance(strategy, PriorityStrategy)
    
    def test_get_strategy_weighted_random(self):
        """Test getting WEIGHTED_RANDOM strategy."""
        strategy = get_strategy('WEIGHTED_RANDOM')
        assert isinstance(strategy, WeightedRandomStrategy)
    
    def test_get_strategy_case_insensitive(self):
        """Test get_strategy is case-insensitive."""
        strategy_upper = get_strategy('FIFO')
        strategy_lower = get_strategy('fifo')
        strategy_mixed = get_strategy('FiFo')
        
        # All should return the same strategy instance
        assert isinstance(strategy_upper, FIFOStrategy)
        assert isinstance(strategy_lower, FIFOStrategy)
        assert isinstance(strategy_mixed, FIFOStrategy)
    
    def test_get_strategy_unknown_raises_error(self):
        """Test that unknown strategy raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            get_strategy('UNKNOWN')
        
        assert "Unknown strategy" in str(exc_info.value)
        assert "UNKNOWN" in str(exc_info.value)
        assert "Valid strategies" in str(exc_info.value)
    
    def test_get_strategy_empty_raises_error(self):
        """Test that empty strategy name raises ValueError."""
        with pytest.raises(ValueError):
            get_strategy('')


class TestGetAvailableStrategies:
    """Test get_available_strategies() function."""
    
    def test_returns_list_of_four(self):
        """Test returns list of 4 strategy names."""
        strategies = get_available_strategies()
        assert isinstance(strategies, list)
        assert len(strategies) == 4
    
    def test_contains_all_strategies(self):
        """Test list contains all strategy names."""
        strategies = get_available_strategies()
        assert 'FIFO' in strategies
        assert 'LIFO' in strategies
        assert 'PRIORITY' in strategies
        assert 'WEIGHTED_RANDOM' in strategies
    
    def test_returns_uppercase_names(self):
        """Test all strategy names are uppercase."""
        strategies = get_available_strategies()
        for name in strategies:
            assert name.isupper()


class TestStrategyBehavior:
    """Test that strategies produce different ordering."""
    
    def test_fifo_vs_lifo_different(self):
        """Test FIFO and LIFO produce different ORDER BY clauses."""
        fifo = FIFOStrategy()
        lifo = LIFOStrategy()
        assert fifo.get_order_by_clause() != lifo.get_order_by_clause()
    
    def test_priority_vs_fifo_different(self):
        """Test PRIORITY and FIFO produce different ORDER BY clauses."""
        priority = PriorityStrategy()
        fifo = FIFOStrategy()
        assert priority.get_order_by_clause() != fifo.get_order_by_clause()
    
    def test_all_strategies_unique(self):
        """Test all strategies produce unique ORDER BY clauses."""
        clauses = [
            FIFOStrategy().get_order_by_clause(),
            LIFOStrategy().get_order_by_clause(),
            PriorityStrategy().get_order_by_clause(),
            WeightedRandomStrategy().get_order_by_clause(),
        ]
        # All should be unique
        assert len(clauses) == len(set(clauses))


class TestStrategyRepr:
    """Test string representation of strategies."""
    
    def test_strategy_str(self):
        """Test __str__ returns class name."""
        strategy = FIFOStrategy()
        assert str(strategy) == "FIFOStrategy"
    
    def test_strategy_repr(self):
        """Test __repr__ returns formatted class name."""
        strategy = FIFOStrategy()
        repr_str = repr(strategy)
        assert "<FIFOStrategy>" == repr_str
    
    def test_all_strategies_have_string_repr(self):
        """Test all strategies have proper string representation."""
        strategies = [
            FIFOStrategy(),
            LIFOStrategy(),
            PriorityStrategy(),
            WeightedRandomStrategy(),
        ]
        
        for strategy in strategies:
            str_repr = str(strategy)
            assert str_repr  # Not empty
            assert "Strategy" in str_repr
            assert str_repr == strategy.__class__.__name__


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
