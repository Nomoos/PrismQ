"""Tests for CSV parser."""

import pytest
import pandas as pd
from pathlib import Path
from src.core.csv_parser import CSVParser


class TestCSVParser:
    """Test CSV parser functionality."""
    
    def test_initialization(self):
        """Test parser initialization with defaults."""
        parser = CSVParser()
        assert parser.default_priority == 'medium'
        assert parser.default_status == 'new'
        assert parser.default_category == 'general'
        assert parser.delimiter == ','
        assert parser.encoding == 'utf-8'
    
    def test_initialization_with_custom_values(self):
        """Test parser initialization with custom values."""
        parser = CSVParser(
            default_priority='high',
            default_status='in_progress',
            default_category='content',
            delimiter=';',
            encoding='utf-16'
        )
        assert parser.default_priority == 'high'
        assert parser.default_status == 'in_progress'
        assert parser.default_category == 'content'
        assert parser.delimiter == ';'
        assert parser.encoding == 'utf-16'
    
    def test_parse_simple_csv(self, tmp_path):
        """Test parsing a simple CSV file."""
        # Create test CSV
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("title,description\nIdea 1,Description 1\nIdea 2,Description 2\n")
        
        parser = CSVParser()
        ideas = parser.parse_file(str(csv_file))
        
        assert len(ideas) == 2
        assert ideas[0]['idea']['title'] == 'Idea 1'
        assert ideas[0]['idea']['description'] == 'Description 1'
        assert ideas[1]['idea']['title'] == 'Idea 2'
        assert ideas[1]['idea']['description'] == 'Description 2'
    
    def test_parse_csv_with_all_columns(self, tmp_path):
        """Test parsing CSV with all supported columns."""
        csv_file = tmp_path / "test.csv"
        csv_content = """title,description,category,priority,tags,status,notes,created_by,assigned_to
Video Idea,Make a video,content,high,"tag1,tag2",new,Some notes,John,Jane
"""
        csv_file.write_text(csv_content)
        
        parser = CSVParser()
        ideas = parser.parse_file(str(csv_file))
        
        assert len(ideas) == 1
        idea = ideas[0]
        
        assert idea['idea']['title'] == 'Video Idea'
        assert idea['idea']['description'] == 'Make a video'
        assert idea['idea']['category'] == 'content'
        assert idea['idea']['priority'] == 'high'
        assert idea['metadata']['status'] == 'new'
        assert idea['metadata']['tags'] == ['tag1', 'tag2']
        assert idea['metadata']['created_by'] == 'John'
        assert idea['metadata']['assigned_to'] == 'Jane'
        assert idea['idea']['notes'] == 'Some notes'
    
    def test_parse_csv_with_default_values(self, tmp_path):
        """Test that default values are used when columns are missing."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("title\nIdea 1\n")
        
        parser = CSVParser(
            default_priority='low',
            default_status='archived',
            default_category='general'
        )
        ideas = parser.parse_file(str(csv_file))
        
        assert len(ideas) == 1
        idea = ideas[0]
        
        assert idea['idea']['priority'] == 'low'
        assert idea['metadata']['status'] == 'archived'
        assert idea['idea']['category'] == 'general'
    
    def test_parse_csv_skips_empty_titles(self, tmp_path):
        """Test that rows without titles are skipped."""
        csv_file = tmp_path / "test.csv"
        csv_content = """title,description
Idea 1,Description 1
,No title row
Idea 3,Description 3
"""
        csv_file.write_text(csv_content)
        
        parser = CSVParser()
        ideas = parser.parse_file(str(csv_file))
        
        assert len(ideas) == 2
        assert ideas[0]['idea']['title'] == 'Idea 1'
        assert ideas[1]['idea']['title'] == 'Idea 3'
    
    def test_parse_csv_with_alternative_column_names(self, tmp_path):
        """Test that alternative column names are recognized."""
        csv_file = tmp_path / "test.csv"
        csv_content = """idea,desc,cat,pri,labels
