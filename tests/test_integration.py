"""Integration tests for PrismQ iterative workflow.

These tests demonstrate the 26-stage iterative co-improvement workflow,
particularly the version tracking and cross-module interaction patterns.

Tests are marked with @pytest.mark.integration to distinguish them from unit tests.
"""

import pytest
from tests.helpers import (
    VersionTracker,
    WorkflowStageValidator,
    IntegrationTestHelper,
    create_test_idea,
    assert_version_increment,
    assert_version_sequence,
)


@pytest.mark.integration
class TestIdeaTitleScriptWorkflow:
    """Integration tests for Idea → Title → Script workflow."""
    
    def test_basic_workflow_path(self):
        """Test the basic workflow path through stages."""
        helper = IntegrationTestHelper()
        
        # Start with idea creation
        assert helper.stage_validator.transition_to('idea_creation')
        idea_tracker = helper.start_workflow("Idea")
        idea_tracker.add_version(1, {"stage": "creation"})
        
        # Generate title v1
        assert helper.stage_validator.transition_to('title_v1')
        title_tracker = helper.start_workflow("Title")
        title_tracker.add_version(1, {"stage": "initial", "from_idea": 1})
        
        # Generate script v1
        assert helper.stage_validator.transition_to('script_v1')
        script_tracker = helper.start_workflow("Script")
        script_tracker.add_version(1, {"stage": "initial", "from_title": 1, "from_idea": 1})
        
        # Verify all trackers have v1
        assert idea_tracker.get_current_version() == 1
        assert title_tracker.get_current_version() == 1
        assert script_tracker.get_current_version() == 1
        
        # Verify versions are aligned
        assert helper.validate_cross_version_alignment(1, 1, 1)
        
        # Verify workflow path is valid
        assert helper.stage_validator.is_valid_path()
    
    def test_review_and_improvement_cycle(self):
        """Test the review and improvement cycle creating v2 versions."""
        helper = IntegrationTestHelper()
        
        # Initial versions
        helper.stage_validator.transition_to('idea_creation')
        idea_tracker = helper.start_workflow("Idea")
        idea_tracker.add_version(1)
        
        helper.stage_validator.transition_to('title_v1')
        title_tracker = helper.start_workflow("Title")
        title_tracker.add_version(1)
        
        helper.stage_validator.transition_to('script_v1')
        script_tracker = helper.start_workflow("Script")
        script_tracker.add_version(1)
        
        # Review title based on script
        assert helper.stage_validator.transition_to('title_review')
        
        # Create improved title v2
        assert helper.stage_validator.transition_to('title_v2')
        title_tracker.add_version(2, {"stage": "reviewed", "feedback": "script_review"})
        
        # Create improved script v2 based on new title
        assert helper.stage_validator.transition_to('script_v2')
        script_tracker.add_version(2, {"stage": "reviewed", "from_title": 2})
        
        # Verify version sequences
        assert_version_sequence(title_tracker.versions)
        assert_version_sequence(script_tracker.versions)
        
        # Verify current versions
        assert title_tracker.get_current_version() == 2
        assert script_tracker.get_current_version() == 2
        
        # Versions should still be aligned (within 1)
        assert helper.validate_cross_version_alignment(1, 2, 2)
    
    def test_multiple_iteration_cycles(self):
        """Test multiple iteration cycles up to v3."""
        helper = IntegrationTestHelper()
        
        # Setup initial v1 versions
        helper.stage_validator.transition_to('idea_creation')
        idea_tracker = helper.start_workflow("Idea")
        idea_tracker.add_version(1)
        
        helper.stage_validator.transition_to('title_v1')
        title_tracker = helper.start_workflow("Title")
        title_tracker.add_version(1)
        
        helper.stage_validator.transition_to('script_v1')
        script_tracker = helper.start_workflow("Script")
        script_tracker.add_version(1)
        
        # First improvement cycle (v1 → v2)
        helper.stage_validator.transition_to('title_review')
        helper.stage_validator.transition_to('title_v2')
        title_tracker.add_version(2)
        
        helper.stage_validator.transition_to('script_v2')
        script_tracker.add_version(2)
        
        # Second improvement cycle (v2 → v3)
        helper.stage_validator.transition_to('title_v3')
        title_tracker.add_version(3)
        
        helper.stage_validator.transition_to('script_v3')
        script_tracker.add_version(3)
        
        # Verify all version sequences are valid
        assert_version_sequence(idea_tracker.versions)
        assert_version_sequence(title_tracker.versions)
        assert_version_sequence(script_tracker.versions)
        
        # Verify final versions
        assert idea_tracker.get_current_version() == 1  # Idea stays at v1
        assert title_tracker.get_current_version() == 3
        assert script_tracker.get_current_version() == 3
        
        # Verify alignment
        assert helper.validate_cross_version_alignment(1, 3, 3)
        
        # Verify workflow path
        assert helper.stage_validator.is_valid_path()


