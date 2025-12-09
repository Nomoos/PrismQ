"""Tests for Idea model."""

from datetime import datetime

import pytest

from src.idea import ContentGenre, Idea, IdeaStatus


class TestIdeaBasic:
    """Test basic Idea functionality."""

    def test_create_basic_idea(self):
        """Test creating a basic Idea instance."""
        idea = Idea(
            title="Test Idea",
            concept="Test concept for validation",
        )

        assert idea.title == "Test Idea"
        assert idea.concept == "Test concept for validation"
        assert idea.synopsis == ""
        assert idea.story_premise == ""
        assert idea.purpose == ""
        assert idea.emotional_quality == ""
        assert idea.target_audience == ""
        assert idea.target_demographics == {}
        assert idea.target_platforms == []
        assert idea.target_formats == []
        assert idea.genre == ContentGenre.OTHER
        assert idea.style == ""
        assert idea.keywords == []
        assert idea.themes == []
        assert idea.character_notes == ""
        assert idea.setting_notes == ""
        assert idea.tone_guidance == ""
        assert idea.length_target == ""
        assert idea.outline == ""
        assert idea.skeleton == ""
        assert idea.potential_scores == {}
        assert idea.inspiration_ids == []
        assert idea.metadata == {}
        assert idea.version == 1
        assert idea.status == IdeaStatus.DRAFT
        assert idea.notes == ""
        assert idea.created_at is not None
        assert idea.updated_at is not None
        assert idea.created_by is None

    def test_create_with_all_fields(self):
        """Test creating Idea with all fields for universal content generation."""
        target_demographics = {"age_range": "18-35", "interests": "technology,science"}
        potential_scores = {"platform:youtube": 85, "region:us": 90}
        inspiration_ids = ["insp-1", "insp-2"]
        metadata = {"key": "value"}

        idea = Idea(
            title="Complete Idea",
            concept="Full concept",
            synopsis="A short synopsis",
            story_premise="Story premise for AI",
            purpose="Test purpose",
            emotional_quality="exciting, innovative",
            target_audience="Tech enthusiasts",
            target_demographics=target_demographics,
            target_platforms=["youtube", "tiktok", "podcast"],
            target_formats=["text", "audio", "video"],
            genre=ContentGenre.TECHNOLOGY,
            style="educational",
            keywords=["tech", "innovation", "tutorial"],
            themes=["innovation", "education"],
            character_notes="Expert hosts",
            setting_notes="Modern tech spaces",
            tone_guidance="Engaging and accessible",
            length_target="15-20 minutes",
            outline="1. Intro\n2. Main Content\n3. Conclusion",
            skeleton="Hook → Teach → Practice → Review",
            potential_scores=potential_scores,
            inspiration_ids=inspiration_ids,
            metadata=metadata,
            version=2,
            status=IdeaStatus.VALIDATED,
            notes="Test notes",
            created_by="test-user",
        )

        assert idea.title == "Complete Idea"
        assert idea.concept == "Full concept"
        assert idea.synopsis == "A short synopsis"
        assert idea.story_premise == "Story premise for AI"
        assert idea.purpose == "Test purpose"
        assert idea.emotional_quality == "exciting, innovative"
        assert idea.target_audience == "Tech enthusiasts"
        assert idea.target_demographics == target_demographics
        assert idea.target_platforms == ["youtube", "tiktok", "podcast"]
        assert idea.target_formats == ["text", "audio", "video"]
        assert idea.genre == ContentGenre.TECHNOLOGY
        assert idea.style == "educational"
        assert idea.keywords == ["tech", "innovation", "tutorial"]
        assert idea.outline == "1. Intro\n2. Main Content\n3. Conclusion"
        assert idea.skeleton == "Hook → Teach → Practice → Review"
        assert idea.potential_scores == potential_scores
        assert idea.inspiration_ids == inspiration_ids
        assert idea.metadata == metadata
        assert idea.version == 2
        assert idea.status == IdeaStatus.VALIDATED
        assert idea.notes == "Test notes"
        assert idea.created_by == "test-user"

    def test_create_idea_without_inspirations(self):
        """Test creating an Idea without IdeaInspiration sources."""
        idea = Idea(
            title="Manual Idea",
            concept="Manually created without sources",
            keywords=["manual", "standalone"],
            outline="Custom outline",
            skeleton="Custom skeleton",
        )

        assert idea.title == "Manual Idea"
        assert idea.concept == "Manually created without sources"
        assert idea.keywords == ["manual", "standalone"]
        assert idea.outline == "Custom outline"
        assert idea.skeleton == "Custom skeleton"
        assert idea.inspiration_ids == []  # No inspirations
        assert idea.status == IdeaStatus.DRAFT

    def test_timestamps_auto_generated(self):
        """Test that timestamps are automatically generated."""
        idea = Idea(title="Timestamp Test", concept="Testing auto timestamps")

        assert idea.created_at is not None
        assert idea.updated_at is not None

        # Verify ISO format
        try:
            datetime.fromisoformat(idea.created_at)
            datetime.fromisoformat(idea.updated_at)
        except ValueError:
            pytest.fail("Timestamps should be in ISO format")

    def test_ai_generation_fields(self):
        """Test AI generation support fields."""
        idea = Idea(
            title="Complex Story Idea",
            concept="Multi-layered narrative",
            synopsis="A short version of the story in 2-3 paragraphs for quick AI context",
            story_premise="Deep story premise providing AI with narrative foundation",
            themes=["redemption", "identity", "technology"],
            character_notes="Protagonist: Tech detective with dark past. Antagonist: AI mastermind",
            setting_notes="Near-future cyberpunk city, underground hacker networks",
            tone_guidance="Start mysterious, build tension, maintain hope, end with twist",
            length_target="Feature length, 90-120 minutes",
        )

        assert (
            idea.synopsis == "A short version of the story in 2-3 paragraphs for quick AI context"
        )
        assert idea.story_premise == "Deep story premise providing AI with narrative foundation"
        assert len(idea.themes) == 3
        assert "redemption" in idea.themes
        assert idea.character_notes.startswith("Protagonist:")
        assert idea.setting_notes.startswith("Near-future")
        assert "tension" in idea.tone_guidance
        assert "90-120 minutes" in idea.length_target


