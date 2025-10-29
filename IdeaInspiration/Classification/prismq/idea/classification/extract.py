"""Content extraction helper module.

This module provides helper functions to extract and normalize content from various
sources (text, video metadata with subtitles, audio metadata with transcriptions)
into dictionary format compatible with IdeaInspiration.

Note: IdeaInspiration model is defined externally. This module returns dictionaries
that can be used to populate external IdeaInspiration objects.

The Extract module focuses on:
    - Parsing raw content from different formats
    - Extracting titles, descriptions, and text content
    - Normalizing data into dictionary format
    - Basic keyword extraction from content
"""

from typing import Dict, List, Optional, Any
import re
from .idea_inspiration import IdeaInspirationDict


class IdeaInspirationExtractor:
    """Helper for extracting and normalizing content into dictionary format.
    
    This class handles extraction from different content types and returns
    dictionaries compatible with external IdeaInspiration model:
    - Text content (articles, posts, etc.)
    - Video content (with subtitles/captions)
    - Audio content (with transcriptions)
    """
    
    def __init__(self):
        """Initialize the extractor."""
        pass
    
    def extract_from_text(
        self,
        title: str,
        description: str = "",
        body: str = "",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> IdeaInspirationDict:
        """Extract content from text and return as dictionary.
        
        Args:
            title: Title of the text content
            description: Description or summary
            body: Full body text
            tags: List of tags/keywords
            metadata: Additional metadata
            
        Returns:
            Dictionary compatible with IdeaInspiration model
        """
        tags = tags or []
        metadata = metadata or {}
        
        # Extract keywords from tags and content
        keywords = self._extract_keywords_from_tags(tags)
        
        return {
            'title': title,
            'description': description,
            'content': body,
            'keywords': keywords,
            'source_type': 'text',
            'metadata': metadata
        }
    
    def extract_from_video(
        self,
        title: str,
        description: str = "",
        subtitle_text: str = "",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> IdeaInspirationDict:
        """Extract IdeaInspiration from video content with subtitles.
        
        Args:
            title: Title of the video
            description: Video description
            subtitle_text: Subtitle/caption text from video
            tags: List of tags/keywords
            metadata: Additional metadata (duration, platform, etc.)
            
        Returns:
            IdeaInspiration object with extracted content
        """
        tags = tags or []
        metadata = metadata or {}
        
        # Use subtitle_text as the main content for videos
        keywords = self._extract_keywords_from_tags(tags)
        
        return {
            'title': title,
            'description': description,
            'content': subtitle_text,
            'keywords': keywords,
            'source_type': 'video',
            'metadata': metadata
        }
    
    def extract_from_audio(
        self,
        title: str,
        description: str = "",
        transcription: str = "",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> IdeaInspirationDict:
        """Extract IdeaInspiration from audio content with transcription.
        
        Args:
            title: Title of the audio content
            description: Audio description
            transcription: Transcribed text from audio
            tags: List of tags/keywords
            metadata: Additional metadata (duration, podcast info, etc.)
            
        Returns:
            IdeaInspiration object with extracted content
        """
        tags = tags or []
        metadata = metadata or {}
        
        # Use transcription as the main content for audio
        keywords = self._extract_keywords_from_tags(tags)
        
        return {
            'title': title,
            'description': description,
            'content': transcription,
            'keywords': keywords,
            'source_type': 'audio',
            'metadata': metadata
        }
    
    def extract_from_metadata(self, metadata: Dict[str, Any]) -> IdeaInspirationDict:
        """Extract IdeaInspiration from a metadata dictionary.
        
        This method auto-detects the content type and extracts accordingly.
        
        Args:
            metadata: Dictionary with content fields
            
        Returns:
            IdeaInspiration object with extracted content
        """
        title = metadata.get('title', '')
        description = metadata.get('description', '')
        tags = metadata.get('tags', [])
        
        # Detect content type and extract accordingly
        if 'subtitle_text' in metadata:
            return self.extract_from_video(
                title=title,
                description=description,
                subtitle_text=metadata.get('subtitle_text', ''),
                tags=tags,
                metadata=metadata
            )
        elif 'transcription' in metadata:
            return self.extract_from_audio(
                title=title,
                description=description,
                transcription=metadata.get('transcription', ''),
                tags=tags,
                metadata=metadata
            )
        else:
            # Default to text extraction
            body = metadata.get('body', metadata.get('content', ''))
            return self.extract_from_text(
                title=title,
                description=description,
                body=body,
                tags=tags,
                metadata=metadata
            )
    
    def _extract_keywords_from_tags(self, tags: List[str]) -> List[str]:
        """Extract and clean keywords from tags.
        
        Args:
            tags: List of raw tags
            
        Returns:
            List of cleaned keyword strings
        """
        keywords = []
        for tag in tags:
            # Remove hashtags, clean whitespace
            cleaned = tag.strip().lstrip('#').lower()
            if cleaned and len(cleaned) > 1:
                keywords.append(cleaned)
        return keywords
    
    def extract_keywords_from_text(
        self,
        text: str,
        max_keywords: int = 10,
        min_length: int = 3
    ) -> List[str]:
        """Extract keywords from text using simple heuristics.
        
        This is a basic keyword extraction using word frequency and filtering.
        For more advanced extraction, consider integrating NLP libraries.
        
        Args:
            text: Text to extract keywords from
            max_keywords: Maximum number of keywords to return
            min_length: Minimum length of keywords
            
        Returns:
            List of extracted keywords
        """
        if not text:
            return []
        
        # Convert to lowercase and split into words
        words = re.findall(r'\b[a-z]+\b', text.lower())
        
        # Common stop words to filter out
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your',
            'his', 'her', 'its', 'our', 'their'
        }
        
        # Filter and count words
        word_freq = {}
        for word in words:
            if len(word) >= min_length and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_keywords]]
