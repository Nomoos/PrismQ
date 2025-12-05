"""AI-Powered Script Generator using Qwen2.5-14B-Instruct via Ollama.

This module provides AI-powered script generation for the PrismQ.T.Script.From.Idea.Title
workflow using the Qwen2.5-14B-Instruct model. It generates high-quality, contextually-aware
scripts from ideas and titles using prompt engineering best practices.

Workflow Position:
    Stage: PrismQ.T.Script.From.Idea.Title
    Input: Idea + Title → AI Generation → Output: Script v1

Features:
    - Qwen2.5-14B-Instruct model for script generation
    - Prompt engineering for compelling narratives
    - Platform-specific optimization (YouTube, TikTok, etc.)
    - Graceful fallback to rule-based generation
    - Section-based generation (intro, body, conclusion)
"""

import json
import requests
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AIScriptGeneratorConfig:
    """Configuration for AI-powered script generation.
    
    Attributes:
        model: Name of the Ollama model to use (default: Qwen2.5-14B-Instruct)
        api_base: Base URL for Ollama API
        temperature: Sampling temperature (0.0-2.0, lower = more focused)
        max_tokens: Maximum tokens to generate
        timeout: Request timeout in seconds
        enable_ai: Whether to use AI generation (fallback to rule-based if False)
    """
    model: str = "qwen2.5:14b-instruct"
    api_base: str = "http://localhost:11434"
    temperature: float = 0.7  # Moderate creativity for engaging scripts
    max_tokens: int = 2000
    timeout: int = 120  # Longer timeout for script generation
    enable_ai: bool = True


