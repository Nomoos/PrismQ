"""Idea Creation module for generating Ideas from simple inputs.

This module provides functionality to create multiple Ideas from minimal
inputs like titles or descriptions, using AI-powered generation for
variable-length content optimized for different platforms.

Supports both AI-powered generation (via Ollama) and fallback placeholder
generation when AI is not available.
"""

from typing import List, Dict, Any, Optional, Literal
from dataclasses import dataclass
import sys
import os
import logging

# Add parent directories to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
model_path = os.path.join(parent_dir, 'Model')
sys.path.insert(0, os.path.join(model_path, 'src'))
sys.path.insert(0, model_path)

from idea import Idea, ContentGenre, IdeaStatus
from ai_generator import AIIdeaGenerator, AIConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Common English stop words for keyword extraction
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", 
    "of", "with", "is", "are", "was", "were", "been", "be", "have", "has", 
    "had", "do", "does", "did", "will", "would", "could", "should", "may",
    "might", "can", "must", "shall"
}


@dataclass
class CreationConfig:
    """Configuration for idea creation process.
    
    Attributes:
        min_title_length: Minimum title length in characters
        max_title_length: Maximum title length in characters
        min_story_length: Minimum story/synopsis length in words
        max_story_length: Maximum story/synopsis length in words
        variation_degree: How different generated ideas should be (low/medium/high)
        include_all_fields: Whether to generate all narrative fields
        use_ai: Whether to use AI for generation (requires Ollama)
        ai_model: AI model to use (e.g., "llama3.1:70b-q4_K_M")
        ai_temperature: Temperature for AI generation (0.0-2.0)
        default_num_ideas: Default number of ideas to generate
    """
    min_title_length: int = 20
    max_title_length: int = 100
    min_story_length: int = 100
    max_story_length: int = 1000
    variation_degree: Literal["low", "medium", "high"] = "medium"
    include_all_fields: bool = True
    use_ai: bool = True  # Enable AI by default
    ai_model: str = "llama3.1:70b-q4_K_M"  # Best for RTX 5090
    ai_temperature: float = 0.8
    default_num_ideas: int = 10  # Default to 10 ideas as per requirements


