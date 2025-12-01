"""Tests for ScriptConsistencyReviewService.

Tests the workflow step PrismQ.T.Review.Script.Consistency that:
1. Selects oldest Story with state PrismQ.T.Review.Script.Consistency
2. Performs consistency review on script
3. Creates Review record
4. Links Review directly to Script via review_id FK
5. Updates Story state based on review result
"""

import json
import pytest
import sqlite3
from datetime import datetime, timedelta

from T.Database.models.story import Story
from T.Database.models.script import Script
from T.Database.models.review import Review
from T.Database.repositories.story_repository import StoryRepository
from T.Database.repositories.script_repository import ScriptRepository
from T.Database.repositories.review_repository import ReviewRepository
from T.State.constants.state_names import StateNames

from T.Review.Script.Consistency.src.script_consistency_review_service import (
    ScriptConsistencyReviewService,
    ConsistencyReviewResult,
    process_oldest_consistency_review,
    process_all_consistency_reviews,
    STATE_REVIEW_SCRIPT_CONSISTENCY,
    STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT,
    STATE_REVIEW_SCRIPT_CONTENT,
    DEFAULT_PASS_THRESHOLD,
)


@pytest.fixture
def db_connection():
    """Create an in-memory SQLite database with all required tables."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    
    # Create tables
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Review (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Script (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            version INTEGER NOT NULL CHECK (version >= 0),
            text TEXT NOT NULL,
            review_id INTEGER NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(story_id, version)
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Story (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id TEXT NULL,
            idea_json TEXT NULL,
            title_id INTEGER NULL,
            script_id INTEGER NULL,
            state TEXT NOT NULL DEFAULT 'CREATED',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def sample_consistent_script():
    """Script text that should pass consistency review."""
    return """John walked into the old house at dusk.
The building was empty, dark and quiet.
He looked around nervously.
John climbed the stairs slowly.
At the top, there was a closed door.
He opened it and saw a figure in the shadows.
It was Mary, his old friend from college.
"Mary?" John said. "What are you doing here?"
She smiled. "I came to help you, John."
"""


@pytest.fixture
def sample_inconsistent_script():
    """Script text that should fail consistency review due to name inconsistencies."""
    return """John walked into the old house at dusk.
