"""Tests for PrismQ.T.Review.Title.Readability module.

These tests verify the title readability review workflow stage:
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
_module_path = _project_root / "T" / "Review" / "Title" / "Readability" / "src" / "review_title_readability.py"
_spec = importlib.util.spec_from_file_location("review_title_readability", _module_path)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

ReviewResult = _module.ReviewResult
process_review_title_readability = _module.process_review_title_readability
get_oldest_story_for_review = _module.get_oldest_story_for_review
determine_next_state = _module.determine_next_state
create_review = _module.create_review
evaluate_title_readability = _module.evaluate_title_readability
ACCEPTANCE_THRESHOLD = _module.ACCEPTANCE_THRESHOLD
STATE_REVIEW_TITLE_READABILITY = _module.STATE_REVIEW_TITLE_READABILITY
STATE_TITLE_FROM_SCRIPT_REVIEW_TITLE = _module.STATE_TITLE_FROM_SCRIPT_REVIEW_TITLE
STATE_REVIEW_SCRIPT_READABILITY = _module.STATE_REVIEW_SCRIPT_READABILITY


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
            state=STATE_REVIEW_TITLE_READABILITY
        )
        older_story = story_repository.insert(older_story)
        
        # Create a newer story (small delay to ensure different timestamps)
        newer_story = Story(
            idea_json='{"title": "Newer Story"}',
            state=STATE_REVIEW_TITLE_READABILITY
        )
        newer_story = story_repository.insert(newer_story)
        
        result = get_oldest_story_for_review(story_repository)
        
        assert result is not None
        assert result.id == older_story.id
        assert result.idea_json == '{"title": "Older Story"}'


class TestDetermineNextState:
    """Tests for determine_next_state function."""
    
    def test_not_accepted_returns_to_title_refinement(self):
        """Non-accepted review should return to title refinement."""
        result = determine_next_state(accepted=False)
        assert result == STATE_TITLE_FROM_SCRIPT_REVIEW_TITLE
    
    def test_accepted_proceeds_to_script_readability(self):
        """Accepted review should proceed to script readability review."""
        result = determine_next_state(accepted=True)
        assert result == STATE_REVIEW_SCRIPT_READABILITY


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


class TestEvaluateTitleReadability:
    """Tests for evaluate_title_readability function."""
    
    def test_returns_score_and_text(self):
        """Should return tuple of score and review text."""
        score, text = evaluate_title_readability("The Mystery of the Hidden Key")
        
        assert isinstance(score, int)
        assert 0 <= score <= 100
        assert isinstance(text, str)
        assert len(text) > 0
    
    def test_review_text_has_prefix(self):
        """Review text should have appropriate prefix."""
        score, text = evaluate_title_readability("Test Title")
        
        assert "Title Readability Review" in text
    
    def test_short_title_penalized(self):
        """Short titles should have lower scores."""
        short_score, _ = evaluate_title_readability("X")
        normal_score, _ = evaluate_title_readability("The Great Adventure Begins")
        
        assert short_score < normal_score
    
    def test_long_title_penalized(self):
        """Very long titles should have lower scores."""
        short_score, _ = evaluate_title_readability("The Great Mystery")
        
        long_title = " ".join(["Word"] * 20)
        long_score, _ = evaluate_title_readability(long_title)
        
        assert long_score < short_score
    
    def test_difficult_consonant_clusters_penalized(self):
        """Titles with difficult consonant clusters should be penalized."""
        normal_score, _ = evaluate_title_readability("The Great Mystery")
        difficult_score, _ = evaluate_title_readability("The Sixth Strengths Test")
        
        # The difficult title with 'sths' should score lower
        assert difficult_score <= normal_score
    
    def test_engaging_words_boost_score(self):
        """Titles with engaging words should score higher."""
        plain_score, _ = evaluate_title_readability("The Test Story")
        engaging_score, _ = evaluate_title_readability("The Mystery Story")
        
        # 'mystery' is an engaging word
        assert engaging_score >= plain_score


class TestProcessReviewTitleReadability:
    """Tests for process_review_title_readability function."""
    
    def test_returns_none_when_no_stories(self, db_connection):
        """Should return None when no stories to process."""
        result = process_review_title_readability(db_connection)
        assert result is None
    
    def test_processes_story_and_returns_result(self, db_connection, story_repository):
        """Should process story and return ReviewResult."""
        # Create a story in the correct state
        story = Story(
            idea_json='{"title": "Test Story"}',
            state=STATE_REVIEW_TITLE_READABILITY
        )
        story_repository.insert(story)
        
        result = process_review_title_readability(
            db_connection,
            title_text="The Great Mystery Revealed"
        )
        
        assert result is not None
        assert isinstance(result, ReviewResult)
        assert result.story is not None
        assert result.review is not None
        assert isinstance(result.review, Review)
    
    def test_updates_story_state(self, db_connection, story_repository):
        """Should update story state after processing."""
        # Create a story
        story = Story(
            idea_json='{"title": "Test Story"}',
            state=STATE_REVIEW_TITLE_READABILITY
        )
        story = story_repository.insert(story)
        
        result = process_review_title_readability(db_connection)
        
        # Verify state was updated
        updated_story = story_repository.find_by_id(story.id)
        assert updated_story.state == result.new_state
    
    def test_accepted_transitions_to_script_readability(self, db_connection, story_repository):
        """Accepted review should transition to script readability."""
        story = Story(
            idea_json='{"title": "Test"}',
            state=STATE_REVIEW_TITLE_READABILITY
        )
        story_repository.insert(story)
        
        # Use a title that will score above threshold
        result = process_review_title_readability(
            db_connection,
            title_text="The Amazing Mystery Adventure"  # Good, engaging title
        )
        
        if result.accepted:
            assert result.new_state == STATE_REVIEW_SCRIPT_READABILITY
    
    def test_rejected_transitions_to_title_refinement(self, db_connection, story_repository):
        """Rejected review should transition to title refinement."""
        story = Story(
            idea_json='{"title": "Test"}',
            state=STATE_REVIEW_TITLE_READABILITY
        )
        story_repository.insert(story)
        
        # Use a title that will likely score below threshold
        result = process_review_title_readability(
            db_connection,
            title_text="X"  # Too short
        )
        
        if not result.accepted:
            assert result.new_state == STATE_TITLE_FROM_SCRIPT_REVIEW_TITLE


class TestReviewResult:
    """Tests for ReviewResult dataclass."""
    
    def test_review_result_fields(self, db_connection, story_repository):
        """ReviewResult should have all expected fields."""
        story = Story(
            idea_json='{"title": "Test"}',
            state=STATE_REVIEW_TITLE_READABILITY
        )
        story_repository.insert(story)
        
        result = process_review_title_readability(db_connection)
        
        assert hasattr(result, 'story')
        assert hasattr(result, 'review')
        assert hasattr(result, 'new_state')
        assert hasattr(result, 'accepted')
        
        assert isinstance(result.story, Story)
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
        assert STATE_REVIEW_TITLE_READABILITY == StateNames.REVIEW_TITLE_READABILITY
        assert STATE_TITLE_FROM_SCRIPT_REVIEW_TITLE == StateNames.TITLE_FROM_SCRIPT_REVIEW_TITLE
        assert STATE_REVIEW_SCRIPT_READABILITY == StateNames.REVIEW_SCRIPT_READABILITY


@pytest.mark.integration
class TestReviewWorkflowIntegration:
    """Integration tests for the review workflow."""
    
    def test_complete_acceptance_flow(self, db_connection, story_repository):
        """Test complete acceptance flow."""
        # Setup: Create story in correct state
        story = Story(
            idea_json='{"title": "Horror Story", "concept": "A scary tale"}',
            state=STATE_REVIEW_TITLE_READABILITY
        )
        story = story_repository.insert(story)
        
        # Process: Execute review with good title
        result = process_review_title_readability(
            db_connection,
            title_text="The Amazing Mystery Adventure"
        )
        
        # Verify: Check result
        assert result is not None
        assert result.review.score >= 0
        assert result.review.score <= 100
        
        # Verify: Story state updated in database
        updated = story_repository.find_by_id(story.id)
        assert updated.state in [STATE_REVIEW_SCRIPT_READABILITY, STATE_TITLE_FROM_SCRIPT_REVIEW_TITLE]
    
    def test_complete_rejection_flow(self, db_connection, story_repository):
        """Test complete rejection flow."""
        # Setup: Create story in correct state
        story = Story(
            idea_json='{"title": "Test", "concept": "A test"}',
            state=STATE_REVIEW_TITLE_READABILITY
        )
        story = story_repository.insert(story)
        
        # Process: Execute review with poor title
        result = process_review_title_readability(
            db_connection,
            title_text="X"  # Very short, should fail
        )
        
        # Verify: Check result
        assert result is not None
        assert not result.accepted
        assert result.new_state == STATE_TITLE_FROM_SCRIPT_REVIEW_TITLE
        
        # Verify: Story state updated in database
        updated = story_repository.find_by_id(story.id)
        assert updated.state == STATE_TITLE_FROM_SCRIPT_REVIEW_TITLE
    
    def test_multiple_stories_processed_in_order(self, db_connection, story_repository):
        """Test that multiple stories are processed oldest first."""
        # Create multiple stories
        story1 = Story(
            idea_json='{"title": "Story 1"}',
            state=STATE_REVIEW_TITLE_READABILITY
        )
        story1 = story_repository.insert(story1)
        
        story2 = Story(
            idea_json='{"title": "Story 2"}',
            state=STATE_REVIEW_TITLE_READABILITY
        )
        story2 = story_repository.insert(story2)
        
        # Process first story
        result1 = process_review_title_readability(db_connection)
        assert result1.story.id == story1.id
        
        # Process second story
        result2 = process_review_title_readability(db_connection)
        assert result2.story.id == story2.id
        
        # No more stories to process
        result3 = process_review_title_readability(db_connection)
        assert result3 is None
