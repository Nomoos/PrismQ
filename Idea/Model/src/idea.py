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

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class IdeaStatus(Enum):
    """Status of an Idea in the content workflow."""
    
    DRAFT = "draft"
    VALIDATED = "validated"
    APPROVED = "approved"
    IN_PRODUCTION = "in_production"
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
    concept with clear purpose, theme, target audience, and execution strategy.
    
    Note: Ideas can exist without IdeaInspiration sources - they can be created 
    directly with manual input.
    
    Attributes:
        title: Clear, compelling title for the idea
        concept: Core concept or hook that defines the idea
        synopsis: Short version/first draft summary (1-3 paragraphs) for quick understanding
        story_premise: Core story premise providing AI context for generation
        purpose: What problem does this solve or what value does it provide
        emotional_quality: The emotional tone and impact (e.g., "suspenseful", "inspiring")
        target_audience: Description of the intended audience
        target_demographics: Specific demographic data (age ranges, regions, languages)
        target_platform: Primary platform for content delivery (string, e.g., "youtube", "tiktok")
        genre: Primary content genre
        style: Content style or approach (e.g., "narrative", "analytical")
        keywords: List of keywords or tags associated with the idea
        themes: List of core themes to explore in the content
        character_notes: Character descriptions, roles, and relationships for story depth
        setting_notes: Setting, world-building, and environmental details
        tone_guidance: Detailed guidance on tone, mood, and atmosphere for AI generation
        length_target: Target length specification (e.g., "2000 words", "15 minutes", "10 episodes")
        outline: Structured outline or content structure
        skeleton: Basic framework or skeleton of the content
        potential_scores: Potential performance across contexts (platform, region, demographic)
        inspiration_ids: List of IdeaInspiration IDs that contributed to this Idea (can be empty)
        metadata: Additional flexible metadata (string key-value pairs)
        version: Version number for tracking iterations
        status: Current workflow status
        notes: Development notes and context
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
        created_by: Creator identifier (human or AI agent)
    
    Example:
        >>> idea = Idea(
        ...     title="The Digital Phantom Mystery",
        ...     concept="An investigation into unsolved internet mysteries",
        ...     synopsis="A deep dive into the most puzzling unsolved mysteries of the internet age. "
        ...              "From vanished influencers to encrypted messages, we explore digital cold cases "
        ...              "that continue to baffle investigators and captivate online communities.",
        ...     story_premise="In an era where everything is documented online, some mysteries remain unsolved. "
        ...                   "This series investigates digital disappearances, cryptic online phenomena, "
        ...                   "and internet legends through the lens of modern forensics.",
        ...     purpose="Engage true crime audience with unique digital angle",
        ...     emotional_quality="mysterious, suspenseful, intriguing",
        ...     target_audience="True crime enthusiasts aged 18-35",
        ...     target_demographics={"age_range": "18-35", "interests": "true_crime,technology"},
        ...     target_platform="youtube",
        ...     genre=ContentGenre.TRUE_CRIME,
        ...     keywords=["mystery", "internet", "unsolved", "digital forensics"],
        ...     themes=["digital privacy", "online identity", "modern detective work"],
        ...     character_notes="Host: Tech-savvy investigator with cybersecurity background. "
        ...                     "Supporting: Digital forensics experts, online community members",
        ...     setting_notes="Modern digital landscape, dark web forums, social media platforms",
        ...     tone_guidance="Start mysterious and intriguing, build suspense through investigation, "
        ...                   "maintain journalistic credibility while being engaging",
        ...     length_target="15-20 minute episodes, 8-10 episode season",
        ...     outline="1. Introduction\n2. Case Presentation\n3. Investigation\n4. Conclusion",
        ...     skeleton="Hook → Background → Evidence → Theory → Resolution"
        ... )
        >>> 
        >>> # Ideas can also be created without IdeaInspiration sources
        >>> manual_idea = Idea(
        ...     title="Tech Tutorial Series",
        ...     concept="Teaching Python to beginners",
        ...     synopsis="A beginner-friendly Python course that teaches through real projects",
        ...     keywords=["python", "programming", "tutorial"],
        ...     themes=["learn by doing", "practical skills"],
        ...     length_target="10-15 minute videos",
        ...     inspiration_ids=[]  # No source inspirations
        ... )
    """
    
    title: str
    concept: str
    synopsis: str = ""
    story_premise: str = ""
    purpose: str = ""
    emotional_quality: str = ""
    target_audience: str = ""
    target_demographics: Dict[str, str] = field(default_factory=dict)
    target_platform: str = ""
    genre: ContentGenre = ContentGenre.OTHER
    style: str = ""
    keywords: List[str] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    character_notes: str = ""
    setting_notes: str = ""
    tone_guidance: str = ""
    length_target: str = ""
    outline: str = ""
    skeleton: str = ""
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
            synopsis=data.get("synopsis", ""),
            story_premise=data.get("story_premise", ""),
            purpose=data.get("purpose", ""),
            emotional_quality=data.get("emotional_quality", ""),
            target_audience=data.get("target_audience", ""),
            target_demographics=data.get("target_demographics", {}),
            target_platform=data.get("target_platform", ""),
            genre=genre,
            style=data.get("style", ""),
            keywords=data.get("keywords", []),
            themes=data.get("themes", []),
            character_notes=data.get("character_notes", ""),
            setting_notes=data.get("setting_notes", ""),
            tone_guidance=data.get("tone_guidance", ""),
            length_target=data.get("length_target", ""),
            outline=data.get("outline", ""),
            skeleton=data.get("skeleton", ""),
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
        target_platform: str = "",
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
            target_platform: Primary target platform (e.g., "youtube", "tiktok", "podcast")
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
            if hasattr(insp, 'source_id') and insp.source_id:
                inspiration_ids.append(insp.source_id)
            elif hasattr(insp, 'id'):
                inspiration_ids.append(str(insp.id))
        
        # Aggregate keywords from inspirations if not provided
        if keywords is None:
            keywords = []
            for insp in inspirations:
                if hasattr(insp, 'keywords') and insp.keywords:
                    keywords.extend(insp.keywords)
            # Remove duplicates while preserving order
            keywords = list(dict.fromkeys(keywords))
        
        # Aggregate themes from inspirations if not provided
        if themes is None:
            themes = []
            for insp in inspirations:
                if hasattr(insp, 'themes') and insp.themes:
                    themes.extend(insp.themes)
            # Remove duplicates while preserving order
            themes = list(dict.fromkeys(themes))
        
        # Aggregate potential scores from inspirations if available
        potential_scores = {}
        for insp in inspirations:
            if hasattr(insp, 'contextual_category_scores'):
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
            target_platform=target_platform,
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
    
    def __repr__(self) -> str:
        """String representation of Idea."""
        return (
            f"Idea(title='{self.title[:50]}...', "
            f"version={self.version}, "
            f"status={self.status.value}, "
            f"inspirations={len(self.inspiration_ids)} sources)"
        )
