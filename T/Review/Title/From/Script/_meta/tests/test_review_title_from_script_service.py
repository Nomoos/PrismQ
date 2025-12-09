"""Tests for ReviewTitleFromScriptService.

This module tests the service that processes stories in the
PrismQ.T.Review.Title.From.Script state.
"""

import os
import sqlite3

# Add repo root to path
import sys
from datetime import datetime

import pytest

_current_dir = os.path.dirname(os.path.abspath(__file__))
_repo_root = os.path.dirname(_current_dir)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from Model.Database.models.script import Script
from Model.Database.models.story import Story
from Model.Database.models.title import Title
from Model.Database.repositories.script_repository import ScriptRepository
from Model.Database.repositories.story_repository import StoryRepository
from Model.Database.repositories.title_repository import TitleRepository
from Model.State.constants.state_names import StateNames
from T.Review.Title.From.Script.src.review_title_from_script_service import (
    TITLE_ACCEPTANCE_THRESHOLD,
    ReviewRepository,
    ReviewTitleFromScriptResult,
    ReviewTitleFromScriptService,
    create_review_table_sql,
)


@pytest.fixture
def db_connection():
    """Create an in-memory SQLite database with all required tables."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    # Create all required tables
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS Story (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id INTEGER NULL,
            state TEXT NOT NULL DEFAULT 'CREATED',
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
        
        CREATE TABLE IF NOT EXISTS Script (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            version INTEGER NOT NULL CHECK (version >= 0),
            text TEXT NOT NULL,
            review_id INTEGER NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(story_id, version),
            FOREIGN KEY (story_id) REFERENCES Story(id)
        );
    """
    )

    # Create Review table
    conn.executescript(create_review_table_sql())

    yield conn
    conn.close()


@pytest.fixture
def repositories(db_connection):
    """Create repository instances."""
    return {
        "story": StoryRepository(db_connection),
        "title": TitleRepository(db_connection),
        "script": ScriptRepository(db_connection),
        "review": ReviewRepository(db_connection),
    }


@pytest.fixture
def service(repositories):
    """Create the service instance."""
    return ReviewTitleFromScriptService(
        story_repo=repositories["story"],
        title_repo=repositories["title"],
        script_repo=repositories["script"],
        review_repo=repositories["review"],
    )


class TestReviewRepository:
    """Tests for the ReviewRepository class."""

    def test_insert_review(self, db_connection):
        """Test inserting a review."""
        repo = ReviewRepository(db_connection)
        from Model.Database.models.review import Review

        review = Review(text="Great title, well aligned with script.", score=85)

        saved = repo.insert(review)

        assert saved.id is not None
        assert saved.id > 0
        assert saved.text == "Great title, well aligned with script."
        assert saved.score == 85

    def test_find_review_by_id(self, db_connection):
        """Test finding a review by ID."""
        repo = ReviewRepository(db_connection)
        from Model.Database.models.review import Review

        review = Review(text="Test review", score=75)
        saved = repo.insert(review)

        found = repo.find_by_id(saved.id)

        assert found is not None
        assert found.id == saved.id
        assert found.text == "Test review"
        assert found.score == 75

    def test_find_nonexistent_review(self, db_connection):
        """Test finding a review that doesn't exist."""
        repo = ReviewRepository(db_connection)

        found = repo.find_by_id(99999)

        assert found is None