@pytest.mark.integration
@pytest.mark.version_tracking
class TestVersionTracking:
    """Integration tests specifically for version tracking."""
    
    def test_version_increment_through_workflow(self):
        """Test that versions increment correctly through workflow stages."""
        title_tracker = VersionTracker("Title")
        
        # v1: Initial generation
        title_tracker.add_version(1, {"stage": "initial"})
        
        # v2: After review
        title_tracker.add_version(2, {"stage": "reviewed"})
        assert_version_increment(1, 2)
        
        # v3: After refinement
        title_tracker.add_version(3, {"stage": "refined"})
        assert_version_increment(2, 3)
        
        # Verify complete sequence
        assert_version_sequence([1, 2, 3])
    
    def test_version_metadata_tracking(self):
        """Test that version metadata is tracked correctly."""
        script_tracker = VersionTracker("Script")
        
        script_tracker.add_version(1, {
            "from_idea": 1,
            "from_title": 1,
            "review_status": "pending"
        })
        
        script_tracker.add_version(2, {
            "from_idea": 1,
            "from_title": 2,
            "review_status": "approved",
            "changes": ["Improved flow", "Better alignment with title"]
        })
        
        history = script_tracker.get_history()
        
        # Verify v1 metadata
        assert history[0]['version'] == 1
        assert history[0]['metadata']['from_idea'] == 1
        assert history[0]['metadata']['from_title'] == 1
        
        # Verify v2 metadata
        assert history[1]['version'] == 2
        assert history[1]['metadata']['from_title'] == 2
        assert "changes" in history[1]['metadata']
    
    def test_parallel_version_tracking(self):
        """Test tracking versions for multiple entities in parallel."""
        idea_tracker = VersionTracker("Idea")
        title_tracker = VersionTracker("Title")
        script_tracker = VersionTracker("Script")
        
        # All start at v1
        idea_tracker.add_version(1)
        title_tracker.add_version(1)
        script_tracker.add_version(1)
        
        # Title and Script progress to v2
        title_tracker.add_version(2)
        script_tracker.add_version(2)
        
        # Script progresses to v3
        script_tracker.add_version(3)
        
        # Verify individual sequences
        assert_version_sequence(idea_tracker.versions)
        assert_version_sequence(title_tracker.versions)
        assert_version_sequence(script_tracker.versions)
        
        # Verify counts
        assert idea_tracker.get_version_count() == 1
        assert title_tracker.get_version_count() == 2
        assert script_tracker.get_version_count() == 3


