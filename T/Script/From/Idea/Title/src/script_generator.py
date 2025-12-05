"""Script Generator for creating v1 scripts from ideas and titles.

This module implements the script generation logic for MVP-003:
- Takes Idea object and Title v1 as input
- Generates structured script with intro, body, and conclusion
- Optimizes for platform requirements (YouTube shorts < 180s)
- Maintains coherence with title promises and idea intent
- Supports AI-powered generation using Qwen2.5-14B-Instruct via Ollama
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import string
import sys
import os
import logging

logger = logging.getLogger(__name__)

# Add parent directories to path for imports
# Path: T/Script/From/Idea/Title/src/script_generator.py
# Up 6 levels to T/, then into Idea/Model/src
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))
idea_model_path = os.path.join(parent_dir, 'Idea', 'Model', 'src')
sys.path.insert(0, idea_model_path)

try:
    from idea import Idea, ContentGenre
except ImportError:
    # Fallback for testing or development
    pass

# Import AI script generator (lazy import to avoid circular dependency)
_ai_generator_module = None


def _get_ai_generator_module():
    """Lazy import of AI script generator module."""
    global _ai_generator_module
    if _ai_generator_module is None:
        try:
            from . import ai_script_generator as _ai_generator_module
        except ImportError:
            logger.warning("AI script generator module not available")
            _ai_generator_module = False
    return _ai_generator_module if _ai_generator_module else None


class ScriptStructure(Enum):
    """Script structure types."""
    
    THREE_ACT = "three_act"  # Introduction, Development, Conclusion
    HOOK_DELIVER_CTA = "hook_deliver_cta"  # Hook, Deliver, Call-to-Action
    PROBLEM_SOLUTION = "problem_solution"  # Problem, Investigation, Solution
    STORY = "story"  # Beginning, Middle, End


class PlatformTarget(Enum):
    """Target platforms for script optimization."""
    
    YOUTUBE_SHORT = "youtube_short"  # < 60 seconds
    YOUTUBE_MEDIUM = "youtube_medium"  # 60-180 seconds
    YOUTUBE_LONG = "youtube_long"  # > 180 seconds
    TIKTOK = "tiktok"  # < 60 seconds
    INSTAGRAM_REEL = "instagram_reel"  # < 90 seconds
    GENERAL = "general"  # No specific constraints


class ScriptTone(Enum):
    """Script tone options."""
    
    ENGAGING = "engaging"
    MYSTERIOUS = "mysterious"
    EDUCATIONAL = "educational"
    DRAMATIC = "dramatic"
    CONVERSATIONAL = "conversational"


# Common English stop words for keyword extraction
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", 
    "of", "with", "is", "are", "was", "were", "been", "be", "have", "has", 
    "had", "do", "does", "did", "will", "would", "could", "should", "may",
    "might", "can", "must", "shall"
}

# Tone detection keywords mapping
TONE_KEYWORDS = {
    "mysterious": ["mystery", "secrets", "hidden", "unknown"],
    "dramatic": ["shocking", "unbelievable", "terrifying"],
    "educational": ["how", "why", "what", "explained"]
}


@dataclass
class ScriptSection:
    """A section of the script."""
    
    section_type: str  # "introduction", "body", "conclusion"
    content: str
    estimated_duration_seconds: int
    purpose: str  # What this section aims to achieve
    notes: str = ""


@dataclass
class ScriptV1:
    """Initial script draft (version 1).
    
    Attributes:
        script_id: Unique identifier for this script
        idea_id: Reference to source Idea
        title: The title (v1) this script was generated from
        full_text: Complete script text
        sections: Breakdown into intro, body, conclusion
        total_duration_seconds: Estimated total duration
        structure_type: Type of structure used
        platform_target: Target platform
        metadata: Additional metadata
        created_at: Creation timestamp
        version: Version number (integer, 1 for initial draft)
        notes: Additional notes or context
    """
    
    script_id: str
    idea_id: str
    title: str
    full_text: str
    sections: List[ScriptSection]
    total_duration_seconds: int
    structure_type: ScriptStructure
    platform_target: PlatformTarget
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    version: int = 1
    notes: str = ""
    
    def get_section(self, section_type: str) -> Optional[ScriptSection]:
        """Get a specific section by type."""
        for section in self.sections:
            if section.section_type == section_type:
                return section
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "script_id": self.script_id,
            "idea_id": self.idea_id,
            "title": self.title,
            "full_text": self.full_text,
            "sections": [
                {
                    "section_type": s.section_type,
                    "content": s.content,
                    "estimated_duration_seconds": s.estimated_duration_seconds,
                    "purpose": s.purpose,
                    "notes": s.notes
                }
                for s in self.sections
            ],
            "total_duration_seconds": self.total_duration_seconds,
            "structure_type": self.structure_type.value,
            "platform_target": self.platform_target.value,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "version": self.version,
            "notes": self.notes
        }


@dataclass
class ScriptGeneratorConfig:
    """Configuration for script generation.
    
    Attributes:
        platform_target: Target platform for optimization
        target_duration_seconds: Target script duration
        structure_type: Script structure to use
        words_per_second: Narration speed (for duration estimation)
        include_cta: Whether to include call-to-action
        tone: Script tone (engaging, mysterious, educational, etc.)
        use_ai: Whether to use AI-powered generation (default: True)
        ai_model: AI model to use for generation (default: Qwen2.5-14B-Instruct)
        ai_api_base: Base URL for Ollama API
        ai_temperature: AI generation temperature (0.0-2.0)
        ai_timeout: AI request timeout in seconds
    """
    
    platform_target: PlatformTarget = PlatformTarget.YOUTUBE_MEDIUM
    target_duration_seconds: int = 90
    structure_type: ScriptStructure = ScriptStructure.HOOK_DELIVER_CTA
    words_per_second: float = 2.5  # Average speaking rate
    include_cta: bool = True
    tone: ScriptTone = ScriptTone.ENGAGING
    # AI generation settings
    use_ai: bool = True
    ai_model: str = "qwen2.5:14b-instruct"
    ai_api_base: str = "http://localhost:11434"
    ai_temperature: float = 0.7
    ai_timeout: int = 120


class ScriptGenerator:
    """Generate initial script drafts (v1) from ideas and titles.
    
    This class implements the MVP-003 functionality to create structured
    scripts from an Idea object and a title variant.
    
    The generator supports AI-powered script generation using Qwen2.5-14B-Instruct
    via Ollama, with automatic fallback to rule-based generation when AI is unavailable.
    """
    
    def __init__(self, config: Optional[ScriptGeneratorConfig] = None):
        """Initialize ScriptGenerator with configuration.
        
        Args:
            config: Optional generation configuration
        """
        self.config = config or ScriptGeneratorConfig()
        self._ai_generator = None
        self._ai_available = False
        self._init_ai_generator()
    
    def _init_ai_generator(self):
        """Initialize AI generator if available and enabled."""
        if not self.config.use_ai:
            logger.info("AI generation disabled in config")
            return
        
        ai_module = _get_ai_generator_module()
        if ai_module is None:
            logger.info("AI script generator module not available")
            return
        
        try:
            ai_config = ai_module.AIScriptGeneratorConfig(
                model=self.config.ai_model,
                api_base=self.config.ai_api_base,
                temperature=self.config.ai_temperature,
                timeout=self.config.ai_timeout,
                enable_ai=True
            )
            self._ai_generator = ai_module.AIScriptGenerator(config=ai_config)
            self._ai_available = self._ai_generator.is_available()
            
            if self._ai_available:
                logger.info(f"AI script generation enabled with model: {self.config.ai_model}")
            else:
                logger.info("AI script generator initialized but Ollama not available")
        except Exception as e:
            logger.warning(f"Failed to initialize AI generator: {e}")
            self._ai_generator = None
            self._ai_available = False
    
    def is_ai_available(self) -> bool:
        """Check if AI-powered script generation is available.
        
        Returns:
            True if AI generation is available, False otherwise
        """
        return self._ai_available
    
    def generate_script_v1(
        self,
        idea: 'Idea',
        title: str,
        script_id: Optional[str] = None,
        **kwargs
    ) -> ScriptV1:
        """Generate initial script (v1) from idea and title.
        
        This method attempts AI-powered generation using Qwen2.5-14B-Instruct
        if available, with automatic fallback to rule-based generation.
        
        Args:
            idea: Source Idea object
            title: Title variant (v1) to use
            script_id: Optional script ID (generated if not provided)
            **kwargs: Additional configuration overrides
            
        Returns:
            ScriptV1 object with structured script
            
        Raises:
            ValueError: If idea or title is invalid
        """
        if not idea:
            raise ValueError("Idea cannot be None")
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")
        
        # Override config with kwargs
        config = self._apply_config_overrides(kwargs)
        
        # Generate script ID if not provided
        if not script_id:
            script_id = self._generate_script_id(idea, title)
        
        # Analyze idea and title to extract key elements
        analysis = self._analyze_inputs(idea, title)
        
        # Try AI-powered generation first
        ai_generated = False
        full_text = None
        sections = None
        
        if self._ai_available and config.use_ai:
            logger.info(f"Attempting AI-powered script generation for '{title}'")
            full_text, sections = self._generate_with_ai(idea, title, analysis, config)
            if full_text is not None:
                ai_generated = True
                logger.info("AI script generation successful")
            else:
                logger.info("AI generation failed, falling back to rule-based generation")
        
        # Fallback to rule-based generation
        if full_text is None:
            sections = self._generate_sections(idea, title, analysis, config)
            full_text = self._assemble_full_text(sections)
        
        # Calculate total duration
        total_duration = sum(s.estimated_duration_seconds for s in sections)
        
        # Create ScriptV1 object
        script = ScriptV1(
            script_id=script_id,
            idea_id=getattr(idea, 'id', 'unknown'),
            title=title,
            full_text=full_text,
            sections=sections,
            total_duration_seconds=total_duration,
            structure_type=config.structure_type,
            platform_target=config.platform_target,
            metadata={
                "idea_concept": idea.concept if hasattr(idea, 'concept') else "",
                "idea_genre": idea.genre.value if hasattr(idea, 'genre') else "unknown",
                "target_audience": getattr(idea, 'target_audience', 'general'),
                "generation_config": {
                    "tone": config.tone.value if hasattr(config.tone, 'value') else str(config.tone),
                    "target_duration": config.target_duration_seconds,
                    "words_per_second": config.words_per_second,
                    "use_ai": config.use_ai,
                    "ai_model": config.ai_model
                },
                "ai_generated": ai_generated
            },
            notes=f"Generated from idea '{getattr(idea, 'title', 'untitled')}' with title '{title}'"
                  f"{' (AI-powered)' if ai_generated else ' (rule-based)'}"
        )
        
        return script
    
    def _generate_with_ai(
        self,
        idea: 'Idea',
        title: str,
        analysis: Dict[str, Any],
        config: ScriptGeneratorConfig
    ) -> tuple:
        """Generate script content using AI.
        
        Args:
            idea: Source Idea object
            title: Script title
            analysis: Pre-analyzed idea and title data
            config: Generation configuration
        
        Returns:
            Tuple of (full_text, sections) if successful, (None, None) otherwise
        """
        if not self._ai_generator:
            return None, None
        
        try:
            # Convert idea to dictionary for AI generation
            idea_data = {
                "concept": getattr(idea, 'concept', ''),
                "synopsis": getattr(idea, 'synopsis', ''),
                "hook": getattr(idea, 'hook', ''),
                "premise": getattr(idea, 'premise', ''),
                "genre": idea.genre.value if hasattr(idea, 'genre') and hasattr(idea.genre, 'value') else 'general',
                "target_audience": getattr(idea, 'target_audience', 'general audience'),
                "themes": getattr(idea, 'themes', []),
                "keywords": getattr(idea, 'keywords', [])
            }
            
            # Get platform string
            platform = config.platform_target.value if hasattr(config.platform_target, 'value') else str(config.platform_target)
            
            # Get tone string
            tone = config.tone.value if hasattr(config.tone, 'value') else str(config.tone)
            
            # Generate full script using AI
            full_text = self._ai_generator.generate_full_script(
                idea_data=idea_data,
                title=title,
                target_duration_seconds=config.target_duration_seconds,
                platform=platform,
                tone=tone
            )
            
            if full_text is None:
                return None, None
            
            # Create sections from AI-generated text
            sections = self._create_sections_from_ai_text(full_text, config)
            
            return full_text, sections
            
        except Exception as e:
            logger.error(f"AI script generation error: {e}")
            return None, None
    
    def _create_sections_from_ai_text(
        self,
        full_text: str,
        config: ScriptGeneratorConfig
    ) -> List[ScriptSection]:
        """Create section objects from AI-generated text.
        
        Since AI generates a cohesive script, we estimate section boundaries
        based on the target duration ratios.
        
        Args:
            full_text: AI-generated script text
            config: Generation configuration
        
        Returns:
            List of ScriptSection objects
        """
        # Calculate section durations based on structure type
        if config.structure_type == ScriptStructure.HOOK_DELIVER_CTA:
            intro_ratio, body_ratio, conclusion_ratio = 0.15, 0.70, 0.15
        elif config.structure_type == ScriptStructure.THREE_ACT:
            intro_ratio, body_ratio, conclusion_ratio = 0.25, 0.50, 0.25
        elif config.structure_type == ScriptStructure.PROBLEM_SOLUTION:
            intro_ratio, body_ratio, conclusion_ratio = 0.30, 0.50, 0.20
        else:
            intro_ratio, body_ratio, conclusion_ratio = 0.20, 0.60, 0.20
        
        total_words = len(full_text.split())
        
        # Split text roughly by word count
        words = full_text.split()
        intro_words = int(total_words * intro_ratio)
        body_words = int(total_words * body_ratio)
        
        intro_text = ' '.join(words[:intro_words])
        body_text = ' '.join(words[intro_words:intro_words + body_words])
        conclusion_text = ' '.join(words[intro_words + body_words:])
        
        # Calculate durations
        intro_duration = int(config.target_duration_seconds * intro_ratio)
        body_duration = int(config.target_duration_seconds * body_ratio)
        conclusion_duration = int(config.target_duration_seconds * conclusion_ratio)
        
        sections = [
            ScriptSection(
                section_type="introduction",
                content=intro_text,
                estimated_duration_seconds=intro_duration,
                purpose="AI-generated hook to grab attention",
                notes="Generated with Qwen2.5-14B-Instruct"
            ),
            ScriptSection(
                section_type="body",
                content=body_text,
                estimated_duration_seconds=body_duration,
                purpose="AI-generated main content",
                notes="Generated with Qwen2.5-14B-Instruct"
            ),
            ScriptSection(
                section_type="conclusion",
                content=conclusion_text,
                estimated_duration_seconds=conclusion_duration,
                purpose="AI-generated conclusion",
                notes="Generated with Qwen2.5-14B-Instruct"
            )
        ]
        
        return sections
    
    def _apply_config_overrides(self, kwargs: Dict[str, Any]) -> ScriptGeneratorConfig:
        """Apply configuration overrides from kwargs."""
        config = ScriptGeneratorConfig(
            platform_target=kwargs.get('platform_target', self.config.platform_target),
            target_duration_seconds=kwargs.get('target_duration_seconds', self.config.target_duration_seconds),
            structure_type=kwargs.get('structure_type', self.config.structure_type),
            words_per_second=kwargs.get('words_per_second', self.config.words_per_second),
            include_cta=kwargs.get('include_cta', self.config.include_cta),
            tone=kwargs.get('tone', self.config.tone),
            # AI settings
            use_ai=kwargs.get('use_ai', self.config.use_ai),
            ai_model=kwargs.get('ai_model', self.config.ai_model),
            ai_api_base=kwargs.get('ai_api_base', self.config.ai_api_base),
            ai_temperature=kwargs.get('ai_temperature', self.config.ai_temperature),
            ai_timeout=kwargs.get('ai_timeout', self.config.ai_timeout)
        )
        return config
    
    def _generate_script_id(self, idea: 'Idea', title: str) -> str:
        """Generate a unique script ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        idea_id = getattr(idea, 'id', 'unknown')
        return f"script_v1_{idea_id}_{timestamp}"
    
    def _analyze_inputs(self, idea: 'Idea', title: str) -> Dict[str, Any]:
        """Analyze idea and title to extract key elements.
        
        Args:
            idea: Source Idea object
            title: Title to analyze
            
        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "title_keywords": self._extract_keywords(title),
            "title_tone": self._detect_tone(title),
            "idea_themes": getattr(idea, 'themes', []),
            "idea_keywords": getattr(idea, 'keywords', []),
            "core_concept": getattr(idea, 'concept', ''),
            "hook": getattr(idea, 'hook', ''),
            "premise": getattr(idea, 'premise', ''),
            "synopsis": getattr(idea, 'synopsis', ''),
        }
        return analysis
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Simple keyword extraction (in production, would use NLP)
        words = text.lower().split()
        # Filter out common words and punctuation
        keywords = [w.strip(string.punctuation) for w in words if w not in STOP_WORDS and len(w) > 3]
        return keywords[:5]
    
    def _detect_tone(self, title: str) -> str:
        """Detect tone from title."""
        title_lower = title.lower()
        
        # Simple tone detection based on keywords
        for tone, keywords in TONE_KEYWORDS.items():
            if any(word in title_lower for word in keywords):
                return tone
        
        return "engaging"
    
    def _generate_sections(
        self,
        idea: 'Idea',
        title: str,
        analysis: Dict[str, Any],
        config: ScriptGeneratorConfig
    ) -> List[ScriptSection]:
        """Generate script sections based on structure type."""
        
        if config.structure_type == ScriptStructure.HOOK_DELIVER_CTA:
            return self._generate_hook_deliver_cta(idea, title, analysis, config)
        elif config.structure_type == ScriptStructure.THREE_ACT:
            return self._generate_three_act(idea, title, analysis, config)
        elif config.structure_type == ScriptStructure.PROBLEM_SOLUTION:
            return self._generate_problem_solution(idea, title, analysis, config)
        elif config.structure_type == ScriptStructure.STORY:
            return self._generate_story(idea, title, analysis, config)
        else:
            return self._generate_hook_deliver_cta(idea, title, analysis, config)
    
    def _generate_hook_deliver_cta(
        self,
        idea: 'Idea',
        title: str,
        analysis: Dict[str, Any],
        config: ScriptGeneratorConfig
    ) -> List[ScriptSection]:
        """Generate hook-deliver-cta structure."""
        
        # Calculate section durations (percentages of target)
        hook_duration = int(config.target_duration_seconds * 0.15)  # 15%
        deliver_duration = int(config.target_duration_seconds * 0.70)  # 70%
        cta_duration = int(config.target_duration_seconds * 0.15)  # 15%
        
        sections = []
        
        # Hook/Introduction (10-15 seconds)
        hook_content = self._generate_hook_content(idea, title, analysis, hook_duration, config)
        sections.append(ScriptSection(
            section_type="introduction",
            content=hook_content,
            estimated_duration_seconds=hook_duration,
            purpose="Grab attention and set up intrigue",
            notes="Opening hook to engage viewer immediately"
        ))
        
        # Main Content/Delivery (60-150 seconds)
        main_content = self._generate_main_content(idea, title, analysis, deliver_duration, config)
        sections.append(ScriptSection(
            section_type="body",
            content=main_content,
            estimated_duration_seconds=deliver_duration,
            purpose="Deliver on title promise and develop content",
            notes="Main narrative delivering value"
        ))
        
        # Conclusion/CTA (10-20 seconds)
        if config.include_cta:
            conclusion_content = self._generate_conclusion_cta(idea, title, analysis, cta_duration, config)
            sections.append(ScriptSection(
                section_type="conclusion",
                content=conclusion_content,
                estimated_duration_seconds=cta_duration,
                purpose="Provide satisfying ending and call to action",
                notes="Memorable conclusion with optional CTA"
            ))
        
        return sections
    
    def _generate_three_act(
        self,
        idea: 'Idea',
        title: str,
        analysis: Dict[str, Any],
        config: ScriptGeneratorConfig
    ) -> List[ScriptSection]:
        """Generate three-act structure."""
        
        # Calculate section durations
        act1_duration = int(config.target_duration_seconds * 0.25)  # 25%
        act2_duration = int(config.target_duration_seconds * 0.50)  # 50%
        act3_duration = int(config.target_duration_seconds * 0.25)  # 25%
        
        sections = []
        
        # Act 1: Setup
        act1_content = self._generate_hook_content(idea, title, analysis, act1_duration, config)
        sections.append(ScriptSection(
            section_type="introduction",
            content=act1_content,
            estimated_duration_seconds=act1_duration,
            purpose="Setup and establish context",
            notes="Act 1: Introduction"
        ))
        
        # Act 2: Development
        act2_content = self._generate_main_content(idea, title, analysis, act2_duration, config)
        sections.append(ScriptSection(
            section_type="body",
            content=act2_content,
            estimated_duration_seconds=act2_duration,
            purpose="Develop narrative and build tension",
            notes="Act 2: Development"
        ))
        
        # Act 3: Resolution
        act3_content = self._generate_conclusion_cta(idea, title, analysis, act3_duration, config)
        sections.append(ScriptSection(
            section_type="conclusion",
            content=act3_content,
            estimated_duration_seconds=act3_duration,
            purpose="Resolve and conclude",
            notes="Act 3: Resolution"
        ))
        
        return sections
    
    def _generate_problem_solution(
        self,
        idea: 'Idea',
        title: str,
        analysis: Dict[str, Any],
        config: ScriptGeneratorConfig
    ) -> List[ScriptSection]:
        """Generate problem-solution structure."""
        
        problem_duration = int(config.target_duration_seconds * 0.30)
        investigation_duration = int(config.target_duration_seconds * 0.50)
        solution_duration = int(config.target_duration_seconds * 0.20)
        
        sections = []
        
        # Problem
        problem_content = self._generate_problem_content(idea, title, analysis, problem_duration, config)
        sections.append(ScriptSection(
            section_type="introduction",
            content=problem_content,
            estimated_duration_seconds=problem_duration,
            purpose="Establish the problem or question",
            notes="Problem statement"
        ))
        
        # Investigation
        investigation_content = self._generate_main_content(idea, title, analysis, investigation_duration, config)
        sections.append(ScriptSection(
            section_type="body",
            content=investigation_content,
            estimated_duration_seconds=investigation_duration,
            purpose="Explore the problem and investigate",
            notes="Investigation and exploration"
        ))
        
        # Solution
        solution_content = self._generate_solution_content(idea, title, analysis, solution_duration, config)
        sections.append(ScriptSection(
            section_type="conclusion",
            content=solution_content,
            estimated_duration_seconds=solution_duration,
            purpose="Present solution or conclusion",
            notes="Solution and resolution"
        ))
        
        return sections
    
    def _generate_story(
        self,
        idea: 'Idea',
        title: str,
        analysis: Dict[str, Any],
        config: ScriptGeneratorConfig
    ) -> List[ScriptSection]:
        """Generate story structure (beginning, middle, end)."""
        # Similar to three-act but with story focus
        return self._generate_three_act(idea, title, analysis, config)
    
    def _generate_hook_content(
        self,
        idea: 'Idea',
        title: str,
        analysis: Dict[str, Any],
        duration: int,
        config: ScriptGeneratorConfig
    ) -> str:
        """Generate hook/introduction content.
        
        In production, this would use AI to generate compelling hooks.
        For MVP, we create structured content based on idea and title.
        """
        hook = analysis.get('hook', '')
        premise = analysis.get('premise', '')
        
        # Calculate target word count
        target_words = int(duration * config.words_per_second)
        
        # Build hook content
        hook_lines = []
        
        # Use existing hook if available
        if hook:
            hook_lines.append(hook)
        else:
            # Generate hook from title
            hook_lines.append(f"What if I told you about {title.lower()}?")
        
        # Add intrigue
        if premise:
            hook_lines.append(premise[:100] + "...")
        
        hook_content = " ".join(hook_lines)
        
        # Adjust length to target
        words = hook_content.split()
        if len(words) > target_words:
            hook_content = " ".join(words[:target_words]) + "..."
        
        return hook_content
    
    def _generate_main_content(
        self,
        idea: 'Idea',
        title: str,
        analysis: Dict[str, Any],
        duration: int,
        config: ScriptGeneratorConfig
    ) -> str:
        """Generate main content/body.
        
        In production, this would use AI to generate detailed content.
        For MVP, we create structured content based on idea elements.
        """
        synopsis = analysis.get('synopsis', '')
        core_concept = analysis.get('core_concept', '')
        
        # Calculate target word count
        target_words = int(duration * config.words_per_second)
        
        # Build main content
        content_lines = []
        
        # Use synopsis if available
        if synopsis:
            content_lines.append(synopsis)
        
        # Add core concept development
        if core_concept:
            content_lines.append(f"\n\nAt its core, this is about {core_concept.lower()}.")
        
        # Add theme exploration
        themes = analysis.get('idea_themes', [])
        if themes:
            content_lines.append(f"\n\nThis touches on themes of {', '.join(themes)}.")
        
        # Add detailed exploration (placeholder for AI generation)
        content_lines.append("\n\nLet me walk you through the key aspects.")
        content_lines.append("First, we need to understand the context.")
        content_lines.append("Then, we can explore the implications.")
        content_lines.append("Finally, we'll see how this all connects.")
        
        main_content = " ".join(content_lines)
        
        # Adjust length to target
        words = main_content.split()
        if len(words) > target_words:
            main_content = " ".join(words[:target_words])
        elif len(words) < target_words * 0.8:
            # Pad if too short (in production, AI would generate more)
            padding = " This is a fascinating topic that deserves deeper exploration."
            word_count = len(words)
            min_words = int(target_words * 0.8)
            while word_count < min_words:
                main_content += padding
                word_count += len(padding.split())
        
        return main_content
    
    def _generate_conclusion_cta(
        self,
        idea: 'Idea',
        title: str,
        analysis: Dict[str, Any],
        duration: int,
        config: ScriptGeneratorConfig
    ) -> str:
        """Generate conclusion with call-to-action."""
        
        target_words = int(duration * config.words_per_second)
        
        conclusion_lines = []
        
        # Wrap up main point
        conclusion_lines.append(f"So that's the story behind {title.lower()}.")
        
        # Key takeaway
        conclusion_lines.append("The key thing to remember is how interconnected everything is.")
        
        # CTA if enabled
        if config.include_cta:
            conclusion_lines.append("If you found this interesting, let me know in the comments.")
            conclusion_lines.append("And don't forget to subscribe for more content like this.")
        
        conclusion = " ".join(conclusion_lines)
        
        # Adjust length
        words = conclusion.split()
        if len(words) > target_words:
            conclusion = " ".join(words[:target_words])
        
        return conclusion
    
    def _generate_problem_content(
        self,
        idea: 'Idea',
        title: str,
        analysis: Dict[str, Any],
        duration: int,
        config: ScriptGeneratorConfig
    ) -> str:
        """Generate problem statement content."""
        target_words = int(duration * config.words_per_second)
        
        problem_lines = []
        problem_lines.append(f"There's a question that many people ask: {title.lower()}?")
        problem_lines.append("This isn't just a simple curiosity. It's a complex problem that affects many people.")
        
        premise = analysis.get('premise', '')
        if premise:
            problem_lines.append(premise)
        
        problem = " ".join(problem_lines)
        words = problem.split()
        if len(words) > target_words:
            problem = " ".join(words[:target_words])
        
        return problem
    
    def _generate_solution_content(
        self,
        idea: 'Idea',
        title: str,
        analysis: Dict[str, Any],
        duration: int,
        config: ScriptGeneratorConfig
    ) -> str:
        """Generate solution content."""
        target_words = int(duration * config.words_per_second)
        
        solution_lines = []
        solution_lines.append("After examining all the evidence, the answer becomes clear.")
        solution_lines.append(f"The solution to {title.lower()} lies in understanding the bigger picture.")
        
        if config.include_cta:
            solution_lines.append("What do you think? Share your thoughts below.")
        
        solution = " ".join(solution_lines)
        words = solution.split()
        if len(words) > target_words:
            solution = " ".join(words[:target_words])
        
        return solution
    
    def _assemble_full_text(self, sections: List[ScriptSection]) -> str:
        """Assemble full script text from sections."""
        return "\n\n".join(section.content for section in sections)


__all__ = ["ScriptGenerator", "ScriptGeneratorConfig", "ScriptV1", "ScriptSection", "ScriptStructure", "PlatformTarget", "ScriptTone"]