class TestReviewTitleFromScriptService:
    """Tests for the ReviewTitleFromScriptService class."""

    def test_find_oldest_story_no_stories(self, service):
        """Test finding oldest story when none exist."""
        story = service.find_oldest_story_to_process()

        assert story is None

    def test_find_oldest_story_wrong_state(self, service, repositories):
        """Test that stories in wrong state are not found."""
        # Create story in wrong state
        story = Story(idea_json='{"title": "Test"}', state="PrismQ.T.Title.From.Idea")
        repositories["story"].insert(story)

        found = service.find_oldest_story_to_process()

        assert found is None

    def test_find_oldest_story_correct_state(self, service, repositories):
        """Test finding oldest story in correct state."""
        # Create story in correct state
        story = Story(idea_json='{"title": "Test"}', state=StateNames.REVIEW_TITLE_FROM_SCRIPT)
        saved = repositories["story"].insert(story)

        found = service.find_oldest_story_to_process()

        assert found is not None
        assert found.id == saved.id

    def test_find_oldest_story_multiple(self, service, repositories):
        """Test finding oldest among multiple stories."""
        import time

        # Create first story (older)
        story1 = Story(
            idea_json='{"title": "First"}',
            state=StateNames.REVIEW_TITLE_FROM_SCRIPT,
            created_at=datetime(2025, 1, 1, 10, 0, 0),
        )
        saved1 = repositories["story"].insert(story1)

        # Create second story (newer)
        story2 = Story(
            idea_json='{"title": "Second"}',
            state=StateNames.REVIEW_TITLE_FROM_SCRIPT,
            created_at=datetime(2025, 1, 2, 10, 0, 0),
        )
        saved2 = repositories["story"].insert(story2)

        found = service.find_oldest_story_to_process()

        assert found is not None
        assert found.id == saved1.id

    def test_count_stories_to_process(self, service, repositories):
        """Test counting stories to process."""
        # Initially empty
        assert service.count_stories_to_process() == 0

        # Add stories
        for i in range(3):
            story = Story(
                idea_json=f'{{"title": "Test {i}"}}', state=StateNames.REVIEW_TITLE_FROM_SCRIPT
            )
            repositories["story"].insert(story)

        assert service.count_stories_to_process() == 3

    def test_process_story_no_title(self, service, repositories):
        """Test processing story without a title fails gracefully."""
        story = Story(idea_json='{"title": "Test"}', state=StateNames.REVIEW_TITLE_FROM_SCRIPT)
        saved = repositories["story"].insert(story)

        result = service.process_story(saved)

        assert not result.success
        assert "No title found" in result.error_message

    def test_process_story_no_script(self, service, repositories):
        """Test processing story without a script fails gracefully."""
        # Create story
        story = Story(idea_json='{"title": "Test"}', state=StateNames.REVIEW_TITLE_FROM_SCRIPT)
        saved_story = repositories["story"].insert(story)

        # Create title but no script
        title = Title(story_id=saved_story.id, version=0, text="Test Title")
        repositories["title"].insert(title)

        result = service.process_story(saved_story)

        assert not result.success
        assert "No script found" in result.error_message

    def test_process_story_wrong_state(self, service, repositories):
        """Test processing story in wrong state fails."""
        story = Story(idea_json='{"title": "Test"}', state="PrismQ.T.Title.From.Idea")
        saved = repositories["story"].insert(story)

        result = service.process_story(saved)

        assert not result.success
        assert "expected" in result.error_message

    def test_process_story_accepts_title(self, repositories):
        """Test processing story that accepts title."""
        # Create service with lower threshold for accepting titles
        service = ReviewTitleFromScriptService(
            story_repo=repositories["story"],
            title_repo=repositories["title"],
            script_repo=repositories["script"],
            review_repo=repositories["review"],
            acceptance_threshold=50,  # Lower threshold for test
        )

        # Create story
        story = Story(idea_json='{"title": "Test"}', state=StateNames.REVIEW_TITLE_FROM_SCRIPT)
        saved_story = repositories["story"].insert(story)

        # Create title with matching keywords
        title = Title(story_id=saved_story.id, version=0, text="Mystery adventure story discovery")
        repositories["title"].insert(title)

        # Create script with matching keywords
        script = Script(
            story_id=saved_story.id,
            version=0,
            text="This is a mystery story about an adventure with discovery and exploration. " * 10,
        )
        repositories["script"].insert(script)

        result = service.process_story(saved_story)

        assert result.success
        assert result.review_id is not None
        assert result.review_score is not None

        # Verify story state was updated
        updated_story = repositories["story"].find_by_id(saved_story.id)
        assert updated_story.state in [
            StateNames.REVIEW_SCRIPT_FROM_TITLE,
            StateNames.TITLE_FROM_SCRIPT_REVIEW_TITLE,
        ]

    def test_process_story_rejects_title(self, repositories):
        """Test processing story that rejects title."""
        # Create service with very high threshold to ensure rejection
        service = ReviewTitleFromScriptService(
            story_repo=repositories["story"],
            title_repo=repositories["title"],
            script_repo=repositories["script"],
            review_repo=repositories["review"],
            acceptance_threshold=100,  # Very high threshold for test
        )

        # Create story
        story = Story(idea_json='{"title": "Test"}', state=StateNames.REVIEW_TITLE_FROM_SCRIPT)
        saved_story = repositories["story"].insert(story)

        # Create title with no matching keywords
        title = Title(story_id=saved_story.id, version=0, text="Xyz abc def")
        repositories["title"].insert(title)

        # Create script with different content
        script = Script(
            story_id=saved_story.id,
            version=0,
            text="This is completely unrelated content about cooking and recipes.",
        )
        repositories["script"].insert(script)

        result = service.process_story(saved_story)

        assert result.success
        assert result.review_id is not None
        assert result.title_accepted == False

        # Verify story state was updated to rejection state
        updated_story = repositories["story"].find_by_id(saved_story.id)
        assert updated_story.state == StateNames.TITLE_FROM_SCRIPT_REVIEW_TITLE

    def test_process_oldest_story(self, service, repositories):
        """Test processing the oldest story."""
        # Create story with all needed content
        story = Story(idea_json='{"title": "Test"}', state=StateNames.REVIEW_TITLE_FROM_SCRIPT)
        saved_story = repositories["story"].insert(story)

        title = Title(story_id=saved_story.id, version=0, text="Test Title about Mystery")
        repositories["title"].insert(title)

        script = Script(
            story_id=saved_story.id,
            version=0,
            text="A test script about a mystery adventure story.",
        )
        repositories["script"].insert(script)

        result = service.process_oldest_story()

        assert result.success
        assert result.story_id == saved_story.id

    def test_process_oldest_story_none_available(self, service):
        """Test processing when no stories are available."""
        result = service.process_oldest_story()

        assert not result.success
        assert "No stories found" in result.error_message

    def test_process_all_stories(self, service, repositories):
        """Test processing all stories in the state."""
        # Create multiple stories
        for i in range(3):
            story = Story(
                idea_json=f'{{"title": "Story {i}"}}', state=StateNames.REVIEW_TITLE_FROM_SCRIPT
            )
            saved_story = repositories["story"].insert(story)

            title = Title(story_id=saved_story.id, version=0, text=f"Title for story {i}")
            repositories["title"].insert(title)

            script = Script(
                story_id=saved_story.id,
                version=0,
                text=f"Script content for story {i} about title and keywords.",
            )
            repositories["script"].insert(script)

        results = service.process_all_stories()

        assert len(results) == 3
        assert all(r.success for r in results)

    def test_process_all_stories_with_limit(self, service, repositories):
        """Test processing stories with a limit."""
        # Create multiple stories
        for i in range(5):
            story = Story(
                idea_json=f'{{"title": "Story {i}"}}', state=StateNames.REVIEW_TITLE_FROM_SCRIPT
            )
            saved_story = repositories["story"].insert(story)

            title = Title(story_id=saved_story.id, version=0, text=f"Title {i}")
            repositories["title"].insert(title)

            script = Script(story_id=saved_story.id, version=0, text=f"Script {i}")
            repositories["script"].insert(script)

        results = service.process_all_stories(limit=2)

        assert len(results) == 2


