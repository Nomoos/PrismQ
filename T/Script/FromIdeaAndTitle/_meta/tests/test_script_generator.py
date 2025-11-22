"""Tests for Script Generator module."""

import sys
import os
import pytest

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../Model/src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../Model'))

from script_generator import (
    ScriptGenerator,
    ScriptGeneratorConfig,
    ScriptV1,
    ScriptSection,
    ScriptStructure,
    PlatformTarget,
    ScriptTone
)

# Import Idea model for testing
try:
    from idea import Idea, ContentGenre, IdeaStatus
except ImportError:
    # Create mock Idea class for testing if import fails
    from dataclasses import dataclass
    from typing import List
    from enum import Enum
    
    class ContentGenre(Enum):
        MYSTERY = "mystery"
        HORROR = "horror"
        EDUCATIONAL = "educational"
        OTHER = "other"
    
    class IdeaStatus(Enum):
        DRAFT = "draft"
    
    @dataclass
    class Idea:
        id: str = "test-idea-001"
        title: str = "Test Idea"
        concept: str = "A test concept"
        premise: str = "This is a test premise"
        hook: str = "What if this was just a test?"
        synopsis: str = "A comprehensive test synopsis explaining the concept"
        keywords: List[str] = None
        themes: List[str] = None
        genre: ContentGenre = ContentGenre.OTHER
        status: IdeaStatus = IdeaStatus.DRAFT
        target_platforms: List[str] = None
        target_formats: List[str] = None
        
        def __post_init__(self):
            if self.keywords is None:
                self.keywords = ["test", "example"]
            if self.themes is None:
                self.themes = ["testing", "demonstration"]
            if self.target_platforms is None:
                self.target_platforms = ["youtube"]
            if self.target_formats is None:
                self.target_formats = ["video"]


class TestScriptGeneratorBasics:
    """Basic tests for ScriptGenerator."""
    
    def test_generator_initialization(self):
        """Test that generator can be initialized."""
        generator = ScriptGenerator()
        assert generator is not None
        assert isinstance(generator.config, ScriptGeneratorConfig)
    
    def test_generator_with_custom_config(self):
        """Test generator with custom configuration."""
        config = ScriptGeneratorConfig(
            platform_target=PlatformTarget.YOUTUBE_SHORT,
            target_duration_seconds=60,
            tone=ScriptTone.MYSTERIOUS
        )
        generator = ScriptGenerator(config)
        assert generator.config.platform_target == PlatformTarget.YOUTUBE_SHORT
        assert generator.config.target_duration_seconds == 60
        assert generator.config.tone == ScriptTone.MYSTERIOUS
    
    def test_generate_script_v1_basic(self):
        """Test generating a basic script v1."""
        generator = ScriptGenerator()
        idea = Idea(
            id="test-001",
            title="The Mystery of the Abandoned House",
            concept="A house with time-loop paranormal activity",
            premise="Every night at midnight, strange things happen in this house",
            hook="What if time doesn't work the same way inside?",
            synopsis="A detailed exploration of a mysterious abandoned house with paranormal activity",
            themes=["mystery", "paranormal"],
            keywords=["house", "mystery", "time-loop"],
            genre=ContentGenre.MYSTERY
        )
        title = "The Mystery of the Abandoned House"
        
        script = generator.generate_script_v1(idea, title)
        
        assert script is not None
        assert isinstance(script, ScriptV1)
        assert script.title == title
        assert script.idea_id == "test-001"
        assert script.version == 1
        assert len(script.sections) > 0
        assert script.full_text is not None
        assert len(script.full_text) > 0
    
    def test_generate_script_validates_inputs(self):
        """Test that generator validates inputs."""
        generator = ScriptGenerator()
        
        # Test None idea
        with pytest.raises(ValueError, match="Idea cannot be None"):
            generator.generate_script_v1(None, "Test Title")
        
        # Test empty title
        idea = Idea()
        with pytest.raises(ValueError, match="Title cannot be empty"):
            generator.generate_script_v1(idea, "")
        
        # Test whitespace title
        with pytest.raises(ValueError, match="Title cannot be empty"):
            generator.generate_script_v1(idea, "   ")


