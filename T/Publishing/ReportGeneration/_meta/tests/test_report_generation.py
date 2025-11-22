"""Tests for ReportGeneration module."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

import pytest
import json
import tempfile
import shutil
from T.Publishing.ReportGeneration import (
    ReportGenerator,
    PublishingReport,
    generate_publishing_report
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_workflow_data():
    """Sample workflow data for testing."""
    return {
        "total_versions": 3,
        "total_reviews": 5,
        "total_iterations": 2,
        "workflow_duration": "3 days",
        "quality_gates_passed": ["Grammar", "Content", "Consistency"],
        "final_scores": {
            "grammar": 92,
            "content": 88,
            "consistency": 90
        },
        "reviews_history": [
            {"stage": "Grammar", "score": 92, "passed": True},
            {"stage": "Content", "score": 88, "passed": True}
        ]
    }


@pytest.fixture
def sample_export_result():
    """Sample export result for testing."""
    return {
        "formats_exported": ["json", "markdown", "html"],
        "export_paths": {
            "json": "/path/to/content.json",
            "markdown": "/path/to/content.md",
            "html": "/path/to/content.html"
        },
        "export_timestamp": "2025-11-22T22:00:00"
    }


class TestPublishingReport:
    """Test PublishingReport dataclass."""
    
    def test_create_basic_report(self):
        """Test creating a basic PublishingReport."""
        report = PublishingReport(
            content_id="test-001",
            title="Test Story"
        )
        
        assert report.content_id == "test-001"
        assert report.title == "Test Story"
        assert report.generation_timestamp is not None
        assert report.total_versions == 0
        assert report.total_reviews == 0
        assert len(report.quality_gates_passed) == 0
        assert len(report.export_formats) == 0
    
    def test_report_to_dict(self):
        """Test converting report to dictionary."""
        report = PublishingReport(
            content_id="test-001",
            title="Test Story",
            total_versions=3,
            quality_gates_passed=["Grammar", "Content"]
        )
        
        data = report.to_dict()
        
        assert data["content_id"] == "test-001"
        assert data["title"] == "Test Story"
        assert data["total_versions"] == 3
        assert "Grammar" in data["quality_gates_passed"]
    
    def test_report_to_json(self):
        """Test converting report to JSON."""
        report = PublishingReport(
            content_id="test-001",
            title="Test Story"
        )
        
        json_str = report.to_json()
        
        # Should be valid JSON
        data = json.loads(json_str)
        assert data["content_id"] == "test-001"
        assert data["title"] == "Test Story"


class TestReportGenerator:
    """Test ReportGenerator class."""
    
    def test_generator_initialization(self, temp_dir):
        """Test initializing the generator."""
        generator = ReportGenerator(output_dir=temp_dir)
        
        assert generator.output_dir == temp_dir
        assert temp_dir.exists()
    
    def test_generator_default_directory(self):
        """Test generator with default directory."""
        generator = ReportGenerator()
        
        assert generator.output_dir is not None
        assert generator.output_dir.exists()


class TestReportGeneration:
    """Test report generation functionality."""
    
    def test_generate_basic_report(self, temp_dir):
        """Test generating a basic report."""
        generator = ReportGenerator(output_dir=temp_dir)
        report = generator.generate_report(
            content_id="test-001",
            title="Test Story"
        )
        
        assert report.content_id == "test-001"
        assert report.title == "Test Story"
        assert report.summary != ""  # Should have generated summary
    
    def test_generate_report_with_workflow_data(self, temp_dir, sample_workflow_data):
        """Test generating report with workflow data."""
        generator = ReportGenerator(output_dir=temp_dir)
        report = generator.generate_report(
            content_id="test-001",
            title="Test Story",
            workflow_data=sample_workflow_data
        )
        
        assert report.total_versions == 3
        assert report.total_reviews == 5
        assert report.total_iterations == 2
        assert report.workflow_duration == "3 days"
        assert "Grammar" in report.quality_gates_passed
        assert report.final_scores["grammar"] == 92
    
    def test_generate_report_with_export_result(self, temp_dir, sample_export_result):
        """Test generating report with export result."""
        generator = ReportGenerator(output_dir=temp_dir)
        report = generator.generate_report(
            content_id="test-001",
            title="Test Story",
            export_result=sample_export_result
        )
        
        assert "json" in report.export_formats
        assert "markdown" in report.export_formats
        assert "html" in report.export_formats
        assert report.export_paths["json"] == "/path/to/content.json"
        assert report.export_timestamp == "2025-11-22T22:00:00"
    
    def test_generate_complete_report(self, temp_dir, sample_workflow_data, sample_export_result):
        """Test generating a complete report with all data."""
        generator = ReportGenerator(output_dir=temp_dir)
        report = generator.generate_report(
            content_id="test-001",
            title="Test Story",
            workflow_data=sample_workflow_data,
            export_result=sample_export_result
        )
        
        # Check workflow data
        assert report.total_versions == 3
        assert report.total_reviews == 5
        
        # Check export data
        assert len(report.export_formats) == 3
        
        # Check summary is generated
        assert report.summary != ""
        assert len(report.key_achievements) > 0


class TestSummaryGeneration:
    """Test summary generation."""
    
    def test_summary_includes_versions(self, temp_dir):
        """Test summary includes version information."""
        generator = ReportGenerator(output_dir=temp_dir)
        workflow_data = {"total_versions": 3}
        report = generator.generate_report(
            "test-001",
            "Test Story",
            workflow_data=workflow_data
        )
        
        assert any("3 version" in achievement for achievement in report.key_achievements)
    
    def test_summary_includes_reviews(self, temp_dir):
        """Test summary includes review information."""
        generator = ReportGenerator(output_dir=temp_dir)
        workflow_data = {"total_reviews": 5}
        report = generator.generate_report(
            "test-001",
            "Test Story",
            workflow_data=workflow_data
        )
        
        assert any("5 quality review" in achievement for achievement in report.key_achievements)
    
    def test_summary_includes_quality_gates(self, temp_dir):
        """Test summary includes quality gate information."""
        generator = ReportGenerator(output_dir=temp_dir)
        workflow_data = {"quality_gates_passed": ["Grammar", "Content"]}
        report = generator.generate_report(
            "test-001",
            "Test Story",
            workflow_data=workflow_data
        )
        
        assert any("quality gate" in achievement.lower() for achievement in report.key_achievements)


class TestJSONReportSaving:
    """Test saving reports as JSON."""
    
    def test_save_json_report(self, temp_dir):
        """Test saving report as JSON."""
        generator = ReportGenerator(output_dir=temp_dir)
        report = PublishingReport(content_id="test-001", title="Test Story")
        
        output_path = generator.save_report(report, format="json")
        
        assert output_path.exists()
        assert output_path.suffix == ".json"
        
        # Verify content
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data["content_id"] == "test-001"
        assert data["title"] == "Test Story"
    
    def test_json_custom_filename(self, temp_dir):
        """Test saving JSON with custom filename."""
        generator = ReportGenerator(output_dir=temp_dir)
        report = PublishingReport(content_id="test-001", title="Test Story")
        
        output_path = generator.save_report(report, format="json", filename="custom_report.json")
        
        assert output_path.name == "custom_report.json"
        assert output_path.exists()


class TestTextReportSaving:
    """Test saving reports as text."""
    
    def test_save_text_report(self, temp_dir):
        """Test saving report as text."""
        generator = ReportGenerator(output_dir=temp_dir)
        report = PublishingReport(
            content_id="test-001",
            title="Test Story",
            total_versions=3,
            quality_gates_passed=["Grammar"]
        )
        
        output_path = generator.save_report(report, format="txt")
        
        assert output_path.exists()
        assert output_path.suffix == ".txt"
        
        # Verify content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "PUBLISHING REPORT" in content
        assert "Test Story" in content
        assert "Total Versions: 3" in content
        assert "Grammar" in content
    
    def test_text_report_structure(self, temp_dir, sample_workflow_data):
        """Test text report has proper structure."""
        generator = ReportGenerator(output_dir=temp_dir)
        report = generator.generate_report(
            "test-001",
            "Test Story",
            workflow_data=sample_workflow_data
        )
        
        output_path = generator.save_report(report, format="txt")
        
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for sections
        assert "PUBLISHING REPORT" in content
        assert "WORKFLOW STATISTICS" in content
        assert "QUALITY GATES PASSED" in content
        assert "FINAL SCORES" in content
        assert "KEY ACHIEVEMENTS" in content


class TestMarkdownReportSaving:
    """Test saving reports as Markdown."""
    
    def test_save_markdown_report(self, temp_dir):
        """Test saving report as Markdown."""
        generator = ReportGenerator(output_dir=temp_dir)
        report = PublishingReport(
            content_id="test-001",
            title="Test Story",
            total_versions=3
        )
        
        output_path = generator.save_report(report, format="md")
        
        assert output_path.exists()
        assert output_path.suffix == ".md"
        
        # Verify content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "# Publishing Report: Test Story" in content
        assert "**Total Versions:** 3" in content
    
    def test_markdown_report_structure(self, temp_dir, sample_workflow_data, sample_export_result):
        """Test Markdown report has proper structure."""
        generator = ReportGenerator(output_dir=temp_dir)
        report = generator.generate_report(
            "test-001",
            "Test Story",
            workflow_data=sample_workflow_data,
            export_result=sample_export_result
        )
        
        output_path = generator.save_report(report, format="md")
        
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for Markdown elements
        assert content.startswith("# Publishing Report:")
        assert "## Summary" in content
        assert "## Workflow Statistics" in content
        assert "## Quality Gates Passed" in content
        assert "## Export Formats" in content
        assert "- ✓" in content  # Checkmarks for achievements


class TestErrorHandling:
    """Test error handling."""
    
    def test_unknown_format_raises_error(self, temp_dir):
        """Test that unknown format raises ValueError."""
        generator = ReportGenerator(output_dir=temp_dir)
        report = PublishingReport(content_id="test-001", title="Test Story")
        
        with pytest.raises(ValueError, match="Unknown format"):
            generator.save_report(report, format="unknown")


class TestConvenienceFunction:
    """Test the convenience generate_publishing_report function."""
    
    def test_convenience_function_basic(self, temp_dir):
        """Test using the convenience function."""
        report = generate_publishing_report(
            "test-001",
            "Test Story",
            output_dir=temp_dir
        )
        
        assert report.content_id == "test-001"
        assert report.title == "Test Story"
        assert report.summary != ""
    
    def test_convenience_function_with_save(self, temp_dir):
        """Test convenience function with auto-save."""
        report = generate_publishing_report(
            "test-001",
            "Test Story",
            output_dir=temp_dir,
            save_format="json"
        )
        
        # Should have saved the report
        expected_path = temp_dir / "test-001_report.json"
        assert expected_path.exists()
        
        # Verify content
        with open(expected_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data["content_id"] == "test-001"
    
    def test_convenience_function_complete(self, temp_dir, sample_workflow_data, sample_export_result):
        """Test convenience function with all data."""
        report = generate_publishing_report(
            "test-001",
            "Test Story",
            workflow_data=sample_workflow_data,
            export_result=sample_export_result,
            output_dir=temp_dir,
            save_format="md"
        )
        
        assert report.total_versions == 3
        assert len(report.export_formats) == 3
        
        # Should have saved the report
        expected_path = temp_dir / "test-001_report.md"
        assert expected_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
