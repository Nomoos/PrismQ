"""Tests for PrismQ.T.Review.Script.Tone module.

These tests verify the review script tone workflow stage:
1. Selecting oldest Story with correct state
2. Getting the Script for the Story
3. Creating Review model with text and score
4. Linking Review to Script via Script.review_id FK
5. State transitions based on review acceptance
"""

import pytest
import sqlite3
from datetime import datetime
import sys
from pathlib import Path
import importlib.util

# Add project root to path for imports
_test_dir = Path(__file__).parent
_project_root = _test_dir.parent
sys.path.insert(0, str(_project_root))

from T.Database.models.story import Story
from T.Database.models.script import Script
from T.Database.models.review import Review
from T.Database.repositories.story_repository import StoryRepository
from T.Database.repositories.script_repository import ScriptRepository
from T.State.constants.state_names import StateNames


# Import the module to test using direct file loading to avoid circular import
_module_path = _project_root / "T" / "Review" / "Script" / "Tone" / "src" / "review_script_tone.py"
_spec = importlib.util.spec_from_file_location("review_script_tone", _module_path)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

ReviewResult = _module.ReviewResult
process_review_script_tone = _module.process_review_script_tone
get_oldest_story_for_review = _module.get_oldest_story_for_review
get_script_for_story = _module.get_script_for_story
save_review = _module.save_review
update_script_review_id = _module.update_script_review_id
determine_next_state = _module.determine_next_state
create_review = _module.create_review
evaluate_tone = _module.evaluate_tone
ACCEPTANCE_THRESHOLD = _module.ACCEPTANCE_THRESHOLD
STATE_REVIEW_SCRIPT_TONE = _module.STATE_REVIEW_SCRIPT_TONE
STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT = _module.STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT
STATE_REVIEW_SCRIPT_EDITING = _module.STATE_REVIEW_SCRIPT_EDITING


# SQL schema for Script table
SCRIPT_SQL_SCHEMA = """
CREATE TABLE IF NOT EXISTS Script (
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
    """Create an in-memory SQLite database with Story, Script, and Review tables."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    
    # Create all tables
    conn.executescript(Story.get_sql_schema())
    conn.executescript(SCRIPT_SQL_SCHEMA)
    conn.executescript(REVIEW_SQL_SCHEMA)
    
    yield conn
    conn.close()


@pytest.fixture
def story_repository(db_connection):
    """Create a StoryRepository instance."""
    return StoryRepository(db_connection)


@pytest.fixture
def script_repository(db_connection):
    """Create a ScriptRepository instance."""
    return ScriptRepository(db_connection)


class TestGetOldestStoryForReview:
    """Tests for get_oldest_story_for_review function."""
    
    def test_returns_none_when_no_stories(self, story_repository):
        """Should return None when no stories exist."""
        result = get_oldest_story_for_review(story_repository)
        assert result is None
    
    def test_returns_none_when_no_stories_in_correct_state(self, story_repository):
        """Should return None when no stories have the correct state."""
        # Create a story with different state
        story = Story(
            idea_json='{"title": "Test"}',
            state=StateNames.IDEA_CREATION
        )
        story_repository.insert(story)
        
        result = get_oldest_story_for_review(story_repository)
        assert result is None
    
    def test_returns_oldest_story_in_correct_state(self, story_repository, db_connection):
        """Should return the oldest story with the correct state."""
        # Create multiple stories
        older_story = Story(
            idea_json='{"title": "Older Story"}',
            state=STATE_REVIEW_SCRIPT_TONE
        )
        older_story = story_repository.insert(older_story)
        
        # Create a newer story
        newer_story = Story(
            idea_json='{"title": "Newer Story"}',
            state=STATE_REVIEW_SCRIPT_TONE
        )
        newer_story = story_repository.insert(newer_story)
        
        result = get_oldest_story_for_review(story_repository)
        
        assert result is not None
        assert result.id == older_story.id
        assert result.idea_json == '{"title": "Older Story"}'


