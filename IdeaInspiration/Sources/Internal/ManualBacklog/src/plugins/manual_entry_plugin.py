"""Manual Entry plugin for manual idea backlog management."""

from typing import List, Dict, Any, Optional
from . import SourcePlugin
from ..core.idea_manager import IdeaManager


class ManualEntryPlugin(SourcePlugin):
    """Plugin for manually entering and managing ideas."""
    
    def __init__(self, config):
        """Initialize manual entry plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        
        # Initialize idea manager with config defaults
        self.idea_manager = IdeaManager(
            default_priority=config.default_priority,
            default_status=config.default_status,
            default_category=config.default_category,
            default_user=config.default_user
        )
    
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "manual_backlog"
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape ideas from manual entry (not applicable).
        
        This method is not used for manual entry source as ideas are
        created directly through the add_idea method.
        
        Returns:
            Empty list (manual entry doesn't scrape)
        """
        return []
    
    def add_idea(self,
                 title: str,
                 description: str = '',
                 notes: str = '',
                 category: Optional[str] = None,
                 priority: Optional[str] = None,
                 status: Optional[str] = None,
                 tags: Optional[List[str]] = None,
                 created_by: Optional[str] = None,
                 assigned_to: Optional[str] = None) -> Dict[str, Any]:
        """Add a new idea to the backlog.
        
        Args:
            title: Idea title (required)
            description: Idea description
            notes: Additional notes
            category: Category classification
            priority: Priority level (high/medium/low)
            status: Status (new/in_progress/used/archived)
            tags: List of tags
            created_by: Creator name
            assigned_to: Assignee name
            
        Returns:
            Created idea dictionary
            
        Raises:
            ValueError: If title is empty or validation fails
        """
        # Validate before creating
        validation = self.idea_manager.validate_idea_data(
            title=title,
            priority=priority or self.idea_manager.default_priority,
            status=status or self.idea_manager.default_status
        )
        
        if not validation['valid']:
            errors = ', '.join(validation['errors'])
            raise ValueError(f"Idea validation failed: {errors}")
        
        # Show warnings if any
        for warning in validation['warnings']:
            print(f"Warning: {warning}")
        
        # Create idea
        idea = self.idea_manager.create_idea(
            title=title,
            description=description,
            notes=notes,
            category=category,
            priority=priority,
            status=status,
            tags=tags,
            created_by=created_by,
            assigned_to=assigned_to
        )
        
        return idea
    
    def update_idea(self, existing_idea: Dict[str, Any], **updates) -> Dict[str, Any]:
        """Update an existing idea.
        
        Args:
            existing_idea: Existing idea dictionary
            **updates: Fields to update
            
        Returns:
            Updated idea dictionary
        """
        return self.idea_manager.update_idea(existing_idea, **updates)
    
    def mark_as_used(self, existing_idea: Dict[str, Any]) -> Dict[str, Any]:
        """Mark an idea as used.
        
        Args:
            existing_idea: Existing idea dictionary
            
        Returns:
            Updated idea dictionary
        """
        from datetime import datetime
        
        updates = {
            'status': 'used',
            'used_at': datetime.now().isoformat()
        }
        
        return self.idea_manager.update_idea(existing_idea, **updates)
    
    def archive_idea(self, existing_idea: Dict[str, Any]) -> Dict[str, Any]:
        """Archive an idea.
        
        Args:
            existing_idea: Existing idea dictionary
            
        Returns:
            Updated idea dictionary
        """
        updates = {'status': 'archived'}
        return self.idea_manager.update_idea(existing_idea, **updates)
