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


class TestMVP011AcceptanceCriteria:
    """Tests specifically for MVP-011: Script Refinement v3 acceptance criteria."""
    
    def setup_method(self):
        """Set up test data for MVP-011 tests."""
        # Create a v2 script with comprehensive sections
        sections = [
            ScriptSection(
                section_type="introduction",
                content="In a small forgotten town, there stands a house that locals avoid. "
                        "What if I told you this house remembers everything?",
                estimated_duration_seconds=20,
                purpose="Hook the audience with mystery"
            ),
            ScriptSection(
                section_type="body",
                content="The house was built in 1892. Strange occurrences have been reported. "
                        "People claim to hear voices from the past. Time seems to loop inside.",
                estimated_duration_seconds=70,
                purpose="Deliver main narrative"
            ),
            ScriptSection(
                section_type="conclusion",
                content="The mystery deepens with each visitor. Will you dare to find out?",
                estimated_duration_seconds=20,
                purpose="Conclude and engage"
            )
        ]
        
        self.script_v2 = ScriptV1(
            script_id="script_v2_mvp011",
            idea_id="idea_mvp011",
            title="The Haunted House Mystery",
            full_text="\n\n".join([s.content for s in sections]),
            sections=sections,
            total_duration_seconds=110,
            structure_type=ScriptStructure.HOOK_DELIVER_CTA,
            platform_target=PlatformTarget.YOUTUBE_MEDIUM,
            version=2
        )
        # Add version_history attribute for testing
        self.script_v2.version_history = ["script_v1_mvp011"]
        
        # Create review feedback emphasizing narrative flow improvements
        self.review_feedback = ReviewFeedback(
            script_review=MockScriptReview(
                script_id="script_v2_mvp011",
                overall_score=75,
                improvement_points=[
                    MockImprovementPoint(
                        title="Strengthen time-loop theme",
                        description="Title v3 emphasizes memory/time-loop aspect, script should amplify this",
                        priority="high"
                    ),
                    MockImprovementPoint(
                        title="Polish narrative transitions",
                        description="Body to conclusion transition feels abrupt",
                        priority="medium"
                    ),
                    MockImprovementPoint(
                        title="Enhance atmospheric build-up",
                        description="Middle section needs more tension",
                        priority="medium"
                    )
                ],
                strengths=["Strong hook", "Clear mystery setup"],
                optimal_length_seconds=110,
                current_length_seconds=110
            ),
            title_review=MockTitleReview(
                title_id="title_v3_mvp011",
                notes="Title v3 emphasizes temporal recursion - script should highlight time-loop mechanics"
            ),
            review_type="comprehensive_v3_refinement",
            priority_issues=["Strengthen time-loop theme"]
        )
        
        self.title_v3 = "The House That Remembers—Forever"
    
    def test_v3_refines_from_v2_using_feedback(self):
        """Acceptance: Refine script from v2 to v3 using feedback."""
        improver = ScriptImprover()
        
        script_v3 = improver.generate_script_v2(
            original_script=self.script_v2,
            title_v2=self.title_v3,
            review_feedback=self.review_feedback
        )
        
        # Verify it's v3 and builds on v2
        assert script_v3.version == 3
        assert script_v3.previous_script_id == "script_v2_mvp011"
        
        # Verify feedback was incorporated
        assert len(script_v3.review_feedback_addressed) > 0
        # Check that high-priority issues were addressed
        feedback_text = "\n".join(script_v3.review_feedback_addressed)
        assert "time-loop" in feedback_text.lower() or "loop" in feedback_text.lower()
        
        # Verify improvements were documented
        assert script_v3.improvements_made != ""
        assert "critical" in script_v3.improvements_made.lower() or "issue" in script_v3.improvements_made.lower()
    
    def test_v3_aligns_with_title_v3(self):
        """Acceptance: Ensure alignment with title v3."""
        improver = ScriptImprover()
        
        script_v3 = improver.generate_script_v2(
            original_script=self.script_v2,
            title_v2=self.title_v3,
            review_feedback=self.review_feedback
        )
        
        # Verify title alignment
        assert script_v3.title == self.title_v3
        assert script_v3.title_alignment_notes != ""
        assert self.title_v3 in script_v3.title_alignment_notes
        
        # Verify metadata tracks title alignment
        assert "title_v2" in script_v3.metadata
        assert script_v3.metadata["title_v2"] == self.title_v3
    
    def test_v3_polishes_narrative_flow(self):
        """Acceptance: Polish narrative flow."""
        improver = ScriptImprover()
        
        script_v3 = improver.generate_script_v2(
            original_script=self.script_v2,
            title_v2=self.title_v3,
            review_feedback=self.review_feedback
        )
        
        # Verify sections were processed (narrative flow consideration)
        assert len(script_v3.sections) == len(self.script_v2.sections)
        
        # Verify each section has been considered for improvement
        for section in script_v3.sections:
            assert section.content is not None and section.content != ""
            assert section.purpose is not None
            
        # Verify full text was assembled (part of narrative flow)
        assert script_v3.full_text != ""
        assert len(script_v3.full_text) > 0
    
    def test_v3_stores_reference_to_v2(self):
        """Acceptance: Store v3 with reference to v2."""
        improver = ScriptImprover()
        
        script_v3 = improver.generate_script_v2(
            original_script=self.script_v2,
            title_v2=self.title_v3,
            review_feedback=self.review_feedback
        )
        
        # Verify direct reference to v2
        assert script_v3.previous_script_id == "script_v2_mvp011"
        
        # Verify version history includes both v1 and v2
        assert "script_v1_mvp011" in script_v3.version_history
        assert "script_v2_mvp011" in script_v3.version_history
        
        # Verify version progression
        assert script_v3.version == 3
        
        # Verify metadata tracks original
        assert script_v3.metadata["original_script_id"] == self.script_v2.script_id
        assert script_v3.metadata["original_version"] == 2
    
    def test_supports_versioning_beyond_v3(self):
        """Acceptance: Support versioning (v3, v4, v5, v6, v7, etc.)."""
        improver = ScriptImprover()
        
        # Create v3 from v2
        script_v3 = improver.generate_script_v2(
            original_script=self.script_v2,
            title_v2=self.title_v3,
            review_feedback=self.review_feedback
        )
        
        assert script_v3.version == 3
        
        # Create v4 from v3
        review_v3 = ReviewFeedback(
            script_review=MockScriptReview(
                script_id=script_v3.script_id,
                overall_score=80,
                improvement_points=[
                    MockImprovementPoint(
                        title="Minor polish",
                        description="Small refinements needed",
                        priority="low"
                    )
                ]
            )
        )
        
        script_v4 = improver.generate_script_v2(
            original_script=script_v3,
            title_v2="Title v4",
            review_feedback=review_v3
        )
        
        assert script_v4.version == 4
        assert script_v4.previous_script_id == script_v3.script_id
        assert script_v3.script_id in script_v4.version_history
        
        # Create v5 from v4
        review_v4 = ReviewFeedback(
            script_review=MockScriptReview(
                script_id=script_v4.script_id,
                overall_score=85
            )
        )
        
        script_v5 = improver.generate_script_v2(
            original_script=script_v4,
            title_v2="Title v5",
            review_feedback=review_v4
        )
        
        assert script_v5.version == 5
        assert script_v5.previous_script_id == script_v4.script_id
        
        # Verify complete version history (v1 → v2 → v3 → v4 → v5)
        assert "script_v1_mvp011" in script_v5.version_history
        assert "script_v2_mvp011" in script_v5.version_history
        assert script_v3.script_id in script_v5.version_history
        assert script_v4.script_id in script_v5.version_history
    
    def test_v3_comprehensive_acceptance(self):
        """Comprehensive test: Verify v3 incorporates feedback and aligns with title v3."""
        improver = ScriptImprover()
        
        script_v3 = improver.generate_script_v2(
            original_script=self.script_v2,
            title_v2=self.title_v3,
            review_feedback=self.review_feedback
        )
        
        # Version verification
        assert script_v3.version == 3
        assert script_v3.previous_script_id == self.script_v2.script_id
        
        # Feedback incorporation verification
        assert len(script_v3.review_feedback_addressed) > 0
        assert script_v3.improvements_made != ""
        
        # Title alignment verification
        assert script_v3.title == self.title_v3
        assert script_v3.title_alignment_notes != ""
        
        # Structure preservation
        assert script_v3.structure_type == self.script_v2.structure_type
        assert script_v3.platform_target == self.script_v2.platform_target
        assert script_v3.idea_id == self.script_v2.idea_id
        
        # Content quality
        assert script_v3.full_text != ""
        assert len(script_v3.sections) > 0
        assert script_v3.total_duration_seconds > 0
        
        # Metadata completeness
        assert script_v3.created_at != ""
        assert script_v3.notes != ""
        assert "v3" in script_v3.notes or "3" in script_v3.notes
        
        # Version history completeness
        assert len(script_v3.version_history) == 2  # Contains v1 and v2
        
        # Serialization support
        data_dict = script_v3.to_dict()
        assert data_dict["version"] == 3
        assert data_dict["previous_script_id"] == self.script_v2.script_id