class TestDetermineNextState:
    """Tests for determine_next_state function."""
    
    def test_not_accepted_goes_to_script_rewrite(self):
        """Not accepted should transition to script rewrite state."""
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
            script_text="This is a test script about horror and fear.",
        )
        
        assert isinstance(score, int)
        assert 0 <= score <= 100
        assert isinstance(text, str)
        assert len(text) > 0
    
    def test_tone_review_prefix(self):
        """Review should have appropriate prefix."""
        score, text = evaluate_tone(
            script_text="Test script content about mysterious dark events.",
        )
        
        assert "Tone review:" in text
    
    def test_short_script_penalized(self):
        """Short scripts should have lower scores."""
        short_score, _ = evaluate_tone(
            script_text="Too short.",
        )
        
        normal_score, _ = evaluate_tone(
            script_text=" ".join(["word"] * 150),
        )
        
        assert short_score < normal_score
    
    def test_consistent_positive_tone(self):
        """Scripts with consistent positive tone should score well."""
        score, text = evaluate_tone(
            script_text="The happy character felt joy and excitement. Everything was wonderful and amazing. They loved the beautiful view.",
        )
        
        assert "positive tone" in text.lower() or "consistent" in text.lower()
        assert score >= 70
    
    def test_consistent_negative_tone(self):
        """Scripts with consistent dark/negative tone should score well."""
        score, text = evaluate_tone(
            script_text="The dark night was filled with fear and horror. The terrible events were scary and ugly. " * 5,
        )
        
        assert "dark" in text.lower() or "dramatic" in text.lower() or "consistent" in text.lower()
        assert score >= 70
    
    def test_target_tone_alignment(self):
        """Scripts should be evaluated against target tone if specified."""
        # Test dark tone alignment
        aligned_score, _ = evaluate_tone(
            script_text="The dark night was filled with fear and horror. Scary shadows lurked everywhere.",
            target_tone="dark suspense"
        )
        
        unaligned_score, _ = evaluate_tone(
            script_text="The happy sunny day was wonderful. Everyone was joyful and excited.",
            target_tone="dark suspense"
        )
        
        assert aligned_score > unaligned_score


