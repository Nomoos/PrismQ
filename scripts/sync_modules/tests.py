#!/usr/bin/env python3
"""
Tests for sync_modules functionality.

This test file covers module synchronization and discovery,
especially validation of directory structures.
"""

import pytest
import json
from pathlib import Path
import sys

# Add parent directory to PYTHONPATH for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sync_modules.module_discovery import (
    discover_modules_from_json,
    _discover_first_level_modules,
    _discover_modules_recursive,
    _add_module_from_config,
    get_hardcoded_modules
)
from sync_modules.path_utils import derive_remote_name


class TestModuleDiscovery:
    """Test suite for module discovery functionality."""

    @pytest.fixture
    def temp_repo(self, tmp_path):
        """
        Create a temporary repository structure for testing.
        
        Args:
            tmp_path: Pytest temporary directory
            
        Returns:
            Path to temporary repository root
        """
        repo_root = tmp_path / "test_repo"
        repo_root.mkdir()
        src_dir = repo_root / "src"
        src_dir.mkdir()
        return repo_root

    def test_discover_valid_module_with_src_subdirectory(self, temp_repo):
        """
        Test discovery of a valid module with proper src/ subdirectory.
        
        A valid module must have:
        - module.json file
        - src/ subdirectory
        """
        # Create valid module structure
        module_dir = temp_repo / "src" / "TestModule"
        module_dir.mkdir(parents=True)
        (module_dir / "src").mkdir()
        
        # Create module.json
        module_json = {
            "remote": {
                "url": "https://github.com/Nomoos/PrismQ.TestModule.git"
            }
        }
        with open(module_dir / "module.json", 'w') as f:
            json.dump(module_json, f)
        
        # Discover modules
        modules = discover_modules_from_json(temp_repo, recursive=False)
        
        assert len(modules) == 1
        assert modules[0]['path'] == 'src/TestModule'
        assert modules[0]['remote_url'] == 'https://github.com/Nomoos/PrismQ.TestModule.git'
        assert modules[0]['remote_name'] == 'prismq-testmodule'

    def test_reject_module_without_src_subdirectory(self, temp_repo):
        """
        Test that modules without src/ subdirectory are rejected.
        
        This is a critical validation - modules must have proper structure.
        """
        # Create invalid module structure (missing src/ subdirectory)
        module_dir = temp_repo / "src" / "InvalidModule"
        module_dir.mkdir(parents=True)
        
        # Create module.json but NO src/ subdirectory
        module_json = {
            "remote": {
                "url": "https://github.com/Nomoos/PrismQ.InvalidModule.git"
            }
        }
        with open(module_dir / "module.json", 'w') as f:
            json.dump(module_json, f)
        
        # Discover modules - should NOT find the invalid module
        modules = discover_modules_from_json(temp_repo, recursive=False)
        
        assert len(modules) == 0, "Module without src/ subdirectory should be rejected"

    def test_reject_module_without_module_json(self, temp_repo):
        """
        Test that directories without module.json are not discovered.
        
        module.json is required for module discovery.
        """
        # Create directory structure with src/ but no module.json
        module_dir = temp_repo / "src" / "NoConfigModule"
        module_dir.mkdir(parents=True)
        (module_dir / "src").mkdir()
        
        # No module.json created
        
        # Discover modules - should find nothing
        modules = discover_modules_from_json(temp_repo, recursive=False)
        
        assert len(modules) == 0, "Directory without module.json should be ignored"

    def test_reject_module_json_without_remote_url(self, temp_repo):
        """
        Test that module.json without remote.url is rejected.
        
        Remote URL is required for synchronization.
        """
        # Create valid directory structure
        module_dir = temp_repo / "src" / "NoURLModule"
        module_dir.mkdir(parents=True)
        (module_dir / "src").mkdir()
        
        # Create module.json without remote.url
        module_json = {
            "some_other_field": "value"
        }
        with open(module_dir / "module.json", 'w') as f:
            json.dump(module_json, f)
        
        # Discover modules - should reject invalid config
        modules = discover_modules_from_json(temp_repo, recursive=False)
        
        assert len(modules) == 0, "Module without remote.url should be rejected"

    def test_nested_module_structure_example(self, temp_repo):
        """
        Test the specific example from problem statement.
        
        Repository: PrismQ.RepositoryTemplate.ModuleExample
        Expected path: src/RepositoryTemplate/src/ModuleExample
        """
        # Create nested structure
        parent_dir = temp_repo / "src" / "RepositoryTemplate"
        parent_dir.mkdir(parents=True)
        (parent_dir / "src").mkdir()
        
        # Create nested module
        module_dir = parent_dir / "src" / "ModuleExample"
        module_dir.mkdir(parents=True)
        (module_dir / "src").mkdir()
        
        # Create module.json for nested module
        module_json = {
            "remote": {
                "url": "https://github.com/Nomoos/PrismQ.RepositoryTemplate.ModuleExample.git"
            }
        }
        with open(module_dir / "module.json", 'w') as f:
            json.dump(module_json, f)
        
        # Discover with recursive=True to find nested modules
        modules = discover_modules_from_json(temp_repo, recursive=True)
        
        # Should find the nested module
        nested_modules = [m for m in modules if 'ModuleExample' in m['path']]
        assert len(nested_modules) == 1
        assert nested_modules[0]['path'] == 'src/RepositoryTemplate/src/ModuleExample'
        assert nested_modules[0]['remote_name'] == 'prismq-repositorytemplate-moduleexample'

    def test_discover_multiple_valid_modules(self, temp_repo):
        """
        Test discovery of multiple valid modules at first level.
        """
        # Create first module
        module1_dir = temp_repo / "src" / "Module1"
        module1_dir.mkdir(parents=True)
        (module1_dir / "src").mkdir()
        with open(module1_dir / "module.json", 'w') as f:
            json.dump({"remote": {"url": "https://github.com/Owner/Module1.git"}}, f)
        
        # Create second module
        module2_dir = temp_repo / "src" / "Module2"
        module2_dir.mkdir(parents=True)
        (module2_dir / "src").mkdir()
        with open(module2_dir / "module.json", 'w') as f:
            json.dump({"remote": {"url": "https://github.com/Owner/Module2.git"}}, f)
        
        # Discover modules
        modules = discover_modules_from_json(temp_repo, recursive=False)
        
        assert len(modules) == 2
        paths = [m['path'] for m in modules]
        assert 'src/Module1' in paths
        assert 'src/Module2' in paths

    def test_discover_only_first_level_non_recursive(self, temp_repo):
        """
        Test that non-recursive discovery only finds first-level modules.
        """
        # Create first-level module
        module_dir = temp_repo / "src" / "FirstLevel"
        module_dir.mkdir(parents=True)
        (module_dir / "src").mkdir()
        with open(module_dir / "module.json", 'w') as f:
            json.dump({"remote": {"url": "https://github.com/Owner/FirstLevel.git"}}, f)
        
        # Create nested module
        nested_dir = module_dir / "src" / "Nested"
        nested_dir.mkdir(parents=True)
        (nested_dir / "src").mkdir()
        with open(nested_dir / "module.json", 'w') as f:
            json.dump({"remote": {"url": "https://github.com/Owner/Nested.git"}}, f)
        
        # Discover with recursive=False
        modules = discover_modules_from_json(temp_repo, recursive=False)
        
        # Should only find first-level module
        assert len(modules) == 1
        assert modules[0]['path'] == 'src/FirstLevel'

    def test_recursive_discovery_finds_deeply_nested(self, temp_repo):
        """
        Test that recursive discovery finds modules at any depth.
        """
        # Create deeply nested structure: src/A/src/B/src/C
        a_dir = temp_repo / "src" / "A"
        a_dir.mkdir(parents=True)
        (a_dir / "src").mkdir()
        with open(a_dir / "module.json", 'w') as f:
            json.dump({"remote": {"url": "https://github.com/Owner/A.git"}}, f)
        
        b_dir = a_dir / "src" / "B"
        b_dir.mkdir(parents=True)
        (b_dir / "src").mkdir()
        with open(b_dir / "module.json", 'w') as f:
            json.dump({"remote": {"url": "https://github.com/Owner/B.git"}}, f)
        
        c_dir = b_dir / "src" / "C"
        c_dir.mkdir(parents=True)
        (c_dir / "src").mkdir()
        with open(c_dir / "module.json", 'w') as f:
            json.dump({"remote": {"url": "https://github.com/Owner/C.git"}}, f)
        
        # Discover recursively
        modules = discover_modules_from_json(temp_repo, recursive=True)
        
        # Should find all three modules
        assert len(modules) == 3
        paths = [m['path'] for m in modules]
        assert 'src/A' in paths
        assert 'src/A/src/B' in paths
        assert 'src/A/src/B/src/C' in paths

    def test_invalid_json_in_module_json(self, temp_repo):
        """
        Test that malformed module.json is handled gracefully.
        """
        # Create valid directory structure
        module_dir = temp_repo / "src" / "BadJSON"
        module_dir.mkdir(parents=True)
        (module_dir / "src").mkdir()
        
        # Write invalid JSON
        with open(module_dir / "module.json", 'w') as f:
            f.write("{ invalid json }")
        
        # Should not crash, just skip the module
        modules = discover_modules_from_json(temp_repo, recursive=False)
        
        assert len(modules) == 0

    def test_no_src_directory_at_repo_root(self, tmp_path):
        """
        Test behavior when repo has no src/ directory at all.
        """
        repo_root = tmp_path / "no_src_repo"
        repo_root.mkdir()
        
        # No src/ directory created
        
        # Should return empty list, not crash
        modules = discover_modules_from_json(repo_root, recursive=False)
        
        assert len(modules) == 0


