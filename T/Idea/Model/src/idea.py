"""Idea model for PrismQ content creation.

This module defines the core Idea data model representing a distilled/fused
concept derived from one or more IdeaInspiration instances. Idea serves as
the foundation for creative content generation in the PrismQ workflow.

The Idea model maintains an M:N (many-to-many) relationship with IdeaInspiration,
allowing multiple inspirations to be blended into a single cohesive concept that
serves as the seed for original stories, scripts, and content.

Workflow Position:
    IdeaInspiration → Idea → Script → Proofreading → Publishing
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# Translation constants
CZECH_TRANSLATION_NOTE = (
    "\n\n[Poznámka: Pro produkční překlad použijte StoryTranslation model s AI překladačem]"
)


class IdeaStatus(Enum):
    """Status of an Idea in the content workflow.

    This enum represents the complete workflow stages from initial inspiration
    to final publication and archival. Each state represents a distinct phase
    in the content creation pipeline.

    Progressive Multi-Format Workflow:
        IdeaInspiration → Idea → Outline → Skeleton → Title
          ↓
        Script → ScriptDraft → ScriptReview → ScriptApproved
          ↓
        TextPublishing → PublishedText (text is published & used for voiceover)
          ├─→ AnalyticsReviewText (optional early analytics)
          ↓
        Voiceover → VoiceoverReview → VoiceoverApproved
          ↓
        AudioPublishing → PublishedAudio (audio is published & used for video)
          ├─→ AnalyticsReviewAudio (optional early analytics)
          ↓
        ScenePlanning → KeyframePlanning → KeyframeGeneration
          ↓
        VideoAssembly → VideoReview → VideoFinalized
          ↓
        PublishPlanning → PublishedVideo → AnalyticsReviewVideo
          ↓
        Archived

    Note: Content follows progressive enrichment:
    - Text: Published text serves as source for voiceover recording
    - Audio: Published audio serves as foundation for video scene planning
    - Video: Combines published audio with visual elements
    - Can stop at any stage (text-only, audio-only, or full video)
    """

    # Legacy states (kept for backward compatibility)
    DRAFT = "draft"
    VALIDATED = "validated"
    APPROVED = "approved"
    IN_PRODUCTION = "in_production"

    # Idea Development Phase
    IDEA = "idea"
    OUTLINE = "outline"
    SKELETON = "skeleton"
    TITLE = "title"

    # Script Development Phase
    SCRIPT = "script"
    SCRIPT_DRAFT = "script_draft"
    SCRIPT_REVIEW = "script_review"
    SCRIPT_APPROVED = "script_approved"

    # Text Publication (First Format - Source for Audio)
    TEXT_PUBLISHING = "text_publishing"
    TEXT_PUBLISHED = "text_published"
    TEXT_ANALYTICS = "text_analytics"

    # Voiceover Production Phase (Uses Published Text)
    VOICEOVER = "voiceover"
    VOICEOVER_REVIEW = "voiceover_review"
    VOICEOVER_APPROVED = "voiceover_approved"

    # Audio Publication (Second Format - Source for Video)
    AUDIO_PUBLISHING = "audio_publishing"
    AUDIO_PUBLISHED = "audio_published"
    AUDIO_ANALYTICS = "audio_analytics"

    # Visual Production Phase (Uses Published Audio)
    SCENE_PLANNING = "scene_planning"
    KEYFRAME_PLANNING = "keyframe_planning"
    KEYFRAME_GENERATION = "keyframe_generation"

    # Video Assembly Phase
    VIDEO_ASSEMBLY = "video_assembly"
    VIDEO_REVIEW = "video_review"
    VIDEO_FINALIZED = "video_finalized"

    # Video Publication (Third Format)
    VIDEO_PUBLISH_PLANNING = "video_publish_planning"
    VIDEO_PUBLISHED = "video_published"
    VIDEO_ANALYTICS = "video_analytics"

    # Legacy Publication States (for backward compatibility)
    PUBLISH_PLANNING = "publish_planning"
    PUBLISHED = "published"
    ANALYTICS_REVIEW = "analytics_review"

    # Final State
    ARCHIVED = "archived"


class ContentGenre(Enum):
    """Genre classification for content."""

    TRUE_CRIME = "true_crime"
    MYSTERY = "mystery"
    HORROR = "horror"
    SCIENCE_FICTION = "science_fiction"
    DOCUMENTARY = "documentary"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    LIFESTYLE = "lifestyle"
    TECHNOLOGY = "technology"
    OTHER = "other"


@dataclass
class Idea:
    """Core data model for distilled content ideas.

    Idea represents a refined concept that can be created independently or derived
    from one or more IdeaInspiration instances. It captures the essence of a creative
    concept with comprehensive storytelling elements and execution strategy.

    Note: Ideas can exist without IdeaInspiration sources - they can be created
    directly with manual input.

    Attributes:
        title: Clear, compelling title for the idea
        concept: Core concept or hook that defines the idea

        Story Foundation (Základy příběhu):
            idea: Basic story spark - word, sentence, scene, or feeling (Nápad)
            premise: Short 1-3 sentence explanation of what story is about (Premisa)
            logline: One-sentence dramatic version creating WOW effect
            hook: First sentence/moment that draws readers in (Háček)

        Story Structure (Struktura příběhu):
            synopsis: Short summary (1-3 paragraphs) for quick understanding
            story_premise: Core story premise providing AI context for generation
            skeleton: Very brief 3-6 point overview of story arc (Kostra příběhu)
            outline: Detailed plan with scenes, emotions, tension building (Osnova)
            beat_sheet: Breakdown into small story beats/moments (Taktová mapa)
            scenes: Scene breakdown - basic building blocks (Scény)

        Narrative Elements (Narativní prvky):
            pov: Point of view - who tells the story (Úhel pohledu)
            emotional_arc: Character's emotional journey from start to end (Emoční oblouk)
            reveal: Key information reveals (Odhalení)
            twist: Unexpected changes in story perception (Zvrat)
            climax: Most intense moment (Vrchol příběhu)
            ending: Conclusion content (Závěr)
            ending_type: Type of ending (open/shock/emotional)

        Content Properties:
            purpose: What problem does this solve or what value does it provide
            emotional_quality: The emotional tone and impact (e.g., "suspenseful", "inspiring")
            target_audience: Description of the intended audience
            target_demographics: Specific demographic data (age ranges, regions, languages)
            target_platforms: List of target platforms (e.g., ["youtube", "tiktok", "podcast"])
            target_formats: List of output formats (e.g., ["text", "audio", "video"])
            genre: Primary content genre
            style: Content style or approach (e.g., "narrative", "analytical")
            keywords: List of keywords or tags associated with the idea
            themes: List of core themes to explore in the content
            character_notes: Character descriptions, roles, and relationships
            setting_notes: Setting, world-building, and environmental details
            tone_guidance: Detailed guidance on tone, mood, and atmosphere
            length_target: Target length specification (e.g., "2000 words", "15 minutes")

        Metadata:
            potential_scores: Potential performance across contexts (platform, region, demographic)
            inspiration_ids: List of IdeaInspiration IDs that contributed to this Idea
            metadata: Additional flexible metadata (string key-value pairs)
            version: Version number for tracking iterations
            status: Current workflow status
            notes: Development notes and context
            created_at: Timestamp of creation
            updated_at: Timestamp of last update
            created_by: Creator identifier (human or AI agent)

    Note on Universal Generation:
        Ideas are designed for universal content generation. Each idea can be released
        simultaneously as text, audio, and video across multiple platforms. The target_formats
        and target_platforms fields support this multi-format, multi-platform approach.

    Example:
        >>> # Short horror story with complete narrative structure
        >>> idea = Idea(
        ...     title="The Echo",
        ...     concept="A girl hears a voice that sounds exactly like her own",
        ...     idea="Girl hears voice exactly like hers",
        ...     premise="A teenage girl starts hearing a voice that sounds identical to her own, "
        ...             "giving her warnings about the future. When the warnings come true, "
        ...             "she realizes the voice is her future self trying to prevent her death.",
        ...     logline="A girl discovers she can hear her own future thoughts—and they're telling her to run.",
        ...     hook="Last night I woke up... but my body kept sleeping.",
        ...     skeleton="1. Girl hears strange voice\n2. Voice sounds like her\n3. Voice predicts events\n"
        ...               "4. Predictions come true\n5. Final warning: run now\n6. She realizes too late",
        ...     beat_sheet="- Hears whisper at night\n- Recognizes own voice\n- Voice warns about accident\n"
        ...                 "- Accident happens exactly as warned\n- Voice says 'run NOW'\n"
        ...                 "- She sees herself in the mirror but it's not her reflection",
        ...     pov="first person (I) - intimate, strong emotions",
        ...     emotional_arc="curiosity → confusion → fear → terror → realization",
        ...     reveal="The voice is her future self",
        ...     twist="She's already dead - talking to her past self",
        ...     climax="Final moment when she realizes the truth",
        ...     ending="She tries to warn her past self, becoming the voice",
        ...     ending_type="shock",
        ...     target_platforms=["tiktok", "youtube", "medium"],
        ...     target_formats=["video", "audio", "text"],
        ...     genre=ContentGenre.HORROR,
        ...     length_target="60 seconds video / 500 words text",
        ...     tone_guidance="Start mysterious, build to terrifying, end with shocking twist"
        ... )
        >>>
        >>> # Educational content example
        >>> educational = Idea(
        ...     title="How Quantum Computers Actually Work",
        ...     concept="Explaining quantum computing through everyday analogies",
        ...     premise="Quantum computers process information fundamentally differently than regular computers. "
        ...             "This explainer uses everyday analogies to make the complex simple.",
        ...     logline="Your computer checks one path at a time; quantum computers check all paths at once.",
        ...     hook="What if your GPS could explore every possible route simultaneously?",
        ...     skeleton="1. Traditional computing basics\n2. The quantum difference\n"
        ...               "3. Real-world applications\n4. The future impact",
        ...     outline="Intro: Hook with GPS analogy\nSection 1: How normal computers work\n"
        ...             "Section 2: Quantum superposition explained\nSection 3: What this enables\n"
        ...             "Conclusion: Why it matters",
        ...     target_platforms=["youtube", "medium", "linkedin"],
        ...     target_formats=["video", "text"],
        ...     genre=ContentGenre.EDUCATIONAL,
        ...     length_target="8-10 minutes"
        ... )
    """

    title: str
    concept: str

    # Story Foundation (Základy příběhu)
    idea: str = ""  # Basic spark: word, sentence, scene, feeling (Nápad)
    premise: str = ""  # Short 1-3 sentence explanation (Premisa)
    logline: str = ""  # One-sentence dramatic version for WOW effect
    hook: str = ""  # First sentence/moment that draws readers in (Háček)

    # Story Structure (Struktura příběhu)
    synopsis: str = ""  # Short summary (1-3 paragraphs)
    story_premise: str = ""  # Story premise for AI context (legacy field)
    skeleton: str = ""  # Very brief 3-6 point overview (Kostra)
    outline: str = ""  # Detailed plan with scenes, emotions, tension (Osnova)
    beat_sheet: str = ""  # Small story beats/moments (Taktová mapa)
    scenes: str = ""  # Scene breakdown (Scény)

    # Narrative Elements (Narativní prvky)
    pov: str = ""  # Point of view: first person/third person (Úhel pohledu)
    emotional_arc: str = ""  # Character's emotional journey (Emoční oblouk)
    reveal: str = ""  # Key information reveals (Odhalení)
    twist: str = ""  # Unexpected story changes (Zvrat)
    climax: str = ""  # Most intense moment (Vrchol příběhu)
    ending: str = ""  # Conclusion type and content (Závěr)
    ending_type: str = ""  # open/shock/emotional ending

    # Content Properties
    purpose: str = ""
    emotional_quality: str = ""
    target_audience: str = ""
    target_demographics: Dict[str, str] = field(default_factory=dict)
    target_platforms: List[str] = field(default_factory=list)
    target_formats: List[str] = field(default_factory=list)
    genre: ContentGenre = ContentGenre.OTHER
    style: str = ""
    keywords: List[str] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    character_notes: str = ""
    setting_notes: str = ""
    tone_guidance: str = ""
    length_target: str = ""

    # Multi-Language Support
    original_language: str = "en"  # ISO 639-1 code for original language

    potential_scores: Dict[str, int] = field(default_factory=dict)
    inspiration_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
    version: int = 1
    status: IdeaStatus = IdeaStatus.DRAFT
    notes: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None

    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert Idea to dictionary representation.

        Returns:
            Dictionary containing all fields with Enums converted to strings
        """
        data = asdict(self)
        data["genre"] = self.genre.value
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Idea":
        """Create Idea from dictionary.

        Args:
            data: Dictionary containing Idea fields

        Returns:
            Idea instance
        """
        # Handle enum conversions
        genre = data.get("genre", "other")
        if isinstance(genre, str):
            try:
                genre = ContentGenre(genre)
            except ValueError:
                genre = ContentGenre.OTHER

        status = data.get("status", "draft")
        if isinstance(status, str):
            try:
                status = IdeaStatus(status)
            except ValueError:
                status = IdeaStatus.DRAFT

        return cls(
            title=data.get("title", ""),
            concept=data.get("concept", ""),
            idea=data.get("idea", ""),
            premise=data.get("premise", ""),
            logline=data.get("logline", ""),
            hook=data.get("hook", ""),
            synopsis=data.get("synopsis", ""),
            story_premise=data.get("story_premise", ""),
            skeleton=data.get("skeleton", ""),
            outline=data.get("outline", ""),
            beat_sheet=data.get("beat_sheet", ""),
            scenes=data.get("scenes", ""),
            pov=data.get("pov", ""),
            emotional_arc=data.get("emotional_arc", ""),
            reveal=data.get("reveal", ""),
            twist=data.get("twist", ""),
            climax=data.get("climax", ""),
            ending=data.get("ending", ""),
            ending_type=data.get("ending_type", ""),
            purpose=data.get("purpose", ""),
            emotional_quality=data.get("emotional_quality", ""),
            target_audience=data.get("target_audience", ""),
            target_demographics=data.get("target_demographics", {}),
            target_platforms=data.get("target_platforms", []),
            target_formats=data.get("target_formats", []),
            genre=genre,
            style=data.get("style", ""),
            keywords=data.get("keywords", []),
            themes=data.get("themes", []),
            character_notes=data.get("character_notes", ""),
            setting_notes=data.get("setting_notes", ""),
            tone_guidance=data.get("tone_guidance", ""),
            length_target=data.get("length_target", ""),
            original_language=data.get("original_language", "en"),
            potential_scores=data.get("potential_scores", {}),
            inspiration_ids=data.get("inspiration_ids", []),
            metadata=data.get("metadata", {}),
            version=data.get("version", 1),
            status=status,
            notes=data.get("notes", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            created_by=data.get("created_by"),
        )

    @classmethod
    def from_inspirations(
        cls,
        inspirations: List[Any],
        title: str,
        concept: str,
        synopsis: str = "",
        story_premise: str = "",
        purpose: str = "",
        emotional_quality: str = "",
        target_audience: str = "",
        target_demographics: Optional[Dict[str, str]] = None,
        target_platforms: Optional[List[str]] = None,
        target_formats: Optional[List[str]] = None,
        genre: ContentGenre = ContentGenre.OTHER,
        style: str = "",
        keywords: Optional[List[str]] = None,
        themes: Optional[List[str]] = None,
        character_notes: str = "",
        setting_notes: str = "",
        tone_guidance: str = "",
        length_target: str = "",
        outline: str = "",
        skeleton: str = "",
        created_by: Optional[str] = None,
    ) -> "Idea":
        """Create Idea from one or more IdeaInspiration instances.

        This factory method demonstrates the fusion/distillation process where
        multiple IdeaInspiration instances are combined into a single cohesive
        Idea concept.

        Args:
            inspirations: List of IdeaInspiration instances to blend
            title: Title for the new Idea
            concept: Core concept distilled from the inspirations
            synopsis: Short version/first draft summary
            story_premise: Core story premise for AI context
            purpose: Purpose of this Idea
            emotional_quality: Emotional tone and impact
            target_audience: Description of target audience
            target_demographics: Demographic targeting data
            target_platforms: List of target platforms (e.g., ["youtube", "spotify", "medium"])
            target_formats: List of output formats (e.g., ["text", "audio", "video"])
            genre: Content genre
            style: Content style or approach
            keywords: List of keywords or tags
            themes: List of core themes
            character_notes: Character descriptions and roles
            setting_notes: Setting and world-building details
            tone_guidance: Detailed tone/mood guidance for AI
            length_target: Target length specification
            outline: Structured outline or content structure
            skeleton: Basic framework or skeleton of the content
            created_by: Creator identifier

        Returns:
            Idea instance with linked inspiration IDs
        """
        # Extract inspiration IDs (assuming they have source_id or id attribute)
        inspiration_ids = []
        for insp in inspirations:
            if hasattr(insp, "source_id") and insp.source_id:
                inspiration_ids.append(insp.source_id)
            elif hasattr(insp, "id"):
                inspiration_ids.append(str(insp.id))

        # Aggregate keywords from inspirations if not provided
        if keywords is None:
            keywords = []
            for insp in inspirations:
                if hasattr(insp, "keywords") and insp.keywords:
                    keywords.extend(insp.keywords)
            # Remove duplicates while preserving order
            keywords = list(dict.fromkeys(keywords))

        # Aggregate themes from inspirations if not provided
        if themes is None:
            themes = []
            for insp in inspirations:
                if hasattr(insp, "themes") and insp.themes:
                    themes.extend(insp.themes)
            # Remove duplicates while preserving order
            themes = list(dict.fromkeys(themes))

        # Aggregate potential scores from inspirations if available
        potential_scores = {}
        for insp in inspirations:
            if hasattr(insp, "contextual_category_scores"):
                for key, value in insp.contextual_category_scores.items():
                    if key in potential_scores:
                        # Average the scores if multiple inspirations have the same context
                        potential_scores[key] = (potential_scores[key] + value) // 2
                    else:
                        potential_scores[key] = value

        return cls(
            title=title,
            concept=concept,
            synopsis=synopsis,
            story_premise=story_premise,
            purpose=purpose,
            emotional_quality=emotional_quality,
            target_audience=target_audience,
            target_demographics=target_demographics or {},
            target_platforms=target_platforms or [],
            target_formats=target_formats or [],
            genre=genre,
            style=style,
            keywords=keywords,
            themes=themes,
            character_notes=character_notes,
            setting_notes=setting_notes,
            tone_guidance=tone_guidance,
            length_target=length_target,
            outline=outline,
            skeleton=skeleton,
            potential_scores=potential_scores,
            inspiration_ids=inspiration_ids,
            created_by=created_by,
        )

    def create_new_version(self, **updates) -> "Idea":
        """Create a new version of this Idea with updates.

        Args:
            **updates: Keyword arguments for fields to update

        Returns:
            New Idea instance with incremented version
        """
        data = self.to_dict()
        data["version"] = self.version + 1
        data["updated_at"] = datetime.now().isoformat()
        data.update(updates)
        return Idea.from_dict(data)

    def generate_summary(self, max_length: int = 500) -> str:
        """Generate a concise summary of the Idea.

        Creates a summary that captures the essence of the Idea using key fields
        like title, concept, premise, and synopsis. Useful for quick overview,
        sharing, or translation.

        Args:
            max_length: Maximum length of summary in characters (default 500)

        Returns:
            Concise summary of the Idea

        Example:
            >>> idea = Idea(title="The Echo", concept="Time travel horror",
            ...             premise="A girl hears her future self warning her")
            >>> summary = idea.generate_summary(max_length=200)
        """
        # Build summary from available fields in order of priority
        summary_parts = []

        # Always include title and concept
        summary_parts.append(f"Title: {self.title}")
        summary_parts.append(f"Concept: {self.concept}")

        # Add premise if available and not too long
        if self.premise:
            summary_parts.append(f"Premise: {self.premise}")

        # Add logline if available (usually concise)
        if self.logline:
            summary_parts.append(f"Logline: {self.logline}")

        # Add synopsis if available and we have space
        if self.synopsis:
            summary_parts.append(f"Synopsis: {self.synopsis}")

        # Add genre and target info
        summary_parts.append(f"Genre: {self.genre.value}")

        if self.target_platforms:
            platforms = ", ".join(self.target_platforms[:3])  # Limit to first 3
            summary_parts.append(f"Platforms: {platforms}")

        if self.target_formats:
            formats = ", ".join(self.target_formats)
            summary_parts.append(f"Formats: {formats}")

        # Join and truncate if necessary
        summary = "\n".join(summary_parts)

        if len(summary) > max_length:
            # Truncate to max_length, breaking at last complete sentence/line
            # Ensure we don't exceed max_length even if no newline is found
            truncated = summary[:max_length]
            last_newline = truncated.rfind("\n")
            if last_newline > 0:
                summary = truncated[:last_newline]
            else:
                summary = truncated

            if not summary.endswith("."):
                summary += "..."

        return summary

    def translate_summary_to_czech(self, summary: Optional[str] = None) -> str:
        """Translate summary to Czech language.

        Translates the Idea summary to Czech (CS) language. This is a placeholder
        implementation that would integrate with translation services in production.

        Args:
            summary: Optional pre-generated summary to translate. If not provided,
                    generates summary first using generate_summary()

        Returns:
            Czech translation of the summary

        Note:
            In production, this would integrate with:
            - StoryTranslation model for full translation workflow
            - AI translation services (OpenAI, DeepL, etc.)
            - Translation feedback loop for quality assurance

        Example:
            >>> idea = Idea(title="The Echo", concept="Time travel horror")
            >>> czech_summary = idea.translate_summary_to_czech()
        """
        # Get or generate summary
        if summary is None:
            summary = self.generate_summary()

        # Simple translation mapping for demonstration
        # In production, this would use AI translation services
        translation_map = {
            "Title:": "Název:",
            "Concept:": "Koncept:",
            "Premise:": "Premisa:",
            "Logline:": "Logline:",
            "Synopsis:": "Synopse:",
            "Genre:": "Žánr:",
            "Platforms:": "Platformy:",
            "Formats:": "Formáty:",
            # Genre translations
            "true_crime": "skutečný zločin",
            "mystery": "mystérium",
            "horror": "horor",
            "science_fiction": "sci-fi",
            "documentary": "dokumentární",
            "educational": "vzdělávací",
            "entertainment": "zábava",
            "lifestyle": "životní styl",
            "technology": "technologie",
            "other": "jiné",
        }

        # Apply translations
        czech_summary = summary
        for english, czech in translation_map.items():
            czech_summary = czech_summary.replace(english, czech)

        # Add note about translation method
        czech_summary += CZECH_TRANSLATION_NOTE

        return czech_summary

    def __repr__(self) -> str:
        """String representation of Idea."""
        return (
            f"Idea(title='{self.title[:50]}...', "
            f"version={self.version}, "
            f"status={self.status.value}, "
            f"inspirations={len(self.inspiration_ids)} sources)"
        )