class TestProcessReviewScriptTone:
    """Tests for process_review_script_tone function."""
    
    def test_returns_none_when_no_stories(self, db_connection):
        """Should return None when no stories to process."""
        result = process_review_script_tone(db_connection)
        assert result is None
    
    def test_processes_story_and_returns_result(self, db_connection, story_repository):
        """Should process story and return ReviewResult."""
        # Create a story in the correct state
        story = Story(
            idea_json='{"title": "Test Story"}',
            state=STATE_REVIEW_SCRIPT_TONE
        )
        story_repository.insert(story)
        
        result = process_review_script_tone(
            db_connection,
            script_text="This is a test script with consistent dark tone about fear and horror."
        )
        
        assert result is not None
        assert isinstance(result, ReviewResult)
        assert result.story is not None
        assert result.review is not None
        assert result.script is not None
        assert isinstance(result.review, Review)
        assert isinstance(result.script, Script)
    
    def test_review_saved_to_database(self, db_connection, story_repository):
        """Review should be saved to database and have an ID."""
        story = Story(
            idea_json='{"title": "Test Story"}',
            state=STATE_REVIEW_SCRIPT_TONE
        )
        story_repository.insert(story)
        
        result = process_review_script_tone(
            db_connection,
            script_text="This is a test script with consistent dark tone about fear and horror."
        )
        
        # Verify review has an ID (was saved to database)
        assert result.review.id is not None
        
        # Verify review can be retrieved from database
        cursor = db_connection.execute("SELECT * FROM Review WHERE id = ?", (result.review.id,))
        row = cursor.fetchone()
        assert row is not None
        assert row['score'] == result.review.score
    
    def test_script_references_review(self, db_connection, story_repository, script_repository):
        """Script should have review_id set to link to the Review."""
        # Create story with existing script
        story = Story(
            idea_json='{"title": "Test Story"}',
            state=STATE_REVIEW_SCRIPT_TONE
        )
        story = story_repository.insert(story)
        
        # Create initial script for the story
        initial_script = Script(
            story_id=story.id,
            version=0,
            text="Initial script content about dark horror and fear."
        )
        initial_script = script_repository.insert(initial_script)
        
        # Update story to reference the script
        story.script_id = initial_script.id
        story_repository.update(story)
        
        # Process the review
        result = process_review_script_tone(db_connection)
        
        # Verify script has review_id set (same script, not new version)
        assert result.script is not None
        assert result.script.id == initial_script.id  # Same script, not a new version
        assert result.script.review_id is not None
        assert result.script.review_id == result.review.id
        
        # Verify in database the script's review_id was updated
        updated_script = script_repository.find_by_id(initial_script.id)
        assert updated_script.review_id == result.review.id
    
    def test_updates_story_state(self, db_connection, story_repository):
        """Should update story state after processing."""
        # Create a story
        story = Story(
            idea_json='{"title": "Test Story"}',
            state=STATE_REVIEW_SCRIPT_TONE
        )
        story = story_repository.insert(story)
        
        result = process_review_script_tone(db_connection)
        
        # Verify state was updated
        updated_story = story_repository.find_by_id(story.id)
        assert updated_story.state == result.new_state
    
    def test_accepted_transitions_to_editing(self, db_connection, story_repository):
        """Accepted review should transition to editing review state."""
        story = Story(
            idea_json='{"title": "Test"}',
            state=STATE_REVIEW_SCRIPT_TONE
        )
        story_repository.insert(story)
        
        # Use a script that will score above threshold
        result = process_review_script_tone(
            db_connection,
            script_text=" ".join(["good consistent happy wonderful amazing joy love beautiful"] * 20)
        )
        
        if result.accepted:
            assert result.new_state == STATE_REVIEW_SCRIPT_EDITING
    
    def test_not_accepted_transitions_to_rewrite(self, db_connection, story_repository):
        """Not accepted review should transition to script rewrite state."""
        story = Story(
            idea_json='{"title": "Test"}',
            state=STATE_REVIEW_SCRIPT_TONE
        )
        story_repository.insert(story)
        
        # Use a very short script that will score below threshold
        result = process_review_script_tone(
            db_connection,
            script_text="Too short."
        )
        
        if not result.accepted:
            assert result.new_state == STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT


class TestGetScriptForStory:
    """Tests for get_script_for_story function."""
    
    def test_returns_script_by_story_script_id(self, db_connection, story_repository, script_repository):
        """Should return Script when story has script_id."""
        # Create story
        story = Story(
            idea_json='{"title": "Test"}',
            state=STATE_REVIEW_SCRIPT_TONE
        )
        story = story_repository.insert(story)
        
        # Create script
        script = Script(
            story_id=story.id,
            version=0,
            text="Test script content"
        )
        script = script_repository.insert(script)
        
        # Update story to reference script
        story.script_id = script.id
        story_repository.update(story)
        
        # Get script for story
        result = get_script_for_story(script_repository, story)
        
        assert result is not None
        assert result.id == script.id
        assert result.text == "Test script content"
    
    def test_returns_latest_version_if_no_script_id(self, db_connection, story_repository, script_repository):
        """Should return latest Script version when story has no script_id."""
        # Create story without script_id
        story = Story(
            idea_json='{"title": "Test"}',
            state=STATE_REVIEW_SCRIPT_TONE
        )
        story = story_repository.insert(story)
        
        # Create multiple script versions
        script_v0 = Script(story_id=story.id, version=0, text="Version 0")
        script_v0 = script_repository.insert(script_v0)
        
        script_v1 = Script(story_id=story.id, version=1, text="Version 1")
        script_v1 = script_repository.insert(script_v1)
        
        # Get script for story (should return latest version)
        result = get_script_for_story(script_repository, story)
        
        assert result is not None
        assert result.version == 1
        assert result.text == "Version 1"
    
    def test_returns_none_when_no_script(self, db_connection, story_repository, script_repository):
        """Should return None when no script exists for story."""
        story = Story(
            idea_json='{"title": "Test"}',
            state=STATE_REVIEW_SCRIPT_TONE
        )
        story = story_repository.insert(story)
        
        result = get_script_for_story(script_repository, story)
        
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
        assert row['text'] == "Test review"
        assert row['score'] == 75


