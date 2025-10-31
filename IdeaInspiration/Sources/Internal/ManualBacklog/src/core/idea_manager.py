"""Idea manager for Manual Backlog source."""

import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime


class IdeaManager:
    """Manages creation and transformation of manual ideas.
    
    Follows Single Responsibility Principle (SRP) by focusing only on
    idea creation and transformation logic.
    """
    
    def __init__(self, default_priority: str = 'medium',
                 default_status: str = 'new',
                 default_category: str = 'general',
                 default_user: str = 'unknown'):
        """Initialize idea manager.
        
        Args:
            default_priority: Default priority for ideas (default: 'medium')
            default_status: Default status for ideas (default: 'new')
            default_category: Default category for ideas (default: 'general')
            default_user: Default user for created_by (default: 'unknown')
        """
        self.default_priority = default_priority
        self.default_status = default_status
        self.default_category = default_category
        self.default_user = default_user
    
    def create_idea(self,
                    title: str,
                    description: str = '',
                    notes: str = '',
                    category: Optional[str] = None,
                    priority: Optional[str] = None,
                    status: Optional[str] = None,
                    tags: Optional[List[str]] = None,
                    created_by: Optional[str] = None,
                    assigned_to: Optional[str] = None) -> Dict[str, Any]:
        """Create a new idea in IdeaInspiration format.
        
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
            Idea dictionary in IdeaInspiration format
            
        Raises:
            ValueError: If title is empty
        """
        # Validate required fields
        if not title or not title.strip():
            raise ValueError("Title is required and cannot be empty")
        
        # Use defaults if not provided
        category = category or self.default_category
        priority = priority or self.default_priority
        status = status or self.default_status
        tags = tags or []
        created_by = created_by or self.default_user
        assigned_to = assigned_to or ''
        
        # Normalize strings
        title = title.strip()
        description = description.strip() if description else ''
        notes = notes.strip() if notes else ''
        category = category.strip()
        priority = priority.strip().lower()
        status = status.strip().lower()
        created_by = created_by.strip()
        assigned_to = assigned_to.strip()
        
        # Generate unique source_id
        source_id = self._generate_source_id(title, description)
        
        # Current timestamp
        now = datetime.now().isoformat()
        
        # Calculate age_days (0 for new ideas)
        age_days = 0
        
        # Calculate basic priority score
        priority_score = self._calculate_priority_score(priority)
        
        # Calculate actionability (default medium value)
        actionability = 5.0
        
        # Build IdeaInspiration format
        idea = {
            'source': 'manual_backlog',
            'source_id': source_id,
            'idea': {
                'title': title,
                'description': description,
                'notes': notes,
                'category': category,
                'priority': priority
            },
            'metadata': {
                'status': status,
                'created_by': created_by,
                'assigned_to': assigned_to,
                'tags': [tag.strip() for tag in tags if tag.strip()]
            },
            'tracking': {
                'created_at': now,
                'modified_at': now,
                'used_at': None,
                'age_days': age_days
            },
            'universal_metrics': {
                'priority_score': priority_score,
                'actionability': actionability
            }
        }
        
        return idea
    
    def update_idea(self, existing_idea: Dict[str, Any], **updates) -> Dict[str, Any]:
        """Update an existing idea with new values.
        
        Args:
            existing_idea: Existing idea dictionary
            **updates: Fields to update
            
        Returns:
            Updated idea dictionary
        """
        # Update modified timestamp
        existing_idea['tracking']['modified_at'] = datetime.now().isoformat()
        
        # Update idea fields
        if 'title' in updates:
            existing_idea['idea']['title'] = updates['title'].strip()
        if 'description' in updates:
            existing_idea['idea']['description'] = updates['description'].strip()
        if 'notes' in updates:
            existing_idea['idea']['notes'] = updates['notes'].strip()
        if 'category' in updates:
            existing_idea['idea']['category'] = updates['category'].strip()
        if 'priority' in updates:
            priority = updates['priority'].strip().lower()
            existing_idea['idea']['priority'] = priority
            # Update priority score
            existing_idea['universal_metrics']['priority_score'] = self._calculate_priority_score(priority)
        
        # Update metadata fields
        if 'status' in updates:
            existing_idea['metadata']['status'] = updates['status'].strip().lower()
        if 'tags' in updates:
            tags = updates['tags']
            if isinstance(tags, list):
                existing_idea['metadata']['tags'] = [tag.strip() for tag in tags if tag.strip()]
            elif isinstance(tags, str):
                existing_idea['metadata']['tags'] = [tag.strip() for tag in tags.split(',') if tag.strip()]
        if 'created_by' in updates:
            existing_idea['metadata']['created_by'] = updates['created_by'].strip()
        if 'assigned_to' in updates:
            existing_idea['metadata']['assigned_to'] = updates['assigned_to'].strip()
        
        # Update tracking
        if 'used_at' in updates:
            existing_idea['tracking']['used_at'] = updates['used_at']
        
        # Recalculate age
        if existing_idea['tracking']['created_at']:
            created = datetime.fromisoformat(existing_idea['tracking']['created_at'])
            age_days = (datetime.now() - created).days
            existing_idea['tracking']['age_days'] = age_days
        
        return existing_idea
    
    def _generate_source_id(self, title: str, description: str) -> str:
        """Generate unique source ID for an idea.
        
        Args:
            title: Idea title
            description: Idea description
            
        Returns:
            Unique source ID
        """
        # Combine fields for uniqueness, include timestamp for truly unique IDs
        timestamp = datetime.now().isoformat()
        unique_string = f"{title}|{description}|{timestamp}"
        
        # Generate hash
        hash_obj = hashlib.sha256(unique_string.encode())
        hash_hex = hash_obj.hexdigest()[:16]  # Use first 16 chars
        
        return f"manual_{hash_hex}"
    
    def _calculate_priority_score(self, priority: str) -> float:
        """Calculate numeric priority score from priority string.
        
        Args:
            priority: Priority string (high, medium, low)
            
        Returns:
            Priority score (0-10)
        """
        priority_lower = str(priority).lower().strip()
        
        priority_map = {
            'high': 8.0,
            'medium': 5.0,
            'low': 2.0,
            'critical': 10.0,
            'urgent': 9.0,
            'normal': 5.0,
            'minor': 3.0
        }
        
        return priority_map.get(priority_lower, 5.0)
    
    def validate_idea_data(self, **fields) -> Dict[str, Any]:
        """Validate idea data before creation.
        
        Args:
            **fields: Idea fields to validate
            
        Returns:
            Dictionary with validation results
        """
        validation = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required fields
        if 'title' not in fields or not fields['title'] or not fields['title'].strip():
            validation['valid'] = False
            validation['errors'].append("Title is required")
        
        # Check priority value
        if 'priority' in fields:
            priority = fields['priority'].lower().strip()
            valid_priorities = ['high', 'medium', 'low', 'critical', 'urgent', 'normal', 'minor']
            if priority not in valid_priorities:
                validation['warnings'].append(
                    f"Priority '{priority}' not recognized. Will use default scoring."
                )
        
        # Check status value
        if 'status' in fields:
            status = fields['status'].lower().strip()
            valid_statuses = ['new', 'in_progress', 'used', 'archived']
            if status not in valid_statuses:
                validation['warnings'].append(
                    f"Status '{status}' not standard. Expected: {', '.join(valid_statuses)}"
                )
        
        return validation
