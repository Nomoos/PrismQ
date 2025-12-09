"""Tests for ScriptWriter model."""

from datetime import datetime

import pytest

from T.Review.Content import (
    CategoryScore,
    ContentLength,
    ImprovementPoint,
    ReviewCategory,
    ScriptReview,
)
from T.Content import (
    FeedbackLoopIteration,
    OptimizationResult,
    OptimizationStrategy,
    ScriptWriter,
)


class TestScriptWriterBasic:
    """Test basic ScriptWriter functionality."""

    def test_create_basic_writer(self):
        """Test creating a basic ScriptWriter instance."""
        writer = ScriptWriter()

        assert writer.writer_id == "AI-ScriptWriter-001"
        assert writer.target_score_threshold == 80
        assert writer.max_iterations == 3
        assert writer.optimization_strategy == OptimizationStrategy.COMPREHENSIVE
        assert writer.current_iteration == 0
        assert writer.iterations_history == []
        assert writer.original_content == ""
        assert writer.current_content == ""
        assert writer.cumulative_improvements == []
        assert writer.initial_score == 0
        assert writer.current_score == 0
        assert writer.score_progression == []
        assert writer.total_score_improvement == 0
        assert writer.target_audience == ""
        assert writer.target_length_seconds is None
        assert writer.youtube_short_mode is False
        assert writer.focus_areas == []

    def test_create_custom_writer(self):
        """Test creating ScriptWriter with custom settings."""
        writer = ScriptWriter(
            writer_id="CustomWriter-001",
            target_score_threshold=85,
            max_iterations=5,
            optimization_strategy=OptimizationStrategy.YOUTUBE_SHORT,
        )

        assert writer.writer_id == "CustomWriter-001"
        assert writer.target_score_threshold == 85
        assert writer.max_iterations == 5
        assert writer.optimization_strategy == OptimizationStrategy.YOUTUBE_SHORT


class TestOptimizationFromReview:
    """Test optimize_from_review functionality."""

    def test_optimize_from_review_basic(self):
        """Test basic optimization from review."""
        writer = ScriptWriter()

        original_content = "Test script content that needs optimization."

        # Create review
        review = ScriptReview(
            content_id="script-001",
            script_title="Test",
            overall_score=70,
            target_audience="Test audience",
            current_length_seconds=120,
            optimal_length_seconds=90,
        )

        # Add improvement point
        review.improvement_points.append(
            ImprovementPoint(
                category=ReviewCategory.PACING,
                title="Improve pacing",
                description="Speed up middle section",
                priority="high",
                impact_score=15,
                suggested_fix="Cut 20 seconds",
            )
        )

        # Optimize
        result = writer.optimize_from_review(original_content=original_content, review=review)

        assert isinstance(result, OptimizationResult)
        assert result.original_text == original_content
        assert len(result.changes_made) > 0
        assert result.estimated_score_improvement >= 0
        assert writer.current_iteration == 1
        assert writer.initial_score == 70
        assert writer.current_score == 70
        assert len(writer.iterations_history) == 1

    def test_optimize_youtube_short(self):
        """Test optimization for YouTube short."""
        writer = ScriptWriter(optimization_strategy=OptimizationStrategy.YOUTUBE_SHORT)

        original_content = "Long script that needs shortening..."

        review = ScriptReview(
            content_id="short-001",
            script_title="Short",
            overall_score=65,
            is_youtube_short=True,
            target_length=ContentLength.YOUTUBE_SHORT,
            current_length_seconds=85,
            optimal_length_seconds=55,
            hook_strength_score=80,
            retention_score=60,
        )

        result = writer.optimize_from_review(
            original_content=original_content, review=review, target_audience="Young adults"
        )

        assert writer.youtube_short_mode is True
        assert writer.target_audience == "Young adults"
        assert writer.target_length_seconds == 55
        assert "YouTube short" in str(result.changes_made)

    def test_optimize_with_major_revision(self):
        """Test optimization when major revision needed."""
        writer = ScriptWriter()

        original_content = "Content with major issues."

        review = ScriptReview(
            content_id="script-001", script_title="Test", overall_score=50, needs_major_revision=True
        )

        result = writer.optimize_from_review(original_content=original_content, review=review)

        # Should indicate major revision
        assert any("major" in change.lower() for change in result.changes_made)
        assert result.estimated_score_improvement >= 20


