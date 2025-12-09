"""Tests for PrismQ.T.Review.Content.Tone module.

These tests verify the review content tone workflow stage:
1. Selecting Story with lowest current content version in correct state
2. Getting the Content for the Story
3. Creating Review model with text and score
4. Linking Review to Content via Content.review_id FK
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
sys.path.insert(0, str(_project_root))

from Model.Database.models.review import Review
from Model.Database.models.content import Content
from Model.Database.models.story import Story
from Model.Database.repositories.content_repository import ContentRepository
from Model.Database.repositories.story_repository import StoryRepository
from Model.State.constants.state_names import StateNames

# Import the module to test using direct file loading to avoid circular import
_module_path = _project_root / "T" / "Review" / "Content" / "Tone" / "src" / "review_content_tone.py"
_spec = importlib.util.spec_from_file_location("review_content_tone", _module_path)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

ReviewResult = _module.ReviewResult
process_review_content_tone = _module.process_review_content_tone
get_story_with_lowest_content_version = _module.get_story_with_lowest_content_version
get_content_for_story = _module.get_content_for_story
save_review = _module.save_review
update_content_review_id = _module.update_content_review_id
determine_next_state = _module.determine_next_state
create_review = _module.create_review
evaluate_tone = _module.evaluate_tone
ACCEPTANCE_THRESHOLD = _module.ACCEPTANCE_THRESHOLD
STATE_REVIEW_SCRIPT_TONE = _module.STATE_REVIEW_SCRIPT_TONE
STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT = _module.STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT
STATE_REVIEW_SCRIPT_EDITING = _module.STATE_REVIEW_SCRIPT_EDITING


# SQL schema for Content table
SCRIPT_SQL_SCHEMA = """
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

