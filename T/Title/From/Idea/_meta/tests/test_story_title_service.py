"""Tests for Story and Title creation service from Idea.

This module tests the StoryTitleService functionality which creates
10 Story objects with FK reference to Idea and generates the first
Title (v0) for each Story.
"""

import os
import sqlite3
import sys
from pathlib import Path

import pytest

# Set up paths before any other imports
_test_dir = Path(__file__).parent
_project_root = _test_dir.parent.parent.parent.parent.parent.parent
_idea_model_path = _project_root / "T" / "Idea" / "Model" / "src"
_src_path = _test_dir.parent.parent / "src"

# Add all required paths
sys.path.insert(0, str(_project_root))
sys.path.insert(0, str(_idea_model_path))
sys.path.insert(0, str(_src_path))

from story_title_service import (
    StoryTitleResult,
    StoryTitleService,
    create_stories_from_idea,
)
from title_generator import TitleConfig

from idea import ContentGenre, Idea, IdeaStatus

# Import database models
from Model.Database.models.story import Story, StoryState
from Model.Database.models.title import Title


class TestStoryTitleService:
    """Tests for StoryTitleService class."""

    def test_create_10_stories_from_idea(self):
        """Test creating exactly 10 stories from an idea."""
        idea = Idea(
            title="The Future of AI",
            concept="An exploration of artificial intelligence trends",
            status=IdeaStatus.DRAFT,
        )

        service = StoryTitleService()
        result = service.create_stories_with_titles(idea)

        assert result.count == 10
        assert len(result.stories) == 10
        assert len(result.titles) == 10
        assert len(result.title_variants) == 10

    def test_stories_reference_idea(self):
        """Test that all stories reference the same idea."""
        idea = Idea(
            title="Digital Privacy",
            concept="Understanding online privacy concerns",
            status=IdeaStatus.DRAFT,
        )

        result = create_stories_from_idea(idea)

        # All stories should have the same idea_id
        idea_ids = [story.idea_id for story in result.stories]
        assert len(set(idea_ids)) == 1  # All same
        assert result.idea_id == idea_ids[0]

    def test_explicit_idea_id(self):
        """Test using explicit idea_id."""
        idea = Idea(title="Test Idea", concept="Test concept", status=IdeaStatus.DRAFT)

        result = create_stories_from_idea(idea, idea_id="custom-idea-123")

        assert result.idea_id == "custom-idea-123"
        for story in result.stories:
            assert story.idea_id == "custom-idea-123"

    def test_each_story_has_title_v0(self):
        """Test that each story gets a Title v0."""
        idea = Idea(
            title="Machine Learning Basics",
            concept="Introduction to ML concepts",
            status=IdeaStatus.DRAFT,
        )

        result = create_stories_from_idea(idea)

        for story, title in result.get_story_title_pairs():
            assert title.story_id == story.id
            assert title.version == 0
            assert len(title.text) > 0

    def test_stories_in_content_from_idea_title_state(self):
        """Test that all stories are transitioned to SCRIPT_FROM_IDEA_TITLE state."""
        idea = Idea(
            title="Blockchain Technology",
            concept="Understanding decentralized systems",
            status=IdeaStatus.DRAFT,
        )

        result = create_stories_from_idea(idea)

        for story in result.stories:
            assert story.state == StoryState.SCRIPT_FROM_IDEA_TITLE.value

    def test_invalid_idea_none(self):
        """Test error handling with None idea."""
        service = StoryTitleService()

        with pytest.raises(ValueError, match="Idea cannot be None"):
            service.create_stories_with_titles(None)

    def test_invalid_idea_empty(self):
        """Test error handling with empty idea."""
        idea = Idea(title="", concept="", status=IdeaStatus.DRAFT)

        service = StoryTitleService()

        with pytest.raises(ValueError, match="must have at least a title or concept"):
            service.create_stories_with_titles(idea)

    def test_title_variants_diverse(self):
        """Test that 10 different title variants are generated."""
        idea = Idea(
            title="Python Programming", concept="Learning Python language", status=IdeaStatus.DRAFT
        )

        result = create_stories_from_idea(idea)

        # Check all variants have different styles (10 unique styles)
        styles = [v.style for v in result.title_variants]
        assert len(set(styles)) == 10  # All 10 variants should have unique styles
        # Verify some expected styles are present (doesn't require exact set)
        assert "direct" in styles
        assert "question" in styles
        assert "how-to" in styles