class TestFeedbackLoopControl:
    """Test feedback loop control methods."""

    def test_should_continue_iteration_max_reached(self):
        """Test stopping when max iterations reached."""
        writer = ScriptWriter(max_iterations=3)
        writer.current_iteration = 3
        writer.current_score = 75  # Below threshold

        assert writer.should_continue_iteration() is False

    def test_should_continue_iteration_threshold_reached(self):
        """Test stopping when threshold reached."""
        writer = ScriptWriter(target_score_threshold=80)
        writer.current_iteration = 1
        writer.current_score = 85  # Above threshold

        assert writer.should_continue_iteration() is False

    def test_should_continue_iteration_diminishing_returns(self):
        """Test stopping on diminishing returns."""
        writer = ScriptWriter()
        writer.current_iteration = 2
        writer.current_score = 75
        writer.score_progression = [70, 73, 75]  # Only +2 and +2

        # Should stop due to small improvements
        assert writer.should_continue_iteration() is False

    def test_should_continue_iteration_normal(self):
        """Test continuing when conditions are good."""
        writer = ScriptWriter(target_score_threshold=80)
        writer.current_iteration = 1
        writer.current_score = 70
        writer.score_progression = [60, 70]  # +10 improvement

        assert writer.should_continue_iteration() is True


class TestFeedbackLoopSummary:
    """Test feedback loop summary."""

    def test_get_feedback_loop_summary(self):
        """Test getting feedback loop summary."""
        writer = ScriptWriter(writer_id="Test-001", target_score_threshold=85, max_iterations=3)

        # Simulate some progress
        writer.current_iteration = 2
        writer.initial_score = 65
        writer.current_score = 78
        writer.score_progression = [65, 72, 78]
        writer.total_score_improvement = 13
        writer.cumulative_improvements = ["Fix pacing", "Improve hook"]
        writer.focus_areas = ["Pacing", "Engagement"]
        writer.target_audience = "Test audience"
        writer.youtube_short_mode = True

        summary = writer.get_feedback_loop_summary()

        assert summary["writer_id"] == "Test-001"
        assert summary["current_iteration"] == 2
        assert summary["max_iterations"] == 3
        assert summary["initial_score"] == 65
        assert summary["current_score"] == 78
        assert summary["total_improvement"] == 13
        assert summary["score_progression"] == [65, 72, 78]
        assert summary["target_threshold"] == 85
        assert summary["target_reached"] is False
        assert summary["improvements_applied"] == 2
        assert summary["focus_areas"] == ["Pacing", "Engagement"]
        assert summary["optimization_strategy"] == "comprehensive"
        assert summary["youtube_short_mode"] is True
        assert summary["target_audience"] == "Test audience"


class TestStrategyDetermination:
    """Test optimization strategy determination."""

    def test_determine_strategy_youtube_short(self):
        """Test strategy for YouTube short optimization."""
        writer = ScriptWriter()

        review = ScriptReview(
            content_id="short-001",
            script_title="Test",
            overall_score=70,
            is_youtube_short=True,
            current_length_seconds=120,
            optimal_length_seconds=60,
        )

        strategy = writer._determine_strategy(review)

        assert strategy == OptimizationStrategy.YOUTUBE_SHORT

    def test_determine_strategy_engagement(self):
        """Test strategy for engagement issues."""
        writer = ScriptWriter()

        review = ScriptReview(content_id="script-001", script_title="Test", overall_score=70)

        # Add weak engagement score
        review.category_scores.append(
            CategoryScore(category=ReviewCategory.ENGAGEMENT, score=60, reasoning="Weak")
        )

        strategy = writer._determine_strategy(review)

        assert strategy == OptimizationStrategy.ENGAGEMENT_BOOST

    def test_determine_strategy_pacing(self):
        """Test strategy for pacing issues."""
        writer = ScriptWriter()

        review = ScriptReview(content_id="script-001", script_title="Test", overall_score=70)

        review.category_scores.append(
            CategoryScore(category=ReviewCategory.PACING, score=55, reasoning="Too slow")
        )

        strategy = writer._determine_strategy(review)

        assert strategy == OptimizationStrategy.PACING_IMPROVEMENT

    def test_determine_strategy_comprehensive(self):
        """Test fallback to comprehensive strategy."""
        writer = ScriptWriter()

        review = ScriptReview(content_id="script-001", script_title="Test", overall_score=70)

        strategy = writer._determine_strategy(review)

        assert strategy == OptimizationStrategy.COMPREHENSIVE


