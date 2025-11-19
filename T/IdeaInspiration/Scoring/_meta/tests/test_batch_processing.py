"""Unit tests for Scoring batch processing functionality."""

import sys
from pathlib import Path

# Add paths
test_dir = Path(__file__).parent
scoring_root = test_dir.parent.parent
model_dir = scoring_root.parent / 'Model'

sys.path.insert(0, str(model_dir))
sys.path.insert(0, str(scoring_root))

from idea_inspiration import IdeaInspiration, ContentType
from src.scoring import ScoringEngine


def test_score_idea_inspiration_single():
    """Test scoring a single IdeaInspiration object."""
    engine = ScoringEngine()
    
    idea = IdeaInspiration(
        title="Test Article",
        description="Test description",
        content="This is a test content with enough text to score properly.",
        keywords=["test", "article"],
        source_type=ContentType.TEXT
    )
    
    score_breakdown = engine.score_idea_inspiration(idea)
    
    assert score_breakdown is not None
    assert hasattr(score_breakdown, 'overall_score')
    assert 0 <= score_breakdown.overall_score <= 100
    assert score_breakdown.title_score >= 0
    assert score_breakdown.description_score >= 0
    assert score_breakdown.text_quality_score >= 0
    print("✓ Single IdeaInspiration scoring works")


def test_score_idea_inspiration_batch():
    """Test scoring multiple IdeaInspiration objects."""
    engine = ScoringEngine()
    
    ideas = [
        IdeaInspiration(
            title="Article 1",
            description="First article",
            content="Content for the first article with sufficient text.",
            keywords=["first"],
            source_type=ContentType.TEXT
        ),
        IdeaInspiration(
            title="Article 2",
            description="Second article",
            content="Content for the second article with good quality text.",
            keywords=["second"],
            source_type=ContentType.TEXT
        ),
        IdeaInspiration(
            title="Video Tutorial",
            description="Learn something new",
            content="Tutorial content goes here with details.",
            keywords=["video", "tutorial"],
            source_type=ContentType.VIDEO,
            metadata={
                'statistics': {
                    'viewCount': '10000',
                    'likeCount': '500',
                    'commentCount': '50'
                }
            }
        )
    ]
    
    score_breakdowns = engine.score_idea_inspiration_batch(ideas)
    
    assert len(score_breakdowns) == 3
    assert all(hasattr(sb, 'overall_score') for sb in score_breakdowns)
    assert all(0 <= sb.overall_score <= 100 for sb in score_breakdowns)
    
    # Video with engagement should have engagement_score > 0
    assert score_breakdowns[2].engagement_score > 0
    
    print("✓ Batch IdeaInspiration scoring works")
    print(f"  - Scored {len(score_breakdowns)} items")
    print(f"  - Scores: {[f'{sb.overall_score:.1f}' for sb in score_breakdowns]}")


def test_score_with_engagement_metrics():
    """Test scoring with engagement metrics."""
    engine = ScoringEngine()
    
    idea = IdeaInspiration(
        title="Popular Video",
        description="Viral content",
        content="This video went viral with millions of views.",
        keywords=["viral", "popular"],
        source_type=ContentType.VIDEO,
        metadata={
            'statistics': {
                'viewCount': '1000000',
                'likeCount': '50000',
                'commentCount': '1000'
            }
        }
    )
    
    score_breakdown = engine.score_idea_inspiration(idea)
    
    assert score_breakdown.engagement_score > 0
    assert score_breakdown.overall_score > 0
    print("✓ Engagement metrics scoring works")
    print(f"  - Engagement score: {score_breakdown.engagement_score:.1f}")


def test_score_empty_list():
    """Test scoring an empty list."""
    engine = ScoringEngine()
    
    result = engine.score_idea_inspiration_batch([])
    
    assert result == []
    print("✓ Empty list handling works")


def test_score_preserves_other_attributes():
    """Test that scoring preserves other IdeaInspiration attributes."""
    engine = ScoringEngine()
    
    idea = IdeaInspiration(
        title="Test",
        description="Description",
        content="Content",
        keywords=["test"],
        source_type=ContentType.TEXT,
        source_id="test-123",
        source_platform="test-platform",
        category="test-category"
    )
    
    score_breakdown = engine.score_idea_inspiration(idea)
    
    # Original object should be unchanged
    assert idea.source_id == "test-123"
    assert idea.source_platform == "test-platform"
    assert idea.category == "test-category"
    print("✓ Original object attributes preserved")


if __name__ == "__main__":
    print("Running Scoring batch processing tests...\n")
    
    test_score_idea_inspiration_single()
    test_score_empty_list()
    test_score_idea_inspiration_batch()
    test_score_with_engagement_metrics()
    test_score_preserves_other_attributes()
    
    print("\nAll tests passed! ✓")