class TestScriptStructures:
    """Test different script structures."""
    
    def test_hook_deliver_cta_structure(self):
        """Test hook-deliver-cta structure."""
        config = ScriptGeneratorConfig(
            structure_type=ScriptStructure.HOOK_DELIVER_CTA,
            target_duration_seconds=90
        )
        generator = ScriptGenerator(config)
        idea = Idea(
            title="Test Topic",
            concept="Test concept",
            premise="Test premise"
        )
        
        script = generator.generate_script_v1(idea, "Test Title")
        
        assert script.structure_type == ScriptStructure.HOOK_DELIVER_CTA
        assert len(script.sections) == 3  # intro, body, conclusion
        assert script.sections[0].section_type == "introduction"
        assert script.sections[1].section_type == "body"
        assert script.sections[2].section_type == "conclusion"
    
    def test_three_act_structure(self):
        """Test three-act structure."""
        config = ScriptGeneratorConfig(
            structure_type=ScriptStructure.THREE_ACT,
            target_duration_seconds=90
        )
        generator = ScriptGenerator(config)
        idea = Idea()
        
        script = generator.generate_script_v1(idea, "Test Title")
        
        assert script.structure_type == ScriptStructure.THREE_ACT
        assert len(script.sections) == 3
    
    def test_problem_solution_structure(self):
        """Test problem-solution structure."""
        config = ScriptGeneratorConfig(
            structure_type=ScriptStructure.PROBLEM_SOLUTION,
            target_duration_seconds=90
        )
        generator = ScriptGenerator(config)
        idea = Idea()
        
        script = generator.generate_script_v1(idea, "Test Title")
        
        assert script.structure_type == ScriptStructure.PROBLEM_SOLUTION
        assert len(script.sections) == 3
    
    def test_story_structure(self):
        """Test story structure."""
        config = ScriptGeneratorConfig(
            structure_type=ScriptStructure.STORY,
            target_duration_seconds=90
        )
        generator = ScriptGenerator(config)
        idea = Idea()
        
        script = generator.generate_script_v1(idea, "Test Title")
        
        assert script.structure_type == ScriptStructure.STORY
        assert len(script.sections) == 3


class TestPlatformTargets:
    """Test different platform targets."""
    
    def test_youtube_short_target(self):
        """Test YouTube short optimization."""
        config = ScriptGeneratorConfig(
            platform_target=PlatformTarget.YOUTUBE_SHORT,
            target_duration_seconds=60
        )
        generator = ScriptGenerator(config)
        idea = Idea()
        
        script = generator.generate_script_v1(idea, "Short Video Title")
        
        assert script.platform_target == PlatformTarget.YOUTUBE_SHORT
        assert script.total_duration_seconds <= 70  # Allow some variance
    
    def test_youtube_medium_target(self):
        """Test YouTube medium duration."""
        config = ScriptGeneratorConfig(
            platform_target=PlatformTarget.YOUTUBE_MEDIUM,
            target_duration_seconds=120
        )
        generator = ScriptGenerator(config)
        idea = Idea()
        
        script = generator.generate_script_v1(idea, "Medium Video Title")
        
        assert script.platform_target == PlatformTarget.YOUTUBE_MEDIUM
        assert 100 <= script.total_duration_seconds <= 140
    
    def test_custom_duration(self):
        """Test custom duration targeting."""
        config = ScriptGeneratorConfig(
            target_duration_seconds=45
        )
        generator = ScriptGenerator(config)
        idea = Idea()
        
        script = generator.generate_script_v1(idea, "Custom Duration")
        
        # Should be reasonably close to target
        assert 35 <= script.total_duration_seconds <= 55


class TestScriptSections:
    """Test script section functionality."""
    
    def test_sections_have_content(self):
        """Test that all sections have content."""
        generator = ScriptGenerator()
        idea = Idea(
            concept="Test concept with detailed information",
            premise="A premise that explains the idea",
            synopsis="A comprehensive synopsis explaining everything"
        )
        
        script = generator.generate_script_v1(idea, "Test Title")
        
        for section in script.sections:
            assert section.content is not None
            assert len(section.content) > 0
            assert section.estimated_duration_seconds > 0
            assert section.purpose is not None
    
    def test_sections_have_appropriate_durations(self):
        """Test that section durations are reasonable."""
        config = ScriptGeneratorConfig(target_duration_seconds=90)
        generator = ScriptGenerator(config)
        idea = Idea()
        
        script = generator.generate_script_v1(idea, "Test Title")
        
        # Introduction should be shorter than body
        intro = script.get_section("introduction")
        body = script.get_section("body")
        
        assert intro is not None
        assert body is not None
        assert intro.estimated_duration_seconds < body.estimated_duration_seconds
    
    def test_get_section_method(self):
        """Test get_section method."""
        generator = ScriptGenerator()
        idea = Idea()
        
        script = generator.generate_script_v1(idea, "Test Title")
        
        intro = script.get_section("introduction")
        assert intro is not None
        assert intro.section_type == "introduction"
        
        body = script.get_section("body")
        assert body is not None
        assert body.section_type == "body"
        
        nonexistent = script.get_section("nonexistent")
        assert nonexistent is None


