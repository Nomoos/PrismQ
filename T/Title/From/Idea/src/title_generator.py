"""Title Generation module for creating title variants from Ideas.

⚠️  DEPRECATED: This template-based title generation is deprecated.
⚠️  Use ai_title_generator.AITitleGenerator instead.
⚠️  
⚠️  The ONLY approved way to generate titles is through AI with the
⚠️  literary-focused prompt in ai_title_generator module.

This module provides functionality to generate 3-10 compelling title variants
from an Idea object, focusing on engagement, clarity, and SEO optimization.
Default is 10 variants using diverse generation strategies.

This module is kept for backward compatibility only and should not be used
for new code. It will be removed in a future version.
"""

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

# Add parent directories to path for imports
# Navigate up to T/ directory and then to Idea/Model
current_file = Path(__file__)
t_module_dir = current_file.parent.parent.parent.parent.parent
model_path = t_module_dir / "Idea" / "Model"
sys.path.insert(0, str(model_path / "src"))
sys.path.insert(0, str(model_path))

from idea import ContentGenre, Idea


@dataclass
class TitleConfig:
    """Configuration for title generation.

    Attributes:
        num_variants: Number of title variants to generate (3-10)
        min_length: Minimum title length in characters
        max_length: Maximum title length in characters
        focus: Primary focus for title generation
        include_keywords: Whether to emphasize keywords from idea
    """

    num_variants: int = 10
    min_length: int = 20
    max_length: int = 100
    focus: Literal["engagement", "seo", "clarity", "balanced"] = "balanced"
    include_keywords: bool = True


# Import TitleVariant from the new modular structure using relative import
from .title_variant import TitleVariant