The building was empty, dark and quiet.
He looked around nervously.
Suddenly, Johnny heard a noise from upstairs.
John climbed the stairs slowly.
At the top, there was a closed door.
He opened it and saw a figure in the shadows.
It was Mary, his old friend from college.
But wait - hadn't Mary died last year?
Johnny remembered attending her funeral.
Yet here she was, standing before him.
"Maria?" he said. "How is this possible?"
She smiled. "I never died, Johnny. That was someone else."
"""


class TestScriptConsistencyReviewService:
    """Tests for ScriptConsistencyReviewService."""
    
    def test_count_pending_empty(self, db_connection):
        """Test count_pending when no stories exist."""
        service = ScriptConsistencyReviewService(db_connection)
        
        assert service.count_pending() == 0
    
    def test_count_pending_with_stories(self, db_connection):
        """Test count_pending with stories in correct state."""
        service = ScriptConsistencyReviewService(db_connection)
        story_repo = StoryRepository(db_connection)
        
        # Create stories in target state
        for i in range(3):
            story_repo.insert(Story(
                state=STATE_REVIEW_SCRIPT_CONSISTENCY,
                script_id=i + 1
            ))
        
        # Create story in different state
        story_repo.insert(Story(state='CREATED'))
        
        assert service.count_pending() == 3
    
    def test_get_oldest_story_empty(self, db_connection):
        """Test get_oldest_story when no stories exist."""
        service = ScriptConsistencyReviewService(db_connection)
        
        assert service.get_oldest_story() is None
    
    def test_get_oldest_story_returns_oldest(self, db_connection):
        """Test get_oldest_story returns the oldest story."""
        service = ScriptConsistencyReviewService(db_connection)
        story_repo = StoryRepository(db_connection)
        
        base_time = datetime.now()
        
        # Create stories with different creation times
        story1 = story_repo.insert(Story(
            state=STATE_REVIEW_SCRIPT_CONSISTENCY,
            script_id=1,
            created_at=base_time - timedelta(hours=2)
        ))
        
        story2 = story_repo.insert(Story(
            state=STATE_REVIEW_SCRIPT_CONSISTENCY,
            script_id=2,
            created_at=base_time
        ))
        
        oldest = service.get_oldest_story()
        
        assert oldest is not None
        assert oldest.id == story1.id
    
    def test_process_oldest_story_no_stories(self, db_connection):
        """Test process_oldest_story when no stories exist."""
        service = ScriptConsistencyReviewService(db_connection)
        
        result = service.process_oldest_story()
        
        assert result.success is False
        assert result.story_id is None
        assert "No stories found" in result.error
    
    def test_process_oldest_story_missing_script(self, db_connection):
        """Test process_oldest_story when story has no script_id."""
        service = ScriptConsistencyReviewService(db_connection)
        story_repo = StoryRepository(db_connection)
        
        # Create story without script_id
        story = story_repo.insert(Story(
            state=STATE_REVIEW_SCRIPT_CONSISTENCY,
            script_id=None
        ))
        
        result = service.process_oldest_story()
        
        assert result.success is False
        assert result.story_id == story.id
        assert "no script_id" in result.error
    
    def test_process_oldest_story_script_not_found(self, db_connection):
        """Test process_oldest_story when script doesn't exist."""
        service = ScriptConsistencyReviewService(db_connection)
        story_repo = StoryRepository(db_connection)
        
        # Create story with non-existent script_id
        story = story_repo.insert(Story(
            state=STATE_REVIEW_SCRIPT_CONSISTENCY,
            script_id=999  # Non-existent script
        ))
        
        result = service.process_oldest_story()
        
        assert result.success is False
        assert result.story_id == story.id
        assert "not found" in result.error
    
    def test_process_oldest_story_passes(
        self, db_connection, sample_consistent_script
    ):
        """Test process_oldest_story with script that passes review."""
        service = ScriptConsistencyReviewService(db_connection)
        story_repo = StoryRepository(db_connection)
        script_repo = ScriptRepository(db_connection)
        review_repo = ReviewRepository(db_connection)
        
        # Create story and script
        story = story_repo.insert(Story(
            state=STATE_REVIEW_SCRIPT_CONSISTENCY
        ))
        
        script = script_repo.insert(Script(
            story_id=story.id,
            version=0,
            text=sample_consistent_script
        ))
        
        story.script_id = script.id
        story_repo.update(story)
        
        # Process
        result = service.process_oldest_story()
        
        assert result.success is True
        assert result.story_id == story.id
        assert result.script_id == script.id
        assert result.review_id is not None
        assert result.score >= 0
        assert result.passes is True  # Consistent script should pass
        assert result.new_state == STATE_REVIEW_SCRIPT_CONTENT
        
        # Verify Review was created
        review = review_repo.find_by_id(result.review_id)
        assert review is not None
        assert review.score == result.score
        
        # Verify Script has review_id FK set (Review linked directly to Script)
        updated_script = script_repo.find_by_id(script.id)
        assert updated_script.review_id == result.review_id
        
        # Verify Story state was updated
        updated_story = story_repo.find_by_id(story.id)
        assert updated_story.state == STATE_REVIEW_SCRIPT_CONTENT
    
    def test_process_oldest_story_fails(
        self, db_connection, sample_inconsistent_script
    ):
        """Test process_oldest_story with script that fails review."""
        # Use a lower threshold to ensure pass, or create really inconsistent script
        service = ScriptConsistencyReviewService(db_connection, pass_threshold=95)
        story_repo = StoryRepository(db_connection)
        script_repo = ScriptRepository(db_connection)
        
        # Create story and script with inconsistencies
        story = story_repo.insert(Story(
            state=STATE_REVIEW_SCRIPT_CONSISTENCY
        ))
        
        script = script_repo.insert(Script(
            story_id=story.id,
            version=0,
            text=sample_inconsistent_script
        ))
        
        story.script_id = script.id
        story_repo.update(story)
        
        # Process
        result = service.process_oldest_story()
        
        assert result.success is True
        assert result.story_id == story.id
        # The script has name inconsistencies, should fail with high threshold
        assert result.new_state == STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT
        
        # Verify Story state was updated to failure state
        updated_story = story_repo.find_by_id(story.id)
        assert updated_story.state == STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT
    
    def test_process_oldest_story_fifo_order(self, db_connection, sample_consistent_script):
        """Test that stories are processed in FIFO order."""
        service = ScriptConsistencyReviewService(db_connection)
        story_repo = StoryRepository(db_connection)
        script_repo = ScriptRepository(db_connection)
        
        base_time = datetime.now()
        
        # Create stories in different order
        stories = []
        for i, offset in enumerate([3, 1, 2]):  # Created out of order
            story = story_repo.insert(Story(
                state=STATE_REVIEW_SCRIPT_CONSISTENCY,
                created_at=base_time - timedelta(hours=offset)
            ))
            script = script_repo.insert(Script(
                story_id=story.id,
                version=0,
                text=sample_consistent_script
            ))
            story.script_id = script.id
            story_repo.update(story)
            stories.append(story)
        
        # Process first - should be oldest (3 hours ago)
        result1 = service.process_oldest_story()
        assert result1.success is True
        assert result1.story_id == stories[0].id  # 3 hours ago
        
        # Process second - should be 2 hours ago
        result2 = service.process_oldest_story()
        assert result2.success is True
        assert result2.story_id == stories[2].id  # 2 hours ago
        
        # Process third - should be 1 hour ago
        result3 = service.process_oldest_story()
        assert result3.success is True
        assert result3.story_id == stories[1].id  # 1 hour ago
        
        # No more stories
        result4 = service.process_oldest_story()
        assert result4.success is False
        assert result4.story_id is None
    
    def test_process_all_pending(self, db_connection, sample_consistent_script):
        """Test process_all_pending processes all stories."""
        service = ScriptConsistencyReviewService(db_connection)
        story_repo = StoryRepository(db_connection)
        script_repo = ScriptRepository(db_connection)
        
        # Create multiple stories
        for i in range(3):
            story = story_repo.insert(Story(
                state=STATE_REVIEW_SCRIPT_CONSISTENCY
            ))
            script = script_repo.insert(Script(
                story_id=story.id,
                version=0,
                text=sample_consistent_script
            ))
            story.script_id = script.id
            story_repo.update(story)
        
        results = service.process_all_pending()
        
        assert len(results) == 3
        assert all(r.success for r in results)
        assert service.count_pending() == 0
    
    def test_process_all_pending_with_limit(self, db_connection, sample_consistent_script):
        """Test process_all_pending with limit."""
        service = ScriptConsistencyReviewService(db_connection)
        story_repo = StoryRepository(db_connection)
        script_repo = ScriptRepository(db_connection)
        
        # Create 5 stories
        for i in range(5):
            story = story_repo.insert(Story(
                state=STATE_REVIEW_SCRIPT_CONSISTENCY
            ))
            script = script_repo.insert(Script(
                story_id=story.id,
                version=0,
                text=sample_consistent_script
            ))
            story.script_id = script.id
            story_repo.update(story)
        
        results = service.process_all_pending(limit=2)
        
        assert len(results) == 2
        assert service.count_pending() == 3
    
    def test_get_processing_summary(self, db_connection, sample_consistent_script):
        """Test get_processing_summary returns correct statistics."""
        service = ScriptConsistencyReviewService(db_connection)
        story_repo = StoryRepository(db_connection)
        script_repo = ScriptRepository(db_connection)
        
        # Create stories
        for i in range(2):
            story = story_repo.insert(Story(
                state=STATE_REVIEW_SCRIPT_CONSISTENCY
            ))
            script = script_repo.insert(Script(
                story_id=story.id,
                version=0,
                text=sample_consistent_script
            ))
            story.script_id = script.id
            story_repo.update(story)
        
        results = service.process_all_pending()
        summary = service.get_processing_summary(results)
        
        assert summary['total_processed'] == 2
        assert summary['successful'] == 2
        assert summary['failed'] == 0
        assert summary['success_rate'] == 1.0
        assert summary['input_state'] == STATE_REVIEW_SCRIPT_CONSISTENCY
        assert summary['output_state_pass'] == STATE_REVIEW_SCRIPT_CONTENT
        assert summary['output_state_fail'] == STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT


class TestConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_process_oldest_consistency_review(
        self, db_connection, sample_consistent_script
    ):
        """Test process_oldest_consistency_review function."""
        story_repo = StoryRepository(db_connection)
        script_repo = ScriptRepository(db_connection)
        
        # Create story and script
        story = story_repo.insert(Story(
            state=STATE_REVIEW_SCRIPT_CONSISTENCY
        ))
        script = script_repo.insert(Script(
            story_id=story.id,
            version=0,
            text=sample_consistent_script
        ))
        story.script_id = script.id
        story_repo.update(story)
        
        result = process_oldest_consistency_review(db_connection)
        
        assert result.success is True
        assert result.story_id == story.id
    
    def test_process_oldest_consistency_review_empty(self, db_connection):
        """Test process_oldest_consistency_review when no stories."""
        result = process_oldest_consistency_review(db_connection)
        
        assert result.success is False
        assert result.error is not None
    
    def test_process_all_consistency_reviews(
        self, db_connection, sample_consistent_script
    ):
        """Test process_all_consistency_reviews function."""
        story_repo = StoryRepository(db_connection)
        script_repo = ScriptRepository(db_connection)
        
        # Create stories
        for i in range(2):
            story = story_repo.insert(Story(
                state=STATE_REVIEW_SCRIPT_CONSISTENCY
            ))
            script = script_repo.insert(Script(
                story_id=story.id,
                version=0,
                text=sample_consistent_script
            ))
            story.script_id = script.id
            story_repo.update(story)
        
        summary = process_all_consistency_reviews(db_connection)
        
        assert summary['total_processed'] == 2
        assert summary['successful'] == 2


class TestStateConstants:
    """Tests for state constants."""
    
    def test_state_constants_match_state_names(self):
        """Test that state constants match StateNames."""
        assert STATE_REVIEW_SCRIPT_CONSISTENCY == StateNames.REVIEW_SCRIPT_CONSISTENCY
        assert STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT == StateNames.SCRIPT_FROM_TITLE_REVIEW_SCRIPT
        assert STATE_REVIEW_SCRIPT_CONTENT == StateNames.REVIEW_SCRIPT_CONTENT
    
    def test_default_pass_threshold(self):
        """Test default pass threshold value."""
        assert DEFAULT_PASS_THRESHOLD == 80