@pytest.mark.integration
class TestWorkflowStageTransitions:
    """Integration tests for workflow stage transitions."""
    
    def test_forward_progression(self):
        """Test forward progression through workflow stages."""
        validator = WorkflowStageValidator()
        
        # Forward progression
        stages = [
            'idea_creation',
            'title_v1',
            'script_v1',
            'title_review',
            'title_v2',
            'script_v2'
        ]
        
        for stage in stages:
            assert validator.transition_to(stage), f"Failed to transition to {stage}"
        
        assert validator.is_valid_path()
        assert validator.get_stage_history() == stages
    
    def test_iterative_improvement_path(self):
        """Test path through multiple improvement iterations."""
        validator = WorkflowStageValidator()
        
        # Initial creation
        validator.transition_to('idea_creation')
        validator.transition_to('title_v1')
        validator.transition_to('script_v1')
        
        # First iteration (v1 → v2)
        validator.transition_to('title_review')
        validator.transition_to('title_v2')
        validator.transition_to('script_v2')
        
        # Second iteration (v2 → v3)
        validator.transition_to('title_v3')
        validator.transition_to('script_v3')
        
        assert validator.is_valid_path()
        
        # Verify we went through all expected stages
        history = validator.get_stage_history()
        assert 'idea_creation' in history
        assert 'title_v1' in history
        assert 'title_v2' in history
        assert 'title_v3' in history
    
    def test_invalid_stage_skipping(self):
        """Test that skipping stages is not allowed."""
        validator = WorkflowStageValidator()
        
        validator.transition_to('idea_creation')
        validator.transition_to('title_v1')
        
        # Cannot skip directly to v3
        assert not validator.transition_to('title_v3')
        
        # Cannot skip script generation
        assert not validator.transition_to('title_review')
        
        # Must go through proper stages
        assert validator.transition_to('script_v1')


@pytest.mark.integration
class TestCrossModuleAlignment:
    """Integration tests for cross-module version alignment."""
    
    def test_synchronized_versions(self):
        """Test that versions can stay synchronized across modules."""
        helper = IntegrationTestHelper()
        
        idea_tracker = helper.start_workflow("Idea")
        title_tracker = helper.start_workflow("Title")
        script_tracker = helper.start_workflow("Script")
        
        # All at v1
        idea_tracker.add_version(1)
        title_tracker.add_version(1)
        script_tracker.add_version(1)
        
        assert helper.validate_cross_version_alignment(1, 1, 1)
        
        # All at v2
        idea_tracker.add_version(2)
        title_tracker.add_version(2)
        script_tracker.add_version(2)
        
        assert helper.validate_cross_version_alignment(2, 2, 2)
    
    def test_acceptable_version_drift(self):
        """Test acceptable version drift during development."""
        helper = IntegrationTestHelper()
        
        # Idea at v1, others at v2 (acceptable)
        assert helper.validate_cross_version_alignment(1, 2, 2)
        
        # Title at v3, others at v2 (acceptable)
        assert helper.validate_cross_version_alignment(2, 3, 2)
        
        # Script ahead by 1 (acceptable)
        assert helper.validate_cross_version_alignment(2, 2, 3)
    
    def test_unacceptable_version_drift(self):
        """Test detection of unacceptable version drift."""
        helper = IntegrationTestHelper()
        
        # Title and Script too far apart (more than 1)
        assert not helper.validate_cross_version_alignment(1, 2, 4)
        
        # Large drift in title/script alignment
        assert not helper.validate_cross_version_alignment(1, 3, 5)
    
    def test_version_alignment_during_iteration(self):
        """Test version alignment through a complete iteration cycle."""
        helper = IntegrationTestHelper()
        
        idea_tracker = helper.start_workflow("Idea")
        title_tracker = helper.start_workflow("Title")
        script_tracker = helper.start_workflow("Script")
        
        # Initial state
        idea_tracker.add_version(1)
        title_tracker.add_version(1)
        script_tracker.add_version(1)
        assert helper.validate_cross_version_alignment(1, 1, 1)
        
        # Title updated after review
        title_tracker.add_version(2)
        assert helper.validate_cross_version_alignment(1, 2, 1)
        
        # Script updated to match new title
        script_tracker.add_version(2)
        assert helper.validate_cross_version_alignment(1, 2, 2)
        
        # Final refinement
        title_tracker.add_version(3)
        script_tracker.add_version(3)
        assert helper.validate_cross_version_alignment(1, 3, 3)


