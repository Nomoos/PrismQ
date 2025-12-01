"""Tests for PrismQ.T.Review.Script.From.Title module.

These tests verify the review script from title workflow stage:
1. Selecting oldest Story with correct state
2. Creating Review model with text and score
3. State transitions based on review acceptance
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
from T.Database.models.review import Review
from T.Database.repositories.story_repository import StoryRepository
from T.State.constants.state_names import StateNames


# Import the module to test using direct file loading to avoid circular import
_module_path = _project_root / "T" / "Review" / "Script" / "From" / "Title" / "src" / "review_script_from_title.py"
_spec = importlib.util.spec_from_file_location("review_script_from_title", _module_path)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

ReviewResult = _module.ReviewResult
process_review_script_from_title = _module.process_review_script_from_title
get_oldest_story_for_review = _module.get_oldest_story_for_review
determine_next_state = _module.determine_next_state
create_review = _module.create_review
evaluate_script = _module.evaluate_script
ACCEPTANCE_THRESHOLD = _module.ACCEPTANCE_THRESHOLD
STATE_REVIEW_SCRIPT_FROM_TITLE = _module.STATE_REVIEW_SCRIPT_FROM_TITLE
STATE_REVIEW_TITLE_FROM_SCRIPT = _module.STATE_REVIEW_TITLE_FROM_SCRIPT
STATE_REVIEW_SCRIPT_GRAMMAR = _module.STATE_REVIEW_SCRIPT_GRAMMAR


@pytest.fixture
def db_connection():
    """Create an in-memory SQLite database with Story table."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    
    # Create Story table
    conn.executescript(Story.get_sql_schema())
    
    yield conn
    conn.close()


@pytest.fixture
def story_repository(db_connection):
    """Create a StoryRepository instance."""
    return StoryRepository(db_connection)


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
            state=STATE_REVIEW_SCRIPT_FROM_TITLE
        )
        older_story = story_repository.insert(older_story)
        
        # Create a newer story (small delay to ensure different timestamps)
        newer_story = Story(
            idea_json='{"title": "Newer Story"}',
            state=STATE_REVIEW_SCRIPT_FROM_TITLE
        )
        newer_story = story_repository.insert(newer_story)
        
        result = get_oldest_story_for_review(story_repository)
        
        assert result is not None
        assert result.id == older_story.id
        assert result.idea_json == '{"title": "Older Story"}'


class TestDetermineNextState:
    """Tests for determine_next_state function."""
    
    def test_first_review_goes_to_title_review(self):
        """First review should transition to Review.Title.From.Script."""
        result = determine_next_state(accepted=True, is_first_review=True)
        assert result == STATE_REVIEW_TITLE_FROM_SCRIPT
        
        # Even if not accepted, first review goes to title review
        result = determine_next_state(accepted=False, is_first_review=True)
        assert result == STATE_REVIEW_TITLE_FROM_SCRIPT
    
    def test_not_accepted_stays_for_rewrite(self):
        """Non-first review that's not accepted should stay in same state."""
        result = determine_next_state(accepted=False, is_first_review=False)
        assert result == STATE_REVIEW_SCRIPT_FROM_TITLE
    
    def test_accepted_non_first_goes_to_grammar(self):
        """Accepted non-first review should proceed to grammar check."""
        result = determine_next_state(accepted=True, is_first_review=False)
        assert result == STATE_REVIEW_SCRIPT_GRAMMAR


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


class TestEvaluateScript:
    """Tests for evaluate_script function."""
    
    def test_returns_score_and_text(self):
        """Should return tuple of score and review text."""
        score, text = evaluate_script(
            script_text="This is a test script about horror.",
            title_text="Horror Story",
            is_first_review=True
        )
        
        assert isinstance(score, int)
        assert 0 <= score <= 100
        assert isinstance(text, str)
        assert len(text) > 0
    
    def test_first_review_prefix(self):
        """First review should have appropriate prefix."""
        score, text = evaluate_script(
            script_text="Test script content",
            title_text="Test Title",
            is_first_review=True
        )
        
        assert "Initial script review" in text
    
    def test_follow_up_review_prefix(self):
        """Follow-up review should have appropriate prefix."""
        score, text = evaluate_script(
            script_text="Test script content",
            title_text="Test Title",
            is_first_review=False
        )
        
        assert "Follow-up script review" in text
    
    def test_short_script_penalized(self):
        """Short scripts should have lower scores."""
        short_score, _ = evaluate_script(
            script_text="Too short.",
            title_text="Test",
            is_first_review=True
        )
        
        normal_score, _ = evaluate_script(
            script_text=" ".join(["word"] * 150),
            title_text="Test",
            is_first_review=True
        )
        
        assert short_score < normal_score
    
    def test_title_alignment_affects_score(self):
        """Scripts aligned with title should score higher."""
        aligned_score, _ = evaluate_script(
            script_text="The horror story began in a dark castle with mysterious echoes.",
            title_text="Horror Castle Mystery",
            is_first_review=True
        )
        
        unaligned_score, _ = evaluate_script(
            script_text="The sun was shining on a beautiful summer day.",
            title_text="Horror Castle Mystery",
            is_first_review=True
        )
        
        assert aligned_score > unaligned_score