class TestScriptWriterSerialization:
    """Test serialization and deserialization."""

    def test_to_dict(self):
        """Test converting ScriptWriter to dictionary."""
        writer = ScriptWriter(
            writer_id="Test-001",
            target_score_threshold=85,
            optimization_strategy=OptimizationStrategy.YOUTUBE_SHORT,
        )

        writer.current_iteration = 2
        writer.original_content = "Original"
        writer.current_content = "Current"

        data = writer.to_dict()

        assert isinstance(data, dict)
        assert data["writer_id"] == "Test-001"
        assert data["target_score_threshold"] == 85
        assert data["optimization_strategy"] == "youtube_short"
        assert data["current_iteration"] == 2
        assert data["original_content"] == "Original"
        assert data["current_content"] == "Current"

    def test_from_dict(self):
        """Test creating ScriptWriter from dictionary."""
        data = {
            "writer_id": "Test-001",
            "target_score_threshold": 85,
            "max_iterations": 5,
            "optimization_strategy": "youtube_short",
            "current_iteration": 2,
            "original_content": "Original",
            "current_content": "Current",
            "cumulative_improvements": ["Fix 1", "Fix 2"],
            "initial_score": 65,
            "current_score": 78,
            "score_progression": [65, 78],
            "target_audience": "Test",
            "youtube_short_mode": True,
            "iterations_history": [
                {
                    "iteration_number": 1,
                    "review_score": 65,
                    "optimization_applied": ["Fix 1"],
                    "score_improvement": 13,
                }
            ],
        }

        writer = ScriptWriter.from_dict(data)

        assert writer.writer_id == "Test-001"
        assert writer.target_score_threshold == 85
        assert writer.max_iterations == 5
        assert writer.optimization_strategy == OptimizationStrategy.YOUTUBE_SHORT
        assert writer.current_iteration == 2
        assert writer.original_content == "Original"
        assert writer.current_content == "Current"
        assert len(writer.cumulative_improvements) == 2
        assert writer.initial_score == 65
        assert writer.current_score == 78
        assert writer.youtube_short_mode is True
        assert len(writer.iterations_history) == 1

    def test_roundtrip_serialization(self):
        """Test that to_dict -> from_dict preserves data."""
        original = ScriptWriter(
            writer_id="Test-001",
            target_score_threshold=85,
            max_iterations=5,
            optimization_strategy=OptimizationStrategy.YOUTUBE_SHORT,
        )

        original.current_iteration = 2
        original.original_content = "Original text"
        original.current_content = "Current text"
        original.cumulative_improvements = ["Improvement 1", "Improvement 2"]
        original.initial_score = 65
        original.current_score = 78
        original.score_progression = [65, 72, 78]
        original.total_score_improvement = 13
        original.target_audience = "Test audience"
        original.target_length_seconds = 90
        original.youtube_short_mode = True
        original.focus_areas = ["Pacing", "Engagement"]

        # Roundtrip
        data = original.to_dict()
        restored = ScriptWriter.from_dict(data)

        # Compare fields
        assert restored.writer_id == original.writer_id
        assert restored.target_score_threshold == original.target_score_threshold
        assert restored.max_iterations == original.max_iterations
        assert restored.optimization_strategy == original.optimization_strategy
        assert restored.current_iteration == original.current_iteration
        assert restored.original_content == original.original_content
        assert restored.current_content == original.current_content
        assert restored.cumulative_improvements == original.cumulative_improvements
        assert restored.initial_score == original.initial_score
        assert restored.current_score == original.current_score
        assert restored.score_progression == original.score_progression
        assert restored.total_score_improvement == original.total_score_improvement
        assert restored.target_audience == original.target_audience
        assert restored.target_length_seconds == original.target_length_seconds
        assert restored.youtube_short_mode == original.youtube_short_mode
        assert restored.focus_areas == original.focus_areas


class TestScriptWriterRepresentation:
    """Test string representation."""

    def test_repr(self):
        """Test __repr__ method."""
        writer = ScriptWriter(writer_id="Test-001", max_iterations=3)

        writer.current_iteration = 2
        writer.current_score = 78
        writer.total_score_improvement = 13

        repr_str = repr(writer)

        assert "ScriptWriter(" in repr_str
        assert "id='Test-001'" in repr_str
        assert "iteration=2/3" in repr_str
        assert "score=78%" in repr_str
        assert "improvement=+13" in repr_str
