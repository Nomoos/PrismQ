"""Unit tests for Classification batch processing functionality."""

import sys
from pathlib import Path

# Add paths
test_dir = Path(__file__).parent
classification_root = test_dir.parent.parent
model_dir = classification_root.parent / 'Model'

sys.path.insert(0, str(model_dir))
sys.path.insert(0, str(classification_root))

from idea_inspiration import IdeaInspiration, ContentType
from src.classification import TextClassifier, PrimaryCategory


def test_classify_single():
    """Test classifying a single IdeaInspiration object."""
    classifier = TextClassifier()
    
    idea = IdeaInspiration(
        title="My Story About Something That Happened",
        description="Let me tell you what happened...",
        content="So this happened to me yesterday...",
        keywords=["story", "personal"],
        source_type=ContentType.TEXT
    )
    
    enrichment = classifier.enrich(idea)
    
    assert enrichment is not None
    assert hasattr(enrichment, 'category')
    assert isinstance(enrichment.category, PrimaryCategory)
    assert 0 <= enrichment.category_confidence <= 1
    assert enrichment.category == PrimaryCategory.STORYTELLING
    print("✓ Single IdeaInspiration classification works")


def test_classify_batch():
    """Test classifying multiple IdeaInspiration objects."""
    classifier = TextClassifier()
    
    ideas = [
        IdeaInspiration(
            title="AITA Story",
            description="Am I the bad guy here?",
            content="This happened at work...",
            keywords=["aita", "story"],
            source_type=ContentType.TEXT
        ),
        IdeaInspiration(
            title="Funny Meme Compilation",
            description="Best memes",
            content="Check out these hilarious memes",
            keywords=["meme", "funny"],
            source_type=ContentType.VIDEO
        ),
        IdeaInspiration(
            title="Python Tutorial",
            description="Learn Python",
            content="In this tutorial we'll learn...",
            keywords=["tutorial", "python"],
            source_type=ContentType.VIDEO
        )
    ]
    
    enrichments = classifier.enrich_batch(ideas)
    
    assert len(enrichments) == 3
    assert all(hasattr(e, 'category') for e in enrichments)
    
    # Check categories are appropriate
    assert enrichments[0].category == PrimaryCategory.STORYTELLING
    assert enrichments[1].category == PrimaryCategory.ENTERTAINMENT
    assert enrichments[2].category == PrimaryCategory.EDUCATION
    
    print("✓ Batch IdeaInspiration classification works")
    print(f"  - Classified {len(enrichments)} items")
    print(f"  - Categories: {[e.category.value for e in enrichments]}")


def test_classify_batch_alias():
    """Test that classify_batch is an alias for enrich_batch."""
    classifier = TextClassifier()
    
    ideas = [
        IdeaInspiration(
            title="Test",
            description="Test",
            content="Test content",
            keywords=["test"],
            source_type=ContentType.TEXT
        )
    ]
    
    result1 = classifier.enrich_batch(ideas)
    result2 = classifier.classify_batch(ideas)
    
    assert len(result1) == len(result2)
    assert result1[0].category == result2[0].category
    print("✓ classify_batch alias works")


def test_classify_empty_list():
    """Test classifying an empty list."""
    classifier = TextClassifier()
    
    result = classifier.enrich_batch([])
    
    assert result == []
    print("✓ Empty list handling works")


def test_classify_sets_flags():
    """Test that classification sets appropriate flags."""
    classifier = TextClassifier()
    
    story_idea = IdeaInspiration(
        title="My True Story",
        description="This really happened",
        content="Let me tell you what happened...",
        keywords=["story", "true"],
        source_type=ContentType.TEXT
    )
    
    enrichment = classifier.enrich(story_idea)
    
    assert 'is_story' in enrichment.flags
    assert 'is_usable' in enrichment.flags
    assert enrichment.flags['is_story'] == True
    assert enrichment.flags['is_usable'] == True  # Storytelling is usable
    print("✓ Classification flags work correctly")


def test_classify_generates_tags():
    """Test that classification generates tags from indicators."""
    classifier = TextClassifier()
    
    idea = IdeaInspiration(
        title="My AITA Confession Story",
        description="This happened yesterday",
        content="I need to confess something...",
        keywords=["aita", "confession", "story"],
        source_type=ContentType.TEXT
    )
    
    enrichment = classifier.enrich(idea)
    
    assert len(enrichment.tags) > 0
    print("✓ Tag generation works")
    print(f"  - Generated tags: {enrichment.tags}")


def test_classify_different_categories():
    """Test classification across different content categories."""
    classifier = TextClassifier()
    
    test_cases = [
        ("Funny Cat Video", "Comedy compilation", "cats", PrimaryCategory.ENTERTAINMENT),
        ("How to Cook Pasta", "Step by step guide", "tutorial", PrimaryCategory.EDUCATION),
        ("My Daily Routine", "Day in my life", "vlog", PrimaryCategory.LIFESTYLE),
        ("Epic Gaming Moments", "Gameplay highlights", "gaming", PrimaryCategory.GAMING),
    ]
    
    for title, desc, content, expected_category in test_cases:
        idea = IdeaInspiration(
            title=title,
            description=desc,
            content=content,
            keywords=[],
            source_type=ContentType.VIDEO
        )
        
        enrichment = classifier.enrich(idea)
        assert enrichment.category == expected_category, \
            f"Expected {expected_category.value} for '{title}', got {enrichment.category.value}"
    
    print("✓ Multi-category classification works")


if __name__ == "__main__":
    print("Running Classification batch processing tests...\n")
    
    test_classify_single()
    test_classify_empty_list()
    test_classify_batch()
    test_classify_batch_alias()
    test_classify_sets_flags()
    test_classify_generates_tags()
    test_classify_different_categories()
    
    print("\nAll tests passed! ✓")