class TestProcessReviewScriptFromTitle:
    """Tests for process_review_script_from_title function."""
    
    def test_returns_none_when_no_stories(self, db_connection):
        """Should return None when no stories to process."""
        result = process_review_script_from_title(db_connection)
        assert result is None
    
    def test_processes_story_and_returns_result(self, db_connection, story_repository):
        """Should process story and return ReviewResult."""
        # Create a story in the correct state
        story = Story(
            idea_json='{"title": "Test Story"}',
            state=STATE_REVIEW_SCRIPT_FROM_TITLE
        )
        story_repository.insert(story)
        
        result = process_review_script_from_title(
            db_connection,
            is_first_review=True,
            script_text="This is a test script with good content about the topic.",
            title_text="Test Story"
        )
        
        assert result is not None
        assert isinstance(result, ReviewResult)
        assert result.story is not None
        assert result.review is not None
        assert isinstance(result.review, Review)
        assert result.is_first_review is True
    
    def test_updates_story_state(self, db_connection, story_repository):
        """Should update story state after processing."""
        # Create a story
        story = Story(
            idea_json='{"title": "Test Story"}',
            state=STATE_REVIEW_SCRIPT_FROM_TITLE
        )
        story = story_repository.insert(story)
        
        result = process_review_script_from_title(
            db_connection,
            is_first_review=True
        )
        
        # Verify state was updated
        updated_story = story_repository.find_by_id(story.id)
        assert updated_story.state == result.new_state
    
    def test_first_review_transitions_to_title_review(self, db_connection, story_repository):
        """First review should transition to title review state."""
        story = Story(
            idea_json='{"title": "Test"}',
            state=STATE_REVIEW_SCRIPT_FROM_TITLE
        )
        story_repository.insert(story)
        
        result = process_review_script_from_title(
            db_connection,
            is_first_review=True
        )
        
        assert result.new_state == STATE_REVIEW_TITLE_FROM_SCRIPT
    
    def test_accepted_non_first_transitions_to_grammar(self, db_connection, story_repository):
        """Accepted non-first review should transition to grammar review."""
        story = Story(
            idea_json='{"title": "Test"}',
            state=STATE_REVIEW_SCRIPT_FROM_TITLE
        )
        story_repository.insert(story)
        
        # Use a script that will score above threshold
        result = process_review_script_from_title(
            db_connection,
            is_first_review=False,
            script_text=" ".join(["good content about the main topic"] * 50),
            title_text="main topic"
        )
        
        if result.accepted:
            assert result.new_state == STATE_REVIEW_SCRIPT_GRAMMAR
        else:
            assert result.new_state == STATE_REVIEW_SCRIPT_FROM_TITLE


class TestReviewResult:
    """Tests for ReviewResult dataclass."""
    
    def test_review_result_fields(self, db_connection, story_repository):
        """ReviewResult should have all expected fields."""
        story = Story(
            idea_json='{"title": "Test"}',
            state=STATE_REVIEW_SCRIPT_FROM_TITLE
        )
        story_repository.insert(story)
        
        result = process_review_script_from_title(
            db_connection,
            is_first_review=True
        )
        
        assert hasattr(result, 'story')
        assert hasattr(result, 'review')
        assert hasattr(result, 'new_state')
        assert hasattr(result, 'accepted')
        assert hasattr(result, 'is_first_review')
        
        assert isinstance(result.story, Story)
        assert isinstance(result.review, Review)
        assert isinstance(result.new_state, str)
        assert isinstance(result.accepted, bool)
        assert isinstance(result.is_first_review, bool)


class TestConstants:
    """Tests for module constants."""
    
    def test_acceptance_threshold_in_valid_range(self):
        """Acceptance threshold should be in valid score range."""
        assert 0 <= ACCEPTANCE_THRESHOLD <= 100
    
    def test_state_constants_are_valid(self):
        """State constants should match StateNames values."""
        assert STATE_REVIEW_SCRIPT_FROM_TITLE == StateNames.REVIEW_SCRIPT_FROM_TITLE
        assert STATE_REVIEW_TITLE_FROM_SCRIPT == StateNames.REVIEW_TITLE_FROM_SCRIPT
        assert STATE_REVIEW_SCRIPT_GRAMMAR == StateNames.REVIEW_SCRIPT_GRAMMAR


@pytest.mark.integration
class TestReviewWorkflowIntegration:
    """Integration tests for the review workflow."""
    
    def test_complete_first_review_flow(self, db_connection, story_repository):
        """Test complete first review flow."""
        # Setup: Create story in correct state
        story = Story(
            idea_json='{"title": "Horror Story", "concept": "A scary tale"}',
            state=STATE_REVIEW_SCRIPT_FROM_TITLE
        )
        story = story_repository.insert(story)
        
        # Process: Execute review
        result = process_review_script_from_title(
            db_connection,
            is_first_review=True,
            script_text="The horror began on a dark night. " * 20,
            title_text="Horror Story"
        )
        
        # Verify: Check result
        assert result is not None
        assert result.is_first_review is True
        assert result.new_state == STATE_REVIEW_TITLE_FROM_SCRIPT
        
        # Verify: Story state updated in database
        updated = story_repository.find_by_id(story.id)
        assert updated.state == STATE_REVIEW_TITLE_FROM_SCRIPT
    
    def test_multiple_stories_processed_in_order(self, db_connection, story_repository):
        """Test that multiple stories are processed oldest first."""
        # Create multiple stories
        story1 = Story(
            idea_json='{"title": "Story 1"}',
            state=STATE_REVIEW_SCRIPT_FROM_TITLE
        )
        story1 = story_repository.insert(story1)
        
        story2 = Story(
            idea_json='{"title": "Story 2"}',
            state=STATE_REVIEW_SCRIPT_FROM_TITLE
        )
        story2 = story_repository.insert(story2)
        
        # Process first story
        result1 = process_review_script_from_title(db_connection, is_first_review=True)
        assert result1.story.id == story1.id
        
        # Process second story
        result2 = process_review_script_from_title(db_connection, is_first_review=True)
        assert result2.story.id == story2.id
        
        # No more stories to process
        result3 = process_review_script_from_title(db_connection, is_first_review=True)
        assert result3 is None
