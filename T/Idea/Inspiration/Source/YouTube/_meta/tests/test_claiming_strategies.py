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
    WorkflowStateStrategy,
    WORKFLOW_STATE_ORDER,
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
    
    def test_workflow_state_strategy_instantiation(self):
        """Test WorkflowStateStrategy can be instantiated."""
        strategy = WorkflowStateStrategy()
        assert isinstance(strategy, BaseClaimStrategy)
        assert str(strategy) == "WorkflowStateStrategy"


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
    
    def test_workflow_state_order_by(self):
        """Test WORKFLOW_STATE generates correct ORDER BY clause."""
        strategy = WorkflowStateStrategy()
        order_by = strategy.get_order_by_clause()
        assert "CASE" in order_by
        assert "state" in order_by
        assert "DESC" in order_by
        assert "created_at ASC" in order_by
    
    def test_workflow_state_order_by_contains_all_states(self):
        """Test WORKFLOW_STATE ORDER BY contains all workflow states."""
        strategy = WorkflowStateStrategy()
        order_by = strategy.get_order_by_clause()
        
        # Check that key workflow states are included
        assert "PrismQ.T.Idea.Creation" in order_by
        assert "PrismQ.T.Title.From.Idea" in order_by
        assert "PrismQ.T.Publishing" in order_by
        assert "PrismQ.T.Story.Review" in order_by


class TestStrategyRegistry:
    """Test strategy registry and lookup."""
    
    def test_strategies_registry_contains_all(self):
        """Test STRATEGIES contains all five strategies."""
        assert len(STRATEGIES) == 5
        assert 'FIFO' in STRATEGIES
        assert 'LIFO' in STRATEGIES
        assert 'PRIORITY' in STRATEGIES
        assert 'WEIGHTED_RANDOM' in STRATEGIES
        assert 'WORKFLOW_STATE' in STRATEGIES
    
    def test_strategies_are_correct_types(self):
        """Test registry contains correct strategy instances."""
        assert isinstance(STRATEGIES['FIFO'], FIFOStrategy)
        assert isinstance(STRATEGIES['LIFO'], LIFOStrategy)
        assert isinstance(STRATEGIES['PRIORITY'], PriorityStrategy)
        assert isinstance(STRATEGIES['WEIGHTED_RANDOM'], WeightedRandomStrategy)
        assert isinstance(STRATEGIES['WORKFLOW_STATE'], WorkflowStateStrategy)


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
    
    def test_get_strategy_workflow_state(self):
        """Test getting WORKFLOW_STATE strategy."""
        strategy = get_strategy('WORKFLOW_STATE')
        assert isinstance(strategy, WorkflowStateStrategy)
    
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
    
    def test_returns_list_of_five(self):
        """Test returns list of 5 strategy names."""
        strategies = get_available_strategies()
        assert isinstance(strategies, list)
        assert len(strategies) == 5
    
    def test_contains_all_strategies(self):
        """Test list contains all strategy names."""
        strategies = get_available_strategies()
        assert 'FIFO' in strategies
        assert 'LIFO' in strategies
        assert 'PRIORITY' in strategies
        assert 'WEIGHTED_RANDOM' in strategies
        assert 'WORKFLOW_STATE' in strategies
    
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
    
    def test_workflow_state_vs_priority_different(self):
        """Test WORKFLOW_STATE and PRIORITY produce different ORDER BY clauses."""
        workflow = WorkflowStateStrategy()
        priority = PriorityStrategy()
        assert workflow.get_order_by_clause() != priority.get_order_by_clause()
    
    def test_all_strategies_unique(self):
        """Test all strategies produce unique ORDER BY clauses."""
        clauses = [
            FIFOStrategy().get_order_by_clause(),
            LIFOStrategy().get_order_by_clause(),
            PriorityStrategy().get_order_by_clause(),
            WeightedRandomStrategy().get_order_by_clause(),
            WorkflowStateStrategy().get_order_by_clause(),
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
            WorkflowStateStrategy(),
        ]
        
        for strategy in strategies:
            str_repr = str(strategy)
            assert str_repr  # Not empty
            assert "Strategy" in str_repr
            assert str_repr == strategy.__class__.__name__


class TestWorkflowStateOrder:
    """Test workflow state order mapping."""
    
    def test_workflow_state_order_contains_all_stages(self):
        """Test WORKFLOW_STATE_ORDER contains all 19 workflow stages."""
        assert len(WORKFLOW_STATE_ORDER) == 19
    
    def test_workflow_state_order_starts_with_idea_creation(self):
        """Test workflow starts with Idea.Creation as stage 1."""
        assert WORKFLOW_STATE_ORDER['PrismQ.T.Idea.Creation'] == 1
    
    def test_workflow_state_order_ends_with_publishing(self):
        """Test workflow ends with Publishing as stage 19."""
        assert WORKFLOW_STATE_ORDER['PrismQ.T.Publishing'] == 19
    
    def test_workflow_state_order_is_sequential(self):
        """Test workflow stages are numbered sequentially."""
        values = sorted(WORKFLOW_STATE_ORDER.values())
        expected = list(range(1, 20))
        assert values == expected
    
    def test_workflow_state_order_generation_stages(self):
        """Test generation stages follow correct order."""
        assert WORKFLOW_STATE_ORDER['PrismQ.T.Title.From.Idea'] == 2
        assert WORKFLOW_STATE_ORDER['PrismQ.T.Script.From.Title.Idea'] == 3
    
    def test_workflow_state_order_review_stages(self):
        """Test review stages follow correct order."""
        # Initial reviews (stages 4-6)
        assert WORKFLOW_STATE_ORDER['PrismQ.T.Review.Title.By.Script.Idea'] == 4
        assert WORKFLOW_STATE_ORDER['PrismQ.T.Review.Script.By.Title.Idea'] == 5
        assert WORKFLOW_STATE_ORDER['PrismQ.T.Review.Title.By.Script'] == 6
        
        # Quality reviews (stages 10-16)
        assert WORKFLOW_STATE_ORDER['PrismQ.T.Review.Script.Grammar'] == 10
        assert WORKFLOW_STATE_ORDER['PrismQ.T.Review.Script.Readability'] == 16
    
    def test_workflow_state_order_expert_review(self):
        """Test expert review stages follow correct order."""
        assert WORKFLOW_STATE_ORDER['PrismQ.T.Story.Review'] == 17
        assert WORKFLOW_STATE_ORDER['PrismQ.T.Story.Polish'] == 18


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
