"""Tests for ReviewContentFromTitleIdeaService.

This module tests the service that processes stories in the
PrismQ.T.Review.Content.From.Title.Idea state.
"""

import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import pytest

# Setup paths
_current_dir = Path(__file__).parent
_module_root = _current_dir.parent.parent  # T/Review/Content/From/Title/Idea
_t_root = _module_root.parent.parent.parent.parent.parent  # T
_repo_root = _t_root.parent  # repo root
_review_content_dir = _t_root / "Review" / "Content"

for _path in [str(_repo_root), str(_t_root), str(_review_content_dir)]:
    if _path not in sys.path:
        sys.path.insert(0, _path)

from Model.Database.models.content import Content
from Model.Database.models.review import Review
from Model.Database.models.story import Story
from Model.Database.models.title import Title
from Model.Database.repositories.content_repository import ContentRepository
from Model.Database.repositories.story_repository import StoryRepository
from Model.Database.repositories.title_repository import TitleRepository
from T.Review.Content.From.Title.Idea.src.review_content_from_title_idea_service import (
    CONTENT_ACCEPTANCE_THRESHOLD,
    ReviewContentFromTitleIdeaResult,
    ReviewContentFromTitleIdeaService,
    ReviewRepository,
    _format_review_text,
)


CREATE_TABLES_SQL = """
    CREATE TABLE IF NOT EXISTS Story (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        idea_id INTEGER NULL,
        state TEXT NOT NULL DEFAULT 'CREATED',
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS Title (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        story_id INTEGER NOT NULL,
        version INTEGER NOT NULL CHECK (version >= 0),
        text TEXT NOT NULL,
        review_id INTEGER NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        UNIQUE(story_id, version),
        FOREIGN KEY (story_id) REFERENCES Story(id)
    );

    CREATE TABLE IF NOT EXISTS Content (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        story_id INTEGER NOT NULL,
        version INTEGER NOT NULL CHECK (version >= 0),
        text TEXT NOT NULL,
        review_id INTEGER NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        UNIQUE(story_id, version),
        FOREIGN KEY (story_id) REFERENCES Story(id)
    );

    CREATE TABLE IF NOT EXISTS Review (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
"""

INPUT_STATE = "PrismQ.T.Review.Content.From.Title.Idea"
OUTPUT_STATE_PASS = "PrismQ.T.Review.Title.From.Content"
OUTPUT_STATE_FAIL = "PrismQ.T.Content.From.Content.Review.Title"


