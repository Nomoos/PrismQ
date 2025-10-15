"""Tests for template synchronization."""

import pytest
from pathlib import Path
import shutil

from ..core.template import TemplateService, TemplateSyncError


class TestTemplateService:
    """Test suite for TemplateService."""
    
    @pytest.fixture
    def template_dir(self, tmp_path):
        """Create a template directory structure."""
        template = tmp_path / "template"
        template.mkdir()
        
        # Create directory structure
        (template / "src").mkdir()
        (template / "tests").mkdir()
        (template / "docs").mkdir()
        
        # Create files
        (template / "src" / "__init__.py").write_text("# init")
        (template / "tests" / "test_example.py").write_text("# test")
        (template / "docs" / "README.md").write_text("# README")
        (template / ".gitignore").write_text("*.pyc")
        
        return template
    
    @pytest.fixture
    def template_service(self, template_dir):
        """Create TemplateService with test template."""
        return TemplateService(template_dir)
    
    def test_copy_template_structure(self, template_service, tmp_path):
        """Test copying template structure to new directory."""
        target = tmp_path / "new_module"
        
        template_service.copy_template_structure(target)
        
        # Check directories exist
        assert (target / "src").exists()
        assert (target / "tests").exists()
        assert (target / "docs").exists()
        
        # Check files copied (except excluded ones)
        assert (target / "src" / "__init__.py").exists()
        assert (target / "tests" / "test_example.py").exists()
        # README.md should be excluded
        assert not (target / "docs" / "README.md").exists()
    
    def test_copy_template_raises_if_template_not_found(self, tmp_path):
        """Test that error is raised if template doesn't exist."""
        service = TemplateService(tmp_path / "nonexistent")
        target = tmp_path / "new_module"
        
        with pytest.raises(TemplateSyncError, match="Template directory not found"):
            service.copy_template_structure(target)
    
    def test_copy_template_raises_if_target_inside_template(self, template_service, template_dir):
        """Test that error is raised if target is inside template (circular reference)."""
        target = template_dir / "subdir"
        
        with pytest.raises(TemplateSyncError, match="subdirectory of template"):
            template_service.copy_template_structure(target)
    
    def test_sync_missing_files_adds_new_files(self, template_service, template_dir, tmp_path):
        """Test syncing missing files to existing directory."""
        target = tmp_path / "existing_module"
        target.mkdir()
        
        # Create partial structure (missing some files/dirs)
        (target / "src").mkdir()
        (target / "src" / "__init__.py").write_text("# existing")
        
        # Sync
        added = template_service.sync_missing_files(target)
        
        # Should have added missing directories and files
        assert len(added) > 0
        assert (target / "tests").exists()
        assert (target / "docs").exists()
        assert (target / "tests" / "test_example.py").exists()
        
        # Existing file should not be overwritten
        assert (target / "src" / "__init__.py").read_text() == "# existing"
    
    def test_sync_missing_files_no_changes_if_complete(self, template_service, template_dir, tmp_path):
        """Test sync when target already has all files."""
        target = tmp_path / "complete_module"
        
        # Copy entire template
        shutil.copytree(template_dir, target)
        
        # Sync should find nothing to add
        added = template_service.sync_missing_files(target)
        
        assert len(added) == 0
    
    def test_sync_missing_files_raises_if_target_not_found(self, template_service, tmp_path):
        """Test that error is raised if target doesn't exist."""
        target = tmp_path / "nonexistent"
        
        with pytest.raises(TemplateSyncError, match="Target directory not found"):
            template_service.sync_missing_files(target)
    
    def test_create_basic_structure(self, tmp_path):
        """Test creating basic module structure without template."""
        service = TemplateService(tmp_path / "nonexistent")
        target = tmp_path / "new_module"
        
        service.create_basic_structure(target)
        
        # Check standard directories
        assert (target / "src").exists()
        assert (target / "tests").exists()
        assert (target / "docs").exists()
        assert (target / "scripts").exists()
        assert (target / "issues" / "new").exists()
        assert (target / "issues" / "wip").exists()
        assert (target / "issues" / "done").exists()
        assert (target / ".github" / "ISSUE_TEMPLATE").exists()
        
        # Check __init__.py created
        init_file = target / "src" / "__init__.py"
        assert init_file.exists()
        assert '__version__' in init_file.read_text()
        
        # Check .gitignore created
        assert (target / ".gitignore").exists()
    
    def test_excluded_files_not_copied(self, template_service, template_dir, tmp_path):
        """Test that excluded files are not copied."""
        # Add excluded files to template
        (template_dir / ".git").mkdir()
        (template_dir / "module.json").write_text("{}")
        (template_dir / "pyproject.toml").write_text("[tool]")
        
        target = tmp_path / "new_module"
        template_service.copy_template_structure(target)
        
        # Excluded files should not be copied
        assert not (target / ".git").exists()
        assert not (target / "module.json").exists()
        assert not (target / "pyproject.toml").exists()
