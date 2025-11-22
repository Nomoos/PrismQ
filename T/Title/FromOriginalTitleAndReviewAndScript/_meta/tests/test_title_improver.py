"""Tests for Title Improvement module (MVP-006)."""

import sys
import os
import pytest
from pathlib import Path

# Add parent directories to path for imports
test_dir = Path(__file__).parent
sys.path.insert(0, str(test_dir / '../../src'))
sys.path.insert(0, str(test_dir / '../../../../Idea/Model/src'))
sys.path.insert(0, str(test_dir / '../../../../Idea/Model'))
sys.path.insert(0, str(test_dir / '../../../../Review/Title/ByScriptAndIdea'))
sys.path.insert(0, str(test_dir / '../../../../Review/Script/ByTitle'))
sys.path.insert(0, str(test_dir / '../../../../Review/Script'))

from title_improver import (
    TitleImprover,
    ImprovedTitle,
    TitleVersion,
    improve_title_from_reviews
)
from title_review import (
    TitleReview,
    TitleImprovementPoint,
    TitleReviewCategory,
    TitleCategoryScore
)
from script_review import (
    ScriptReview,
    ImprovementPoint,
    ReviewCategory,
    CategoryScore,
    ContentLength
)
from idea import Idea, IdeaStatus, ContentGenre


class TestTitleVersion:
    """Tests for TitleVersion data class."""
    
    def test_create_title_version(self):
        """Test creating a title version."""
        version = TitleVersion(
            version_number="v1",
            text="Test Title",
            notes="Original version"
        )
        
        assert version.version_number == "v1"
        assert version.text == "Test Title"
        assert version.notes == "Original version"
        assert version.created_by == "AI-TitleImprover-001"
    
    def test_title_version_to_dict(self):
        """Test converting title version to dictionary."""
        version = TitleVersion(
            version_number="v2",
            text="Improved Title",
            changes_from_previous="Added keywords",
            review_score=85
        )
        
        result = version.to_dict()
        
        assert result['version_number'] == "v2"
        assert result['text'] == "Improved Title"
        assert result['changes_from_previous'] == "Added keywords"
        assert result['review_score'] == 85


class TestImprovedTitle:
    """Tests for ImprovedTitle data class."""
    
    def test_create_improved_title(self):
        """Test creating an improved title result."""
        original = TitleVersion("v1", "Original Title")
        new = TitleVersion("v2", "Improved Title")
        
        result = ImprovedTitle(
            new_version=new,
            original_version=original,
            rationale="Added keywords for better alignment"
        )
        
        assert result.new_version.version_number == "v2"
        assert result.original_version.version_number == "v1"
        assert "alignment" in result.rationale
    
    def test_improved_title_to_dict(self):
        """Test converting improved title to dictionary."""
        original = TitleVersion("v1", "Original")
        new = TitleVersion("v2", "Improved")
        
        result = ImprovedTitle(
            new_version=new,
            original_version=original,
            rationale="Test rationale",
            addressed_improvements=["alignment", "engagement"]
        )
        
        data = result.to_dict()
        
        assert 'new_version' in data
        assert 'original_version' in data
        assert data['rationale'] == "Test rationale"
        assert len(data['addressed_improvements']) == 2


