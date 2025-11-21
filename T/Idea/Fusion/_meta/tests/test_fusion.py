"""Tests for Idea Fusion module."""

import sys
import os
import pytest

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../Model/src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../Model'))

from fusion import IdeaFusion, FusionConfig
from idea import Idea, ContentGenre, IdeaStatus


class TestIdeaFusion:
    """Tests for IdeaFusion class."""
    
    def test_fuse_two_ideas_basic(self):
        """Test basic fusion of two ideas."""
        idea1 = Idea(
            title="Idea 1",
            concept="First concept",
            keywords=["tech", "ai"],
            themes=["innovation"],
            genre=ContentGenre.TECHNOLOGY
        )
        idea2 = Idea(
            title="Idea 2",
            concept="Second concept",
            keywords=["ai", "future"],
            themes=["innovation", "progress"],
            genre=ContentGenre.TECHNOLOGY
        )
        
        fusion = IdeaFusion()
        fused = fusion.fuse_ideas([idea1, idea2])
        
        assert fused is not None
        assert fused.title is not None
        assert fused.concept is not None
        assert "tech" in fused.keywords
        assert "ai" in fused.keywords
        assert "future" in fused.keywords
        assert "innovation" in fused.themes
        assert fused.genre == ContentGenre.TECHNOLOGY
    
    def test_fuse_ideas_with_best_elements_strategy(self):
        """Test fusion using best_elements strategy."""
        idea1 = Idea(
            title="Short",
            concept="Brief concept",
            premise="A short premise",
            synopsis="Short synopsis",
            keywords=["a", "b"],
            genre=ContentGenre.EDUCATIONAL
        )
        idea2 = Idea(
            title="Much Longer Title",
            concept="A much more detailed and comprehensive concept",
            premise="A very detailed and comprehensive premise with lots of context",
            synopsis="An extended synopsis with much more detail and information",
            keywords=["b", "c"],
            genre=ContentGenre.EDUCATIONAL
        )
        
        fusion = IdeaFusion()
        fused = fusion.fuse_ideas([idea1, idea2], strategy="best_elements")
        
        # Should select longer/more detailed values
        assert len(fused.premise) > len(idea1.premise)
        assert fused.premise == idea2.premise
        assert len(fused.synopsis) > len(idea1.synopsis)
        
        # Keywords should be merged
        assert "a" in fused.keywords
        assert "b" in fused.keywords
        assert "c" in fused.keywords
    
    def test_fuse_ideas_preserves_source_ids(self):
        """Test that source IDs are preserved in fusion."""
        idea1 = Idea(
            title="Idea 1",
            concept="First",
            inspiration_ids=["source1", "source2"]
        )
        idea2 = Idea(
            title="Idea 2",
            concept="Second",
            inspiration_ids=["source3"]
        )
        
        fusion = IdeaFusion()
        fused = fusion.fuse_ideas([idea1, idea2])
        
        assert "source1" in fused.inspiration_ids
        assert "source2" in fused.inspiration_ids
        assert "source3" in fused.inspiration_ids
    
    def test_fuse_ideas_with_explicit_title(self):
        """Test fusion with explicitly provided title."""
        idea1 = Idea(title="Idea 1", concept="First")
        idea2 = Idea(title="Idea 2", concept="Second")
        
        fusion = IdeaFusion()
        fused = fusion.fuse_ideas(
            [idea1, idea2],
            title="Custom Fused Title"
        )
        
        assert fused.title == "Custom Fused Title"
    
    def test_fuse_ideas_with_explicit_concept(self):
        """Test fusion with explicitly provided concept."""
        idea1 = Idea(title="Idea 1", concept="First")
        idea2 = Idea(title="Idea 2", concept="Second")
        
        fusion = IdeaFusion()
        fused = fusion.fuse_ideas(
            [idea1, idea2],
            concept="Custom fused concept"
        )
        
        assert fused.concept == "Custom fused concept"
    
    def test_fuse_empty_list_raises_error(self):
        """Test that fusing empty list raises ValueError."""
        fusion = IdeaFusion()
        with pytest.raises(ValueError, match="Cannot fuse empty list"):
            fusion.fuse_ideas([])
    
    def test_fuse_respects_max_sources_limit(self):
        """Test that fusion respects max_sources configuration."""
        ideas = [
            Idea(title=f"Idea {i}", concept=f"Concept {i}", keywords=[f"kw{i}"])
            for i in range(15)
        ]
        
        config = FusionConfig(max_sources=5)
        fusion = IdeaFusion(config)
        fused = fusion.fuse_ideas(ideas)
        
        # Only first 5 sources should be used
        assert len([kw for kw in fused.keywords if kw.startswith("kw")]) <= 5
    
    def test_fuse_merges_target_platforms(self):
        """Test that target platforms are merged correctly."""
        idea1 = Idea(
            title="Idea 1",
            concept="First",
            target_platforms=["youtube", "tiktok"]
        )
        idea2 = Idea(
            title="Idea 2",
            concept="Second",
            target_platforms=["tiktok", "instagram"]
        )
        
        fusion = IdeaFusion()
        fused = fusion.fuse_ideas([idea1, idea2])
        
        assert "youtube" in fused.target_platforms
        assert "tiktok" in fused.target_platforms
        assert "instagram" in fused.target_platforms
        # No duplicates
        assert fused.target_platforms.count("tiktok") == 1
    
    def test_fuse_merges_target_formats(self):
        """Test that target formats are merged correctly."""
        idea1 = Idea(
            title="Idea 1",
            concept="First",
            target_formats=["text", "audio"]
        )
        idea2 = Idea(
            title="Idea 2",
            concept="Second",
            target_formats=["audio", "video"]
        )
        
        fusion = IdeaFusion()
        fused = fusion.fuse_ideas([idea1, idea2])
        
        assert "text" in fused.target_formats
        assert "audio" in fused.target_formats
        assert "video" in fused.target_formats
        assert fused.target_formats.count("audio") == 1
    
    def test_fuse_merges_demographics(self):
        """Test that target demographics are merged."""
        idea1 = Idea(
            title="Idea 1",
            concept="First",
            target_demographics={"age": "18-25", "region": "US"}
        )
        idea2 = Idea(
            title="Idea 2",
            concept="Second",
            target_demographics={"age": "25-35", "interests": "tech"}
        )
        
        fusion = IdeaFusion()
        fused = fusion.fuse_ideas([idea1, idea2])
        
        assert "age" in fused.target_demographics
        assert "region" in fused.target_demographics
        assert "interests" in fused.target_demographics
    
    def test_fuse_averages_potential_scores(self):
        """Test that potential scores are averaged correctly."""
        idea1 = Idea(
            title="Idea 1",
            concept="First",
            potential_scores={"platform_youtube": 80, "region_us": 90}
        )
        idea2 = Idea(
            title="Idea 2",
            concept="Second",
            potential_scores={"platform_youtube": 60, "region_us": 70}
        )
        
        fusion = IdeaFusion()
        fused = fusion.fuse_ideas([idea1, idea2])
        
        # Should average: (80 + 60) / 2 = 70, (90 + 70) / 2 = 80
        assert fused.potential_scores["platform_youtube"] == 70
        assert fused.potential_scores["region_us"] == 80
    
    def test_fused_idea_has_draft_status(self):
        """Test that fused idea starts with DRAFT status."""
        idea1 = Idea(title="Idea 1", concept="First", status=IdeaStatus.APPROVED)
        idea2 = Idea(title="Idea 2", concept="Second", status=IdeaStatus.VALIDATED)
        
        fusion = IdeaFusion()
        fused = fusion.fuse_ideas([idea1, idea2])
        
        assert fused.status == IdeaStatus.DRAFT
    
    def test_fused_idea_has_notes(self):
        """Test that fused idea includes fusion notes."""
        idea1 = Idea(title="Idea 1", concept="First")
        idea2 = Idea(title="Idea 2", concept="Second")
        
        fusion = IdeaFusion()
        fused = fusion.fuse_ideas([idea1, idea2])
        
        assert "Fused from" in fused.notes
        assert "2 source ideas" in fused.notes