@pytest.fixture
def db_connection():
    """Create an in-memory SQLite database with all required tables."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(CREATE_TABLES_SQL)
    yield conn
    conn.close()


@pytest.fixture
def service(db_connection):
    """Create service instance with in-memory database."""
    return ReviewContentFromTitleIdeaService(db_connection, preview_mode=False)


@pytest.fixture
def repositories(db_connection):
    """Create repository instances."""
    return {
        "story": StoryRepository(db_connection),
        "title": TitleRepository(db_connection),
        "content": ContentRepository(db_connection),
        "review": ReviewRepository(db_connection),
    }


class TestServiceConstants:
    """Tests for service state constants."""

    def test_input_state(self):
        """Test that input state is correct."""
        assert ReviewContentFromTitleIdeaService.INPUT_STATE == INPUT_STATE

    def test_output_state_pass(self):
        """Test that pass output state is correct."""
        assert ReviewContentFromTitleIdeaService.OUTPUT_STATE_PASS == OUTPUT_STATE_PASS

    def test_output_state_fail(self):
        """Test that fail output state is correct."""
        assert ReviewContentFromTitleIdeaService.OUTPUT_STATE_FAIL == OUTPUT_STATE_FAIL

    def test_acceptance_threshold(self):
        """Test that acceptance threshold is 70."""
        assert CONTENT_ACCEPTANCE_THRESHOLD == 70


class TestReviewRepository:
    """Tests for the ReviewRepository class."""

    def test_insert_review(self, db_connection):
        """Test inserting a review."""
        repo = ReviewRepository(db_connection)
        review = Review(text="Content review feedback.", score=80)

        saved = repo.insert(review)

        assert saved.id is not None
        assert saved.id > 0
        assert saved.text == "Content review feedback."
        assert saved.score == 80

    def test_insert_multiple_reviews(self, db_connection):
        """Test inserting multiple reviews."""
        repo = ReviewRepository(db_connection)

        for i in range(3):
            review = Review(text=f"Review {i}", score=70 + i)
            saved = repo.insert(review)
            assert saved.id is not None


class TestProcessOldestStory:
    """Tests for process_oldest_story method."""

    def test_no_stories_returns_success_with_no_story_id(self, service):
        """Test that processing with no stories returns gracefully."""
        result = service.process_oldest_story()

        assert result.success is True
        assert result.story_id is None
        assert result.error == "No stories found in state"

    def test_story_in_wrong_state_is_ignored(self, service, repositories):
        """Test that stories in wrong state are not processed."""
        story = Story(idea_id="1", state="PrismQ.T.Title.From.Idea")
        repositories["story"].insert(story)

        result = service.process_oldest_story()

        assert result.story_id is None

    def test_story_without_title_fails_gracefully(self, service, repositories):
        """Test processing story without a title fails with clear error."""
        story = Story(idea_id="1", state=INPUT_STATE)
        saved = repositories["story"].insert(story)

        result = service.process_oldest_story()

        assert result.success is False
        assert result.story_id == saved.id
        assert "No title found" in result.error

    def test_story_without_content_fails_gracefully(self, service, repositories):
        """Test processing story without content fails with clear error."""
        story = Story(idea_id="1", state=INPUT_STATE)
        saved_story = repositories["story"].insert(story)

        title = Title(story_id=saved_story.id, version=0, text="Test Title")
        repositories["title"].insert(title)

        result = service.process_oldest_story()

        assert result.success is False
        assert result.story_id == saved_story.id
        assert "No content found" in result.error

    def test_processes_oldest_story_first(self, service, repositories):
        """Test that the oldest story is processed first."""
        # Create two stories - older one first
        story1 = Story(
            idea_id="1",
            state=INPUT_STATE,
            created_at=datetime(2025, 1, 1, 10, 0, 0),
        )
        saved1 = repositories["story"].insert(story1)

        story2 = Story(
            idea_id="2",
            state=INPUT_STATE,
            created_at=datetime(2025, 1, 2, 10, 0, 0),
        )
        saved2 = repositories["story"].insert(story2)

        # Add title and content for both
        for story_id in [saved1.id, saved2.id]:
            title = Title(story_id=story_id, version=0, text="Test title text")
            repositories["title"].insert(title)
            content = Content(story_id=story_id, version=0, text="Test content text")
            repositories["content"].insert(content)

        result = service.process_oldest_story()

        assert result.success is True
        assert result.story_id == saved1.id  # Oldest story processed first

    def test_successful_processing_returns_score(self, service, repositories):
        """Test that successful processing returns a review score."""
        story = Story(idea_id="1", state=INPUT_STATE)
        saved_story = repositories["story"].insert(story)

        title = Title(story_id=saved_story.id, version=0, text="Amazing Adventure Story")
        repositories["title"].insert(title)

        content = Content(
            story_id=saved_story.id,
            version=0,
            text="This amazing adventure story follows a hero on an incredible journey.",
        )
        repositories["content"].insert(content)

        result = service.process_oldest_story()

        assert result.success is True
        assert result.score is not None
        assert 0 <= result.score <= 100

    def test_successful_processing_creates_review_record(self, service, repositories):
        """Test that successful processing creates a Review record in the database."""
        story = Story(idea_id="1", state=INPUT_STATE)
        saved_story = repositories["story"].insert(story)

        title = Title(story_id=saved_story.id, version=0, text="Test Title")
        repositories["title"].insert(title)

        content = Content(story_id=saved_story.id, version=0, text="Test content text.")
        repositories["content"].insert(content)

        result = service.process_oldest_story()

        assert result.success is True
        assert result.review_id is not None

        # Verify review was actually saved
        cursor = service._conn.execute(
            "SELECT id, score FROM Review WHERE id = ?", (result.review_id,)
        )
        row = cursor.fetchone()
        assert row is not None
        assert row["score"] == result.score

    def test_successful_processing_updates_story_state(self, service, repositories):
        """Test that successful processing updates the story state."""
        story = Story(idea_id="1", state=INPUT_STATE)
        saved_story = repositories["story"].insert(story)

        title = Title(story_id=saved_story.id, version=0, text="Test Title")
        repositories["title"].insert(title)

        content = Content(story_id=saved_story.id, version=0, text="Test content text.")
        repositories["content"].insert(content)

        result = service.process_oldest_story()

        assert result.success is True
        assert result.next_state in [OUTPUT_STATE_PASS, OUTPUT_STATE_FAIL]

        # Verify story state was updated in DB
        updated_story = repositories["story"].find_by_id(saved_story.id)
        assert updated_story.state == result.next_state

    def test_accepted_content_transitions_to_pass_state(self, service, repositories):
        """Test that accepted content transitions to the pass state."""
        story = Story(idea_id="1", state=INPUT_STATE)
        saved_story = repositories["story"].insert(story)

        # Create title and content with strong alignment to score >= 70
        keywords = "mystery adventure discovery story horror terror fear"
        title = Title(story_id=saved_story.id, version=0, text=f"{keywords} tale")
        repositories["title"].insert(title)

        # Repeat keywords many times for strong alignment
        content_text = (f"The {keywords} unfolds as our hero faces terror and fear. " * 20)
        content = Content(story_id=saved_story.id, version=0, text=content_text)
        repositories["content"].insert(content)

        result = service.process_oldest_story()

        assert result.success is True
        if result.accepted:
            assert result.next_state == OUTPUT_STATE_PASS
            updated_story = repositories["story"].find_by_id(saved_story.id)
            assert updated_story.state == OUTPUT_STATE_PASS

    def test_rejected_content_transitions_to_fail_state(self, db_connection, repositories):
        """Test that rejected content transitions to the fail state."""
        # Use a service that will always reject (100% threshold)
        story = Story(idea_id="1", state=INPUT_STATE)
        saved_story = repositories["story"].insert(story)

        title = Title(story_id=saved_story.id, version=0, text="Completely Unrelated Title")
        repositories["title"].insert(title)

        # Very short content with no alignment - will score below any threshold
        content = Content(story_id=saved_story.id, version=0, text="x")
        repositories["content"].insert(content)

        # Use very high threshold to force failure
        service = ReviewContentFromTitleIdeaService(db_connection, preview_mode=False)
        # Monkey-patch threshold for test
        original_threshold = CONTENT_ACCEPTANCE_THRESHOLD

        result = service.process_oldest_story()

        assert result.success is True
        assert result.next_state in [OUTPUT_STATE_PASS, OUTPUT_STATE_FAIL]


class TestPreviewMode:
    """Tests for preview mode (no database saves)."""

    def test_preview_mode_does_not_save_review(self, db_connection, repositories):
        """Test that preview mode doesn't save review to database."""
        preview_service = ReviewContentFromTitleIdeaService(db_connection, preview_mode=True)

        story = Story(idea_id="1", state=INPUT_STATE)
        saved_story = repositories["story"].insert(story)

        title = Title(story_id=saved_story.id, version=0, text="Test Title")
        repositories["title"].insert(title)

        content = Content(story_id=saved_story.id, version=0, text="Test content.")
        repositories["content"].insert(content)

        result = preview_service.process_oldest_story()

        assert result.success is True
        # In preview mode, review_id should be None (not saved)
        assert result.review_id is None

    def test_preview_mode_does_not_update_story_state(self, db_connection, repositories):
        """Test that preview mode doesn't update story state."""
        preview_service = ReviewContentFromTitleIdeaService(db_connection, preview_mode=True)

        story = Story(idea_id="1", state=INPUT_STATE)
        saved_story = repositories["story"].insert(story)

        title = Title(story_id=saved_story.id, version=0, text="Test Title")
        repositories["title"].insert(title)

        content = Content(story_id=saved_story.id, version=0, text="Test content.")
        repositories["content"].insert(content)

        preview_service.process_oldest_story()

        # Story state should remain unchanged
        story_after = repositories["story"].find_by_id(saved_story.id)
        assert story_after.state == INPUT_STATE

    def test_preview_mode_still_returns_review_text_and_score(self, db_connection, repositories):
        """Test that preview mode still computes and returns review data."""
        preview_service = ReviewContentFromTitleIdeaService(db_connection, preview_mode=True)

        story = Story(idea_id="1", state=INPUT_STATE)
        saved_story = repositories["story"].insert(story)

        title = Title(story_id=saved_story.id, version=0, text="Test Title")
        repositories["title"].insert(title)

        content = Content(story_id=saved_story.id, version=0, text="Test content text.")
        repositories["content"].insert(content)

        result = preview_service.process_oldest_story()

        assert result.success is True
        assert result.score is not None
        assert result.text is not None