class TestUpdateScriptReviewId:
    """Tests for update_script_review_id function."""
    
    def test_updates_script_review_id(self, db_connection, story_repository, script_repository):
        """Should update existing script's review_id."""
        # Create a story
        story = Story(idea_json='{"title": "Test"}', state=STATE_REVIEW_SCRIPT_TONE)
        story = story_repository.insert(story)
        
        # Create a script without review_id
        script = Script(story_id=story.id, version=0, text="Test content")
        script = script_repository.insert(script)
        assert script.review_id is None
        
        # Create and save a review
        review = Review(text="Test review", score=80)
        review = save_review(db_connection, review)
        
        # Update script's review_id
        update_script_review_id(db_connection, script.id, review.id)
        
        # Verify the update in database
        updated_script = script_repository.find_by_id(script.id)
        assert updated_script.review_id == review.id


class TestReviewResult:
    """Tests for ReviewResult dataclass."""
    
    def test_review_result_fields(self, db_connection, story_repository):
        """ReviewResult should have all expected fields."""
        story = Story(
            idea_json='{"title": "Test"}',
            state=STATE_REVIEW_SCRIPT_TONE
        )
        story_repository.insert(story)
        
        result = process_review_script_tone(db_connection)
        
        assert hasattr(result, 'story')
        assert hasattr(result, 'script')
        assert hasattr(result, 'review')
        assert hasattr(result, 'new_state')
        assert hasattr(result, 'accepted')
        
        assert isinstance(result.story, Story)
        assert isinstance(result.script, Script)
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
    
    def test_complete_review_flow_accepted(self, db_connection, story_repository):
        """Test complete review flow when accepted."""
        # Setup: Create story in correct state
        story = Story(
            idea_json='{"title": "Horror Story", "concept": "A scary tale"}',
            state=STATE_REVIEW_SCRIPT_TONE
        )
        story = story_repository.insert(story)
        
        # Process: Execute review with good tone script
        result = process_review_script_tone(
            db_connection,
            script_text="The dark night was filled with fear and horror. " * 20,
            target_tone="dark horror"
        )
        
        # Verify: Check result
        assert result is not None
        assert result.accepted is True
        assert result.new_state == STATE_REVIEW_SCRIPT_EDITING
        
        # Verify: Story state updated in database
        updated = story_repository.find_by_id(story.id)
        assert updated.state == STATE_REVIEW_SCRIPT_EDITING
    
    def test_complete_review_flow_not_accepted(self, db_connection, story_repository):
        """Test complete review flow when not accepted."""
        # Setup: Create story in correct state
        story = Story(
            idea_json='{"title": "Horror Story", "concept": "A scary tale"}',
            state=STATE_REVIEW_SCRIPT_TONE
        )
        story = story_repository.insert(story)
        
        # Process: Execute review with poor tone script (too short)
        result = process_review_script_tone(
            db_connection,
            script_text="Short script."
        )
        
        # Verify: Check result
        assert result is not None
        assert result.accepted is False
        assert result.new_state == STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT
        
        # Verify: Story state updated in database
        updated = story_repository.find_by_id(story.id)
        assert updated.state == STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT
    
    def test_multiple_stories_processed_in_order(self, db_connection, story_repository):
        """Test that multiple stories are processed oldest first."""
        # Create multiple stories
        story1 = Story(
            idea_json='{"title": "Story 1"}',
            state=STATE_REVIEW_SCRIPT_TONE
        )
        story1 = story_repository.insert(story1)
        
        story2 = Story(
            idea_json='{"title": "Story 2"}',
            state=STATE_REVIEW_SCRIPT_TONE
        )
        story2 = story_repository.insert(story2)
        
        # Process first story
        result1 = process_review_script_tone(db_connection)
        assert result1.story.id == story1.id
        
        # Process second story
        result2 = process_review_script_tone(db_connection)
        assert result2.story.id == story2.id
        
        # No more stories to process
        result3 = process_review_script_tone(db_connection)
        assert result3 is None