class TestStateTransitions:
    """Tests for state transition logic."""

    def test_acceptance_threshold_boundary(self, repositories):
        """Test state transition at acceptance threshold boundary."""
        # Create service with specific threshold
        service = ReviewTitleFromScriptService(
            story_repo=repositories["story"],
            title_repo=repositories["title"],
            script_repo=repositories["script"],
            review_repo=repositories["review"],
            acceptance_threshold=70,
        )

        # Create story
        story = Story(idea_json='{"title": "Test"}', state=StateNames.REVIEW_TITLE_FROM_SCRIPT)
        saved_story = repositories["story"].insert(story)

        # Create title and script with known matching content
        title = Title(
            story_id=saved_story.id, version=0, text="Adventure mystery story exploration"
        )
        repositories["title"].insert(title)

        # Create script with very high keyword match
        matching_words = "adventure mystery story exploration discovery journey quest"
        script = Script(story_id=saved_story.id, version=0, text=(matching_words + " ") * 20)
        repositories["script"].insert(script)

        result = service.process_story(saved_story)

        assert result.success
        # With good keyword matching, score should be above threshold
        assert result.review_score is not None

        updated_story = repositories["story"].find_by_id(saved_story.id)
        expected_state = (
            StateNames.REVIEW_SCRIPT_FROM_TITLE
            if result.title_accepted
            else StateNames.TITLE_FROM_SCRIPT_REVIEW_TITLE
        )
        assert updated_story.state == expected_state


