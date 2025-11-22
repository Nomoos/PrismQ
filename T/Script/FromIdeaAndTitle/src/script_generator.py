"""Script Generator for creating v1 scripts from ideas and titles.

This module implements the script generation logic for MVP-003:
- Takes Idea object and Title v1 as input
- Generates structured script with intro, body, and conclusion
- Optimizes for platform requirements (YouTube shorts < 180s)
- Maintains coherence with title promises and idea intent
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import string
import sys
import os

# Add parent directories to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
idea_model_path = os.path.join(parent_dir, 'Idea', 'Model', 'src')
sys.path.insert(0, idea_model_path)

try:
    from idea import Idea, ContentGenre
except ImportError:
    # Fallback for testing or development
    pass


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
        version: Version number (always "v1" for initial)
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
    version: str = "v1"
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
    """
    
    platform_target: PlatformTarget = PlatformTarget.YOUTUBE_MEDIUM
    target_duration_seconds: int = 90
    structure_type: ScriptStructure = ScriptStructure.HOOK_DELIVER_CTA
    words_per_second: float = 2.5  # Average speaking rate
    include_cta: bool = True
    tone: ScriptTone = ScriptTone.ENGAGING


class ScriptGenerator:
    """Generate initial script drafts (v1) from ideas and titles.
    
    This class implements the MVP-003 functionality to create structured
    scripts from an Idea object and a title variant.
    """
    
    def __init__(self, config: Optional[ScriptGeneratorConfig] = None):
        """Initialize ScriptGenerator with configuration.
        
        Args:
            config: Optional generation configuration
        """
        self.config = config or ScriptGeneratorConfig()
    
    def generate_script_v1(
        self,
        idea: 'Idea',
        title: str,
        script_id: Optional[str] = None,
        **kwargs
    ) -> ScriptV1:
        """Generate initial script (v1) from idea and title.
        
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
        
        # Generate script sections
        sections = self._generate_sections(idea, title, analysis, config)
        
        # Combine sections into full text
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
                    "tone": config.tone,
                    "target_duration": config.target_duration_seconds,
                    "words_per_second": config.words_per_second
                }
            },
            notes=f"Generated from idea '{getattr(idea, 'title', 'untitled')}' with title '{title}'"
        )
        
        return script
    
    def _apply_config_overrides(self, kwargs: Dict[str, Any]) -> ScriptGeneratorConfig:
        """Apply configuration overrides from kwargs."""
        config = ScriptGeneratorConfig(
            platform_target=kwargs.get('platform_target', self.config.platform_target),
            target_duration_seconds=kwargs.get('target_duration_seconds', self.config.target_duration_seconds),
            structure_type=kwargs.get('structure_type', self.config.structure_type),
            words_per_second=kwargs.get('words_per_second', self.config.words_per_second),
            include_cta=kwargs.get('include_cta', self.config.include_cta),
            tone=kwargs.get('tone', self.config.tone)
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
