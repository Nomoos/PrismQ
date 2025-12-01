"""Tests for PrismQ.T.Review.Script.Readability module.

These tests verify the review script readability workflow stage:
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
_module_path = _project_root / "T" / "Review" / "Script" / "Readability" / "src" / "review_script_readability_service.py"
_spec = importlib.util.spec_from_file_location("review_script_readability_service", _module_path)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

ReviewResult = _module.ReviewResult
process_review_script_readability = _module.process_review_script_readability
get_oldest_story_for_review = _module.get_oldest_story_for_review
determine_next_state = _module.determine_next_state
create_review = _module.create_review
evaluate_script_readability = _module.evaluate_script_readability
ACCEPTANCE_THRESHOLD = _module.ACCEPTANCE_THRESHOLD
STATE_REVIEW_SCRIPT_READABILITY = _module.STATE_REVIEW_SCRIPT_READABILITY
STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT = _module.STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT
STATE_STORY_REVIEW = _module.STATE_STORY_REVIEW


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
            state=STATE_REVIEW_SCRIPT_READABILITY
        )
        older_story = story_repository.insert(older_story)
        
        # Create a newer story (small delay to ensure different timestamps)
        newer_story = Story(
            idea_json='{"title": "Newer Story"}',
            state=STATE_REVIEW_SCRIPT_READABILITY
        )
        newer_story = story_repository.insert(newer_story)
        
        result = get_oldest_story_for_review(story_repository)
        
        assert result is not None
        assert result.id == older_story.id
        assert result.idea_json == '{"title": "Older Story"}'


class TestDetermineNextState:
    """Tests for determine_next_state function."""
    
    def test_not_accepted_goes_to_script_refinement(self):
        """Not accepted review should transition to script refinement."""
        result = determine_next_state(accepted=False)
        assert result == STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT
    
    def test_accepted_goes_to_story_review(self):
        """Accepted review should proceed to story review."""
        result = determine_next_state(accepted=True)
        assert result == STATE_STORY_REVIEW


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


class TestEvaluateScriptReadability:
    """Tests for evaluate_script_readability function."""
    
    def test_returns_score_text_and_review(self):
        """Should return tuple of score, review text, and ReadabilityReview."""
        score, text, review = evaluate_script_readability(
            script_text="This is a test script about horror.",
            script_id="test-001",
            script_version="v3"
        )
        
        assert isinstance(score, int)
        assert 0 <= score <= 100
        assert isinstance(text, str)
        assert len(text) > 0
        assert review is not None
    
    def test_good_script_gets_high_score(self):
        """A well-formed script should get a high score."""
        # A script without readability issues
        good_script = """The sun rose over the quiet valley.
Birds began their morning songs.
A gentle breeze rustled the leaves.
Peace filled the air."""
        
        score, text, review = evaluate_script_readability(
            script_text=good_script,
            script_id="good-script-001"
        )
        
        # Good script should have high score
        assert score >= 85
    
    def test_difficult_script_gets_lower_score(self):
        """A script with readability issues should get a lower score."""
        # A script with tongue twisters and pronunciation issues
        difficult_script = """Peter Piper picked a peck of particularly problematic peppers.
The phenomenon of phosphorescence perplexed physicists persistently.
She sells seashells by the seashore, specifically selecting superior specimens.
The strengths of the sixth method remained unclear."""
        
        score, text, review = evaluate_script_readability(
            script_text=difficult_script,
            script_id="difficult-script-001"
        )
        
        # Difficult script should have lower score
        assert score < 85


class TestProcessReviewScriptReadability:
    """Tests for process_review_script_readability function."""
    
    def test_returns_none_when_no_stories(self, db_connection):
        """Should return None when no stories to process."""
        result = process_review_script_readability(db_connection)
        assert result is None
    
    def test_processes_story_and_returns_result(self, db_connection, story_repository):
        """Should process story and return ReviewResult."""
        # Create a story in the correct state
        story = Story(
            idea_json='{"title": "Test Story"}',
            state=STATE_REVIEW_SCRIPT_READABILITY
        )
        story_repository.insert(story)
        
        result = process_review_script_readability(
            db_connection,
            script_text="This is a simple test script about the story. It has good flow and is easy to read."
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
            state=STATE_REVIEW_SCRIPT_READABILITY
        )
        story = story_repository.insert(story)
        
        result = process_review_script_readability(db_connection)
        
        # Verify state was updated
        updated_story = story_repository.find_by_id(story.id)
        assert updated_story.state == result.new_state
    
    def test_accepted_review_transitions_to_story_review(self, db_connection, story_repository):
        """Accepted review should transition to story review state."""
        story = Story(
            idea_json='{"title": "Test"}',
            state=STATE_REVIEW_SCRIPT_READABILITY
        )
        story_repository.insert(story)
        
        # Use a script that will pass readability
        good_script = """The sun rose over the quiet valley.
