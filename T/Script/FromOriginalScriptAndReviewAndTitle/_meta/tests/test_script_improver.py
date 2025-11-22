"""Tests for Script Improver module."""

import sys
import os
import pytest
from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../FromIdeaAndTitle/src'))

from script_improver import (
    ScriptImprover,
    ScriptImproverConfig,
    ScriptV2,
    ReviewFeedback
)

# Import ScriptV1 and related classes
try:
    from script_generator import (
        ScriptV1,
        ScriptSection,
        ScriptStructure,
        PlatformTarget,
        ScriptTone
    )
except ImportError:
    # Create minimal mock classes for testing if import fails
    class ScriptStructure(Enum):
        HOOK_DELIVER_CTA = "hook_deliver_cta"
    
    class PlatformTarget(Enum):
        YOUTUBE_MEDIUM = "youtube_medium"
    
    class ScriptTone(Enum):
        ENGAGING = "engaging"
        MYSTERIOUS = "mysterious"
    
    @dataclass
    class ScriptSection:
        section_type: str
        content: str
        estimated_duration_seconds: int
        purpose: str
        notes: str = ""
    
    @dataclass
    class ScriptV1:
        script_id: str
        idea_id: str
        title: str
        full_text: str
        sections: List[ScriptSection]
        total_duration_seconds: int
        structure_type: ScriptStructure
        platform_target: PlatformTarget
        metadata: Dict[str, Any] = field(default_factory=dict)
        created_at: str = ""
        version: int = 1
        notes: str = ""
        version_history: List[str] = field(default_factory=list)


# Mock review classes for testing
@dataclass
class MockImprovementPoint:
    """Mock improvement point for testing."""
    title: str
    description: str
    priority: str = "high"


@dataclass
class MockScriptReview:
    """Mock script review for testing."""
    script_id: str
    overall_score: int
    improvement_points: List[MockImprovementPoint] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    optimal_length_seconds: int = None
    current_length_seconds: int = None


@dataclass
class MockTitleReview:
    """Mock title review for testing."""
    title_id: str
    notes: str = ""


class TestScriptImproverBasics:
    """Basic tests for ScriptImprover."""
    
    def test_improver_initialization(self):
        """Test that improver can be initialized."""
        improver = ScriptImprover()
        assert improver is not None
        assert isinstance(improver.config, ScriptImproverConfig)
    
    def test_improver_with_custom_config(self):
        """Test improver with custom configuration."""
        config = ScriptImproverConfig(
            target_duration_seconds=120,
            preserve_successful_elements=True,
            address_all_critical_issues=True
        )
        improver = ScriptImprover(config)
        assert improver.config.target_duration_seconds == 120
        assert improver.config.preserve_successful_elements is True
        assert improver.config.address_all_critical_issues is True