class IdeaCreator:
    """Create multiple Ideas from simple inputs like titles or descriptions.
    
    This class generates rich, detailed Ideas from minimal input using
    AI-powered content generation (via Ollama) with variable length optimization.
    Falls back to placeholder generation when AI is not available.
    """
    
    def __init__(self, config: Optional[CreationConfig] = None):
        """Initialize IdeaCreator with configuration.
        
        Args:
            config: Optional creation configuration
        """
        self.config = config or CreationConfig()
        
        # Initialize AI generator if enabled
        self.ai_generator = None
        if self.config.use_ai:
            ai_config = AIConfig(
                model=self.config.ai_model,
                temperature=self.config.ai_temperature
            )
            self.ai_generator = AIIdeaGenerator(ai_config)
            
            if self.ai_generator.available:
                logger.info(f"AI generation enabled with model: {self.config.ai_model}")
            else:
                logger.warning("AI generation requested but Ollama not available, using fallback")
                self.ai_generator = None
    
    def create_from_title(
        self,
        title: str,
        num_ideas: int = None,  # Changed to None to use default from config
        target_platforms: Optional[List[str]] = None,
        target_formats: Optional[List[str]] = None,
        genre: Optional[ContentGenre] = None,
        length_target: Optional[str] = None,
        **kwargs
    ) -> List[Idea]:
        """Create multiple Ideas from a title.
        
        Args:
            title: Base title to generate ideas from
            num_ideas: Number of ideas to generate (default: 10 from config)
            target_platforms: Optional target platforms
            target_formats: Optional target formats
            genre: Optional content genre
            length_target: Optional length target specification
            **kwargs: Additional arguments to pass to Idea creation
            
        Returns:
            List of generated Idea instances
            
        Raises:
            ValueError: If title is empty or num_ideas < 1
        """
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")
        
        # Use default from config if not specified
        if num_ideas is None:
            num_ideas = self.config.default_num_ideas
            
        if num_ideas < 1:
            raise ValueError("num_ideas must be at least 1")
        
        # Try AI generation first if available
        if self.ai_generator:
            try:
                ai_ideas = self.ai_generator.generate_ideas_from_title(
                    title=title,
                    num_ideas=num_ideas,
                    target_platforms=target_platforms,
                    target_formats=target_formats,
                    genre=genre.value if genre else None,
                    length_target=length_target
                )
                
                if ai_ideas:
                    return self._create_ideas_from_ai_data(
                        ai_ideas=ai_ideas,
                        target_platforms=target_platforms,
                        target_formats=target_formats,
                        genre=genre,
                        length_target=length_target,
                        source_type="title",
                        source=title,
                        **kwargs
                    )
                else:
                    logger.warning("AI generation returned no ideas, using fallback")
            except Exception as e:
                logger.warning(f"AI generation failed: {e}, using fallback")
        
        # Fallback to placeholder generation
        return self._create_ideas_from_title_fallback(
            title=title,
            num_ideas=num_ideas,
            target_platforms=target_platforms,
            target_formats=target_formats,
            genre=genre,
            length_target=length_target,
            **kwargs
        )
    
    def create_from_description(
        self,
        description: str,
        num_ideas: int = None,  # Changed to None to use default from config
        target_platforms: Optional[List[str]] = None,
        target_formats: Optional[List[str]] = None,
        genre: Optional[ContentGenre] = None,
        length_target: Optional[str] = None,
        **kwargs
    ) -> List[Idea]:
        """Create multiple Ideas from a description.
        
        Args:
            description: Base description to generate ideas from
            num_ideas: Number of ideas to generate (default: 10 from config)
            target_platforms: Optional target platforms
            target_formats: Optional target formats
            genre: Optional content genre
            length_target: Optional length target specification
            **kwargs: Additional arguments to pass to Idea creation
            
        Returns:
            List of generated Idea instances
            
        Raises:
            ValueError: If description is empty or num_ideas < 1
        """
        if not description or not description.strip():
            raise ValueError("Description cannot be empty")
        
        # Use default from config if not specified
        if num_ideas is None:
            num_ideas = self.config.default_num_ideas
            
        if num_ideas < 1:
            raise ValueError("num_ideas must be at least 1")
        
        # Try AI generation first if available
        if self.ai_generator:
            try:
                ai_ideas = self.ai_generator.generate_ideas_from_description(
                    description=description,
                    num_ideas=num_ideas,
                    target_platforms=target_platforms,
                    target_formats=target_formats,
                    genre=genre.value if genre else None,
                    length_target=length_target
                )
                
                if ai_ideas:
                    return self._create_ideas_from_ai_data(
                        ai_ideas=ai_ideas,
                        target_platforms=target_platforms,
                        target_formats=target_formats,
                        genre=genre,
                        length_target=length_target,
                        source_type="description",
                        source=description,
                        **kwargs
                    )
                else:
                    logger.warning("AI generation returned no ideas, using fallback")
            except Exception as e:
                logger.warning(f"AI generation failed: {e}, using fallback")
        
        # Fallback to placeholder generation
        return self._create_ideas_from_description_fallback(
            description=description,
            num_ideas=num_ideas,
            target_platforms=target_platforms,
            target_formats=target_formats,
            genre=genre,
            length_target=length_target,
            **kwargs
        )
    
    def _create_ideas_from_ai_data(
        self,
        ai_ideas: List[Dict[str, Any]],
        target_platforms: Optional[List[str]] = None,
        target_formats: Optional[List[str]] = None,
        genre: Optional[ContentGenre] = None,
        length_target: Optional[str] = None,
        source_type: str = "unknown",
        source: str = "",
        **kwargs
    ) -> List[Idea]:
        """Create Idea objects from AI-generated data.
        
        Args:
            ai_ideas: List of idea dictionaries from AI
            target_platforms: Target platforms
            target_formats: Target formats
            genre: Content genre
            length_target: Target length
            source_type: Type of source (title/description)
            source: Original source text
            **kwargs: Additional Idea arguments
            
        Returns:
            List of Idea instances
        """
        ideas = []
        for i, ai_idea in enumerate(ai_ideas):
            idea = Idea(
                title=ai_idea.get('title', f'Untitled Idea {i + 1}'),
                concept=ai_idea.get('concept', ''),
                idea=ai_idea.get('title', ''),  # Use title as basic idea spark
                premise=ai_idea.get('premise', ''),
                logline=ai_idea.get('logline', ''),
                hook=ai_idea.get('hook', ''),
                synopsis=ai_idea.get('synopsis', ''),
                story_premise=ai_idea.get('premise', ''),  # Same as premise
                skeleton=ai_idea.get('skeleton', ''),
                outline=ai_idea.get('outline', ''),
                target_platforms=target_platforms or ["youtube", "medium"],
                target_formats=target_formats or ["text", "video"],
                genre=genre or ContentGenre.OTHER,
                length_target=length_target or "variable",
                keywords=ai_idea.get('keywords', []),
                themes=ai_idea.get('themes', []),
                status=IdeaStatus.DRAFT,
                notes=f"AI-generated from {source_type}: '{source}' (variation {i + 1}/{len(ai_ideas)})",
                created_by=kwargs.get("created_by", "IdeaCreator-AI"),
                **{k: v for k, v in kwargs.items() if k != "created_by"}
            )
            ideas.append(idea)
        
        return ideas
    
    def _create_ideas_from_title_fallback(
        self,
        title: str,
        num_ideas: int,
        target_platforms: Optional[List[str]] = None,
        target_formats: Optional[List[str]] = None,
        genre: Optional[ContentGenre] = None,
        length_target: Optional[str] = None,
        **kwargs
    ) -> List[Idea]:
        """Fallback method for creating ideas from title without AI.
        
        This is the original implementation that uses placeholder generation.
        """
        ideas = []
        for i in range(num_ideas):
            # Generate variations based on variation_degree
            variation_suffix = self._get_variation_suffix(i, num_ideas)
            
            # Generate title variation
            idea_title = self._generate_title_variation(title, i, num_ideas)
            
            # Generate concept from title
            concept = self._generate_concept_from_title(title, i)
            
            # Generate detailed narrative fields
            narrative_fields = self._generate_narrative_fields(
                title=idea_title,
                concept=concept,
                variation_index=i
            )
            
            # Create the idea
            idea = Idea(
                title=idea_title,
                concept=concept,
                idea=narrative_fields.get("idea", ""),
                premise=narrative_fields.get("premise", ""),
                logline=narrative_fields.get("logline", ""),
                hook=narrative_fields.get("hook", ""),
                synopsis=narrative_fields.get("synopsis", ""),
                story_premise=narrative_fields.get("story_premise", ""),
                skeleton=narrative_fields.get("skeleton", ""),
                outline=narrative_fields.get("outline", ""),
                target_platforms=target_platforms or ["youtube", "medium"],
                target_formats=target_formats or ["text", "video"],
                genre=genre or ContentGenre.OTHER,
                length_target=length_target or "variable",
                keywords=narrative_fields.get("keywords", []),
                themes=narrative_fields.get("themes", []),
                status=IdeaStatus.DRAFT,
                notes=f"Generated from title: '{title}' (variation {i + 1}/{num_ideas})",
                created_by=kwargs.get("created_by", "IdeaCreator"),
                **{k: v for k, v in kwargs.items() if k != "created_by"}
            )
            
            ideas.append(idea)
        
        return ideas
    
    def _create_ideas_from_description_fallback(
        self,
        description: str,
        num_ideas: int,
        target_platforms: Optional[List[str]] = None,
        target_formats: Optional[List[str]] = None,
        genre: Optional[ContentGenre] = None,
        length_target: Optional[str] = None,
        **kwargs
    ) -> List[Idea]:
        """Fallback method for creating ideas from description without AI.
        
        This is the original implementation that uses placeholder generation.
        """
        ideas = []
        for i in range(num_ideas):
            # Generate title from description
            title = self._generate_title_from_description(description, i)
            
            # Use description as base concept
            concept = self._generate_concept_from_description(description, i)
            
            # Generate detailed narrative fields
            narrative_fields = self._generate_narrative_fields(
                title=title,
                concept=concept,
                description=description,
                variation_index=i
            )
            
            # Create the idea
            idea = Idea(
                title=title,
                concept=concept,
                idea=narrative_fields.get("idea", ""),
                premise=narrative_fields.get("premise", ""),
                logline=narrative_fields.get("logline", ""),
                hook=narrative_fields.get("hook", ""),
                synopsis=narrative_fields.get("synopsis", ""),
                story_premise=narrative_fields.get("story_premise", ""),
                skeleton=narrative_fields.get("skeleton", ""),
                outline=narrative_fields.get("outline", ""),
                target_platforms=target_platforms or ["youtube", "medium"],
                target_formats=target_formats or ["text", "video"],
                genre=genre or ContentGenre.OTHER,
                length_target=length_target or "variable",
                keywords=narrative_fields.get("keywords", []),
                themes=narrative_fields.get("themes", []),
                status=IdeaStatus.DRAFT,
                notes=f"Generated from description (variation {i + 1}/{num_ideas})",
                created_by=kwargs.get("created_by", "IdeaCreator"),
                **{k: v for k, v in kwargs.items() if k != "created_by"}
            )
            
            ideas.append(idea)
        
        return ideas
    
    def _get_variation_suffix(self, index: int, total: int) -> str:
        """Get variation suffix for diversity.
        
        Args:
            index: Current variation index
            total: Total number of variations
            
        Returns:
            Variation suffix string
        """
        if self.config.variation_degree == "low":
            return ""
        elif self.config.variation_degree == "medium":
            variations = ["", " (Alternative)", " (Variant)"]
            return variations[index % len(variations)]
        else:  # high
            variations = [
                "", " (Version A)", " (Version B)", " (Alternative)",
                " (Variant)", " (Perspective 1)", " (Perspective 2)"
            ]
            return variations[index % len(variations)]
    
    def _generate_title_variation(self, base_title: str, index: int, total: int) -> str:
        """Generate a title variation.
        
        Args:
            base_title: Base title to vary
            index: Variation index
            total: Total variations
            
        Returns:
            Varied title
        """
        if index == 0:
            return base_title
        
        # Simple variations for demonstration
        # In production, this would use AI for more sophisticated variations
        variations = [
            base_title,
            f"{base_title}: A Deep Dive",
            f"Understanding {base_title}",
            f"{base_title} Explained",
            f"The Truth About {base_title}",
            f"{base_title}: Behind the Scenes"
        ]
        
        return variations[index % len(variations)]
    
    def _generate_concept_from_title(self, title: str, variation: int) -> str:
        """Generate a concept from a title.
        
        Args:
            title: Title to generate concept from
            variation: Variation index for diversity
            
        Returns:
            Generated concept
        """
        # In production, this would use AI for sophisticated concept generation
        # For now, we create a basic concept
        approaches = [
            f"An exploration of {title.lower()} and its implications",
            f"Understanding the key aspects of {title.lower()}",
            f"A comprehensive look at {title.lower()}",
            f"Examining {title.lower()} from multiple perspectives"
        ]
        
        return approaches[variation % len(approaches)]
    
    def _generate_title_from_description(self, description: str, variation: int) -> str:
        """Generate a title from a description.
        
        Args:
            description: Description to generate title from
            variation: Variation index
            
        Returns:
            Generated title
        """
        # Extract key words from description (simple approach)
        words = description.split()[:5]  # First 5 words
        base = " ".join(words)
        
        # Limit title length
        if len(base) > self.config.max_title_length:
            base = base[:self.config.max_title_length - 3] + "..."
        
        if variation == 0:
            return base
        
        # Add variation suffix
        suffixes = ["", ": The Story", ": Revealed", ": Explained", ": A Journey"]
        suffix = suffixes[variation % len(suffixes)]
        
        title = base + suffix
        if len(title) > self.config.max_title_length:
            title = title[:self.config.max_title_length]
        
        return title
    
    def _generate_concept_from_description(self, description: str, variation: int) -> str:
        """Generate a concept from a description.
        
        Args:
            description: Description to generate concept from
            variation: Variation index
            
        Returns:
            Generated concept
        """
        # Use description as base, potentially with variations
        if variation == 0:
            return description
        
        # Add perspective variations
        perspectives = [
            description,
            f"{description} - Exploring the deeper implications",
            f"{description} - A fresh perspective",
            f"{description} - Understanding the complete picture"
        ]
        
        return perspectives[variation % len(perspectives)]
    
    def _generate_narrative_fields(
        self,
        title: str,
        concept: str,
        description: Optional[str] = None,
        variation_index: int = 0
    ) -> Dict[str, Any]:
        """Generate detailed narrative fields for an idea.
        
        In production, this would use AI for sophisticated content generation.
        For now, we create structured placeholders.
        
        Args:
            title: Idea title
            concept: Idea concept
            description: Optional base description
            variation_index: Variation index for diversity
            
        Returns:
            Dictionary of narrative field values
        """
        fields = {}
        
        if not self.config.include_all_fields:
            # Minimal fields
            fields["synopsis"] = concept
            fields["keywords"] = self._extract_keywords(title, concept)
            fields["themes"] = self._extract_themes(title, concept)
            return fields
        
        # Generate all narrative fields
        base_text = description or concept
        
        # Story Foundation
        fields["idea"] = self._generate_idea_field(title, base_text, variation_index)
        fields["premise"] = self._generate_premise(title, base_text, variation_index)
        fields["logline"] = self._generate_logline(title, base_text, variation_index)
        fields["hook"] = self._generate_hook(title, base_text, variation_index)
        
        # Story Structure
        fields["synopsis"] = self._generate_synopsis(title, base_text, variation_index)
        fields["story_premise"] = fields["premise"]  # Same as premise
        fields["skeleton"] = self._generate_skeleton(title, variation_index)
        fields["outline"] = self._generate_outline(title, variation_index)
        
        # Extract keywords and themes
        fields["keywords"] = self._extract_keywords(title, concept)
        fields["themes"] = self._extract_themes(title, concept)
        
        return fields
    
    def _generate_idea_field(self, title: str, base_text: str, variation: int) -> str:
        """Generate the 'idea' field (basic spark)."""
        # Extract core concept
        words = title.split()[:3]
        return " ".join(words)
    
    def _generate_premise(self, title: str, base_text: str, variation: int) -> str:
        """Generate premise (1-3 sentence explanation)."""
        return f"{base_text} This explores the fundamental aspects and implications of the topic."
    
    def _generate_logline(self, title: str, base_text: str, variation: int) -> str:
        """Generate logline (one-sentence dramatic version)."""
        return f"Discover the truth behind {title.lower()} in this compelling exploration."
    
    def _generate_hook(self, title: str, base_text: str, variation: int) -> str:
        """Generate hook (attention-grabbing opening)."""
        hooks = [
            f"What if everything you knew about {title.lower()} was wrong?",
            f"The story behind {title.lower()} will surprise you.",
            f"You won't believe what we discovered about {title.lower()}."
        ]
        return hooks[variation % len(hooks)]
    
    def _generate_synopsis(self, title: str, base_text: str, variation: int) -> str:
        """Generate synopsis (1-3 paragraph summary)."""
        # Generate synopsis of variable length based on config
        target_words = (self.config.min_story_length + self.config.max_story_length) // 2
        
        # Simple approach: extend base text
        synopsis = f"{base_text}\n\n"
        synopsis += f"This content explores {title.lower()} through detailed analysis and "
        synopsis += "compelling storytelling. We examine the key elements, implications, "
        synopsis += "and broader context to provide a comprehensive understanding.\n\n"
        synopsis += "Through this exploration, viewers will gain valuable insights and "
        synopsis += "perspectives that challenge conventional thinking."
        
        return synopsis
    
    def _generate_skeleton(self, title: str, variation: int) -> str:
        """Generate skeleton (3-6 point overview)."""
        return f"1. Introduction to {title}\n2. Core concepts and principles\n" \
               f"3. Key insights and analysis\n4. Practical implications\n" \
               f"5. Conclusion and takeaways"
    
    def _generate_outline(self, title: str, variation: int) -> str:
        """Generate outline (detailed plan)."""
        return f"Introduction: Hook the audience\n" \
               f"Section 1: Background and context for {title}\n" \
               f"Section 2: Deep dive into key aspects\n" \
               f"Section 3: Analysis and insights\n" \
               f"Section 4: Practical applications\n" \
               f"Conclusion: Summary and call to action"
    
    def _extract_keywords(self, title: str, concept: str) -> List[str]:
        """Extract keywords from title and concept.
        
        Args:
            title: Title text
            concept: Concept text
            
        Returns:
            List of keywords
        """
        # Simple keyword extraction
        # In production, would use NLP techniques
        text = f"{title} {concept}".lower()
        words = text.split()
        
        # Filter common words and extract unique keywords
        keywords = [w.strip(".,!?;:") for w in words if w not in STOP_WORDS and len(w) > 3]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                unique_keywords.append(kw)
                seen.add(kw)
        
        return unique_keywords[:10]  # Limit to 10 keywords
    
    def _extract_themes(self, title: str, concept: str) -> List[str]:
        """Extract themes from title and concept.
        
        Args:
            title: Title text
            concept: Concept text
            
        Returns:
            List of themes
        """
        # Simple theme extraction based on keywords
        # In production, would use more sophisticated analysis
        text = f"{title} {concept}".lower()
        
        theme_indicators = {
            "innovation": ["innovation", "new", "future", "technology"],
            "education": ["learn", "education", "understand", "knowledge"],
            "entertainment": ["story", "entertainment", "fun", "enjoy"],
            "analysis": ["analysis", "examine", "explore", "investigate"],
            "practical": ["practical", "application", "use", "implement"]
        }
        
        themes = []
        for theme, indicators in theme_indicators.items():
            if any(indicator in text for indicator in indicators):
                themes.append(theme)
        
        return themes[:5]  # Limit to 5 themes


__all__ = ["IdeaCreator", "CreationConfig"]
