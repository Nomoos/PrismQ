"""Tests for unclassified IdeaInspiration processing."""

import sys
from pathlib import Path
import tempfile

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from workers.classification_worker import ClassificationWorker
from classification import IdeaInspiration, ContentType


def test_find_unclassified_ideas():
    """Test finding unclassified IdeaInspiration records."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        worker = ClassificationWorker(
            worker_id="test-worker",
            idea_db_path=tmp.name
        )
        
        # Insert test data
        idea1 = IdeaInspiration(
            title="Unclassified 1",
            description="Test",
            content="Content",
            keywords=["test"],
            source_type=ContentType.TEXT,
            source_platform="test",
            category=None  # Unclassified
        )
        
        idea2 = IdeaInspiration(
            title="Classified",
            description="Test",
            content="Content",
            keywords=["test"],
            source_type=ContentType.TEXT,
            source_platform="test",
            category="Education / Informational"  # Already classified
        )
        
        idea3 = IdeaInspiration(
            title="Unclassified 2",
            description="Test",
            content="Content",
            keywords=["test"],
            source_type=ContentType.TEXT,
            source_platform="test",
            category=""  # Empty category
        )
        
        worker.idea_db.insert(idea1)
        worker.idea_db.insert(idea2)
        worker.idea_db.insert(idea3)
        
        # Find unclassified
        unclassified = worker.find_unclassified_ideas(limit=10)
        
        assert len(unclassified) == 2
        assert 1 in unclassified
        assert 3 in unclassified
        assert 2 not in unclassified


def test_process_unclassified_ideas():
    """Test processing unclassified IdeaInspiration records."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        worker = ClassificationWorker(
            worker_id="test-worker",
            idea_db_path=tmp.name
        )
        
        # Insert unclassified test data
        idea1 = IdeaInspiration(
            title="Amazing startup story",
            description="A founder's journey",
            content="This is a narrative about building a startup...",
            keywords=["startup", "story"],
            source_type=ContentType.TEXT,
            source_platform="reddit"
        )
        
        idea2 = IdeaInspiration(
            title="Python tutorial",
            description="Learn Python basics",
            content="Python programming tutorial...",
            keywords=["python", "tutorial"],
            source_type=ContentType.TEXT,
            source_platform="youtube"
        )
        
        id1 = worker.idea_db.insert(idea1)
        id2 = worker.idea_db.insert(idea2)
        
        # Process unclassified
        result = worker.process_unclassified_ideas(limit=10)
        
        assert result['processed'] == 2
        assert result['successful'] == 2
        assert result['failed'] == 0
        
        # Verify classification was applied
        classified1 = worker.idea_db.get_by_id(id1)
        classified2 = worker.idea_db.get_by_id(id2)
        
        assert classified1.category is not None
        assert classified2.category is not None
        
        # Verify no more unclassified
        remaining = worker.find_unclassified_ideas(limit=10)
        assert len(remaining) == 0


def test_process_unclassified_with_limit():
    """Test processing unclassified records respects limit."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        worker = ClassificationWorker(
            worker_id="test-worker",
            idea_db_path=tmp.name
        )
        
        # Insert 5 unclassified records
        for i in range(5):
            idea = IdeaInspiration(
                title=f"Test {i}",
                description="Test",
                content="Content",
                keywords=["test"],
                source_type=ContentType.TEXT,
                source_platform="test"
            )
            worker.idea_db.insert(idea)
        
        # Process with limit=2
        result = worker.process_unclassified_ideas(limit=2)
        
        assert result['processed'] == 2
        
        # Verify 3 remain unclassified
        remaining = worker.find_unclassified_ideas(limit=10)
        assert len(remaining) == 3


def test_process_unclassified_empty_database():
    """Test processing when no unclassified records exist."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        worker = ClassificationWorker(
            worker_id="test-worker",
            idea_db_path=tmp.name
        )
        
        # Process with empty database
        result = worker.process_unclassified_ideas(limit=10)
        
        assert result['processed'] == 0
        assert result['successful'] == 0
        assert result['failed'] == 0


if __name__ == '__main__':
    # Run tests
    test_find_unclassified_ideas()
    print("✓ test_find_unclassified_ideas")
    
    test_process_unclassified_ideas()
    print("✓ test_process_unclassified_ideas")
    
    test_process_unclassified_with_limit()
    print("✓ test_process_unclassified_with_limit")
    
    test_process_unclassified_empty_database()
    print("✓ test_process_unclassified_empty_database")
    
    print("\nAll tests passed!")
