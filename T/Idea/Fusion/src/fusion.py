"""Idea Fusion module for combining multiple Ideas or IdeaInspiration sources.

This module provides functionality to fuse multiple Ideas or IdeaInspiration
instances into new, cohesive Ideas using AI-powered combination logic.
"""

from typing import List, Dict, Any, Optional, Literal
from dataclasses import dataclass
import sys
import os

# Add parent directories to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
model_path = os.path.join(parent_dir, 'Model')
sys.path.insert(0, os.path.join(model_path, 'src'))
sys.path.insert(0, model_path)

from idea import Idea, ContentGenre, IdeaStatus


FusionStrategy = Literal["best_elements", "weighted_merge", "theme_based", "keyword_cluster"]


@dataclass
class FusionConfig:
    """Configuration for idea fusion process.
    
    Attributes:
        strategy: Fusion strategy to use
        title_generation: How to generate title ("ai", "combine", "first")
        preserve_sources: Whether to preserve source IDs in fused idea
        min_quality_score: Minimum quality score for source selection
        max_sources: Maximum number of sources to fuse
    """
    strategy: FusionStrategy = "best_elements"
    title_generation: Literal["ai", "combine", "first"] = "combine"
    preserve_sources: bool = True
    min_quality_score: int = 0
    max_sources: int = 10


