"""AI-powered Idea generation using local LLMs via Ollama.

This module provides AI generation capabilities for creating Ideas using
local LLM models through Ollama API. It supports various high-quality models
optimized for RTX 5090 and other high-end GPUs.
"""

import json
import requests
from typing import List, Dict, Any, Optional, Literal
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AIConfig:
    """Configuration for AI model and generation.
    
    Attributes:
        model: Name of the Ollama model to use
        api_base: Base URL for Ollama API
        temperature: Sampling temperature (0.0-2.0)
        max_tokens: Maximum tokens to generate
        timeout: Request timeout in seconds
    """
    model: str = "llama3.1:70b-q4_K_M"  # Default: Best for RTX 5090
    api_base: str = "http://localhost:11434"
    temperature: float = 0.8
    max_tokens: int = 2000
    timeout: int = 120


class AIIdeaGenerator:
    """Generate Ideas using local AI models via Ollama.
    
    This class handles communication with local LLM models through the
    Ollama API to generate rich, detailed Ideas with comprehensive
    narrative structure.
    """
    
    def __init__(self, config: Optional[AIConfig] = None):
        """Initialize AI generator with configuration.
        
        Args:
            config: Optional AI configuration
        """
        self.config = config or AIConfig()
        self.available = self._check_ollama_availability()
    
    def _check_ollama_availability(self) -> bool:
        """Check if Ollama is available and running.
        
        Returns:
            True if Ollama is available, False otherwise
        """
        try:
            response = requests.get(
                f"{self.config.api_base}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False
    
    def generate_ideas_from_title(
        self,
        title: str,
        num_ideas: int = 10,
        target_platforms: Optional[List[str]] = None,
        target_formats: Optional[List[str]] = None,
        genre: Optional[str] = None,
        length_target: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Generate multiple idea variations from a title using AI.
        
        Args:
            title: Base title to generate ideas from
            num_ideas: Number of idea variations to generate
            target_platforms: Target platforms for content
            target_formats: Target formats for content
            genre: Content genre
            length_target: Target content length
            
        Returns:
            List of dictionaries containing idea data
        """
        if not self.available:
            logger.warning("Ollama not available, returning empty list")
            return []
        
        prompt = self._create_title_prompt(
            title=title,
            num_ideas=num_ideas,
            target_platforms=target_platforms,
            target_formats=target_formats,
            genre=genre,
            length_target=length_target
        )
        
        response_text = self._call_ollama(prompt)
        return self._parse_ideas_response(response_text, num_ideas)
    
    def generate_ideas_from_description(
        self,
        description: str,
        num_ideas: int = 10,
        target_platforms: Optional[List[str]] = None,
        target_formats: Optional[List[str]] = None,
        genre: Optional[str] = None,
        length_target: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Generate multiple ideas from a description using AI.
        
        Args:
            description: Description to generate ideas from
            num_ideas: Number of ideas to generate
            target_platforms: Target platforms for content
            target_formats: Target formats for content
            genre: Content genre
            length_target: Target content length
            
        Returns:
            List of dictionaries containing idea data
        """
        if not self.available:
            logger.warning("Ollama not available, returning empty list")
            return []
        
        prompt = self._create_description_prompt(
            description=description,
            num_ideas=num_ideas,
            target_platforms=target_platforms,
            target_formats=target_formats,
            genre=genre,
            length_target=length_target
        )
        
        response_text = self._call_ollama(prompt)
        return self._parse_ideas_response(response_text, num_ideas)
    
    def _create_title_prompt(
        self,
        title: str,
        num_ideas: int,
        target_platforms: Optional[List[str]] = None,
        target_formats: Optional[List[str]] = None,
        genre: Optional[str] = None,
        length_target: Optional[str] = None
    ) -> str:
        """Create a prompt for generating ideas from a title.
        
        Args:
            title: Base title
            num_ideas: Number of ideas to generate
            target_platforms: Target platforms
            target_formats: Target formats
            genre: Content genre
            length_target: Target length
            
        Returns:
            Formatted prompt string
        """
        platforms_str = ", ".join(target_platforms) if target_platforms else "youtube, medium"
        formats_str = ", ".join(target_formats) if target_formats else "text, video"
        genre_str = genre if genre else "general"
        length_str = length_target if length_target else "variable"
        
        prompt = f"""You are a creative content strategist. Generate {num_ideas} unique and compelling content ideas based on the title: "{title}"

Target platforms: {platforms_str}
Target formats: {formats_str}
Genre: {genre_str}
Length target: {length_str}

For each idea, provide:
1. A unique title variation
2. A compelling concept (1-2 sentences)
3. A detailed premise (2-3 sentences)
4. A logline (one impactful sentence)
5. A hook (attention-grabbing opening)
6. A synopsis (2-3 paragraphs, 150-300 words)
7. A skeleton (5-7 key points)
8. An outline (detailed structure with sections)
9. 5-10 relevant keywords
10. 3-5 main themes

Make each idea distinct and engaging for the target platforms and formats.

Format your response as a JSON array of {num_ideas} objects, each with these fields:
- title
- concept
- premise
- logline
- hook
- synopsis
- skeleton
- outline
- keywords (array of strings)
- themes (array of strings)

Return ONLY the JSON array, no additional text."""
        
        return prompt
    
    def _create_description_prompt(
        self,
        description: str,
        num_ideas: int,
        target_platforms: Optional[List[str]] = None,
        target_formats: Optional[List[str]] = None,
        genre: Optional[str] = None,
        length_target: Optional[str] = None
    ) -> str:
        """Create a prompt for generating ideas from a description.
        
        Args:
            description: Base description
            num_ideas: Number of ideas to generate
            target_platforms: Target platforms
            target_formats: Target formats
            genre: Content genre
            length_target: Target length
            
        Returns:
            Formatted prompt string
        """
        platforms_str = ", ".join(target_platforms) if target_platforms else "youtube, medium"
        formats_str = ", ".join(target_formats) if target_formats else "text, video"
        genre_str = genre if genre else "general"
        length_str = length_target if length_target else "variable"
        
        prompt = f"""You are a creative content strategist. Generate {num_ideas} unique and compelling content ideas based on this description: "{description}"

Target platforms: {platforms_str}
Target formats: {formats_str}
Genre: {genre_str}
Length target: {length_str}

For each idea, provide:
1. A unique title
2. A compelling concept (1-2 sentences)
3. A detailed premise (2-3 sentences)
4. A logline (one impactful sentence)
5. A hook (attention-grabbing opening)
6. A synopsis (2-3 paragraphs, 150-300 words)
7. A skeleton (5-7 key points)
8. An outline (detailed structure with sections)
9. 5-10 relevant keywords
10. 3-5 main themes

Make each idea distinct and engaging for the target platforms and formats.

Format your response as a JSON array of {num_ideas} objects, each with these fields:
- title
- concept
- premise
- logline
- hook
- synopsis
- skeleton
- outline
- keywords (array of strings)
- themes (array of strings)

Return ONLY the JSON array, no additional text."""
        
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
            return result.get("response", "")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API call failed: {e}")
            raise RuntimeError(f"Failed to generate ideas: {e}")
    
    def _parse_ideas_response(
        self,
        response_text: str,
        expected_count: int
    ) -> List[Dict[str, Any]]:
        """Parse AI response into idea dictionaries.
        
        Args:
            response_text: Raw response from AI
            expected_count: Expected number of ideas
            
        Returns:
            List of parsed idea dictionaries
        """
        try:
            # Try to extract JSON from response
            # Sometimes models add explanatory text before/after JSON
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']')
            
            if start_idx >= 0 and end_idx > start_idx:
                json_text = response_text[start_idx:end_idx + 1]
                ideas = json.loads(json_text)
                
                if isinstance(ideas, list):
                    # Validate and clean each idea
                    validated_ideas = []
                    for idea in ideas[:expected_count]:
                        if isinstance(idea, dict) and 'title' in idea:
                            validated_ideas.append(self._validate_idea_dict(idea))
                    
                    return validated_ideas
            
            logger.warning("Failed to parse JSON from AI response")
            return []
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            return []
    
    def _validate_idea_dict(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and ensure all required fields exist in idea dict.
        
        Args:
            idea: Raw idea dictionary
            
        Returns:
            Validated idea dictionary with all fields
        """
        # Ensure all required fields exist
        required_fields = {
            'title': '',
            'concept': '',
            'premise': '',
            'logline': '',
            'hook': '',
            'synopsis': '',
            'skeleton': '',
            'outline': '',
            'keywords': [],
            'themes': []
        }
        
        for field, default in required_fields.items():
            if field not in idea:
                idea[field] = default
            elif field in ['keywords', 'themes'] and not isinstance(idea[field], list):
                idea[field] = [idea[field]] if idea[field] else []
        
        return idea


__all__ = ["AIIdeaGenerator", "AIConfig"]
