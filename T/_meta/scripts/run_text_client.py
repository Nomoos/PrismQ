#!/usr/bin/env python3
"""Interactive Text Client for PrismQ.T Text Generation Pipeline.

This content provides a quick, interactive way to work with the PrismQ Text
Generation Pipeline. It allows you to:
- Create and manage Ideas
- Generate Titles from Ideas
- Generate Contents from Titles and Ideas
- Review and iterate on content
- Track versions through the workflow

Usage:
    python run_text_client.py
    python run_text_client.py --demo      # Run with demo data
    python run_text_client.py --help      # Show help

The client operates in an interactive REPL mode, allowing you to explore
the text generation workflow step by step.
"""

import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Add module paths for imports
SCRIPT_DIR = Path(__file__).parent.absolute()
REPO_ROOT = SCRIPT_DIR.parent.parent.parent  # T/_meta/contents -> T -> repo root
T_ROOT = SCRIPT_DIR.parent.parent  # T/_meta/contents -> T

# Add paths for imports
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(T_ROOT / "Idea" / "Model"))
sys.path.insert(0, str(T_ROOT / "Content" / "src"))

# Try to import PrismQ modules
try:
    from src.idea import ContentGenre, Idea, IdeaStatus

    IDEA_AVAILABLE = True
except ImportError:
    IDEA_AVAILABLE = False

try:
    from content_writer import OptimizationStrategy, ContentWriter

    SCRIPT_WRITER_AVAILABLE = True
except ImportError:
    SCRIPT_WRITER_AVAILABLE = False


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for terminal styling."""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_header(text: str) -> None:
    """Print a styled header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'═' * 70}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'═' * 70}{Colors.END}\n")


def print_section(text: str) -> None:
    """Print a styled section header."""
    print(f"\n{Colors.CYAN}{'─' * 50}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.CYAN}{'─' * 50}{Colors.END}")


def print_success(text: str) -> None:
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_warning(text: str) -> None:
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_error(text: str) -> None:
    """Print an error message."""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text: str) -> None:
    """Print an info message."""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


