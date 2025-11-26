"""Tests for SimpleIdea model and prompt templates."""

import pytest
from datetime import datetime
from src.simple_idea import SimpleIdea, IdeaPromptTemplates, EXAMPLE_IDEAS


class TestSimpleIdeaBasic:
    """Test basic SimpleIdea functionality."""
    
    def test_create_basic_idea(self):
        """Test creating a basic SimpleIdea instance."""
        idea = SimpleIdea(text="Write a horror story about a haunted house.")
        
        assert idea.text == "Write a horror story about a haunted house."
        assert idea.version == 1
        assert idea.id is None
        assert idea.created_at is not None
    
    def test_create_with_all_fields(self):
        """Test creating SimpleIdea with all fields specified."""
        idea = SimpleIdea(
            id=42,
            text="Create an educational video about quantum computing.",
            version=3,
            created_at="2025-01-15T10:30:00"
        )
        
        assert idea.id == 42
        assert idea.text == "Create an educational video about quantum computing."
        assert idea.version == 3
        assert idea.created_at == "2025-01-15T10:30:00"
    
    def test_timestamps_auto_generated(self):
        """Test that timestamps are automatically generated."""
        idea = SimpleIdea(text="Test idea")
        
        assert idea.created_at is not None
        
        # Verify ISO format
        try:
            datetime.fromisoformat(idea.created_at)
        except ValueError:
            pytest.fail("Timestamp should be in ISO format")
    
    def test_default_version_is_one(self):
        """Test that default version is 1."""
        idea = SimpleIdea(text="Test idea")
        assert idea.version == 1
    
    def test_version_cannot_be_less_than_one(self):
        """Test that version is corrected if less than 1."""
        idea = SimpleIdea(text="Test idea", version=0)
        assert idea.version == 1
        
        idea2 = SimpleIdea(text="Test idea", version=-5)
        assert idea2.version == 1


class TestSimpleIdeaSerialization:
    """Test serialization and deserialization."""
    
    def test_to_dict(self):
        """Test converting SimpleIdea to dictionary."""
        idea = SimpleIdea(
            id=1,
            text="Write a mystery story.",
            version=2,
            created_at="2025-01-15T10:00:00"
        )
        
        data = idea.to_dict()
        
        assert isinstance(data, dict)
        assert data["id"] == 1
        assert data["text"] == "Write a mystery story."
        assert data["version"] == 2
        assert data["created_at"] == "2025-01-15T10:00:00"
    
    def test_from_dict(self):
        """Test creating SimpleIdea from dictionary."""
        data = {
            "id": 5,
            "text": "Create a documentary about climate change.",
            "version": 1,
            "created_at": "2025-01-15T12:00:00"
        }
        
        idea = SimpleIdea.from_dict(data)
        
        assert idea.id == 5
        assert idea.text == "Create a documentary about climate change."
        assert idea.version == 1
        assert idea.created_at == "2025-01-15T12:00:00"
    
    def test_from_dict_with_defaults(self):
        """Test from_dict with missing fields uses defaults."""
        data = {"text": "Minimal idea"}
        
        idea = SimpleIdea.from_dict(data)
        
        assert idea.text == "Minimal idea"
        assert idea.version == 1
        assert idea.id is None
        # created_at is set by __post_init__ if None from dict
        assert idea.created_at is not None
    
    def test_roundtrip_serialization(self):
        """Test that to_dict -> from_dict preserves data."""
        original = SimpleIdea(
            text="Write a story about time travel.",
            version=4,
        )
        
        # Roundtrip
        data = original.to_dict()
        restored = SimpleIdea.from_dict(data)
        
        assert restored.text == original.text
        assert restored.version == original.version
        assert restored.created_at == original.created_at


class TestSimpleIdeaVersioning:
    """Test version management functionality."""
    
    def test_create_new_version(self):
        """Test creating a new version of an idea."""
        original = SimpleIdea(
            text="Original idea text",
            version=1
        )
        
        updated = original.create_new_version("Updated idea text")
        
        assert updated.text == "Updated idea text"
        assert updated.version == 2
        assert updated.id is None  # New version gets new ID
        assert original.text == "Original idea text"  # Original unchanged
        assert original.version == 1
    
    def test_create_new_version_without_text_change(self):
        """Test creating new version without changing text."""
        original = SimpleIdea(text="Same text", version=3)
        
        updated = original.create_new_version()
        
        assert updated.text == "Same text"
        assert updated.version == 4
    
    def test_version_increments(self):
        """Test that versions increment correctly."""
        idea = SimpleIdea(text="Test", version=1)
        
        v2 = idea.create_new_version()
        v3 = v2.create_new_version()
        v4 = v3.create_new_version()
        
        assert idea.version == 1
        assert v2.version == 2
        assert v3.version == 3
        assert v4.version == 4


