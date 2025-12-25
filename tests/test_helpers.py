"""Unit tests for test helpers module.

Tests the test helper utilities for version tracking and workflow validation.
"""

import pytest

from tests.helpers import (
    IntegrationTestHelper,
    VersionTracker,
    WorkflowStageValidator,
    assert_version_increment,
    assert_version_sequence,
    create_version_history,
)


class TestVersionTracker:
    """Tests for VersionTracker helper class."""

    def test_create_tracker(self):
        """Test creating a version tracker."""
        tracker = VersionTracker(entity_type="Idea")

        assert tracker.entity_type == "Idea"
        assert tracker.versions == []
        assert tracker.history == []

    def test_add_first_version(self):
        """Test adding the first version."""
        tracker = VersionTracker(entity_type="Title")
        tracker.add_version(1)

        assert tracker.get_current_version() == 1
        assert tracker.get_version_count() == 1

    def test_add_sequential_versions(self):
        """Test adding multiple sequential versions."""
        tracker = VersionTracker(entity_type="Script")

        tracker.add_version(1)
        tracker.add_version(2)
        tracker.add_version(3)

        assert tracker.get_current_version() == 3
        assert tracker.get_version_count() == 3
        assert tracker.versions == [1, 2, 3]

    def test_first_version_must_be_one(self):
        """Test that first version must be 1."""
        tracker = VersionTracker(entity_type="Idea")

        with pytest.raises(ValueError, match="First version must be 1"):
            tracker.add_version(2)

    def test_versions_must_be_sequential(self):
        """Test that versions must increment by 1."""
        tracker = VersionTracker(entity_type="Idea")
        tracker.add_version(1)

        with pytest.raises(ValueError, match="Versions must be sequential"):
            tracker.add_version(3)  # Skipping version 2

    def test_add_version_with_metadata(self):
        """Test adding version with metadata."""
        tracker = VersionTracker(entity_type="Idea")
        metadata = {"change": "Updated concept", "reason": "Review feedback"}

        tracker.add_version(1, metadata)

        history = tracker.get_history()
        assert len(history) == 1
        assert history[0]["version"] == 1
        assert history[0]["metadata"] == metadata

    def test_validate_sequence_valid(self):
        """Test validating a correct sequence."""
        tracker = VersionTracker(entity_type="Idea")
        tracker.add_version(1)
        tracker.add_version(2)
        tracker.add_version(3)

        assert tracker.validate_sequence() is True

    def test_validate_sequence_empty(self):
        """Test validating an empty sequence."""
        tracker = VersionTracker(entity_type="Idea")

        assert tracker.validate_sequence() is True

    def test_get_history(self):
        """Test retrieving version history."""
        tracker = VersionTracker(entity_type="Title")

        tracker.add_version(1, {"type": "initial"})
        tracker.add_version(2, {"type": "reviewed"})

        history = tracker.get_history()
        assert len(history) == 2
        assert history[0]["version"] == 1
        assert history[1]["version"] == 2

    def test_get_current_version_empty(self):
        """Test getting current version when no versions added."""
        tracker = VersionTracker(entity_type="Idea")

        assert tracker.get_current_version() is None


class TestWorkflowStageValidator:
    """Tests for WorkflowStageValidator helper class."""

    def test_create_validator(self):
        """Test creating a workflow stage validator."""
        validator = WorkflowStageValidator()

        assert validator.current_stage is None
        assert validator.stage_history == []

    def test_first_stage_must_be_idea_creation(self):
        """Test that first stage must be PrismQ.T.Idea.From.User."""
        validator = WorkflowStageValidator()

        assert validator.transition_to("PrismQ.T.Idea.From.User") is True
        assert validator.current_stage == "PrismQ.T.Idea.From.User"

    def test_cannot_start_with_invalid_stage(self):
        """Test that workflow cannot start with arbitrary stage."""
        validator = WorkflowStageValidator()

        assert validator.transition_to("PrismQ.T.Title.From.Idea") is False
        assert validator.current_stage is None

    def test_valid_transition(self):
        """Test valid stage transition."""
        validator = WorkflowStageValidator()

        validator.transition_to("PrismQ.T.Idea.From.User")
        assert validator.transition_to("PrismQ.T.Title.From.Idea") is True
        assert validator.current_stage == "PrismQ.T.Title.From.Idea"

    def test_invalid_transition(self):
        """Test invalid stage transition."""
        validator = WorkflowStageValidator()

        validator.transition_to("PrismQ.T.Idea.From.User")
        # Can't skip to script generation directly without title
        assert validator.transition_to("PrismQ.T.Script.From.Idea.Title") is False
        assert validator.current_stage == "PrismQ.T.Idea.From.User"  # Should stay in current stage

    def test_stage_history_tracking(self):
        """Test that stage history is tracked correctly."""
        validator = WorkflowStageValidator()

        validator.transition_to("PrismQ.T.Idea.From.User")
        validator.transition_to("PrismQ.T.Title.From.Idea")
        validator.transition_to("PrismQ.T.Script.From.Idea.Title")

        history = validator.get_stage_history()
        assert history == [
            "PrismQ.T.Idea.From.User",
            "PrismQ.T.Title.From.Idea",
            "PrismQ.T.Script.From.Idea.Title",
        ]

    def test_is_valid_path_true(self):
        """Test that valid path is recognized."""
        validator = WorkflowStageValidator()

        validator.transition_to("PrismQ.T.Idea.From.User")
        validator.transition_to("PrismQ.T.Title.From.Idea")
        validator.transition_to("PrismQ.T.Script.From.Idea.Title")

        assert validator.is_valid_path() is True

    def test_is_valid_path_empty(self):
        """Test that empty path is valid."""
        validator = WorkflowStageValidator()

        assert validator.is_valid_path() is True

    def test_iteration_path(self):
        """Test iteration back for refinement."""
        validator = WorkflowStageValidator()

        validator.transition_to("PrismQ.T.Idea.From.User")
        validator.transition_to("PrismQ.T.Title.From.Idea")
        validator.transition_to("PrismQ.T.Script.From.Idea.Title")
        validator.transition_to("PrismQ.T.Review.Title.From.Script.Idea")
        validator.transition_to("PrismQ.T.Title.From.Title.Review.Script")

        assert validator.current_stage == "PrismQ.T.Title.From.Title.Review.Script"
        assert validator.is_valid_path() is True