@pytest.mark.integration
@pytest.mark.slow
class TestCompleteWorkflowScenario:
    """Integration test for a complete workflow scenario."""
    
    def test_full_workflow_from_idea_to_refinement(self):
        """Test a complete workflow from idea creation to final refinement.
        
        This test simulates the full 26-stage workflow focusing on the
        Idea → Title → Script → Review → Improve cycle.
        """
        helper = IntegrationTestHelper()
        
        # Stage 1: Idea Creation
        assert helper.stage_validator.transition_to('idea_creation')
        idea_tracker = helper.start_workflow("Idea")
        idea_tracker.add_version(1, {"stage": "creation", "status": "draft"})
        
        # Stage 2: Title v1 Generation
        assert helper.stage_validator.transition_to('title_v1')
        title_tracker = helper.start_workflow("Title")
        title_tracker.add_version(1, {
            "stage": "initial",
            "from_idea": 1,
            "variants": 5
        })
        
        # Stage 3: Script v1 Generation
        assert helper.stage_validator.transition_to('script_v1')
        script_tracker = helper.start_workflow("Script")
        script_tracker.add_version(1, {
            "stage": "initial",
            "from_idea": 1,
            "from_title": 1,
            "word_count": 1500
        })
        
        # Verify initial alignment
        assert helper.validate_cross_version_alignment(1, 1, 1)
        
        # Stage 4: Title Review (cross-validation)
        assert helper.stage_validator.transition_to('title_review')
        
        # Stage 5: Title v2 (improved based on script)
        assert helper.stage_validator.transition_to('title_v2')
        title_tracker.add_version(2, {
            "stage": "reviewed",
            "review_source": "script",
            "improvements": ["better alignment", "clearer promise"]
        })
        
        # Stage 6: Script v2 (updated for new title)
        assert helper.stage_validator.transition_to('script_v2')
        script_tracker.add_version(2, {
            "stage": "reviewed",
            "from_title": 2,
            "word_count": 1600
        })
        
        # Verify alignment after first iteration
        assert helper.validate_cross_version_alignment(1, 2, 2)
        
        # Stage 7: Title v3 (final refinement)
        assert helper.stage_validator.transition_to('title_v3')
        title_tracker.add_version(3, {
            "stage": "refined",
            "status": "approved"
        })
        
        # Stage 8: Script v3 (final refinement)
        assert helper.stage_validator.transition_to('script_v3')
        script_tracker.add_version(3, {
            "stage": "refined",
            "from_title": 3,
            "status": "approved",
            "word_count": 1550
        })
        
        # Final verification
        assert helper.validate_cross_version_alignment(1, 3, 3)
        assert helper.stage_validator.is_valid_path()
        
        # Verify version sequences
        assert_version_sequence(idea_tracker.versions)
        assert_version_sequence(title_tracker.versions)
        assert_version_sequence(script_tracker.versions)
        
        # Verify version counts
        assert idea_tracker.get_version_count() == 1  # Idea stays at v1
        assert title_tracker.get_version_count() == 3  # Through refinement
        assert script_tracker.get_version_count() == 3  # Through refinement
        
        # Verify workflow stages
        stage_history = helper.stage_validator.get_stage_history()
        expected_stages = [
            'idea_creation',
            'title_v1',
            'script_v1',
            'title_review',
            'title_v2',
            'script_v2',
            'title_v3',
            'script_v3'
        ]
        assert stage_history == expected_stages