class TestSimpleIdeaRepresentation:
    """Test string representation."""
    
    def test_repr_short_text(self):
        """Test __repr__ with short text."""
        idea = SimpleIdea(id=1, text="Short text", version=2)
        
        repr_str = repr(idea)
        
        assert "SimpleIdea" in repr_str
        assert "id=1" in repr_str
        assert "version=2" in repr_str
        assert "Short text" in repr_str
    
    def test_repr_long_text_truncated(self):
        """Test __repr__ truncates long text."""
        long_text = "A" * 100
        idea = SimpleIdea(text=long_text, version=1)
        
        repr_str = repr(idea)
        
        assert "..." in repr_str
        assert len(repr_str) < 150


class TestIdeaPromptTemplates:
    """Test prompt template functionality."""
    
    def test_get_all_templates(self):
        """Test getting all available templates."""
        templates = IdeaPromptTemplates.get_all_templates()
        
        assert isinstance(templates, dict)
        assert len(templates) > 0
        assert "horror_story" in templates
        assert "educational_content" in templates
        assert "viral_short" in templates
    
    def test_get_template(self):
        """Test getting a specific template."""
        template = IdeaPromptTemplates.get_template("horror_story")
        
        assert isinstance(template, str)
        assert "{protagonist}" in template
        assert "{supernatural_element}" in template
        assert "{twist}" in template
    
    def test_get_template_not_found(self):
        """Test getting non-existent template raises error."""
        with pytest.raises(ValueError) as exc_info:
            IdeaPromptTemplates.get_template("non_existent_template")
        
        assert "not found" in str(exc_info.value)
    
    def test_format_template(self):
        """Test formatting a template with variables."""
        formatted = IdeaPromptTemplates.format_template(
            "horror_story",
            protagonist="a teenage girl",
            supernatural_element="hearing voices",
            twist="she's the ghost"
        )
        
        assert "a teenage girl" in formatted
        assert "hearing voices" in formatted
        assert "she's the ghost" in formatted
        assert "{protagonist}" not in formatted
    
    def test_list_template_names(self):
        """Test listing all template names."""
        names = IdeaPromptTemplates.list_template_names()
        
        assert isinstance(names, list)
        assert len(names) > 0
        assert "horror_story" in names
        assert "mystery_story" in names
    
    def test_get_template_variables(self):
        """Test getting variables from a template."""
        variables = IdeaPromptTemplates.get_template_variables("horror_story")
        
        assert isinstance(variables, list)
        assert "protagonist" in variables
        assert "supernatural_element" in variables
        assert "twist" in variables
    
    def test_simple_prompt_template(self):
        """Test the simple prompt template."""
        formatted = IdeaPromptTemplates.format_template(
            "simple_prompt",
            concept="A story about friendship"
        )
        
        assert formatted == "A story about friendship"
    
    def test_structured_idea_template(self):
        """Test the structured idea template."""
        formatted = IdeaPromptTemplates.format_template(
            "structured_idea",
            title="The Echo",
            concept="Girl hears future self",
            audience="Horror fans",
            message="Face your fears",
            format="Short video"
        )
        
        assert "Title: The Echo" in formatted
        assert "Concept: Girl hears future self" in formatted
        assert "Target Audience: Horror fans" in formatted


class TestSimpleIdeaFromTemplate:
    """Test creating SimpleIdea from templates."""
    
    def test_from_prompt_template(self):
        """Test creating SimpleIdea from a prompt template."""
        idea = SimpleIdea.from_prompt_template(
            "horror_story",
            protagonist="a young writer",
            supernatural_element="her novels coming true",
            twist="she wrote her own death"
        )
        
        assert "a young writer" in idea.text
        assert "her novels coming true" in idea.text
        assert "she wrote her own death" in idea.text
        assert idea.version == 1
    
    def test_from_prompt_template_not_found(self):
        """Test from_prompt_template with invalid template."""
        with pytest.raises(ValueError) as exc_info:
            SimpleIdea.from_prompt_template("invalid_template")
        
        assert "not found" in str(exc_info.value)
    
    def test_from_simple_prompt_template(self):
        """Test creating SimpleIdea from simple_prompt template."""
        idea = SimpleIdea.from_prompt_template(
            "simple_prompt",
            concept="Create a video about productivity"
        )
        
        assert idea.text == "Create a video about productivity"


class TestExampleIdeas:
    """Test the pre-defined example ideas."""
    
    def test_example_ideas_exist(self):
        """Test that example ideas are defined."""
        assert isinstance(EXAMPLE_IDEAS, list)
        assert len(EXAMPLE_IDEAS) > 0
    
    def test_example_ideas_are_valid(self):
        """Test that all example ideas are valid SimpleIdea instances."""
        for idea in EXAMPLE_IDEAS:
            assert isinstance(idea, SimpleIdea)
            assert idea.text is not None
            assert len(idea.text) > 0
            assert idea.version >= 1
    
    def test_example_ideas_have_content(self):
        """Test that example ideas have meaningful content."""
        for idea in EXAMPLE_IDEAS:
            # Each example should have at least 50 characters
            assert len(idea.text) >= 50