class TestStoryTitleServiceWithDatabase:
    """Tests for StoryTitleService with database persistence."""

    @pytest.fixture
    def db_connection(self):
        """Create in-memory SQLite database for testing."""
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        yield conn
        conn.close()

    def test_persistence_to_database(self, db_connection):
        """Test that stories and titles are persisted to database."""
        service = StoryTitleService(db_connection)
        service.ensure_tables_exist()

        idea = Idea(
            title="Test Persistence",
            concept="Testing database persistence",
            status=IdeaStatus.DRAFT,
        )

        result = service.create_stories_with_titles(idea)

        # Verify stories in database
        cursor = db_connection.execute("SELECT COUNT(*) FROM Story")
        story_count = cursor.fetchone()[0]
        assert story_count == 10

        # Verify titles in database
        cursor = db_connection.execute("SELECT COUNT(*) FROM Title")
        title_count = cursor.fetchone()[0]
        assert title_count == 10

    def test_story_title_fk_relationship(self, db_connection):
        """Test FK relationship between Story and Title."""
        service = StoryTitleService(db_connection)
        service.ensure_tables_exist()

        idea = Idea(
            title="FK Test", concept="Testing foreign key relationship", status=IdeaStatus.DRAFT
        )

        result = service.create_stories_with_titles(idea)

        # Each title should reference its story
        for story, title in result.get_story_title_pairs():
            cursor = db_connection.execute("SELECT story_id FROM Title WHERE id = ?", (title.id,))
            row = cursor.fetchone()
            assert row["story_id"] == story.id

    def test_story_state_persisted(self, db_connection):
        """Test that story state is correctly persisted."""
        service = StoryTitleService(db_connection)
        service.ensure_tables_exist()

        idea = Idea(
            title="State Test", concept="Testing state persistence", status=IdeaStatus.DRAFT
        )

        result = service.create_stories_with_titles(idea)

        # All stories should have SCRIPT_FROM_IDEA_TITLE state in database
        cursor = db_connection.execute(
            "SELECT state FROM Story WHERE state = ?", (StoryState.SCRIPT_FROM_IDEA_TITLE.value,)
        )
        rows = cursor.fetchall()
        assert len(rows) == 10

    def test_multiple_ideas_separate_stories(self, db_connection):
        """Test that different ideas create separate story sets."""
        service = StoryTitleService(db_connection)
        service.ensure_tables_exist()

        idea1 = Idea(title="First Idea", concept="First concept", status=IdeaStatus.DRAFT)
        idea2 = Idea(title="Second Idea", concept="Second concept", status=IdeaStatus.DRAFT)

        result1 = service.create_stories_with_titles(idea1)
        result2 = service.create_stories_with_titles(idea2)

        # Each idea should have its own set of stories
        assert result1.idea_id != result2.idea_id

        # Total 20 stories in database
        cursor = db_connection.execute("SELECT COUNT(*) FROM Story")
        total_stories = cursor.fetchone()[0]
        assert total_stories == 20

        # 10 stories for each idea
        cursor = db_connection.execute(
            "SELECT COUNT(*) FROM Story WHERE idea_id = ?", (result1.idea_id,)
        )
        idea1_stories = cursor.fetchone()[0]
        assert idea1_stories == 10

    def test_skip_if_exists_prevents_duplicates(self, db_connection):
        """Test that skip_if_exists prevents creating duplicate stories for same Idea."""
        service = StoryTitleService(db_connection)
        service.ensure_tables_exist()

        idea = Idea(
            title="Skip Test Idea", concept="Testing skip if exists", status=IdeaStatus.DRAFT
        )

        # First call should create stories
        result1 = service.create_stories_with_titles(idea)
        assert result1 is not None
        assert result1.count == 10

        # Second call with skip_if_exists=True (default) should return None
        result2 = service.create_stories_with_titles(idea)
        assert result2 is None

        # Total should still be 10 stories
        cursor = db_connection.execute("SELECT COUNT(*) FROM Story")
        total_stories = cursor.fetchone()[0]
        assert total_stories == 10

    def test_skip_if_exists_disabled_allows_duplicates(self, db_connection):
        """Test that skip_if_exists=False allows creating duplicate stories."""
        service = StoryTitleService(db_connection)
        service.ensure_tables_exist()

        idea = Idea(
            title="Duplicate Test Idea",
            concept="Testing skip if exists disabled",
            status=IdeaStatus.DRAFT,
        )

        # First call creates stories
        result1 = service.create_stories_with_titles(idea, skip_if_exists=False)
        assert result1 is not None
        assert result1.count == 10

        # Second call with skip_if_exists=False should also create stories
        result2 = service.create_stories_with_titles(idea, skip_if_exists=False)
        assert result2 is not None
        assert result2.count == 10

        # Total should be 20 stories
        cursor = db_connection.execute("SELECT COUNT(*) FROM Story")
        total_stories = cursor.fetchone()[0]
        assert total_stories == 20

    def test_idea_has_stories_method(self, db_connection):
        """Test the idea_has_stories method."""
        service = StoryTitleService(db_connection)
        service.ensure_tables_exist()

        idea = Idea(
            title="Has Stories Test", concept="Testing has stories method", status=IdeaStatus.DRAFT
        )

        # Before creating stories, should return False
        assert service.idea_has_stories(idea) == False

        # Create stories
        service.create_stories_with_titles(idea, skip_if_exists=False)

        # After creating stories, should return True
        assert service.idea_has_stories(idea) == True