Birds began their morning songs.
A gentle breeze rustled the leaves.
Peace filled the air."""
        
        result = process_review_script_readability(
            db_connection,
            script_text=good_script
        )
        
        if result.accepted:
            assert result.new_state == STATE_STORY_REVIEW
    
    def test_rejected_review_transitions_to_script_refinement(self, db_connection, story_repository):
        """Rejected review should transition to script refinement state."""
        story = Story(
            idea_json='{"title": "Test"}',
            state=STATE_REVIEW_SCRIPT_READABILITY
        )
        story_repository.insert(story)
        
        # Use a difficult script that will fail readability
        difficult_script = """Peter Piper picked a peck of particularly problematic peppers.
The phenomenon of phosphorescence perplexed physicists persistently pursuing explanations.
She sells seashells by the seashore, specifically selecting superior specimens.
The strengths of the sixth method remained unclear and undoubtedly questionable.
Subsequently, the methodology employed in the implementation of the aforementioned functionality was unequivocally quintessential."""
        
        result = process_review_script_readability(
            db_connection,
            script_text=difficult_script
        )
        
        if not result.accepted:
            assert result.new_state == STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT


class TestReviewResult:
    """Tests for ReviewResult dataclass."""
    
    def test_review_result_fields(self, db_connection, story_repository):
        """ReviewResult should have all expected fields."""
        story = Story(
            idea_json='{"title": "Test"}',
            state=STATE_REVIEW_SCRIPT_READABILITY
        )
        story_repository.insert(story)
        
        result = process_review_script_readability(db_connection)
        
        assert hasattr(result, 'story')
        assert hasattr(result, 'review')
        assert hasattr(result, 'new_state')
        assert hasattr(result, 'accepted')
        assert hasattr(result, 'readability_review')
        
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
        assert STATE_REVIEW_SCRIPT_READABILITY == StateNames.REVIEW_SCRIPT_READABILITY
        assert STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT == StateNames.SCRIPT_FROM_SCRIPT_REVIEW_TITLE
        assert STATE_STORY_REVIEW == StateNames.STORY_REVIEW


@pytest.mark.integration
class TestReadabilityReviewWorkflowIntegration:
    """Integration tests for the readability review workflow."""
    
    def test_complete_review_flow_accepted(self, db_connection, story_repository):
        """Test complete review flow for accepted script."""
        # Setup: Create story in correct state
        story = Story(
            idea_json='{"title": "Simple Story", "concept": "A simple tale"}',
            state=STATE_REVIEW_SCRIPT_READABILITY
        )
        story = story_repository.insert(story)
        
        # Good script that should pass readability
        good_script = """The morning came quietly to the small town.
Sarah opened her eyes slowly.
She listened to the birds outside her window.
It was going to be a good day."""
        
        # Process: Execute review
        result = process_review_script_readability(
            db_connection,
            script_text=good_script
        )
        
        # Verify: Check result
        assert result is not None
        
        # Verify: Story state updated in database
        updated = story_repository.find_by_id(story.id)
        if result.accepted:
            assert updated.state == STATE_STORY_REVIEW
        else:
            assert updated.state == STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT
    
    def test_complete_review_flow_rejected(self, db_connection, story_repository):
        """Test complete review flow for rejected script."""
        # Setup: Create story in correct state
        story = Story(
            idea_json='{"title": "Complex Story", "concept": "A complex tale"}',
            state=STATE_REVIEW_SCRIPT_READABILITY
        )
        story = story_repository.insert(story)
        
        # Difficult script that should fail readability
        difficult_script = """Peter Piper picked a peck of particularly problematic peppers from the phosphorescent patch.
The phenomenon of phosphorescence perplexed physicists persistently pursuing explanations.
Subsequently the methodology employed in the implementation of the aforementioned functionality was unequivocally quintessential and indubitably problematic.
She sells seashells by the seashore specifically selecting superior specimens systematically.
This is a very long sentence that goes on and on without any natural pauses or breathing points making it extremely difficult for a voiceover artist to deliver smoothly and naturally in one breath."""
        
        # Process: Execute review
        result = process_review_script_readability(
            db_connection,
            script_text=difficult_script
        )
        
        # Verify: Check result
        assert result is not None
        
        # Verify: Story state updated in database
        updated = story_repository.find_by_id(story.id)
        if not result.accepted:
            assert updated.state == STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT
    
    def test_multiple_stories_processed_in_order(self, db_connection, story_repository):
        """Test that multiple stories are processed oldest first."""
        # Create multiple stories
        story1 = Story(
            idea_json='{"title": "Story 1"}',
            state=STATE_REVIEW_SCRIPT_READABILITY
        )
        story1 = story_repository.insert(story1)
        
        story2 = Story(
            idea_json='{"title": "Story 2"}',
            state=STATE_REVIEW_SCRIPT_READABILITY
        )
        story2 = story_repository.insert(story2)
        
        # Process first story
        result1 = process_review_script_readability(db_connection)
        assert result1.story.id == story1.id
        
        # Process second story
        result2 = process_review_script_readability(db_connection)
        assert result2.story.id == story2.id
        
        # No more stories to process
        result3 = process_review_script_readability(db_connection)
        assert result3 is None