class TestScriptMetadata:
    """Test script metadata and output."""
    
    def test_script_has_metadata(self):
        """Test that script includes metadata."""
        generator = ScriptGenerator()
        idea = Idea(
            id="test-123",
            concept="Test concept",
            genre=ContentGenre.EDUCATIONAL
        )
        
        script = generator.generate_script_v1(idea, "Educational Title")
        
        assert script.metadata is not None
        assert "idea_concept" in script.metadata
        assert "idea_genre" in script.metadata
        assert "generation_config" in script.metadata
    
    def test_script_to_dict(self):
        """Test converting script to dictionary."""
        generator = ScriptGenerator()
        idea = Idea()
        
        script = generator.generate_script_v1(idea, "Test Title")
        script_dict = script.to_dict()
        
        assert isinstance(script_dict, dict)
        assert "script_id" in script_dict
        assert "title" in script_dict
        assert "full_text" in script_dict
        assert "sections" in script_dict
        assert "version" in script_dict
        assert script_dict["version"] == 1
    
    def test_script_has_timestamps(self):
        """Test that script includes creation timestamp."""
        generator = ScriptGenerator()
        idea = Idea()
        
        script = generator.generate_script_v1(idea, "Test Title")
        
        assert script.created_at is not None
        assert len(script.created_at) > 0
        # Should be in ISO format
        assert "T" in script.created_at or "-" in script.created_at


class TestConfigurationOverrides:
    """Test configuration overrides via kwargs."""
    
    def test_override_platform_target(self):
        """Test overriding platform target."""
        generator = ScriptGenerator()
        idea = Idea()
        
        script = generator.generate_script_v1(
            idea,
            "Test Title",
            platform_target=PlatformTarget.TIKTOK
        )
        
        assert script.platform_target == PlatformTarget.TIKTOK
    
    def test_override_duration(self):
        """Test overriding target duration."""
        generator = ScriptGenerator()
        idea = Idea()
        
        script = generator.generate_script_v1(
            idea,
            "Test Title",
            target_duration_seconds=150
        )
        
        # Should be close to 150 seconds
        assert 140 <= script.total_duration_seconds <= 160
    
    def test_override_structure(self):
        """Test overriding structure type."""
        generator = ScriptGenerator()
        idea = Idea()
        
        script = generator.generate_script_v1(
            idea,
            "Test Title",
            structure_type=ScriptStructure.PROBLEM_SOLUTION
        )
        
        assert script.structure_type == ScriptStructure.PROBLEM_SOLUTION
    
    def test_custom_script_id(self):
        """Test providing custom script ID."""
        generator = ScriptGenerator()
        idea = Idea()
        custom_id = "custom-script-123"
        
        script = generator.generate_script_v1(
            idea,
            "Test Title",
            script_id=custom_id
        )
        
        assert script.script_id == custom_id


class TestContentGeneration:
    """Test content generation quality."""
    
    def test_uses_idea_content(self):
        """Test that generated script uses idea content."""
        generator = ScriptGenerator()
        idea = Idea(
            title="Unique Idea Title XYZ123",
            concept="Very specific unique concept ABC789",
            premise="Distinctive premise DEF456",
            hook="Memorable hook GHI321"
        )
        
        script = generator.generate_script_v1(idea, "Test Title")
        
        # Script should reference or use idea content
        # Check metadata contains idea info
        assert script.metadata["idea_concept"] == idea.concept
    
    def test_full_text_assembly(self):
        """Test that full text is properly assembled."""
        generator = ScriptGenerator()
        idea = Idea()
        
        script = generator.generate_script_v1(idea, "Test Title")
        
        # Full text should contain content from all sections
        for section in script.sections:
            # At least part of the section content should be in full text
            assert section.content[:50] in script.full_text or \
                   section.content in script.full_text
    
    def test_respects_tone_setting(self):
        """Test that tone setting is applied."""
        config = ScriptGeneratorConfig(tone=ScriptTone.EDUCATIONAL)
        generator = ScriptGenerator(config)
        idea = Idea()
        
        script = generator.generate_script_v1(idea, "Test Title")
        
        # Check that tone is recorded in metadata
        assert script.metadata["generation_config"]["tone"] == ScriptTone.EDUCATIONAL
    
    def test_include_cta_setting(self):
        """Test include_cta setting."""
        config = ScriptGeneratorConfig(include_cta=False)
        generator = ScriptGenerator(config)
        idea = Idea()
        
        script = generator.generate_script_v1(idea, "Test Title")
        
        # Should still have sections but conclusion may be shorter
        assert len(script.sections) >= 2


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_minimal_idea(self):
        """Test with minimal idea information."""
        generator = ScriptGenerator()
        idea = Idea(
            title="Minimal",
            concept="Basic concept"
        )
        
        script = generator.generate_script_v1(idea, "Minimal Title")
        
        assert script is not None
        assert len(script.full_text) > 0
        assert len(script.sections) > 0
    
    def test_long_title(self):
        """Test with very long title."""
        generator = ScriptGenerator()
        idea = Idea()
        long_title = "A Very Long Title " * 10
        
        script = generator.generate_script_v1(idea, long_title)
        
        assert script is not None
        assert script.title == long_title
    
    def test_very_short_duration(self):
        """Test with very short target duration."""
        config = ScriptGeneratorConfig(target_duration_seconds=10)
        generator = ScriptGenerator(config)
        idea = Idea()
        
        script = generator.generate_script_v1(idea, "Short")
        
        assert script is not None
        # Should handle short duration gracefully
        assert script.total_duration_seconds > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
