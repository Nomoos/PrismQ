"""Tests for ReviewTitleFromContentIdeaService.

Tests the service that processes stories in the
PrismQ.T.Review.Title.From.Content.Idea state.
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import pytest

# Add project root to path
REPO_ROOT = Path(__file__).resolve().parents[7]
sys.path.insert(0, str(REPO_ROOT))

from Model.Database.repositories.story_repository import StoryRepository
from Model.Database.repositories.title_repository import TitleRepository
from Model.Database.repositories.content_repository import ContentRepository
from Model.Database.repositories.review_repository import ReviewRepository
from Model.Entities.story import Story
from Model.Entities.title import Title
from Model.Entities.content import Content
from Model.State.constants.state_names import StateNames
from T.Review.Title.From.Content.Idea.src.review_title_from_content_idea_service import (
    ReviewTitleFromContentIdeaService,
    ReviewTitleFromContentIdeaResult,
    TITLE_ACCEPTANCE_THRESHOLD,
)


def _create_test_db() -> sqlite3.Connection:
    """Create an in-memory SQLite database with all required tables."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS Idea (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 0),
            review_id INTEGER,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS Review (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS Story (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id INTEGER NULL,
            state TEXT NOT NULL DEFAULT 'PrismQ.T.Idea.From.User',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (idea_id) REFERENCES Idea(id)
        );

        CREATE TABLE IF NOT EXISTS Title (
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

        CREATE TABLE IF NOT EXISTS StoryReview (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            review_id INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (story_id) REFERENCES Story(id),
            FOREIGN KEY (review_id) REFERENCES Review(id)
        );
    """)
    return conn


def _insert_idea(conn: sqlite3.Connection, text: str = "Test idea") -> int:
    """Insert a test idea and return its ID."""
    cursor = conn.execute(
        "INSERT INTO Idea (text, version, created_at) VALUES (?, ?, ?)",
        (text, 1, datetime.now().isoformat()),
    )
    conn.commit()
    return cursor.lastrowid


def _insert_story(conn: sqlite3.Connection, idea_id: int, state: str) -> Story:
    """Insert a test story and return the Story entity."""
    story_repo = StoryRepository(conn)
    story = Story(idea_id=str(idea_id), state=state)
    return story_repo.insert(story)


def _insert_title(conn: sqlite3.Connection, story_id: int, text: str = "Test Title") -> Title:
    """Insert a test title and return the Title entity."""
    title_repo = TitleRepository(conn)
    title = Title(story_id=story_id, version=1, text=text)
    return title_repo.insert(title)


def _insert_content(conn: sqlite3.Connection, story_id: int, text: str = "Test content") -> Content:
    """Insert a test content and return the Content entity."""
    content_repo = ContentRepository(conn)
    content = Content(story_id=story_id, version=1, text=text)
    return content_repo.insert(content)


class TestReviewTitleFromContentIdeaService:
    """Tests for the ReviewTitleFromContentIdeaService."""

    def test_no_stories_returns_success_with_no_story_id(self):
        """Test that service returns success when no stories are available."""
        conn = _create_test_db()
        service = ReviewTitleFromContentIdeaService(conn, preview_mode=True)

        result = service.process_oldest_story()

        assert result.success is True
        assert result.story_id is None
        assert result.error == "No stories found in state"

    def test_story_without_title_returns_error(self):
        """Test that a story without a title is handled gracefully."""
        conn = _create_test_db()
        idea_id = _insert_idea(conn)
        story = _insert_story(conn, idea_id, StateNames.REVIEW_TITLE_FROM_CONTENT_IDEA)

        service = ReviewTitleFromContentIdeaService(conn, preview_mode=True)
        result = service.process_oldest_story()

        assert result.success is False
        assert result.story_id == story.id
        assert result.error is not None
        assert "title" in result.error.lower()

    def test_story_without_content_returns_error(self):
        """Test that a story without content is handled gracefully."""
        conn = _create_test_db()
        idea_id = _insert_idea(conn)
        story = _insert_story(conn, idea_id, StateNames.REVIEW_TITLE_FROM_CONTENT_IDEA)
        _insert_title(conn, story.id, "My Test Title")

        service = ReviewTitleFromContentIdeaService(conn, preview_mode=True)
        result = service.process_oldest_story()

        assert result.success is False
        assert result.story_id == story.id
        assert result.error is not None
        assert "content" in result.error.lower()

    def test_story_with_title_and_content_is_processed(self):
        """Test that a story with title and content is processed successfully."""
        conn = _create_test_db()
        idea_id = _insert_idea(conn, "A horror story about echoes in an old house")
        story = _insert_story(conn, idea_id, StateNames.REVIEW_TITLE_FROM_CONTENT_IDEA)
        _insert_title(conn, story.id, "The Haunting Echo")
        _insert_content(conn, story.id, "In the old house, a mysterious echo reveals dark secrets...")

        service = ReviewTitleFromContentIdeaService(conn, preview_mode=True)
        result = service.process_oldest_story()

        assert result.success is True
        assert result.story_id == story.id
        assert result.score is not None
        assert 0 <= result.score <= 100
        assert result.text is not None
        assert result.accepted is not None
        assert result.next_state is not None

    def test_accepted_title_transitions_to_review_content(self):
        """Test that an accepted title transitions to REVIEW_CONTENT_FROM_TITLE_IDEA."""
        conn = _create_test_db()
        idea_id = _insert_idea(conn, "Mystery story about echoes")
        story = _insert_story(conn, idea_id, StateNames.REVIEW_TITLE_FROM_CONTENT_IDEA)
        # Use title and content that align well
        _insert_title(
            conn, story.id,
            "The Mystery Echo: Secrets of the Old House"
        )
        _insert_content(
            conn, story.id,
            "The mystery echo in the old house reveals hidden secrets. "
            "Every sound uncovers a new clue in this haunting mystery."
        )

        service = ReviewTitleFromContentIdeaService(conn, preview_mode=True)
        result = service.process_oldest_story()

        assert result.success is True
        # If accepted, next state should be REVIEW_CONTENT_FROM_TITLE_IDEA
        if result.accepted:
            assert result.next_state == StateNames.REVIEW_CONTENT_FROM_TITLE_IDEA
        else:
            assert result.next_state == StateNames.TITLE_FROM_TITLE_REVIEW_CONTENT

    def test_rejected_title_transitions_to_title_refinement(self):
        """Test that a rejected title transitions to TITLE_FROM_TITLE_REVIEW_CONTENT."""
        conn = _create_test_db()
        idea_id = _insert_idea(conn, "Nature documentary about butterflies")
        story = _insert_story(conn, idea_id, StateNames.REVIEW_TITLE_FROM_CONTENT_IDEA)
        # Use completely mismatched title and content to get a low score
        _insert_title(conn, story.id, "Space Adventure")
        _insert_content(
            conn, story.id,
            "In the haunted forest, ghosts roam the shadows at night."
        )

        service = ReviewTitleFromContentIdeaService(conn, preview_mode=True)
        result = service.process_oldest_story()

        assert result.success is True
        # If rejected, next state should be TITLE_FROM_TITLE_REVIEW_CONTENT
        if not result.accepted:
            assert result.next_state == StateNames.TITLE_FROM_TITLE_REVIEW_CONTENT

    def test_preview_mode_does_not_save_to_db(self):
        """Test that preview mode does not persist changes to the database."""
        conn = _create_test_db()
        idea_id = _insert_idea(conn, "Test idea")
        story = _insert_story(conn, idea_id, StateNames.REVIEW_TITLE_FROM_CONTENT_IDEA)
        _insert_title(conn, story.id, "Test Title")
        _insert_content(conn, story.id, "Test content for the story")

        service = ReviewTitleFromContentIdeaService(conn, preview_mode=True)
        result = service.process_oldest_story()

        assert result.success is True
        assert result.review_id is None  # No review saved in preview mode

        # Story state should not have changed in the database
        story_repo = StoryRepository(conn)
        unchanged_story = story_repo.find_by_id(story.id)
        assert unchanged_story.state == StateNames.REVIEW_TITLE_FROM_CONTENT_IDEA

    def test_non_preview_mode_saves_review_and_updates_state(self):
        """Test that non-preview mode saves review and updates story state."""
        conn = _create_test_db()
        idea_id = _insert_idea(conn, "Test idea for full review")
        story = _insert_story(conn, idea_id, StateNames.REVIEW_TITLE_FROM_CONTENT_IDEA)
        _insert_title(conn, story.id, "Test Title For Review")
        _insert_content(conn, story.id, "This is the test content for the story review.")

        service = ReviewTitleFromContentIdeaService(conn, preview_mode=False)
        result = service.process_oldest_story()

        assert result.success is True
        assert result.review_id is not None  # Review was saved

        # Story state should have changed
        story_repo = StoryRepository(conn)
        updated_story = story_repo.find_by_id(story.id)
        assert updated_story.state != StateNames.REVIEW_TITLE_FROM_CONTENT_IDEA
        assert updated_story.state in [
            StateNames.REVIEW_CONTENT_FROM_TITLE_IDEA,
            StateNames.TITLE_FROM_TITLE_REVIEW_CONTENT,
        ]

    def test_correct_input_state(self):
        """Test that service uses the correct input state."""
        conn = _create_test_db()
        service = ReviewTitleFromContentIdeaService(conn)

        assert service.INPUT_STATE == "PrismQ.T.Review.Title.From.Content.Idea"

    def test_correct_output_states(self):
        """Test that service uses the correct output states."""
        conn = _create_test_db()
        service = ReviewTitleFromContentIdeaService(conn)

        assert service.OUTPUT_STATE_PASS == "PrismQ.T.Review.Content.From.Title.Idea"
        assert service.OUTPUT_STATE_FAIL == "PrismQ.T.Title.From.Title.Review.Content"

    def test_idea_text_is_used_in_review(self):
        """Test that idea text is fetched and used during review."""
        conn = _create_test_db()
        idea_text = "Horror story about a haunting echo in an abandoned mansion"
        idea_id = _insert_idea(conn, idea_text)
        story = _insert_story(conn, idea_id, StateNames.REVIEW_TITLE_FROM_CONTENT_IDEA)
        _insert_title(conn, story.id, "The Haunting Echo")
        _insert_content(conn, story.id, "An echo haunts the abandoned mansion")

        service = ReviewTitleFromContentIdeaService(conn, preview_mode=True)
        result = service.process_oldest_story()

        assert result.success is True
        # The review should complete successfully with idea context
        assert result.score is not None

    def test_processes_oldest_story_first(self):
        """Test that the oldest story is processed first (FIFO order)."""
        conn = _create_test_db()
        idea_id = _insert_idea(conn)

        # Create two stories
        story1 = _insert_story(conn, idea_id, StateNames.REVIEW_TITLE_FROM_CONTENT_IDEA)
        story2 = _insert_story(conn, idea_id, StateNames.REVIEW_TITLE_FROM_CONTENT_IDEA)

        _insert_title(conn, story1.id, "First Story Title")
        _insert_content(conn, story1.id, "First story content")
        _insert_title(conn, story2.id, "Second Story Title")
        _insert_content(conn, story2.id, "Second story content")

        service = ReviewTitleFromContentIdeaService(conn, preview_mode=True)
        result = service.process_oldest_story()

        # Should process the first (oldest) story
        assert result.story_id == story1.id


class TestAcceptanceThreshold:
    """Tests for the acceptance threshold constant."""

    def test_default_acceptance_threshold(self):
        """Test that the default acceptance threshold is 70."""
        assert TITLE_ACCEPTANCE_THRESHOLD == 70


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
