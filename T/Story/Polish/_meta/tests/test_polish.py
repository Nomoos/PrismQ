"""Tests for Story Polish module."""

import sys
import os
import pytest
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from polish import (
    StoryPolish,
    StoryPolisher,
    PolishConfig,
    ChangeLogEntry,
    ComponentType,
    ChangeType,
    PriorityLevel,
    polish_story_with_gpt,
    polish_story_to_json
)


class TestChangeLogEntry:
    """Tests for ChangeLogEntry data model."""
    
    def test_create_change_log_entry(self):
        """Test creating a change log entry."""
        entry = ChangeLogEntry(
            component=ComponentType.TITLE,
            change_type=ChangeType.CAPITALIZATION,
            before="The House: and Hunts",
            after="The House: And Hunts",
            rationale="Capitalize for visual impact"
        )
        
        assert entry.component == ComponentType.TITLE
        assert entry.change_type == ChangeType.CAPITALIZATION
        assert "and Hunts" in entry.before
        assert "And Hunts" in entry.after
    
    def test_change_log_to_dict(self):
        """Test converting change log to dictionary."""
        entry = ChangeLogEntry(
            component=ComponentType.SCRIPT,
            change_type=ChangeType.OPENING_ENHANCEMENT,
            before="Original opening",
            after="Enhanced opening",
            rationale="Add relatable context"
        )
        
        data = entry.to_dict()
        
        assert data['component'] == 'script'
        assert data['change_type'] == 'opening_enhancement'
        assert data['rationale'] == "Add relatable context"
    
    def test_change_log_from_dict(self):
        """Test creating change log from dictionary."""
        data = {
            'component': 'title',
            'change_type': 'word_choice',
            'before': 'Old title',
            'after': 'New title',
            'rationale': 'Better word choice',
            'suggestion_reference': 'Test suggestion'
        }
        
        entry = ChangeLogEntry.from_dict(data)
        
        assert entry.component == ComponentType.TITLE
        assert entry.change_type == ChangeType.WORD_CHOICE
        assert entry.suggestion_reference == 'Test suggestion'