class TestStoryTitleResult:
    """Tests for StoryTitleResult data class."""

    def test_count_property(self):
        """Test count property returns correct number."""
        result = StoryTitleResult(
            idea_id="test-id",
            stories=[Story(idea_id="test-id") for _ in range(5)],
            titles=[Title(story_id=i, version=0, text=f"Title {i}") for i in range(5)],
        )

        assert result.count == 5

    def test_get_story_title_pairs(self):
        """Test get_story_title_pairs returns correct pairs."""
        stories = [Story(idea_id="test", id=i) for i in range(3)]
        titles = [Title(story_id=i, version=0, text=f"Title {i}") for i in range(3)]

        result = StoryTitleResult(idea_id="test", stories=stories, titles=titles)

        pairs = result.get_story_title_pairs()
        assert len(pairs) == 3
        for i, (story, title) in enumerate(pairs):
            assert story.id == i
            assert title.story_id == i


class TestConvenienceFunction:
    """Tests for create_stories_from_idea convenience function."""

    def test_create_stories_from_idea(self):
        """Test convenience function creates stories correctly."""
        idea = Idea(
            title="Cloud Computing", concept="Understanding cloud services", status=IdeaStatus.DRAFT
        )

        result = create_stories_from_idea(idea)

        assert result.count == 10
        assert all(isinstance(s, Story) for s in result.stories)
        assert all(isinstance(t, Title) for t in result.titles)

    def test_with_custom_config(self):
        """Test convenience function with custom title config."""
        config = TitleConfig(num_variants=10, max_length=70)

        idea = Idea(
            title="Test with Config", concept="Testing configuration", status=IdeaStatus.DRAFT
        )

        result = create_stories_from_idea(idea, title_config=config)

        assert result.count == 10
        for title in result.titles:
            assert len(title.text) <= 70


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_idea_with_only_concept(self):
        """Test creating stories from idea with only concept."""
        idea = Idea(
            title="",
            concept="A comprehensive exploration of quantum computing",
            status=IdeaStatus.DRAFT,
        )

        result = create_stories_from_idea(idea)

        assert result.count == 10
        # ID should be derived from concept hash
        assert result.idea_id.startswith("idea-")

    def test_idea_with_unicode(self):
        """Test creating stories from idea with unicode characters."""
        idea = Idea(
            title="Technology & Innovation",
            concept="Exploring tech trends",
            status=IdeaStatus.DRAFT,
        )

        result = create_stories_from_idea(idea)

        assert result.count == 10
        assert all(s.state == StoryState.SCRIPT_FROM_IDEA_TITLE.value for s in result.stories)

    def test_very_long_title(self):
        """Test with very long idea title."""
        idea = Idea(
            title="A Very Long Title About The Future of Technology and Innovation " * 3,
            concept="Long title test",
            status=IdeaStatus.DRAFT,
        )

        result = create_stories_from_idea(idea)

        assert result.count == 10
        # Idea ID should be truncated
        assert len(result.idea_id) <= 50


