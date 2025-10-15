"""Tests for path derivation logic.

Tests cover:
- Positive cases: correct path derivation
- Negative cases: validation and error handling
- Edge cases: repetitive patterns, empty inputs
- Property-based tests with hypothesis
"""

import pytest
from hypothesis import given, strategies as st

from ..core.paths import (
    derive_module_path,
    derive_remote_name,
    parse_module_hierarchy,
    PathDerivationError
)


class TestDeriveModulePath:
    """Test suite for derive_module_path function."""
    
    def test_single_component(self):
        """Test single-level module: PrismQ.Module → src/Module"""
        module_name, module_path = derive_module_path("PrismQ.Module")
        assert module_name == "Module"
        assert module_path == "src/Module"
    
    def test_two_components(self):
        """Test two-level module: PrismQ.Parent.Child → src/Parent/src/Child"""
        module_name, module_path = derive_module_path("PrismQ.Parent.Child")
        assert module_name == "Parent.Child"
        assert module_path == "src/Parent/src/Child"
    
    def test_three_components(self):
        """Test three-level module: PrismQ.A.B.C → src/A/src/B/src/C"""
        module_name, module_path = derive_module_path("PrismQ.A.B.C")
        assert module_name == "A.B.C"
        assert module_path == "src/A/src/B/src/C"
    
    def test_repository_template(self):
        """Test real example: PrismQ.RepositoryTemplate"""
        module_name, module_path = derive_module_path("PrismQ.RepositoryTemplate")
        assert module_name == "RepositoryTemplate"
        assert module_path == "src/RepositoryTemplate"
    
    def test_idea_inspiration_sources(self):
        """Test real example: PrismQ.IdeaInspiration.Sources"""
        module_name, module_path = derive_module_path("PrismQ.IdeaInspiration.Sources")
        assert module_name == "IdeaInspiration.Sources"
        assert module_path == "src/IdeaInspiration/src/Sources"
    
    def test_deep_nesting(self):
        """Test deeply nested module with 6 levels"""
        repo_name = "PrismQ.IdeaInspiration.Sources.Content.Shorts.YouTubeSource"
        module_name, module_path = derive_module_path(repo_name)
        
        assert module_name == "IdeaInspiration.Sources.Content.Shorts.YouTubeSource"
        expected = "src/IdeaInspiration/src/Sources/src/Content/src/Shorts/src/YouTubeSource"
        assert module_path == expected
    
    def test_without_prismq_prefix(self):
        """Test module name without PrismQ. prefix"""
        module_name, module_path = derive_module_path("Module")
        assert module_name == "Module"
        assert module_path == "src/Module"
    
    def test_path_component_count_matches(self):
        """Test that number of components matches number of 'src/' in path"""
        test_cases = [
            ("PrismQ.A", 1),
            ("PrismQ.A.B", 2),
            ("PrismQ.A.B.C", 3),
            ("PrismQ.A.B.C.D", 4),
        ]
        
        for repo_name, expected_count in test_cases:
            _, module_path = derive_module_path(repo_name)
            src_count = module_path.count('src/')
            assert src_count == expected_count, f"For {repo_name}: expected {expected_count} 'src/', got {src_count}"
    
    def test_no_double_src(self):
        """Test that path never contains 'src/src' pattern"""
        test_cases = [
            "PrismQ.Module",
            "PrismQ.Parent.Child",
            "PrismQ.A.B.C",
            "PrismQ.RepositoryTemplate.ModuleExample",
            "PrismQ.Very.Deep.Nested.Module.Structure"
        ]
        
        for repo_name in test_cases:
            _, module_path = derive_module_path(repo_name)
            assert 'src/src' not in module_path, f"Path {module_path} contains 'src/src'"
    
    def test_no_repetitive_component_pattern(self):
        """Test that module components don't repeat in path"""
        # This should produce src/Test/src/Module, not src/Test/src/Test
        module_name, module_path = derive_module_path("PrismQ.Test.Module")
        assert 'Test/src/Test' not in module_path
        
        # Path should be well-formed
        assert module_path == "src/Test/src/Module"
    
    def test_path_starts_with_src(self):
        """Test that all paths start with 'src/'"""
        test_cases = [
            "PrismQ.Module",
            "PrismQ.Parent.Child",
            "PrismQ.A.B.C.D.E"
        ]
        
        for repo_name in test_cases:
            _, module_path = derive_module_path(repo_name)
            assert module_path.startswith('src/'), f"Path {module_path} doesn't start with 'src/'"
    
    def test_empty_repo_name_raises_error(self):
        """Test that empty repo name raises PathDerivationError"""
        with pytest.raises(PathDerivationError, match="cannot be empty"):
            derive_module_path("")
    
    def test_only_prismq_prefix_raises_error(self):
        """Test that 'PrismQ.' alone raises error"""
        with pytest.raises(PathDerivationError):
            derive_module_path("PrismQ.")
    
    def test_empty_component_raises_error(self):
        """Test that empty components raise error"""
        with pytest.raises(PathDerivationError):
            derive_module_path("PrismQ.Module..SubModule")
    
    @given(st.lists(st.text(min_size=1, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))), min_size=1, max_size=5))
    def test_property_no_src_src_pattern(self, components):
        """Property test: generated paths never contain 'src/src'"""
        repo_name = "PrismQ." + ".".join(components)
        try:
            _, module_path = derive_module_path(repo_name)
            assert 'src/src' not in module_path
        except PathDerivationError:
            # Invalid input is acceptable
            pass
    
    @given(st.lists(st.text(min_size=1, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))), min_size=1, max_size=5))
    def test_property_component_count_matches(self, components):
        """Property test: component count matches 'src/' count"""
        repo_name = "PrismQ." + ".".join(components)
        try:
            module_name, module_path = derive_module_path(repo_name)
            component_count = len(module_name.split('.'))
            src_count = module_path.count('src/')
            assert component_count == src_count
        except PathDerivationError:
            # Invalid input is acceptable
            pass


