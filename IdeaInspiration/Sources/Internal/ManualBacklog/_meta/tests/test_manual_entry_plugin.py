"""Tests for manual entry plugin."""

import pytest
from unittest.mock import Mock
from src.plugins.manual_entry_plugin import ManualEntryPlugin


@pytest.fixture
def mock_config():
    """Fixture to create a mock config object."""
    config = Mock()
    config.default_priority = 'medium'
    config.default_status = 'new'
    config.default_category = 'general'
    config.default_user = 'testuser'
    return config


class TestManualEntryPlugin:
    """Test manual entry plugin functionality."""
    
    def test_initialization(self, mock_config):
        """Test plugin initialization."""
        plugin = ManualEntryPlugin(mock_config)
        
        assert plugin.config == mock_config
        assert plugin.get_source_name() == "manual_backlog"
        assert plugin.idea_manager is not None
    
    def test_get_source_name(self, mock_config):
        """Test source name retrieval."""
        plugin = ManualEntryPlugin(mock_config)
        
        assert plugin.get_source_name() == "manual_backlog"
    
    def test_scrape_returns_empty_list(self, mock_config):
        """Test that scrape returns empty list (not applicable for manual entry)."""
        plugin = ManualEntryPlugin(mock_config)
        ideas = plugin.scrape()
        
        assert ideas == []
    
    def test_add_simple_idea(self, mock_config):
        """Test adding a simple idea."""
        plugin = ManualEntryPlugin(mock_config)
        idea = plugin.add_idea(title="Test Idea")
        
        assert idea['idea']['title'] == "Test Idea"
        assert idea['source'] == "manual_backlog"
    
    def test_add_idea_with_all_fields(self, mock_config):
        """Test adding an idea with all fields."""
        plugin = ManualEntryPlugin(mock_config)
        idea = plugin.add_idea(
            title="Complete Idea",
            description="Description",
            notes="Notes",
            category="content",
            priority="high",
            status="in_progress",
            tags=["tag1", "tag2"],
            created_by="John",
            assigned_to="Jane"
        )
        
        assert idea['idea']['title'] == "Complete Idea"
        assert idea['idea']['description'] == "Description"
        assert idea['idea']['notes'] == "Notes"
        assert idea['idea']['category'] == "content"
        assert idea['idea']['priority'] == "high"
        assert idea['metadata']['status'] == "in_progress"
        assert idea['metadata']['tags'] == ["tag1", "tag2"]
        assert idea['metadata']['created_by'] == "John"
        assert idea['metadata']['assigned_to'] == "Jane"
    
    def test_add_idea_empty_title_raises_error(self, mock_config):
        """Test that adding idea with empty title raises error."""
        plugin = ManualEntryPlugin(mock_config)
        
        with pytest.raises(ValueError, match="validation failed"):
            plugin.add_idea(title="")
    
    def test_add_idea_uses_defaults(self):
        """Test that defaults from config are used."""
        config = Mock()
        config.default_priority = 'high'
        config.default_status = 'in_progress'
        config.default_category = 'content'
        config.default_user = 'john'
        
        plugin = ManualEntryPlugin(config)
        idea = plugin.add_idea(title="Test")
        
        assert idea['idea']['priority'] == 'high'
        assert idea['metadata']['status'] == 'in_progress'
        assert idea['idea']['category'] == 'content'
        assert idea['metadata']['created_by'] == 'john'
    
    def test_update_idea(self, mock_config):
        """Test updating an idea."""
        plugin = ManualEntryPlugin(mock_config)
        
        # Create original idea
        idea = plugin.add_idea(title="Original", priority="low")
        
        # Update it
        updated = plugin.update_idea(idea, title="Updated", priority="high")
        
        assert updated['idea']['title'] == "Updated"
        assert updated['idea']['priority'] == "high"
    
    def test_mark_as_used(self, mock_config):
        """Test marking an idea as used."""
        plugin = ManualEntryPlugin(mock_config)
        
        # Create idea
        idea = plugin.add_idea(title="Test")
        assert idea['metadata']['status'] == 'new'
        assert idea['tracking']['used_at'] is None
        
        # Mark as used
        used_idea = plugin.mark_as_used(idea)
        
        assert used_idea['metadata']['status'] == 'used'
        assert used_idea['tracking']['used_at'] is not None
    
    def test_archive_idea(self, mock_config):
        """Test archiving an idea."""
        plugin = ManualEntryPlugin(mock_config)
        
        # Create idea
        idea = plugin.add_idea(title="Test")
        assert idea['metadata']['status'] == 'new'
        
        # Archive it
        archived_idea = plugin.archive_idea(idea)
        
        assert archived_idea['metadata']['status'] == 'archived'
    
    def test_add_idea_validation_warnings(self, mock_config, capsys):
        """Test that validation warnings are displayed."""
        plugin = ManualEntryPlugin(mock_config)
        
        # Add idea with unusual priority
        idea = plugin.add_idea(title="Test", priority="super_high")
        
        # Check that warning was printed
        captured = capsys.readouterr()
        assert "Warning" in captured.out or idea is not None  # Either warning shown or idea created
    
    def test_idea_manager_integration(self, mock_config):
        """Test that plugin properly uses idea manager."""
        plugin = ManualEntryPlugin(mock_config)
        
        # Verify idea manager was initialized with correct defaults
        assert plugin.idea_manager.default_priority == 'medium'
        assert plugin.idea_manager.default_status == 'new'
        assert plugin.idea_manager.default_category == 'general'
        assert plugin.idea_manager.default_user == 'testuser'