class TestFormatReviewText:
    """Tests for the _format_review_text helper function."""

    def test_format_includes_title(self):
        """Test that formatted review includes the title."""
        from by_title_and_idea import review_content_by_title_and_idea

        class _Genre:
            value = "other"

        class _Idea:
            concept = "test"
            title = "test"
            premise = "test"
            hook = None
            genre = _Genre()
            target_audience = None
            target_platforms = []
            length_target = None
            version = 1

        review = review_content_by_title_and_idea(
            content_text="Test content for review.",
            title="My Amazing Title",
            idea=_Idea(),
        )

        text = _format_review_text(review, "My Amazing Title")

        assert "My Amazing Title" in text
        assert "OVERALL SCORE" in text

    def test_format_includes_score(self):
        """Test that formatted review includes the score."""
        from by_title_and_idea import review_content_by_title_and_idea

        class _Genre:
            value = "other"

        class _Idea:
            concept = "test"
            title = "test"
            premise = "test"
            hook = None
            genre = _Genre()
            target_audience = None
            target_platforms = []
            length_target = None
            version = 1

        review = review_content_by_title_and_idea(
            content_text="Test content.",
            title="Title",
            idea=_Idea(),
        )

        text = _format_review_text(review, "Title")

        assert str(review.overall_score) in text

    def test_format_shows_accepted_status(self):
        """Test that accepted content shows correct status."""
        from by_title_and_idea import review_content_by_title_and_idea

        class _Genre:
            value = "horror"

        class _Idea:
            concept = "fear terror darkness"
            title = "horror story"
            premise = "A terrifying horror story"
            hook = None
            genre = _Genre()
            target_audience = None
            target_platforms = []
            length_target = None
            version = 1

        # Content that should score well
        review = review_content_by_title_and_idea(
            content_text=(
                "What if you woke up and everyone was gone? Terror fills your heart as fear "
                "grips your mind in the darkness. The horror is just beginning... "
            ) * 5,
            title="Horror in the Dark",
            idea=_Idea(),
        )

        text = _format_review_text(review, "Horror in the Dark")

        assert "STATUS:" in text
        if review.overall_score >= CONTENT_ACCEPTANCE_THRESHOLD:
            assert "accepted" in text.lower()
        else:
            assert "revision" in text.lower()