class TestBatchFusion:
    """Tests for batch fusion functionality."""
    
    def test_batch_fuse_basic(self):
        """Test basic batch fusion."""
        ideas = [
            Idea(title=f"Idea {i}", concept=f"Concept {i}")
            for i in range(6)
        ]
        
        fusion = IdeaFusion()
        fused_ideas = fusion.batch_fuse(
            source_pool=ideas,
            num_outputs=2,
            fusion_size=3
        )
        
        assert len(fused_ideas) == 2
        assert all(isinstance(idea, Idea) for idea in fused_ideas)
    
    def test_batch_fuse_with_small_pool_raises_error(self):
        """Test that batch fusion with small pool raises error."""
        ideas = [
            Idea(title="Idea 1", concept="Concept 1"),
            Idea(title="Idea 2", concept="Concept 2")
        ]
        
        fusion = IdeaFusion()
        with pytest.raises(ValueError, match="Source pool size"):
            fusion.batch_fuse(
                source_pool=ideas,
                num_outputs=2,
                fusion_size=3  # Requires at least 3 sources
            )
    
    def test_batch_fuse_creates_different_combinations(self):
        """Test that batch fusion creates different combinations."""
        ideas = [
            Idea(title=f"Idea {i}", concept=f"Concept {i}", keywords=[f"kw{i}"])
            for i in range(9)
        ]
        
        fusion = IdeaFusion()
        fused_ideas = fusion.batch_fuse(
            source_pool=ideas,
            num_outputs=3,
            fusion_size=3
        )
        
        assert len(fused_ideas) == 3
        # Each should have different keyword combinations
        keyword_sets = [set(idea.keywords) for idea in fused_ideas]
        assert keyword_sets[0] != keyword_sets[1]


