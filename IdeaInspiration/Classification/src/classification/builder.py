"""Content builder helper module.

This module provides a builder pattern for constructing IdeaInspiration objects
step-by-step with validation and enrichment.

The Builder module focuses on:
    - Step-by-step construction of IdeaInspiration data
    - Validation of content fields
    - Enrichment with keywords and metadata
    - Flexible and chainable API
"""

from typing import List, Dict, Optional, Any
from .idea_inspiration import IdeaInspirationDict
from .extract import IdeaInspirationExtractor

# Import IdeaInspiration from Model
import sys
from pathlib import Path
_model_path = Path(__file__).parent.parent.parent.parent / 'Model'
if str(_model_path) not in sys.path:
    sys.path.insert(0, str(_model_path))

from idea_inspiration import IdeaInspiration, ContentType


class IdeaInspirationBuilder:
    """Builder for constructing IdeaInspiration objects.
    
    This class provides a fluent interface for building IdeaInspiration objects
    with validation and optional enrichment.
    
    Example:
        builder = IdeaInspirationBuilder()
        inspiration = (builder
            .set_title("My Story")
            .set_description("A tale about...")
            .set_content("Once upon a time...")
            .add_keyword("story")
            .add_keyword("narrative")
            .set_source_type("text")
            .build())
    """
    
    def __init__(self):
        """Initialize the builder with empty values."""
        self._title: str = ""
        self._description: str = ""
        self._content: str = ""
        self._keywords: List[str] = []
        self._source_type: str = "text"
        self._metadata: Dict[str, Any] = {}
        self._extractor = IdeaInspirationExtractor()
    
    def set_title(self, title: str) -> 'IdeaInspirationBuilder':
        """Set the title.
        
        Args:
            title: Title text
            
        Returns:
            Self for chaining
        """
        self._title = title.strip() if title else ""
        return self
    
    def set_description(self, description: str) -> 'IdeaInspirationBuilder':
        """Set the description.
        
        Args:
            description: Description text
            
        Returns:
            Self for chaining
        """
        self._description = description.strip() if description else ""
        return self
    
    def set_content(self, content: str) -> 'IdeaInspirationBuilder':
        """Set the main content text.
        
        Args:
            content: Content text (body, subtitles, transcription)
            
        Returns:
            Self for chaining
        """
        self._content = content.strip() if content else ""
        return self
    
    def set_keywords(self, keywords: List[str]) -> 'IdeaInspirationBuilder':
        """Set the keywords list (replaces existing).
        
        Args:
            keywords: List of keywords
            
        Returns:
            Self for chaining
        """
        self._keywords = [k.strip() for k in keywords if k.strip()]
        return self
    
    def add_keyword(self, keyword: str) -> 'IdeaInspirationBuilder':
        """Add a single keyword.
        
        Args:
            keyword: Keyword to add
            
        Returns:
            Self for chaining
        """
        keyword = keyword.strip()
        if keyword and keyword not in self._keywords:
            self._keywords.append(keyword)
        return self
    
    def add_keywords(self, keywords: List[str]) -> 'IdeaInspirationBuilder':
        """Add multiple keywords.
        
        Args:
            keywords: List of keywords to add
            
        Returns:
            Self for chaining
        """
        for keyword in keywords:
            self.add_keyword(keyword)
        return self
    
    def set_source_type(self, source_type: str) -> 'IdeaInspirationBuilder':
        """Set the source type.
        
        Args:
            source_type: Source type (text, video, audio)
            
        Returns:
            Self for chaining
        """
        self._source_type = source_type
        return self
    
    def set_metadata(self, metadata: Dict[str, Any]) -> 'IdeaInspirationBuilder':
        """Set metadata dictionary (replaces existing).
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            Self for chaining
        """
        self._metadata = metadata.copy() if metadata else {}
        return self
    
    def add_metadata(self, key: str, value: Any) -> 'IdeaInspirationBuilder':
        """Add a single metadata entry.
        
        Args:
            key: Metadata key
            value: Metadata value
            
        Returns:
            Self for chaining
        """
        self._metadata[key] = value
        return self
    

    def extract_keywords_from_content(
        self,
        max_keywords: int = 10,
        merge_with_existing: bool = True
    ) -> 'IdeaInspirationBuilder':
        """Extract keywords from title, description, and content.
        
        Args:
            max_keywords: Maximum number of keywords to extract
            merge_with_existing: If True, merge with existing keywords
            
        Returns:
            Self for chaining
        """
        # Combine all text for keyword extraction
        all_text = f"{self._title} {self._description} {self._content}"
        
        # Extract keywords
        extracted = self._extractor.extract_keywords_from_text(
            all_text,
            max_keywords=max_keywords
        )
        
        if merge_with_existing:
            # Add extracted keywords to existing ones (avoid duplicates)
            for keyword in extracted:
                if keyword not in self._keywords:
                    self._keywords.append(keyword)
        else:
            # Replace existing keywords
            self._keywords = extracted
        
        return self
    
    def from_metadata_dict(self, metadata: Dict[str, Any]) -> 'IdeaInspirationBuilder':
        """Populate builder from a metadata dictionary.
        
        Args:
            metadata: Dictionary with content fields
            
        Returns:
            Self for chaining
        """
        if 'title' in metadata:
            self.set_title(metadata['title'])
        
        if 'description' in metadata:
            self.set_description(metadata['description'])
        
        # Handle different content field names
        content = (
            metadata.get('content') or
            metadata.get('body') or
            metadata.get('subtitle_text') or
            metadata.get('transcription') or
            ""
        )
        if content:
            self.set_content(content)
        
        if 'tags' in metadata:
            self.add_keywords(metadata['tags'])
        
        if 'keywords' in metadata:
            self.add_keywords(metadata['keywords'])
        
        # Detect source type
        if 'subtitle_text' in metadata:
            self.set_source_type('video')
        elif 'transcription' in metadata:
            self.set_source_type('audio')
        elif 'source_type' in metadata:
            self.set_source_type(metadata['source_type'])
        
        return self
    
    def validate(self) -> bool:
        """Validate that required fields are set.
        
        Returns:
            True if valid, False otherwise
        """
        # At minimum, we need a title or some content
        return bool(self._title or self._content or self._description)
    
    def build(self) -> IdeaInspiration:
        """Build and return an IdeaInspiration object.
        
        Returns:
            IdeaInspiration object with the configured fields
            
        Raises:
            ValueError: If validation fails
        """
        if not self.validate():
            raise ValueError(
                "Cannot build IdeaInspiration: must have at least a title, "
                "description, or content"
            )
        
        # Convert source_type string to ContentType enum
        try:
            content_type = ContentType(self._source_type)
        except ValueError:
            content_type = ContentType.UNKNOWN
        
        # Convert metadata values to strings for compatibility
        str_metadata = {str(k): str(v) for k, v in self._metadata.items()}
        
        return IdeaInspiration(
            title=self._title,
            description=self._description,
            content=self._content,
            keywords=self._keywords.copy(),
            source_type=content_type,
            metadata=str_metadata
        )
    
    def reset(self) -> 'IdeaInspirationBuilder':
        """Reset the builder to empty state.
        
        Returns:
            Self for chaining
        """
        self._title = ""
        self._description = ""
        self._content = ""
        self._keywords = []
        self._source_type = "text"
        self._metadata = {}
        return self