class TestTitleImprover:
    """Tests for TitleImprover class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.improver = TitleImprover()
        
        # Sample data
        self.original_title = "The Mystery House"
        self.script_text = """
        In the abandoned Victorian house on Elm Street, strange echoes fill the air.
        Every night, Sarah hears voices repeating her words moments after she speaks.
        The haunting sound grows stronger, revealing dark secrets buried in the walls.
        """
        
        # Create sample title review
        self.title_review = TitleReview(
            title_id="title-001",
            title_text=self.original_title,
            title_version="v1",
            overall_score=65,
            script_alignment_score=60,
            idea_alignment_score=70,
            engagement_score=75,
            script_id="script-001",
            key_script_elements=["echo", "Victorian", "haunting", "secrets"],
            suggested_keywords=["echo", "haunting"],
            current_length_chars=len(self.original_title),
            optimal_length_chars=60
        )
        
        # Add improvement points
        self.title_review.improvement_points = [
            TitleImprovementPoint(
                category=TitleReviewCategory.SCRIPT_ALIGNMENT,
                title="Missing key script elements",
                description="Title doesn't mention 'echo' which is central to script",
                priority="high",
                impact_score=85,
                suggested_fix="Incorporate 'echo' keyword"
            ),
            TitleImprovementPoint(
                category=TitleReviewCategory.ENGAGEMENT,
                title="Generic title",
                description="Title is too generic and not intriguing",
                priority="medium",
                impact_score=70,
                suggested_fix="Add intrigue or mystery element"
            )
        ]
        
        # Create sample script review
        self.script_review = ScriptReview(
            script_id="script-001",
            script_title=self.original_title,
            overall_score=72,
            target_audience="Horror enthusiasts",
            audience_alignment_score=75,
            target_length=ContentLength.SHORT_FORM,
            current_length_seconds=120
        )
        
        # Add improvement points
        self.script_review.improvement_points = [
            ImprovementPoint(
                category=ReviewCategory.ENGAGEMENT,
                title="Opening hook",
                description="Script has strong echo element that title should reflect",
                priority="high",
                impact_score=80,
                suggested_fix="Emphasize the echo mystery"
            )
        ]
    
    def test_improve_title_basic(self):
        """Test basic title improvement."""
        result = self.improver.improve_title(
            original_title=self.original_title,
            script_text=self.script_text,
            title_review=self.title_review,
            script_review=self.script_review
        )
        
        assert isinstance(result, ImprovedTitle)
        assert result.original_version.text == self.original_title
        assert result.new_version.text != self.original_title
        assert result.new_version.version_number == "v2"
        assert len(result.rationale) > 0
    
    def test_improve_title_with_idea(self):
        """Test title improvement with idea context."""
        idea = Idea(
            title="Echoing Mystery",
            concept="Horror story about mysterious echoes in an abandoned house",
            status=IdeaStatus.APPROVED
        )
        
        result = self.improver.improve_title(
            original_title=self.original_title,
            script_text=self.script_text,
            title_review=self.title_review,
            script_review=self.script_review,
            idea=idea
        )
        
        assert isinstance(result, ImprovedTitle)
        assert result.new_version.text != self.original_title
    
    def test_improve_title_custom_versions(self):
        """Test improvement with custom version numbers."""
        result = self.improver.improve_title(
            original_title=self.original_title,
            script_text=self.script_text,
            title_review=self.title_review,
            script_review=self.script_review,
            original_version_number="v2",
            new_version_number="v3"
        )
        
        assert result.original_version.version_number == "v2"
        assert result.new_version.version_number == "v3"
    
    def test_improve_title_incorporates_script_elements(self):
        """Test that improvement incorporates key script elements."""
        result = self.improver.improve_title(
            original_title=self.original_title,
            script_text=self.script_text,
            title_review=self.title_review,
            script_review=self.script_review
        )
        
        # Should incorporate "echo" or "haunting" from script elements
        improved_lower = result.new_version.text.lower()
        has_key_element = any(
            elem.lower() in improved_lower
            for elem in ["echo", "haunting", "victorian"]
        )
        assert has_key_element
    
    def test_improve_title_addresses_improvements(self):
        """Test that addressed improvements are tracked."""
        result = self.improver.improve_title(
            original_title=self.original_title,
            script_text=self.script_text,
            title_review=self.title_review,
            script_review=self.script_review
        )
        
        assert len(result.addressed_improvements) > 0
        assert any("alignment" in imp.lower() or "script" in imp.lower()
                   for imp in result.addressed_improvements)
    
    def test_improve_title_version_history(self):
        """Test that version history is maintained."""
        result = self.improver.improve_title(
            original_title=self.original_title,
            script_text=self.script_text,
            title_review=self.title_review,
            script_review=self.script_review
        )
        
        assert len(result.version_history) == 2
        assert result.version_history[0].version_number == "v1"
        assert result.version_history[1].version_number == "v2"
    
    def test_improve_title_invalid_inputs(self):
        """Test error handling for invalid inputs."""
        with pytest.raises(ValueError):
            self.improver.improve_title(
                original_title="",
                script_text=self.script_text,
                title_review=self.title_review,
                script_review=self.script_review
            )
        
        with pytest.raises(ValueError):
            self.improver.improve_title(
                original_title=self.original_title,
                script_text="",
                title_review=self.title_review,
                script_review=self.script_review
            )
        
        with pytest.raises(ValueError):
            self.improver.improve_title(
                original_title=self.original_title,
                script_text=self.script_text,
                title_review=None,
                script_review=self.script_review
            )


class TestTitleImprovementStrategies:
    """Tests for specific improvement strategies."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.improver = TitleImprover()
    
    def test_extract_title_improvements(self):
        """Test extracting improvements from title review."""
        review = TitleReview(
            title_id="test",
            title_text="Test Title",
            overall_score=70
        )
        
        review.improvement_points = [
            TitleImprovementPoint(
                category=TitleReviewCategory.SCRIPT_ALIGNMENT,
                title="High priority item",
                description="Test",
                priority="high",
                impact_score=90
            ),
            TitleImprovementPoint(
                category=TitleReviewCategory.CLARITY,
                title="Low priority item",
                description="Test",
                priority="low",
                impact_score=40
            ),
            TitleImprovementPoint(
                category=TitleReviewCategory.ENGAGEMENT,
                title="Medium priority item",
                description="Test",
                priority="medium",
                impact_score=70
            )
        ]
        
        improvements = self.improver._extract_title_improvements(review)
        
        assert len(improvements) == 3
        # Should be sorted by priority then impact
        assert improvements[0]['priority'] == 'high'
        assert improvements[1]['priority'] == 'medium'
        assert improvements[2]['priority'] == 'low'
    
    def test_extract_script_insights(self):
        """Test extracting relevant insights from script review."""
        review = ScriptReview(
            script_id="test",
            script_title="Test",
            overall_score=75
        )
        
        review.improvement_points = [
            ImprovementPoint(
                category=ReviewCategory.ENGAGEMENT,
                title="Title promise",
                description="Script mentions title expectations",
                priority="high",
                impact_score=80
            ),
            ImprovementPoint(
                category=ReviewCategory.PACING,
                title="Story pacing",
                description="Story moves too slowly",
                priority="medium",
                impact_score=60
            )
        ]
        
        insights = self.improver._extract_script_insights(review)
        
        # Should only extract title-relevant insights
        assert len(insights) >= 0
        if insights:
            assert any('title' in ins['description'].lower() for ins in insights)
    
    def test_incorporate_script_elements(self):
        """Test incorporating script elements into title."""
        title = "The House"
        elements = ["mystery", "echo", "Victorian"]
        
        result = self.improver._incorporate_script_elements(title, elements)
        
        # Should have added an element
        assert len(result) > len(title)
        # Should contain at least one element
        result_lower = result.lower()
        assert any(elem.lower() in result_lower for elem in elements)
    
    def test_adjust_length_too_long(self):
        """Test adjusting title that's too long."""
        long_title = "This is a Very Long Title That Exceeds the Optimal Length"
        optimal_length = 40
        
        result = self.improver._adjust_length(long_title, optimal_length)
        
        assert len(result) <= optimal_length + 3  # Allow for "..."
    
    def test_adjust_length_already_optimal(self):
        """Test that optimal length titles are not changed."""
        title = "Perfect Length Title"
        optimal_length = 50
        
        result = self.improver._adjust_length(title, optimal_length)
        
        assert result == title