class TitleGenerator:
    """Generate compelling title variants from Ideas.

    This class creates multiple title options based on an Idea's content,
    optimizing for engagement, clarity, and SEO value.
    """

    def __init__(self, config: Optional[TitleConfig] = None):
        """Initialize TitleGenerator with configuration.

        Args:
            config: Optional title generation configuration
        """
        self.config = config or TitleConfig()

    def generate_from_idea(
        self, idea: Idea, num_variants: Optional[int] = None
    ) -> List[TitleVariant]:
        """Generate title variants from an Idea.

        Args:
            idea: Idea object to generate titles from
            num_variants: Optional override for number of variants (3-10)

        Returns:
            List of TitleVariant instances

        Raises:
            ValueError: If idea is invalid or num_variants out of range
        """
        if not idea:
            raise ValueError("Idea cannot be None")
        if not idea.title and not idea.concept:
            raise ValueError("Idea must have at least a title or concept")

        # Determine number of variants
        n_variants = num_variants if num_variants is not None else self.config.num_variants
        if n_variants < 3 or n_variants > 10:
            raise ValueError("num_variants must be between 3 and 10")

        # Extract key information from idea
        base_title = idea.title or self._extract_title_from_concept(idea.concept)
        keywords = self._extract_keywords(idea)

        # Generate variants using different strategies
        variants = []

        # Strategy 1: Direct - Use the original or cleaned title
        if len(variants) < n_variants:
            variants.append(self._generate_direct_variant(base_title, keywords, idea))

        # Strategy 2: Question-based - Turn into a question
        if len(variants) < n_variants:
            variants.append(self._generate_question_variant(base_title, keywords, idea))

        # Strategy 3: How-to - Action-oriented
        if len(variants) < n_variants:
            variants.append(self._generate_howto_variant(base_title, keywords, idea))

        # Strategy 4: Curiosity - Intrigue-focused
        if len(variants) < n_variants:
            variants.append(self._generate_curiosity_variant(base_title, keywords, idea))

        # Strategy 5: Authoritative - Expert perspective
        if len(variants) < n_variants:
            variants.append(self._generate_authoritative_variant(base_title, keywords, idea))

        # Strategy 6: Listicle - Number-based
        if len(variants) < n_variants:
            variants.append(self._generate_listicle_variant(base_title, keywords, idea))

        # Strategy 7: Problem-Solution - Address pain points
        if len(variants) < n_variants:
            variants.append(self._generate_problem_solution_variant(base_title, keywords, idea))

        # Strategy 8: Comparison - Versus style
        if len(variants) < n_variants:
            variants.append(self._generate_comparison_variant(base_title, keywords, idea))

        # Strategy 9: Ultimate Guide - Comprehensive resource
        if len(variants) < n_variants:
            variants.append(self._generate_ultimate_guide_variant(base_title, keywords, idea))

        # Strategy 10: Benefit-focused - Value proposition
        if len(variants) < n_variants:
            variants.append(self._generate_benefit_variant(base_title, keywords, idea))

        return variants[:n_variants]

    def _extract_title_from_concept(self, concept: str) -> str:
        """Extract a title from concept text.

        Args:
            concept: Concept text

        Returns:
            Extracted title
        """
        # Take first sentence or up to max length
        sentences = concept.split(".")
        title = sentences[0].strip()

        if len(title) > self.config.max_length:
            title = title[: self.config.max_length - 3] + "..."

        return title

    def _extract_keywords(self, idea: Idea) -> List[str]:
        """Extract key words from idea for title generation.

        Args:
            idea: Idea object

        Returns:
            List of keywords
        """
        keywords = []

        # Use existing keywords if available
        if hasattr(idea, "keywords") and idea.keywords:
            keywords.extend(idea.keywords[:3])  # Top 3 keywords

        # Extract from themes
        if hasattr(idea, "themes") and idea.themes:
            keywords.extend(idea.themes[:2])  # Top 2 themes

        # Extract from title
        if idea.title:
            # Simple keyword extraction (remove common words)
            words = idea.title.split()
            stop_words = {
                "the",
                "a",
                "an",
                "and",
                "or",
                "but",
                "in",
                "on",
                "at",
                "to",
                "for",
                "of",
                "with",
            }
            for word in words:
                clean_word = word.strip(".,!?:;").lower()
                if clean_word not in stop_words and len(clean_word) > 3:
                    keywords.append(clean_word)

        # Return unique keywords, limited to top 5
        return list(dict.fromkeys(keywords))[:5]

    def _generate_direct_variant(
        self, base_title: str, keywords: List[str], idea: Idea
    ) -> TitleVariant:
        """Generate direct/straightforward variant.

        Args:
            base_title: Base title to work from
            keywords: Extracted keywords
            idea: Original idea

        Returns:
            TitleVariant
        """
        title = self._ensure_length(base_title)

        return TitleVariant(
            text=title, style="direct", length=len(title), keywords=keywords, score=0.85
        )

    def _generate_question_variant(
        self, base_title: str, keywords: List[str], idea: Idea
    ) -> TitleVariant:
        """Generate question-based variant.

        Args:
            base_title: Base title to work from
            keywords: Extracted keywords
            idea: Original idea

        Returns:
            TitleVariant
        """
        # Transform to question format
        question_starters = [
            f"What is {base_title}?",
            f"How Does {base_title} Work?",
            f"Why {base_title} Matters?",
            f"What You Need to Know About {base_title}",
        ]

        # Choose based on title characteristics
        if "future" in base_title.lower() or "trend" in base_title.lower():
            title = f"What's the Future of {base_title}?"
        elif "how" in base_title.lower():
            title = base_title if base_title.endswith("?") else base_title + "?"
        else:
            title = question_starters[0]

        title = self._ensure_length(title)

        return TitleVariant(
            text=title, style="question", length=len(title), keywords=keywords, score=0.82
        )

    def _generate_howto_variant(
        self, base_title: str, keywords: List[str], idea: Idea
    ) -> TitleVariant:
        """Generate how-to/action-oriented variant.

        Args:
            base_title: Base title to work from
            keywords: Extracted keywords
            idea: Original idea

        Returns:
            TitleVariant
        """
        # Create actionable title
        if base_title.lower().startswith("how to"):
            title = base_title
        elif base_title.lower().startswith("the"):
            # Remove "The " prefix and add "How to Understand"
            the_prefix = "The "
            clean = (
                base_title[len(the_prefix) :] if base_title.startswith(the_prefix) else base_title
            )
            title = f"How to Understand {clean}"
        else:
            title = f"How to Master {base_title}"

        title = self._ensure_length(title)

        return TitleVariant(
            text=title, style="how-to", length=len(title), keywords=keywords, score=0.88
        )

    def _generate_curiosity_variant(
        self, base_title: str, keywords: List[str], idea: Idea
    ) -> TitleVariant:
        """Generate curiosity/intrigue-focused variant.

        Args:
            base_title: Base title to work from
            keywords: Extracted keywords
            idea: Original idea

        Returns:
            TitleVariant
        """
        # Create intriguing title
        curiosity_templates = [
            f"The Hidden Truth About {base_title}",
            f"{base_title}: What Nobody Tells You",
            f"The Untold Story of {base_title}",
            f"Discover the Secrets of {base_title}",
        ]

        # Choose template based on content
        if hasattr(idea, "genre"):
            if idea.genre == ContentGenre.EDUCATIONAL:
                title = f"The Complete Guide to {base_title}"
            elif idea.genre == ContentGenre.ENTERTAINMENT:
                title = f"The Fascinating World of {base_title}"
            else:
                title = curiosity_templates[0]
        else:
            title = curiosity_templates[0]

        title = self._ensure_length(title)

        return TitleVariant(
            text=title, style="curiosity", length=len(title), keywords=keywords, score=0.80
        )

    def _generate_authoritative_variant(
        self, base_title: str, keywords: List[str], idea: Idea
    ) -> TitleVariant:
        """Generate authoritative/expert variant.

        Args:
            base_title: Base title to work from
            keywords: Extracted keywords
            idea: Original idea

        Returns:
            TitleVariant
        """
        # Create authoritative title
        authority_templates = [
            f"{base_title}: A Comprehensive Analysis",
            f"Understanding {base_title}: Expert Insights",
            f"{base_title} Explained: A Deep Dive",
            f"The Essential Guide to {base_title}",
        ]

        # Select based on idea characteristics
        if "analysis" in base_title.lower() or "research" in base_title.lower():
            title = base_title
        else:
            title = authority_templates[0]

        title = self._ensure_length(title)

        return TitleVariant(
            text=title, style="authoritative", length=len(title), keywords=keywords, score=0.83
        )

    def _generate_listicle_variant(
        self, base_title: str, keywords: List[str], idea: Idea
    ) -> TitleVariant:
        """Generate listicle/numbered variant.

        Args:
            base_title: Base title to work from
            keywords: Extracted keywords
            idea: Original idea

        Returns:
            TitleVariant
        """
        # Create numbered list title
        numbers = ["5", "7", "10", "15"]
        number = numbers[len(base_title) % len(numbers)]

        listicle_templates = [
            f"{number} Essential Things About {base_title}",
            f"{number} Ways to Understand {base_title}",
            f"{number} Key Insights on {base_title}",
            f"Top {number} Facts About {base_title}",
        ]

        title = listicle_templates[0]
        title = self._ensure_length(title)

        return TitleVariant(
            text=title, style="listicle", length=len(title), keywords=keywords, score=0.86
        )

    def _generate_problem_solution_variant(
        self, base_title: str, keywords: List[str], idea: Idea
    ) -> TitleVariant:
        """Generate problem-solution variant.

        Args:
            base_title: Base title to work from
            keywords: Extracted keywords
            idea: Original idea

        Returns:
            TitleVariant
        """
        # Create problem-solving title
        problem_templates = [
            f"Solving {base_title} Challenges",
            f"Overcoming {base_title} Issues",
            f"{base_title}: Problems and Solutions",
            f"Fixing Common {base_title} Problems",
        ]

        title = problem_templates[0]
        title = self._ensure_length(title)

        return TitleVariant(
            text=title, style="problem-solution", length=len(title), keywords=keywords, score=0.84
        )

    def _generate_comparison_variant(
        self, base_title: str, keywords: List[str], idea: Idea
    ) -> TitleVariant:
        """Generate comparison/versus variant.

        Args:
            base_title: Base title to work from
            keywords: Extracted keywords
            idea: Original idea

        Returns:
            TitleVariant
        """
        # Create comparison title
        comparison_templates = [
            f"{base_title}: Then vs Now",
            f"Comparing {base_title} Approaches",
            f"{base_title}: Myths vs Reality",
            f"Old vs New: {base_title}",
        ]

        title = comparison_templates[0]
        title = self._ensure_length(title)

        return TitleVariant(
            text=title, style="comparison", length=len(title), keywords=keywords, score=0.81
        )

    def _generate_ultimate_guide_variant(
        self, base_title: str, keywords: List[str], idea: Idea
    ) -> TitleVariant:
        """Generate ultimate guide variant.

        Args:
            base_title: Base title to work from
            keywords: Extracted keywords
            idea: Original idea

        Returns:
            TitleVariant
        """
        # Create comprehensive guide title
        guide_templates = [
            f"The Ultimate Guide to {base_title}",
            f"{base_title}: The Complete Resource",
            f"Everything You Need About {base_title}",
            f"Mastering {base_title}: A Complete Guide",
        ]

        title = guide_templates[0]
        title = self._ensure_length(title)

        return TitleVariant(
            text=title, style="ultimate-guide", length=len(title), keywords=keywords, score=0.87
        )

    def _generate_benefit_variant(
        self, base_title: str, keywords: List[str], idea: Idea
    ) -> TitleVariant:
        """Generate benefit-focused variant.

        Args:
            base_title: Base title to work from
            keywords: Extracted keywords
            idea: Original idea

        Returns:
            TitleVariant
        """
        # Create benefit-driven title
        benefit_templates = [
            f"Why {base_title} Matters to You",
            f"The Benefits of Understanding {base_title}",
            f"How {base_title} Can Transform Your Life",
            f"{base_title}: Unlock Your Potential",
        ]

        title = benefit_templates[0]
        title = self._ensure_length(title)

        return TitleVariant(
            text=title, style="benefit", length=len(title), keywords=keywords, score=0.85
        )

    def _ensure_length(self, title: str) -> str:
        """Ensure title is within configured length bounds.

        Args:
            title: Title to check

        Returns:
            Title adjusted to length constraints
        """
        if len(title) > self.config.max_length:
            # Truncate and add ellipsis
            return title[: self.config.max_length - 3] + "..."
        elif len(title) < self.config.min_length:
            # Title too short - this is acceptable as we prioritize quality
            return title

        return title


def generate_titles_from_idea(
    idea: Idea, num_variants: int = 10, config: Optional[TitleConfig] = None
) -> List[TitleVariant]:
    """Convenience function to generate titles from an idea.

    Args:
        idea: Idea object to generate titles from
        num_variants: Number of variants to generate (3-10, default 10)
        config: Optional configuration

    Returns:
        List of TitleVariant instances
    """
    generator = TitleGenerator(config)
    return generator.generate_from_idea(idea, num_variants)
