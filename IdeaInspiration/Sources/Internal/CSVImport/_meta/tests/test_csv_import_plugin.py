"""Tests for CSV import plugin."""

import pytest
from unittest.mock import Mock
from pathlib import Path
from src.plugins.csv_import_plugin import CSVImportPlugin


class TestCSVImportPlugin:
    """Test CSV import plugin functionality."""
    
    def test_initialization(self):
        """Test plugin initialization."""
        config = Mock()
        config.default_priority = 'medium'
        config.default_status = 'new'
        config.default_category = 'general'
        config.csv_delimiter = ','
        config.csv_encoding = 'utf-8'
        
        plugin = CSVImportPlugin(config)
        
        assert plugin.config == config
        assert plugin.get_source_name() == "csv_import"
        assert plugin.parser is not None
    
    def test_scrape_with_file_path(self, tmp_path):
        """Test scraping with provided file path."""
        # Create test CSV
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("title,description\nIdea 1,Description 1\n")
        
        # Mock config
        config = Mock()
        config.default_priority = 'medium'
        config.default_status = 'new'
        config.default_category = 'general'
        config.csv_delimiter = ','
        config.csv_encoding = 'utf-8'
        
        plugin = CSVImportPlugin(config)
        ideas = plugin.scrape(str(csv_file))
        
        assert len(ideas) == 1
        assert ideas[0]['idea']['title'] == 'Idea 1'
    
    def test_scrape_with_config_path(self, tmp_path):
        """Test scraping using config default path."""
        # Create test CSV
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("title\nIdea 1\n")
        
        # Mock config with default_csv_path
        config = Mock()
        config.default_csv_path = str(csv_file)
        config.default_priority = 'medium'
        config.default_status = 'new'
        config.default_category = 'general'
        config.csv_delimiter = ','
        config.csv_encoding = 'utf-8'
        
        plugin = CSVImportPlugin(config)
        ideas = plugin.scrape()
        
        assert len(ideas) == 1
    
    def test_scrape_missing_file(self):
        """Test scraping with non-existent file."""
        config = Mock()
        config.default_priority = 'medium'
        config.default_status = 'new'
        config.default_category = 'general'
        config.csv_delimiter = ','
        config.csv_encoding = 'utf-8'
        
        plugin = CSVImportPlugin(config)
        ideas = plugin.scrape('/nonexistent/file.csv')
        
        assert len(ideas) == 0
    
    def test_scrape_no_path_provided(self):
        """Test scraping without file path and no config default."""
        config = Mock()
        config.default_csv_path = None
        config.default_priority = 'medium'
        config.default_status = 'new'
        config.default_category = 'general'
        config.csv_delimiter = ','
        config.csv_encoding = 'utf-8'
        
        plugin = CSVImportPlugin(config)
        ideas = plugin.scrape()
        
        assert len(ideas) == 0
    
    def test_scrape_invalid_csv_structure(self, tmp_path):
        """Test scraping CSV without required title column."""
        # Create CSV without title
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("description,category\nDesc 1,Cat 1\n")
        
        config = Mock()
        config.default_priority = 'medium'
        config.default_status = 'new'
        config.default_category = 'general'
        config.csv_delimiter = ','
        config.csv_encoding = 'utf-8'
        
        plugin = CSVImportPlugin(config)
        ideas = plugin.scrape(str(csv_file))
        
        assert len(ideas) == 0
    
    def test_scrape_with_batch_id(self, tmp_path):
        """Test scraping with custom batch ID."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("title\nIdea 1\n")
        
        config = Mock()
        config.default_priority = 'medium'
        config.default_status = 'new'
        config.default_category = 'general'
        config.csv_delimiter = ','
        config.csv_encoding = 'utf-8'
        
        plugin = CSVImportPlugin(config)
        ideas = plugin.scrape(str(csv_file), batch_id='custom_batch')
        
        assert len(ideas) == 1
        assert ideas[0]['import_batch'] == 'custom_batch'
    
    def test_import_multiple_files_success(self, tmp_path):
        """Test importing multiple files successfully."""
        # Create test CSVs
        csv1 = tmp_path / "test1.csv"
        csv1.write_text("title\nIdea 1\n")
        
        csv2 = tmp_path / "test2.csv"
        csv2.write_text("title\nIdea 2\nIdea 3\n")
        
        config = Mock()
        config.default_priority = 'medium'
        config.default_status = 'new'
        config.default_category = 'general'
        config.csv_delimiter = ','
        config.csv_encoding = 'utf-8'
        
        plugin = CSVImportPlugin(config)
        results = plugin.import_multiple_files([str(csv1), str(csv2)])
        
        assert results['total_files'] == 2
        assert results['successful_files'] == 2
        assert results['failed_files'] == 0
        assert results['total_ideas'] == 3
    
    def test_import_multiple_files_with_failures(self, tmp_path):
        """Test importing multiple files with some failures."""
        # Create one valid CSV
        csv1 = tmp_path / "test1.csv"
        csv1.write_text("title\nIdea 1\n")
        
        # Create one invalid CSV (missing title)
        csv2 = tmp_path / "invalid.csv"
        csv2.write_text("description\nNo title here\n")
        
        config = Mock()
        config.default_priority = 'medium'
        config.default_status = 'new'
        config.default_category = 'general'
        config.csv_delimiter = ','
        config.csv_encoding = 'utf-8'
        
        plugin = CSVImportPlugin(config)
        
        # Import one valid and one invalid file
        results = plugin.import_multiple_files([str(csv1), str(csv2)])
        
        assert results['total_files'] == 2
        assert results['successful_files'] == 2  # Both files processed, but one has 0 ideas
        assert results['failed_files'] == 0
        # Only the valid file contributed ideas
        assert results['total_ideas'] == 1
    
    def test_get_source_name(self):
        """Test that source name is correct."""
        config = Mock()
        config.default_priority = 'medium'
        config.default_status = 'new'
        config.default_category = 'general'
        config.csv_delimiter = ','
        config.csv_encoding = 'utf-8'
        
        plugin = CSVImportPlugin(config)
        
        assert plugin.get_source_name() == "csv_import"