class IdeaFusion:
    """Fuse multiple Ideas or IdeaInspiration sources into unified Ideas.
    
    This class implements various strategies for combining multiple source
    ideas into cohesive, new ideas that synthesize the best elements.
    """
    
    def __init__(self, config: Optional[FusionConfig] = None):
        """Initialize IdeaFusion with configuration.
        
        Args:
            config: Optional fusion configuration
        """
        self.config = config or FusionConfig()
    
    def fuse_ideas(
        self,
        sources: List[Idea],
        strategy: Optional[FusionStrategy] = None,
        title: Optional[str] = None,
        concept: Optional[str] = None,
        **kwargs
    ) -> Idea:
        """Fuse multiple Ideas into a single new Idea.
        
        Args:
            sources: List of source Ideas to fuse
            strategy: Fusion strategy (overrides config)
            title: Optional explicit title for fused idea
            concept: Optional explicit concept for fused idea
            **kwargs: Additional arguments to pass to Idea creation
            
        Returns:
            New Idea instance representing the fusion
            
        Raises:
            ValueError: If sources list is empty or invalid
        """
        if not sources:
            raise ValueError("Cannot fuse empty list of sources")
        
        if len(sources) > self.config.max_sources:
            sources = sources[:self.config.max_sources]
        
        strategy = strategy or self.config.strategy
        
        # Generate title if not provided
        if title is None:
            title = self._generate_title(sources)
        
        # Generate concept if not provided
        if concept is None:
            concept = self._generate_concept(sources, strategy)
        
        # Aggregate fields based on strategy
        fused_data = self._apply_fusion_strategy(sources, strategy)
        
        # Collect source IDs if configured
        inspiration_ids = []
        if self.config.preserve_sources:
            for source in sources:
                if hasattr(source, 'id') and source.id:
                    inspiration_ids.append(str(source.id))
                inspiration_ids.extend(source.inspiration_ids)
        
        # Remove duplicates while preserving order
        inspiration_ids = list(dict.fromkeys(inspiration_ids))
        
        # Create fused idea
        fused_idea = Idea(
            title=title,
            concept=concept,
            idea=fused_data.get("idea", ""),
            premise=fused_data.get("premise", ""),
            logline=fused_data.get("logline", ""),
            hook=fused_data.get("hook", ""),
            synopsis=fused_data.get("synopsis", ""),
            story_premise=fused_data.get("story_premise", ""),
            skeleton=fused_data.get("skeleton", ""),
            outline=fused_data.get("outline", ""),
            beat_sheet=fused_data.get("beat_sheet", ""),
            scenes=fused_data.get("scenes", ""),
            pov=fused_data.get("pov", ""),
            emotional_arc=fused_data.get("emotional_arc", ""),
            reveal=fused_data.get("reveal", ""),
            twist=fused_data.get("twist", ""),
            climax=fused_data.get("climax", ""),
            ending=fused_data.get("ending", ""),
            ending_type=fused_data.get("ending_type", ""),
            purpose=fused_data.get("purpose", ""),
            emotional_quality=fused_data.get("emotional_quality", ""),
            target_audience=fused_data.get("target_audience", ""),
            target_demographics=fused_data.get("target_demographics", {}),
            target_platforms=fused_data.get("target_platforms", []),
            target_formats=fused_data.get("target_formats", []),
            genre=fused_data.get("genre", ContentGenre.OTHER),
            style=fused_data.get("style", ""),
            keywords=fused_data.get("keywords", []),
            themes=fused_data.get("themes", []),
            character_notes=fused_data.get("character_notes", ""),
            setting_notes=fused_data.get("setting_notes", ""),
            tone_guidance=fused_data.get("tone_guidance", ""),
            length_target=fused_data.get("length_target", ""),
            potential_scores=fused_data.get("potential_scores", {}),
            inspiration_ids=inspiration_ids,
            status=IdeaStatus.DRAFT,
            notes=f"Fused from {len(sources)} source ideas using {strategy} strategy",
            created_by=kwargs.get("created_by", "IdeaFusion"),
            **{k: v for k, v in kwargs.items() if k != "created_by"}
        )
        
        return fused_idea
    
    def batch_fuse(
        self,
        source_pool: List[Idea],
        num_outputs: int,
        fusion_size: int = 3,
        strategy: Optional[FusionStrategy] = None
    ) -> List[Idea]:
        """Create multiple fused ideas from a pool of sources.
        
        Args:
            source_pool: Pool of source Ideas
            num_outputs: Number of fused ideas to create
            fusion_size: Number of sources to fuse per output
            strategy: Fusion strategy (overrides config)
            
        Returns:
            List of fused Idea instances
            
        Raises:
            ValueError: If source pool is too small
        """
        if len(source_pool) < fusion_size:
            raise ValueError(
                f"Source pool size ({len(source_pool)}) must be >= fusion_size ({fusion_size})"
            )
        
        fused_ideas = []
        strategy = strategy or self.config.strategy
        
        # Simple approach: divide pool into groups
        # For more sophisticated batching, implement clustering or scoring
        for i in range(num_outputs):
            # Select sources for this fusion (simple round-robin)
            start_idx = (i * fusion_size) % len(source_pool)
            sources = []
            for j in range(fusion_size):
                idx = (start_idx + j) % len(source_pool)
                sources.append(source_pool[idx])
            
            # Fuse the selected sources
            fused_idea = self.fuse_ideas(sources=sources, strategy=strategy)
            fused_ideas.append(fused_idea)
        
        return fused_ideas
    
    def _generate_title(self, sources: List[Idea]) -> str:
        """Generate title for fused idea.
        
        Args:
            sources: Source ideas
            
        Returns:
            Generated title
        """
        if self.config.title_generation == "first":
            return sources[0].title
        elif self.config.title_generation == "combine":
            # Simple combination - take key words from top sources
            titles = [s.title for s in sources[:3] if s.title]
            if titles:
                return " + ".join(titles[:2])
            return "Fused Idea"
        else:  # "ai"
            # Placeholder for AI generation - would integrate with LLM
            return f"Fused: {sources[0].title[:30]}..."
    
    def _generate_concept(self, sources: List[Idea], strategy: FusionStrategy) -> str:
        """Generate concept for fused idea.
        
        Args:
            sources: Source ideas
            strategy: Fusion strategy
            
        Returns:
            Generated concept
        """
        concepts = [s.concept for s in sources if s.concept]
        if not concepts:
            return "Fused concept from multiple sources"
        
        if strategy == "best_elements":
            # Take the most detailed concept
            return max(concepts, key=len)
        else:
            # Combine first two concepts
            if len(concepts) >= 2:
                return f"{concepts[0]} combined with {concepts[1]}"
            return concepts[0]
    
    def _apply_fusion_strategy(
        self,
        sources: List[Idea],
        strategy: FusionStrategy
    ) -> Dict[str, Any]:
        """Apply fusion strategy to combine source ideas.
        
        Args:
            sources: Source ideas
            strategy: Fusion strategy to apply
            
        Returns:
            Dictionary of fused field values
        """
        if strategy == "best_elements":
            return self._fuse_best_elements(sources)
        elif strategy == "weighted_merge":
            return self._fuse_weighted_merge(sources)
        elif strategy == "theme_based":
            return self._fuse_theme_based(sources)
        elif strategy == "keyword_cluster":
            return self._fuse_keyword_cluster(sources)
        else:
            return self._fuse_best_elements(sources)
    
    def _fuse_best_elements(self, sources: List[Idea]) -> Dict[str, Any]:
        """Fuse by selecting best element for each field.
        
        Selects the longest/most detailed value for each field.
        
        Args:
            sources: Source ideas
            
        Returns:
            Fused field values
        """
        result = {}
        
        # Text fields - take longest
        text_fields = [
            "idea", "premise", "logline", "hook", "synopsis", "story_premise",
            "skeleton", "outline", "beat_sheet", "scenes", "pov", "emotional_arc",
            "reveal", "twist", "climax", "ending", "ending_type", "purpose",
            "emotional_quality", "target_audience", "style", "character_notes",
            "setting_notes", "tone_guidance", "length_target"
        ]
        
        for field in text_fields:
            values = [getattr(s, field) for s in sources if getattr(s, field, "")]
            result[field] = max(values, key=len) if values else ""
        
        # List fields - merge and deduplicate
        result["keywords"] = self._merge_lists([s.keywords for s in sources])
        result["themes"] = self._merge_lists([s.themes for s in sources])
        result["target_platforms"] = self._merge_lists([s.target_platforms for s in sources])
        result["target_formats"] = self._merge_lists([s.target_formats for s in sources])
        
        # Dict fields - merge
        result["target_demographics"] = self._merge_dicts([s.target_demographics for s in sources])
        result["potential_scores"] = self._merge_scores([s.potential_scores for s in sources])
        
        # Enum fields - take from first or most common
        genres = [s.genre for s in sources if s.genre]
        result["genre"] = genres[0] if genres else ContentGenre.OTHER
        
        return result
    
    def _fuse_weighted_merge(self, sources: List[Idea]) -> Dict[str, Any]:
        """Fuse with weighted priority based on potential scores.
        
        Args:
            sources: Source ideas
            
        Returns:
            Fused field values
        """
        # Calculate weights based on potential scores
        weights = []
        for source in sources:
            if source.potential_scores:
                avg_score = sum(source.potential_scores.values()) / len(source.potential_scores)
                weights.append(avg_score)
            else:
                weights.append(1.0)
        
        # Normalize weights
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        else:
            weights = [1.0 / len(sources)] * len(sources)
        
        # Sort sources by weight
        sorted_sources = sorted(zip(sources, weights), key=lambda x: x[1], reverse=True)
        sources = [s for s, w in sorted_sources]
        
        # Use best_elements strategy but with weighted source order
        return self._fuse_best_elements(sources)
    
    def _fuse_theme_based(self, sources: List[Idea]) -> Dict[str, Any]:
        """Fuse based on common themes.
        
        Args:
            sources: Source ideas
            
        Returns:
            Fused field values
        """
        # Find common themes
        all_themes = [set(s.themes) for s in sources if s.themes]
        if len(all_themes) > 1:
            common_themes = set.intersection(*all_themes)
        else:
            common_themes = set()
        
        # Start with best_elements
        result = self._fuse_best_elements(sources)
        
        # Emphasize common themes
        if common_themes:
            result["themes"] = list(common_themes) + result["themes"]
            result["themes"] = list(dict.fromkeys(result["themes"]))  # Remove duplicates
        
        return result
    
    def _fuse_keyword_cluster(self, sources: List[Idea]) -> Dict[str, Any]:
        """Fuse based on keyword clustering.
        
        Args:
            sources: Source ideas
            
        Returns:
            Fused field values
        """
        # Count keyword frequencies
        keyword_counts: Dict[str, int] = {}
        for source in sources:
            for keyword in source.keywords:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # Start with best_elements
        result = self._fuse_best_elements(sources)
        
        # Prioritize most common keywords
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        result["keywords"] = [kw for kw, count in sorted_keywords]
        
        return result
    
    def _merge_lists(self, lists: List[List[str]]) -> List[str]:
        """Merge multiple lists, removing duplicates while preserving order.
        
        Args:
            lists: List of string lists to merge
            
        Returns:
            Merged list with duplicates removed
        """
        result = []
        seen = set()
        for lst in lists:
            for item in lst:
                if item not in seen:
                    result.append(item)
                    seen.add(item)
        return result
    
    def _merge_dicts(self, dicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multiple dictionaries, later values override earlier ones.
        
        Args:
            dicts: List of dictionaries to merge
            
        Returns:
            Merged dictionary
        """
        result = {}
        for d in dicts:
            result.update(d)
        return result
    
    def _merge_scores(self, score_dicts: List[Dict[str, int]]) -> Dict[str, int]:
        """Merge score dictionaries by averaging.
        
        Args:
            score_dicts: List of score dictionaries
            
        Returns:
            Merged scores (averaged)
        """
        result: Dict[str, List[int]] = {}
        for scores in score_dicts:
            for key, value in scores.items():
                if key not in result:
                    result[key] = []
                result[key].append(value)
        
        # Average the scores
        return {key: sum(values) // len(values) for key, values in result.items()}


__all__ = ["IdeaFusion", "FusionConfig", "FusionStrategy"]