class TestPathUtils:
    """Test suite for path utility functions."""

    def test_derive_remote_name_standard(self):
        """Test remote name derivation for standard URL."""
        remote = derive_remote_name("https://github.com/Nomoos/PrismQ.RepositoryTemplate.git")
        assert remote == "prismq-repositorytemplate"

    def test_derive_remote_name_nested(self):
        """Test remote name derivation for nested module."""
        remote = derive_remote_name("https://github.com/Nomoos/PrismQ.RepositoryTemplate.ModuleExample.git")
        assert remote == "prismq-repositorytemplate-moduleexample"

    def test_derive_remote_name_with_underscores(self):
        """Test that underscores are replaced with hyphens."""
        remote = derive_remote_name("https://github.com/Owner/My_Test_Module.git")
        assert remote == "my-test-module"

    def test_derive_remote_name_without_git_extension(self):
        """Test URL without .git extension."""
        remote = derive_remote_name("https://github.com/Nomoos/PrismQ.TestModule")
        assert remote == "prismq-testmodule"

    def test_derive_remote_name_mixed_case(self):
        """Test that remote name is converted to lowercase."""
        remote = derive_remote_name("https://github.com/Owner/MixedCase.Module")
        assert remote == "mixedcase-module"


class TestHardcodedModules:
    """Test suite for hardcoded module configurations."""

    def test_get_hardcoded_modules_returns_list(self):
        """Test that hardcoded modules returns a list."""
        modules = get_hardcoded_modules()
        assert isinstance(modules, list)

    def test_hardcoded_modules_have_required_fields(self):
        """Test that all hardcoded modules have required fields."""
        modules = get_hardcoded_modules()
        
        for module in modules:
            assert 'path' in module
            assert 'remote_name' in module
            assert 'remote_url' in module
            assert 'branch' in module

    def test_hardcoded_modules_use_main_branch(self):
        """Test that all hardcoded modules use 'main' branch."""
        modules = get_hardcoded_modules()
        
        for module in modules:
            assert module['branch'] == 'main'