class TestScriptV2Generation:
    """Tests for generating improved script versions."""
    
    def setup_method(self):
        """Set up test data."""
        # Create original script v1
        sections = [
            ScriptSection(
                section_type="introduction",
                content="What if I told you about the Mystery of the Abandoned House?",
                estimated_duration_seconds=15,
                purpose="Hook the audience"
            ),
            ScriptSection(
                section_type="body",
                content="This house has been abandoned for decades. Strange things happen there. People report seeing lights and hearing sounds.",
                estimated_duration_seconds=60,
                purpose="Deliver main content"
            ),
            ScriptSection(
                section_type="conclusion",
                content="The mystery remains unsolved. What do you think?",
                estimated_duration_seconds=15,
                purpose="Conclude and engage"
            )
        ]
        
        self.original_script = ScriptV1(
            script_id="script_v1_001",
            idea_id="idea_001",
            title="The Mystery of the Abandoned House",
            full_text="\n\n".join([s.content for s in sections]),
            sections=sections,
            total_duration_seconds=90,
            structure_type=ScriptStructure.HOOK_DELIVER_CTA,
            platform_target=PlatformTarget.YOUTUBE_MEDIUM,
            version=1
        )
        
        # Create review feedback
        script_review = MockScriptReview(
            script_id="script_v1_001",
            overall_score=70,
            improvement_points=[
                MockImprovementPoint(
                    title="Add paranormal angle",
                    description="Title mentions mystery but script needs more paranormal elements",
                    priority="high"
                ),
                MockImprovementPoint(
                    title="Improve pacing",
                    description="Middle section drags, needs tightening",
                    priority="medium"
                )
            ],
            strengths=["Strong hook", "Clear structure"],
            optimal_length_seconds=90,
            current_length_seconds=90
        )
        
        title_review = MockTitleReview(
            title_id="title_v1_001",
            notes="Title should emphasize time-loop aspect"
        )
        
        self.review_feedback = ReviewFeedback(
            script_review=script_review,
            title_review=title_review,
            review_type="general",
            priority_issues=["Add paranormal angle"]
        )
        
        self.title_v2 = "The House That Remembers"
    
    def test_generate_script_v2_basic(self):
        """Test generating a basic script v2."""
        improver = ScriptImprover()
        
        script_v2 = improver.generate_script_v2(
            original_script=self.original_script,
            title_v2=self.title_v2,
            review_feedback=self.review_feedback
        )
        
        assert script_v2 is not None
        assert isinstance(script_v2, ScriptV2)
        assert script_v2.version == 2
        assert script_v2.previous_script_id == "script_v1_001"
        assert script_v2.title == self.title_v2
        assert len(script_v2.sections) == 3
    
    def test_script_v2_version_tracking(self):
        """Test that version tracking works correctly."""
        improver = ScriptImprover()
        
        script_v2 = improver.generate_script_v2(
            original_script=self.original_script,
            title_v2=self.title_v2,
            review_feedback=self.review_feedback
        )
        
        assert script_v2.version == 2
        assert "script_v1_001" in script_v2.version_history
        assert script_v2.previous_script_id == "script_v1_001"
        assert script_v2.idea_id == self.original_script.idea_id
    
    def test_script_v2_feedback_addressed(self):
        """Test that review feedback is properly addressed."""
        improver = ScriptImprover()
        
        script_v2 = improver.generate_script_v2(
            original_script=self.original_script,
            title_v2=self.title_v2,
            review_feedback=self.review_feedback
        )
        
        # Should have improvements documented
        assert len(script_v2.review_feedback_addressed) > 0
        assert script_v2.improvements_made != ""
        assert "critical" in script_v2.improvements_made.lower() or "issue" in script_v2.improvements_made.lower()
    
    def test_script_v2_title_alignment(self):
        """Test that script v2 aligns with new title."""
        improver = ScriptImprover()
        
        script_v2 = improver.generate_script_v2(
            original_script=self.original_script,
            title_v2=self.title_v2,
            review_feedback=self.review_feedback
        )
        
        assert script_v2.title == self.title_v2
        assert script_v2.title_alignment_notes != ""
        assert self.title_v2 in script_v2.title_alignment_notes
    
    def test_script_v2_preserves_structure(self):
        """Test that script v2 preserves the structure type and platform target."""
        improver = ScriptImprover()
        
        script_v2 = improver.generate_script_v2(
            original_script=self.original_script,
            title_v2=self.title_v2,
            review_feedback=self.review_feedback
        )
        
        assert script_v2.structure_type == self.original_script.structure_type
        assert script_v2.platform_target == self.original_script.platform_target
    
    def test_script_v2_sections_maintained(self):
        """Test that all sections are maintained in v2."""
        improver = ScriptImprover()
        
        script_v2 = improver.generate_script_v2(
            original_script=self.original_script,
            title_v2=self.title_v2,
            review_feedback=self.review_feedback
        )
        
        # Should have same number of sections
        assert len(script_v2.sections) == len(self.original_script.sections)
        
        # Section types should match
        original_types = {s.section_type for s in self.original_script.sections}
        v2_types = {s.section_type for s in script_v2.sections}
        assert original_types == v2_types