@pytest.mark.integration
class TestManualCreationPipeline:
    """Integration tests for manual Idea creation pipeline (Worker10 review).
    
    This test class verifies that the pipeline for manual Idea object creation
    starts correctly and follows the expected sequence of stages:
    
    1. Idea.Creation (manual entry point)
    2. Title.From.Idea (v1)
    3. Script.From.Title.Idea (v1)
    4. Review.Title.By.Script.Idea
    5. Title.From.Script.Review.Title (v2)
    6. Review.Script.By.Title.Idea
    7. Script.From.Title.Review.Script (v2)
    """
    
    def test_manual_creation_pipeline_sequence(self):
        """Test that manual creation pipeline follows the correct stage sequence.
        
        This test verifies the complete pipeline from manual Idea.Creation through
        the first co-improvement cycle (v1 → v2) with proper review stages.
        """
        helper = IntegrationTestHelper()
        
        # Stage 1: Idea.Creation (manual entry point)
        assert helper.stage_validator.transition_to('idea_creation'), \
            "Failed to start with manual Idea.Creation"
        idea_tracker = helper.start_workflow("Idea")
        idea_tracker.add_version(1, {
            "stage": "creation",
            "method": "manual",
            "description": "Manually created idea for testing pipeline"
        })
        
        # Stage 2: Title.From.Idea (v1)
        assert helper.stage_validator.transition_to('title_v1'), \
            "Failed to transition from Idea.Creation to Title.From.Idea"
        title_tracker = helper.start_workflow("Title")
        title_tracker.add_version(1, {
            "stage": "from_idea",
            "from_idea": 1,
            "description": "Initial title generated from idea"
        })
        
        # Stage 3: Script.From.Title.Idea (v1)
        assert helper.stage_validator.transition_to('script_v1'), \
            "Failed to transition to Script.From.Title.Idea"
        script_tracker = helper.start_workflow("Script")
        script_tracker.add_version(1, {
            "stage": "from_title_and_idea",
            "from_title": 1,
            "from_idea": 1,
            "description": "Initial script generated from title and idea"
        })
        
        # Stage 4: Review.Title.By.Script.Idea
        assert helper.stage_validator.transition_to('title_review'), \
            "Failed to transition to Review.Title.By.Script.Idea"
        
        # Stage 5: Title.From.Script.Review.Title (v2 - improved title)
        assert helper.stage_validator.transition_to('title_v2'), \
            "Failed to transition to Title.From.Script.Review.Title"
        title_tracker.add_version(2, {
            "stage": "from_review",
            "from_script": 1,
            "reviewed_by": "script_and_idea",
            "description": "Improved title based on script review"
        })
        
        # Stage 6: Review.Script.By.Title.Idea
        assert helper.stage_validator.transition_to('script_review'), \
            "Failed to transition to Review.Script.By.Title.Idea"
        
        # Stage 7: Script.From.Title.Review.Script (v2 - improved script)
        assert helper.stage_validator.transition_to('script_v2'), \
            "Failed to transition to Script.From.Title.Review.Script"
        script_tracker.add_version(2, {
            "stage": "from_review",
            "from_title": 2,
            "reviewed_by": "title_and_idea",
            "description": "Improved script based on title review"
        })
        
        # Verify all version sequences are valid
        assert_version_sequence(idea_tracker.versions), \
            "Idea version sequence is invalid"
        assert_version_sequence(title_tracker.versions), \
            "Title version sequence is invalid"
        assert_version_sequence(script_tracker.versions), \
            "Script version sequence is invalid"
        
        # Verify current versions after first improvement cycle
        assert idea_tracker.get_current_version() == 1, \
            "Idea should remain at v1"
        assert title_tracker.get_current_version() == 2, \
            "Title should be at v2 after review cycle"
        assert script_tracker.get_current_version() == 2, \
            "Script should be at v2 after review cycle"
        
        # Verify versions are properly aligned (within 1 version of each other)
        assert helper.validate_cross_version_alignment(1, 2, 2), \
            "Versions are not properly aligned"
        
        # Verify the complete stage history matches expected sequence
        stage_history = helper.stage_validator.get_stage_history()
        expected_stages = [
            'idea_creation',         # Idea.Creation
            'title_v1',              # Title.From.Idea
            'script_v1',             # Script.From.Title.Idea
            'title_review',          # Review.Title.By.Script.Idea
            'title_v2',              # Title.From.Script.Review.Title
            'script_review',         # Review.Script.By.Title.Idea
            'script_v2'              # Script.From.Title.Review.Script
        ]
        assert stage_history == expected_stages, \
            f"Stage history doesn't match expected sequence.\nExpected: {expected_stages}\nActual: {stage_history}"
        
        # Verify the workflow path is valid
        assert helper.stage_validator.is_valid_path(), \
            "Workflow path is not valid according to stage transition rules"
    
    def test_manual_creation_pipeline_metadata_tracking(self):
        """Test that metadata is properly tracked through manual creation pipeline."""
        helper = IntegrationTestHelper()
        
        # Create workflow with detailed metadata
        helper.stage_validator.transition_to('idea_creation')
        idea_tracker = helper.start_workflow("Idea")
        idea_tracker.add_version(1, {
            "method": "manual",
            "author": "content_creator",
            "timestamp": "2025-11-24T00:00:00Z"
        })
        
        helper.stage_validator.transition_to('title_v1')
        title_tracker = helper.start_workflow("Title")
        title_tracker.add_version(1, {
            "from_idea": 1,
            "generation_method": "ai_assisted"
        })
        
        helper.stage_validator.transition_to('script_v1')
        script_tracker = helper.start_workflow("Script")
        script_tracker.add_version(1, {
            "from_idea": 1,
            "from_title": 1,
            "generation_method": "ai_assisted"
        })
        
        # Progress through review cycle
        helper.stage_validator.transition_to('title_review')
        helper.stage_validator.transition_to('title_v2')
        title_tracker.add_version(2, {
            "from_review": True,
            "improvements": ["better alignment with script", "SEO optimization"]
        })
        
        helper.stage_validator.transition_to('script_review')
        helper.stage_validator.transition_to('script_v2')
        script_tracker.add_version(2, {
            "from_review": True,
            "improvements": ["better flow", "aligned with improved title"]
        })
        
        # Verify metadata is preserved in history
        idea_history = idea_tracker.get_history()
        assert idea_history[0]['metadata']['method'] == 'manual'
        assert idea_history[0]['metadata']['author'] == 'content_creator'
        
        title_history = title_tracker.get_history()
        assert title_history[0]['metadata']['from_idea'] == 1
        assert title_history[1]['metadata']['from_review'] == True
        assert len(title_history[1]['metadata']['improvements']) == 2
        
        script_history = script_tracker.get_history()
        assert script_history[0]['metadata']['from_title'] == 1
        assert script_history[1]['metadata']['from_review'] == True
        assert 'improvements' in script_history[1]['metadata']
    
    def test_manual_creation_pipeline_version_alignment(self):
        """Test version alignment requirements in manual creation pipeline.
        
        The manual creation pipeline should maintain proper version alignment:
        - Idea stays at v1 (doesn't iterate)
        - Title and Script co-improve together
        - Versions should be within 1 of each other during co-improvement
        """
        helper = IntegrationTestHelper()
        
        # Initial creation (all at v1)
        helper.stage_validator.transition_to('idea_creation')
        idea_tracker = helper.start_workflow("Idea")
        idea_tracker.add_version(1)
        
        helper.stage_validator.transition_to('title_v1')
        title_tracker = helper.start_workflow("Title")
        title_tracker.add_version(1)
        
        helper.stage_validator.transition_to('script_v1')
        script_tracker = helper.start_workflow("Script")
        script_tracker.add_version(1)
        
        # Verify initial alignment
        assert helper.validate_cross_version_alignment(1, 1, 1), \
            "Initial versions should be aligned"
        
        # First co-improvement cycle (v1 → v2)
        helper.stage_validator.transition_to('title_review')
        helper.stage_validator.transition_to('title_v2')
        title_tracker.add_version(2)
        
        # After title improvement, alignment should still be valid
        # (title is one ahead, which is acceptable during co-improvement)
        assert helper.validate_cross_version_alignment(1, 2, 1), \
            "Alignment should be valid with title at v2, script at v1"
        
        helper.stage_validator.transition_to('script_review')
        helper.stage_validator.transition_to('script_v2')
        script_tracker.add_version(2)
        
        # After both improvements, versions should be aligned again
        assert helper.validate_cross_version_alignment(1, 2, 2), \
            "Versions should be aligned after co-improvement cycle"
        
        # Verify idea remains at v1 throughout
        assert idea_tracker.get_current_version() == 1, \
            "Idea should never iterate beyond v1"
        
        # Verify title and script progressed together
        assert title_tracker.get_current_version() == 2
        assert script_tracker.get_current_version() == 2
