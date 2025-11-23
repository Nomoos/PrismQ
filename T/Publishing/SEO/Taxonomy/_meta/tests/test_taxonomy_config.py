"""Tests for TaxonomyConfig module."""

import sys
from pathlib import Path
import json
import tempfile

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(project_root))

import pytest
from T.Publishing.SEO.Taxonomy.taxonomy_config import (
    TaxonomyConfig,
    load_taxonomy_config,
    create_custom_taxonomy,
    DEFAULT_TAXONOMY,
    TECH_FOCUSED_TAXONOMY,
    LIFESTYLE_FOCUSED_TAXONOMY
)


class TestTaxonomyConfig:
    """Test TaxonomyConfig dataclass."""
    
    def test_create_config(self):
        """Test creating a TaxonomyConfig."""
        config = TaxonomyConfig(
            categories={"Tech": ["AI", "Web"]},
            min_relevance=0.8,
            max_tags=5,
            max_categories=2
        )
        
        assert config.categories == {"Tech": ["AI", "Web"]}
        assert config.min_relevance == 0.8
        assert config.max_tags == 5
        assert config.max_categories == 2
    
    def test_default_values(self):
        """Test default configuration values."""
        config = TaxonomyConfig(categories={"Test": []})
        
        assert config.min_relevance == 0.7
        assert config.max_tags == 10
        assert config.max_categories == 3
        assert config.tag_similarity_threshold == 0.85
        assert config.enable_hierarchical is True
    
    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = TaxonomyConfig(
            categories={"Tech": ["AI"]},
            min_relevance=0.75
        )
        
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert "categories" in config_dict
        assert config_dict["min_relevance"] == 0.75
    
    def test_to_json(self):
        """Test converting config to JSON string."""
        config = TaxonomyConfig(
            categories={"Tech": ["AI"]},
            min_relevance=0.75
        )
        
        json_str = config.to_json()
        assert isinstance(json_str, str)
        
        # Parse to verify valid JSON
        parsed = json.loads(json_str)
        assert parsed["min_relevance"] == 0.75
    
    def test_to_json_with_file(self):
        """Test saving config to JSON file."""
        config = TaxonomyConfig(
            categories={"Tech": ["AI"]},
            min_relevance=0.75
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = Path(f.name)
        
        try:
            json_str = config.to_json(filepath=filepath)
            
            # Verify file was created
            assert filepath.exists()
            
            # Verify content
            loaded_data = json.loads(filepath.read_text())
            assert loaded_data["min_relevance"] == 0.75
        finally:
            # Clean up
            if filepath.exists():
                filepath.unlink()
    
    def test_get_all_categories(self):
        """Test getting flattened category list."""
        config = TaxonomyConfig(
            categories={
                "Tech": ["AI", "Web"],
                "Business": ["Marketing"]
            }
        )
        
        all_cats = config.get_all_categories()
        
        assert "Tech" in all_cats
        assert "Tech/AI" in all_cats
        assert "Tech/Web" in all_cats
        assert "Business" in all_cats
        assert "Business/Marketing" in all_cats
    
    def test_validate_valid_config(self):
        """Test validation with valid config."""
        config = TaxonomyConfig(
            categories={"Tech": []},
            min_relevance=0.7,
            max_tags=10,
            max_categories=3,
            tag_similarity_threshold=0.85
        )
        
        assert config.validate() is True
    
    def test_validate_invalid_min_relevance(self):
        """Test validation with invalid min_relevance."""
        config = TaxonomyConfig(
            categories={"Tech": []},
            min_relevance=1.5  # Invalid
        )
        
        with pytest.raises(ValueError, match="min_relevance must be between 0 and 1"):
            config.validate()
    
    def test_validate_invalid_max_tags(self):
        """Test validation with invalid max_tags."""
        config = TaxonomyConfig(
            categories={"Tech": []},
            max_tags=0  # Invalid
        )
        
        with pytest.raises(ValueError, match="max_tags must be at least 1"):
            config.validate()
    
    def test_validate_invalid_max_categories(self):
        """Test validation with invalid max_categories."""
        config = TaxonomyConfig(
            categories={"Tech": []},
            max_categories=-1  # Invalid
        )
        
        with pytest.raises(ValueError, match="max_categories must be at least 1"):
            config.validate()
    
    def test_validate_empty_categories(self):
        """Test validation with empty categories."""
        config = TaxonomyConfig(categories={})
        
        with pytest.raises(ValueError, match="categories cannot be empty"):
            config.validate()


class TestLoadTaxonomyConfig:
    """Test loading config from file."""
    
    def test_load_valid_config(self):
        """Test loading valid config file."""
        config_data = {
            "categories": {"Tech": ["AI", "Web"]},
            "min_relevance": 0.75,
            "max_tags": 8,
            "max_categories": 2
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            filepath = Path(f.name)
        
        try:
            config = load_taxonomy_config(filepath)
            
            assert config.categories == {"Tech": ["AI", "Web"]}
            assert config.min_relevance == 0.75
            assert config.max_tags == 8
        finally:
            if filepath.exists():
                filepath.unlink()
    
    def test_load_nonexistent_file(self):
        """Test loading non-existent file."""
        filepath = Path("/tmp/nonexistent_config.json")
        
        with pytest.raises(FileNotFoundError):
            load_taxonomy_config(filepath)
    
    def test_load_invalid_json(self):
        """Test loading invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json {")
            filepath = Path(f.name)
        
        try:
            with pytest.raises(ValueError, match="Invalid JSON"):
                load_taxonomy_config(filepath)
        finally:
            if filepath.exists():
                filepath.unlink()
    
    def test_load_invalid_structure(self):
        """Test loading config with invalid structure."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"invalid": "structure"}, f)
            filepath = Path(f.name)
        
        try:
            with pytest.raises(ValueError):
                load_taxonomy_config(filepath)
        finally:
            if filepath.exists():
                filepath.unlink()


class TestDefaultTaxonomy:
    """Test default taxonomy configuration."""
    
    def test_default_taxonomy_exists(self):
        """Test that DEFAULT_TAXONOMY is defined."""
        assert DEFAULT_TAXONOMY is not None
        assert isinstance(DEFAULT_TAXONOMY, TaxonomyConfig)
    
    def test_default_categories(self):
        """Test default categories."""
        assert len(DEFAULT_TAXONOMY.categories) > 0
        assert "Technology" in DEFAULT_TAXONOMY.categories
        assert "Business" in DEFAULT_TAXONOMY.categories
        assert "Lifestyle" in DEFAULT_TAXONOMY.categories
    
    def test_default_parameters(self):
        """Test default parameters."""
        assert DEFAULT_TAXONOMY.min_relevance == 0.7
        assert DEFAULT_TAXONOMY.max_tags == 10
        assert DEFAULT_TAXONOMY.max_categories == 3
    
    def test_default_validation(self):
        """Test that default config is valid."""
        assert DEFAULT_TAXONOMY.validate() is True


class TestPresetTaxonomies:
    """Test preset taxonomy configurations."""
    
    def test_tech_focused_taxonomy(self):
        """Test TECH_FOCUSED_TAXONOMY."""
        assert TECH_FOCUSED_TAXONOMY is not None
        assert isinstance(TECH_FOCUSED_TAXONOMY, TaxonomyConfig)
        
        # Should have tech-related categories
        assert "Programming" in TECH_FOCUSED_TAXONOMY.categories
        assert "AI & Machine Learning" in TECH_FOCUSED_TAXONOMY.categories
        
        # Should be valid
        assert TECH_FOCUSED_TAXONOMY.validate() is True
    
    def test_lifestyle_focused_taxonomy(self):
        """Test LIFESTYLE_FOCUSED_TAXONOMY."""
        assert LIFESTYLE_FOCUSED_TAXONOMY is not None
        assert isinstance(LIFESTYLE_FOCUSED_TAXONOMY, TaxonomyConfig)
        
        # Should have lifestyle-related categories
        assert "Health & Wellness" in LIFESTYLE_FOCUSED_TAXONOMY.categories
        assert "Home & Living" in LIFESTYLE_FOCUSED_TAXONOMY.categories
        
        # Should be valid
        assert LIFESTYLE_FOCUSED_TAXONOMY.validate() is True


class TestCreateCustomTaxonomy:
    """Test custom taxonomy creation."""
    
    def test_create_simple_taxonomy(self):
        """Test creating simple custom taxonomy."""
        config = create_custom_taxonomy(
            categories={"Cooking": ["Baking", "Grilling"]},
            min_relevance=0.65,
            max_tags=8,
            max_categories=2
        )
        
        assert config.categories == {"Cooking": ["Baking", "Grilling"]}
        assert config.min_relevance == 0.65
        assert config.max_tags == 8
        assert config.max_categories == 2
    
    def test_create_taxonomy_validation(self):
        """Test that created taxonomy is validated."""
        # Should raise error for invalid config
        with pytest.raises(ValueError):
            create_custom_taxonomy(
                categories={},  # Empty categories
                min_relevance=0.7
            )
    
    def test_create_taxonomy_defaults(self):
        """Test default values in custom taxonomy."""
        config = create_custom_taxonomy(
            categories={"Test": []}
        )
        
        # Should use default values
        assert config.min_relevance == 0.7
        assert config.max_tags == 10
        assert config.max_categories == 3


class TestTaxonomyConfigIntegration:
    """Test integration with other modules."""
    
    def test_config_with_tag_generator(self):
        """Test using config with tag generator."""
        from T.Publishing.SEO.Taxonomy.tag_generator import TagGenerator
        
        config = TaxonomyConfig(
            categories={"Tech": ["AI"]},
            max_tags=5,
            min_relevance=0.75
        )
        
        generator = TagGenerator(config=config)
        assert generator.config.max_tags == 5
        assert generator.config.min_relevance == 0.75
    
    def test_config_with_category_classifier(self):
        """Test using config with category classifier."""
        from T.Publishing.SEO.Taxonomy.category_classifier import CategoryClassifier
        
        config = TaxonomyConfig(
            categories={"Tech": ["AI"]},
            max_categories=2
        )
        
        classifier = CategoryClassifier(config=config)
        assert classifier.config.max_categories == 2


class TestEdgeCases:
    """Test edge cases."""
    
    def test_deeply_nested_categories(self):
        """Test with deeply nested categories (not supported but shouldn't crash)."""
        config = TaxonomyConfig(
            categories={
                "Parent": ["Child1", "Child2"]
            }
        )
        
        # Should handle gracefully
        all_cats = config.get_all_categories()
        assert "Parent" in all_cats
        assert "Parent/Child1" in all_cats
    
    def test_large_number_of_categories(self):
        """Test with many categories."""
        categories = {
            f"Category{i}": [f"Sub{j}" for j in range(5)]
            for i in range(20)
        }
        
        config = TaxonomyConfig(categories=categories)
        assert config.validate() is True
        
        all_cats = config.get_all_categories()
        assert len(all_cats) > 100  # 20 parents + 100 children
    
    def test_unicode_categories(self):
        """Test with unicode category names."""
        config = TaxonomyConfig(
            categories={"Technologie": ["IA", "Web"]}
        )
        
        assert config.validate() is True
