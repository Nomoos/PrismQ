"""Tests for Content Grammar Review Service (PrismQ.T.Review.Content.Grammar).

Tests the grammar review service functionality including:
- Processing stories in PrismQ.T.Review.Content.Grammar state
- Creating Review records
- Linking Reviews to Content via FK (Content.review_id)
- State transitions based on review outcome

Note: StoryReview linking table is not used for Content reviews.
"""

import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(project_root))

import pytest

from Model.Database.models.review import Review
from Model.State.constants.state_names import StateNames
from T.Review.Content.Grammar import (
    DEFAULT_PASS_THRESHOLD,
    INPUT_STATE,
    OUTPUT_STATE_FAIL,
    OUTPUT_STATE_PASS,
    GrammarReviewResult,
    ContentGrammarReviewService,
    process_oldest_grammar_review,
)


@pytest.fixture
def db_connection():
    """Create an in-memory database with required schema."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    # Create required tables
    conn.executecontent(
        """
        CREATE TABLE IF NOT EXISTS Idea (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 0),
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        
        CREATE TABLE IF NOT EXISTS Story (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id INTEGER NULL,
            state TEXT NOT NULL DEFAULT 'PrismQ.T.Title.From.Idea',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (idea_id) REFERENCES Idea(id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_story_state ON Story(state);
        CREATE INDEX IF NOT EXISTS idx_story_created_at ON Story(created_at);
        
        CREATE TABLE IF NOT EXISTS Content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            version INTEGER NOT NULL CHECK (version >= 0),
            text TEXT NOT NULL,
            review_id INTEGER NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(story_id, version),
            FOREIGN KEY (story_id) REFERENCES Story(id),
            FOREIGN KEY (review_id) REFERENCES Review(id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_content_story_id ON Content(story_id);
        
        CREATE TABLE IF NOT EXISTS Review (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """
    )
    conn.commit()

    yield conn

    conn.close()


@pytest.fixture
def service(db_connection):
    """Create a ContentGrammarReviewService with the test database."""
    return ContentGrammarReviewService(db_connection)


class TestContentGrammarReviewService:
    """Test the ContentGrammarReviewService class."""

    def test_service_initialization(self, db_connection):
        """Test that service initializes correctly."""
        service = ContentGrammarReviewService(db_connection)

        assert service.story_repo is not None
        assert service.content_repo is not None
        assert service.review_repo is not None
        assert service.grammar_checker is not None
        assert service.pass_threshold == DEFAULT_PASS_THRESHOLD

    def test_service_with_custom_threshold(self, db_connection):
        """Test service with custom pass threshold."""
        service = ContentGrammarReviewService(db_connection, pass_threshold=90)

        assert service.pass_threshold == 90
        assert service.grammar_checker.pass_threshold == 90

    def test_count_pending_no_stories(self, service):
        """Test count_pending returns 0 when no stories exist."""
        count = service.count_pending()

        assert count == 0

    def test_get_oldest_story_no_stories(self, service):
        """Test get_oldest_story returns None when no stories exist."""
        story = service.get_oldest_story()

        assert story is None

    def test_process_oldest_story_no_stories(self, service):
        """Test process_oldest_story when no stories exist."""
        result = service.process_oldest_story()

        assert result.success is False
        assert result.story_id is None
        assert result.error is not None
        assert "No stories found" in result.error


class TestGrammarReviewProcessing:
    """Test grammar review processing workflow."""

    def _create_test_story_with_content(
        self, conn, content_text: str, state: str = INPUT_STATE, created_at: str = None
    ) -> int:
        """Helper to create a test story with a content."""
        cursor = conn.cursor()

        # Create story
        if created_at:
            cursor.execute(
                "INSERT INTO Story (state, created_at, updated_at) VALUES (?, ?, ?)",
                (state, created_at, created_at),
            )
        else:
            cursor.execute("INSERT INTO Story (state) VALUES (?)", (state,))
        story_id = cursor.lastrowid

        # Create content for the story
        cursor.execute(
            "INSERT INTO Content (story_id, version, text) VALUES (?, ?, ?)",
            (story_id, 0, content_text),
        )

        conn.commit()
        return story_id

    def test_process_story_with_correct_grammar(self, db_connection, service):
        """Test processing a story with grammatically correct content."""
        # Create a story with correct grammar
        content_text = """The hero walked into the sunset.
Birds sang their evening songs.
Nature welcomed the night."""

        story_id = self._create_test_story_with_content(db_connection, content_text)

        # Process the story
        result = service.process_oldest_story()

        # Should succeed and pass
        assert result.success is True
        assert result.story_id == story_id
        assert result.passes is True
        assert result.score >= 85
        assert result.review_id is not None
        assert result.new_state == OUTPUT_STATE_PASS

        # Verify story state was updated
        cursor = db_connection.execute("SELECT state FROM Story WHERE id = ?", (story_id,))
        row = cursor.fetchone()
        assert row["state"] == OUTPUT_STATE_PASS

    def test_process_story_with_grammar_errors(self, db_connection, service):
        """Test processing a story with grammar errors."""
        # Create a story with grammar errors
        content_text = """He were walking down the street.
I recieved a message yesterday.
They was very happy about it."""

        story_id = self._create_test_story_with_content(db_connection, content_text)

        # Process the story
        result = service.process_oldest_story()

        # Should succeed but fail grammar review
        assert result.success is True
        assert result.story_id == story_id
        assert result.passes is False
        assert result.score < 85
        assert result.review_id is not None
        assert result.issues_count > 0
        assert result.new_state == OUTPUT_STATE_FAIL

        # Verify story state was updated
        cursor = db_connection.execute("SELECT state FROM Story WHERE id = ?", (story_id,))
        row = cursor.fetchone()
        assert row["state"] == OUTPUT_STATE_FAIL

    def test_review_record_created(self, db_connection, service):
        """Test that a Review record is created."""
        content_text = "The hero walks into the room."
        story_id = self._create_test_story_with_content(db_connection, content_text)

        # Process the story
        result = service.process_oldest_story()

        # Verify Review record exists
        cursor = db_connection.execute("SELECT * FROM Review WHERE id = ?", (result.review_id,))
        review_row = cursor.fetchone()

        assert review_row is not None
        assert review_row["score"] >= 0
        assert review_row["score"] <= 100
        assert "Grammar Review" in review_row["text"]

    def test_content_review_id_set(self, db_connection, service):
        """Test that Content.review_id FK is set to link Review directly."""
        content_text = "The hero saves the day."
        story_id = self._create_test_story_with_content(db_connection, content_text)

        # Process the story
        result = service.process_oldest_story()

        # Verify Content.review_id is set
        cursor = db_connection.execute("SELECT * FROM Content WHERE story_id = ?", (story_id,))
        content_row = cursor.fetchone()

        assert content_row is not None
        assert content_row["review_id"] == result.review_id


class TestFIFOOrdering:
    """Test that stories are processed in FIFO order (oldest first)."""

    def _create_test_story_with_content(
        self, conn, content_text: str, state: str, created_at: str
    ) -> int:
        """Helper to create a test story with a content."""
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO Story (state, created_at, updated_at) VALUES (?, ?, ?)",
            (state, created_at, created_at),
        )
        story_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO Content (story_id, version, text) VALUES (?, ?, ?)",
            (story_id, 0, content_text),
        )

        conn.commit()
        return story_id

    def test_oldest_story_processed_first(self, db_connection, service):
        """Test that the oldest story is processed first."""
        # Create stories with different timestamps
        base_time = datetime.now()

        old_time = (base_time - timedelta(hours=2)).isoformat()
        mid_time = (base_time - timedelta(hours=1)).isoformat()
        new_time = base_time.isoformat()

        # Create in non-chronological order
        story2 = self._create_test_story_with_content(
            db_connection, "Story 2 text.", INPUT_STATE, mid_time
        )
        story1 = self._create_test_story_with_content(
            db_connection, "Story 1 text.", INPUT_STATE, old_time
        )
        story3 = self._create_test_story_with_content(
            db_connection, "Story 3 text.", INPUT_STATE, new_time
        )

        # First processing should get story1 (oldest)
        result = service.process_oldest_story()
        assert result.story_id == story1

        # Second processing should get story2
        result = service.process_oldest_story()
        assert result.story_id == story2

        # Third processing should get story3
        result = service.process_oldest_story()
        assert result.story_id == story3

    def test_only_correct_state_processed(self, db_connection, service):
        """Test that only stories with correct state are processed."""
        # Create stories with different states
        base_time = datetime.now()

        # Story in correct state
        story1 = self._create_test_story_with_content(
            db_connection,
            "Correct state story.",
            INPUT_STATE,
            (base_time - timedelta(hours=1)).isoformat(),
        )

        # Story in different state (should be ignored)
        cursor = db_connection.cursor()
        cursor.execute(
            "INSERT INTO Story (state, created_at) VALUES (?, ?)",
            ("PrismQ.T.Other.State", base_time.isoformat()),
        )
        story2 = cursor.lastrowid
        cursor.execute(
            "INSERT INTO Content (story_id, version, text) VALUES (?, ?, ?)",
            (story2, 0, "Different state story."),
        )
        db_connection.commit()

        # Processing should only get story1
        result = service.process_oldest_story()
        assert result.story_id == story1

        # No more stories to process
        result = service.process_oldest_story()
        assert result.story_id is None


class TestProcessAllPending:
    """Test processing all pending stories."""

    def _create_test_story_with_content(self, conn, content_text: str) -> int:
        """Helper to create a test story with a content."""
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Story (state) VALUES (?)", (INPUT_STATE,))
        story_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO Content (story_id, version, text) VALUES (?, ?, ?)",
            (story_id, 0, content_text),
        )
        conn.commit()
        return story_id

    def test_process_all_pending(self, db_connection, service):
        """Test processing all pending stories."""
        # Create multiple stories
        story_ids = [
            self._create_test_story_with_content(db_connection, f"Story {i} text.") for i in range(3)
        ]

        # Process all
        results = service.process_all_pending()

        assert len(results) == 3
        assert all(r.success for r in results)
        processed_ids = [r.story_id for r in results]
        assert set(processed_ids) == set(story_ids)

    def test_process_all_pending_with_limit(self, db_connection, service):
        """Test processing with limit."""
        # Create 5 stories
        for i in range(5):
            self._create_test_story_with_content(db_connection, f"Story {i} text.")

        # Process with limit of 2
        results = service.process_all_pending(limit=2)

        assert len(results) == 2

    def test_get_processing_summary(self, db_connection, service):
        """Test getting processing summary."""
        # Create stories with different outcomes
        # Good grammar
        self._create_test_story_with_content(db_connection, "Perfect grammar here.")
        # Bad grammar
        self._create_test_story_with_content(db_connection, "He were happy. I recieved gifts.")

        # Process all
        results = service.process_all_pending()

        # Get summary
        summary = service.get_processing_summary(results)

        assert summary["total_processed"] == 2
        assert summary["successful"] == 2
        assert summary["failed"] == 0
        assert "input_state" in summary
        assert "output_state_pass" in summary
        assert "output_state_fail" in summary


class TestConvenienceFunction:
    """Test the convenience function process_oldest_grammar_review."""

    def test_process_oldest_grammar_review(self, db_connection):
        """Test the convenience function."""
        # Create a story
        cursor = db_connection.cursor()
        cursor.execute("INSERT INTO Story (state) VALUES (?)", (INPUT_STATE,))
        story_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO Content (story_id, version, text) VALUES (?, ?, ?)",
            (story_id, 0, "The hero walks away."),
        )
        db_connection.commit()

        # Use convenience function
        result = process_oldest_grammar_review(db_connection)

        assert result.success is True
        assert result.story_id == story_id


class TestStateConstants:
    """Test that state constants are correct."""

    def test_input_state(self):
        """Test input state constant."""
        assert INPUT_STATE == StateNames.REVIEW_SCRIPT_GRAMMAR
        assert INPUT_STATE == "PrismQ.T.Review.Content.Grammar"

    def test_output_state_pass(self):
        """Test output state for passing reviews."""
        assert OUTPUT_STATE_PASS == StateNames.REVIEW_SCRIPT_CONSISTENCY
        assert OUTPUT_STATE_PASS == "PrismQ.T.Review.Content.Consistency"

    def test_output_state_fail(self):
        """Test output state for failing reviews."""
        assert OUTPUT_STATE_FAIL == StateNames.SCRIPT_FROM_TITLE_REVIEW_SCRIPT
        assert OUTPUT_STATE_FAIL == "PrismQ.T.Content.From.Title.Review.Content"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
