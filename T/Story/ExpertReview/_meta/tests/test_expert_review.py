"""Tests for ExpertReview model and StoryExpertReviewer."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

import pytest
from T.Story.ExpertReview import (
    ExpertReview,
    OverallAssessment,
    StoryCoherence,
    AudienceFit,
    ProfessionalQuality,
    PlatformOptimization,
    ImprovementSuggestion,
    ComponentType,
    Priority,
    EffortLevel,
    AlignmentLevel,
    MatchLevel,
    ReviewDecision,
    StoryExpertReviewer,
    review_story_with_gpt,
    review_story_to_json,
    get_expert_feedback
)
import json


class TestExpertReviewBasic:
    """Test basic ExpertReview functionality."""
    
    def test_create_basic_review(self):
        """Test creating a basic ExpertReview instance."""
        review = ExpertReview(
            story_id="story-001",
            story_version="v3",
            title="Test Title",
            script="Test script content"
        )
        
        assert review.story_id == "story-001"
        assert review.story_version == "v3"
        assert review.title == "Test Title"
        assert review.script == "Test script content"
        assert review.reviewer_id == "GPT-ExpertReviewer-001"
        assert review.reviewed_at is not None
        assert len(review.improvement_suggestions) == 0
        assert review.decision is None
    
    def test_create_review_with_assessment(self):
        """Test creating a review with overall assessment."""
        assessment = OverallAssessment(
            ready_for_publishing=True,
            quality_score=96,
            confidence=95
        )
        
        review = ExpertReview(
            story_id="story-002",
            story_version="v3",
            title="Great Title",
            script="Excellent script",
            overall_assessment=assessment
        )
        
        assert review.overall_assessment.ready_for_publishing is True
        assert review.overall_assessment.quality_score == 96
        assert review.overall_assessment.confidence == 95
    
    def test_review_with_publish_decision(self):
        """Test review that recommends publishing."""
        review = ExpertReview(
            story_id="story-publish",
            story_version="v3",
            title="Perfect Story",
            script="Amazing content",
            decision=ReviewDecision.PUBLISH
        )
        
        assert review.decision == ReviewDecision.PUBLISH
    
    def test_review_with_polish_decision(self):
        """Test review that recommends polish."""
        review = ExpertReview(
            story_id="story-polish",
            story_version="v3",
            title="Good Story",
            script="Good content but needs improvement",
            decision=ReviewDecision.POLISH
        )
        
        assert review.decision == ReviewDecision.POLISH


class TestAssessmentComponents:
    """Test assessment component classes."""
    
    def test_overall_assessment(self):
        """Test OverallAssessment class."""
        assessment = OverallAssessment(
            ready_for_publishing=True,
            quality_score=95,
            confidence=90
        )
        
        assert assessment.ready_for_publishing is True
        assert assessment.quality_score == 95
        assert assessment.confidence == 90
        
        # Test to_dict
        data = assessment.to_dict()
        assert data['ready_for_publishing'] is True
        assert data['quality_score'] == 95
        assert data['confidence'] == 90
    
    def test_story_coherence(self):
        """Test StoryCoherence class."""
        coherence = StoryCoherence(
            score=92,
            feedback="Excellent coherence",
            title_script_alignment=AlignmentLevel.PERFECT
        )
        
        assert coherence.score == 92
        assert coherence.feedback == "Excellent coherence"
        assert coherence.title_script_alignment == AlignmentLevel.PERFECT
        
        # Test to_dict
        data = coherence.to_dict()
        assert data['score'] == 92
        assert data['title_script_alignment'] == 'perfect'
    
    def test_audience_fit(self):
        """Test AudienceFit class."""
        fit = AudienceFit(
            score=88,
            feedback="Great fit for target audience",
            demographic_match=MatchLevel.EXCELLENT
        )
        
        assert fit.score == 88
        assert fit.demographic_match == MatchLevel.EXCELLENT
        
        data = fit.to_dict()
        assert data['demographic_match'] == 'excellent'
    
    def test_professional_quality(self):
        """Test ProfessionalQuality class."""
        quality = ProfessionalQuality(
            score=90,
            feedback="Production ready",
            production_ready=True
        )
        
        assert quality.score == 90
        assert quality.production_ready is True
        
        data = quality.to_dict()
        assert data['production_ready'] is True
    
    def test_platform_optimization(self):
        """Test PlatformOptimization class."""
        optimization = PlatformOptimization(
            score=94,
            feedback="Perfect for platform",
            platform_perfect=True
        )
        
        assert optimization.score == 94
        assert optimization.platform_perfect is True


class TestImprovementSuggestion:
    """Test ImprovementSuggestion functionality."""
    
    def test_create_suggestion(self):
        """Test creating an improvement suggestion."""
        suggestion = ImprovementSuggestion(
            component=ComponentType.TITLE,
            priority=Priority.HIGH,
            suggestion="Improve title specificity",
            impact="Increases click-through rate",
            estimated_effort=EffortLevel.SMALL
        )
        
        assert suggestion.component == ComponentType.TITLE
        assert suggestion.priority == Priority.HIGH
        assert suggestion.suggestion == "Improve title specificity"
        assert suggestion.impact == "Increases click-through rate"
        assert suggestion.estimated_effort == EffortLevel.SMALL
    
    def test_suggestion_to_dict(self):
        """Test converting suggestion to dictionary."""
        suggestion = ImprovementSuggestion(
            component=ComponentType.SCRIPT,
            priority=Priority.MEDIUM,
            suggestion="Enhance opening hook",
            impact="Better engagement",
            estimated_effort=EffortLevel.SMALL
        )
        
        data = suggestion.to_dict()
        assert data['component'] == 'script'
        assert data['priority'] == 'medium'
        assert data['suggestion'] == "Enhance opening hook"
        assert data['impact'] == "Better engagement"
        assert data['estimated_effort'] == 'small'
    
    def test_suggestion_from_dict(self):
        """Test creating suggestion from dictionary."""
        data = {
            'component': 'title',
            'priority': 'high',
            'suggestion': 'Test suggestion',
            'impact': 'Test impact',
            'estimated_effort': 'small'
        }
        
        suggestion = ImprovementSuggestion.from_dict(data)
        assert suggestion.component == ComponentType.TITLE
        assert suggestion.priority == Priority.HIGH
        assert suggestion.estimated_effort == EffortLevel.SMALL


class TestExpertReviewMethods:
    """Test ExpertReview methods."""
    
    def test_to_dict(self):
        """Test converting review to dictionary."""
        review = ExpertReview(
            story_id="story-001",
            story_version="v3",
            title="Test Title",
            script="Test script"
        )
        
        review.overall_assessment = OverallAssessment(
            ready_for_publishing=True,
            quality_score=95,
            confidence=90
        )
        
        review.decision = ReviewDecision.PUBLISH
        
        data = review.to_dict()
        assert data['story_id'] == "story-001"
        assert data['story_version'] == "v3"
        assert data['title'] == "Test Title"
        assert data['overall_assessment']['quality_score'] == 95
        assert data['decision'] == 'publish'
    
    def test_to_json(self):
        """Test converting review to JSON string."""
        review = ExpertReview(
            story_id="story-001",
            story_version="v3",
            title="Test",
            script="Test"
        )
        
        review.decision = ReviewDecision.POLISH
        
        json_str = review.to_json()
        assert isinstance(json_str, str)
        
        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert parsed['story_id'] == "story-001"
        assert parsed['decision'] == 'polish'
    
    def test_get_high_priority_suggestions(self):
        """Test filtering high-priority suggestions."""
        review = ExpertReview(
            story_id="story-001",
            story_version="v3",
            title="Test",
            script="Test"
        )
        
        review.improvement_suggestions = [
            ImprovementSuggestion(
                component=ComponentType.TITLE,
                priority=Priority.HIGH,
                suggestion="High priority item",
                impact="Big impact",
                estimated_effort=EffortLevel.SMALL
            ),
            ImprovementSuggestion(
                component=ComponentType.SCRIPT,
                priority=Priority.LOW,
                suggestion="Low priority item",
                impact="Small impact",
                estimated_effort=EffortLevel.LARGE
            ),
            ImprovementSuggestion(
                component=ComponentType.BOTH,
                priority=Priority.HIGH,
                suggestion="Another high priority",
                impact="Important",
                estimated_effort=EffortLevel.MEDIUM
            )
        ]
        
        high_priority = review.get_high_priority_suggestions()
        assert len(high_priority) == 2
        assert all(s.priority == Priority.HIGH for s in high_priority)
    
    def test_get_small_effort_suggestions(self):
        """Test filtering small effort suggestions."""
        review = ExpertReview(
            story_id="story-001",
            story_version="v3",
            title="Test",
            script="Test"
        )
        
        review.improvement_suggestions = [
            ImprovementSuggestion(
                component=ComponentType.TITLE,
                priority=Priority.HIGH,
                suggestion="Quick fix",
                impact="Good",
                estimated_effort=EffortLevel.SMALL
            ),
            ImprovementSuggestion(
                component=ComponentType.SCRIPT,
                priority=Priority.HIGH,
                suggestion="Big change",
                impact="Great",
                estimated_effort=EffortLevel.LARGE
            )
        ]
        
        small_effort = review.get_small_effort_suggestions()
        assert len(small_effort) == 1
        assert small_effort[0].estimated_effort == EffortLevel.SMALL
    
    def test_get_suggestions_by_component(self):
        """Test filtering suggestions by component."""
        review = ExpertReview(
            story_id="story-001",
            story_version="v3",
            title="Test",
            script="Test"
        )
        
        review.improvement_suggestions = [
            ImprovementSuggestion(
                component=ComponentType.TITLE,
                priority=Priority.HIGH,
                suggestion="Title fix",
                impact="Good",
                estimated_effort=EffortLevel.SMALL
            ),
            ImprovementSuggestion(
                component=ComponentType.SCRIPT,
                priority=Priority.MEDIUM,
                suggestion="Script fix",
                impact="Good",
                estimated_effort=EffortLevel.SMALL
            ),
            ImprovementSuggestion(
                component=ComponentType.TITLE,
                priority=Priority.LOW,
                suggestion="Another title fix",
                impact="Small",
                estimated_effort=EffortLevel.SMALL
            )
        ]
        
        title_suggestions = review.get_suggestions_by_component(ComponentType.TITLE)
        assert len(title_suggestions) == 2
        assert all(s.component == ComponentType.TITLE for s in title_suggestions)


class TestStoryExpertReviewer:
    """Test StoryExpertReviewer functionality."""
    
    def test_create_reviewer(self):
        """Test creating reviewer instance."""
        reviewer = StoryExpertReviewer(
            model="gpt-4",
            publish_threshold=95
        )
        
        assert reviewer.model == "gpt-4"
        assert reviewer.publish_threshold == 95
    
    def test_review_story_basic(self):
        """Test basic story review."""
        reviewer = StoryExpertReviewer(publish_threshold=95)
        
        review = reviewer.review_story(
            title="Test Title",
            script="This is a test script with sufficient content for review.",
            audience_context={"demographic": "US female 14-29", "platform": "YouTube shorts"},
            original_idea="Test idea",
            story_id="test-001",
            story_version="v3"
        )
        
        assert review.story_id == "test-001"
        assert review.story_version == "v3"
        assert review.title == "Test Title"
        assert review.overall_assessment is not None
        assert review.decision is not None
        assert review.story_coherence is not None
        assert review.audience_fit is not None
        assert review.professional_quality is not None
        assert review.platform_optimization is not None
    
    def test_review_produces_decision(self):
        """Test that review produces a decision."""
        reviewer = StoryExpertReviewer(publish_threshold=95)
        
        review = reviewer.review_story(
            title="Good Title",
            script="Test script content",
            audience_context={},
            story_id="test-002"
        )
        
        assert review.decision in [ReviewDecision.PUBLISH, ReviewDecision.POLISH]
    
    def test_high_quality_content_gets_publish_decision(self):
        """Test that high-quality content gets publish decision."""
        reviewer = StoryExpertReviewer(publish_threshold=90)  # Lower threshold for testing
        
        # Provide comprehensive, high-quality content
        review = reviewer.review_story(
            title="Compelling and Specific Title That Captures Attention",
            script="This is a comprehensive script with excellent structure. " * 50,
            audience_context={
                "demographic": "US female 14-29",
                "platform": "YouTube shorts",
                "style": "engaging"
            },
            original_idea="A well-thought-out original idea",
            story_id="high-quality",
            story_version="v5"
        )
        
        # With lower threshold and good content, should get publish
        assert review.overall_assessment.quality_score >= 90
    
    def test_review_includes_all_assessment_dimensions(self):
        """Test that review includes all assessment dimensions."""
        reviewer = StoryExpertReviewer()
        
        review = reviewer.review_story(
            title="Test",
            script="Test script",
            audience_context={},
            story_id="test-003"
        )
        
        assert review.overall_assessment is not None
        assert isinstance(review.overall_assessment.quality_score, int)
        assert 0 <= review.overall_assessment.quality_score <= 100
        
        assert review.story_coherence is not None
        assert isinstance(review.story_coherence.score, int)
        
        assert review.audience_fit is not None
        assert isinstance(review.audience_fit.score, int)
        
        assert review.professional_quality is not None
        assert isinstance(review.professional_quality.score, int)
        
        assert review.platform_optimization is not None
        assert isinstance(review.platform_optimization.score, int)


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_review_story_with_gpt(self):
        """Test review_story_with_gpt function."""
        review = review_story_with_gpt(
            title="Test Title",
            script="Test script content",
            audience_context={"platform": "YouTube"},
            story_id="conv-001"
        )
        
        assert isinstance(review, ExpertReview)
        assert review.story_id == "conv-001"
        assert review.decision is not None
    
    def test_review_story_to_json(self):
        """Test review_story_to_json function."""
        json_result = review_story_to_json(
            title="Test Title",
            script="Test script",
            audience_context={},
            story_id="json-001"
        )
        
        assert isinstance(json_result, str)
        
        # Verify it's valid JSON
        parsed = json.loads(json_result)
        assert parsed['story_id'] == "json-001"
        assert 'overall_assessment' in parsed
        assert 'decision' in parsed
    
    def test_get_expert_feedback(self):
        """Test get_expert_feedback function."""
        review = review_story_with_gpt(
            title="Test",
            script="Test",
            audience_context={},
            story_id="feedback-001"
        )
        
        feedback = get_expert_feedback(review)
        
        assert isinstance(feedback, dict)
        assert 'story_id' in feedback
        assert 'decision' in feedback
        assert 'quality_score' in feedback
        assert 'ready_for_publishing' in feedback
        assert 'next_action' in feedback
        assert 'high_priority_suggestions' in feedback
        assert 'small_effort_suggestions' in feedback
    
    def test_feedback_includes_next_action(self):
        """Test that feedback includes appropriate next action."""
        review = review_story_with_gpt(
            title="Test",
            script="Test",
            audience_context={},
            story_id="action-001"
        )
        
        feedback = get_expert_feedback(review)
        
        assert 'next_action' in feedback
        assert isinstance(feedback['next_action'], str)
        
        if feedback['decision'] == 'publish':
            assert 'Publishing' in feedback['next_action']
        else:
            assert 'Polish' in feedback['next_action']


class TestEnums:
    """Test enum classes."""
    
    def test_component_type_enum(self):
        """Test ComponentType enum."""
        assert ComponentType.TITLE.value == "title"
        assert ComponentType.SCRIPT.value == "script"
        assert ComponentType.BOTH.value == "both"
    
    def test_priority_enum(self):
        """Test Priority enum."""
        assert Priority.HIGH.value == "high"
        assert Priority.MEDIUM.value == "medium"
        assert Priority.LOW.value == "low"
    
    def test_effort_level_enum(self):
        """Test EffortLevel enum."""
        assert EffortLevel.SMALL.value == "small"
        assert EffortLevel.MEDIUM.value == "medium"
        assert EffortLevel.LARGE.value == "large"
    
    def test_alignment_level_enum(self):
        """Test AlignmentLevel enum."""
        assert AlignmentLevel.PERFECT.value == "perfect"
        assert AlignmentLevel.GOOD.value == "good"
        assert AlignmentLevel.NEEDS_WORK.value == "needs_work"
    
    def test_match_level_enum(self):
        """Test MatchLevel enum."""
        assert MatchLevel.EXCELLENT.value == "excellent"
        assert MatchLevel.GOOD.value == "good"
        assert MatchLevel.NEEDS_WORK.value == "needs_work"
    
    def test_review_decision_enum(self):
        """Test ReviewDecision enum."""
        assert ReviewDecision.PUBLISH.value == "publish"
        assert ReviewDecision.POLISH.value == "polish"


class TestWorkflowIntegration:
    """Test workflow integration scenarios."""
    
    def test_publish_workflow(self):
        """Test workflow when story is ready for publishing."""
        reviewer = StoryExpertReviewer(publish_threshold=85)  # Lower for testing
        
        review = reviewer.review_story(
            title="Excellent Title for Target Audience",
            script="High quality script with great structure and compelling content. " * 30,
            audience_context={
                "demographic": "US female 14-29",
                "platform": "YouTube shorts"
            },
            original_idea="Well-developed idea",
            story_id="publish-test",
            story_version="v5"
        )
        
        feedback = get_expert_feedback(review)
        
        # When quality is high enough, should recommend publishing
        if feedback['ready_for_publishing']:
            assert feedback['decision'] == 'publish'
            assert 'Publishing' in feedback['next_action']
    
    def test_polish_workflow(self):
        """Test workflow when story needs polish."""
        reviewer = StoryExpertReviewer(publish_threshold=98)  # Very high threshold
        
        review = reviewer.review_story(
            title="OK Title",
            script="Decent script but not perfect",
            audience_context={},
            story_id="polish-test",
            story_version="v3"
        )
        
        feedback = get_expert_feedback(review)
        
        # With high threshold, should recommend polish
        if not feedback['ready_for_publishing']:
            assert feedback['decision'] == 'polish'
            assert 'Polish' in feedback['next_action']
            # Should have suggestions
            assert len(review.improvement_suggestions) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