class TestPolishConfig:
    """Tests for PolishConfig."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = PolishConfig()
        
        assert config.gpt_model == "gpt-4"
        assert config.max_iterations == 2
        assert config.apply_priority_threshold == PriorityLevel.HIGH
        assert config.preserve_length is True
        assert config.preserve_essence is True
        assert config.target_quality_score == 95
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = PolishConfig(
            gpt_model="gpt-5",
            max_iterations=3,
            apply_priority_threshold=PriorityLevel.MEDIUM,
            target_quality_score=98
        )
        
        assert config.gpt_model == "gpt-5"
        assert config.max_iterations == 3
        assert config.apply_priority_threshold == PriorityLevel.MEDIUM
        assert config.target_quality_score == 98
    
    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = PolishConfig(gpt_model="gpt-4")
        data = config.to_dict()
        
        assert data['gpt_model'] == "gpt-4"
        assert data['max_iterations'] == 2
        assert data['apply_priority_threshold'] == "high"


class TestStoryPolish:
    """Tests for StoryPolish data model."""
    
    def test_create_story_polish(self):
        """Test creating a story polish result."""
        polish = StoryPolish(
            polish_id="polish_001",
            story_id="story_001",
            original_title="Original Title",
            polished_title="Polished Title",
            original_script="Original script text",
            polished_script="Polished script text",
            original_quality_score=92,
            expected_quality_score=96,
            quality_delta=4,
            iteration_number=1
        )
        
        assert polish.polish_id == "polish_001"
        assert polish.story_id == "story_001"
        assert polish.quality_delta == 4
        assert polish.iteration_number == 1
        assert polish.ready_for_review is True
    
    def test_story_polish_to_dict(self):
        """Test converting story polish to dictionary."""
        polish = StoryPolish(
            polish_id="polish_002",
            story_id="story_002",
            original_title="Test",
            polished_title="Test Polish",
            original_script="Script",
            polished_script="Polished Script"
        )
        
        data = polish.to_dict()
        
        assert data['polish_id'] == "polish_002"
        assert data['story_id'] == "story_002"
        assert 'created_at' in data
    
    def test_story_polish_to_json(self):
        """Test converting story polish to JSON."""
        polish = StoryPolish(
            polish_id="polish_003",
            story_id="story_003",
            original_title="JSON Test",
            polished_title="JSON Test Polish",
            original_script="Script",
            polished_script="Script Polish"
        )
        
        json_str = polish.to_json()
        
        assert "polish_003" in json_str
        assert "story_003" in json_str
        assert isinstance(json_str, str)
    
    def test_story_polish_from_dict(self):
        """Test creating story polish from dictionary."""
        data = {
            'polish_id': 'polish_004',
            'story_id': 'story_004',
            'original_title': 'Original',
            'polished_title': 'Polished',
            'original_script': 'Script',
            'polished_script': 'Polish Script',
            'change_log': [],
            'quality_delta': 5
        }
        
        polish = StoryPolish.from_dict(data)
        
        assert polish.polish_id == 'polish_004'
        assert polish.quality_delta == 5


class TestStoryPolisher:
    """Tests for StoryPolisher class."""
    
    def test_create_polisher_default_config(self):
        """Test creating polisher with default config."""
        polisher = StoryPolisher()
        
        assert polisher.config is not None
        assert polisher.config.gpt_model == "gpt-4"
    
    def test_create_polisher_custom_config(self):
        """Test creating polisher with custom config."""
        config = PolishConfig(gpt_model="gpt-5")
        polisher = StoryPolisher(config)
        
        assert polisher.config.gpt_model == "gpt-5"
    
    def test_filter_suggestions_by_priority_high(self):
        """Test filtering suggestions by high priority."""
        polisher = StoryPolisher()
        
        suggestions = [
            {'component': 'title', 'priority': 'high', 'suggestion': 'High'},
            {'component': 'title', 'priority': 'medium', 'suggestion': 'Medium'},
            {'component': 'title', 'priority': 'low', 'suggestion': 'Low'}
        ]
        
        filtered = polisher._filter_suggestions_by_priority(suggestions)
        
        # Default config applies HIGH priority threshold
        assert len(filtered) == 1
        assert filtered[0]['priority'] == 'high'
    
    def test_filter_suggestions_by_priority_medium(self):
        """Test filtering suggestions by medium priority."""
        config = PolishConfig(apply_priority_threshold=PriorityLevel.MEDIUM)
        polisher = StoryPolisher(config)
        
        suggestions = [
            {'component': 'title', 'priority': 'high', 'suggestion': 'High'},
            {'component': 'title', 'priority': 'medium', 'suggestion': 'Medium'},
            {'component': 'title', 'priority': 'low', 'suggestion': 'Low'}
        ]
        
        filtered = polisher._filter_suggestions_by_priority(suggestions)
        
        # MEDIUM threshold should include HIGH and MEDIUM
        assert len(filtered) == 2
    
    def test_polish_title_capitalization(self):
        """Test polishing title with capitalization improvement."""
        polisher = StoryPolisher()
        
        suggestions = [
            {
                'component': 'title',
                'priority': 'high',
                'suggestion': 'Capitalize "and" for stronger visual impact'
            }
        ]
        
        polished, changes = polisher._polish_title(
            "The House That Remembers: and Hunts",
            suggestions,
            None,
            None
        )
        
        assert "And Hunts" in polished
        assert len(changes) == 1
        assert changes[0].change_type == ChangeType.CAPITALIZATION
    
    def test_polish_script_opening_enhancement(self):
        """Test polishing script with opening enhancement."""
        polisher = StoryPolisher()
        
        suggestions = [
            {
                'component': 'script',
                'priority': 'high',
                'suggestion': 'Add brief relatable context in opening'
            }
        ]
        
        original_script = "Every night at midnight, she returns..."
        polished, changes = polisher._polish_script(
            original_script,
            suggestions,
            None,
            None
        )
        
        assert "We've all driven past" in polished
        assert len(changes) == 1
        assert changes[0].change_type == ChangeType.OPENING_ENHANCEMENT
    
    def test_estimate_quality_increase(self):
        """Test estimating quality score increase."""
        polisher = StoryPolisher()
        
        suggestions = [
            {'priority': 'high'},
            {'priority': 'high'}
        ]
        
        delta = polisher._estimate_quality_increase(2, suggestions)
        
        assert delta > 0
        assert delta <= 10  # Capped at 10
    
    def test_polish_story_complete_flow(self):
        """Test complete story polishing flow."""
        polisher = StoryPolisher()
        
        # Create expert review data
        review_data = {
            'overall_assessment': {
                'quality_score': 92,
                'ready_for_publishing': False
            },
            'improvement_suggestions': [
                {
                    'component': 'title',
                    'priority': 'high',
                    'suggestion': 'Capitalize "and" for stronger visual impact'
                },
                {
                    'component': 'script',
                    'priority': 'high',
                    'suggestion': 'Add brief relatable context in opening'
                }
            ]
        }
        
        # Polish the story
        polish = polisher.polish_story(
            story_id="story_test_001",
            current_title="The House That Remembers: and Hunts",
            current_script="Every night at midnight, she returns...",
            expert_review_data=review_data,
            iteration_number=1
        )
        
        # Verify results
        assert polish.story_id == "story_test_001"
        assert polish.iteration_number == 1
        assert polish.quality_delta > 0
        assert polish.expected_quality_score > polish.original_quality_score
        assert len(polish.change_log) > 0
        assert polish.ready_for_review is True
        
        # Check title improvement
        assert "And Hunts" in polish.polished_title
        
        # Check script improvement
        assert "We've all driven past" in polish.polished_script
    
    def test_polish_story_no_applicable_suggestions(self):
        """Test polishing when no suggestions meet priority threshold."""
        config = PolishConfig(apply_priority_threshold=PriorityLevel.HIGH)
        polisher = StoryPolisher(config)
        
        review_data = {
            'overall_assessment': {
                'quality_score': 95
            },
            'improvement_suggestions': [
                {
                    'component': 'title',
                    'priority': 'low',
                    'suggestion': 'Minor tweak'
                }
            ]
        }
        
        polish = polisher.polish_story(
            story_id="story_test_002",
            current_title="Perfect Title",
            current_script="Perfect script text",
            expert_review_data=review_data
        )
        
        # Should have no changes since low priority doesn't meet HIGH threshold
        assert len(polish.change_log) == 0
        assert polish.polished_title == polish.original_title
        assert polish.polished_script == polish.original_script


@pytest.mark.integration
class TestStoryPolisherIntegration:
    """Integration tests for story polisher."""
    
    def test_multiple_iteration_tracking(self):
        """Test tracking multiple polish iterations."""
        polisher = StoryPolisher()
        
        review_data = {
            'overall_assessment': {'quality_score': 88},
            'improvement_suggestions': [
                {
                    'component': 'title',
                    'priority': 'high',
                    'suggestion': 'Capitalize "and"'
                }
            ]
        }
        
        # First iteration
        polish1 = polisher.polish_story(
            story_id="story_iter_001",
            current_title="Title: and Subtitle",
            current_script="Script text",
            expert_review_data=review_data,
            iteration_number=1
        )
        
        assert polish1.iteration_number == 1
        assert "polish_1" in polish1.polish_id
        
        # Second iteration
        polish2 = polisher.polish_story(
            story_id="story_iter_001",
            current_title=polish1.polished_title,
            current_script=polish1.polished_script,
            expert_review_data=review_data,
            iteration_number=2
        )
        
        assert polish2.iteration_number == 2
        assert "polish_2" in polish2.polish_id
    
    def test_json_serialization_roundtrip(self):
        """Test JSON serialization and deserialization."""
        polisher = StoryPolisher()
        
        review_data = {
            'overall_assessment': {'quality_score': 90},
            'improvement_suggestions': [
                {
                    'component': 'script',
                    'priority': 'high',
                    'suggestion': 'Add opening context'
                }
            ]
        }
        
        polish = polisher.polish_story(
            story_id="story_json_001",
            current_title="Test Title",
            current_script="Test script",
            expert_review_data=review_data
        )
        
        # Convert to JSON and back
        json_str = polish.to_json()
        assert isinstance(json_str, str)
        assert "story_json_001" in json_str
        
        # Verify JSON is parseable
        import json
        data = json.loads(json_str)
        assert data['story_id'] == "story_json_001"
        assert 'change_log' in data


def test_convenience_function_polish_story_with_gpt():
    """Test convenience function for polishing."""
    review_data = {
        'overall_assessment': {'quality_score': 90},
        'improvement_suggestions': [
            {
                'component': 'title',
                'priority': 'high',
                'suggestion': 'Test suggestion'
            }
        ]
    }
    
    polish = polish_story_with_gpt(
        story_id="test_conv_001",
        current_title="Test Title",
        current_script="Test Script",
        expert_review_data=review_data
    )
    
    assert polish.story_id == "test_conv_001"
    assert polish.ready_for_review is True


def test_convenience_function_polish_story_to_json():
    """Test convenience function for JSON conversion."""
    polish = StoryPolish(
        polish_id="test_json",
        story_id="story_json",
        original_title="Title",
        polished_title="Polished",
        original_script="Script",
        polished_script="Polished Script"
    )
    
    json_str = polish_story_to_json(polish)
    
    assert isinstance(json_str, str)
    assert "test_json" in json_str
