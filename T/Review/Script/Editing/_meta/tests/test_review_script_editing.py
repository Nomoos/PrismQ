"""Tests for PrismQ.T.Review.Content.Editing service module.

These tests verify the review content editing workflow stage:
1. Selecting oldest Story with correct state
2. Getting the Content associated with the Story
3. Creating Review model with text and score
4. Linking the Review to the Content via review_id FK
5. State transitions based on review acceptance
"""

import importlib.util
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import pytest

# Add project root to path for imports
_test_dir = Path(__file__).parent
_project_root = _test_dir.parent

# Ensure project root is in path
sys.path.insert(0, str(_project_root))

from Model.Database.models.review import Review
from Model.Database.models.content import Content
from Model.Database.models.story import Story
from Model.Database.repositories.review_repository import ReviewRepository
from Model.Database.repositories.content_repository import ContentRepository
from Model.Database.repositories.story_repository import StoryRepository
from Model.State.constants.state_names import StateNames

# Import the module to test using direct file loading to avoid circular import
_module_path = (
    _project_root
    / "T"
    / "Review"
    / "Content"
    / "Editing"
    / "src"
    / "review_content_editing_service.py"
)
_spec = importlib.util.spec_from_file_location("review_content_editing_service", _module_path)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

ReviewResult = _module.ReviewResult
process_review_content_editing = _module.process_review_content_editing
get_oldest_story_for_review = _module.get_oldest_story_for_review
determine_next_state = _module.determine_next_state
create_review = _module.create_review
evaluate_content = _module.evaluate_content
ACCEPTANCE_THRESHOLD = _module.ACCEPTANCE_THRESHOLD
STATE_REVIEW_SCRIPT_EDITING = _module.STATE_REVIEW_SCRIPT_EDITING
STATE_SCRIPT_REFINEMENT = _module.STATE_SCRIPT_REFINEMENT
STATE_REVIEW_TITLE_READABILITY = _module.STATE_REVIEW_TITLE_READABILITY


def get_content_schema():
    """Get SQL schema for Content table."""
    return """
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
    """


def get_review_schema():
    """Get SQL schema for Review table."""
    return """
    CREATE TABLE IF NOT EXISTS Review (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """


@pytest.fixture
def db_connection():
    """Create an in-memory SQLite database with Story, Content, and Review tables."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    # Create Story table
    conn.executecontent(Story.get_sql_schema())

    # Create Review table
    conn.executecontent(get_review_schema())

    # Create Content table
    conn.executecontent(get_content_schema())

    yield conn
    conn.close()


@pytest.fixture
def story_repository(db_connection):
    """Create a StoryRepository instance."""
    return StoryRepository(db_connection)


@pytest.fixture
def content_repository(db_connection):
    """Create a ContentRepository instance."""
    return ContentRepository(db_connection)


@pytest.fixture
def review_repository(db_connection):
    """Create a ReviewRepository instance."""
    return ReviewRepository(db_connection)


class TestGetOldestStoryForReview:
    """Tests for get_oldest_story_for_review function."""

    def test_returns_none_when_no_stories(self, story_repository, db_connection):
        """Should return None when no stories exist."""
        result = get_oldest_story_for_review(story_repository, db_connection)
        assert result is None

    def test_returns_none_when_no_stories_in_correct_state(self, story_repository, db_connection):
        """Should return None when no stories have the correct state."""
        # Create a story with different state
        story = Story(idea_json='{"title": "Test"}', state=StateNames.IDEA_CREATION)
        story_repository.insert(story)

        result = get_oldest_story_for_review(story_repository, db_connection)
        assert result is None

    def test_returns_story_with_lowest_content_version(
        self, story_repository, content_repository, db_connection
    ):
        """Should return story with lowest content version (not oldest created)."""
        # Create first story (will have version 2 contents)
        story1 = Story(
            idea_json='{"title": "Story 1 - high version"}', state=STATE_REVIEW_SCRIPT_EDITING
        )
        story1 = story_repository.insert(story1)

        # Create contents for story1 - versions 0, 1, 2 (max = 2)
        for v in range(3):
            content = Content(story_id=story1.id, version=v, text=f"Content v{v} for story1")
            content_repository.insert(content)

        # Create second story (will have version 0 content only)
        story2 = Story(
            idea_json='{"title": "Story 2 - low version"}', state=STATE_REVIEW_SCRIPT_EDITING
        )
        story2 = story_repository.insert(story2)

        # Create only version 0 content for story2 (max = 0)
        content = Content(story_id=story2.id, version=0, text="Content v0 for story2")
        content_repository.insert(content)

        # Should return story2 because it has lower max content version
        result = get_oldest_story_for_review(story_repository, db_connection)

        assert result is not None
        assert result.id == story2.id
        assert result.idea_json == '{"title": "Story 2 - low version"}'


class TestDetermineNextState:
    """Tests for determine_next_state function."""

    def test_accepted_goes_to_title_readability(self):
        """Accepted review should transition to Title Readability."""
        result = determine_next_state(accepted=True)
        assert result == STATE_REVIEW_TITLE_READABILITY

    def test_not_accepted_goes_to_content_refinement(self):
        """Non-accepted review should go to Content Refinement."""
        result = determine_next_state(accepted=False)
        assert result == STATE_SCRIPT_REFINEMENT


class TestCreateReview:
    """Tests for create_review function."""

    def test_creates_review_with_correct_fields(self):
        """Should create a Review with correct text and score."""
        review = create_review(score=75, text="Test review content")

        assert review.text == "Test review content"
        assert review.score == 75
        assert isinstance(review.created_at, datetime)

    def test_score_validation(self):
        """Score must be within 0-100 range."""
        # Valid scores
        review = create_review(score=0, text="Min score")
        assert review.score == 0

        review = create_review(score=100, text="Max score")
        assert review.score == 100

        # Invalid scores should raise
        with pytest.raises(ValueError):
            create_review(score=-1, text="Invalid")

        with pytest.raises(ValueError):
            create_review(score=101, text="Invalid")

    def test_score_type_validation(self):
        """Score must be an integer."""
        with pytest.raises(TypeError):
            create_review(score="75", text="Invalid type")

        with pytest.raises(TypeError):
            create_review(score=75.5, text="Invalid type")


class TestEvaluateContent:
    """Tests for evaluate_content function."""

    def test_returns_score_and_text(self):
        """Should return tuple of score and review text."""
        score, text = evaluate_content(
            content_text="This is a test content with good content about the topic."
        )

        assert isinstance(score, int)
        assert 0 <= score <= 100
        assert isinstance(text, str)
        assert len(text) > 0

    def test_editing_review_prefix(self):
        """Review should have editing review prefix."""
        score, text = evaluate_content(content_text="Test content content.")

        assert "Editing review" in text

    def test_short_content_penalized(self):
        """Short contents should have lower scores."""
        short_score, _ = evaluate_content(content_text="Too short.")

        # Use varied content to avoid repeated word penalty
        normal_content = "The quick brown fox jumps over the lazy dog. " * 15
        normal_score, _ = evaluate_content(content_text=normal_content)

        assert short_score < normal_score

    def test_wordy_phrases_detected(self):
        """Contents with wordy phrases should be penalized."""
        clean_content = "He walked to the store. She bought groceries. They went home."
        wordy_content = "In order to go to the store, he walked. Due to the fact that she needed food, she bought groceries."

        clean_score, _ = evaluate_content(content_text=clean_content)
        wordy_score, wordy_text = evaluate_content(content_text=wordy_content)

        assert wordy_score < clean_score
        assert "wordy" in wordy_text.lower()

    def test_redundant_phrases_detected(self):
        """Contents with redundant phrases should be penalized."""
        redundant_content = "It was a very unique experience. The exact same thing happened twice."

        _, review_text = evaluate_content(content_text=redundant_content)

        assert "redundant" in review_text.lower()


class TestProcessReviewContentEditing:
    """Tests for process_review_content_editing function."""

    def test_returns_none_when_no_stories(self, db_connection):
        """Should return None when no stories to process."""
        result = process_review_content_editing(db_connection)
        assert result is None

    def test_processes_story_and_returns_result(self, db_connection, story_repository):
        """Should process story and return ReviewResult."""
        # Create a story in the correct state
        story = Story(idea_json='{"title": "Test Story"}', state=STATE_REVIEW_SCRIPT_EDITING)
        story_repository.insert(story)

        result = process_review_content_editing(
            db_connection, content_text="This is a test content with good content about the topic."
        )

        assert result is not None
        assert isinstance(result, ReviewResult)
        assert result.story is not None
        assert result.review is not None
        assert isinstance(result.review, Review)

    def test_updates_story_state(self, db_connection, story_repository):
        """Should update story state after processing."""
        # Create a story
        story = Story(idea_json='{"title": "Test Story"}', state=STATE_REVIEW_SCRIPT_EDITING)
        story = story_repository.insert(story)

        result = process_review_content_editing(db_connection)

        # Verify state was updated
        updated_story = story_repository.find_by_id(story.id)
        assert updated_story.state == result.new_state

    def test_accepted_transitions_to_title_readability(self, db_connection, story_repository):
        """Accepted review should transition to title readability state."""
        story = Story(idea_json='{"title": "Test"}', state=STATE_REVIEW_SCRIPT_EDITING)
        story_repository.insert(story)

        # Use a clean content that will score above threshold
        result = process_review_content_editing(
            db_connection, content_text=" ".join(["good clean content about the main topic"] * 50)
        )

        if result.accepted:
            assert result.new_state == STATE_REVIEW_TITLE_READABILITY
        else:
            assert result.new_state == STATE_SCRIPT_REFINEMENT

    def test_not_accepted_transitions_to_content_refinement(self, db_connection, story_repository):
        """Non-accepted review should transition to content refinement."""
        story = Story(idea_json='{"title": "Test"}', state=STATE_REVIEW_SCRIPT_EDITING)
        story_repository.insert(story)

        # Use a content with many issues to ensure it fails
        wordy_content = "In order to do this. Due to the fact that it is. Very unique. Past history."

        result = process_review_content_editing(db_connection, content_text=wordy_content)

        # Even if it passes, check the correct state mapping
        if not result.accepted:
            assert result.new_state == STATE_SCRIPT_REFINEMENT


class TestReviewResult:
    """Tests for ReviewResult dataclass."""

    def test_review_result_fields(self, db_connection, story_repository):
        """ReviewResult should have all expected fields including content."""
        story = Story(idea_json='{"title": "Test"}', state=STATE_REVIEW_SCRIPT_EDITING)
        story_repository.insert(story)

        result = process_review_content_editing(db_connection)

        assert hasattr(result, "story")
        assert hasattr(result, "content")
        assert hasattr(result, "review")
        assert hasattr(result, "new_state")
        assert hasattr(result, "accepted")

        assert isinstance(result.story, Story)
        assert isinstance(result.content, Content)
        assert isinstance(result.review, Review)
        assert isinstance(result.new_state, str)
        assert isinstance(result.accepted, bool)


class TestConstants:
    """Tests for module constants."""

    def test_acceptance_threshold_in_valid_range(self):
        """Acceptance threshold should be in valid score range."""
        assert 0 <= ACCEPTANCE_THRESHOLD <= 100

    def test_state_constants_are_valid(self):
        """State constants should have expected values."""
        assert STATE_REVIEW_SCRIPT_EDITING == StateNames.REVIEW_SCRIPT_EDITING
        assert STATE_REVIEW_TITLE_READABILITY == StateNames.REVIEW_TITLE_READABILITY
        assert STATE_SCRIPT_REFINEMENT == "PrismQ.T.Content.From.Title.Review.Content"


@pytest.mark.integration
class TestReviewWorkflowIntegration:
    """Integration tests for the review workflow."""

    def test_complete_accepted_review_flow(self, db_connection, story_repository):
        """Test complete accepted review flow."""
        # Setup: Create story in correct state
        story = Story(
            idea_json='{"title": "Test Story", "concept": "A great concept"}',
            state=STATE_REVIEW_SCRIPT_EDITING,
        )
        story = story_repository.insert(story)

        # Process: Execute review with clean content
        result = process_review_content_editing(
            db_connection, content_text="Clear concise content. " * 50
        )

        # Verify: Check result
        assert result is not None

        # Verify: Story state updated in database
        updated = story_repository.find_by_id(story.id)
        if result.accepted:
            assert updated.state == STATE_REVIEW_TITLE_READABILITY
        else:
            assert updated.state == STATE_SCRIPT_REFINEMENT

    def test_multiple_stories_processed_in_order(self, db_connection, story_repository):
        """Test that multiple stories are processed oldest first."""
        # Create multiple stories
        story1 = Story(idea_json='{"title": "Story 1"}', state=STATE_REVIEW_SCRIPT_EDITING)
        story1 = story_repository.insert(story1)

        story2 = Story(idea_json='{"title": "Story 2"}', state=STATE_REVIEW_SCRIPT_EDITING)
        story2 = story_repository.insert(story2)

        # Process first story
        result1 = process_review_content_editing(db_connection)
        assert result1.story.id == story1.id

        # Process second story
        result2 = process_review_content_editing(db_connection)
        assert result2.story.id == story2.id

        # No more stories to process
        result3 = process_review_content_editing(db_connection)
        assert result3 is None


@pytest.mark.integration
class TestContentReviewLinkage:
    """Tests for Content-Review relationship via review_id FK."""

    def test_review_linked_to_content(
        self, db_connection, story_repository, content_repository, review_repository
    ):
        """Test that Review is linked to Content via review_id FK."""
        # Create a story in the correct state
        story = Story(idea_json='{"title": "Test Story"}', state=STATE_REVIEW_SCRIPT_EDITING)
        story = story_repository.insert(story)

        # Create a content for the story
        content = Content(
            story_id=story.id, version=0, text="This is the content content for review testing."
        )
        content = content_repository.insert(content)

        # Update story to reference the content
        story.content_id = content.id
        story_repository.update(story)

        # Process the review
        result = process_review_content_editing(db_connection)

        # Verify: Review was created and persisted
        assert result is not None
        assert result.review is not None
        assert result.review.id is not None

        # Verify: Review is linked to Content
        updated_content = content_repository.find_by_id(content.id)
        assert updated_content.review_id == result.review.id

        # Verify: Content in result has the review_id set
        assert result.content.review_id == result.review.id

    def test_review_persisted_in_database(
        self, db_connection, story_repository, content_repository, review_repository
    ):
        """Test that Review is persisted and can be retrieved."""
        # Create a story in the correct state
        story = Story(idea_json='{"title": "Test Story"}', state=STATE_REVIEW_SCRIPT_EDITING)
        story = story_repository.insert(story)

        # Create a content for the story
        content = Content(story_id=story.id, version=0, text="This is the content content.")
        content = content_repository.insert(content)

        # Update story to reference the content
        story.content_id = content.id
        story_repository.update(story)

        # Process the review
        result = process_review_content_editing(db_connection)

        # Verify: Review can be retrieved from database
        retrieved_review = review_repository.find_by_id(result.review.id)
        assert retrieved_review is not None
        assert retrieved_review.score == result.review.score
        assert retrieved_review.text == result.review.text

    def test_content_text_used_for_evaluation(
        self, db_connection, story_repository, content_repository
    ):
        """Test that Content text is used for evaluation when available."""
        # Create a story in the correct state
        story = Story(idea_json='{"title": "Test Story"}', state=STATE_REVIEW_SCRIPT_EDITING)
        story = story_repository.insert(story)

        # Create a content with wordy text that will get lower score
        content = Content(
            story_id=story.id,
            version=0,
            text="In order to do this. Due to the fact that it is. Very unique. Past history.",
        )
        content = content_repository.insert(content)

        # Update story to reference the content
        story.content_id = content.id
        story_repository.update(story)

        # Process the review (should use content text from database)
        result = process_review_content_editing(db_connection)

        # Verify: Review mentions editing issues
        assert result is not None
        assert "wordy" in result.review.text.lower() or "redundant" in result.review.text.lower()