class TestIdeaSerialization:
    """Test serialization and deserialization."""

    def test_to_dict(self):
        """Test converting Idea to dictionary."""
        idea = Idea(
            title="Test Idea",
            concept="Test concept",
            target_platforms=["youtube", "medium"],
            target_formats=["video", "text"],
            genre=ContentGenre.DOCUMENTARY,
            status=IdeaStatus.DRAFT,
            inspiration_ids=["insp-1", "insp-2"],
        )

        data = idea.to_dict()

        assert isinstance(data, dict)
        assert data["title"] == "Test Idea"
        assert data["concept"] == "Test concept"
        assert data["target_platforms"] == ["youtube", "medium"]
        assert data["target_formats"] == ["video", "text"]
        assert data["genre"] == "documentary"  # Converted to string
        assert data["status"] == "draft"  # Converted to string
        assert data["inspiration_ids"] == ["insp-1", "insp-2"]
        assert data["version"] == 1

    def test_from_dict(self):
        """Test creating Idea from dictionary."""
        data = {
            "title": "Dict Idea",
            "concept": "From dictionary",
            "purpose": "Testing",
            "target_platforms": ["tiktok", "instagram"],
            "target_formats": ["video"],
            "genre": "entertainment",
            "status": "validated",
            "inspiration_ids": ["id-1"],
            "version": 3,
        }

        idea = Idea.from_dict(data)

        assert idea.title == "Dict Idea"
        assert idea.concept == "From dictionary"
        assert idea.purpose == "Testing"
        assert idea.target_platforms == ["tiktok", "instagram"]
        assert idea.target_formats == ["video"]
        assert idea.genre == ContentGenre.ENTERTAINMENT
        assert idea.status == IdeaStatus.VALIDATED
        assert idea.inspiration_ids == ["id-1"]
        assert idea.version == 3

    def test_from_dict_with_invalid_enum(self):
        """Test from_dict handles invalid enum values gracefully."""
        data = {
            "title": "Test",
            "concept": "Test",
            "target_platforms": ["invalid_platform"],
            "target_formats": ["text"],
            "genre": "invalid_genre",
            "status": "invalid_status",
        }

        idea = Idea.from_dict(data)

        # Should fall back to defaults for enums
        assert idea.target_platforms == ["invalid_platform"]  # Lists are kept as-is
        assert idea.target_formats == ["text"]
        assert idea.genre == ContentGenre.OTHER
        assert idea.status == IdeaStatus.DRAFT

    def test_roundtrip_serialization(self):
        """Test that to_dict -> from_dict preserves data."""
        original = Idea(
            title="Roundtrip Test",
            concept="Testing serialization",
            purpose="Validate data preservation",
            emotional_quality="analytical",
            target_audience="Developers",
            target_demographics={"age": "25-40"},
            target_platforms=["podcast", "youtube"],
            target_formats=["audio", "video"],
            genre=ContentGenre.TECHNOLOGY,
            style="conversational",
            keywords=["test", "serialization", "roundtrip"],
            themes=["technology", "testing"],
            outline="Test outline structure",
            skeleton="Test skeleton framework",
            potential_scores={"us": 85},
            inspiration_ids=["a", "b"],
            metadata={"key": "value"},
            version=5,
            status=IdeaStatus.APPROVED,
            notes="Test notes",
            created_by="tester",
        )

        # Roundtrip
        data = original.to_dict()
        restored = Idea.from_dict(data)

        # Compare key fields
        assert restored.title == original.title
        assert restored.concept == original.concept
        assert restored.purpose == original.purpose
        assert restored.emotional_quality == original.emotional_quality
        assert restored.target_audience == original.target_audience
        assert restored.target_demographics == original.target_demographics
        assert restored.target_platforms == original.target_platforms
        assert restored.target_formats == original.target_formats
        assert restored.genre == original.genre
        assert restored.style == original.style
        assert restored.keywords == original.keywords
        assert restored.outline == original.outline
        assert restored.skeleton == original.skeleton
        assert restored.potential_scores == original.potential_scores
        assert restored.inspiration_ids == original.inspiration_ids
        assert restored.metadata == original.metadata
        assert restored.version == original.version
        assert restored.status == original.status
        assert restored.notes == original.notes
        assert restored.created_by == original.created_by


