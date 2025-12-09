"""Title variant data model.

This module defines the data structure for representing generated title variants.
Follows Single Responsibility Principle - only responsible for data representation.
"""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class TitleVariant:
    """Represents a single generated title variant.
    
    Attributes:
        text: The title text
        style: Style/approach of this variant (e.g., 'direct', 'question')
        length: Character length of the title
        keywords: Extracted or identified keywords
        score: Quality score (0.0-1.0)
    """
    
    text: str
    style: str
    length: int
    keywords: List[str]
    score: float = 0.8
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.
        
        Returns:
            Dictionary with all variant attributes
        """
        return {
            "text": self.text,
            "style": self.style,
            "length": self.length,
            "keywords": self.keywords,
            "score": self.score,
        }
