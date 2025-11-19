"""Protocol and helpers for working with IdeaInspiration model.

Note: The IdeaInspiration model is defined in the parent PrismQ.IdeaInspiration package.
This module provides protocols and type hints for working with that external model
in the context of classification.

This classification module enriches IdeaInspiration objects with:
    - Category classification (primary category)
    - Story detection flags
    - Confidence scores
    - Classification tags/flags
"""

from typing import Protocol, List, Dict, Any, Optional, Union
from typing_extensions import TypedDict


class IdeaInspirationProtocol(Protocol):
    """Protocol defining the expected interface of IdeaInspiration model.
    
    The actual IdeaInspiration model is defined elsewhere. This protocol
    documents the interface that classification functions expect.
    """
    
    title: str
    description: str
    content: str  # Could be body text, subtitles, or transcription
    keywords: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        ...


class IdeaInspirationDict(TypedDict, total=False):
    """TypedDict for IdeaInspiration as dictionary.
    
    Used when working with IdeaInspiration in dictionary form.
    """
    title: str
    description: str
    content: str
    keywords: List[str]
    source_type: str
    metadata: Dict[str, Any]


# Type alias for accepting either protocol or dict
IdeaInspirationLike = Union[IdeaInspirationProtocol, Dict[str, Any]]


def get_text_fields(inspiration: IdeaInspirationLike) -> Dict[str, str]:
    """Extract text fields from IdeaInspiration object or dict.
    
    Args:
        inspiration: IdeaInspiration object or dictionary
        
    Returns:
        Dictionary with title, description, content, and keywords as string
    """
    if isinstance(inspiration, dict):
        return {
            'title': inspiration.get('title', ''),
            'description': inspiration.get('description', ''),
            'content': inspiration.get('content', ''),
            'keywords_str': ' '.join(inspiration.get('keywords', []))
        }
    else:
        # Object with attributes
        return {
            'title': getattr(inspiration, 'title', ''),
            'description': getattr(inspiration, 'description', ''),
            'content': getattr(inspiration, 'content', ''),
            'keywords_str': ' '.join(getattr(inspiration, 'keywords', []))
        }


def get_keywords(inspiration: IdeaInspirationLike) -> List[str]:
    """Extract keywords from IdeaInspiration object or dict.
    
    Args:
        inspiration: IdeaInspiration object or dictionary
        
    Returns:
        List of keywords
    """
    if isinstance(inspiration, dict):
        return inspiration.get('keywords', [])
    else:
        return getattr(inspiration, 'keywords', [])