class TestTitleSimilarity:
    """Tests for title similarity and uniqueness features."""

    def test_calculate_title_similarity_identical(self):
        """Test similarity between identical titles."""
        service = StoryTitleService()

        similarity = service.calculate_title_similarity("The Future of AI", "The Future of AI")

        assert similarity == 1.0

    def test_calculate_title_similarity_completely_different(self):
        """Test similarity between completely different titles."""
        service = StoryTitleService()

        similarity = service.calculate_title_similarity(
            "Quantum Computing Basics", "Music Streaming Apps"
        )

        # No common words, should be 0
        assert similarity == 0.0

    def test_calculate_title_similarity_partial_overlap(self):
        """Test similarity with partial word overlap."""
        service = StoryTitleService()

        similarity = service.calculate_title_similarity(
            "The Future of AI Technology", "The History of AI Technology"
        )

        # Words: the, future, of, ai, technology vs the, history, of, ai, technology
        # Intersection: the, of, ai, technology (4)
        # Union: the, future, of, ai, technology, history (6)
        # Jaccard: 4/6 = 0.667
        assert 0.6 < similarity < 0.7

    def test_calculate_title_similarity_case_insensitive(self):
        """Test that similarity is case insensitive."""
        service = StoryTitleService()

        similarity = service.calculate_title_similarity("The Future of AI", "THE FUTURE OF AI")

        assert similarity == 1.0

    def test_calculate_title_similarity_empty_strings(self):
        """Test similarity with empty strings."""
        service = StoryTitleService()

        assert service.calculate_title_similarity("", "") == 0.0
        assert service.calculate_title_similarity("Test", "") == 0.0
        assert service.calculate_title_similarity("", "Test") == 0.0