class AIScriptGenerator:
    """Generate scripts using AI-powered prompt engineering with Qwen2.5-14B-Instruct.
    
    This class uses carefully crafted prompts to generate high-quality
    scripts that follow storytelling best practices and are optimized for
    the target platform and audience.
    """
    
    def __init__(
        self,
        config: Optional[AIScriptGeneratorConfig] = None
    ):
        """Initialize the AI script generator.
        
        Args:
            config: Optional AI configuration
        """
        self.config = config or AIScriptGeneratorConfig()
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
            logger.warning(f"Ollama not available: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if AI script generation is available.
        
        Returns:
            True if AI generation is available, False otherwise
        """
        return self.available
    
    def generate_full_script(
        self,
        idea_data: Dict[str, Any],
        title: str,
        target_duration_seconds: int = 90,
        platform: str = "youtube_medium",
        tone: str = "engaging"
    ) -> Optional[str]:
        """Generate a complete script using AI.
        
        Args:
            idea_data: Dictionary containing idea information (concept, synopsis, etc.)
            title: The title for the script
            target_duration_seconds: Target duration in seconds
            platform: Target platform (youtube_short, youtube_medium, tiktok, etc.)
            tone: Script tone (engaging, mysterious, educational, dramatic)
        
        Returns:
            Generated script text, or None if AI is unavailable
        """
        if not self.available:
            logger.info("AI not available for script generation")
            return None
        
        prompt = self._create_full_script_prompt(
            idea_data=idea_data,
            title=title,
            target_duration=target_duration_seconds,
            platform=platform,
            tone=tone
        )
        
        try:
            response = self._call_ollama(prompt)
            script = self._extract_script_text(response)
            return script
        except Exception as e:
            logger.error(f"AI script generation failed: {e}")
            return None
    
    def generate_hook(
        self,
        idea_data: Dict[str, Any],
        title: str,
        target_duration_seconds: int = 15,
        tone: str = "engaging"
    ) -> Optional[str]:
        """Generate just the hook/introduction section using AI.
        
        Args:
            idea_data: Dictionary containing idea information
            title: The title for the script
            target_duration_seconds: Target duration for the hook
            tone: Script tone
        
        Returns:
            Generated hook text, or None if AI is unavailable
        """
        if not self.available:
            return None
        
        prompt = self._create_hook_prompt(
            idea_data=idea_data,
            title=title,
            target_duration=target_duration_seconds,
            tone=tone
        )
        
        try:
            response = self._call_ollama(prompt)
            return self._extract_script_text(response)
        except Exception as e:
            logger.error(f"AI hook generation failed: {e}")
            return None
    
    def generate_body(
        self,
        idea_data: Dict[str, Any],
        title: str,
        hook: str,
        target_duration_seconds: int = 60,
        tone: str = "engaging"
    ) -> Optional[str]:
        """Generate the main body section using AI.
        
        Args:
            idea_data: Dictionary containing idea information
            title: The title for the script
            hook: The already generated hook/introduction
            target_duration_seconds: Target duration for the body
            tone: Script tone
        
        Returns:
            Generated body text, or None if AI is unavailable
        """
        if not self.available:
            return None
        
        prompt = self._create_body_prompt(
            idea_data=idea_data,
            title=title,
            hook=hook,
            target_duration=target_duration_seconds,
            tone=tone
        )
        
        try:
            response = self._call_ollama(prompt)
            return self._extract_script_text(response)
        except Exception as e:
            logger.error(f"AI body generation failed: {e}")
            return None
    
    def generate_conclusion(
        self,
        idea_data: Dict[str, Any],
        title: str,
        hook: str,
        body: str,
        target_duration_seconds: int = 15,
        include_cta: bool = True,
        tone: str = "engaging"
    ) -> Optional[str]:
        """Generate the conclusion section using AI.
        
        Args:
            idea_data: Dictionary containing idea information
            title: The title for the script
            hook: The hook/introduction
            body: The main body
            target_duration_seconds: Target duration for conclusion
            include_cta: Whether to include a call-to-action
            tone: Script tone
        
        Returns:
            Generated conclusion text, or None if AI is unavailable
        """
        if not self.available:
            return None
        
        prompt = self._create_conclusion_prompt(
            idea_data=idea_data,
            title=title,
            hook=hook,
            body=body,
            target_duration=target_duration_seconds,
            include_cta=include_cta,
            tone=tone
        )
        
        try:
            response = self._call_ollama(prompt)
            return self._extract_script_text(response)
        except Exception as e:
            logger.error(f"AI conclusion generation failed: {e}")
            return None
    
    def _create_full_script_prompt(
        self,
        idea_data: Dict[str, Any],
        title: str,
        target_duration: int,
        platform: str,
        tone: str
    ) -> str:
        """Create prompt for full script generation.
        
        Uses advanced prompt engineering techniques:
        - Role definition (expert scriptwriter)
        - Clear constraints (duration, platform, structure)
        - Context from idea
        - Output formatting instructions
        
        Args:
            idea_data: Idea information dictionary
            title: Script title
            target_duration: Target duration in seconds
            platform: Target platform
            tone: Script tone
        
        Returns:
            Engineered prompt for AI
        """
        # Extract idea components
        concept = idea_data.get('concept', '')
        synopsis = idea_data.get('synopsis', '')
        hook = idea_data.get('hook', '')
        premise = idea_data.get('premise', '')
        genre = idea_data.get('genre', 'general')
        target_audience = idea_data.get('target_audience', 'general audience')
        themes = idea_data.get('themes', [])
        
        # Calculate approximate word count (2.5 words per second for narration)
        target_words = int(target_duration * 2.5)
        
        # Platform-specific instructions
        platform_instructions = self._get_platform_instructions(platform)
        
        prompt = f"""You are an expert scriptwriter specializing in short-form video content for social media. Your task is to write a compelling, engaging script for narration.

**Title**: "{title}"

**Core Concept**: {concept}

**Synopsis**: {synopsis}

**Hook/Opening Idea**: {hook}

**Premise**: {premise}

**Genre**: {genre}

**Target Audience**: {target_audience}

**Themes**: {', '.join(themes) if themes else 'Not specified'}

**Target Duration**: {target_duration} seconds (approximately {target_words} words)

**Platform**: {platform}

**Tone**: {tone}

{platform_instructions}

**Script Structure Requirements**:
1. **Hook/Introduction** (first 10-15% of script):
   - Open with an attention-grabbing statement or question
   - Create immediate intrigue
   - Establish the tone
   - Make the viewer want to keep watching

2. **Main Body** (70-75% of script):
   - Deliver on the title's promise
   - Build narrative tension or provide valuable information
   - Maintain engagement throughout
   - Use vivid descriptions and emotional language
   - Include sensory details when appropriate

3. **Conclusion** (10-15% of script):
   - Provide a satisfying resolution or key takeaway
   - Create a memorable ending
   - Optional: subtle call-to-action

**Writing Guidelines**:
- Write in first or second person for intimacy
- Use short, punchy sentences for impact
- Include natural pauses (use ... for dramatic effect)
- Avoid complex vocabulary - aim for accessibility
- Create emotional connection with the audience
- Match the {tone} tone throughout

**Output Format**:
Return ONLY the script text, ready for narration. No section headers, no stage directions, no explanations. Just the spoken words.

Script:"""
        
        return prompt
    
    def _create_hook_prompt(
        self,
        idea_data: Dict[str, Any],
        title: str,
        target_duration: int,
        tone: str
    ) -> str:
        """Create prompt for hook/introduction generation."""
        concept = idea_data.get('concept', '')
        hook = idea_data.get('hook', '')
        premise = idea_data.get('premise', '')
        target_words = int(target_duration * 2.5)
        
        prompt = f"""You are an expert scriptwriter. Write a compelling hook/introduction for a video script.

**Title**: "{title}"
**Core Concept**: {concept}
**Hook Idea**: {hook}
**Premise**: {premise}
**Target Length**: {target_duration} seconds ({target_words} words)
**Tone**: {tone}

**Requirements**:
1. Open with an attention-grabbing statement or question
2. Create immediate intrigue and curiosity
3. Establish the tone of the content
4. Make the viewer want to continue watching
5. Naturally lead into the main content

**Output Format**:
Return ONLY the hook text, ready for narration. No explanations or section headers.

Hook:"""
        
        return prompt
    
    def _create_body_prompt(
        self,
        idea_data: Dict[str, Any],
        title: str,
        hook: str,
        target_duration: int,
        tone: str
    ) -> str:
        """Create prompt for body generation."""
        concept = idea_data.get('concept', '')
        synopsis = idea_data.get('synopsis', '')
        themes = idea_data.get('themes', [])
        target_words = int(target_duration * 2.5)
        
        prompt = f"""You are an expert scriptwriter. Write the main body of a video script that continues from an existing hook.

**Title**: "{title}"
**Core Concept**: {concept}
**Synopsis**: {synopsis}
**Themes**: {', '.join(themes) if themes else 'Not specified'}
**Target Length**: {target_duration} seconds ({target_words} words)
**Tone**: {tone}

**Already Written Hook**:
{hook}

**Requirements**:
1. Continue naturally from the hook
2. Deliver on the title's promise
3. Build narrative tension or provide valuable information
4. Maintain engagement throughout
5. Use vivid descriptions and emotional language
6. Lead naturally toward a conclusion

**Output Format**:
Return ONLY the body text, ready for narration. No explanations or section headers.

Body:"""
        
        return prompt
    
    def _create_conclusion_prompt(
        self,
        idea_data: Dict[str, Any],
        title: str,
        hook: str,
        body: str,
        target_duration: int,
        include_cta: bool,
        tone: str
    ) -> str:
        """Create prompt for conclusion generation."""
        concept = idea_data.get('concept', '')
        target_words = int(target_duration * 2.5)
        
        cta_instruction = """
7. End with a subtle call-to-action (e.g., "Let me know what you think in the comments" or "Follow for more")""" if include_cta else ""
        
        prompt = f"""You are an expert scriptwriter. Write a satisfying conclusion for a video script.

**Title**: "{title}"
**Core Concept**: {concept}
**Target Length**: {target_duration} seconds ({target_words} words)
**Tone**: {tone}

**Already Written Content**:
Hook: {hook}

Body: {body}

**Requirements**:
1. Continue naturally from the body
2. Provide a satisfying resolution or key takeaway
3. Create a memorable ending
4. Maintain the {tone} tone
5. Leave the viewer with something to think about
6. Keep it concise but impactful{cta_instruction}

**Output Format**:
Return ONLY the conclusion text, ready for narration. No explanations or section headers.

Conclusion:"""
        
        return prompt
    
    def _get_platform_instructions(self, platform: str) -> str:
        """Get platform-specific writing instructions."""
        instructions = {
            "youtube_short": """**Platform-Specific Instructions (YouTube Shorts)**:
- Maximize engagement in the first 3 seconds
- Keep sentences very short and punchy
- High energy throughout
- Vertical format optimized content""",
            
            "youtube_medium": """**Platform-Specific Instructions (YouTube)**:
- Strong hook in first 5-10 seconds
- Good pacing with natural flow
- Balance entertainment with information
- Encourage engagement and watch time""",
            
            "youtube_long": """**Platform-Specific Instructions (YouTube Long-Form)**:
- Build up to key moments
- Include multiple hooks throughout
- Deeper storytelling allowed
- Reward viewers who watch longer""",
            
            "tiktok": """**Platform-Specific Instructions (TikTok)**:
- Extremely attention-grabbing opening
- Very short, snappy sentences
- Trend-aware language
- Maximum engagement focus""",
            
            "instagram_reel": """**Platform-Specific Instructions (Instagram Reels)**:
- Visual storytelling focus
- Aesthetic and polished tone
- Relatable content
- Clear and concise messaging"""
        }
        
        return instructions.get(platform, """**Platform-Specific Instructions**:
- Focus on engagement
- Clear and accessible language
- Strong narrative structure""")
    
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
            raise RuntimeError(f"Failed to generate AI script: {e}")
    
    def _extract_script_text(self, response: str) -> str:
        """Extract script text from AI response.
        
        Args:
            response: Raw AI response
        
        Returns:
            Cleaned script text
        """
        cleaned = response.strip()
        
        # Remove common prefixes that the model might add
        prefixes_to_remove = [
            "Script:", "Hook:", "Body:", "Conclusion:",
            "Here is the script:", "Here's the script:",
            "Output:", "Result:"
        ]
        
        for prefix in prefixes_to_remove:
            if cleaned.lower().startswith(prefix.lower()):
                cleaned = cleaned[len(prefix):].strip()
        
        # Remove quotes if the entire response is quoted
        if cleaned.startswith('"') and cleaned.endswith('"'):
            cleaned = cleaned[1:-1]
        if cleaned.startswith("'") and cleaned.endswith("'"):
            cleaned = cleaned[1:-1]
        
        return cleaned


def generate_ai_script(
    idea_data: Dict[str, Any],
    title: str,
    target_duration_seconds: int = 90,
    platform: str = "youtube_medium",
    tone: str = "engaging",
    config: Optional[AIScriptGeneratorConfig] = None
) -> Optional[str]:
    """Convenience function to generate an AI-powered script.
    
    This function provides the main entry point for AI-enhanced script
    generation using Qwen2.5-14B-Instruct.
    
    Args:
        idea_data: Dictionary containing idea information
        title: Script title
        target_duration_seconds: Target duration in seconds
        platform: Target platform
        tone: Script tone
        config: Optional AI configuration
    
    Returns:
        Generated script text, or None if AI is unavailable
    
    Example:
        >>> idea = {
        ...     "concept": "A haunted house mystery",
        ...     "synopsis": "A girl discovers a time-loop...",
        ...     "hook": "Every night at midnight, she returns.",
        ...     "genre": "horror"
        ... }
        >>> script = generate_ai_script(
        ...     idea_data=idea,
        ...     title="The Mystery of the Abandoned House",
        ...     target_duration_seconds=90
        ... )
        >>> if script:
        ...     print(script)
    """
    generator = AIScriptGenerator(config=config)
    return generator.generate_full_script(
        idea_data=idea_data,
        title=title,
        target_duration_seconds=target_duration_seconds,
        platform=platform,
        tone=tone
    )


__all__ = [
    "AIScriptGenerator",
    "AIScriptGeneratorConfig",
    "generate_ai_script"
]