# SQL schema for Review table
REVIEW_SQL_SCHEMA = """
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

    # Create all tables
    conn.executecontent(Story.get_sql_schema())
    conn.executecontent(SCRIPT_SQL_SCHEMA)
    conn.executecontent(REVIEW_SQL_SCHEMA)

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


class TestGetStoryWithLowestContentVersion:
    """Tests for get_story_with_lowest_content_version function."""

    def test_returns_none_when_no_stories(self, db_connection, story_repository):
        """Should return None when no stories exist."""
        result = get_story_with_lowest_content_version(db_connection, story_repository)
        assert result is None

    def test_returns_none_when_no_stories_in_correct_state(
        self, db_connection, story_repository, content_repository
    ):
        """Should return None when no stories have the correct state."""
        # Create a story with different state
        story = Story(idea_json='{"title": "Test"}', state=StateNames.IDEA_CREATION)
        story = story_repository.insert(story)

        # Create a content for the story
        content = Content(story_id=story.id, version=0, text="Test content")
        content_repository.insert(content)

        result = get_story_with_lowest_content_version(db_connection, story_repository)
        assert result is None

    def test_returns_story_with_lowest_content_version(
        self, db_connection, story_repository, content_repository
    ):
        """Should return the story whose content has the lowest current version."""
        # Create story A with content versions 0, 1, 2 (max=2)
        story_a = Story(idea_json='{"title": "Story A"}', state=STATE_REVIEW_SCRIPT_TONE)
        story_a = story_repository.insert(story_a)
        for v in range(3):  # versions 0, 1, 2
            content = Content(story_id=story_a.id, version=v, text=f"Story A v{v}")
            content_repository.insert(content)

        # Create story B with content versions 0, 1 (max=1)
        story_b = Story(idea_json='{"title": "Story B"}', state=STATE_REVIEW_SCRIPT_TONE)
        story_b = story_repository.insert(story_b)
        for v in range(2):  # versions 0, 1
            content = Content(story_id=story_b.id, version=v, text=f"Story B v{v}")
            content_repository.insert(content)

        # Should return story B (lower max version)
        result = get_story_with_lowest_content_version(db_connection, story_repository)

        assert result is not None
        assert result.id == story_b.id
        assert result.idea_json == '{"title": "Story B"}'

    def test_returns_none_when_story_has_no_contents(self, db_connection, story_repository):
        """Should return None when stories in correct state have no contents."""
        # Create a story in correct state but with no contents
        story = Story(idea_json='{"title": "No Contents"}', state=STATE_REVIEW_SCRIPT_TONE)
        story_repository.insert(story)

        result = get_story_with_lowest_content_version(db_connection, story_repository)
        assert result is None


class TestDetermineNextState:
    """Tests for determine_next_state function."""

    def test_not_accepted_goes_to_content_rewrite(self):
        """Not accepted should transition to content rewrite state."""
        result = determine_next_state(accepted=False)
        assert result == STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT

    def test_accepted_goes_to_editing(self):
        """Accepted should proceed to editing review."""
        result = determine_next_state(accepted=True)
        assert result == STATE_REVIEW_SCRIPT_EDITING


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


class TestEvaluateTone:
    """Tests for evaluate_tone function."""

    def test_returns_score_and_text(self):
        """Should return tuple of score and review text."""
        score, text = evaluate_tone(
            content_text="This is a test content about horror and fear.",
        )

        assert isinstance(score, int)
        assert 0 <= score <= 100
        assert isinstance(text, str)
        assert len(text) > 0

    def test_tone_review_prefix(self):
        """Review should have appropriate prefix."""
        score, text = evaluate_tone(
            content_text="Test content content about mysterious dark events.",
        )

        assert "Tone review:" in text

    def test_short_content_penalized(self):
        """Short contents should have lower scores."""
        short_score, _ = evaluate_tone(
            content_text="Too short.",
        )

        normal_score, _ = evaluate_tone(
            content_text=" ".join(["word"] * 150),
        )

        assert short_score < normal_score

    def test_consistent_positive_tone(self):
        """Contents with consistent positive tone should score well."""
        score, text = evaluate_tone(
            content_text="The happy character felt joy and excitement. Everything was wonderful and amazing. They loved the beautiful view.",
        )

        assert "positive tone" in text.lower() or "consistent" in text.lower()
        assert score >= 70

    def test_consistent_negative_tone(self):
        """Contents with consistent dark/negative tone should score well."""
        score, text = evaluate_tone(
            content_text="The dark night was filled with fear and horror. The terrible events were scary and ugly. "
            * 5,
        )

        assert "dark" in text.lower() or "dramatic" in text.lower() or "consistent" in text.lower()
        assert score >= 70

    def test_target_tone_alignment(self):
        """Contents should be evaluated against target tone if specified."""
        # Test dark tone alignment
        aligned_score, _ = evaluate_tone(
            content_text="The dark night was filled with fear and horror. Scary shadows lurked everywhere.",
            target_tone="dark suspense",
        )

        unaligned_score, _ = evaluate_tone(
            content_text="The happy sunny day was wonderful. Everyone was joyful and excited.",
            target_tone="dark suspense",
        )

        assert aligned_score > unaligned_score


class TestProcessReviewContentTone:
    """Tests for process_review_content_tone function."""

    def test_returns_none_when_no_stories(self, db_connection):
        """Should return None when no stories to process."""
        result = process_review_content_tone(db_connection)
        assert result is None

    def test_processes_story_and_returns_result(
        self, db_connection, story_repository, content_repository
    ):
        """Should process story and return ReviewResult."""
        # Create a story in the correct state
        story = Story(idea_json='{"title": "Test Story"}', state=STATE_REVIEW_SCRIPT_TONE)
        story = story_repository.insert(story)

        # Create a content for the story (required by new selection logic)
        content = Content(
            story_id=story.id,
            version=0,
            text="This is a test content with consistent dark tone about fear and horror.",
        )
        content_repository.insert(content)

        result = process_review_content_tone(db_connection)

        assert result is not None
        assert isinstance(result, ReviewResult)
        assert result.story is not None
        assert result.review is not None
        assert result.content is not None
        assert isinstance(result.review, Review)
        assert isinstance(result.content, Content)

    def test_review_saved_to_database(self, db_connection, story_repository, content_repository):
        """Review should be saved to database and have an ID."""
        story = Story(idea_json='{"title": "Test Story"}', state=STATE_REVIEW_SCRIPT_TONE)
        story = story_repository.insert(story)

        # Create a content for the story
        content = Content(
            story_id=story.id,
            version=0,
            text="This is a test content with consistent dark tone about fear and horror.",
        )
        content_repository.insert(content)

        result = process_review_content_tone(db_connection)

        # Verify review has an ID (was saved to database)
        assert result.review.id is not None

        # Verify review can be retrieved from database
        cursor = db_connection.execute("SELECT * FROM Review WHERE id = ?", (result.review.id,))
        row = cursor.fetchone()
        assert row is not None
        assert row["score"] == result.review.score

    def test_content_references_review(self, db_connection, story_repository, content_repository):
        """Content should have review_id set to link to the Review."""
        # Create story with existing content
        story = Story(idea_json='{"title": "Test Story"}', state=STATE_REVIEW_SCRIPT_TONE)
        story = story_repository.insert(story)

        # Create initial content for the story
        initial_content = Content(
            story_id=story.id, version=0, text="Initial content content about dark horror and fear."
        )
        initial_content = content_repository.insert(initial_content)

        # Update story to reference the content
        story.content_id = initial_content.id
        story_repository.update(story)

        # Process the review
        result = process_review_content_tone(db_connection)

        # Verify content has review_id set (same content, not new version)
        assert result.content is not None
        assert result.content.id == initial_content.id  # Same content, not a new version
        assert result.content.review_id is not None
        assert result.content.review_id == result.review.id

        # Verify in database the content's review_id was updated
        updated_content = content_repository.find_by_id(initial_content.id)
        assert updated_content.review_id == result.review.id

    def test_updates_story_state(self, db_connection, story_repository, content_repository):
        """Should update story state after processing."""
        # Create a story
        story = Story(idea_json='{"title": "Test Story"}', state=STATE_REVIEW_SCRIPT_TONE)
        story = story_repository.insert(story)

        # Create a content for the story
        content = Content(story_id=story.id, version=0, text="Test content content about dark horror.")
        content_repository.insert(content)

        result = process_review_content_tone(db_connection)

        # Verify state was updated
        updated_story = story_repository.find_by_id(story.id)
        assert updated_story.state == result.new_state

    def test_accepted_transitions_to_editing(
        self, db_connection, story_repository, content_repository
    ):
        """Accepted review should transition to editing review state."""
        story = Story(idea_json='{"title": "Test"}', state=STATE_REVIEW_SCRIPT_TONE)
        story = story_repository.insert(story)

        # Create a content with good content
        content = Content(
            story_id=story.id,
            version=0,
            text=" ".join(["good consistent happy wonderful amazing joy love beautiful"] * 20),
        )
        content_repository.insert(content)

        result = process_review_content_tone(db_connection)

        if result.accepted:
            assert result.new_state == STATE_REVIEW_SCRIPT_EDITING

    def test_not_accepted_transitions_to_rewrite(
        self, db_connection, story_repository, content_repository
    ):
        """Not accepted review should transition to content rewrite state."""
        story = Story(idea_json='{"title": "Test"}', state=STATE_REVIEW_SCRIPT_TONE)
        story = story_repository.insert(story)

        # Create a very short content
        content = Content(story_id=story.id, version=0, text="Too short.")
        content_repository.insert(content)

        result = process_review_content_tone(db_connection)

        if not result.accepted:
            assert result.new_state == STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT


class TestGetContentForStory:
    """Tests for get_content_for_story function."""

    def test_returns_content_by_story_content_id(
        self, db_connection, story_repository, content_repository
    ):
        """Should return Content when story has content_id."""
        # Create story
        story = Story(idea_json='{"title": "Test"}', state=STATE_REVIEW_SCRIPT_TONE)
        story = story_repository.insert(story)

        # Create content
        content = Content(story_id=story.id, version=0, text="Test content content")
        content = content_repository.insert(content)

        # Update story to reference content
        story.content_id = content.id
        story_repository.update(story)

        # Get content for story
        result = get_content_for_story(content_repository, story)

        assert result is not None
        assert result.id == content.id
        assert result.text == "Test content content"

    def test_returns_latest_version_if_no_content_id(
        self, db_connection, story_repository, content_repository
    ):
        """Should return latest Content version when story has no content_id."""
        # Create story without content_id
        story = Story(idea_json='{"title": "Test"}', state=STATE_REVIEW_SCRIPT_TONE)
        story = story_repository.insert(story)

        # Create multiple content versions
        content_v0 = Content(story_id=story.id, version=0, text="Version 0")
        content_v0 = content_repository.insert(content_v0)

        content_v1 = Content(story_id=story.id, version=1, text="Version 1")
        content_v1 = content_repository.insert(content_v1)

        # Get content for story (should return latest version)
        result = get_content_for_story(content_repository, story)

        assert result is not None
        assert result.version == 1
        assert result.text == "Version 1"

    def test_returns_none_when_no_content(self, db_connection, story_repository, content_repository):
        """Should return None when no content exists for story."""
        story = Story(idea_json='{"title": "Test"}', state=STATE_REVIEW_SCRIPT_TONE)
        story = story_repository.insert(story)

        result = get_content_for_story(content_repository, story)

        assert result is None


class TestSaveReview:
    """Tests for save_review function."""

    def test_saves_review_to_database(self, db_connection):
        """Should save review to database and set ID."""
        review = Review(text="Test review", score=75)

        saved_review = save_review(db_connection, review)

        assert saved_review.id is not None

        # Verify it exists in database
        cursor = db_connection.execute("SELECT * FROM Review WHERE id = ?", (saved_review.id,))
        row = cursor.fetchone()
        assert row is not None
        assert row["text"] == "Test review"
        assert row["score"] == 75


class TestUpdateContentReviewId:
    """Tests for update_content_review_id function."""

    def test_updates_content_review_id(self, db_connection, story_repository, content_repository):
        """Should update existing content's review_id."""
        # Create a story
        story = Story(idea_json='{"title": "Test"}', state=STATE_REVIEW_SCRIPT_TONE)
        story = story_repository.insert(story)

        # Create a content without review_id
        content = Content(story_id=story.id, version=0, text="Test content")
        content = content_repository.insert(content)
        assert content.review_id is None

        # Create and save a review
        review = Review(text="Test review", score=80)
        review = save_review(db_connection, review)

        # Update content's review_id
        update_content_review_id(db_connection, content.id, review.id)

        # Verify the update in database
        updated_content = content_repository.find_by_id(content.id)
        assert updated_content.review_id == review.id


