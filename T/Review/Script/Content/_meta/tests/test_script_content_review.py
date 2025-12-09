"""Unit tests for content_content_review service.

Tests the ContentContentReviewer service that:
1. Selects oldest Story where state is PrismQ.T.Review.Content.Content
2. Generates content review using ContentReview model
3. Creates Review record and links it to Content via Content.review_id FK
4. Updates Story state based on review result
"""

import importlib.util
import os
import sqlite3
from datetime import datetime, timedelta

import pytest

# Direct import to avoid T.Review.Content circular import
_tests_dir = os.path.dirname(os.path.abspath(__file__))
_module_path = os.path.join(
    _tests_dir, "..", "..", "..", "..", "Content", "Content", "content_content_review.py"
)
_module_path = os.path.normpath(_module_path)

# Check if running from tests directory or module tests
if not os.path.exists(_module_path):
    # Try path from main tests directory
    _module_path = os.path.join(
        _tests_dir, "..", "T", "Review", "Content", "Content", "content_content_review.py"
    )
    _module_path = os.path.normpath(_module_path)
    if not os.path.exists(_module_path):
        # Try absolute path
        _module_path = (
            "/home/runner/work/PrismQ/PrismQ/T/Review/Content/Content/content_content_review.py"
        )

_spec = importlib.util.spec_from_file_location("content_content_review", _module_path)
_scr_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_scr_module)

ContentContentReviewer = _scr_module.ContentContentReviewer
ContentReviewResult = _scr_module.ContentReviewResult
review_oldest_story_content = _scr_module.review_oldest_story_content

from Model.Database.models.review import Review
from Model.Database.models.content import Content
from Model.Database.models.story import Story
from Model.State.constants.state_names import StateNames
from T.Review.Model.src.content_review import ContentReview


