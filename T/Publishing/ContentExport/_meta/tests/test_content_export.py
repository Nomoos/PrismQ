"""Tests for ContentExport module."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

import pytest
import json
import tempfile
import shutil
from T.Publishing.ContentExport import (
    ContentExporter,
    ContentExportResult,
    export_content
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_content():
    """Sample content for testing."""
    return {
        "id": "test-001",
        "title": "Test Story Title",
        "script": "This is the test story content.\nIt has multiple lines.\n\nAnd paragraphs too.",
        "metadata": {
            "author": "Test Author",
            "date": "2025-11-22",
            "version": "v3",
            "genre": "Fiction"
        }
    }


class TestContentExportResult:
    """Test ContentExportResult dataclass."""
    
    def test_create_result(self):
        """Test creating a ContentExportResult."""
        result = ContentExportResult(content_id="test-001")
        
        assert result.content_id == "test-001"
        assert result.export_timestamp is not None
        assert len(result.formats_exported) == 0
        assert len(result.export_paths) == 0
        assert result.success is True
        assert len(result.errors) == 0
    
    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = ContentExportResult(
            content_id="test-001",
            formats_exported=["json", "markdown"],
            export_paths={"json": "/path/to/file.json"},
            success=True
        )
        
        data = result.to_dict()
        
        assert data["content_id"] == "test-001"
        assert "json" in data["formats_exported"]
        assert "json" in data["export_paths"]
        assert data["success"] is True


class TestContentExporter:
    """Test ContentExporter class."""
    
    def test_exporter_initialization(self, temp_dir):
        """Test initializing the exporter."""
        exporter = ContentExporter(output_dir=temp_dir)
        
        assert exporter.output_dir == temp_dir
        assert temp_dir.exists()
    
    def test_exporter_default_directory(self):
        """Test exporter with default directory."""
        exporter = ContentExporter()
        
        assert exporter.output_dir is not None
        assert exporter.output_dir.exists()


class TestJSONExport:
    """Test JSON export functionality."""
    
    def test_export_json(self, temp_dir, sample_content):
        """Test exporting content as JSON."""
        exporter = ContentExporter(output_dir=temp_dir)
        result = exporter.export_content(sample_content, "test-001", formats=["json"])
        
        assert result.success is True
        assert "json" in result.formats_exported
        assert "json" in result.export_paths
        
        # Verify file exists
        json_path = Path(result.export_paths["json"])
        assert json_path.exists()
        
        # Verify content
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data["id"] == "test-001"
        assert data["title"] == "Test Story Title"
        assert "This is the test story content" in data["script"]
        assert data["metadata"]["author"] == "Test Author"
    
    def test_json_format_validation(self, temp_dir, sample_content):
        """Test that exported JSON is valid."""
        exporter = ContentExporter(output_dir=temp_dir)
        result = exporter.export_content(sample_content, "test-001", formats=["json"])
        
        json_path = Path(result.export_paths["json"])
        
        # Should not raise exception
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert isinstance(data, dict)
        assert "export_timestamp" in data


class TestMarkdownExport:
    """Test Markdown export functionality."""
    
    def test_export_markdown(self, temp_dir, sample_content):
        """Test exporting content as Markdown."""
        exporter = ContentExporter(output_dir=temp_dir)
        result = exporter.export_content(sample_content, "test-001", formats=["markdown"])
        
        assert result.success is True
        assert "markdown" in result.formats_exported
        assert "markdown" in result.export_paths
        
        # Verify file exists
        md_path = Path(result.export_paths["markdown"])
        assert md_path.exists()
        
        # Verify content
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "# Test Story Title" in content
        assert "## Metadata" in content
        assert "Test Author" in content
        assert "This is the test story content" in content
    
    def test_markdown_structure(self, temp_dir, sample_content):
        """Test Markdown has proper structure."""
        exporter = ContentExporter(output_dir=temp_dir)
        result = exporter.export_content(sample_content, "test-001", formats=["markdown"])
        
        md_path = Path(result.export_paths["markdown"])
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for headers
        assert content.startswith("# ")
        assert "## Metadata" in content
        assert "## Content" in content
        
        # Check for metadata items
        assert "**Author**:" in content or "author" in content.lower()
        assert "**Genre**:" in content or "genre" in content.lower()


class TestHTMLExport:
    """Test HTML export functionality."""
    
    def test_export_html(self, temp_dir, sample_content):
        """Test exporting content as HTML."""
        exporter = ContentExporter(output_dir=temp_dir)
        result = exporter.export_content(sample_content, "test-001", formats=["html"])
        
        assert result.success is True
        assert "html" in result.formats_exported
        assert "html" in result.export_paths
        
        # Verify file exists
        html_path = Path(result.export_paths["html"])
        assert html_path.exists()
        
        # Verify content
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "<!DOCTYPE html>" in content
        assert "<title>Test Story Title</title>" in content
        assert "Test Author" in content
        assert "This is the test story content" in content
    
    def test_html_structure(self, temp_dir, sample_content):
        """Test HTML has proper structure."""
        exporter = ContentExporter(output_dir=temp_dir)
        result = exporter.export_content(sample_content, "test-001", formats=["html"])
        
        html_path = Path(result.export_paths["html"])
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required HTML elements
        assert "<!DOCTYPE html>" in content
        assert "<html" in content
        assert "<head>" in content
        assert "<body>" in content
        assert "</html>" in content
        
        # Check for CSS
        assert "<style>" in content
        
        # Check for metadata section
        assert 'class="metadata"' in content
    
    def test_html_escaping(self, temp_dir):
        """Test that HTML special characters are escaped."""
        content_with_html = {
            "id": "test-html",
            "title": "Test <script>alert('XSS')</script>",
            "script": "Content with <b>tags</b> & special chars",
            "metadata": {"note": "Test & test"}
        }
        
        exporter = ContentExporter(output_dir=temp_dir)
        result = exporter.export_content(content_with_html, "test-html", formats=["html"])
        
        html_path = Path(result.export_paths["html"])
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should escape special characters
        assert "&lt;script&gt;" in content
        assert "&amp;" in content
        # Should not contain raw script tag in title
        assert "<title>Test <script>" not in content


class TestMultiFormatExport:
    """Test exporting to multiple formats."""
    
    def test_export_all_formats(self, temp_dir, sample_content):
        """Test exporting to all formats."""
        exporter = ContentExporter(output_dir=temp_dir)
        result = exporter.export_content(sample_content, "test-001")
        
        assert result.success is True
        assert len(result.formats_exported) == 3
        assert "json" in result.formats_exported
        assert "markdown" in result.formats_exported
        assert "html" in result.formats_exported
        
        # Verify all files exist
        for format_name, path_str in result.export_paths.items():
            assert Path(path_str).exists()
    
    def test_export_selected_formats(self, temp_dir, sample_content):
        """Test exporting only selected formats."""
        exporter = ContentExporter(output_dir=temp_dir)
        result = exporter.export_content(
            sample_content,
            "test-001",
            formats=["json", "markdown"]
        )
        
        assert result.success is True
        assert len(result.formats_exported) == 2
        assert "json" in result.formats_exported
        assert "markdown" in result.formats_exported
        assert "html" not in result.formats_exported


class TestErrorHandling:
    """Test error handling."""
    
    def test_unknown_format(self, temp_dir, sample_content):
        """Test handling unknown format."""
        exporter = ContentExporter(output_dir=temp_dir)
        result = exporter.export_content(
            sample_content,
            "test-001",
            formats=["unknown_format"]
        )
        
        assert result.success is False
        assert len(result.errors) > 0
        assert "Unknown format" in result.errors[0]
    
    def test_empty_content(self, temp_dir):
        """Test exporting empty content."""
        empty_content = {
            "id": "",
            "title": "",
            "script": "",
            "metadata": {}
        }
        
        exporter = ContentExporter(output_dir=temp_dir)
        result = exporter.export_content(empty_content, "empty-001")
        
        # Should still succeed but files will be minimal
        assert result.success is True
        assert len(result.formats_exported) == 3


class TestValidation:
    """Test export validation."""
    
    def test_validate_successful_export(self, temp_dir, sample_content):
        """Test validating a successful export."""
        exporter = ContentExporter(output_dir=temp_dir)
        result = exporter.export_content(sample_content, "test-001")
        
        is_valid = exporter.validate_export(result)
        
        assert is_valid is True
        assert result.success is True
        assert len(result.errors) == 0
    
    def test_validate_missing_file(self, temp_dir):
        """Test validation catches missing files."""
        exporter = ContentExporter(output_dir=temp_dir)
        
        # Create a result with a non-existent path
        result = ContentExportResult(content_id="test-001")
        result.formats_exported = ["json"]
        result.export_paths = {"json": str(temp_dir / "nonexistent.json")}
        
        is_valid = exporter.validate_export(result)
        
        assert is_valid is False
        assert result.success is False
        assert len(result.errors) > 0


class TestConvenienceFunction:
    """Test the convenience export_content function."""
    
    def test_convenience_function(self, temp_dir, sample_content):
        """Test using the convenience function."""
        result = export_content(sample_content, "test-001", output_dir=temp_dir)
        
        assert result.success is True
        assert len(result.formats_exported) == 3
        
        # Verify all files exist
        for path_str in result.export_paths.values():
            assert Path(path_str).exists()
    
    def test_convenience_function_validation(self, temp_dir, sample_content):
        """Test that convenience function validates exports."""
        result = export_content(sample_content, "test-001", output_dir=temp_dir)
        
        # Should be validated automatically
        assert result.success is True
        
        # Verify files are readable
        for format_name, path_str in result.export_paths.items():
            with open(path_str, 'r', encoding='utf-8') as f:
                content = f.read()
                assert len(content) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