class TestReviewResult:
    """Tests for ReviewResult dataclass."""

    def test_review_result_fields(self, db_connection, story_repository, content_repository):
        """ReviewResult should have all expected fields."""
        story = Story(idea_json='{"title": "Test"}', state=STATE_REVIEW_SCRIPT_TONE)
        story = story_repository.insert(story)

        # Create a content for the story
        content = Content(story_id=story.id, version=0, text="Test content content.")
        content_repository.insert(content)

        result = process_review_content_tone(db_connection)

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
        """State constants should match StateNames values."""
        assert STATE_REVIEW_SCRIPT_TONE == StateNames.REVIEW_SCRIPT_TONE
        assert STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT == StateNames.SCRIPT_FROM_TITLE_REVIEW_SCRIPT
        assert STATE_REVIEW_SCRIPT_EDITING == StateNames.REVIEW_SCRIPT_EDITING


@pytest.mark.integration
class TestToneReviewWorkflowIntegration:
    """Integration tests for the tone review workflow."""

    def test_complete_review_flow_accepted(
        self, db_connection, story_repository, content_repository
    ):
        """Test complete review flow when accepted."""
        # Setup: Create story in correct state
        story = Story(
            idea_json='{"title": "Horror Story", "concept": "A scary tale"}',
            state=STATE_REVIEW_SCRIPT_TONE,
        )
        story = story_repository.insert(story)

        # Create a content for the story with good content
        content = Content(
            story_id=story.id,
            version=0,
            text="The dark night was filled with fear and horror. " * 20,
        )
        content_repository.insert(content)

        # Process: Execute review
        result = process_review_content_tone(db_connection, target_tone="dark horror")

        # Verify: Check result
        assert result is not None
        assert result.accepted is True
        assert result.new_state == STATE_REVIEW_SCRIPT_EDITING

        # Verify: Story state updated in database
        updated = story_repository.find_by_id(story.id)
        assert updated.state == STATE_REVIEW_SCRIPT_EDITING

    def test_complete_review_flow_not_accepted(
        self, db_connection, story_repository, content_repository
    ):
        """Test complete review flow when not accepted."""
        # Setup: Create story in correct state
        story = Story(
            idea_json='{"title": "Horror Story", "concept": "A scary tale"}',
            state=STATE_REVIEW_SCRIPT_TONE,
        )
        story = story_repository.insert(story)

        # Create a content with poor content (too short)
        content = Content(story_id=story.id, version=0, text="Short content.")
        content_repository.insert(content)

        # Process: Execute review
        result = process_review_content_tone(db_connection)

        # Verify: Check result
        assert result is not None
        assert result.accepted is False
        assert result.new_state == STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT

        # Verify: Story state updated in database
        updated = story_repository.find_by_id(story.id)
        assert updated.state == STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT

    def test_multiple_stories_processed_by_lowest_version(
        self, db_connection, story_repository, content_repository
    ):
        """Test that multiple stories are processed by lowest content version first."""
        # Create story 1 with content versions 0, 1, 2 (max=2)
        story1 = Story(idea_json='{"title": "Story 1"}', state=STATE_REVIEW_SCRIPT_TONE)
        story1 = story_repository.insert(story1)
        for v in range(3):
            content = Content(story_id=story1.id, version=v, text=f"Story 1 v{v}")
            content_repository.insert(content)

        # Create story 2 with content versions 0, 1 (max=1)
        story2 = Story(idea_json='{"title": "Story 2"}', state=STATE_REVIEW_SCRIPT_TONE)
        story2 = story_repository.insert(story2)
        for v in range(2):
            content = Content(story_id=story2.id, version=v, text=f"Story 2 v{v}")
            content_repository.insert(content)

        # Process first story - should be story2 (lower max version)
        result1 = process_review_content_tone(db_connection)
        assert result1.story.id == story2.id

        # Process second story - should be story1
        result2 = process_review_content_tone(db_connection)
        assert result2.story.id == story1.id

        # No more stories to process
        result3 = process_review_content_tone(db_connection)
        assert result3 is None
