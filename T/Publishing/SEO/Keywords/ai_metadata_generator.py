"""AI-Powered SEO Metadata Generator using LLMs via Ollama.

This module provides prompt-engineered, GPT-based SEO metadata generation
as specified in POST-001. It uses local LLM models through Ollama API to
create high-quality, contextually-aware SEO metadata.

Workflow Position:
    Stage: SEO Optimization (POST-001)
    Input: Title + Script + Keywords → AI Generation → Output: Enhanced SEO metadata

Features:
    - GPT-based meta description generation
    - AI-enhanced title tag optimization
    - Context-aware keyword suggestions
    - Intelligent Open Graph metadata
    - Raises AIUnavailableError when AI is not available (no fallback)
"""

import json
import re
import requests
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .metadata_generator import SEOMetadata

logger = logging.getLogger(__name__)


class AIUnavailableError(Exception):
    """Exception raised when AI service (Ollama) is unavailable.
    
    This exception is raised instead of falling back to alternative methods,
    as per the requirement to not perform fallback when AI is unavailable.
    The caller should handle this exception and wait for AI to become available.
    """
    pass


@dataclass
class AIConfig:
    """Configuration for AI-powered metadata generation.
    
    Attributes:
        model: Name of the Ollama model to use (default: qwen3:30b)
        api_base: Base URL for Ollama API
        temperature: Sampling temperature (0.0-2.0, lower = more focused)
        max_tokens: Maximum tokens to generate
        timeout: Request timeout in seconds
        enable_ai: Whether to use AI generation (raises error if False or unavailable)
    """
    model: str = "qwen3:30b"  # Default local AI model - excellent balance of quality and speed
    api_base: str = "http://localhost:11434"
    temperature: float = 0.3  # Lower temp for more consistent SEO output
    max_tokens: int = 500
    timeout: int = 30
    enable_ai: bool = True


