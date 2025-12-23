"""AI-Powered Content Generator using Qwen3:32b via Ollama.

This module provides AI-powered content generation for the PrismQ.T.Content.From.Idea.Title
workflow using the Qwen3:32b model.

ALL generation goes through local AI models. No fallback to rule-based generation.

Input to AI:
    - Title (Titulek)
    - Idea text
    - One seed variation (randomly picked from 500 predefined variations)

Workflow Position:
    Stage: PrismQ.T.Content.From.Idea.Title
    Input: Title + Idea + Seed → AI Generation → Output: Content v1

Prompt Optimization for Qwen3:32b:
    - Structured markdown format for clarity
    - Clear role definition (expert content writer)
    - Explicit audience context
    - Specific constraints (word count, style, format)
    - Natural language emphasis
    - Avoids meta-commentary requirements
"""

import logging
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)


# =============================================================================
# INPUT SANITIZATION
# =============================================================================


def _sanitize_text_input(text: str, max_length: int = 10000, field_name: str = "text") -> str:
    """Sanitize text input to prevent injection attacks and ensure safety.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        field_name: Name of the field (for error messages)
        
    Returns:
        Sanitized text
        
    Raises:
        ValueError: If text is invalid or too long
    """
    if not text or not text.strip():
        raise ValueError(f"{field_name} cannot be empty")
    
    text = text.strip()
    
    # Check length
    if len(text) > max_length:
        raise ValueError(f"{field_name} too long ({len(text)} chars). Maximum: {max_length}")
    
    # Remove any null bytes
    text = text.replace('\x00', '')
    
    # Check for suspicious patterns (basic protection)
    # Note: This is just basic sanitization. The AI prompt is safe since we control it.
    # The main concern is preventing extremely malicious input
    if len(text) != len(text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')):
        logger.warning(f"Input contains non-UTF-8 characters in {field_name}")
    
    return text


# =============================================================================
# PROMPT FILE LOADING
# =============================================================================

_PROMPTS_DIR = Path(__file__).parent.parent / "_meta" / "prompts"


def _load_prompt(filename: str) -> str:
    """Load a prompt from the prompts directory.

    Args:
        filename: Name of the prompt file (e.g., 'script_generation.txt')

    Returns:
        The prompt text content

    Raises:
        FileNotFoundError: If the prompt file doesn't exist
    """
    prompt_path = _PROMPTS_DIR / filename
    return prompt_path.read_text(encoding="utf-8")


# 500 predefined seed variations - simple words/concepts for creative inspiration
# One is picked randomly for each generation
SEED_VARIATIONS = [
    # Food & Drinks (1-40)
    "pudding",
    "fire",
    "chocolate",
    "coffee",
    "tea",
    "honey",
    "sugar",
    "salt",
    "bread",
    "butter",
    "cheese",
    "wine",
    "beer",
    "whiskey",
    "milk",
    "cream",
    "apple",
    "orange",
    "lemon",
    "strawberry",
    "cherry",
    "grape",
    "banana",
    "mango",
    "chicken",
    "beef",
    "fish",
    "salmon",
    "shrimp",
    "lobster",
    "pasta",
    "rice",
    "soup",
    "salad",
    "pizza",
    "burger",
    "sandwich",
    "cake",
    "pie",
    "cookie",
    # Elements & Nature (41-90)
    "water",
    "earth",
    "wind",
    "thunder",
    "lightning",
    "rain",
    "snow",
    "ice",
    "sun",
    "moon",
    "star",
    "sky",
    "cloud",
    "fog",
    "mist",
    "storm",
    "ocean",
    "sea",
    "river",
    "lake",
    "pond",
    "waterfall",
    "stream",
    "wave",
    "mountain",
    "valley",
    "hill",
    "cliff",
    "cave",
    "desert",
    "forest",
    "jungle",
    "tree",
    "flower",
    "grass",
    "leaf",
    "root",
    "seed",
    "branch",
    "vine",
    "rock",
    "stone",
    "sand",
    "dust",
    "mud",
    "crystal",
    "diamond",
    "gold",
    "silver",
    "copper",
    # Family & People (91-130)
    "sister",
    "brother",
    "mother",
    "father",
    "grandmother",
    "grandfather",
    "aunt",
    "uncle",
    "cousin",
    "daughter",
    "son",
    "wife",
    "husband",
    "friend",
    "neighbor",
    "stranger",
    "child",
    "baby",
    "teenager",
    "adult",
    "elder",
    "teacher",
    "student",
    "doctor",
    "nurse",
    "lawyer",
    "artist",
    "musician",
    "writer",
    "chef",
    "farmer",
    "soldier",
    "king",
    "queen",
    "prince",
    "princess",
    "knight",
    "wizard",
    "witch",
    "hero",
    # US Cities & States (131-180)
    "Maine",
    "Chicago",
    "New York",
    "Los Angeles",
    "Miami",
    "Boston",
    "Seattle",
    "Denver",
    "Austin",
    "Dallas",
    "Houston",
    "Phoenix",
    "Atlanta",
    "Detroit",
    "Cleveland",
    "Portland",
    "San Francisco",
    "Las Vegas",
    "New Orleans",
    "Nashville",
    "Memphis",
    "Philadelphia",
    "Baltimore",
    "Washington",
    "California",
    "Texas",
    "Florida",
    "Alaska",
    "Hawaii",
    "Montana",
    "Arizona",
    "Nevada",
    "Colorado",
    "Oregon",
    "Vermont",
    "Massachusetts",
    "Virginia",
    "Georgia",
    "Tennessee",
    "Kentucky",
    "Minnesota",
    "Wisconsin",
    "Michigan",
    "Ohio",
    "Indiana",
    "Illinois",
    "Missouri",
    "Kansas",
    "Nebraska",
    "Iowa",
    # Countries & Regions (181-240)
    "Germany",
    "United Kingdom",
    "France",
    "Italy",
    "Spain",
    "Portugal",
    "Netherlands",
    "Belgium",
    "Switzerland",
    "Austria",
    "Poland",
    "Sweden",
    "Norway",
    "Denmark",
    "Finland",
    "Iceland",
    "Japan",
    "China",
    "Korea",
    "Vietnam",
    "Thailand",
    "India",
    "Pakistan",
    "Bangladesh",
    "Indonesia",
    "Philippines",
    "Malaysia",
    "Singapore",
    "Taiwan",
    "Mongolia",
    "Nepal",
    "Tibet",
    "Australia",
    "New Zealand",
    "Fiji",
    "Samoa",
    "Tonga",
    "Papua",
    "Tasmania",
    "Queensland",
    "Brazil",
    "Argentina",
    "Chile",
    "Peru",
    "Colombia",
    "Mexico",
    "Canada",
    "Cuba",
    "Egypt",
    "Morocco",
    "Kenya",
    "Nigeria",
    "Ghana",
    "Ethiopia",
    "Tanzania",
    "Zimbabwe",
    "Russia",
    "Ukraine",
    "Turkey",
    "Iran",
    "Iraq",
    "Israel",
    "Jordan",
    "Lebanon",
    # Continents & Regions (241-260)
    "Asia",
    "Europe",
    "Africa",
    "America",
    "Antarctica",
    "Arctic",
    "Pacific",
    "Atlantic",
    "Caribbean",
    "Mediterranean",
    "Scandinavia",
    "Balkans",
    "Middle East",
    "Far East",
    "Southeast Asia",
    "Central America",
    "South America",
    "North America",
    "Western Europe",
    "Eastern Europe",
    # Feelings & Moods (261-310)
    "chill",
    "warm",
    "hot",
    "cold",
    "cool",
    "cozy",
    "comfortable",
    "relaxed",
    "happy",
    "sad",
    "angry",
    "scared",
    "excited",
    "nervous",
    "calm",
    "peaceful",
    "love",
    "hate",
    "fear",
    "hope",
    "joy",
    "sorrow",
    "pride",
    "shame",
    "curious",
    "bored",
    "tired",
    "energetic",
    "lazy",
    "motivated",
    "inspired",
    "creative",
    "lonely",
    "connected",
    "lost",
    "found",
    "confused",
    "clear",
    "certain",
    "doubtful",
    "brave",
    "afraid",
    "strong",
    "weak",
    "confident",
    "shy",
    "bold",
    "humble",
    "grateful",
    "jealous",
    # Time & Seasons (311-350)
    "morning",
    "afternoon",
    "evening",
    "night",
    "midnight",
    "dawn",
    "dusk",
    "twilight",
    "spring",
    "summer",
    "autumn",
    "winter",
    "fall",
    "harvest",
    "bloom",
    "frost",
    "Monday",
    "Friday",
    "Sunday",
    "weekend",
    "holiday",
    "birthday",
    "anniversary",
    "graduation",
    "yesterday",
    "today",
    "tomorrow",
    "forever",
    "never",
    "always",
    "sometimes",
    "often",
    "past",
    "present",
    "future",
    "ancient",
    "modern",
    "vintage",
    "classic",
    "contemporary",
    # Colors (351-380)
    "red",
    "blue",
    "green",
    "yellow",
    "orange",
    "purple",
    "pink",
    "brown",
    "black",
    "white",
    "gray",
    "silver",
    "golden",
    "bronze",
    "copper",
    "crimson",
    "azure",
    "emerald",
    "ruby",
    "sapphire",
    "amber",
    "ivory",
    "ebony",
    "scarlet",
    "turquoise",
    "violet",
    "indigo",
    "maroon",
    "navy",
    "olive",
    # Animals (381-430)
    "dog",
    "cat",
    "bird",
    "fish",
    "horse",
    "cow",
    "pig",
    "sheep",
    "lion",
    "tiger",
    "bear",
    "wolf",
    "fox",
    "deer",
    "rabbit",
    "mouse",
    "eagle",
    "owl",
    "hawk",
    "crow",
    "swan",
    "dove",
    "parrot",
    "penguin",
    "shark",
    "whale",
    "dolphin",
    "octopus",
    "turtle",
    "crab",
    "jellyfish",
    "starfish",
    "snake",
    "lizard",
    "frog",
    "butterfly",
    "bee",
    "spider",
    "ant",
    "dragonfly",
    "elephant",
    "giraffe",
    "zebra",
    "monkey",
    "gorilla",
    "panda",
    "koala",
    "kangaroo",
    "dragon",
    "phoenix",
    # Objects & Things (431-480)
    "door",
    "window",
    "mirror",
    "clock",
    "key",
    "lock",
    "book",
    "letter",
    "phone",
    "computer",
    "camera",
    "guitar",
    "piano",
    "violin",
    "drum",
    "trumpet",
    "car",
    "train",
    "plane",
    "boat",
    "bicycle",
    "motorcycle",
    "bus",
    "helicopter",
    "sword",
    "shield",
    "crown",
    "ring",
    "necklace",
    "bracelet",
    "watch",
    "glasses",
    "candle",
    "lamp",
    "torch",
    "lantern",
    "fire",
    "smoke",
    "ash",
    "ember",
    "bridge",
    "tower",
    "castle",
    "palace",
    "temple",
    "church",
    "lighthouse",
    "windmill",
    "umbrella",
    "blanket",
    # Abstract Concepts (481-500)
    "dream",
    "nightmare",
    "memory",
    "secret",
    "mystery",
    "magic",
    "miracle",
    "destiny",
    "truth",
    "lie",
    "promise",
    "wish",
    "hope",
    "faith",
    "trust",
    "freedom",
    "power",
    "wisdom",
    "courage",
    "justice",
]


def get_random_seed() -> str:
    """Get one random seed variation from the 500 predefined options.

    Returns:
        A single seed variation string
    """
    return random.choice(SEED_VARIATIONS)


def get_seed_by_index(index: int) -> str:
    """Get a specific seed variation by index.

    Args:
        index: Index of the seed (0-499)

    Returns:
        The seed variation at that index
    """
    return SEED_VARIATIONS[index % len(SEED_VARIATIONS)]


@dataclass
class AIContentGeneratorConfig:
    """Configuration for AI-powered content generation.

    All generation uses local AI models via Ollama.

    Attributes:
        model: Name of the Ollama model to use (default: Qwen3:30b)
        api_base: Base URL for Ollama API
        temperature: Sampling temperature (0.0-2.0, lower = more focused)
        max_tokens: Maximum tokens to generate
        timeout: Request timeout in seconds
    """

    model: str = "qwen3:32b"
    api_base: str = "http://localhost:11434"
    temperature: float = 0.7  # Moderate creativity for engaging scripts
    max_tokens: int = 2000
    timeout: int = 120  # Longer timeout for content generation


class AIContentGenerator:
    """Generate content using AI with Qwen3:30b.

    All generation goes through local AI models.

    Input:
        - Title (Titulek)
        - Idea text
        - One seed (randomly picked from 500 predefined variations)
    """

    def __init__(self, config: Optional[AIContentGeneratorConfig] = None):
        """Initialize the AI script generator.

        Args:
            config: Optional AI configuration
        """
        self.config = config or AIContentGeneratorConfig()
        self.available = self._check_ollama_availability()

    def _check_ollama_availability(self) -> bool:
        """Check if Ollama is available and running.

        Returns:
            True if Ollama is available, False otherwise
        """
        try:
            response = requests.get(f"{self.config.api_base}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False

    def is_available(self) -> bool:
        """Check if AI content generation is available.

        Returns:
            True if AI generation is available, False otherwise
        """
        return self.available

    def generate_content(
        self,
        title: str,
        idea_text: str,
        target_duration_seconds: int = 120,
        max_duration_seconds: int = 175,
        audience: Optional[dict] = None,
        seed: Optional[str] = None,
    ) -> Optional[str]:
        """Generate a complete script using AI.

        Args:
            title: The title for the script (Titulek)
            idea_text: The idea/concept text
            target_duration_seconds: Target duration in seconds (default: 120)
            max_duration_seconds: Maximum duration in seconds (default: 175)
            audience: Target audience dict with age_range, gender, country
            seed: Optional specific seed to use (if None, picks randomly from 500)

        Returns:
            Generated content text, or None if AI is unavailable

        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If AI is not available or generation fails
        """
        # Validate inputs
        if not title or not title.strip():
            raise ValueError("title cannot be empty")
        if not idea_text or not idea_text.strip():
            raise ValueError("idea_text cannot be empty")
        
        # Sanitize inputs
        title = _sanitize_text_input(title, max_length=500, field_name="title")
        idea_text = _sanitize_text_input(idea_text, max_length=10000, field_name="idea_text")
        
        # Validate duration parameters
        if target_duration_seconds <= 0:
            raise ValueError(f"target_duration_seconds must be positive, got: {target_duration_seconds}")
        if max_duration_seconds <= 0:
            raise ValueError(f"max_duration_seconds must be positive, got: {max_duration_seconds}")
        if target_duration_seconds > max_duration_seconds:
            raise ValueError(
                f"target_duration_seconds ({target_duration_seconds}) cannot exceed "
                f"max_duration_seconds ({max_duration_seconds})"
            )
        
        # Validate audience structure if provided
        if audience is not None:
            if not isinstance(audience, dict):
                raise ValueError("audience must be a dictionary")
            # Optionally validate audience fields
            valid_keys = {"age_range", "gender", "country"}
            invalid_keys = set(audience.keys()) - valid_keys
            if invalid_keys:
                logger.warning(f"Audience contains unexpected keys: {invalid_keys}")
        
        # Check AI availability
        if not self.available:
            error_msg = (
                f"AI content generation is not available. "
                f"Please ensure Ollama is running with model '{self.config.model}' at {self.config.api_base}"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        # Set default audience if not provided
        if audience is None:
            audience = {
                "age_range": "13-23",
                "gender": "Female",
                "country": "United States",
            }

        # Validate or pick seed
        if seed is not None:
            seed = _sanitize_text_input(seed, max_length=100, field_name="seed")
        else:
            # Pick one seed from 500 variations
            seed = get_random_seed()
        
        logger.info(f"Using seed: {seed}")

        prompt = self._create_content_prompt(
            title=title,
            idea_text=idea_text,
            seed=seed,
            target_duration=target_duration_seconds,
            max_duration=max_duration_seconds,
            audience=audience,
        )

        try:
            response = self._call_ollama(prompt)
            script = self._extract_content_text(response)
            
            # Validate generated content
            if not script or not script.strip():
                raise RuntimeError("AI generated empty content")
            
            logger.info(f"AI content generation successful for '{title}'")
            return script
        except requests.exceptions.Timeout as e:
            error_msg = f"AI content generation timed out after {self.config.timeout}s: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Failed to connect to Ollama at {self.config.api_base}: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"AI content generation request failed: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"AI content generation failed: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _create_content_prompt(
        self, title: str, idea_text: str, seed: str, target_duration: int, max_duration: int, audience: dict
    ) -> str:
        """Create optimized prompt for Qwen3:32b model.

        Optimized for Qwen3's strengths:
        - Clear role definition and instruction following
        - Structured constraints and requirements
        - Explicit output format specification
        - Natural language generation focus

        Args:
            title: Content title
            idea_text: Idea/concept text
            seed: Creative direction seed (used symbolically/thematically)
            target_duration: Target duration in seconds (default: 120)
            max_duration: Maximum duration in seconds (default: 175)
            audience: Target audience dict

        Returns:
            Optimized prompt for Qwen3:32b model
        """
        # Calculate approximate word count (2.5 words per second for narration)
        target_words = int(target_duration * 2.5)
        max_words = int(max_duration * 2.5)

        # Optimized prompt structure for Qwen3:32b
        prompt = f"""You are an expert video content writer specializing in engaging short-form content for {audience.get('gender', 'Female')} audiences aged {audience.get('age_range', '13-23')} in {audience.get('country', 'United States')}.

# Your Task
Write compelling video narration for: "{title}"

# Context
{idea_text}

# Creative Direction
Draw subtle inspiration from: {seed}
(Use this thematically or symbolically—do not mention it directly)

# Requirements
**Structure**: Begin with an attention-grabbing hook, deliver the core message clearly, end with a natural call-to-action.

**Length**: {target_words} words (target) | {max_words} words (maximum)

**Style Guidelines**:
- First sentence must create immediate curiosity or tension
- Use conversational, engaging language throughout
- Maintain consistent energy and pacing
- Make every word count—no filler
- End with a clear action for viewers

**Critical Constraints**:
- Write ONLY the narration text—no labels, headings, or meta-commentary
- Never mention "hook", "CTA", "script", or structural elements
- Never explain what you're doing—just deliver the content
- Stay within word limit

# Output Format
Write the complete narration as a single, flowing text. Start immediately with the hook."""

        return prompt

    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API to generate content.
        
        Args:
            prompt: The prompt to send to the AI
            
        Returns:
            The AI-generated response text
            
        Raises:
            RuntimeError: If the API call fails
        """
        logger.debug(f"Calling Ollama API at {self.config.api_base}")
        logger.debug(f"Model: {self.config.model}, Temperature: {self.config.temperature}")
        
        try:
            response = requests.post(
                f"{self.config.api_base}/api/generate",
                json={
                    "model": self.config.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.config.temperature,
                        "num_predict": self.config.max_tokens,
                    },
                },
                timeout=self.config.timeout,
            )

            response.raise_for_status()
            result = response.json()
            generated_text = result.get("response", "").strip()
            
            if not generated_text:
                logger.error("Ollama returned empty response")
                raise RuntimeError("Ollama returned empty response")
            
            logger.debug(f"Generated {len(generated_text)} characters")
            return generated_text

        except requests.exceptions.Timeout:
            logger.error(f"Ollama API call timed out after {self.config.timeout}s")
            raise RuntimeError(f"Ollama API timed out after {self.config.timeout} seconds")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            raise RuntimeError(f"Failed to connect to Ollama at {self.config.api_base}: {e}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"Ollama API returned error: {e}")
            raise RuntimeError(f"Ollama API error: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API call failed: {e}")
            raise RuntimeError(f"Failed to generate AI script: {e}")
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to parse Ollama response: {e}")
            raise RuntimeError(f"Invalid response from Ollama: {e}")

    def _extract_content_text(self, response: str) -> str:
        """Extract content text from AI response.
        
        Args:
            response: Raw response from AI
            
        Returns:
            Cleaned content text
            
        Raises:
            RuntimeError: If response is empty or invalid
        """
        if not response:
            raise RuntimeError("AI response is empty")
        
        cleaned = response.strip()
        
        if not cleaned:
            raise RuntimeError("AI response contains only whitespace")

        # Remove common prefixes
        prefixes = ["SCRIPT:", "Content:", "script:", "Here is the script:", "Output:", "Narration:"]
        for prefix in prefixes:
            if cleaned.lower().startswith(prefix.lower()):
                cleaned = cleaned[len(prefix) :].strip()

        # Remove quotes if wrapped
        if (cleaned.startswith('"') and cleaned.endswith('"')) or (
            cleaned.startswith("'") and cleaned.endswith("'")
        ):
            cleaned = cleaned[1:-1].strip()
        
        # Final validation
        if not cleaned:
            raise RuntimeError("AI response is empty after cleaning")
        
        # Check for minimum reasonable length (at least 50 characters)
        if len(cleaned) < 50:
            logger.warning(f"Generated content is very short: {len(cleaned)} characters")

        return cleaned


def generate_content(
    title: str,
    idea_text: str,
    target_duration_seconds: int = 120,
    max_duration_seconds: int = 175,
    audience: Optional[dict] = None,
    seed: Optional[str] = None,
    config: Optional[AIContentGeneratorConfig] = None,
) -> str:
    """Convenience function to generate an AI-powered script.

    Args:
        title: Content title (Titulek)
        idea_text: Idea/concept text
        target_duration_seconds: Target duration in seconds (default: 120)
        max_duration_seconds: Maximum duration in seconds (default: 175)
        audience: Target audience dict with age_range, gender, country
        seed: Optional specific seed (if None, picks randomly from 504)
        config: Optional AI configuration

    Returns:
        Generated content text

    Raises:
        RuntimeError: If AI is not available or generation fails

    Example:
        >>> script = generate_content(
        ...     title="The Mystery of the Abandoned House",
        ...     idea_text="A girl discovers a time-loop in an abandoned house...",
        ...     target_duration_seconds=120,
        ...     audience={"age_range": "13-23", "gender": "Female", "country": "United States"}
        ... )
        >>> print(script)
    """
    generator = AIContentGenerator(config=config)
    return generator.generate_content(
        title=title,
        idea_text=idea_text,
        target_duration_seconds=target_duration_seconds,
        max_duration_seconds=max_duration_seconds,
        audience=audience,
        seed=seed,
    )


__all__ = [
    "AIContentGenerator",
    "AIContentGeneratorConfig",
    "generate_content",
    "get_random_seed",
    "get_seed_by_index",
    "SEED_VARIATIONS",
]
