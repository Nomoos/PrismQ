"""Base formatter for social media platforms.

This module provides common utilities and base classes for all social media formatters.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class SocialMediaMetadata:
    """Metadata for social media content.
    
    Attributes:
        platform: Target platform (twitter, linkedin, instagram, facebook)
        character_count: Total character count
        word_count: Total word count
        estimated_engagement_score: Estimated engagement (0-100)
        suggested_posting_time: Suggested posting time
        hashtags: List of hashtags
        variant_count: Number of variants generated
    """
    platform: str = ""
    character_count: int = 0
    word_count: int = 0
    estimated_engagement_score: int = 50
    suggested_posting_time: str = "9:00 AM - 12:00 PM"
    hashtags: List[str] = field(default_factory=list)
    variant_count: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)


@dataclass
class SocialMediaContent:
    """Result of social media formatting operation.
    
    Attributes:
        content_id: Identifier of the formatted content
        platform: Target platform
        formatted_content: Platform-formatted content
        metadata: Social media metadata
        variant_id: Variant identifier for A/B testing
        timestamp: When formatting was performed
        success: Whether formatting succeeded
        errors: List of any errors encountered
    """
    content_id: str
    platform: str
    formatted_content: str
    metadata: SocialMediaMetadata
    variant_id: int = 1
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    success: bool = True
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        data = asdict(self)
        data['metadata'] = self.metadata.to_dict()
        return data


class BaseSocialFormatter:
    """Base class for social media formatters.
    
    Provides common utilities used across all platform formatters.
    """
    
    def __init__(self):
        """Initialize base social formatter."""
        pass
    
    def _extract_key_points(self, script: str, max_points: int = 3) -> List[str]:
        """Extract key points from script.
        
        Args:
            script: Script content
            max_points: Maximum number of key points to extract
        
        Returns:
            List of key points
        """
        # Split into sentences
        sentences = self._split_into_sentences(script)
        
        # Simple heuristic: take sentences with action words or strong statements
        # In a more sophisticated implementation, use NLP for key phrase extraction
        key_sentences = []
        for sentence in sentences:
            # Look for sentences with numbers, percentages, or strong verbs
            if (re.search(r'\d+%|\d+x|result|impact|improve|transform|achieve', sentence.lower()) 
                and len(sentence.split()) > 5):
                key_sentences.append(sentence.strip())
        
        # If we don't have enough, just take the first few sentences
        if len(key_sentences) < max_points:
            key_sentences = sentences[:max_points]
        
        return key_sentences[:max_points]
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences.
        
        Args:
            text: Text to split
        
        Returns:
            List of sentences
        """
        # Simple sentence splitter
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _generate_hook(self, script: str, hook_type: str = "question") -> str:
        """Generate an engaging hook from script content.
        
        Args:
            script: Script content
            hook_type: Type of hook (question, statement, stat)
        
        Returns:
            Hook text
        """
        sentences = self._split_into_sentences(script)
        
        if not sentences:
            return "Here's an interesting insight:"
        
        first_sentence = sentences[0]
        
        if hook_type == "question":
            # Convert first statement to a question if possible
            if "?" in first_sentence:
                return first_sentence
            return f"Have you thought about this? {first_sentence}"
        elif hook_type == "statement":
            # Use first sentence as bold statement
            return first_sentence
        elif hook_type == "stat":
            # Look for numbers in first few sentences
            for sentence in sentences[:3]:
                if re.search(r'\d+', sentence):
                    return sentence
            return first_sentence
        
        return first_sentence
    
    def _extract_main_message(self, script: str, max_length: int = 500) -> str:
        """Extract main message from script.
        
        Args:
            script: Script content
            max_length: Maximum length of message
        
        Returns:
            Main message text
        """
        # Clean up the script
        text = script.strip()
        
        # If script is short enough, return it
        if len(text) <= max_length:
            return text
        
        # Otherwise, take first portion
        sentences = self._split_into_sentences(text)
        
        message = ""
        for sentence in sentences:
            if len(message) + len(sentence) + 1 <= max_length:
                message += sentence + " "
            else:
                break
        
        return message.strip()
    
    def _extract_hashtags(
        self, 
        script: str, 
        min_hashtags: int = 3, 
        max_hashtags: int = 5
    ) -> List[str]:
        """Extract relevant hashtags from script.
        
        Args:
            script: Script content
            min_hashtags: Minimum number of hashtags
            max_hashtags: Maximum number of hashtags
        
        Returns:
            List of hashtags (without # prefix)
        """
        # Simple keyword extraction
        # In production, use NLP or keyword extraction libraries
        
        # Common action/topic words that make good hashtags
        text_lower = script.lower()
        
        potential_tags = []
        
        # Look for common business/content keywords
        keywords = [
            'innovation', 'leadership', 'strategy', 'growth', 'success',
            'business', 'marketing', 'content', 'social', 'digital',
            'entrepreneur', 'startup', 'technology', 'productivity',
            'mindset', 'tips', 'advice', 'howto', 'guide', 'tutorial'
        ]
        
        for keyword in keywords:
            if keyword in text_lower:
                # Capitalize properly for hashtag
                potential_tags.append(keyword.capitalize())
        
        # Ensure we have minimum hashtags
        if len(potential_tags) < min_hashtags:
            # Add generic hashtags
            generic = ['ContentCreation', 'Business', 'Strategy', 'Growth', 'Tips']
            potential_tags.extend(generic[:min_hashtags - len(potential_tags)])
        
        # Return limited set
        return potential_tags[:max_hashtags]
    
    def _truncate_to_limit(
        self, 
        text: str, 
        char_limit: int, 
        suffix: str = "..."
    ) -> str:
        """Truncate text to character limit.
        
        Args:
            text: Text to truncate
            char_limit: Character limit
            suffix: Suffix to add if truncated
        
        Returns:
            Truncated text
        """
        if len(text) <= char_limit:
            return text
        
        # Account for suffix
        limit = char_limit - len(suffix)
        
        # Try to truncate at sentence boundary
        truncated = text[:limit]
        
        # Find last sentence ending
        last_period = max(
            truncated.rfind('.'),
            truncated.rfind('!'),
            truncated.rfind('?')
        )
        
        if last_period > limit * 0.7:  # If we can keep at least 70% of content
            return truncated[:last_period + 1]
        
        # Otherwise, truncate at word boundary
        last_space = truncated.rfind(' ')
        if last_space > 0:
            return truncated[:last_space] + suffix
        
        return truncated + suffix
    
    def _count_characters(self, text: str, count_spaces: bool = True) -> int:
        """Count characters in text.
        
        Args:
            text: Text to count
            count_spaces: Whether to count spaces
        
        Returns:
            Character count
        """
        if count_spaces:
            return len(text)
        return len(text.replace(' ', ''))
    
    def _validate_character_limit(
        self, 
        text: str, 
        limit: int, 
        platform: str
    ) -> bool:
        """Validate text against platform character limit.
        
        Args:
            text: Text to validate
            limit: Character limit
            platform: Platform name for error messages
        
        Returns:
            True if within limit, False otherwise
        """
        char_count = self._count_characters(text)
        return char_count <= limit