class TestIdeaFromInspirations:
    """Test creating Ideas from IdeaInspiration instances."""

    def test_from_inspirations_basic(self):
        """Test basic creation from inspirations."""

        # Mock IdeaInspiration objects
        class MockInspiration:
            def __init__(self, source_id):
                self.source_id = source_id
                self.contextual_category_scores = {}

        inspirations = [
            MockInspiration("insp-1"),
            MockInspiration("insp-2"),
            MockInspiration("insp-3"),
        ]

        idea = Idea.from_inspirations(
            inspirations=inspirations,
            title="Fused Idea",
            concept="Combined from multiple sources",
            purpose="Test fusion",
            target_platforms=["youtube", "tiktok"],
            target_formats=["video"],
            genre=ContentGenre.DOCUMENTARY,
        )

        assert idea.title == "Fused Idea"
        assert idea.concept == "Combined from multiple sources"
        assert idea.purpose == "Test fusion"
        assert idea.target_platforms == ["youtube", "tiktok"]
        assert idea.target_formats == ["video"]
        assert idea.genre == ContentGenre.DOCUMENTARY
        assert len(idea.inspiration_ids) == 3
        assert "insp-1" in idea.inspiration_ids
        assert "insp-2" in idea.inspiration_ids
        assert "insp-3" in idea.inspiration_ids

    def test_from_inspirations_with_scores(self):
        """Test that potential scores are aggregated from inspirations."""

        class MockInspiration:
            def __init__(self, source_id, scores):
                self.source_id = source_id
                self.contextual_category_scores = scores
                self.keywords = []

        inspirations = [
            MockInspiration("insp-1", {"region:us": 80, "age:18-24": 70}),
            MockInspiration("insp-2", {"region:us": 90, "age:25-34": 85}),
            MockInspiration("insp-3", {"region:uk": 75}),
        ]

        idea = Idea.from_inspirations(
            inspirations=inspirations, title="Scored Idea", concept="With aggregated scores"
        )

        # Should aggregate scores
        assert len(idea.potential_scores) > 0
        assert "region:us" in idea.potential_scores
        # US should be averaged: (80 + 90) / 2 = 85
        assert idea.potential_scores["region:us"] == 85

    def test_from_inspirations_with_keywords(self):
        """Test that keywords are aggregated from inspirations."""

        class MockInspiration:
            def __init__(self, source_id, keywords):
                self.source_id = source_id
                self.keywords = keywords
                self.contextual_category_scores = {}

        inspirations = [
            MockInspiration("insp-1", ["mystery", "crime", "investigation"]),
            MockInspiration("insp-2", ["crime", "thriller", "suspense"]),
            MockInspiration("insp-3", ["mystery", "detective"]),
        ]

        idea = Idea.from_inspirations(
            inspirations=inspirations, title="Keyword Test", concept="Testing keyword aggregation"
        )

        # Should aggregate and deduplicate keywords
        assert "mystery" in idea.keywords
        assert "crime" in idea.keywords
        assert "investigation" in idea.keywords
        assert "thriller" in idea.keywords
        assert "suspense" in idea.keywords
        assert "detective" in idea.keywords
        # No duplicates
        assert idea.keywords.count("mystery") == 1
        assert idea.keywords.count("crime") == 1

    def test_from_inspirations_with_created_by(self):
        """Test from_inspirations with creator tracking."""

        class MockInspiration:
            def __init__(self, source_id):
                self.source_id = source_id
                self.contextual_category_scores = {}

        inspirations = [MockInspiration("insp-1")]

        idea = Idea.from_inspirations(
            inspirations=inspirations,
            title="Tracked Idea",
            concept="With creator",
            created_by="AI-Agent-007",
        )

        assert idea.created_by == "AI-Agent-007"


