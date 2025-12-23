"""Story and Title Creation Service for PrismQ.T.Title.From.Idea.

This module provides functionality to generate Title (v0) for Stories
that are ready for title generation (state = PrismQ.T.Title.From.Idea)
and don't have Title or Content references yet.

Workflow Position: Stage 2 in MVP workflow
    PrismQ.T.Idea.Creation
        ↓
    PrismQ.T.Story.From.Idea (creates Stories)
        ↓
    PrismQ.T.Title.From.Idea (generates Title v0) ← This module
        ↓
    PrismQ.T.Content.Draft (v0)

The service:
1. Finds Stories with state PrismQ.T.Title.From.Idea
2. Filters to only Stories without Title references
3. Generates the first Title (version 0) for each Story
4. Updates each Story's state to TITLE_V0
5. Returns the created Titles

Example:
    >>> from T.Title.From.Idea.src.story_title_service import StoryTitleService
    >>>
    >>> # With database connection
    >>> service = StoryTitleService(db_connection)
    >>>
    >>> # Process stories without titles
    >>> result = service.process_stories_without_titles()
    >>>
    >>> print(f"Created {len(result.titles)} titles")
    >>> for story, title in result.get_story_title_pairs():
    ...     print(f"Story {story.id}: {title.text}")
"""

import logging
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Add parent directories to path for imports
current_file = Path(__file__)
t_module_dir = current_file.parent.parent.parent.parent.parent
model_path = t_module_dir / "Idea" / "Model"
database_path = t_module_dir / "Database"

# Ensure paths are available
if str(model_path / "src") not in sys.path:
    sys.path.insert(0, str(model_path / "src"))
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))
if str(database_path) not in sys.path:
    sys.path.insert(0, str(database_path))
if str(t_module_dir) not in sys.path:
    sys.path.insert(0, str(t_module_dir))

# Also add the src directory itself for title_generator imports
src_dir = current_file.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Import title generation components from refactored modules using relative imports
from .title_variant import TitleVariant
from .ai_title_generator import (
    AITitleGenerator,
    TitleGeneratorConfig,
    AIUnavailableError as _AIUnavailableError,
)

# Use the AI module's exception
AIUnavailableError = _AIUnavailableError

from idea import Idea

# Import database models and repositories
from Model.Database.models.story import Story, StoryState
from Model.Database.models.title import Title
from Model.Database.repositories.story_repository import StoryRepository
from Model.Database.repositories.title_repository import TitleRepository
from Model.Database.schema_manager import SchemaManager
from Model import StateNames


@dataclass
class StoryTitleResult:
    """Result of creating Stories with Titles from an Idea.

    Attributes:
        idea_id: The source idea identifier
        stories: List of created Story objects
        titles: List of created Title objects (one per story)
        title_variants: Original title variants used
    """

    idea_id: str
    stories: List[Story] = field(default_factory=list)
    titles: List[Title] = field(default_factory=list)
    title_variants: List[TitleVariant] = field(default_factory=list)

    @property
    def count(self) -> int:
        """Number of stories created."""
        return len(self.stories)

    def get_story_title_pairs(self) -> List[Tuple[Story, Title]]:
        """Get pairs of (Story, Title) for convenient iteration."""
        return list(zip(self.stories, self.titles))


