"""AI-Powered Content Generator using Qwen3:30b via Ollama.

This module provides AI-powered content generation for the PrismQ.T.Content.From.Idea.Title
workflow using the Qwen3:30b model.

ALL generation goes through local AI models. No fallback to rule-based generation.

Input to AI:
    - Title (Titulek)
    - Idea text
    - One seed variation (randomly picked from 500 predefined variations)

Workflow Position:
    Stage: PrismQ.T.Content.From.Idea.Title
    Input: Title + Idea + Seed → AI Generation → Output: Content v1

Prompts are stored as separate text files in _meta/prompts/ for easier
maintenance and editing.
"""

import logging
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)


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
            seed: Optional specific seed to use (if None, picks randomly from 504)

        Returns:
            Generated content text, or None if AI is unavailable

        Raises:
            RuntimeError: If AI is not available
        """
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

        # Pick one seed from 504 variations
        selected_seed = seed if seed else get_random_seed()
        logger.info(f"Using seed: {selected_seed}")

        prompt = self._create_content_prompt(
            title=title,
            idea_text=idea_text,
            seed=selected_seed,
            target_duration=target_duration_seconds,
            max_duration=max_duration_seconds,
            audience=audience,
        )

        try:
            response = self._call_ollama(prompt)
            script = self._extract_content_text(response)
            logger.info(f"AI content generation successful for '{title}'")
            return script
        except Exception as e:
            error_msg = f"AI content generation failed: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _create_content_prompt(
        self, title: str, idea_text: str, seed: str, target_duration: int, max_duration: int, audience: dict
    ) -> str:
        """Create prompt for content generation using updated structure for local models.

        Input:
        - Title (Titulek)
        - Idea text
        - Seed (one picked from 504 variations)
        - Audience (age_range, gender, country)

        Args:
            title: Content title
            idea_text: Idea/concept text
            seed: Creative direction seed (used symbolically/thematically)
            target_duration: Target duration in seconds (default: 120)
            max_duration: Maximum duration in seconds (default: 175)
            audience: Target audience dict

        Returns:
            Engineered prompt for local AI model
        """
        # Calculate approximate word count (2.5 words per second for narration)
        target_words = int(target_duration * 2.5)
        max_words = int(max_duration * 2.5)

        # Build the optimized prompt for local models
        prompt = f"""SYSTEM INSTRUCTION:
You are a professional video content writer.
Follow instructions exactly. Do not add extra sections or explanations.

TASK:
Generate a video content.

INPUTS:
TITLE: {title}
IDEA: {idea_text}
INSPIRATION SEED: {seed} (Single word used only as creative inspiration)

TARGET AUDIENCE:
- Age: {audience.get('age_range', '13-23')}
- Gender: {audience.get('gender', 'Female')}
- Country: {audience.get('country', 'United States')}

REQUIREMENTS:
1. Hook must strongly capture attention within the first 5 seconds.
2. Deliver the main idea clearly and coherently.
3. End with a clear and natural call-to-action.
4. Maintain consistent engaging tone throughout.
5. Use the inspiration seed subtly (symbolic or thematic, not literal repetition).
6. Target length: approximately {target_words} words (for {target_duration} seconds).
7. Maximum length: {max_words} words ({max_duration} seconds).

OUTPUT RULES:
- Output ONLY the content text.
- No headings, no labels, no explanations.
- Do not mention the word "hook", "CTA", or any structure explicitly.
- Do not mention that this is a script.

The first sentence must create immediate curiosity or tension."""

        return prompt

    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API to generate content."""
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
            return result.get("response", "").strip()

        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API call failed: {e}")
            raise RuntimeError(f"Failed to generate AI script: {e}")

    def _extract_content_text(self, response: str) -> str:
        """Extract content text from AI response."""
        cleaned = response.strip()

        # Remove common prefixes
        prefixes = ["SCRIPT:", "Content:", "script:", "Here is the script:", "Output:", "Narration:"]
        for prefix in prefixes:
            if cleaned.lower().startswith(prefix.lower()):
                cleaned = cleaned[len(prefix) :].strip()

        # Remove quotes if wrapped
        if (cleaned.startswith('"') and cleaned.endswith('"')) or (
            cleaned.startswith("'") and cleaned.endswith("'")
        ):
            cleaned = cleaned[1:-1]

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