class TestIdeaVersioning:
    """Test version management functionality."""

    def test_create_new_version(self):
        """Test creating a new version of an idea."""
        original = Idea(
            title="Original", concept="Original concept", version=1, status=IdeaStatus.DRAFT
        )

        updated = original.create_new_version(
            concept="Updated concept", status=IdeaStatus.VALIDATED
        )

        assert updated.title == "Original"  # Unchanged
        assert updated.concept == "Updated concept"  # Updated
        assert updated.version == 2  # Incremented
        assert updated.status == IdeaStatus.VALIDATED  # Updated
        assert original.version == 1  # Original unchanged

    def test_version_increments(self):
        """Test that versions increment correctly."""
        idea = Idea(title="Test", concept="Test", version=5)

        v6 = idea.create_new_version()
        v7 = v6.create_new_version()
        v8 = v7.create_new_version()

        assert idea.version == 5
        assert v6.version == 6
        assert v7.version == 7
        assert v8.version == 8

    def test_updated_at_changes(self):
        """Test that updated_at timestamp changes with new version."""
        import time

        original = Idea(title="Test", concept="Test")
        original_timestamp = original.updated_at

        # Small delay to ensure different timestamp
        time.sleep(0.01)

        updated = original.create_new_version(concept="Updated")

        assert updated.updated_at != original_timestamp


class TestIdeaEnums:
    """Test enum functionality."""

    def test_idea_status_values(self):
        """Test IdeaStatus enum values."""
        assert IdeaStatus.DRAFT.value == "draft"
        assert IdeaStatus.VALIDATED.value == "validated"
        assert IdeaStatus.APPROVED.value == "approved"
        assert IdeaStatus.IN_PRODUCTION.value == "in_production"
        assert IdeaStatus.ARCHIVED.value == "archived"

    def test_content_genre_values(self):
        """Test ContentGenre enum values."""
        assert ContentGenre.TRUE_CRIME.value == "true_crime"
        assert ContentGenre.MYSTERY.value == "mystery"
        assert ContentGenre.HORROR.value == "horror"
        assert ContentGenre.DOCUMENTARY.value == "documentary"
        assert ContentGenre.EDUCATIONAL.value == "educational"
        assert ContentGenre.OTHER.value == "other"


class TestIdeaRepresentation:
    """Test string representation."""

    def test_repr(self):
        """Test __repr__ method."""
        idea = Idea(
            title="A Very Long Title That Should Be Truncated In The Repr",
            concept="Test",
            version=3,
            status=IdeaStatus.VALIDATED,
            inspiration_ids=["a", "b", "c"],
        )

        repr_str = repr(idea)

        assert "Idea(" in repr_str
        assert "version=3" in repr_str
        assert "status=validated" in repr_str
        assert "inspirations=3 sources" in repr_str
        # Title should be truncated
        assert len(repr_str) < 200