class TestVersionAssertions:
    """Tests for version assertion helper functions."""

    def test_assert_version_increment_valid(self):
        """Test valid version increment assertion."""
        # Should not raise
        assert_version_increment(1, 2)
        assert_version_increment(5, 6)

    def test_assert_version_increment_invalid(self):
        """Test invalid version increment assertion."""
        with pytest.raises(AssertionError, match="should increment by 1"):
            assert_version_increment(1, 3)

        with pytest.raises(AssertionError, match="should increment by 1"):
            assert_version_increment(2, 2)

    def test_assert_version_sequence_valid(self):
        """Test valid version sequence assertion."""
        # Should not raise
        assert_version_sequence([1, 2, 3, 4])
        assert_version_sequence([1])
        assert_version_sequence([])

    def test_assert_version_sequence_invalid_start(self):
        """Test sequence starting with wrong number."""
        with pytest.raises(AssertionError, match="First version should be 1"):
            assert_version_sequence([0, 1, 2])

        with pytest.raises(AssertionError, match="First version should be 1"):
            assert_version_sequence([2, 3, 4])

    def test_assert_version_sequence_invalid_gap(self):
        """Test sequence with gap."""
        with pytest.raises(AssertionError, match="Version sequence broken"):
            assert_version_sequence([1, 2, 4])

        with pytest.raises(AssertionError, match="Version sequence broken"):
            assert_version_sequence([1, 3, 4])


class TestCreateVersionHistory:
    """Tests for create_version_history helper function."""

    def test_create_simple_history(self):
        """Test creating version history without metadata."""
        tracker = create_version_history("Idea", num_versions=3)

        assert tracker.entity_type == "Idea"
        assert tracker.get_version_count() == 3
        assert tracker.versions == [1, 2, 3]

    def test_create_history_with_metadata(self):
        """Test creating version history with metadata function."""

        def metadata_fn(v):
            return {"version": v, "type": f"v{v}"}

        tracker = create_version_history("Title", num_versions=2, metadata_fn=metadata_fn)

        history = tracker.get_history()
        assert len(history) == 2
        assert history[0]["metadata"]["type"] == "v1"
        assert history[1]["metadata"]["type"] == "v2"

    def test_create_single_version_history(self):
        """Test creating history with single version."""
        tracker = create_version_history("Script", num_versions=1)

        assert tracker.get_current_version() == 1
        assert tracker.get_version_count() == 1


class TestIntegrationTestHelper:
    """Tests for IntegrationTestHelper class."""

    def test_create_helper(self):
        """Test creating integration test helper."""
        helper = IntegrationTestHelper()

        assert helper.idea_tracker is None
        assert helper.title_tracker is None
        assert helper.script_tracker is None
        assert isinstance(helper.stage_validator, WorkflowStageValidator)

    def test_start_workflow_idea(self):
        """Test starting workflow for Idea."""
        helper = IntegrationTestHelper()
        tracker = helper.start_workflow("Idea")

        assert tracker.entity_type == "Idea"
        assert helper.idea_tracker is tracker

    def test_start_workflow_title(self):
        """Test starting workflow for Title."""
        helper = IntegrationTestHelper()
        tracker = helper.start_workflow("Title")

        assert tracker.entity_type == "Title"
        assert helper.title_tracker is tracker

    def test_start_workflow_script(self):
        """Test starting workflow for Script."""
        helper = IntegrationTestHelper()
        tracker = helper.start_workflow("Script")

        assert tracker.entity_type == "Script"
        assert helper.script_tracker is tracker

    def test_get_all_trackers(self):
        """Test getting all trackers."""
        helper = IntegrationTestHelper()

        idea_tracker = helper.start_workflow("Idea")
        title_tracker = helper.start_workflow("Title")

        trackers = helper.get_all_trackers()

        assert trackers["Idea"] is idea_tracker
        assert trackers["Title"] is title_tracker
        assert trackers["Script"] is None

    def test_validate_cross_version_alignment_aligned(self):
        """Test validation when versions are aligned."""
        helper = IntegrationTestHelper()

        # All same version
        assert helper.validate_cross_version_alignment(2, 2, 2) is True

        # Within 1 version
        assert helper.validate_cross_version_alignment(2, 3, 2) is True
        assert helper.validate_cross_version_alignment(1, 2, 2) is True

    def test_validate_cross_version_alignment_misaligned(self):
        """Test validation when versions are misaligned."""
        helper = IntegrationTestHelper()

        # Title and Script more than 1 version apart
        assert helper.validate_cross_version_alignment(1, 2, 4) is False
        assert helper.validate_cross_version_alignment(1, 5, 2) is False

    def test_validate_cross_version_alignment_edge_cases(self):
        """Test validation edge cases."""
        helper = IntegrationTestHelper()

        # All at version 1
        assert helper.validate_cross_version_alignment(1, 1, 1) is True

        # Mixed but within range
        assert helper.validate_cross_version_alignment(5, 5, 6) is True
        assert helper.validate_cross_version_alignment(5, 6, 5) is True