class TextClient:
    """Interactive client for the PrismQ Text Generation Pipeline.

    This client provides an interactive REPL interface for working with
    the text generation workflow, including Idea creation, Title generation,
    and Content development.

    Version tracking is used to determine which item to process next,
    with the lowest version count being selected for processing.

    State is persisted to a SQLite database to allow running each step
    as a separate process (for batch content workflows).
    """

    STATE_DB = "text_client_state.db"

    def __init__(self, load_state: bool = False):
        """Initialize the text client.

        Args:
            load_state: If True, load state from database if it exists.
        """
        self.current_idea: Optional[Any] = None
        self.current_title: Optional[str] = None
        self.current_content: Optional[str] = None
        self.content_writer: Optional[Any] = None
        self.history: list = []
        self.session_start = datetime.now()

        # Version tracking for each content type
        self.idea_version: int = 0
        self.title_version: int = 0
        self.content_version: int = 0

        # Idea data for persistence (since Idea objects may not serialize directly)
        self._idea_data: Optional[Dict[str, Any]] = None

        # Initialize database
        self._init_db()

        if load_state:
            self._load_state()

    def _get_db_path(self) -> Path:
        """Get the path to the SQLite database file."""
        return SCRIPT_DIR / self.STATE_DB

    def _idea_to_prompt_text(self, idea: Any) -> str:
        """Convert an Idea object to prompt-like text format.

        This method creates a structured prompt text from an Idea object,
        following the requirement that Idea.text should be in "format prompt like".

        Args:
            idea: The Idea object to convert

        Returns:
            A prompt-like text string representing the idea
        """
        parts = []

        # Get title and concept (required fields)
        title = getattr(idea, "title", "")
        concept = getattr(idea, "concept", "")

        if title:
            parts.append(f"Title: {title}")
        if concept:
            parts.append(f"Concept: {concept}")

        # Optional story foundation fields
        premise = getattr(idea, "premise", "")
        if premise:
            parts.append(f"Premise: {premise}")

        logline = getattr(idea, "logline", "")
        if logline:
            parts.append(f"Logline: {logline}")

        hook = getattr(idea, "hook", "")
        if hook:
            parts.append(f"Hook: {hook}")

        # Story structure
        skeleton = getattr(idea, "skeleton", "")
        if skeleton:
            parts.append(f"Structure: {skeleton}")

        # Narrative elements
        emotional_arc = getattr(idea, "emotional_arc", "")
        if emotional_arc:
            parts.append(f"Emotional Arc: {emotional_arc}")

        twist = getattr(idea, "twist", "")
        if twist:
            parts.append(f"Twist: {twist}")

        climax = getattr(idea, "climax", "")
        if climax:
            parts.append(f"Climax: {climax}")

        # Guidance
        tone_guidance = getattr(idea, "tone_guidance", "")
        if tone_guidance:
            parts.append(f"Tone Guidance: {tone_guidance}")

        target_audience = getattr(idea, "target_audience", "")
        if target_audience:
            parts.append(f"Target Audience: {target_audience}")

        # Genre
        genre = getattr(idea, "genre", None)
        if genre:
            genre_value = genre.value if hasattr(genre, "value") else str(genre)
            parts.append(f"Genre: {genre_value}")

        return "\n".join(parts)

    def _prompt_text_to_idea_data(self, text: str) -> Dict[str, Any]:
        """Parse prompt-like text back into idea data dictionary.

        Args:
            text: The prompt text to parse

        Returns:
            Dictionary with idea fields extracted from text
        """
        data = {}

        # Parse key-value lines from the prompt text
        for line in text.split("\n"):
            line = line.strip()
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower().replace(" ", "_")
                value = value.strip()

                # Map parsed keys to idea fields
                field_map = {
                    "title": "title",
                    "concept": "concept",
                    "premise": "premise",
                    "logline": "logline",
                    "hook": "hook",
                    "structure": "skeleton",
                    "skeleton": "skeleton",
                    "emotional_arc": "emotional_arc",
                    "twist": "twist",
                    "climax": "climax",
                    "tone_guidance": "tone_guidance",
                    "target_audience": "target_audience",
                    "genre": "genre",
                }

                if key in field_map:
                    data[field_map[key]] = value

        return data

    # Process state names following PrismQ naming convention (folder structure)
    # See T/WORKFLOW_STATE_MACHINE.md for full state machine documentation
    PROCESS_STATES = {
        "initial": "PrismQ.T.Idea.Creation",  # Initial state - awaiting idea creation
        "idea_created": "PrismQ.T.Title.From.Idea",  # After idea, next is title generation
        "title_generated": "PrismQ.T.Content.FromIdeaAndTitle",  # After title, next is content
        "content_generated": "PrismQ.T.Content.FromOriginalContentAndReviewAndTitle",  # Content iteration
        "content_iterated": "PrismQ.T.Content.FromOriginalContentAndReviewAndTitle",  # Continue iteration
        "exported": "PrismQ.T.Publishing",  # Final state
    }

    def _init_db(self) -> None:
        """Initialize the SQLite database with core tables.

        Tables:
        - Idea: Idea data (referenced by Story via FK)
        - Story: Main object with state (next process name) and idea_id FK
        - TitleVersion: Version history for titles (with direct review_id FK)
        - ContentVersion: Version history for contents (with direct review_id FK)
        - Review: Simple review content
        - StoryReview: Linking table for Story reviews (many-to-many)

        Note: version fields use INTEGER with CHECK >= 0 to simulate unsigned integer
        """
        db_path = self._get_db_path()
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            conn.execute("PRAGMA foreign_keys=ON")

            # Idea: Simple idea data table (referenced by Story via FK)
            # version uses CHECK >= 0 to simulate unsigned integer
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS Idea (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT,
                    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 0),
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
            """
            )

            # Story: Main table with state as string (next process name) and idea_id FK
            # Note: current_title_version_id and current_content_version_id are removed
            # because they are implicit - filter from TitleVersion/ContentVersion tables
            # by highest version integer instead
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS Story (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    idea_id INTEGER NULL,
                    state TEXT NOT NULL DEFAULT 'PrismQ.T.Idea.Creation',
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                    FOREIGN KEY (idea_id) REFERENCES Idea(id)
                )
            """
            )

            # Review: Simple review content (no relationship tracking)
            # Title/Content reference Review directly via FK
            # Story references Review via StoryReview linking table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS Review (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
            """
            )

            # TitleVersion: Version history for titles with direct review FK
            # version uses CHECK >= 0 to simulate unsigned integer
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS TitleVersion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    story_id INTEGER NOT NULL,
                    version INTEGER NOT NULL CHECK (version >= 0),
                    text TEXT NOT NULL,
                    review_id INTEGER NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    FOREIGN KEY (story_id) REFERENCES Story(id),
                    FOREIGN KEY (review_id) REFERENCES Review(id),
                    UNIQUE(story_id, version)
                )
            """
            )

            # ContentVersion: Version history for contents with direct review FK
            # version uses CHECK >= 0 to simulate unsigned integer
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ContentVersion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    story_id INTEGER NOT NULL,
                    version INTEGER NOT NULL CHECK (version >= 0),
                    text TEXT NOT NULL,
                    review_id INTEGER NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    FOREIGN KEY (story_id) REFERENCES Story(id),
                    FOREIGN KEY (review_id) REFERENCES Review(id),
                    UNIQUE(story_id, version)
                )
            """
            )

            # StoryReview: Linking table for Story reviews (many-to-many)
            # Allows one Story to have multiple reviews with different types
            # version uses CHECK >= 0 to simulate unsigned integer
            # UNIQUE(story_id, version, review_type) prevents duplicate reviews of same type for same version
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS StoryReview (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    story_id INTEGER NOT NULL,
                    review_id INTEGER NOT NULL,
                    version INTEGER NOT NULL CHECK (version >= 0),
                    review_type TEXT NOT NULL CHECK (review_type IN ('grammar', 'tone', 'content', 'consistency', 'editing')),
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    FOREIGN KEY (story_id) REFERENCES Story(id),
                    FOREIGN KEY (review_id) REFERENCES Review(id),
                    UNIQUE(story_id, version, review_type)
                )
            """
            )

            conn.commit()

    def _save_state(self) -> None:
        """Save current state to SQLite database for persistence between processes.

        Uses the core tables: Idea, Story, TitleVersion, ContentVersion.
        - Idea data is stored in Idea table
        - Story references Idea via idea_id FK
        - State is stored as a process name string on the Story object
        """
        db_path = self._get_db_path()

        with sqlite3.connect(db_path) as conn:
            conn.execute("PRAGMA foreign_keys=ON")
            cursor = conn.cursor()

            # Determine current state based on workflow progress
            if self.current_content is not None:
                if self.content_version > 1:
                    state = self.PROCESS_STATES["content_iterated"]
                else:
                    state = self.PROCESS_STATES["content_generated"]
            elif self.current_title is not None:
                state = self.PROCESS_STATES["title_generated"]
            elif self.current_idea is not None:
                state = self.PROCESS_STATES["idea_created"]
            else:
                state = self.PROCESS_STATES["initial"]

            # Extract idea data and convert to prompt-like text format
            idea_id = None
            if self.current_idea is not None:
                # Convert full Idea to simplified prompt text format
                # This follows the requirement: "text in format prompt like"
                idea_text = self._idea_to_prompt_text(self.current_idea)

                # Save or update Idea using simplified schema (id, text, version, created_at)
                cursor.execute("SELECT id FROM Idea ORDER BY id DESC LIMIT 1")
                idea_row = cursor.fetchone()

                if idea_row:
                    idea_id = idea_row[0]
                    cursor.execute(
                        """
                        UPDATE Idea SET
                            text = ?, version = ?
                        WHERE id = ?
                    """,
                        (idea_text, self.idea_version, idea_id),
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO Idea (text, version)
                        VALUES (?, ?)
                    """,
                        (idea_text, self.idea_version),
                    )
                    idea_id = cursor.lastrowid

            # Get or create Story
            cursor.execute("SELECT id FROM Story ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()

            if row:
                story_id = row[0]
                # Update existing Story with state and idea_id FK
                cursor.execute(
                    """
                    UPDATE Story SET
                        state = ?,
                        idea_id = ?
                    WHERE id = ?
                """,
                    (state, idea_id, story_id),
                )
            else:
                # Insert new Story with idea_id FK
                cursor.execute(
                    """
                    INSERT INTO Story (state, idea_id)
                    VALUES (?, ?)
                """,
                    (state, idea_id),
                )
                story_id = cursor.lastrowid

            # Save TitleVersion if we have a new title
            # Note: current_title_version_id is implicit (use MAX(version) query)
            if self.current_title:
                cursor.execute(
                    """
                    SELECT MAX(version) FROM TitleVersion WHERE story_id = ?
                """,
                    (story_id,),
                )
                max_version = cursor.fetchone()[0] or 0

                if self.title_version > max_version:
                    cursor.execute(
                        """
                        INSERT INTO TitleVersion (story_id, version, text)
                        VALUES (?, ?, ?)
                    """,
                        (story_id, self.title_version, self.current_title),
                    )

            # Save ContentVersion if we have a new content
            # Note: current_content_version_id is implicit (use MAX(version) query)
            if self.current_content:
                cursor.execute(
                    """
                    SELECT MAX(version) FROM ContentVersion WHERE story_id = ?
                """,
                    (story_id,),
                )
                max_version = cursor.fetchone()[0] or 0

                if self.content_version > max_version:
                    cursor.execute(
                        """
                        INSERT INTO ContentVersion (story_id, version, text)
                        VALUES (?, ?, ?)
                    """,
                        (story_id, self.content_version, self.current_content),
                    )

            conn.commit()

        print_info(f"State saved to {db_path.name} (state: {state})")

    def _load_state(self) -> bool:
        """Load state from SQLite database if it exists.

        Loads from the core tables: Idea, Story, TitleVersion, ContentVersion.
        - Idea data is loaded from Idea table via Story.idea_id FK

        Returns:
            True if state was loaded, False otherwise.
        """
        db_path = self._get_db_path()
        if not db_path.exists():
            return False

        try:
            with sqlite3.connect(db_path) as conn:
                conn.execute("PRAGMA foreign_keys=ON")
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Load Story (most recent)
                cursor.execute(
                    """
                    SELECT * FROM Story ORDER BY id DESC LIMIT 1
                """
                )
                story_row = cursor.fetchone()

                if not story_row:
                    return False

                story_id = story_row["id"]
                current_state = story_row["state"] or self.PROCESS_STATES["initial"]
                idea_id = story_row["idea_id"]

                # Derive version counts from state
                state_order = list(self.PROCESS_STATES.values())
                if current_state in state_order:
                    state_idx = state_order.index(current_state)
                    # Idea version is 1 if we've passed idea_created state
                    if state_idx >= state_order.index(self.PROCESS_STATES["idea_created"]):
                        self.idea_version = 1
                    # Title version from TitleVersion table
                    # Content version from ContentVersion table

                # Load idea data from Idea table via FK (simplified schema: text, version, created_at)
                if idea_id and IDEA_AVAILABLE:
                    cursor.execute("SELECT * FROM Idea WHERE id = ?", (idea_id,))
                    idea_row = cursor.fetchone()

                    if idea_row:
                        # Parse prompt text back to idea data
                        idea_text = idea_row["text"] or ""
                        idea_version = idea_row["version"] or 1

                        # Convert prompt text to idea data dictionary
                        idea_data = self._prompt_text_to_idea_data(idea_text)

                        try:
                            self.current_idea = Idea.from_dict(idea_data)
                            self._idea_data = idea_data
                            self.idea_version = idea_version
                        except (AttributeError, TypeError, KeyError, ValueError):
                            self.current_idea = Idea(
                                title=idea_data.get("title", ""),
                                concept=idea_data.get("concept", ""),
                            )
                            self._idea_data = idea_data
                            self.idea_version = idea_version

                # Load current TitleVersion (highest version is implicit current)
                # Using ORDER BY version DESC LIMIT 1 which is equivalent to MAX(version)
                # for the INTEGER version column
                cursor.execute(
                    """
                    SELECT text, version FROM TitleVersion 
                    WHERE story_id = ? ORDER BY version DESC LIMIT 1
                """,
                    (story_id,),
                )
                title_row = cursor.fetchone()
                if title_row:
                    self.current_title = title_row["text"]
                    self.title_version = title_row["version"]

                # Load current ContentVersion (highest version is implicit current)
                # Using ORDER BY version DESC LIMIT 1 which is equivalent to MAX(version)
                # for the INTEGER version column
                cursor.execute(
                    """
                    SELECT text, version FROM ContentVersion 
                    WHERE story_id = ? ORDER BY version DESC LIMIT 1
                """,
                    (story_id,),
                )
                content_row = cursor.fetchone()
                if content_row:
                    self.current_content = content_row["text"]
                    self.content_version = content_row["version"]

            print_info(f"State loaded from {db_path.name} (state: {current_state})")
            return True
        except (sqlite3.Error, KeyError, TypeError, ValueError) as e:
            print_warning(f"Failed to load state: {e}")
            return False

    def clear_state(self) -> None:
        """Clear the saved state database."""
        db_path = self._get_db_path()
        if db_path.exists():
            db_path.unlink()
            print_info("State database cleared")
            # Reinitialize empty database
            self._init_db()

    def show_welcome(self) -> None:
        """Display welcome message and available modules."""
        print_header("PrismQ.T - Interactive Text Client")

        print("Welcome to the PrismQ Text Generation Pipeline!")
        print("This interactive client helps you create and refine content.\n")

        # Show module availability
        print_section("Module Availability")

        if IDEA_AVAILABLE:
            print_success("Idea model loaded (T/Idea/Model)")
        else:
            print_warning("Idea model not available - some features limited")

        if SCRIPT_WRITER_AVAILABLE:
            print_success("ContentWriter loaded (T/Content)")
        else:
            print_warning("ContentWriter not available - some features limited")

        print()

    def show_menu(self) -> None:
        """Display the main menu options."""
        print_section("Main Menu")

        print(
            f"""
{Colors.BOLD}Idea Management:{Colors.END}
  1. Create new Idea
  2. Load demo Idea
  3. View current Idea
  4. Edit Idea fields

{Colors.BOLD}Title Generation:{Colors.END}
  5. Generate Title from Idea
  6. View current Title

{Colors.BOLD}Content Development:{Colors.END}
  7. Generate Content draft
  8. View current Content
  9. Iterate on Content (unlimited feedback loop)

{Colors.BOLD}Workflow:{Colors.END}
  10. Show workflow status (next to process by lowest version)
  11. Export current content
  12. Reset session

{Colors.BOLD}Help & Info:{Colors.END}
  h.  Show this menu
  s.  Show session summary
  q.  Quit

"""
        )

    def create_idea(self) -> None:
        """Create a new Idea through interactive prompts."""
        if not IDEA_AVAILABLE:
            print_error("Idea model not available. Cannot create Idea.")
            return

        print_section("Create New Idea")

        print("Enter your idea details (press Enter to skip optional fields):\n")

        # Required fields
        title = input(f"{Colors.BOLD}Title{Colors.END} (required): ").strip()
        if not title:
            print_error("Title is required!")
            return

        concept = input(f"{Colors.BOLD}Concept{Colors.END} (required): ").strip()
        if not concept:
            print_error("Concept is required!")
            return

        # Optional story foundation
        print(f"\n{Colors.CYAN}Story Foundation (optional):{Colors.END}")
        premise = input("Premise (1-3 sentences): ").strip()
        logline = input("Logline (one dramatic sentence): ").strip()
        hook = input("Hook (first engaging moment): ").strip()

        # Genre selection
        print(f"\n{Colors.CYAN}Genre:{Colors.END}")
        genres = list(ContentGenre)
        for i, genre in enumerate(genres, 1):
            print(f"  {i}. {genre.value}")
        genre_choice = input("Select genre (1-10, default=10 other): ").strip()
        try:
            genre_idx = int(genre_choice) - 1
            genre = genres[genre_idx] if 0 <= genre_idx < len(genres) else ContentGenre.OTHER
        except ValueError:
            genre = ContentGenre.OTHER

        # Target audience
        target_audience = input("\nTarget audience: ").strip()

        # Create the Idea
        self.current_idea = Idea(
            title=title,
            concept=concept,
            premise=premise,
            logline=logline,
            hook=hook,
            genre=genre,
            target_audience=target_audience,
            created_by="text_client",
        )

        # Increment idea version
        self.idea_version += 1

        self.history.append(
            {
                "action": "create_idea",
                "timestamp": datetime.now().isoformat(),
                "title": title,
                "version": self.idea_version,
            }
        )

        print_success(f"Idea created: '{title}' (version {self.idea_version})")
        self.show_idea()
        self._save_state()

    def load_demo_idea(self) -> None:
        """Load a demo Idea for testing."""
        if not IDEA_AVAILABLE:
            print_error("Idea model not available. Cannot load demo.")
            return

        print_section("Loading Demo Idea")

        self.current_idea = Idea(
            title="The Echo",
            concept="A girl hears a voice that sounds exactly like her own",
            idea="Girl hears voice exactly like hers",
            premise="A teenage girl starts hearing a voice that sounds identical to her own, "
            "giving her warnings about the future. When the warnings come true, "
            "she realizes the voice is her future self trying to prevent her death.",
            logline="A girl discovers she can hear her own future thoughts—and they're telling her to run.",
            hook="Last night I woke up... but my body kept sleeping.",
            skeleton="1. Girl hears strange voice\n2. Voice sounds like her\n3. Voice predicts events\n"
            "4. Predictions come true\n5. Final warning: run now\n6. She realizes too late",
            pov="first person (I) - intimate, strong emotions",
            emotional_arc="curiosity → confusion → fear → terror → realization",
            twist="She's already dead - talking to her past self",
            climax="Final moment when she realizes the truth",
            genre=ContentGenre.HORROR,
            target_audience="Horror enthusiasts aged 18-35",
            target_platforms=["youtube", "tiktok", "medium"],
            target_formats=["video", "audio", "text"],
            length_target="60 seconds video / 500 words text",
            tone_guidance="Start mysterious, build to terrifying, end with shocking twist",
            created_by="demo_loader",
        )

        # Increment idea version
        self.idea_version += 1

        self.history.append(
            {
                "action": "load_demo",
                "timestamp": datetime.now().isoformat(),
                "title": "The Echo",
                "version": self.idea_version,
            }
        )

        print_success(f"Demo Idea loaded: 'The Echo' (version {self.idea_version})")
        self.show_idea()
        self._save_state()

    def show_idea(self) -> None:
        """Display the current Idea."""
        if self.current_idea is None:
            print_warning("No Idea loaded. Create or load one first.")
            return

        print_section("Current Idea")

        idea = self.current_idea
        print(f"{Colors.BOLD}Title:{Colors.END} {idea.title}")
        print(f"{Colors.BOLD}Concept:{Colors.END} {idea.concept}")
        print(f"{Colors.BOLD}Genre:{Colors.END} {idea.genre.value}")
        print(f"{Colors.BOLD}Status:{Colors.END} {idea.status.value}")
        print(f"{Colors.BOLD}Version:{Colors.END} {idea.version}")

        if idea.premise:
            print(f"\n{Colors.BOLD}Premise:{Colors.END}")
            print(f"  {idea.premise}")

        if idea.logline:
            print(f"\n{Colors.BOLD}Logline:{Colors.END}")
            print(f"  {idea.logline}")

        if idea.hook:
            print(f"\n{Colors.BOLD}Hook:{Colors.END}")
            print(f"  {idea.hook}")

        if idea.skeleton:
            print(f"\n{Colors.BOLD}Skeleton:{Colors.END}")
            for line in idea.skeleton.split("\n"):
                print(f"  {line}")

        if idea.target_audience:
            print(f"\n{Colors.BOLD}Target Audience:{Colors.END} {idea.target_audience}")

        if idea.target_platforms:
            print(f"{Colors.BOLD}Platforms:{Colors.END} {', '.join(idea.target_platforms)}")

        print()

    def generate_title(self) -> None:
        """Generate a Title from the current Idea."""
        if self.current_idea is None:
            print_warning("No Idea loaded. Create or load one first.")
            return

        print_section("Generate Title")

        # Simple title generation based on idea fields
        idea = self.current_idea

        # Generate title variants
        variants = []

        # Use existing title as base
        if idea.title:
            variants.append(idea.title)

        # Generate from logline (extract key phrase)
        if idea.logline:
            # Take first part of logline
            logline_title = (
                idea.logline.split("—")[0].strip() if "—" in idea.logline else idea.logline[:50]
            )
            variants.append(logline_title)

        # Generate from concept
        if idea.concept:
            variants.append(idea.concept[:60])

        # Generate hook-based title
        if idea.hook:
            variants.append(f"'{idea.hook[:40]}...'")

        print("Generated Title Variants:")
        for i, variant in enumerate(variants, 1):
            print(f"  {i}. {variant}")

        # Let user select
        choice = input(f"\nSelect title (1-{len(variants)}) or enter custom: ").strip()

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(variants):
                self.current_title = variants[idx]
            else:
                self.current_title = choice
        except ValueError:
            self.current_title = choice if choice else variants[0]

        # Increment title version
        self.title_version += 1

        self.history.append(
            {
                "action": "generate_title",
                "timestamp": datetime.now().isoformat(),
                "title": self.current_title,
                "version": self.title_version,
            }
        )

        print_success(f"Title selected: '{self.current_title}' (version {self.title_version})")
        self._save_state()

    def show_title(self) -> None:
        """Display the current Title."""
        if self.current_title is None:
            print_warning("No Title generated. Generate one first.")
            return

        print_section("Current Title")
        print(f"  {self.current_title}")
        print()

    def generate_content(self) -> None:
        """Generate a Content draft from Idea and Title."""
        if self.current_idea is None:
            print_warning("No Idea loaded. Create or load one first.")
            return

        if self.current_title is None:
            print_warning("No Title generated. Generate one first.")
            return

        print_section("Generate Content Draft")

        idea = self.current_idea

        # Build content structure
        content_parts = []

        # Hook opening
        if idea.hook:
            content_parts.append(f"[HOOK]\n{idea.hook}\n")

        # Main content from skeleton/outline
        if idea.skeleton:
            content_parts.append("[STRUCTURE]")
            for line in idea.skeleton.split("\n"):
                if line.strip():
                    content_parts.append(f"• {line.strip()}")
            content_parts.append("")

        # Emotional arc guidance
        if idea.emotional_arc:
            content_parts.append(f"[EMOTIONAL ARC]\n{idea.emotional_arc}\n")

        # Climax
        if idea.climax:
            content_parts.append(f"[CLIMAX]\n{idea.climax}\n")

        # Twist/Ending
        if idea.twist:
            content_parts.append(f"[TWIST]\n{idea.twist}\n")

        # Tone guidance
        if idea.tone_guidance:
            content_parts.append(f"[TONE GUIDANCE]\n{idea.tone_guidance}\n")

        self.current_content = "\n".join(content_parts)

        # Increment content version
        self.content_version += 1

        # Initialize content writer if available (unlimited iterations)
        if SCRIPT_WRITER_AVAILABLE:
            # Create ContentWriter with a very high max_iterations value to effectively allow unlimited iterations
            # Note: ContentWriter doesn't have a native "unlimited" mode, so we use a large integer
            self.content_writer = ContentWriter(
                writer_id="text_client_writer",
                target_score_threshold=80,
                max_iterations=999999,  # Effectively unlimited
            )
            print_info("ContentWriter initialized for unlimited iteration support")

        self.history.append(
            {
                "action": "generate_content",
                "timestamp": datetime.now().isoformat(),
                "version": self.content_version,
            }
        )

        print_success(f"Content draft generated! (version {self.content_version})")
        self.show_content()
        self._save_state()

    def show_content(self) -> None:
        """Display the current Content."""
        if self.current_content is None:
            print_warning("No Content generated. Generate one first.")
            return

        print_section("Current Content")
        print(self.current_content)

        print(f"\n{Colors.CYAN}Content Version:{Colors.END} {self.content_version}")
        if self.content_writer:
            print(f"{Colors.CYAN}Writer Status:{Colors.END}")
            print(f"  Iteration: {self.content_writer.current_iteration} (unlimited)")
            print(f"  Target Score: {self.content_writer.target_score_threshold}%")

    def iterate_content(self) -> None:
        """Run feedback loop iteration on the content (unlimited iterations)."""
        if self.current_content is None:
            print_warning("No Content generated. Generate one first.")
            return

        if not SCRIPT_WRITER_AVAILABLE:
            print_warning("ContentWriter not available. Cannot iterate.")
            return

        print_section("Content Iteration (Feedback Loop - Unlimited)")

        print("Provide feedback on the current content:")
        print("(Enter areas to improve, or 'skip' for auto-improvement)\n")

        feedback = input("Feedback: ").strip()

        if feedback.lower() != "skip" and feedback:
            # Apply user feedback to content
            self.current_content += (
                f"\n\n[USER FEEDBACK - Iteration {self.content_writer.current_iteration + 1}]\n"
            )
            self.current_content += f"Improvements requested: {feedback}\n"

        # Track iteration and increment content version
        if self.content_writer:
            self.content_writer.current_iteration += 1
        self.content_version += 1

        self.history.append(
            {
                "action": "iterate_content",
                "timestamp": datetime.now().isoformat(),
                "feedback": feedback,
                "version": self.content_version,
            }
        )

        print_success(
            f"Content iteration {self.content_writer.current_iteration} recorded (version {self.content_version})"
        )
        print_info("Unlimited iterations available - continue as needed")
        self._save_state()

    def get_next_to_process(self) -> str:
        """Get the item type with lowest version count for next processing.

        The workflow prioritizes items with the lowest version count to ensure
        balanced progression. When multiple items have the same version count,
        the priority order is: Idea > Title > Content (following the natural
        workflow sequence).

        Returns:
            The name of the item type (Idea, Title, or Content) with lowest version.
            On tie, returns in workflow order: Idea first, then Title, then Content.
        """
        # List in workflow priority order - when versions are equal, earlier items win
        versions = [
            ("Idea", self.idea_version),
            ("Title", self.title_version),
            ("Content", self.content_version),
        ]
        # Sort by version count (ascending); stable sort preserves original order on ties
        versions.sort(key=lambda x: x[1])
        return versions[0][0]

    def show_workflow_status(self) -> None:
        """Display current workflow status with version tracking."""
        print_section("Workflow Status")

        stages = [
            ("Idea", self.current_idea is not None, self.idea_version),
            ("Title", self.current_title is not None, self.title_version),
            ("Content", self.current_content is not None, self.content_version),
        ]

        print(f"\n{Colors.BOLD}Content Status & Version Counts:{Colors.END}")
        for stage, completed, version in stages:
            status = (
                f"{Colors.GREEN}✓{Colors.END}" if completed else f"{Colors.YELLOW}○{Colors.END}"
            )
            print(f"  {status} {stage}: version {version}")

        # Show recommendation for next item to process (lowest version)
        next_item = self.get_next_to_process()
        print(f"\n{Colors.CYAN}➤ Next to process (lowest version):{Colors.END} {next_item}")

        print(f"\n{Colors.BOLD}Session Duration:{Colors.END} {datetime.now() - self.session_start}")
        print(f"{Colors.BOLD}Actions Taken:{Colors.END} {len(self.history)}")

    def export_content(self) -> None:
        """Export current content to a file."""
        print_section("Export Content")

        if not any([self.current_idea, self.current_title, self.current_content]):
            print_warning("No content to export.")
            return

        filename = input("Export filename (default: prismq_export.txt): ").strip()
        filename = filename if filename else "prismq_export.txt"

        content = []
        content.append(f"PrismQ.T Export - {datetime.now().isoformat()}")
        content.append("=" * 60)

        if self.current_idea:
            content.append("\n[IDEA]")
            content.append(f"Title: {self.current_idea.title}")
            content.append(f"Concept: {self.current_idea.concept}")
            if self.current_idea.premise:
                content.append(f"Premise: {self.current_idea.premise}")

        if self.current_title:
            content.append(f"\n[TITLE]\n{self.current_title}")

        if self.current_content:
            content.append(f"\n[SCRIPT]\n{self.current_content}")

        # Write to file
        export_path = Path.cwd() / filename
        with open(export_path, "w", encoding="utf-8") as f:
            f.write("\n".join(content))

        print_success(f"Content exported to: {export_path}")

    def reset_session(self) -> None:
        """Reset the session."""
        print_section("Reset Session")

        confirm = input("Are you sure you want to reset? (y/n): ").strip().lower()
        if confirm == "y":
            self.current_idea = None
            self.current_title = None
            self.current_content = None
            self.content_writer = None
            self.history.clear()
            self.session_start = datetime.now()
            # Reset version counts
            self.idea_version = 0
            self.title_version = 0
            self.content_version = 0
            # Clear state file
            self.clear_state()
            print_success("Session reset! (all versions reset to 0)")
        else:
            print_info("Reset cancelled.")

    def show_session_summary(self) -> None:
        """Display session summary."""
        print_section("Session Summary")

        print(f"{Colors.BOLD}Started:{Colors.END} {self.session_start.isoformat()}")
        print(f"{Colors.BOLD}Duration:{Colors.END} {datetime.now() - self.session_start}")
        print(f"{Colors.BOLD}Actions:{Colors.END} {len(self.history)}")

        if self.history:
            print(f"\n{Colors.BOLD}Action History:{Colors.END}")
            for i, action in enumerate(self.history[-10:], 1):  # Show last 10
                print(f"  {i}. {action['action']} - {action['timestamp']}")

    def _run_interactive_loop(self) -> None:
        """Run the interactive command loop.

        This is the core command processing loop, separated from run() so it can
        be reused when demo mode pre-loads data before starting the loop.
        """
        while True:
            try:
                choice = input(f"{Colors.BOLD}> {Colors.END}").strip().lower()

                if choice == "1":
                    self.create_idea()
                elif choice == "2":
                    self.load_demo_idea()
                elif choice == "3":
                    self.show_idea()
                elif choice == "4":
                    print_info("Edit functionality - use create_idea to modify")
                elif choice == "5":
                    self.generate_title()
                elif choice == "6":
                    self.show_title()
                elif choice == "7":
                    self.generate_content()
                elif choice == "8":
                    self.show_content()
                elif choice == "9":
                    self.iterate_content()
                elif choice == "10":
                    self.show_workflow_status()
                elif choice == "11":
                    self.export_content()
                elif choice == "12":
                    self.reset_session()
                elif choice in ("h", "help", "menu"):
                    self.show_menu()
                elif choice == "s":
                    self.show_session_summary()
                elif choice in ("q", "quit", "exit"):
                    print_info("Thank you for using PrismQ.T Text Client!")
                    break
                elif choice == "":
                    continue
                else:
                    print_warning(f"Unknown command: '{choice}'. Type 'h' for help.")

            except KeyboardInterrupt:
                print("\n")
                print_info("Use 'q' to quit.")
            except EOFError:
                print_info("\nGoodbye!")
                break

    def run(self) -> None:
        """Run the interactive client."""
        self.show_welcome()
        self.show_menu()
        self._run_interactive_loop()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        decontention="PrismQ.T Interactive Text Client",
        formatter_class=argparse.RawDecontentionHelpFormatter,
        epilog="""
Examples:
  python run_text_client.py                    # Start interactive client
  python run_text_client.py --demo             # Start with demo data loaded
  python run_text_client.py --check            # Check module availability
  python run_text_client.py --action create_idea    # Run create idea step
  python run_text_client.py --action generate_title # Run generate title step
  python run_text_client.py --action generate_content # Run generate content step
  python run_text_client.py --action iterate_content  # Run iterate content step
  python run_text_client.py --action export          # Export content
  python run_text_client.py --action status          # Show workflow status
  python run_text_client.py --action load_demo       # Load demo idea
  python run_text_client.py --action reset           # Reset session and clear state
        """,
    )

    parser.add_argument("--demo", action="store_true", help="Start with demo Idea loaded")
    parser.add_argument("--check", action="store_true", help="Check module availability and exit")
    parser.add_argument(
        "--action",
        type=str,
        choices=[
            "create_idea",
            "generate_title",
            "generate_content",
            "iterate_content",
            "export",
            "status",
            "load_demo",
            "reset",
        ],
        help="Run a specific action (for batch content workflows)",
    )

    args = parser.parse_args()

    if args.check:
        print("PrismQ.T Module Availability Check")
        print("=" * 40)
        print(f"Idea Model:    {'✓ Available' if IDEA_AVAILABLE else '✗ Not available'}")
        print(f"ContentWriter:  {'✓ Available' if SCRIPT_WRITER_AVAILABLE else '✗ Not available'}")
        print(f"\nRepository Root: {REPO_ROOT}")
        print(f"T Module Root:   {T_ROOT}")
        return

    # Handle --action mode for batch contents (each step as separate process)
    if args.action:
        # Load state from previous steps
        client = TextClient(load_state=True)

        action_map = {
            "create_idea": client.create_idea,
            "generate_title": client.generate_title,
            "generate_content": client.generate_content,
            "iterate_content": client.iterate_content,
            "export": client.export_content,
            "status": client.show_workflow_status,
            "load_demo": client.load_demo_idea,
            "reset": lambda: (client.reset_session(), client.clear_state()),
        }

        action_func = action_map.get(args.action)
        if action_func:
            print_header(f"PrismQ.T - {args.action.replace('_', ' ').title()}")
            action_func()
        else:
            print_error(f"Unknown action: {args.action}")
            sys.exit(1)
        return

    client = TextClient()

    if args.demo:
        # Pre-load demo data before starting interactive session
        client.show_welcome()
        client.load_demo_idea()
        client.show_menu()
        # Continue with normal interactive loop (client.run starts its own loop)
        client._run_interactive_loop()
    else:
        client.run()


if __name__ == "__main__":
    main()