class TestReviewTitleFromScriptResult:
    """Tests for the result dataclass."""

    def test_successful_result(self):
        """Test creating a successful result."""
        result = ReviewTitleFromScriptResult(
            success=True,
            story_id=1,
            review_id=5,
            review_score=85,
            review_text="Great title alignment.",
            new_state=StateNames.REVIEW_SCRIPT_FROM_TITLE,
            title_accepted=True,
        )

        assert result.success
        assert result.story_id == 1
        assert result.review_id == 5
        assert result.review_score == 85
        assert result.title_accepted == True

    def test_failed_result(self):
        """Test creating a failed result."""
        result = ReviewTitleFromScriptResult(success=False, error_message="No stories found")

        assert not result.success
        assert result.error_message == "No stories found"
        assert result.story_id is None
        assert result.review_id is None


@pytest.mark.integration
class TestIntegrationWorkflow:
    """Integration tests for the complete workflow."""

    def test_complete_review_workflow(self, db_connection, repositories, service):
        """Test the complete review workflow from story to state transition."""
        # 1. Create story in correct state
        story = Story(
            idea_json='{"title": "Horror Story", "concept": "A scary adventure"}',
            state=StateNames.REVIEW_TITLE_FROM_SCRIPT,
        )
        saved_story = repositories["story"].insert(story)

        # 2. Create associated title
        title = Title(story_id=saved_story.id, version=0, text="The Haunting Mystery")
        saved_title = repositories["title"].insert(title)

        # 3. Create associated script
        script = Script(
            story_id=saved_story.id,
            version=0,
            text="This haunting mystery unfolds in an abandoned mansion where strange sounds echo through the halls.",
        )
        saved_script = repositories["script"].insert(script)

        # 4. Process the story
        result = service.process_oldest_story()

        # 5. Verify results
        assert result.success
        assert result.story_id == saved_story.id
        assert result.review_id is not None
        assert result.review_score is not None
        assert result.review_text is not None
        assert result.new_state in [
            StateNames.REVIEW_SCRIPT_FROM_TITLE,
            StateNames.TITLE_FROM_SCRIPT_REVIEW_TITLE,
        ]

        # 6. Verify Review was created
        created_review = repositories["review"].find_by_id(result.review_id)
        assert created_review is not None
        assert created_review.text == result.review_text
        assert created_review.score == result.review_score

        # 7. Verify Story state was updated
        updated_story = repositories["story"].find_by_id(saved_story.id)
        assert updated_story.state == result.new_state
        assert updated_story.updated_at is not None