class TestDeriveRemoteName:
    """Test suite for derive_remote_name function."""
    
    def test_https_url_with_git(self):
        """Test HTTPS URL with .git suffix"""
        url = "https://github.com/Nomoos/PrismQ.Test.git"
        remote_name = derive_remote_name(url)
        assert remote_name == "prismq-test"
    
    def test_https_url_without_git(self):
        """Test HTTPS URL without .git suffix"""
        url = "https://github.com/Nomoos/PrismQ.Module"
        remote_name = derive_remote_name(url)
        assert remote_name == "prismq-module"
    
    def test_dots_replaced_with_hyphens(self):
        """Test that dots are replaced with hyphens"""
        url = "https://github.com/Nomoos/PrismQ.IdeaInspiration.Sources.git"
        remote_name = derive_remote_name(url)
        assert remote_name == "prismq-ideainspiration-sources"
        assert '.' not in remote_name
    
    def test_underscores_replaced_with_hyphens(self):
        """Test that underscores are replaced with hyphens"""
        url = "https://github.com/Nomoos/Test_Module_Name.git"
        remote_name = derive_remote_name(url)
        assert remote_name == "test-module-name"
        assert '_' not in remote_name
    
    def test_lowercase_conversion(self):
        """Test that remote name is lowercase"""
        url = "https://github.com/Nomoos/PrismQ.TestModule.git"
        remote_name = derive_remote_name(url)
        assert remote_name == "prismq-testmodule"
        assert remote_name.islower()


class TestParseModuleHierarchy:
    """Test suite for parse_module_hierarchy function."""
    
    def test_single_level(self):
        """Test single-level module"""
        hierarchy = parse_module_hierarchy("PrismQ.Module")
        assert hierarchy == ["PrismQ.Module"]
    
    def test_two_levels(self):
        """Test two-level module"""
        hierarchy = parse_module_hierarchy("PrismQ.Parent.Child")
        assert hierarchy == [
            "PrismQ.Parent",
            "PrismQ.Parent.Child"
        ]
    
    def test_three_levels(self):
        """Test three-level module"""
        hierarchy = parse_module_hierarchy("PrismQ.A.B.C")
        assert hierarchy == [
            "PrismQ.A",
            "PrismQ.A.B",
            "PrismQ.A.B.C"
        ]
    
    def test_deep_nesting(self):
        """Test deeply nested module"""
        hierarchy = parse_module_hierarchy("PrismQ.IdeaInspiration.Sources.Content.Shorts.YouTubeSource")
        assert hierarchy == [
            "PrismQ.IdeaInspiration",
            "PrismQ.IdeaInspiration.Sources",
            "PrismQ.IdeaInspiration.Sources.Content",
            "PrismQ.IdeaInspiration.Sources.Content.Shorts",
            "PrismQ.IdeaInspiration.Sources.Content.Shorts.YouTubeSource"
        ]
    
    def test_all_have_prismq_prefix(self):
        """Test that all levels have PrismQ prefix"""
        hierarchy = parse_module_hierarchy("PrismQ.A.B.C")
        for level in hierarchy:
            assert level.startswith("PrismQ.")