class TestScriptImproverConfig:
    """Tests for configuration options."""
    
    def setup_method(self):
        """Set up test data."""
        sections = [
            ScriptSection(
                section_type="introduction",
                content="Hook content",
                estimated_duration_seconds=15,
                purpose="Hook"
            ),
            ScriptSection(
                section_type="body",
                content="Main content",
                estimated_duration_seconds=60,
                purpose="Deliver"
            ),
            ScriptSection(
                section_type="conclusion",
                content="Conclusion content",
                estimated_duration_seconds=15,
                purpose="Conclude"
            )
        ]
        
        self.original_script = ScriptV1(
            script_id="script_v1_002",
            idea_id="idea_002",
            title="Original Title",
            full_text="Full text",
            sections=sections,
            total_duration_seconds=90,
            structure_type=ScriptStructure.HOOK_DELIVER_CTA,
            platform_target=PlatformTarget.YOUTUBE_MEDIUM,
            version=1
        )
        
        self.review_feedback = ReviewFeedback(
            script_review=MockScriptReview(
                script_id="script_v1_002",
                overall_score=75
            )
        )
        
        self.title_v2 = "Improved Title"
    
    def test_target_duration_adjustment(self):
        """Test that target duration can be adjusted."""
        config = ScriptImproverConfig(target_duration_seconds=60)
        improver = ScriptImprover(config)
        
        script_v2 = improver.generate_script_v2(
            original_script=self.original_script,
            title_v2=self.title_v2,
            review_feedback=self.review_feedback
        )
        
        # Duration should be adjusted to target
        assert script_v2.total_duration_seconds == 60
    
    def test_config_overrides_with_kwargs(self):
        """Test that config can be overridden with kwargs."""
        improver = ScriptImprover()
        
        script_v2 = improver.generate_script_v2(
            original_script=self.original_script,
            title_v2=self.title_v2,
            review_feedback=self.review_feedback,
            target_duration_seconds=120
        )
        
        # Duration should match kwargs override
        assert script_v2.total_duration_seconds == 120


class TestScriptImproverValidation:
    """Tests for input validation."""
    
    def test_requires_original_script(self):
        """Test that original script is required."""
        improver = ScriptImprover()
        
        with pytest.raises(ValueError, match="Original script cannot be None"):
            improver.generate_script_v2(
                original_script=None,
                title_v2="Title",
                review_feedback=ReviewFeedback()
            )
    
    def test_requires_title_v2(self):
        """Test that title v2 is required."""
        improver = ScriptImprover()
        
        sections = [
            ScriptSection(
                section_type="introduction",
                content="Content",
                estimated_duration_seconds=15,
                purpose="Hook"
            )
        ]
        
        script = ScriptV1(
            script_id="test",
            idea_id="test",
            title="Test",
            full_text="Test",
            sections=sections,
            total_duration_seconds=15,
            structure_type=ScriptStructure.HOOK_DELIVER_CTA,
            platform_target=PlatformTarget.YOUTUBE_MEDIUM,
            version=1
        )
        
        with pytest.raises(ValueError, match="Title v2 cannot be empty"):
            improver.generate_script_v2(
                original_script=script,
                title_v2="",
                review_feedback=ReviewFeedback()
            )
    
    def test_requires_review_feedback(self):
        """Test that review feedback is required."""
        improver = ScriptImprover()
        
        sections = [
            ScriptSection(
                section_type="introduction",
                content="Content",
                estimated_duration_seconds=15,
                purpose="Hook"
            )
        ]
        
        script = ScriptV1(
            script_id="test",
            idea_id="test",
            title="Test",
            full_text="Test",
            sections=sections,
            total_duration_seconds=15,
            structure_type=ScriptStructure.HOOK_DELIVER_CTA,
            platform_target=PlatformTarget.YOUTUBE_MEDIUM,
            version=1
        )
        
        with pytest.raises(ValueError, match="Review feedback cannot be None"):
            improver.generate_script_v2(
                original_script=script,
                title_v2="Title",
                review_feedback=None
            )