class AIMetadataGenerator:
    """Generate SEO metadata using AI-powered prompt engineering.
    
    This class uses carefully crafted prompts to generate high-quality
    SEO metadata that follows best practices and is optimized for
    search engines and social media platforms.
    """
    
    # Character limits from SEO best practices
    META_DESCRIPTION_MIN = 150
    META_DESCRIPTION_MAX = 160
    TITLE_TAG_MAX = 60
    OG_DESCRIPTION_MAX = 200
    
    def __init__(
        self,
        config: Optional[AIConfig] = None,
        brand_name: Optional[str] = None,
        include_brand: bool = True
    ):
        """Initialize the AI metadata generator.
        
        Args:
            config: Optional AI configuration
            brand_name: Optional brand name to append to titles
            include_brand: Whether to include brand name in title tags
        """
        self.config = config or AIConfig()
        self.brand_name = brand_name
        self.include_brand = include_brand
        self.available = self._check_ollama_availability()
    
    def _check_ollama_availability(self) -> bool:
        """Check if Ollama is available and running.
        
        Returns:
            True if Ollama is available, False otherwise
        """
        if not self.config.enable_ai:
            return False
            
        try:
            response = requests.get(
                f"{self.config.api_base}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama not available: {e}")
            return False
    
    def generate_meta_description(
        self,
        title: str,
        script: str,
        primary_keywords: List[str],
        target_length: int = 155
    ) -> str:
        """Generate SEO-optimized meta description using AI.
        
        Uses prompt engineering to create compelling, keyword-rich
        meta descriptions that follow SEO best practices.
        
        Args:
            title: Content title
            script: Content script/body
            primary_keywords: Primary keywords to include
            target_length: Target character count (default: 155)
        
        Returns:
            AI-generated meta description (150-160 characters)
            
        Raises:
            AIUnavailableError: If AI is unavailable or generation fails
        """
        if not self.available:
            error_msg = "AI meta description generation unavailable: Ollama not running"
            logger.error(error_msg)
            raise AIUnavailableError(error_msg)
        
        prompt = self._create_meta_description_prompt(
            title=title,
            script=script,
            keywords=primary_keywords,
            target_length=target_length
        )
        
        try:
            response = self._call_ollama(prompt)
            description = self._extract_meta_description(response)
            
            # Validate length and quality
            if self.META_DESCRIPTION_MIN <= len(description) <= self.META_DESCRIPTION_MAX:
                return description
            else:
                error_msg = f"AI meta description length invalid ({len(description)} chars)"
                logger.error(error_msg)
                raise AIUnavailableError(error_msg)
                
        except AIUnavailableError:
            raise
        except Exception as e:
            error_msg = f"AI meta description generation failed: {e}"
            logger.error(error_msg)
            raise AIUnavailableError(error_msg) from e
    
    def generate_title_tag(
        self,
        title: str,
        primary_keywords: List[str]
    ) -> str:
        """Generate SEO-optimized title tag using AI.
        
        Args:
            title: Original title
            primary_keywords: Primary keywords to incorporate
        
        Returns:
            AI-enhanced title tag (<60 characters)
            
        Raises:
            AIUnavailableError: If AI is unavailable or generation fails
        """
        if not self.available:
            error_msg = "AI title tag generation unavailable: Ollama not running"
            logger.error(error_msg)
            raise AIUnavailableError(error_msg)
        
        prompt = self._create_title_tag_prompt(
            title=title,
            keywords=primary_keywords,
            brand_name=self.brand_name if self.include_brand else None
        )
        
        try:
            response = self._call_ollama(prompt)
            title_tag = self._extract_title_tag(response)
            
            # Validate length
            if len(title_tag) <= self.TITLE_TAG_MAX:
                return title_tag
            else:
                error_msg = f"AI title tag too long ({len(title_tag)} chars)"
                logger.error(error_msg)
                raise AIUnavailableError(error_msg)
                
        except AIUnavailableError:
            raise
        except Exception as e:
            error_msg = f"AI title tag generation failed: {e}"
            logger.error(error_msg)
            raise AIUnavailableError(error_msg) from e
    
    def suggest_related_keywords(
        self,
        title: str,
        script: str,
        primary_keywords: List[str],
        max_suggestions: int = 10
    ) -> List[str]:
        """Generate related keyword suggestions using AI context understanding.
        
        Args:
            title: Content title
            script: Content script
            primary_keywords: Existing primary keywords
            max_suggestions: Maximum number of suggestions
        
        Returns:
            List of AI-suggested related keywords
            
        Raises:
            AIUnavailableError: If AI is unavailable or generation fails
        """
        if not self.available:
            error_msg = "AI related keywords generation unavailable: Ollama not running"
            logger.error(error_msg)
            raise AIUnavailableError(error_msg)
        
        prompt = self._create_related_keywords_prompt(
            title=title,
            script=script,
            keywords=primary_keywords,
            max_count=max_suggestions
        )
        
        try:
            response = self._call_ollama(prompt)
            keywords = self._extract_keywords_list(response)
            return keywords[:max_suggestions]
                
        except AIUnavailableError:
            raise
        except Exception as e:
            error_msg = f"AI related keywords generation failed: {e}"
            logger.error(error_msg)
            raise AIUnavailableError(error_msg) from e
    
    def generate_og_description(
        self,
        title: str,
        script: str,
        meta_description: str,
        primary_keywords: List[str]
    ) -> str:
        """Generate Open Graph description for social media using AI.
        
        Args:
            title: Content title
            script: Content script
            meta_description: Already generated meta description
            primary_keywords: Primary keywords
        
        Returns:
            AI-generated OG description (up to 200 characters)
            
        Raises:
            AIUnavailableError: If AI is unavailable or generation fails
        """
        if not self.available:
            error_msg = "AI OG description generation unavailable: Ollama not running"
            logger.error(error_msg)
            raise AIUnavailableError(error_msg)
        
        prompt = self._create_og_description_prompt(
            title=title,
            script=script,
            meta_description=meta_description,
            keywords=primary_keywords
        )
        
        try:
            response = self._call_ollama(prompt)
            og_desc = self._extract_og_description(response)
            
            # Validate length
            if len(og_desc) <= self.OG_DESCRIPTION_MAX:
                return og_desc
            else:
                return og_desc[:self.OG_DESCRIPTION_MAX].rsplit(' ', 1)[0] + "..."
                
        except AIUnavailableError:
            raise
        except Exception as e:
            error_msg = f"AI OG description generation failed: {e}"
            logger.error(error_msg)
            raise AIUnavailableError(error_msg) from e
    
    def _create_meta_description_prompt(
        self,
        title: str,
        script: str,
        keywords: List[str],
        target_length: int
    ) -> str:
        """Create prompt for meta description generation.
        
        This prompt uses advanced prompt engineering techniques:
        - Role definition (SEO expert)
        - Clear constraints (length, keywords)
        - Output formatting instructions
        - Best practice guidelines
        
        Args:
            title: Content title
            script: Content script
            keywords: Keywords to include
            target_length: Target character count
        
        Returns:
            Engineered prompt for AI
        """
        keywords_str = ", ".join(keywords[:5])  # Top 5 keywords
        
        # Truncate script for context (first 500 chars + last 200 chars)
        script_context = script[:500]
        if len(script) > 700:
            script_context += "..." + script[-200:]
        
        prompt = f"""You are an expert SEO specialist tasked with writing a compelling meta description.

**Content Title**: "{title}"

**Primary Keywords**: {keywords_str}

**Content Preview**:
{script_context}

**Task**: Write a meta description that:
1. Is EXACTLY between 150-160 characters (target: {target_length} characters)
2. Naturally incorporates at least ONE primary keyword
3. Compels users to click through from search results
4. Accurately summarizes the content
5. Uses active voice and includes a call-to-action when appropriate
6. Avoids keyword stuffing or unnatural phrasing

**SEO Best Practices**:
- Start with the most important information
- Include benefit-driven language
- Match search intent
- Be specific and concise
- Avoid generic descriptions

**Output Format**: 
Return ONLY the meta description text, nothing else. No quotes, no explanations.

Meta Description:"""
        
        return prompt
    
    def _create_title_tag_prompt(
        self,
        title: str,
        keywords: List[str],
        brand_name: Optional[str]
    ) -> str:
        """Create prompt for title tag optimization.
        
        Args:
            title: Original title
            keywords: Keywords to consider
            brand_name: Optional brand name
        
        Returns:
            Engineered prompt for AI
        """
        keywords_str = ", ".join(keywords[:3])  # Top 3 keywords
        brand_suffix = f" | {brand_name}" if brand_name else ""
        max_title_length = self.TITLE_TAG_MAX - len(brand_suffix)
        
        prompt = f"""You are an expert SEO specialist optimizing a title tag for search engines.

**Original Title**: "{title}"

**Target Keywords**: {keywords_str}

**Brand Name**: {brand_name if brand_name else "None"}

**Task**: Create an SEO-optimized title tag that:
1. Is MAXIMUM {max_title_length} characters (before brand suffix)
2. Incorporates at least ONE primary keyword naturally
3. Is compelling and click-worthy
4. Accurately represents the content
5. Front-loads important keywords when possible
6. Avoids keyword stuffing

**Output Format**:
Return ONLY the optimized title (without brand suffix), nothing else. No quotes, no explanations.

Optimized Title:"""
        
        return prompt
    
    def _create_related_keywords_prompt(
        self,
        title: str,
        script: str,
        keywords: List[str],
        max_count: int
    ) -> str:
        """Create prompt for related keyword suggestions.
        
        Args:
            title: Content title
            script: Content script (truncated)
            keywords: Existing keywords
            max_count: Maximum keywords to suggest
        
        Returns:
            Engineered prompt for AI
        """
        keywords_str = ", ".join(keywords[:5])
        script_preview = script[:400]
        
        prompt = f"""You are an SEO specialist suggesting related keywords for content optimization.

**Title**: "{title}"

**Current Keywords**: {keywords_str}

**Content Preview**:
{script_preview}...

**Task**: Suggest {max_count} related keywords or phrases that:
1. Are semantically related to the current keywords
2. Would improve SEO and topical relevance
3. Reflect user search intent
4. Are commonly searched terms in this topic area
5. Are NOT already in the current keyword list
6. Are specific and actionable (not too generic)

**Output Format**:
Return a JSON array of keyword strings, nothing else.
Example: ["keyword1", "keyword2", "keyword3"]

Related Keywords:"""
        
        return prompt
    
    def _create_og_description_prompt(
        self,
        title: str,
        script: str,
        meta_description: str,
        keywords: List[str]
    ) -> str:
        """Create prompt for Open Graph description.
        
        Args:
            title: Content title
            script: Content script
            meta_description: Existing meta description
            keywords: Primary keywords
        
        Returns:
            Engineered prompt for AI
        """
        keywords_str = ", ".join(keywords[:3])
        script_preview = script[:300]
        
        prompt = f"""You are a social media optimization specialist creating an Open Graph description.

**Title**: "{title}"

**SEO Meta Description**: "{meta_description}"

**Keywords**: {keywords_str}

**Content Preview**:
{script_preview}...

**Task**: Create an engaging Open Graph description for social media that:
1. Is MAXIMUM 200 characters
2. Is more engaging and conversational than the SEO meta description
3. Optimized for social sharing (Facebook, LinkedIn, Twitter)
4. Includes emotional hooks or curiosity gaps
5. Encourages social engagement and clicks
6. Can be slightly longer and more descriptive than the meta description

**Output Format**:
Return ONLY the OG description text, nothing else. No quotes, no explanations.

OG Description:"""
        
        return prompt
    
    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API to generate content.
        
        Args:
            prompt: Prompt to send to the model
        
        Returns:
            Generated text response
        
        Raises:
            RuntimeError: If API call fails
        """
        try:
            response = requests.post(
                f"{self.config.api_base}/api/generate",
                json={
                    "model": self.config.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.config.temperature,
                        "num_predict": self.config.max_tokens
                    }
                },
                timeout=self.config.timeout
            )
            
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API call failed: {e}")
            raise RuntimeError(f"Failed to generate AI metadata: {e}")
    
    def _extract_meta_description(self, response: str) -> str:
        """Extract meta description from AI response.
        
        Args:
            response: Raw AI response
        
        Returns:
            Cleaned meta description
        """
        # Remove common prefixes
        cleaned = response.strip()
        prefixes = ["Meta Description:", "Description:", "Output:"]
        for prefix in prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
        
        # Remove quotes if present
        cleaned = cleaned.strip('"\'')
        
        return cleaned
    
    def _extract_title_tag(self, response: str) -> str:
        """Extract title tag from AI response.
        
        Args:
            response: Raw AI response
        
        Returns:
            Cleaned title tag
        """
        cleaned = response.strip()
        prefixes = ["Optimized Title:", "Title:", "Title Tag:", "Output:"]
        for prefix in prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
        
        # Remove quotes if present
        cleaned = cleaned.strip('"\'')
        
        # Add brand suffix if configured
        if self.include_brand and self.brand_name:
            brand_suffix = f" | {self.brand_name}"
            if len(cleaned) + len(brand_suffix) <= self.TITLE_TAG_MAX:
                cleaned += brand_suffix
        
        return cleaned
    
    def _extract_keywords_list(self, response: str) -> List[str]:
        """Extract keyword list from AI response.
        
        Args:
            response: Raw AI response
        
        Returns:
            List of keywords
        """
        try:
            # Try to find JSON array in response
            start_idx = response.find('[')
            end_idx = response.rfind(']')
            
            if start_idx >= 0 and end_idx > start_idx:
                json_text = response[start_idx:end_idx + 1]
                keywords = json.loads(json_text)
                
                if isinstance(keywords, list):
                    # Clean and validate keywords
                    return [
                        str(kw).strip().lower()
                        for kw in keywords
                        if isinstance(kw, str) and len(kw.strip()) > 0
                    ]
            
            # Fallback: split by commas or newlines
            keywords = []
            for line in response.split('\n'):
                line = line.strip()
                if line and not line.startswith(('[', ']', '{', '}')):
                    # Remove bullet points, numbers, etc.
                    line = line.lstrip('•-*123456789. ')
                    if line:
                        keywords.append(line.lower())
            
            return keywords
            
        except Exception as e:
            logger.error(f"Failed to extract keywords: {e}")
            return []
    
    def _extract_og_description(self, response: str) -> str:
        """Extract OG description from AI response.
        
        Args:
            response: Raw AI response
        
        Returns:
            Cleaned OG description
        """
        cleaned = response.strip()
        prefixes = ["OG Description:", "Description:", "Open Graph:", "Output:"]
        for prefix in prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
        
        # Remove quotes if present
        cleaned = cleaned.strip('"\'')
        
        return cleaned
    
    def _fallback_meta_description(
        self,
        title: str,
        script: str,
        keywords: List[str]
    ) -> str:
        """Fallback rule-based meta description generation.
        
        Args:
            title: Content title
            script: Content script
            keywords: Primary keywords
        
        Returns:
            Rule-based meta description
        """
        # Simple extraction from first sentences
        sentences = re.split(r'[.!?]+', script)
        
        description = ""
        for sentence in sentences[:3]:
            sentence = sentence.strip()
            if sentence and len(sentence.split()) >= 5:
                test_desc = f"{description} {sentence}".strip()
                if len(test_desc) <= self.META_DESCRIPTION_MAX:
                    description = test_desc
                else:
                    break
        
        # Ensure length
        if len(description) > self.META_DESCRIPTION_MAX:
            description = description[:self.META_DESCRIPTION_MAX].rsplit(' ', 1)[0] + "..."
        elif len(description) < self.META_DESCRIPTION_MIN:
            description = f"{title}. {description}"[:self.META_DESCRIPTION_MAX]
        
        return description.strip()
    
    def _fallback_title_tag(
        self,
        title: str,
        keywords: List[str]
    ) -> str:
        """Fallback rule-based title tag generation.
        
        Args:
            title: Original title
            keywords: Primary keywords
        
        Returns:
            Rule-based title tag
        """
        brand_suffix = f" | {self.brand_name}" if self.include_brand and self.brand_name else ""
        available_space = self.TITLE_TAG_MAX - len(brand_suffix)
        
        if len(title) <= available_space:
            return title + brand_suffix
        else:
            return title[:available_space].rsplit(' ', 1)[0] + brand_suffix


def generate_ai_seo_metadata(
    title: str,
    script: str,
    primary_keywords: List[str],
    secondary_keywords: List[str],
    keyword_density: Dict[str, float],
    config: Optional[AIConfig] = None,
    brand_name: Optional[str] = None,
    generate_related: bool = True
) -> SEOMetadata:
    """Convenience function to generate AI-powered SEO metadata.
    
    This function provides the main entry point for AI-enhanced SEO
    metadata generation as specified in POST-001.
    
    Args:
        title: Content title
        script: Content script/body
        primary_keywords: Primary keywords from extraction
        secondary_keywords: Secondary keywords from extraction
        keyword_density: Keyword density analysis
        config: Optional AI configuration
        brand_name: Optional brand name for title tags
        generate_related: Whether to generate AI-powered related keywords
    
    Returns:
        SEOMetadata object with AI-generated metadata fields
    
    Example:
        >>> from T.Publishing.SEO.Keywords import extract_keywords
        >>> from T.Publishing.SEO.Keywords.ai_metadata_generator import generate_ai_seo_metadata
        >>> 
        >>> # First extract keywords
        >>> extraction = extract_keywords(
        ...     title="How to Learn Python Programming",
        ...     script="Python is a versatile programming language..."
        ... )
        >>> 
        >>> # Then generate AI-enhanced metadata
        >>> metadata = generate_ai_seo_metadata(
        ...     title="How to Learn Python Programming",
        ...     script="Python is a versatile programming language...",
        ...     primary_keywords=extraction.primary_keywords,
        ...     secondary_keywords=extraction.secondary_keywords,
        ...     keyword_density=extraction.keyword_density,
        ...     brand_name="TechEdu"
        ... )
        >>> 
        >>> print(metadata.meta_description)
        >>> print(metadata.quality_score)
    """
    generator = AIMetadataGenerator(
        config=config,
        brand_name=brand_name
    )
    
    # Generate AI-powered metadata
    meta_description = generator.generate_meta_description(
        title=title,
        script=script,
        primary_keywords=primary_keywords
    )
    
    title_tag = generator.generate_title_tag(
        title=title,
        primary_keywords=primary_keywords
    )
    
    og_description = generator.generate_og_description(
        title=title,
        script=script,
        meta_description=meta_description,
        primary_keywords=primary_keywords
    )
    
    # Generate AI-suggested related keywords
    related_keywords = []
    if generate_related:
        related_keywords = generator.suggest_related_keywords(
            title=title,
            script=script,
            primary_keywords=primary_keywords,
            max_suggestions=10
        )
    
    # Create metadata object
    metadata = SEOMetadata(
        primary_keywords=primary_keywords,
        secondary_keywords=secondary_keywords,
        meta_description=meta_description,
        title_tag=title_tag,
        keyword_density=keyword_density,
        related_keywords=related_keywords,
        og_title=title_tag.split(' | ')[0] if ' | ' in title_tag else title_tag,
        og_description=og_description
    )
    
    # Calculate quality score (simplified for AI-generated content)
    metadata.quality_score = _calculate_ai_quality_score(metadata)
    metadata.recommendations = _generate_ai_recommendations(metadata)
    
    return metadata


def _calculate_ai_quality_score(metadata: SEOMetadata) -> int:
    """Calculate quality score for AI-generated metadata.
    
    Args:
        metadata: SEO metadata object
    
    Returns:
        Quality score (0-100)
    """
    score = 0
    
    # Meta description length (25 points)
    desc_len = len(metadata.meta_description)
    if 150 <= desc_len <= 160:
        score += 25
    elif 140 <= desc_len < 150 or 160 < desc_len <= 170:
        score += 20
    elif 120 <= desc_len < 140:
        score += 15
    
    # Title tag length (25 points)
    if len(metadata.title_tag) <= 60:
        score += 25
    elif len(metadata.title_tag) <= 70:
        score += 20
    
    # Keyword presence (30 points)
    if len(metadata.primary_keywords) >= 5:
        score += 30
    elif len(metadata.primary_keywords) >= 3:
        score += 20
    elif len(metadata.primary_keywords) >= 1:
        score += 10
    
    # Related keywords (10 points)
    if len(metadata.related_keywords) >= 5:
        score += 10
    elif len(metadata.related_keywords) >= 3:
        score += 7
    
    # OG metadata (10 points)
    if metadata.og_title and metadata.og_description:
        score += 10
    
    return min(score, 100)


def _generate_ai_recommendations(metadata: SEOMetadata) -> List[str]:
    """Generate recommendations for AI-generated metadata.
    
    Args:
        metadata: SEO metadata object
    
    Returns:
        List of recommendations
    """
    recommendations = []
    
    desc_len = len(metadata.meta_description)
    if desc_len < 150:
        recommendations.append(
            f"Meta description is short ({desc_len} chars). Consider expanding to 150-160 characters."
        )
    elif desc_len > 160:
        recommendations.append(
            f"Meta description is long ({desc_len} chars). May be truncated in search results."
        )
    
    if len(metadata.title_tag) > 60:
        recommendations.append(
            f"Title tag ({len(metadata.title_tag)} chars) may be truncated. Aim for <60 characters."
        )
    
    if not recommendations:
        recommendations.append("AI-generated SEO metadata meets best practice guidelines!")
    
    return recommendations
