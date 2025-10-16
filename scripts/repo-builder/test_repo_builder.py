#!/usr/bin/env python3
"""Tests for repo_builder.py"""

import pytest
from repo_builder import (
    parse_github_url,
    derive_module_chain,
    ModuleParseError,
)


class TestParseGitHubUrl:
    """Test suite for parse_github_url function."""
    
    def test_https_url_nomoos_prismq(self):
        """Test parsing HTTPS URL from Nomoos organization with PrismQ prefix."""
        url = "https://github.com/Nomoos/PrismQ.IdeaInspiration"
        result = parse_github_url(url)
        assert result == "PrismQ.IdeaInspiration"
    
    def test_https_url_nomoos_prismq_nested(self):
        """Test parsing HTTPS URL with nested module."""
        url = "https://github.com/Nomoos/PrismQ.IdeaInspiration.Sources.Content.Shorts.YouTubeSource"
        result = parse_github_url(url)
        assert result == "PrismQ.IdeaInspiration.Sources.Content.Shorts.YouTubeSource"
    
    def test_ssh_url_nomoos_prismq(self):
        """Test parsing SSH URL from Nomoos organization with PrismQ prefix."""
        url = "git@github.com:Nomoos/PrismQ.IdeaInspiration.git"
        result = parse_github_url(url)
        assert result == "PrismQ.IdeaInspiration"
    
    def test_ssh_url_nomoos_prismq_no_git_suffix(self):
        """Test parsing SSH URL without .git suffix."""
        url = "git@github.com:Nomoos/PrismQ.IdeaInspiration"
        result = parse_github_url(url)
        assert result == "PrismQ.IdeaInspiration"
    
    def test_non_nomoos_organization_rejected(self):
        """Test that non-Nomoos organization URLs are rejected."""
        url = "https://github.com/OtherOrg/PrismQ.IdeaInspiration"
        with pytest.raises(ModuleParseError, match="must be from Nomoos organization"):
            parse_github_url(url)
    
    def test_non_prismq_repo_rejected(self):
        """Test that repositories not starting with PrismQ. are rejected."""
        url = "https://github.com/Nomoos/OtherRepo"
        with pytest.raises(ModuleParseError, match="must start with PrismQ."):
            parse_github_url(url)
    
    def test_prismq_only_repo_rejected(self):
        """Test that repository named exactly 'PrismQ' without additional segments is rejected."""
        url = "https://github.com/Nomoos/PrismQ"
        with pytest.raises(ModuleParseError, match="must have at least one segment after PrismQ"):
            parse_github_url(url)
    
    def test_invalid_url_format(self):
        """Test that invalid URL format is rejected."""
        url = "not-a-url"
        with pytest.raises(ModuleParseError, match="Invalid GitHub URL format"):
            parse_github_url(url)


class TestDeriveModuleChain:
    """Test suite for derive_module_chain function."""
    
    def test_chain_order_root_to_deepest(self):
        """Test that chain is ordered from root to deepest."""
        module = "PrismQ.A.B.C"
        chain = derive_module_chain(module)
        expected = ["PrismQ", "PrismQ.A", "PrismQ.A.B", "PrismQ.A.B.C"]
        assert chain == expected
    
    def test_chain_simple_nested_module(self):
        """Test chain derivation for simple nested module."""
        module = "PrismQ.IdeaInspiration"
        chain = derive_module_chain(module)
        expected = ["PrismQ", "PrismQ.IdeaInspiration"]
        assert chain == expected
    
    def test_chain_deeply_nested_module(self):
        """Test chain derivation for deeply nested module."""
        module = "PrismQ.IdeaInspiration.Sources.Content.Shorts.YouTubeSource"
        chain = derive_module_chain(module)
        expected = [
            "PrismQ",
            "PrismQ.IdeaInspiration",
            "PrismQ.IdeaInspiration.Sources",
            "PrismQ.IdeaInspiration.Sources.Content",
            "PrismQ.IdeaInspiration.Sources.Content.Shorts",
            "PrismQ.IdeaInspiration.Sources.Content.Shorts.YouTubeSource"
        ]
        assert chain == expected
    
    def test_chain_from_github_url(self):
        """Test chain derivation from GitHub URL."""
        url = "https://github.com/Nomoos/PrismQ.IdeaInspiration.SubModule"
        chain = derive_module_chain(url)
        expected = ["PrismQ", "PrismQ.IdeaInspiration", "PrismQ.IdeaInspiration.SubModule"]
        assert chain == expected
    
    def test_module_without_prismq_prefix_rejected(self):
        """Test that module names not starting with PrismQ. are rejected."""
        module = "OtherModule.SubModule"
        with pytest.raises(ModuleParseError, match="must start with PrismQ."):
            derive_module_chain(module)
    
    def test_prismq_only_rejected(self):
        """Test that 'PrismQ' alone without additional segments is rejected."""
        module = "PrismQ"
        with pytest.raises(ModuleParseError, match="must have at least one segment after PrismQ"):
            derive_module_chain(module)
    
    def test_invalid_characters_rejected(self):
        """Test that module names with invalid characters are rejected."""
        module = "PrismQ.Invalid-Name"
        with pytest.raises(ModuleParseError, match="only alphanumeric segments"):
            derive_module_chain(module)
    
    def test_non_alphanumeric_segments_rejected(self):
        """Test that segments with non-alphanumeric characters are rejected."""
        module = "PrismQ.Invalid_Name"
        with pytest.raises(ModuleParseError, match="only alphanumeric segments"):
            derive_module_chain(module)
    
    def test_empty_segment_rejected(self):
        """Test that empty segments (double dots) are rejected."""
        module = "PrismQ..SubModule"
        with pytest.raises(ModuleParseError, match="Invalid module name format"):
            derive_module_chain(module)
    
    def test_segment_starting_with_number_rejected(self):
        """Test that segments starting with numbers are rejected."""
        module = "PrismQ.123Module"
        with pytest.raises(ModuleParseError, match="Invalid module name format"):
            derive_module_chain(module)


class TestInputNormalization:
    """Test suite for input normalization behavior."""
    
    def test_dotted_module_name_accepted(self):
        """Test that dotted module names are accepted and normalized."""
        module = "PrismQ.IdeaInspiration.SubModule"
        chain = derive_module_chain(module)
        assert len(chain) == 3
        assert chain[0] == "PrismQ"
        assert chain[-1] == "PrismQ.IdeaInspiration.SubModule"
    
    def test_https_url_normalized(self):
        """Test that HTTPS URLs are normalized to dotted notation."""
        url = "https://github.com/Nomoos/PrismQ.IdeaInspiration"
        chain = derive_module_chain(url)
        assert len(chain) == 2
        assert chain[-1] == "PrismQ.IdeaInspiration"
    
    def test_ssh_url_normalized(self):
        """Test that SSH URLs are normalized to dotted notation."""
        url = "git@github.com:Nomoos/PrismQ.IdeaInspiration.git"
        chain = derive_module_chain(url)
        assert len(chain) == 2
        assert chain[-1] == "PrismQ.IdeaInspiration"