class TestScriptV2DataModel:
    """Tests for ScriptV2 data model."""
    
    def test_script_v2_to_dict(self):
        """Test that ScriptV2 can be converted to dict."""
        sections = [
            ScriptSection(
                section_type="introduction",
                content="Content",
                estimated_duration_seconds=15,
                purpose="Hook"
            )
        ]
        
        script_v2 = ScriptV2(
            script_id="script_v2_001",
            idea_id="idea_001",
            previous_script_id="script_v1_001",
            title="Title v2",
            full_text="Full text",
            sections=sections,
            total_duration_seconds=15,
            structure_type=ScriptStructure.HOOK_DELIVER_CTA,
            platform_target=PlatformTarget.YOUTUBE_MEDIUM,
            version=2,
            improvements_made="Improvements",
            title_alignment_notes="Alignment notes"
        )
        
        data = script_v2.to_dict()
        
        assert isinstance(data, dict)
        assert data["script_id"] == "script_v2_001"
        assert data["version"] == 2
        assert data["previous_script_id"] == "script_v1_001"
        assert data["title"] == "Title v2"
        assert "sections" in data
        assert len(data["sections"]) == 1
    
    def test_script_v2_get_section(self):
        """Test getting a specific section from ScriptV2."""
        sections = [
            ScriptSection(
                section_type="introduction",
                content="Intro content",
                estimated_duration_seconds=15,
                purpose="Hook"
            ),
            ScriptSection(
                section_type="body",
                content="Body content",
                estimated_duration_seconds=60,
                purpose="Deliver"
            )
        ]
        
        script_v2 = ScriptV2(
            script_id="test",
            idea_id="test",
            previous_script_id="test",
            title="Test",
            full_text="Test",
            sections=sections,
            total_duration_seconds=75,
            structure_type=ScriptStructure.HOOK_DELIVER_CTA,
            platform_target=PlatformTarget.YOUTUBE_MEDIUM,
            version=2
        )
        
        intro = script_v2.get_section("introduction")
        assert intro is not None
        assert intro.content == "Intro content"
        
        body = script_v2.get_section("body")
        assert body is not None
        assert body.content == "Body content"
        
        missing = script_v2.get_section("nonexistent")
        assert missing is None


class TestIterativeImprovement:
    """Tests for iterative improvement (v2 → v3 → v4...)."""
    
    def test_v2_to_v3_progression(self):
        """Test that v2 can be improved to v3."""
        # Create a v2 script
        sections = [
            ScriptSection(
                section_type="introduction",
                content="Content",
                estimated_duration_seconds=15,
                purpose="Hook"
            )
        ]
        
        script_v2 = ScriptV1(  # Use ScriptV1 as base class
            script_id="script_v2_001",
            idea_id="idea_001",
            title="Title v2",
            full_text="Full text",
            sections=sections,
            total_duration_seconds=15,
            structure_type=ScriptStructure.HOOK_DELIVER_CTA,
            platform_target=PlatformTarget.YOUTUBE_MEDIUM,
            version=2
        )
        # Add version_history attribute for testing
        script_v2.version_history = ["script_v1_001"]
        
        review_feedback = ReviewFeedback(
            script_review=MockScriptReview(
                script_id="script_v2_001",
                overall_score=85
            )
        )
        
        improver = ScriptImprover()
        script_v3 = improver.generate_script_v2(  # Still use generate_script_v2 for any vN→vN+1
            original_script=script_v2,
            title_v2="Title v3",
            review_feedback=review_feedback
        )
        
        assert script_v3.version == 3
        assert script_v3.previous_script_id == "script_v2_001"
        assert "script_v1_001" in script_v3.version_history
        assert "script_v2_001" in script_v3.version_history