class StoryTitleService:
    """Service for generating Titles for Stories without Title references.

    This service implements the PrismQ.T.Title.From.Idea workflow stage,
    which finds Stories with state TITLE_FROM_IDEA (ready for title generation)
    that don't have Title references yet, and generates Title (version 0) for each.
    
    Title generation is AI-only using Ollama with Qwen3:32b model. If AI is
    unavailable, AIUnavailableError will be raised.

    The service requires a database connection to:
    1. Find Stories with correct state and no titles
    2. Persist generated Titles
    3. Update Story state to next workflow step

    Attributes:
        _conn: SQLite database connection
        _story_repo: Story repository
        _title_repo: Title repository
        _ai_title_generator: AITitleGenerator for creating title variants (required)

    Example:
        >>> conn = sqlite3.connect("prismq.db")
        >>> conn.row_factory = sqlite3.Row
        >>> service = StoryTitleService(conn)
        >>>
        >>> # Process all stories without titles (requires AI)
        >>> try:
        ...     result = service.process_stories_without_titles()
        ...     print(f"Created {len(result.titles)} titles")
        ... except AIUnavailableError as e:
        ...     print(f"AI unavailable: {e}")
    """

    # State constant for this service
    CURRENT_STATE = StateNames.TITLE_FROM_IDEA
    
    NUM_STORIES = 10  # Number of stories to create from each Idea (legacy)
    NUM_VARIANTS = 10  # Number of title variants to generate
    DEFAULT_SIMILARITY_THRESHOLD = 0.7  # Threshold for similarity detection

    def __init__(
        self,
        connection: Optional[sqlite3.Connection] = None,
        title_config: Optional[TitleGeneratorConfig] = None,
        use_ai: bool = True,
        auto_create_schema: bool = True,
    ):
        """Initialize the service.

        Args:
            connection: SQLite connection for persistence.
                Required for new workflow (process_stories_without_titles).
                Optional for backward compatibility (create_stories_with_titles).
            title_config: Optional configuration for title generation.
                Note: Title generation always uses AI. This parameter is kept
                for backward compatibility but is not used.
            use_ai: Whether to use AI for title generation.
                Defaults to True. Must be True as AI is always required.
            auto_create_schema: If True (default), automatically creates database
                tables on initialization. Set to False if schema is managed
                externally via SchemaManager or migration tools.

        Note:
            For production environments with proper schema management, set
            auto_create_schema=False and use SchemaManager.initialize_schema()
            during application bootstrapping instead.
            
            Title generation is AI-only. If AI is unavailable, AIUnavailableError
            will be raised when attempting to generate titles.
        """
        self._conn = connection
        self._story_repo = StoryRepository(connection) if connection else None
        self._title_repo = TitleRepository(connection) if connection else None

        # Optionally ensure required tables exist (for convenience in development/testing)
        if connection and auto_create_schema:
            self.ensure_tables_exist()

        # Initialize AI title generator (required for title generation)
        self._use_ai = use_ai
        self._ai_title_generator = None
        if use_ai:
            self._ai_title_generator = AITitleGenerator()
            if not self._ai_title_generator.is_available():
                self._ai_title_generator = None

    def is_ai_available(self) -> bool:
        """Check if AI title generation is available.

        Returns:
            True if AI generation is configured and Ollama is running
        """
        return self._ai_title_generator is not None and self._ai_title_generator.is_available()

    def generate_title_variants(
        self, idea: Idea, num_variants: Optional[int] = None
    ) -> List[TitleVariant]:
        """Generate title variants from an Idea.

        Uses AI (Qwen2.5-14B-Instruct) for title generation. Raises an error
        if AI is unavailable - no fallback to template-based generation.

        Args:
            idea: Idea object to generate titles from
            num_variants: Number of variants to generate (3-10)

        Returns:
            List of TitleVariant instances

        Raises:
            AIUnavailableError: If AI title generation is not available
        """
        n_variants = num_variants or self.NUM_VARIANTS

        # Check if AI is available - raise error if not
        if not self._ai_title_generator or not self._ai_title_generator.is_available():
            error_msg = "AI title generation unavailable: Ollama not running or not configured"
            logger.error(error_msg)
            raise AIUnavailableError(error_msg)

        # Use AI generation (will raise AIUnavailableError if it fails)
        return self._ai_title_generator.generate_from_idea(idea, n_variants)

    def get_stories_without_titles(self) -> List[Story]:
        """Get Stories that are ready for title generation but don't have titles.

        Finds Stories where:
        1. state = TITLE_FROM_IDEA (ready for title generation)
        2. No Title records exist for the story_id

        Returns:
            List of Story objects without Title references.

        Raises:
            RuntimeError: If no database connection is available.
        """
        if not self._story_repo or not self._title_repo:
            raise RuntimeError("Database connection required for this operation")

        # Get stories with TITLE_FROM_IDEA state
        stories_ready = self._story_repo.find_by_state(StoryState.TITLE_FROM_IDEA)

        # Filter to only those without titles
        stories_without_titles = []
        for story in stories_ready:
            titles = self._title_repo.find_by_story_id(story.id)
            if not titles:
                stories_without_titles.append(story)

        return stories_without_titles

    def story_has_title(self, story_id: int) -> bool:
        """Check if a Story already has a Title.

        Args:
            story_id: The Story's database ID.

        Returns:
            True if the Story has at least one Title, False otherwise.
            Returns False if no database connection.
        """
        if not self._title_repo:
            return False
        titles = self._title_repo.find_by_story_id(story_id)
        return len(titles) > 0

    def story_has_content(self, story_id: int) -> bool:
        """Check if a Story has a Content reference.

        Note: This is a placeholder - Content repository would be needed
        for full implementation. Currently returns False.

        Args:
            story_id: The Story's database ID.

        Returns:
            False (placeholder - no Content repository implemented yet).
        """
        # TODO: Implement when Content repository is available
        # scripts = self._content_repo.find_by_story_id(story_id)
        # return len(scripts) > 0
        return False

    def get_sibling_stories(self, story: Story) -> List[Story]:
        """Get other Stories from the same Idea.

        Args:
            story: The Story to find siblings for.

        Returns:
            List of Story objects from the same Idea (excluding the input story).
            Returns empty list if no database connection or no idea_id.
        """
        if not self._story_repo or not story.idea_id:
            return []

        # Get all stories with the same idea_id
        sibling_stories = self._story_repo.find_by_idea_id(story.idea_id)

        # Exclude the current story
        return [s for s in sibling_stories if s.id != story.id]

    def get_sibling_titles(self, story: Story) -> List[Title]:
        """Get titles from other Stories with the same Idea.

        This method retrieves all titles from sibling stories (stories with
        the same idea_id), useful for checking similarity and avoiding
        duplicate titles.

        Args:
            story: The Story to find sibling titles for.

        Returns:
            List of Title objects from sibling Stories.
            Returns empty list if no database connection.
        """
        if not self._title_repo or not self._story_repo:
            return []

        sibling_stories = self.get_sibling_stories(story)
        sibling_titles = []

        for sibling in sibling_stories:
            titles = self._title_repo.find_by_story_id(sibling.id)
            sibling_titles.extend(titles)

        return sibling_titles

    def calculate_title_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity between two title texts.

        Uses Jaccard similarity based on word overlap.

        Args:
            title1: First title text.
            title2: Second title text.

        Returns:
            Similarity score between 0.0 (no similarity) and 1.0 (identical).
        """
        # Normalize: lowercase and split into words
        words1 = set(title1.lower().split())
        words2 = set(title2.lower().split())

        if not words1 or not words2:
            return 0.0

        # Jaccard similarity: intersection / union
        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def check_title_uniqueness(
        self, title_text: str, story: Story, similarity_threshold: float = None
    ) -> Tuple[bool, List[Tuple[str, float]]]:
        """Check if a title is unique enough compared to sibling titles.

        Args:
            title_text: The title text to check.
            story: The Story this title would belong to.
            similarity_threshold: Maximum allowed similarity (default: DEFAULT_SIMILARITY_THRESHOLD).

        Returns:
            Tuple of:
                - bool: True if title is unique enough, False if too similar.
                - List of (similar_title, similarity_score) tuples for titles
                  that exceed the threshold.
        """
        if similarity_threshold is None:
            similarity_threshold = self.DEFAULT_SIMILARITY_THRESHOLD

        sibling_titles = self.get_sibling_titles(story)
        similar_titles = []

        for sibling_title in sibling_titles:
            similarity = self.calculate_title_similarity(title_text, sibling_title.text)
            if similarity >= similarity_threshold:
                similar_titles.append((sibling_title.text, similarity))

        is_unique = len(similar_titles) == 0
        return is_unique, similar_titles

    def select_best_title(
        self, variants: List[TitleVariant], story: Story, similarity_threshold: float = None
    ) -> Tuple[TitleVariant, List[Tuple[str, float]]]:
        """Select the best title variant that is not too similar to siblings.

        Selection criteria:
        1. Sort variants by score (highest first)
        2. Check each variant for similarity to existing sibling titles
        3. If best title is too similar, remove it and try second best
        4. Repeat until a unique title is found or all exhausted
        5. If all are too similar, return the highest scored as fallback

        Args:
            variants: List of TitleVariant options.
            story: The Story to select a title for.
            similarity_threshold: Maximum allowed similarity with siblings
                                  (default: DEFAULT_SIMILARITY_THRESHOLD).

        Returns:
            Tuple of:
                - Selected TitleVariant
                - List of (similar_title, similarity_score) for reference
        """
        if not variants:
            raise ValueError("No variants provided")

        if similarity_threshold is None:
            similarity_threshold = self.DEFAULT_SIMILARITY_THRESHOLD

        # Sort variants by original score (highest first)
        sorted_variants = sorted(variants, key=lambda v: v.score, reverse=True)

        # Track the best variant as fallback (highest score, even if similar)
        fallback_variant = sorted_variants[0]
        fallback_similar_titles = []

        # Iterate through variants in score order, pick first unique one
        for variant in sorted_variants:
            is_unique, similar_titles = self.check_title_uniqueness(
                variant.text, story, similarity_threshold
            )

            # Keep track of fallback info from best variant
            if variant == fallback_variant:
                fallback_similar_titles = similar_titles

            # If this title is unique enough, select it
            if is_unique:
                return variant, similar_titles

        # All variants are too similar - return the highest scored as fallback
        return fallback_variant, fallback_similar_titles

    def generate_title_for_story(
        self, story: Story, idea: Optional[Idea] = None
    ) -> Optional[Title]:
        """Generate a Title (v0) for a single Story using AI.

        Uses AI (Qwen2.5-14B-Instruct) for title generation. Raises an error
        if AI is unavailable or if no Idea is provided - no fallback titles.

        Args:
            story: The Story to generate a title for.
            idea: Idea object for context. Required for AI title generation.

        Returns:
            Created Title object, or None if story already has a title.

        Raises:
            RuntimeError: If no database connection is available.
            AIUnavailableError: If AI title generation is not available.
            ValueError: If no Idea is provided for title generation.
        """
        if not self._title_repo or not self._story_repo:
            raise RuntimeError("Database connection required for this operation")

        # Check if story already has a title
        if self.story_has_title(story.id):
            return None

        # Idea is required for AI title generation - no fallback
        if not idea:
            raise ValueError(
                f"Idea object is required for AI title generation (Story ID: {story.id}). "
                "The caller must provide a valid Idea object."
            )

        # Generate title variants using AI (will raise AIUnavailableError if AI is unavailable)
        variants = self.generate_title_variants(idea, num_variants=self.NUM_VARIANTS)

        if not variants:
            raise AIUnavailableError(
                "AI title generation returned no variants. "
                "Ensure Ollama is running and the model is available."
            )

        # Select best title considering similarity to sibling titles
        best_variant, similar_titles = self.select_best_title(variants, story)
        title_text = best_variant.text

        # Create Title (version 0)
        title = Title(story_id=story.id, version=0, text=title_text)

        # Persist Title
        title = self._title_repo.insert(title)

        # Update Story state to CONTENT_FROM_IDEA_TITLE (next workflow step)
        # The workflow is: TITLE_FROM_IDEA -> CONTENT_FROM_IDEA_TITLE
        # Title already references Story via story_id FK
        story.transition_to(StoryState.CONTENT_FROM_IDEA_TITLE)
        self._story_repo.update(story)

        return title

    def process_stories_without_titles(self, idea_db=None) -> StoryTitleResult:
        """Process all Stories without titles and generate Title v0 for each.

        This method:
        1. Finds all Stories with state TITLE_FROM_IDEA and no Title references
        2. Generates Title (v0) for each Story
        3. Updates each Story's state to CONTENT_FROM_IDEA_TITLE (next workflow step)

        Args:
            idea_db: Optional SimpleIdeaDatabase to fetch Idea content.
                    If provided, titles will be generated from Idea content.

        Returns:
            StoryTitleResult containing processed Stories and created Titles.

        Raises:
            RuntimeError: If no database connection is available.
        """
        if not self._story_repo or not self._title_repo:
            raise RuntimeError("Database connection required for this operation")

        stories_to_process = self.get_stories_without_titles()

        stories: List[Story] = []
        titles: List[Title] = []
        title_variants: List[TitleVariant] = []

        for story in stories_to_process:
            idea = None

            # Try to get Idea content for better title generation
            if idea_db:
                try:
                    idea_id = int(story.idea_id)
                    idea_dict = idea_db.get_idea(idea_id)
                    if idea_dict:
                        idea = Idea(
                            title=idea_dict.get("text", ""), concept=idea_dict.get("text", "")
                        )
                except (ValueError, TypeError):
                    pass

            # Generate title
            title = self.generate_title_for_story(story, idea)
            if title:
                stories.append(story)
                titles.append(title)

        # Return result with first idea_id found or empty string
        idea_id = stories[0].idea_id if stories else ""

        return StoryTitleResult(
            idea_id=idea_id, stories=stories, titles=titles, title_variants=title_variants
        )

    # === Legacy methods for backward compatibility ===

    def idea_has_stories(self, idea: Idea, idea_id: Optional[str] = None) -> bool:
        """Check if an Idea already has Stories in the database.

        DEPRECATED: Use Story.From.Idea module for creating stories.
        This method is kept for backward compatibility.

        Args:
            idea: The Idea object to check.
            idea_id: Optional explicit idea identifier.

        Returns:
            True if the Idea already has Stories, False otherwise.
            Always returns False if no database connection is available.
        """
        if not self._story_repo:
            return False
        effective_idea_id = idea_id or self._get_idea_id(idea)
        count = self._story_repo.count_by_idea_id(effective_idea_id)
        return count > 0

    def create_stories_with_titles(
        self, idea: Idea, idea_id: Optional[str] = None, skip_if_exists: bool = True
    ) -> Optional[StoryTitleResult]:
        """Create 10 Stories from an Idea, each with a first Title.

        DEPRECATED: Use Story.From.Idea module to create stories first,
        then use process_stories_without_titles() to generate titles.
        This method is kept for backward compatibility.

        This method:
        1. Checks if Idea already has Stories (if skip_if_exists=True)
        2. Generates 10 title variants from the Idea
        3. Creates 10 Story objects, each referencing the Idea
        4. Creates the first Title (v0) for each Story using a variant
        5. Updates each Story's state to TITLE_V0
        6. Persists to database if connection was provided

        Args:
            idea: The source Idea object containing concept, title, etc.
            idea_id: Optional explicit idea identifier. If not provided,
                uses idea.title as a simple identifier (for ideas without
                database persistence).
            skip_if_exists: If True (default), returns None if the Idea
                already has Stories in the database. This ensures the module
                only picks Ideas that aren't referenced by Story table rows yet.

        Returns:
            StoryTitleResult containing created Stories and Titles,
            or None if skip_if_exists=True and Idea already has Stories.

        Raises:
            ValueError: If idea is None or has no title/concept.
        """
        if not idea:
            raise ValueError("Idea cannot be None")

        if not idea.title and not idea.concept:
            raise ValueError("Idea must have at least a title or concept")

        # Determine idea ID
        effective_idea_id = idea_id or self._get_idea_id(idea)

        # Check if Idea already has Stories (skip if exists)
        if skip_if_exists and self.idea_has_stories(idea, effective_idea_id):
            return None

        # Generate title variants using AI (required - no fallback)
        # Will raise AIUnavailableError if AI is not available
        title_variants = self.generate_title_variants(idea, num_variants=self.NUM_STORIES)

        # Create Stories and Titles
        stories: List[Story] = []
        titles: List[Title] = []

        for i, variant in enumerate(title_variants):
            # Create Story with TITLE_FROM_IDEA state (ready for title processing)
            # Note: This bypasses the Story.From.Idea module for legacy compatibility
            story = Story(
                idea_id=effective_idea_id,
                state=StoryState.TITLE_FROM_IDEA.value,  # Use proper workflow state
            )

            # Persist Story if we have a connection
            if self._story_repo:
                story = self._story_repo.insert(story)
            else:
                # Assign a temporary ID for in-memory usage
                story.id = i + 1

            # Create Title (version 0) for this Story
            title = Title(story_id=story.id, version=0, text=variant.text)

            # Persist Title if we have a connection
            if self._title_repo:
                title = self._title_repo.insert(title)
            else:
                # Assign a temporary ID for in-memory usage
                title.id = i + 1

            # Update Story state to CONTENT_FROM_IDEA_TITLE (next workflow step)
            # Title already references Story via story_id FK
            story.transition_to(StoryState.CONTENT_FROM_IDEA_TITLE)
            if self._story_repo:
                self._story_repo.update(story)

            stories.append(story)
            titles.append(title)

        return StoryTitleResult(
            idea_id=effective_idea_id, stories=stories, titles=titles, title_variants=title_variants
        )

    def _get_idea_id(self, idea: Idea) -> str:
        """Extract or generate an identifier for the Idea.

        Args:
            idea: The Idea object.

        Returns:
            A string identifier for the Idea.
        """
        # Try to use existing ID if available
        if hasattr(idea, "id") and idea.id:
            return str(idea.id)

        # Use title as a simple identifier
        if idea.title:
            # Create a simple slug from title
            return idea.title.lower().replace(" ", "-")[:50]

        # Use deterministic hash of concept as fallback (hashlib for stability)
        import hashlib

        concept_hash = hashlib.md5(idea.concept.encode()).hexdigest()[:8]
        return f"idea-{concept_hash}"

    def ensure_tables_exist(self) -> None:
        """Ensure all required database tables exist.

        Delegates to SchemaManager for centralized schema management.
        This method is provided for backward compatibility and convenience
        in development/testing scenarios.

        For production environments, prefer using SchemaManager directly
        during application bootstrapping:

            from Model.Database.schema_manager import SchemaManager
            schema_manager = SchemaManager(connection)
            schema_manager.initialize_schema()

        Raises:
            RuntimeError: If no database connection is available.
        """
        if not self._conn:
            raise RuntimeError("No database connection available")

        # Delegate to centralized SchemaManager
        schema_manager = SchemaManager(self._conn)
        schema_manager.initialize_schema()


def create_stories_from_idea(
    idea: Idea,
    connection: Optional[sqlite3.Connection] = None,
    idea_id: Optional[str] = None,
    title_config: Optional[TitleGeneratorConfig] = None,
    skip_if_exists: bool = True,
) -> Optional[StoryTitleResult]:
    """Convenience function to create Stories with Titles from an Idea.

    DEPRECATED: Use Story.From.Idea module to create stories first,
    then use process_stories_without_titles() to generate titles.
    This function is kept for backward compatibility.
    
    Requires AI (Ollama with Qwen3:32b) to be available for title generation.

    Args:
        idea: The source Idea object.
        connection: Optional SQLite connection for persistence.
        idea_id: Optional explicit idea identifier.
        title_config: Optional configuration for title generation (not used).
        skip_if_exists: If True (default), returns None if the Idea
            already has Stories in the database.

    Returns:
        StoryTitleResult containing created Stories and Titles,
        or None if skip_if_exists=True and Idea already has Stories.
        
    Raises:
        AIUnavailableError: If AI title generation is not available.

    Example:
        >>> idea = Idea(title="AI Future", concept="Exploring AI trends")
        >>> try:
        ...     result = create_stories_from_idea(idea)
        ...     if result:
        ...         print(f"Created {result.count} stories")
        ... except AIUnavailableError:
        ...     print("AI unavailable - cannot generate titles")
    """
    service = StoryTitleService(connection, title_config)
    return service.create_stories_with_titles(idea, idea_id, skip_if_exists)


def process_stories_without_titles(
    connection: sqlite3.Connection, idea_db=None, title_config: Optional[TitleGeneratorConfig] = None
) -> StoryTitleResult:
    """Process Stories without Title references and generate Title v0 for each.

    This is the main entry point for the PrismQ.T.Title.From.Idea module.
    It finds Stories with state TITLE_FROM_IDEA that don't have Title
    references yet, and generates the first Title (v0) for each.
    
    Requires AI (Ollama with Qwen3:32b) to be available for title generation.

    Args:
        connection: SQLite connection for persistence.
        idea_db: Optional SimpleIdeaDatabase for fetching Idea content.
        title_config: Optional configuration for title generation (not used).

    Returns:
        StoryTitleResult containing processed Stories and created Titles.
        
    Raises:
        AIUnavailableError: If AI title generation is not available.

    Example:
        >>> conn = sqlite3.connect("prismq.db")
        >>> conn.row_factory = sqlite3.Row
        >>> result = process_stories_without_titles(conn)
        >>> print(f"Created {len(result.titles)} titles")
    """
    service = StoryTitleService(connection, title_config)
    return service.process_stories_without_titles(idea_db)