class TestTitleUniquenessWithDatabase:
    """Tests for title uniqueness checking with database."""

    @pytest.fixture
    def db_connection(self):
        """Create in-memory SQLite database for testing."""
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        yield conn
        conn.close()

    def test_get_sibling_stories(self, db_connection):
        """Test retrieving sibling stories from the same idea."""
        service = StoryTitleService(db_connection)
        service.ensure_tables_exist()

        idea = Idea(title="Test Idea", concept="Testing siblings", status=IdeaStatus.DRAFT)

        # Create stories from idea
        result = service.create_stories_with_titles(idea)

        # Get siblings for the first story
        first_story = result.stories[0]
        siblings = service.get_sibling_stories(first_story)

        # Should have 9 siblings (10 stories - 1 current)
        assert len(siblings) == 9

        # All siblings should have the same idea_id
        for sibling in siblings:
            assert sibling.idea_id == first_story.idea_id
            assert sibling.id != first_story.id

    def test_get_sibling_titles(self, db_connection):
        """Test retrieving titles from sibling stories."""
        service = StoryTitleService(db_connection)
        service.ensure_tables_exist()

        idea = Idea(title="Test Idea", concept="Testing sibling titles", status=IdeaStatus.DRAFT)

        # Create stories from idea
        result = service.create_stories_with_titles(idea)

        # Get sibling titles for the first story
        first_story = result.stories[0]
        sibling_titles = service.get_sibling_titles(first_story)

        # Should have 9 sibling titles (10 titles - 1 for current story)
        assert len(sibling_titles) == 9

    def test_check_title_uniqueness_unique(self, db_connection):
        """Test that a unique title passes uniqueness check."""
        service = StoryTitleService(db_connection)
        service.ensure_tables_exist()

        idea = Idea(title="Test Idea", concept="Testing uniqueness", status=IdeaStatus.DRAFT)

        result = service.create_stories_with_titles(idea)
        first_story = result.stories[0]

        # Check a completely different title
        is_unique, similar_titles = service.check_title_uniqueness(
            "Completely Different Title About Unrelated Topic", first_story
        )

        # Should be unique (no similar titles)
        assert is_unique is True
        assert len(similar_titles) == 0

    def test_select_best_title_with_variants(self, db_connection):
        """Test selecting best title from variants."""
        from title_generator import TitleVariant

        service = StoryTitleService(db_connection)
        service.ensure_tables_exist()

        idea = Idea(title="Test", concept="Testing best selection", status=IdeaStatus.DRAFT)

        result = service.create_stories_with_titles(idea)
        first_story = result.stories[0]

        # Create test variants
        variants = [
            TitleVariant(
                text="Option A Title", style="direct", length=14, keywords=["option"], score=0.8
            ),
            TitleVariant(
                text="Option B Title", style="question", length=14, keywords=["option"], score=0.85
            ),
            TitleVariant(
                text="Option C Title", style="how-to", length=14, keywords=["option"], score=0.9
            ),
        ]

        best, similar = service.select_best_title(variants, first_story)

        # Should select highest scoring variant (Option C with 0.9)
        assert best.text == "Option C Title"
        assert best.score == 0.9

    def test_select_best_title_skips_similar(self, db_connection):
        """Test that select_best_title skips similar titles and picks next best."""
        from title_generator import TitleVariant

        from Model.Database.models.title import Title
        from Model.Database.repositories.title_repository import TitleRepository

        service = StoryTitleService(db_connection)
        service.ensure_tables_exist()

        idea = Idea(title="Test", concept="Testing skip similar", status=IdeaStatus.DRAFT)

        result = service.create_stories_with_titles(idea)
        first_story = result.stories[0]
        second_story = result.stories[1]

        # Get existing title from first story (sibling of second)
        title_repo = TitleRepository(db_connection)
        existing_title = title_repo.find_by_story_id(first_story.id)[0]

        # Create variants where highest-scored is similar to existing sibling title
        variants = [
            TitleVariant(
                text="Completely Different Unique Title",
                style="direct",
                length=33,
                keywords=["different"],
                score=0.8,
            ),
            TitleVariant(
                text="Another Unique Option",
                style="question",
                length=21,
                keywords=["another"],
                score=0.85,
            ),
            TitleVariant(
                text=existing_title.text,
                style="how-to",
                length=len(existing_title.text),
                keywords=["test"],
                score=0.95,
            ),  # Highest score but identical to sibling
        ]

        best, similar = service.select_best_title(variants, second_story)

        # Should NOT select highest scoring variant because it's identical to sibling
        # Instead should select "Another Unique Option" (0.85) - second best that is unique
        assert best.text == "Another Unique Option"
        assert best.score == 0.85

    def test_select_best_title_fallback_when_all_similar(self, db_connection):
        """Test that select_best_title falls back to best when all are similar."""
        from title_generator import TitleVariant

        from Model.Database.models.title import Title
        from Model.Database.repositories.title_repository import TitleRepository

        service = StoryTitleService(db_connection)
        service.ensure_tables_exist()

        idea = Idea(title="Test", concept="Testing fallback", status=IdeaStatus.DRAFT)

        result = service.create_stories_with_titles(idea)
        first_story = result.stories[0]
        second_story = result.stories[1]

        # Get existing title from first story
        title_repo = TitleRepository(db_connection)
        existing_title = title_repo.find_by_story_id(first_story.id)[0]

        # All variants are similar to existing title (same words, different order)
        existing_words = existing_title.text.split()
        variants = [
            TitleVariant(
                text=existing_title.text,
                style="direct",
                length=len(existing_title.text),
                keywords=["test"],
                score=0.9,
            ),
            TitleVariant(
                text=existing_title.text,
                style="question",
                length=len(existing_title.text),
                keywords=["test"],
                score=0.85,
            ),
            TitleVariant(
                text=existing_title.text,
                style="how-to",
                length=len(existing_title.text),
                keywords=["test"],
                score=0.8,
            ),
        ]

        best, similar = service.select_best_title(variants, second_story)

        # Should fall back to highest scored since all are similar
        assert best.score == 0.9