class TestFusionStrategies:
    """Tests for different fusion strategies."""
    
    def test_weighted_merge_strategy(self):
        """Test weighted_merge strategy prioritizes high-scoring ideas."""
        idea1 = Idea(
            title="Low Score",
            concept="Low scoring concept",
            premise="Short",
            potential_scores={"score": 20}
        )
        idea2 = Idea(
            title="High Score",
            concept="High scoring concept",
            premise="This is a much longer and more detailed premise",
            potential_scores={"score": 90}
        )
        
        fusion = IdeaFusion()
        fused = fusion.fuse_ideas([idea1, idea2], strategy="weighted_merge")
        
        # Should prefer the high-scoring idea's premise
        assert len(fused.premise) > len(idea1.premise)
    
    def test_theme_based_strategy(self):
        """Test theme_based strategy emphasizes common themes."""
        idea1 = Idea(
            title="Idea 1",
            concept="First",
            themes=["innovation", "technology", "future"]
        )
        idea2 = Idea(
            title="Idea 2",
            concept="Second",
            themes=["innovation", "science", "future"]
        )
        idea3 = Idea(
            title="Idea 3",
            concept="Third",
            themes=["innovation", "future", "progress"]
        )
        
        fusion = IdeaFusion()
        fused = fusion.fuse_ideas([idea1, idea2, idea3], strategy="theme_based")
        
        # Common themes should be present and prioritized
        assert "innovation" in fused.themes
        assert "future" in fused.themes
    
    def test_keyword_cluster_strategy(self):
        """Test keyword_cluster strategy prioritizes common keywords."""
        idea1 = Idea(
            title="Idea 1",
            concept="First",
            keywords=["ai", "tech", "innovation"]
        )
        idea2 = Idea(
            title="Idea 2",
            concept="Second",
            keywords=["ai", "tech", "future"]
        )
        idea3 = Idea(
            title="Idea 3",
            concept="Third",
            keywords=["ai", "science"]
        )
        
        fusion = IdeaFusion()
        fused = fusion.fuse_ideas([idea1, idea2, idea3], strategy="keyword_cluster")
        
        # "ai" appears 3 times, "tech" 2 times - should be prioritized
        assert fused.keywords[0] == "ai"
        assert fused.keywords[1] == "tech"


class TestFusionConfig:
    """Tests for FusionConfig."""
    
    def test_config_defaults(self):
        """Test default configuration values."""
        config = FusionConfig()
        
        assert config.strategy == "best_elements"
        assert config.title_generation == "combine"
        assert config.preserve_sources is True
        assert config.min_quality_score == 0
        assert config.max_sources == 10
    
    def test_config_custom_values(self):
        """Test custom configuration values."""
        config = FusionConfig(
            strategy="weighted_merge",
            title_generation="ai",
            preserve_sources=False,
            min_quality_score=50,
            max_sources=5
        )
        
        assert config.strategy == "weighted_merge"
        assert config.title_generation == "ai"
        assert config.preserve_sources is False
        assert config.min_quality_score == 50
        assert config.max_sources == 5
    
    def test_fusion_uses_config(self):
        """Test that IdeaFusion uses provided config."""
        config = FusionConfig(preserve_sources=False)
        fusion = IdeaFusion(config)
        
        idea1 = Idea(title="Idea 1", concept="First", inspiration_ids=["s1"])
        idea2 = Idea(title="Idea 2", concept="Second", inspiration_ids=["s2"])
        
        fused = fusion.fuse_ideas([idea1, idea2])
        
        # Should not preserve sources when config.preserve_sources is False
        assert len(fused.inspiration_ids) == 0