class TestConvenienceFunction:
    """Tests for convenience function."""
    
    def test_improve_title_from_reviews(self):
        """Test convenience function."""
        title = "Mystery Story"
        script = "A mysterious tale of secrets and revelations."
        
        title_review = TitleReview(
            title_id="test",
            title_text=title,
            overall_score=70,
            script_alignment_score=65,
            key_script_elements=["mystery", "secrets"]
        )
        
        script_review = ScriptReview(
            script_id="test",
            script_title=title,
            overall_score=75
        )
        
        result = improve_title_from_reviews(
            original_title=title,
            script_text=script,
            title_review=title_review,
            script_review=script_review
        )
        
        assert isinstance(result, ImprovedTitle)
        assert result.original_version.text == title
        assert result.new_version.text != title


class TestAcceptanceCriteria:
    """Tests verifying MVP-006 acceptance criteria."""
    
    def test_generates_v2_from_both_reviews(self):
        """Verify: Generate title v2 using feedback from both reviews."""
        improver = TitleImprover()
        
        title = "The Secret"
        script = "A tale of hidden mysteries and dangerous secrets in an old house."
        
        # Create both reviews with feedback
        title_review = TitleReview(
            title_id="ac-test-1",
            title_text=title,
            overall_score=65,
            script_alignment_score=60,
            key_script_elements=["mysteries", "dangerous", "old house"]
        )
        title_review.improvement_points = [
            TitleImprovementPoint(
                category=TitleReviewCategory.SCRIPT_ALIGNMENT,
                title="Missing key elements",
                description="Doesn't mention danger or mystery",
                priority="high",
                impact_score=85
            )
        ]
        
        script_review = ScriptReview(
            script_id="ac-test-1",
            script_title=title,
            overall_score=70
        )
        script_review.improvement_points = [
            ImprovementPoint(
                category=ReviewCategory.ENGAGEMENT,
                title="Title promise",
                description="Title should set up the danger and mystery",
                priority="high",
                impact_score=80
            )
        ]
        
        result = improver.improve_title(
            original_title=title,
            script_text=script,
            title_review=title_review,
            script_review=script_review
        )
        
        # Should generate v2
        assert result.new_version.version_number == "v2"
        # Should be different from v1
        assert result.new_version.text != title
        # Should have rationale
        assert len(result.rationale) > 0
    
    def test_uses_v1_and_reviews(self):
        """Verify: Use title v1, script v1, and both review feedbacks."""
        improver = TitleImprover()
        
        title_v1 = "Simple Title"
        script_v1 = "Complex narrative with multiple themes."
        
        title_review = TitleReview(
            title_id="ac-test-2",
            title_text=title_v1,
            overall_score=70,
            script_alignment_score=65
        )
        
        script_review = ScriptReview(
            script_id="ac-test-2",
            script_title=title_v1,
            overall_score=72
        )
        
        result = improver.improve_title(
            original_title=title_v1,
            script_text=script_v1,
            title_review=title_review,
            script_review=script_review,
            original_version_number="v1"
        )
        
        # Should reference v1
        assert result.original_version.version_number == "v1"
        assert result.original_version.text == title_v1
    
    def test_maintains_engagement(self):
        """Verify: Maintain engagement while improving alignment."""
        improver = TitleImprover()
        
        # Title with good engagement but poor alignment
        title = "The Shocking Truth!"
        script = "A documentary about scientific discoveries."
        
        title_review = TitleReview(
            title_id="ac-test-3",
            title_text=title,
            overall_score=70,
            script_alignment_score=50,  # Poor alignment
            engagement_score=85,  # Good engagement
            key_script_elements=["scientific", "discoveries"]
        )
        
        script_review = ScriptReview(
            script_id="ac-test-3",
            script_title=title,
            overall_score=75
        )
        
        result = improver.improve_title(
            original_title=title,
            script_text=script,
            title_review=title_review,
            script_review=script_review
        )
        
        # Should have engagement notes
        assert len(result.engagement_notes) > 0
        # Should mention engagement score
        assert "engagement" in result.engagement_notes.lower()
    
    def test_stores_v2_with_reference_to_v1(self):
        """Verify: Store v2 with reference to v1."""
        improver = TitleImprover()
        
        title_v1 = "Original Title"
        script = "Script content here."
        
        title_review = TitleReview(
            title_id="ac-test-4",
            title_text=title_v1,
            overall_score=70
        )
        
        script_review = ScriptReview(
            script_id="ac-test-4",
            script_title=title_v1,
            overall_score=72
        )
        
        result = improver.improve_title(
            original_title=title_v1,
            script_text=script,
            title_review=title_review,
            script_review=script_review
        )
        
        # Should have version history
        assert len(result.version_history) >= 2
        # Should have original version
        assert result.original_version.text == title_v1
        # New version should reference changes
        assert len(result.new_version.changes_from_previous) > 0
    
    def test_v2_addresses_feedback(self):
        """Verify: v2 addresses feedback from v1 reviews."""
        improver = TitleImprover()
        
        title = "Generic Story"
        script = "A thrilling adventure about space exploration and alien encounters."
        
        # Reviews with specific feedback
        title_review = TitleReview(
            title_id="ac-test-5",
            title_text=title,
            overall_score=60,
            script_alignment_score=55,
            key_script_elements=["space", "exploration", "alien"]
        )
        title_review.improvement_points = [
            TitleImprovementPoint(
                category=TitleReviewCategory.SCRIPT_ALIGNMENT,
                title="Missing space/alien theme",
                description="Title should mention space or alien elements",
                priority="high",
                impact_score=90
            )
        ]
        
        script_review = ScriptReview(
            script_id="ac-test-5",
            script_title=title,
            overall_score=75
        )
        
        result = improver.improve_title(
            original_title=title,
            script_text=script,
            title_review=title_review,
            script_review=script_review
        )
        
        # Should address improvements
        assert len(result.addressed_improvements) > 0
        # Should mention what was addressed in rationale
        assert len(result.rationale) > 0
        # Improved title should incorporate script elements
        improved_lower = result.new_version.text.lower()
        assert any(elem in improved_lower for elem in ["space", "alien", "exploration"])
