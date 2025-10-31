"""Tests for database operations."""

import pytest
import json
from pathlib import Path
from datetime import datetime
from src.core.database import Database


class TestDatabase:
    """Test database functionality."""
    
    def test_initialization_creates_database(self, tmp_path):
        """Test that database is created on initialization."""
        db_path = tmp_path / "test.db"
        
        # Database should not exist initially
        assert not db_path.exists()
        
        # Initialize database (non-interactive)
        db = Database(str(db_path), interactive=False)
        
        # Database file should now exist
        assert db_path.exists()
    
    def test_save_single_idea(self, tmp_path):
        """Test saving a single idea to database."""
        db_path = tmp_path / "test.db"
        db = Database(str(db_path), interactive=False)
        
        idea = {
            'source_id': 'test_001',
            'source': 'csv_import',
            'idea': {
                'title': 'Test Idea',
                'description': 'Test Description',
                'notes': 'Test Notes',
                'category': 'content',
                'priority': 'high'
            },
            'metadata': {
                'status': 'new',
                'created_by': 'John',
                'assigned_to': 'Jane',
                'tags': ['tag1', 'tag2']
            },
            'tracking': {
                'created_at': datetime.now().isoformat(),
                'modified_at': datetime.now().isoformat(),
                'used_at': None,
                'age_days': 0
            },
            'universal_metrics': {
                'priority_score': 8.0,
                'actionability': 7.0
            }
        }
        
        saved_count = db.save_ideas([idea])
        
        assert saved_count == 1
    
    def test_save_multiple_ideas(self, tmp_path):
        """Test saving multiple ideas to database."""
        db_path = tmp_path / "test.db"
        db = Database(str(db_path), interactive=False)
        
        ideas = [
            {
                'source_id': f'test_{i}',
                'source': 'csv_import',
                'idea': {
                    'title': f'Idea {i}',
                    'description': f'Description {i}',
                    'notes': '',
                    'category': 'content',
                    'priority': 'medium'
                },
                'metadata': {
                    'status': 'new',
                    'created_by': '',
                    'assigned_to': '',
                    'tags': []
                },
                'tracking': {
                    'created_at': datetime.now().isoformat(),
                    'modified_at': datetime.now().isoformat(),
                    'used_at': None,
                    'age_days': 0
                },
                'universal_metrics': {
                    'priority_score': 5.0,
                    'actionability': 5.0
                }
            }
            for i in range(5)
        ]
        
        saved_count = db.save_ideas(ideas)
        
        assert saved_count == 5
    
    def test_get_all_ideas(self, tmp_path):
        """Test retrieving all ideas from database."""
        db_path = tmp_path / "test.db"
        db = Database(str(db_path), interactive=False)
        
        # Save some ideas
        ideas = [
            {
                'source_id': f'test_{i}',
                'source': 'csv_import',
                'idea': {
                    'title': f'Idea {i}',
                    'description': '',
                    'notes': '',
                    'category': 'content',
                    'priority': 'medium'
                },
                'metadata': {
                    'status': 'new',
                    'created_by': '',
                    'assigned_to': '',
                    'tags': []
                },
                'tracking': {
                    'created_at': datetime.now().isoformat(),
                    'modified_at': datetime.now().isoformat(),
                    'used_at': None,
                    'age_days': 0
                },
                'universal_metrics': {
                    'priority_score': 5.0,
                    'actionability': 5.0
                }
            }
            for i in range(3)
        ]
        
        db.save_ideas(ideas)
        
        # Retrieve all ideas
        retrieved = db.get_ideas()
        
        assert len(retrieved) == 3
    
    def test_get_ideas_filtered_by_status(self, tmp_path):
        """Test filtering ideas by status."""
        db_path = tmp_path / "test.db"
        db = Database(str(db_path), interactive=False)
        
        # Save ideas with different statuses
        ideas = [
            self._create_test_idea('test_1', status='new'),
            self._create_test_idea('test_2', status='new'),
            self._create_test_idea('test_3', status='in_progress'),
        ]
        
        db.save_ideas(ideas)
        
        # Get only 'new' ideas
        new_ideas = db.get_ideas(status='new')
        
        assert len(new_ideas) == 2
        for idea in new_ideas:
            assert idea['metadata']['status'] == 'new'
    
    def test_get_ideas_filtered_by_category(self, tmp_path):
        """Test filtering ideas by category."""
        db_path = tmp_path / "test.db"
        db = Database(str(db_path), interactive=False)
        
        # Save ideas with different categories
        ideas = [
            self._create_test_idea('test_1', category='content'),
            self._create_test_idea('test_2', category='content'),
            self._create_test_idea('test_3', category='marketing'),
        ]
        
        db.save_ideas(ideas)
        
        # Get only 'content' ideas
        content_ideas = db.get_ideas(category='content')
        
        assert len(content_ideas) == 2
        for idea in content_ideas:
            assert idea['idea']['category'] == 'content'
    
    def test_get_ideas_with_limit(self, tmp_path):
        """Test limiting number of retrieved ideas."""
        db_path = tmp_path / "test.db"
        db = Database(str(db_path), interactive=False)
        
        # Save 5 ideas
        ideas = [self._create_test_idea(f'test_{i}') for i in range(5)]
        db.save_ideas(ideas)
        
        # Get only 3 ideas
        limited_ideas = db.get_ideas(limit=3)
        
        assert len(limited_ideas) == 3
    
    def test_check_duplicate_exists(self, tmp_path):
        """Test checking for duplicate ideas."""
        db_path = tmp_path / "test.db"
        db = Database(str(db_path), interactive=False)
        
        idea = self._create_test_idea('test_001')
        db.save_ideas([idea])
        
        # Check for duplicate
        assert db.check_duplicate('test_001') is True
        assert db.check_duplicate('test_002') is False
    
    def test_get_stats(self, tmp_path):
        """Test getting database statistics."""
        db_path = tmp_path / "test.db"
        db = Database(str(db_path), interactive=False)
        
        # Save ideas with various attributes
        ideas = [
            self._create_test_idea('test_1', status='new', category='content', priority='high'),
            self._create_test_idea('test_2', status='new', category='content', priority='medium'),
            self._create_test_idea('test_3', status='in_progress', category='marketing', priority='high'),
        ]
        
        db.save_ideas(ideas)
        
        stats = db.get_stats()
        
        assert stats['total'] == 3
        assert stats['by_status']['new'] == 2
        assert stats['by_status']['in_progress'] == 1
        assert stats['by_category']['content'] == 2
        assert stats['by_category']['marketing'] == 1
        assert stats['by_priority']['high'] == 2
        assert stats['by_priority']['medium'] == 1
    
    def test_save_empty_list(self, tmp_path):
        """Test saving empty list returns 0."""
        db_path = tmp_path / "test.db"
        db = Database(str(db_path), interactive=False)
        
        saved_count = db.save_ideas([])
        
        assert saved_count == 0
    
    def test_update_existing_idea(self, tmp_path):
        """Test that saving an idea with same source_id updates it."""
        db_path = tmp_path / "test.db"
        db = Database(str(db_path), interactive=False)
        
        # Save original idea
        idea1 = self._create_test_idea('test_001', title='Original Title')
        db.save_ideas([idea1])
        
        # Update the idea
        idea2 = self._create_test_idea('test_001', title='Updated Title')
        db.save_ideas([idea2])
        
        # Should still have only 1 idea
        ideas = db.get_ideas()
        assert len(ideas) == 1
        assert ideas[0]['idea']['title'] == 'Updated Title'
    
    def _create_test_idea(self, source_id: str, **kwargs) -> dict:
        """Helper method to create a test idea."""
        return {
            'source_id': source_id,
            'source': 'csv_import',
            'idea': {
                'title': kwargs.get('title', 'Test Idea'),
                'description': kwargs.get('description', 'Test Description'),
                'notes': kwargs.get('notes', ''),
                'category': kwargs.get('category', 'content'),
                'priority': kwargs.get('priority', 'medium')
            },
            'metadata': {
                'status': kwargs.get('status', 'new'),
                'created_by': kwargs.get('created_by', ''),
                'assigned_to': kwargs.get('assigned_to', ''),
                'tags': kwargs.get('tags', [])
            },
            'tracking': {
                'created_at': datetime.now().isoformat(),
                'modified_at': datetime.now().isoformat(),
                'used_at': None,
                'age_days': 0
            },
            'universal_metrics': {
                'priority_score': 5.0,
                'actionability': 5.0
            }
        }