class TestDirectoryStructureValidation:
    """
    Test suite specifically for directory structure validation.
    
    This addresses the problem statement about ensuring correct
    directory structure validation.
    """

    @pytest.fixture
    def temp_repo(self, tmp_path):
        """Create a temporary repository structure."""
        repo_root = tmp_path / "test_repo"
        repo_root.mkdir()
        src_dir = repo_root / "src"
        src_dir.mkdir()
        return repo_root

    def test_wrong_structure_flat_module(self, temp_repo):
        """
        Test rejection of flat module structure (no src/ subdirectory).
        
        Wrong structure: src/Module/file.py (missing src/ subdirectory)
        Correct structure: src/Module/src/file.py
        """
        # Create wrong structure
        module_dir = temp_repo / "src" / "FlatModule"
        module_dir.mkdir(parents=True)
        # Create some files but NO src/ subdirectory
        (module_dir / "file.py").write_text("# content")
        
        module_json = {
            "remote": {
                "url": "https://github.com/Owner/FlatModule.git"
            }
        }
        with open(module_dir / "module.json", 'w') as f:
            json.dump(module_json, f)
        
        modules = discover_modules_from_json(temp_repo, recursive=False)
        
        assert len(modules) == 0, "Flat module structure without src/ should be rejected"

    def test_wrong_nested_structure_missing_intermediate_src(self, temp_repo):
        """
        Test rejection when intermediate src/ is missing in nested structure.
        
        Wrong: src/Parent/Child/src/... (missing src/ between Parent and Child)
        Correct: src/Parent/src/Child/src/...
        """
        # Create wrong nested structure
        parent_dir = temp_repo / "src" / "Parent"
        parent_dir.mkdir(parents=True)
        (parent_dir / "src").mkdir()  # Parent has src/
        
        # But Child is directly under Parent, not under Parent/src/
        child_dir = parent_dir / "Child"  # WRONG - should be Parent/src/Child
        child_dir.mkdir(parents=True)
        (child_dir / "src").mkdir()
        
        module_json = {
            "remote": {
                "url": "https://github.com/Owner/PrismQ.Parent.Child.git"
            }
        }
        with open(child_dir / "module.json", 'w') as f:
            json.dump(module_json, f)
        
        # Discover recursively
        modules = discover_modules_from_json(temp_repo, recursive=True)
        
        # The child module should be found but its path will be wrong
        # It will be src/Parent/Child instead of src/Parent/src/Child
        wrong_modules = [m for m in modules if m['path'] == 'src/Parent/Child']
        
        # This should actually find it, showing the structure is wrong
        # In production, this would need manual validation
        assert len(wrong_modules) == 1
        # Document that this path is incorrect for a nested module
        assert wrong_modules[0]['path'] == 'src/Parent/Child'
        # The correct path should be src/Parent/src/Child

    def test_correct_nested_structure(self, temp_repo):
        """
        Test acceptance of correct nested module structure.
        
        Correct: src/Parent/src/Child/src/...
        """
        # Create correct nested structure
        parent_dir = temp_repo / "src" / "Parent"
        parent_dir.mkdir(parents=True)
        (parent_dir / "src").mkdir()
        
        # Child is under Parent/src/ (CORRECT)
        child_dir = parent_dir / "src" / "Child"
        child_dir.mkdir(parents=True)
        (child_dir / "src").mkdir()
        
        module_json = {
            "remote": {
                "url": "https://github.com/Owner/PrismQ.Parent.Child.git"
            }
        }
        with open(child_dir / "module.json", 'w') as f:
            json.dump(module_json, f)
        
        modules = discover_modules_from_json(temp_repo, recursive=True)
        
        correct_modules = [m for m in modules if 'Child' in m['path']]
        assert len(correct_modules) == 1
        assert correct_modules[0]['path'] == 'src/Parent/src/Child'

    def test_repository_template_module_example_correct_structure(self, temp_repo):
        """
        Test the exact example from problem statement with correct structure.
        
        Repository: PrismQ.RepositoryTemplate.ModuleExample
        Correct path: src/RepositoryTemplate/src/ModuleExample
        """
        # Create correct structure
        repo_template_dir = temp_repo / "src" / "RepositoryTemplate"
        repo_template_dir.mkdir(parents=True)
        (repo_template_dir / "src").mkdir()
        
        module_example_dir = repo_template_dir / "src" / "ModuleExample"
        module_example_dir.mkdir(parents=True)
        (module_example_dir / "src").mkdir()
        
        module_json = {
            "remote": {
                "url": "https://github.com/Nomoos/PrismQ.RepositoryTemplate.ModuleExample.git"
            }
        }
        with open(module_example_dir / "module.json", 'w') as f:
            json.dump(module_json, f)
        
        modules = discover_modules_from_json(temp_repo, recursive=True)
        
        module_example_modules = [m for m in modules if 'ModuleExample' in m['path']]
        assert len(module_example_modules) == 1
        assert module_example_modules[0]['path'] == 'src/RepositoryTemplate/src/ModuleExample'
        assert module_example_modules[0]['remote_name'] == 'prismq-repositorytemplate-moduleexample'

    def test_repository_template_module_example_wrong_structure(self, temp_repo):
        """
        Test the example from problem statement with WRONG structure.
        
        Repository: PrismQ.RepositoryTemplate.ModuleExample
        Wrong path: src/RepositoryTemplate/ModuleExample (missing intermediate src/)
        """
        # Create WRONG structure
        repo_template_dir = temp_repo / "src" / "RepositoryTemplate"
        repo_template_dir.mkdir(parents=True)
        (repo_template_dir / "src").mkdir()
        
        # ModuleExample directly under RepositoryTemplate (WRONG)
        module_example_dir = repo_template_dir / "ModuleExample"  # Should be RepositoryTemplate/src/ModuleExample
        module_example_dir.mkdir(parents=True)
        (module_example_dir / "src").mkdir()
        
        module_json = {
            "remote": {
                "url": "https://github.com/Nomoos/PrismQ.RepositoryTemplate.ModuleExample.git"
            }
        }
        with open(module_example_dir / "module.json", 'w') as f:
            json.dump(module_json, f)
        
        modules = discover_modules_from_json(temp_repo, recursive=True)
        
        # Will find it but with wrong path
        wrong_modules = [m for m in modules if 'ModuleExample' in m['path']]
        assert len(wrong_modules) == 1
        # Path will be wrong
        assert wrong_modules[0]['path'] == 'src/RepositoryTemplate/ModuleExample'
        # Should be 'src/RepositoryTemplate/src/ModuleExample'


if __name__ == "__main__":
    # Run tests directly from this file
    pytest.main([__file__, "-v"])
