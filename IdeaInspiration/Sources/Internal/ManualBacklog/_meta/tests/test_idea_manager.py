"""Tests for idea manager."""

import pytest
from datetime import datetime
from src.core.idea_manager import IdeaManager


class TestIdeaManager:
    """Test idea manager functionality."""
    
    def test_initialization(self):
        """Test manager initialization with defaults."""
        manager = IdeaManager()
        assert manager.default_priority == 'medium'
        assert manager.default_status == 'new'
        assert manager.default_category == 'general'
        assert manager.default_user == 'unknown'
    
    def test_initialization_with_custom_values(self):
        """Test manager initialization with custom values."""
        manager = IdeaManager(
            default_priority='high',
            default_status='in_progress',
            default_category='content',
            default_user='john'
        )
        assert manager.default_priority == 'high'
        assert manager.default_status == 'in_progress'
        assert manager.default_category == 'content'
        assert manager.default_user == 'john'
    
    def test_create_simple_idea(self):
        """Test creating a simple idea with only title."""
        manager = IdeaManager()
        idea = manager.create_idea(title="Test Idea")
        
        assert idea['source'] == 'manual_backlog'
        assert idea['idea']['title'] == "Test Idea"
        assert idea['idea']['description'] == ''
        assert idea['idea']['category'] == 'general'
        assert idea['idea']['priority'] == 'medium'
        assert idea['metadata']['status'] == 'new'
    
    def test_create_idea_with_all_fields(self):
        """Test creating an idea with all fields."""
        manager = IdeaManager()
        idea = manager.create_idea(
            title="Complete Idea",
            description="Full description",
            notes="Some notes",
            category="content",
            priority="high",
            status="in_progress",
            tags=["tag1", "tag2"],
            created_by="John",
            assigned_to="Jane"
        )
        
        assert idea['idea']['title'] == "Complete Idea"
        assert idea['idea']['description'] == "Full description"
        assert idea['idea']['notes'] == "Some notes"
        assert idea['idea']['category'] == "content"
        assert idea['idea']['priority'] == "high"
        assert idea['metadata']['status'] == "in_progress"
        assert idea['metadata']['tags'] == ["tag1", "tag2"]
        assert idea['metadata']['created_by'] == "John"
        assert idea['metadata']['assigned_to'] == "Jane"
    
    def test_create_idea_empty_title_raises_error(self):
        """Test that empty title raises ValueError."""
        manager = IdeaManager()
        
        with pytest.raises(ValueError, match="Title is required"):
            manager.create_idea(title="")
        
        with pytest.raises(ValueError, match="Title is required"):
            manager.create_idea(title="   ")
    
    def test_create_idea_trims_whitespace(self):
        """Test that whitespace is trimmed from fields."""
        manager = IdeaManager()
        idea = manager.create_idea(
            title="  Idea  ",
            description="  Description  ",
            notes="  Notes  ",
            category="  content  ",
            priority="  HIGH  ",
            created_by="  John  "
        )
        
        assert idea['idea']['title'] == "Idea"
        assert idea['idea']['description'] == "Description"
        assert idea['idea']['notes'] == "Notes"
        assert idea['idea']['category'] == "content"
        assert idea['idea']['priority'] == "high"
        assert idea['metadata']['created_by'] == "John"
    
    def test_create_idea_generates_unique_source_id(self):
        """Test that each idea gets a unique source ID."""
        manager = IdeaManager()
        
        idea1 = manager.create_idea(title="Idea 1")
        idea2 = manager.create_idea(title="Idea 2")
        idea3 = manager.create_idea(title="Idea 1")  # Same title
        
        # All should have different IDs
        assert idea1['source_id'] != idea2['source_id']
        assert idea1['source_id'] != idea3['source_id']
        assert idea2['source_id'] != idea3['source_id']
        
        # IDs should start with 'manual_'
        assert idea1['source_id'].startswith('manual_')
        assert idea2['source_id'].startswith('manual_')
        assert idea3['source_id'].startswith('manual_')
    
    def test_create_idea_has_timestamps(self):
        """Test that created ideas have timestamps."""
        manager = IdeaManager()
        idea = manager.create_idea(title="Test")
        
        assert 'created_at' in idea['tracking']
        assert 'modified_at' in idea['tracking']
        assert idea['tracking']['created_at'] is not None
        assert idea['tracking']['modified_at'] is not None
        assert idea['tracking']['used_at'] is None
        assert idea['tracking']['age_days'] == 0
    
    def test_create_idea_calculates_priority_score(self):
        """Test priority score calculation."""
        manager = IdeaManager()
        
        high_idea = manager.create_idea(title="High", priority="high")
        medium_idea = manager.create_idea(title="Medium", priority="medium")
        low_idea = manager.create_idea(title="Low", priority="low")
        
        assert high_idea['universal_metrics']['priority_score'] == 8.0
        assert medium_idea['universal_metrics']['priority_score'] == 5.0
        assert low_idea['universal_metrics']['priority_score'] == 2.0
    
    def test_update_idea_title(self):
        """Test updating idea title."""
        manager = IdeaManager()
        idea = manager.create_idea(title="Original")
        
        updated = manager.update_idea(idea, title="Updated")
        
        assert updated['idea']['title'] == "Updated"
    
    def test_update_idea_multiple_fields(self):
        """Test updating multiple fields."""
        manager = IdeaManager()
        idea = manager.create_idea(
            title="Original",
            description="Original desc",
            priority="low"
        )
        
        updated = manager.update_idea(
            idea,
            title="Updated",
            description="Updated desc",
            priority="high",
            status="in_progress",
            tags=["new", "tags"]
        )
        
        assert updated['idea']['title'] == "Updated"
        assert updated['idea']['description'] == "Updated desc"
        assert updated['idea']['priority'] == "high"
        assert updated['metadata']['status'] == "in_progress"
        assert updated['metadata']['tags'] == ["new", "tags"]
    
    def test_update_idea_updates_modified_timestamp(self):
        """Test that update changes modified_at timestamp."""
        from unittest.mock import patch
        from datetime import datetime, timedelta
        
        manager = IdeaManager()
        
        # Mock initial timestamp
        initial_time = datetime(2025, 1, 1, 12, 0, 0)
        with patch('src.core.idea_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value = initial_time
            idea = manager.create_idea(title="Test")
        
        original_modified = idea['tracking']['modified_at']
        
        # Mock updated timestamp (1 hour later)
        updated_time = datetime(2025, 1, 1, 13, 0, 0)
        with patch('src.core.idea_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value = updated_time
            updated = manager.update_idea(idea, title="Updated")
        
        assert updated['tracking']['modified_at'] != original_modified
    
    def test_update_idea_with_tags_string(self):
        """Test updating tags with comma-separated string."""
        manager = IdeaManager()
        idea = manager.create_idea(title="Test")
        
        updated = manager.update_idea(idea, tags="tag1, tag2, tag3")
        
        assert updated['metadata']['tags'] == ["tag1", "tag2", "tag3"]
    
    def test_update_idea_priority_updates_score(self):
        """Test that updating priority also updates priority score."""
        manager = IdeaManager()
        idea = manager.create_idea(title="Test", priority="low")
        
        assert idea['universal_metrics']['priority_score'] == 2.0
        
        updated = manager.update_idea(idea, priority="high")
        
        assert updated['universal_metrics']['priority_score'] == 8.0
    
    def test_calculate_priority_score_variations(self):
        """Test priority score calculation for various priorities."""
        manager = IdeaManager()
        
        assert manager._calculate_priority_score('critical') == 10.0
        assert manager._calculate_priority_score('urgent') == 9.0
        assert manager._calculate_priority_score('high') == 8.0
        assert manager._calculate_priority_score('medium') == 5.0
        assert manager._calculate_priority_score('normal') == 5.0
        assert manager._calculate_priority_score('low') == 2.0
        assert manager._calculate_priority_score('minor') == 3.0
        assert manager._calculate_priority_score('unknown') == 5.0  # default
    
    def test_validate_idea_data_valid(self):
        """Test validation with valid data."""
        manager = IdeaManager()
        
        validation = manager.validate_idea_data(
            title="Valid Title",
            priority="high",
            status="new"
        )
        
        assert validation['valid'] is True
        assert len(validation['errors']) == 0
    
    def test_validate_idea_data_missing_title(self):
        """Test validation with missing title."""
        manager = IdeaManager()
        
        validation = manager.validate_idea_data(title="")
        
        assert validation['valid'] is False
        assert "Title is required" in validation['errors']
    
    def test_validate_idea_data_invalid_priority(self):
        """Test validation with invalid priority."""
        manager = IdeaManager()
        
        validation = manager.validate_idea_data(
            title="Test",
            priority="super_high"
        )
        
        assert validation['valid'] is True  # Still valid, just warning
        assert len(validation['warnings']) > 0
    
    def test_validate_idea_data_invalid_status(self):
        """Test validation with invalid status."""
        manager = IdeaManager()
        
        validation = manager.validate_idea_data(
            title="Test",
            status="maybe"
        )
        
        assert validation['valid'] is True  # Still valid, just warning
        assert len(validation['warnings']) > 0
    
    def test_idea_has_all_required_fields(self):
        """Test that created ideas have all required fields."""
        manager = IdeaManager()
        idea = manager.create_idea(title="Test")
        
        # Top-level fields
        assert 'source' in idea
        assert 'source_id' in idea
        assert 'idea' in idea
        assert 'metadata' in idea
        assert 'tracking' in idea
        assert 'universal_metrics' in idea
        
        # Idea fields
        assert 'title' in idea['idea']
        assert 'description' in idea['idea']
        assert 'notes' in idea['idea']
        assert 'category' in idea['idea']
        assert 'priority' in idea['idea']
        
        # Metadata fields
        assert 'status' in idea['metadata']
        assert 'created_by' in idea['metadata']
        assert 'assigned_to' in idea['metadata']
        assert 'tags' in idea['metadata']
        
        # Tracking fields
        assert 'created_at' in idea['tracking']
        assert 'modified_at' in idea['tracking']
        assert 'used_at' in idea['tracking']
        assert 'age_days' in idea['tracking']
        
        # Metrics
        assert 'priority_score' in idea['universal_metrics']
        assert 'actionability' in idea['universal_metrics']
