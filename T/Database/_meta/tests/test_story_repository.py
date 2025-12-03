"""Tests for StoryRepository.

Tests cover:
- CRUD operations (Insert + Read + Update)
- State-based queries
- find_next_for_processing method for story selection logic
"""

import pytest
import sqlite3
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path for proper imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from T.Database.models.story import Story
from T.Database.models.script import Script
from T.Database.models.title import Title
from T.Database.models.review import Review
from T.Database.repositories.story_repository import StoryRepository
from T.Database.repositories.script_repository import ScriptRepository
from T.Database.repositories.title_repository import TitleRepository
from T.Database.repositories.review_repository import ReviewRepository


@pytest.fixture
def db_connection():
    """Create in-memory SQLite database with all required tables."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    
    # Create Story table
    conn.execute("""
        CREATE TABLE Story (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id TEXT NULL,
            idea_json TEXT NULL,
            title_id INTEGER NULL,
            script_id INTEGER NULL,
            state TEXT NOT NULL DEFAULT 'CREATED',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    
    # Create Review table
    conn.execute("""
        CREATE TABLE Review (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
            created_at TEXT NOT NULL
        )
    """)
    
    # Create Title table
    conn.execute("""
        CREATE TABLE Title (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            version INTEGER NOT NULL CHECK (version >= 0),
            text TEXT NOT NULL,
            review_id INTEGER NULL,
            created_at TEXT NOT NULL,
            UNIQUE(story_id, version),
            FOREIGN KEY (story_id) REFERENCES Story(id),
            FOREIGN KEY (review_id) REFERENCES Review(id)
        )
    """)
    
    # Create Script table
    conn.execute("""
        CREATE TABLE Script (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            version INTEGER NOT NULL CHECK (version >= 0),
            text TEXT NOT NULL,
            review_id INTEGER NULL,
            created_at TEXT NOT NULL,
            UNIQUE(story_id, version),
            FOREIGN KEY (story_id) REFERENCES Story(id),
            FOREIGN KEY (review_id) REFERENCES Review(id)
        )
    """)
    
    conn.commit()
    
    yield conn
    conn.close()


@pytest.fixture
def story_repo(db_connection):
    """Create StoryRepository instance."""
    return StoryRepository(db_connection)


@pytest.fixture
def script_repo(db_connection):
    """Create ScriptRepository instance."""
    return ScriptRepository(db_connection)


@pytest.fixture
def title_repo(db_connection):
    """Create TitleRepository instance."""
    return TitleRepository(db_connection)


@pytest.fixture
def review_repo(db_connection):
    """Create ReviewRepository instance."""
    return ReviewRepository(db_connection)


class TestStoryRepositoryBasicOperations:
    """Basic CRUD tests for StoryRepository."""
    
    def test_insert_story(self, story_repo):
        """Test inserting a new story."""
        story = Story(
            idea_id="1",
            idea_json='{"title": "Test"}',
            state="CREATED"
        )
        saved = story_repo.insert(story)
        
        assert saved.id is not None
        assert saved.id > 0
        assert saved.idea_id == "1"
        assert saved.state == "CREATED"
    
    def test_find_by_id(self, story_repo):
        """Test finding story by ID."""
        story = Story(idea_id="1", state="CREATED")
        saved = story_repo.insert(story)
        
        found = story_repo.find_by_id(saved.id)
        
        assert found is not None
        assert found.id == saved.id
    
    def test_find_by_state(self, story_repo):
        """Test finding stories by state."""
        story_repo.insert(Story(idea_id="1", state="STATE_A"))
        story_repo.insert(Story(idea_id="2", state="STATE_A"))
        story_repo.insert(Story(idea_id="3", state="STATE_B"))
        
        stories = story_repo.find_by_state("STATE_A")
        
        assert len(stories) == 2
    
    def test_update_story_state(self, story_repo):
        """Test updating story state."""
        story = Story(idea_id="1", state="CREATED")
        saved = story_repo.insert(story)
        
        saved.state = "PROCESSING"
        story_repo.update(saved)
        
        found = story_repo.find_by_id(saved.id)
        assert found.state == "PROCESSING"


class TestFindNextForProcessingBasic:
    """Basic tests for find_next_for_processing method."""
    
    def test_no_stories_returns_none(self, story_repo):
        """Test that no matching stories returns None."""
        result = story_repo.find_next_for_processing("PrismQ.T.Script.From.Idea.Title")
        assert result is None
    
    def test_no_matching_state_returns_none(self, story_repo):
        """Test that no stories with matching state returns None."""
        story_repo.insert(Story(idea_id="1", state="DIFFERENT_STATE"))
        
        result = story_repo.find_next_for_processing("PrismQ.T.Script.From.Idea.Title")
        assert result is None
    
    def test_finds_story_with_matching_state(self, story_repo):
        """Test finding story with matching state."""
        state = "PrismQ.T.Script.From.Idea.Title"
        story = Story(idea_id="1", state=state)
        saved = story_repo.insert(story)
        
        result = story_repo.find_next_for_processing(state)
        
        assert result is not None
        assert result.id == saved.id
    
    def test_returns_only_one_story(self, story_repo):
        """Test that only one story is returned."""
        state = "PrismQ.T.Script.From.Idea.Title"
        story_repo.insert(Story(idea_id="1", state=state))
        story_repo.insert(Story(idea_id="2", state=state))
        story_repo.insert(Story(idea_id="3", state=state))
        
        result = story_repo.find_next_for_processing(state)
        
        assert result is not None
        # Should return exactly one result


class TestFindNextForProcessingVersionPriority:
    """Tests for version-based priority in find_next_for_processing."""
    
    def test_script_module_selects_lowest_script_version(
        self, story_repo, script_repo
    ):
        """Test script module selects story with lowest script version."""
        state = "PrismQ.T.Script.From.Idea.Title"
        
        # Create stories with different script versions
        story1 = story_repo.insert(Story(idea_id="1", state=state))
        story2 = story_repo.insert(Story(idea_id="2", state=state))
        story3 = story_repo.insert(Story(idea_id="3", state=state))
        
        # Story 1 has script version 5
        for v in range(6):
            script_repo.insert(Script(story_id=story1.id, version=v, text="text"))
        
        # Story 2 has script version 2
        for v in range(3):
            script_repo.insert(Script(story_id=story2.id, version=v, text="text"))
        
        # Story 3 has script version 0 (no scripts = 0)
        # No scripts added
        
        result = story_repo.find_next_for_processing(state)
        
        assert result is not None
        assert result.id == story3.id  # Lowest version (0)
    
    def test_title_module_selects_lowest_title_version(
        self, story_repo, title_repo
    ):
        """Test title module selects story with lowest title version."""
        state = "PrismQ.T.Title.From.Script.Review"
        
        # Create stories with different title versions
        story1 = story_repo.insert(Story(idea_id="1", state=state))
        story2 = story_repo.insert(Story(idea_id="2", state=state))
        story3 = story_repo.insert(Story(idea_id="3", state=state))
        
        # Story 1 has title version 3
        for v in range(4):
            title_repo.insert(Title(story_id=story1.id, version=v, text="title"))
        
        # Story 2 has title version 1
        for v in range(2):
            title_repo.insert(Title(story_id=story2.id, version=v, text="title"))
        
        # Story 3 has title version 0 (no titles = 0)
        # No titles added
        
        result = story_repo.find_next_for_processing(state)
        
        assert result is not None
        assert result.id == story3.id  # Lowest version (0)


class TestFindNextForProcessingScorePriority:
    """Tests for score-based priority in find_next_for_processing."""
    
    def test_higher_score_has_priority_when_same_version(
        self, story_repo, script_repo, title_repo, review_repo
    ):
        """Test that higher score is prioritized when versions are equal."""
        state = "PrismQ.T.Script.From.Idea.Title"
        
        # Create stories (all will have version 0 - no scripts)
        story1 = story_repo.insert(Story(idea_id="1", state=state))
        story2 = story_repo.insert(Story(idea_id="2", state=state))
        story3 = story_repo.insert(Story(idea_id="3", state=state))
        
        # Add titles with reviews to story1 (score 50)
        review1 = review_repo.insert(Review(text="Review 1", score=50))
        title_repo.insert(Title(story_id=story1.id, version=0, text="title", review_id=review1.id))
        
        # Add titles with reviews to story2 (score 90)
        review2 = review_repo.insert(Review(text="Review 2", score=90))
        title_repo.insert(Title(story_id=story2.id, version=0, text="title", review_id=review2.id))
        
        # Add titles with reviews to story3 (score 30)
        review3 = review_repo.insert(Review(text="Review 3", score=30))
        title_repo.insert(Title(story_id=story3.id, version=0, text="title", review_id=review3.id))
        
        result = story_repo.find_next_for_processing(state)
        
        assert result is not None
        assert result.id == story2.id  # Highest score (90/2 = 45)
    
    def test_average_of_script_and_title_scores(
        self, story_repo, script_repo, title_repo, review_repo
    ):
        """Test story score is average of script and title review scores."""
        state = "PrismQ.T.Script.From.Idea.Title"
        
        story1 = story_repo.insert(Story(idea_id="1", state=state))
        story2 = story_repo.insert(Story(idea_id="2", state=state))
        
        # Story 1: title score 60, script score 40 -> avg = 50
        title_review1 = review_repo.insert(Review(text="Title review", score=60))
        script_review1 = review_repo.insert(Review(text="Script review", score=40))
        title_repo.insert(Title(story_id=story1.id, version=0, text="title", review_id=title_review1.id))
        script_repo.insert(Script(story_id=story1.id, version=0, text="script", review_id=script_review1.id))
        
        # Story 2: title score 80, script score 80 -> avg = 80
        title_review2 = review_repo.insert(Review(text="Title review", score=80))
        script_review2 = review_repo.insert(Review(text="Script review", score=80))
        title_repo.insert(Title(story_id=story2.id, version=0, text="title", review_id=title_review2.id))
        script_repo.insert(Script(story_id=story2.id, version=0, text="script", review_id=script_review2.id))
        
        result = story_repo.find_next_for_processing(state)
        
        assert result is not None
        assert result.id == story2.id  # Higher average score


class TestFindNextForProcessingCreatedAtPriority:
    """Tests for created_at-based priority in find_next_for_processing."""
    
    def test_oldest_story_selected_when_version_and_score_equal(
        self, story_repo
    ):
        """Test oldest story is selected when version and score are equal."""
        state = "PrismQ.T.Script.From.Idea.Title"
        
        # Create stories with different creation times
        now = datetime.now()
        
        story1 = Story(
            idea_id="1",
            state=state,
            created_at=now - timedelta(hours=1)  # 1 hour ago
        )
        story2 = Story(
            idea_id="2",
            state=state,
            created_at=now - timedelta(hours=3)  # 3 hours ago (oldest)
        )
        story3 = Story(
            idea_id="3",
            state=state,
            created_at=now - timedelta(hours=2)  # 2 hours ago
        )
        
        saved1 = story_repo.insert(story1)
        saved2 = story_repo.insert(story2)
        saved3 = story_repo.insert(story3)
        
        result = story_repo.find_next_for_processing(state)
        
        assert result is not None
        assert result.id == saved2.id  # Oldest story


class TestFindNextForProcessingSortingOrder:
    """Tests for complete sorting order: version -> score -> created_at."""
    
    def test_full_sorting_order(
        self, story_repo, script_repo, title_repo, review_repo
    ):
        """Test complete sorting: version ASC, score DESC, created_at ASC."""
        state = "PrismQ.T.Script.From.Idea.Title"
        now = datetime.now()
        
        # Story 1: version 2, score 90, older
        story1 = story_repo.insert(Story(
            idea_id="1",
            state=state,
            created_at=now - timedelta(hours=5)
        ))
        for v in range(3):
            script_repo.insert(Script(story_id=story1.id, version=v, text="text"))
        review1 = review_repo.insert(Review(text="Review", score=90))
        title_repo.insert(Title(story_id=story1.id, version=0, text="title", review_id=review1.id))
        
        # Story 2: version 1, score 50, older
        story2 = story_repo.insert(Story(
            idea_id="2",
            state=state,
            created_at=now - timedelta(hours=4)
        ))
        for v in range(2):
            script_repo.insert(Script(story_id=story2.id, version=v, text="text"))
        review2 = review_repo.insert(Review(text="Review", score=50))
        title_repo.insert(Title(story_id=story2.id, version=0, text="title", review_id=review2.id))
        
        # Story 3: version 1, score 80, newer - should be selected
        # (same version as story2 but higher score)
        story3 = story_repo.insert(Story(
            idea_id="3",
            state=state,
            created_at=now - timedelta(hours=1)
        ))
        for v in range(2):
            script_repo.insert(Script(story_id=story3.id, version=v, text="text"))
        review3 = review_repo.insert(Review(text="Review", score=80))
        title_repo.insert(Title(story_id=story3.id, version=0, text="title", review_id=review3.id))
        
        result = story_repo.find_next_for_processing(state)
        
        assert result is not None
        # Story3 wins: same version as story2 (1), but higher score (80 vs 50)
        assert result.id == story3.id
    
    def test_version_takes_priority_over_score(
        self, story_repo, script_repo, title_repo, review_repo
    ):
        """Test that lower version wins over higher score."""
        state = "PrismQ.T.Script.From.Idea.Title"
        
        # Story 1: version 3, score 100
        story1 = story_repo.insert(Story(idea_id="1", state=state))
        for v in range(4):
            script_repo.insert(Script(story_id=story1.id, version=v, text="text"))
        review1 = review_repo.insert(Review(text="Review", score=100))
        title_repo.insert(Title(story_id=story1.id, version=0, text="title", review_id=review1.id))
        
        # Story 2: version 0, score 10 - should win (lower version)
        story2 = story_repo.insert(Story(idea_id="2", state=state))
        # No scripts = version 0
        review2 = review_repo.insert(Review(text="Review", score=10))
        title_repo.insert(Title(story_id=story2.id, version=0, text="title", review_id=review2.id))
        
        result = story_repo.find_next_for_processing(state)
        
        assert result is not None
        assert result.id == story2.id  # Lower version wins
    
    def test_score_takes_priority_over_created_at(
        self, story_repo, script_repo, title_repo, review_repo
    ):
        """Test that higher score wins over older created_at."""
        state = "PrismQ.T.Script.From.Idea.Title"
        now = datetime.now()
        
        # Story 1: score 30, older
        story1 = story_repo.insert(Story(
            idea_id="1",
            state=state,
            created_at=now - timedelta(hours=10)
        ))
        review1 = review_repo.insert(Review(text="Review", score=30))
        title_repo.insert(Title(story_id=story1.id, version=0, text="title", review_id=review1.id))
        
        # Story 2: score 90, newer - should win (higher score)
        story2 = story_repo.insert(Story(
            idea_id="2",
            state=state,
            created_at=now - timedelta(hours=1)
        ))
        review2 = review_repo.insert(Review(text="Review", score=90))
        title_repo.insert(Title(story_id=story2.id, version=0, text="title", review_id=review2.id))
        
        result = story_repo.find_next_for_processing(state)
        
        assert result is not None
        assert result.id == story2.id  # Higher score wins


class TestFindNextForProcessingEdgeCases:
    """Edge case tests for find_next_for_processing."""
    
    def test_story_with_no_reviews_has_zero_score(
        self, story_repo, title_repo
    ):
        """Test that stories without reviews have score of 0."""
        state = "PrismQ.T.Script.From.Idea.Title"
        
        # Story without reviews
        story1 = story_repo.insert(Story(idea_id="1", state=state))
        title_repo.insert(Title(story_id=story1.id, version=0, text="title"))
        
        result = story_repo.find_next_for_processing(state)
        
        assert result is not None
        assert result.id == story1.id
    
    def test_uses_latest_version_review_score(
        self, story_repo, title_repo, review_repo
    ):
        """Test that latest version's review score is used."""
        state = "PrismQ.T.Title.From.Script"
        
        story1 = story_repo.insert(Story(idea_id="1", state=state))
        story2 = story_repo.insert(Story(idea_id="2", state=state))
        
        # Story 1: version 0 has score 100, version 1 has score 20
        # Latest (v1) score should be used
        review1_v0 = review_repo.insert(Review(text="Review v0", score=100))
        review1_v1 = review_repo.insert(Review(text="Review v1", score=20))
        title_repo.insert(Title(story_id=story1.id, version=0, text="title", review_id=review1_v0.id))
        title_repo.insert(Title(story_id=story1.id, version=1, text="title", review_id=review1_v1.id))
        
        # Story 2: version 0 has score 50
        review2 = review_repo.insert(Review(text="Review", score=50))
        title_repo.insert(Title(story_id=story2.id, version=0, text="title", review_id=review2.id))
        
        result = story_repo.find_next_for_processing(state)
        
        assert result is not None
        # Story2 wins because story1's latest score (20) is lower than story2's (50)
        assert result.id == story2.id
    
    def test_module_detection_script_keyword(self, story_repo):
        """Test that .Script. in state triggers script version sorting."""
        # This is implicitly tested by other tests, but here's an explicit check
        state_with_script = "PrismQ.T.Script.From.Idea.Title"
        state_without_script = "PrismQ.T.Review.Title.Readability"
        
        # Verify the method recognizes script modules
        story1 = story_repo.insert(Story(idea_id="1", state=state_with_script))
        result1 = story_repo.find_next_for_processing(state_with_script)
        assert result1 is not None
        
        story2 = story_repo.insert(Story(idea_id="2", state=state_without_script))
        result2 = story_repo.find_next_for_processing(state_without_script)
        assert result2 is not None
    
    def test_module_detection_title_from_script(self, story_repo, title_repo):
        """Test that PrismQ.T.Title.From.Script correctly uses title version."""
        # State pattern: PrismQ.T.Title.From.Script.Review
        # This is a TITLE module (output is Title), so should sort by title version
        state = "PrismQ.T.Title.From.Script.Review"
        
        story1 = story_repo.insert(Story(idea_id="1", state=state))
        story2 = story_repo.insert(Story(idea_id="2", state=state))
        story3 = story_repo.insert(Story(idea_id="3", state=state))
        
        # Story 1 has title version 3
        for v in range(4):
            title_repo.insert(Title(story_id=story1.id, version=v, text="title"))
        
        # Story 2 has title version 1
        for v in range(2):
            title_repo.insert(Title(story_id=story2.id, version=v, text="title"))
        
        # Story 3 has title version 0 (no titles = 0)
        # No titles added
        
        result = story_repo.find_next_for_processing(state)
        
        assert result is not None
        assert result.id == story3.id  # Lowest title version (0)


class TestFindNextForProcessingReviewModules:
    """Tests for Review module types (PrismQ.T.Review.Script.* and PrismQ.T.Review.Title.*)."""
    
    def test_review_script_module_uses_script_version(
        self, story_repo, script_repo
    ):
        """Test PrismQ.T.Review.Script.* uses script version for sorting."""
        state = "PrismQ.T.Review.Script.Grammar"
        
        story1 = story_repo.insert(Story(idea_id="1", state=state))
        story2 = story_repo.insert(Story(idea_id="2", state=state))
        story3 = story_repo.insert(Story(idea_id="3", state=state))
        
        # Story 1 has script version 5
        for v in range(6):
            script_repo.insert(Script(story_id=story1.id, version=v, text="text"))
        
        # Story 2 has script version 2
        for v in range(3):
            script_repo.insert(Script(story_id=story2.id, version=v, text="text"))
        
        # Story 3 has script version 0 (no scripts = 0)
        # No scripts added
        
        result = story_repo.find_next_for_processing(state)
        
        assert result is not None
        assert result.id == story3.id  # Lowest script version (0)
    
    def test_review_title_module_uses_title_version(
        self, story_repo, title_repo
    ):
        """Test PrismQ.T.Review.Title.* uses title version for sorting."""
        state = "PrismQ.T.Review.Title.Readability"
        
        story1 = story_repo.insert(Story(idea_id="1", state=state))
        story2 = story_repo.insert(Story(idea_id="2", state=state))
        story3 = story_repo.insert(Story(idea_id="3", state=state))
        
        # Story 1 has title version 4
        for v in range(5):
            title_repo.insert(Title(story_id=story1.id, version=v, text="title"))
        
        # Story 2 has title version 1
        for v in range(2):
            title_repo.insert(Title(story_id=story2.id, version=v, text="title"))
        
        # Story 3 has title version 0 (no titles = 0)
        # No titles added
        
        result = story_repo.find_next_for_processing(state)
        
        assert result is not None
        assert result.id == story3.id  # Lowest title version (0)
    
    def test_review_script_tone_module(self, story_repo, script_repo):
        """Test PrismQ.T.Review.Script.Tone uses script version."""
        state = "PrismQ.T.Review.Script.Tone"
        
        story1 = story_repo.insert(Story(idea_id="1", state=state))
        story2 = story_repo.insert(Story(idea_id="2", state=state))
        
        # Story 1 has script version 3
        for v in range(4):
            script_repo.insert(Script(story_id=story1.id, version=v, text="text"))
        
        # Story 2 has script version 0
        # No scripts added
        
        result = story_repo.find_next_for_processing(state)
        
        assert result is not None
        assert result.id == story2.id  # Lowest script version (0)
    
    def test_review_script_editing_module(self, story_repo, script_repo):
        """Test PrismQ.T.Review.Script.Editing uses script version."""
        state = "PrismQ.T.Review.Script.Editing"
        
        story1 = story_repo.insert(Story(idea_id="1", state=state))
        story2 = story_repo.insert(Story(idea_id="2", state=state))
        
        # Story 1 has script version 1
        for v in range(2):
            script_repo.insert(Script(story_id=story1.id, version=v, text="text"))
        
        # Story 2 has script version 0
        # No scripts added
        
        result = story_repo.find_next_for_processing(state)
        
        assert result is not None
        assert result.id == story2.id  # Lowest script version (0)


class TestFindNextForProcessingStoryModules:
    """Tests for Story module types (PrismQ.T.Story.*)."""
    
    def test_story_review_module_uses_max_of_both_versions(
        self, story_repo, script_repo, title_repo
    ):
        """Test PrismQ.T.Story.Review uses max of script and title versions."""
        state = "PrismQ.T.Story.Review"
        
        story1 = story_repo.insert(Story(idea_id="1", state=state))
        story2 = story_repo.insert(Story(idea_id="2", state=state))
        story3 = story_repo.insert(Story(idea_id="3", state=state))
        
        # Story 1: script v3, title v1 -> max = 3
        for v in range(4):
            script_repo.insert(Script(story_id=story1.id, version=v, text="text"))
        for v in range(2):
            title_repo.insert(Title(story_id=story1.id, version=v, text="title"))
        
        # Story 2: script v1, title v4 -> max = 4
        for v in range(2):
            script_repo.insert(Script(story_id=story2.id, version=v, text="text"))
        for v in range(5):
            title_repo.insert(Title(story_id=story2.id, version=v, text="title"))
        
        # Story 3: script v0, title v0 -> max = 0 (no content)
        # No scripts or titles added
        
        result = story_repo.find_next_for_processing(state)
        
        assert result is not None
        assert result.id == story3.id  # Lowest max version (0)
    
    def test_story_polish_module_uses_max_of_both_versions(
        self, story_repo, script_repo, title_repo
    ):
        """Test PrismQ.T.Story.Polish uses max of script and title versions."""
        state = "PrismQ.T.Story.Polish"
        
        story1 = story_repo.insert(Story(idea_id="1", state=state))
        story2 = story_repo.insert(Story(idea_id="2", state=state))
        
        # Story 1: script v2, title v2 -> max = 2
        for v in range(3):
            script_repo.insert(Script(story_id=story1.id, version=v, text="text"))
        for v in range(3):
            title_repo.insert(Title(story_id=story1.id, version=v, text="title"))
        
        # Story 2: script v0, title v1 -> max = 1
        for v in range(1):
            script_repo.insert(Script(story_id=story2.id, version=v, text="text"))
        for v in range(2):
            title_repo.insert(Title(story_id=story2.id, version=v, text="title"))
        
        result = story_repo.find_next_for_processing(state)
        
        assert result is not None
        assert result.id == story2.id  # Lowest max version (1)
    
    def test_story_from_idea_module(self, story_repo, script_repo, title_repo):
        """Test PrismQ.T.Story.From.Idea uses max of both versions."""
        state = "PrismQ.T.Story.From.Idea"
        
        story1 = story_repo.insert(Story(idea_id="1", state=state))
        story2 = story_repo.insert(Story(idea_id="2", state=state))
        
        # Story 1 has versions: script v1, title v2 -> max = 2
        script_repo.insert(Script(story_id=story1.id, version=0, text="text"))
        script_repo.insert(Script(story_id=story1.id, version=1, text="text"))
        title_repo.insert(Title(story_id=story1.id, version=0, text="title"))
        title_repo.insert(Title(story_id=story1.id, version=1, text="title"))
        title_repo.insert(Title(story_id=story1.id, version=2, text="title"))
        
        # Story 2 has versions: script v0, title v0 -> max = 0
        script_repo.insert(Script(story_id=story2.id, version=0, text="text"))
        title_repo.insert(Title(story_id=story2.id, version=0, text="title"))
        
        result = story_repo.find_next_for_processing(state)
        
        assert result is not None
        assert result.id == story2.id  # Lowest max version (0)


class TestModuleTypeDetection:
    """Tests for _get_module_type helper method."""
    
    def test_script_module_types(self, story_repo):
        """Test detection of Script module types."""
        assert story_repo._get_module_type("PrismQ.T.Script.From.Idea.Title") == "script"
        assert story_repo._get_module_type("PrismQ.T.Script.From.Title.Review.Script") == "script"
    
    def test_title_module_types(self, story_repo):
        """Test detection of Title module types."""
        assert story_repo._get_module_type("PrismQ.T.Title.From.Idea") == "title"
        assert story_repo._get_module_type("PrismQ.T.Title.From.Script.Review.Title") == "title"
    
    def test_review_script_module_types(self, story_repo):
        """Test detection of Review.Script module types."""
        assert story_repo._get_module_type("PrismQ.T.Review.Script.Grammar") == "review_script"
        assert story_repo._get_module_type("PrismQ.T.Review.Script.Tone") == "review_script"
        assert story_repo._get_module_type("PrismQ.T.Review.Script.Content") == "review_script"
        assert story_repo._get_module_type("PrismQ.T.Review.Script.Consistency") == "review_script"
        assert story_repo._get_module_type("PrismQ.T.Review.Script.Editing") == "review_script"
        assert story_repo._get_module_type("PrismQ.T.Review.Script.Readability") == "review_script"
    
    def test_review_title_module_types(self, story_repo):
        """Test detection of Review.Title module types."""
        assert story_repo._get_module_type("PrismQ.T.Review.Title.Readability") == "review_title"
        assert story_repo._get_module_type("PrismQ.T.Review.Title.By.Script") == "review_title"
        assert story_repo._get_module_type("PrismQ.T.Review.Title.By.Script.Idea") == "review_title"
    
    def test_story_module_types(self, story_repo):
        """Test detection of Story module types."""
        assert story_repo._get_module_type("PrismQ.T.Story.Review") == "story"
        assert story_repo._get_module_type("PrismQ.T.Story.Polish") == "story"
        assert story_repo._get_module_type("PrismQ.T.Story.From.Idea") == "story"
    
    def test_unknown_module_types(self, story_repo):
        """Test detection of unknown module types."""
        assert story_repo._get_module_type("PrismQ.T.Publishing") == "unknown"
        assert story_repo._get_module_type("PrismQ.T.Idea.Creation") == "unknown"
        assert story_repo._get_module_type("InvalidState") == "unknown"


class TestPreviewNextForProcessing:
    """Tests for preview_next_for_processing method."""
    
    def test_preview_returns_none_when_no_stories(self, story_repo, capsys):
        """Test preview returns None and prints message when no stories."""
        state = "PrismQ.T.Script.From.Idea.Title"
        
        result = story_repo.preview_next_for_processing(state, wait_for_confirm=False)
        
        assert result is None
        captured = capsys.readouterr()
        assert "No stories found for processing" in captured.out
        assert state in captured.out
    
    def test_preview_displays_story_info(self, story_repo, capsys):
        """Test preview displays story information."""
        state = "PrismQ.T.Script.From.Idea.Title"
        story = story_repo.insert(Story(
            idea_id="1",
            idea_json='{"title": "Test Story", "concept": "Test concept"}',
            state=state
        ))
        
        result = story_repo.preview_next_for_processing(state, wait_for_confirm=False)
        
        assert result is not None
        assert result.id == story.id
        
        captured = capsys.readouterr()
        assert "SELECTED STORY FOR PROCESSING" in captured.out
        assert f"Story ID: {story.id}" in captured.out
        assert f"State: {state}" in captured.out
        assert "Test Story" in captured.out
    
    def test_preview_returns_selected_story(self, story_repo):
        """Test preview returns the correctly selected story."""
        state = "PrismQ.T.Script.From.Idea.Title"
        story1 = story_repo.insert(Story(idea_id="1", state=state))
        story2 = story_repo.insert(Story(idea_id="2", state="OTHER_STATE"))
        
        result = story_repo.preview_next_for_processing(state, wait_for_confirm=False)
        
        assert result is not None
        assert result.id == story1.id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