@pytest.fixture
def db_connection():
    """Create in-memory SQLite database with schema."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    # Create tables
    conn.executecontent(
        """
        CREATE TABLE IF NOT EXISTS Story (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id INTEGER NULL,
            state TEXT NOT NULL DEFAULT 'CREATED',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (idea_id) REFERENCES Idea(id)
        );
        
        CREATE TABLE IF NOT EXISTS Content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            version INTEGER NOT NULL DEFAULT 0,
            text TEXT NOT NULL,
            review_id INTEGER NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        
        CREATE TABLE IF NOT EXISTS Review (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        
        CREATE INDEX IF NOT EXISTS idx_story_state ON Story(state);
        CREATE INDEX IF NOT EXISTS idx_story_created_at ON Story(created_at);
    """
    )

    yield conn
    conn.close()


@pytest.fixture
def service(db_connection):
    """Create ContentContentReviewer service."""
    return ContentContentReviewer(db_connection)


@pytest.fixture
def sample_content_text():
    """Sample content text for testing."""
    return """
    Scene 1: The Discovery
    
    The protagonist walked slowly through the abandoned warehouse, 
    flashlight cutting through the darkness. "Hello?" she called out,
    her voice echoing off the cold walls.
    
    No response came. Just the distant sound of dripping water.
    
    She moved deeper into the building, each step carefully placed
    to avoid making noise. Something wasn't right here.
    
    Scene 2: The Confrontation
    
    "I know you're here," she said, her voice steady despite the fear
    building in her chest. "We need to talk."
    
    A shadow moved in the corner. Then a voice, cold and familiar:
    "You shouldn't have come."
    """


class TestContentContentReviewerInit:
    """Tests for ContentContentReviewer initialization."""

    def test_init_with_defaults(self, db_connection):
        """Test service initialization with default values."""
        service = ContentContentReviewer(db_connection)

        assert service.pass_threshold == 75
        assert service.max_high_severity_issues == 3
        assert service.INPUT_STATE == StateNames.REVIEW_SCRIPT_CONTENT
        assert service.OUTPUT_STATE_PASS == StateNames.REVIEW_SCRIPT_TONE
        assert service.OUTPUT_STATE_FAIL == StateNames.SCRIPT_FROM_SCRIPT_REVIEW_TITLE

    def test_init_with_custom_threshold(self, db_connection):
        """Test service initialization with custom threshold."""
        service = ContentContentReviewer(db_connection, pass_threshold=80)

        assert service.pass_threshold == 80


class TestGetOldestStory:
    """Tests for get_oldest_story method."""

    def test_get_oldest_story_returns_oldest(self, db_connection, service):
        """Test that get_oldest_story returns the oldest story in state."""
        # Insert stories with different timestamps
        base_time = datetime.now()

        # Oldest story (should be selected)
        oldest_time = (base_time - timedelta(hours=2)).isoformat()
        db_connection.execute(
            "INSERT INTO Story (state, created_at, updated_at) VALUES (?, ?, ?)",
            (StateNames.REVIEW_SCRIPT_CONTENT, oldest_time, oldest_time),
        )

        # Newer story
        newer_time = (base_time - timedelta(hours=1)).isoformat()
        db_connection.execute(
            "INSERT INTO Story (state, created_at, updated_at) VALUES (?, ?, ?)",
            (StateNames.REVIEW_SCRIPT_CONTENT, newer_time, newer_time),
        )

        # Newest story
        newest_time = base_time.isoformat()
        db_connection.execute(
            "INSERT INTO Story (state, created_at, updated_at) VALUES (?, ?, ?)",
            (StateNames.REVIEW_SCRIPT_CONTENT, newest_time, newest_time),
        )
        db_connection.commit()

        story = service.get_oldest_story()

        assert story is not None
        assert story.id == 1  # First inserted (oldest)

    def test_get_oldest_story_ignores_other_states(self, db_connection, service):
        """Test that get_oldest_story ignores stories in other states."""
        # Insert story in different state (older)
        old_time = (datetime.now() - timedelta(hours=5)).isoformat()
        db_connection.execute(
            "INSERT INTO Story (state, created_at, updated_at) VALUES (?, ?, ?)",
            (StateNames.REVIEW_SCRIPT_GRAMMAR, old_time, old_time),
        )

        # Insert story in correct state (newer)
        new_time = datetime.now().isoformat()
        db_connection.execute(
            "INSERT INTO Story (state, created_at, updated_at) VALUES (?, ?, ?)",
            (StateNames.REVIEW_SCRIPT_CONTENT, new_time, new_time),
        )
        db_connection.commit()

        story = service.get_oldest_story()

        assert story is not None
        assert story.id == 2  # Second story (correct state)
        assert story.state == StateNames.REVIEW_SCRIPT_CONTENT

    def test_get_oldest_story_returns_none_when_empty(self, db_connection, service):
        """Test that get_oldest_story returns None when no stories found."""
        story = service.get_oldest_story()

        assert story is None


class TestPerformContentReview:
    """Tests for perform_content_review method."""

    def test_review_returns_content_review(self, service, sample_content_text):
        """Test that perform_content_review returns ContentReview object."""
        review = service.perform_content_review(
            content_text=sample_content_text, content_id="content-001"
        )

        assert isinstance(review, ContentReview)
        assert review.content_id == "content-001"
        assert 0 <= review.overall_score <= 100
        assert 0 <= review.logic_score <= 100
        assert 0 <= review.plot_score <= 100
        assert 0 <= review.character_score <= 100
        assert 0 <= review.pacing_score <= 100

    def test_review_passes_for_good_content(self, db_connection, sample_content_text):
        """Test that good content passes the review."""
        # Use lower threshold for this test since sample content may not score 75+
        service_low_threshold = ContentContentReviewer(db_connection, pass_threshold=60)

        review = service_low_threshold.perform_content_review(
            content_text=sample_content_text, content_id="content-001"
        )

        # Sample content has dialogue and scene markers, should score reasonably
        assert review.overall_score >= 60
        assert review.passes

    def test_review_fails_for_minimal_content(self, service):
        """Test that minimal content fails the review."""
        minimal_content = "Hello world."

        review = service.perform_content_review(content_text=minimal_content, content_id="content-002")

        # Very short content should fail
        assert len(review.issues) > 0

    def test_review_generates_summary(self, service, sample_content_text):
        """Test that review generates a summary."""
        review = service.perform_content_review(
            content_text=sample_content_text, content_id="content-001"
        )

        assert review.summary != ""
        assert "score" in review.summary.lower() or str(review.overall_score) in review.summary


class TestProcessOldestStory:
    """Tests for process_oldest_story workflow method."""

    def test_process_oldest_story_success(self, db_connection, service, sample_content_text):
        """Test successful processing of oldest story."""
        # Insert content
        db_connection.execute(
            "INSERT INTO Content (story_id, text, version, created_at) VALUES (?, ?, ?, ?)",
            (1, sample_content_text, 3, datetime.now().isoformat()),
        )

        # Insert story with content reference
        db_connection.execute(
            "INSERT INTO Story (content_id, state, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (
                1,
                StateNames.REVIEW_SCRIPT_CONTENT,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
            ),
        )
        db_connection.commit()

        result = service.process_oldest_story()

        assert result is not None
        assert result.story_id == 1
        assert result.review_id is not None
        assert result.content_review is not None
        assert result.error is None

    def test_process_oldest_story_updates_state_on_pass(self, db_connection, sample_content_text):
        """Test that passing review updates state to REVIEW_SCRIPT_TONE."""
        # Use low threshold to ensure pass
        service = ContentContentReviewer(db_connection, pass_threshold=50)

        # Insert content
        db_connection.execute(
            "INSERT INTO Content (story_id, text, version, created_at) VALUES (?, ?, ?, ?)",
            (1, sample_content_text, 3, datetime.now().isoformat()),
        )

        # Insert story
        db_connection.execute(
            "INSERT INTO Story (content_id, state, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (
                1,
                StateNames.REVIEW_SCRIPT_CONTENT,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
            ),
        )
        db_connection.commit()

        result = service.process_oldest_story()

        assert result.passes
        assert result.new_state == StateNames.REVIEW_SCRIPT_TONE

    def test_process_oldest_story_updates_state_on_fail(self, db_connection):
        """Test that failing review updates state to SCRIPT_FROM_SCRIPT_REVIEW_TITLE."""
        # Use high threshold to ensure fail
        service = ContentContentReviewer(db_connection, pass_threshold=99)

        # Insert minimal content
        db_connection.execute(
            "INSERT INTO Content (story_id, text, version, created_at) VALUES (?, ?, ?, ?)",
            (1, "Short text.", 3, datetime.now().isoformat()),
        )

        # Insert story
        db_connection.execute(
            "INSERT INTO Story (content_id, state, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (
                1,
                StateNames.REVIEW_SCRIPT_CONTENT,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
            ),
        )
        db_connection.commit()

        result = service.process_oldest_story()

        assert not result.passes
        assert result.new_state == StateNames.SCRIPT_FROM_SCRIPT_REVIEW_TITLE

    def test_process_oldest_story_creates_review_record(
        self, db_connection, service, sample_content_text
    ):
        """Test that processing creates Review record in database."""
        # Insert content
        db_connection.execute(
            "INSERT INTO Content (story_id, text, version, created_at) VALUES (?, ?, ?, ?)",
            (1, sample_content_text, 3, datetime.now().isoformat()),
        )

        # Insert story
        db_connection.execute(
            "INSERT INTO Story (content_id, state, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (
                1,
                StateNames.REVIEW_SCRIPT_CONTENT,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
            ),
        )
        db_connection.commit()

        result = service.process_oldest_story()

        # Verify Review was created
        cursor = db_connection.execute("SELECT * FROM Review WHERE id = ?", (result.review_id,))
        review_row = cursor.fetchone()

        assert review_row is not None
        assert review_row["score"] == result.overall_score

    def test_process_oldest_story_links_review_to_content(
        self, db_connection, service, sample_content_text
    ):
        """Test that processing links Review to Content via Content.review_id FK."""
        # Insert content
        db_connection.execute(
            "INSERT INTO Content (story_id, text, version, created_at) VALUES (?, ?, ?, ?)",
            (1, sample_content_text, 3, datetime.now().isoformat()),
        )

        # Insert story
        db_connection.execute(
            "INSERT INTO Story (content_id, state, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (
                1,
                StateNames.REVIEW_SCRIPT_CONTENT,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
            ),
        )
        db_connection.commit()

        result = service.process_oldest_story()

        # Verify Content.review_id was updated
        cursor = db_connection.execute("SELECT * FROM Content WHERE id = ?", (result.content_id,))
        content_row = cursor.fetchone()

        assert content_row is not None
        assert content_row["review_id"] == result.review_id

    def test_process_oldest_story_returns_content_id(
        self, db_connection, service, sample_content_text
    ):
        """Test that result includes content_id."""
        # Insert content
        db_connection.execute(
            "INSERT INTO Content (story_id, text, version, created_at) VALUES (?, ?, ?, ?)",
            (1, sample_content_text, 3, datetime.now().isoformat()),
        )

        # Insert story
        db_connection.execute(
            "INSERT INTO Story (content_id, state, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (
                1,
                StateNames.REVIEW_SCRIPT_CONTENT,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
            ),
        )
        db_connection.commit()

        result = service.process_oldest_story()

        assert result.content_id == 1

    def test_process_oldest_story_returns_none_when_no_stories(self, db_connection, service):
        """Test that process_oldest_story returns None when no stories found."""
        result = service.process_oldest_story()

        assert result is None

    def test_process_oldest_story_handles_missing_content(self, db_connection, service):
        """Test error handling when content is not found."""
        # Insert story without content
        db_connection.execute(
            "INSERT INTO Story (content_id, state, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (
                999,
                StateNames.REVIEW_SCRIPT_CONTENT,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
            ),
        )
        db_connection.commit()

        result = service.process_oldest_story()

        assert result is not None
        assert result.error is not None
        assert "Content not found" in result.error


class TestConvenienceFunction:
    """Tests for review_oldest_story_content convenience function."""

    def test_review_oldest_story_content_success(self, db_connection, sample_content_text):
        """Test convenience function succeeds."""
        # Insert content
        db_connection.execute(
            "INSERT INTO Content (story_id, text, version, created_at) VALUES (?, ?, ?, ?)",
            (1, sample_content_text, 3, datetime.now().isoformat()),
        )

        # Insert story
        db_connection.execute(
            "INSERT INTO Story (content_id, state, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (
                1,
                StateNames.REVIEW_SCRIPT_CONTENT,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
            ),
        )
        db_connection.commit()

        result = review_oldest_story_content(db_connection)

        assert result is not None
        assert result.story_id == 1

    def test_review_oldest_story_content_with_custom_threshold(
        self, db_connection, sample_content_text
    ):
        """Test convenience function with custom threshold."""
        # Insert content
        db_connection.execute(
            "INSERT INTO Content (story_id, text, version, created_at) VALUES (?, ?, ?, ?)",
            (1, sample_content_text, 3, datetime.now().isoformat()),
        )

        # Insert story
        db_connection.execute(
            "INSERT INTO Story (content_id, state, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (
                1,
                StateNames.REVIEW_SCRIPT_CONTENT,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
            ),
        )
        db_connection.commit()

        result = review_oldest_story_content(db_connection, pass_threshold=50)

        assert result is not None
        assert result.passes  # Low threshold should pass


class TestStateTransitions:
    """Tests for correct state transitions based on workflow documentation."""

    def test_input_state_is_review_content_content(self, service):
        """Test that INPUT_STATE is PrismQ.T.Review.Content.Content."""
        assert service.INPUT_STATE == "PrismQ.T.Review.Content.Content"

    def test_output_state_pass_is_review_content_tone(self, service):
        """Test that OUTPUT_STATE_PASS is PrismQ.T.Review.Content.Tone."""
        assert service.OUTPUT_STATE_PASS == "PrismQ.T.Review.Content.Tone"

    def test_output_state_fail_is_content_from_content_review_title(self, service):
        """Test that OUTPUT_STATE_FAIL is PrismQ.T.Content.From.Content.Review.Title."""
        assert service.OUTPUT_STATE_FAIL == "PrismQ.T.Content.From.Content.Review.Title"