Video Idea,Make a video,content,high,"tag1,tag2"
"""
        csv_file.write_text(csv_content)
        
        parser = CSVParser()
        ideas = parser.parse_file(str(csv_file))
        
        assert len(ideas) == 1
        idea = ideas[0]
        
        assert idea['idea']['title'] == 'Video Idea'
        assert idea['idea']['description'] == 'Make a video'
        assert idea['idea']['category'] == 'content'
        assert idea['idea']['priority'] == 'high'
        assert idea['metadata']['tags'] == ['tag1', 'tag2']
    
    def test_generate_source_id_is_unique(self):
        """Test that source IDs are unique and deterministic."""
        parser = CSVParser()
        
        id1 = parser._generate_source_id('Title 1', 'Desc 1', 0, '/path/file.csv')
        id2 = parser._generate_source_id('Title 2', 'Desc 2', 1, '/path/file.csv')
        id3 = parser._generate_source_id('Title 1', 'Desc 1', 0, '/path/file.csv')
        
        # Different inputs should produce different IDs
        assert id1 != id2
        
        # Same inputs should produce same ID
        assert id1 == id3
        
        # IDs should start with 'csv_'
        assert id1.startswith('csv_')
    
    def test_calculate_priority_score(self):
        """Test priority score calculation."""
        parser = CSVParser()
        
        assert parser._calculate_priority_score('high') == 8.0
        assert parser._calculate_priority_score('medium') == 5.0
        assert parser._calculate_priority_score('low') == 2.0
        assert parser._calculate_priority_score('critical') == 10.0
        assert parser._calculate_priority_score('unknown') == 5.0  # default
    
    def test_validate_csv_structure_valid(self, tmp_path):
        """Test CSV structure validation for valid file."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("title,description\nIdea 1,Desc 1\n")
        
        parser = CSVParser()
        validation = parser.validate_csv_structure(str(csv_file))
        
        assert validation['valid'] is True
        assert validation['has_title'] is True
        assert validation['total_rows'] == 1
        assert 'title' in validation['columns']
    
    def test_validate_csv_structure_missing_title(self, tmp_path):
        """Test CSV structure validation for file without title column."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("description,category\nDesc 1,Cat 1\n")
        
        parser = CSVParser()
        validation = parser.validate_csv_structure(str(csv_file))
        
        assert validation['valid'] is False
        assert validation['has_title'] is False
        assert 'error' in validation
        assert 'suggestions' in validation
    
    def test_parse_file_not_found(self):
        """Test that FileNotFoundError is raised for missing file."""
        parser = CSVParser()
        
        with pytest.raises(FileNotFoundError):
            parser.parse_file('/nonexistent/file.csv')
    
    def test_generate_batch_id(self):
        """Test batch ID generation."""
        parser = CSVParser()
        
        batch_id = parser._generate_batch_id('/path/to/ideas.csv')
        
        assert batch_id.startswith('ideas_')
        assert len(batch_id) > 10  # Should include timestamp
    
    def test_parse_csv_with_batch_id(self, tmp_path):
        """Test that batch ID is included in parsed ideas."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("title\nIdea 1\n")
        
        parser = CSVParser()
        ideas = parser.parse_file(str(csv_file), batch_id='test_batch')
        
        assert len(ideas) == 1
        assert ideas[0]['import_batch'] == 'test_batch'
    
    def test_idea_has_required_fields(self, tmp_path):
        """Test that parsed ideas have all required fields."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("title\nIdea 1\n")
        
        parser = CSVParser()
        ideas = parser.parse_file(str(csv_file))
        
        assert len(ideas) == 1
        idea = ideas[0]
        
        # Check required top-level fields
        assert 'source' in idea
        assert 'source_id' in idea
        assert 'idea' in idea
        assert 'metadata' in idea
        assert 'tracking' in idea
        assert 'universal_metrics' in idea
        
        # Check idea fields
        assert 'title' in idea['idea']
        assert 'description' in idea['idea']
        assert 'category' in idea['idea']
        assert 'priority' in idea['idea']
        
        # Check metadata fields
        assert 'status' in idea['metadata']
        assert 'tags' in idea['metadata']
        
        # Check tracking fields
        assert 'created_at' in idea['tracking']
        assert 'modified_at' in idea['tracking']
        
        # Check metrics
        assert 'priority_score' in idea['universal_metrics']
        assert 'actionability' in idea['universal_metrics']
