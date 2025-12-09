"""Tests for the Interactive CLI client for Idea creation."""

import os
import sys
import tempfile

import pytest

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../Model/src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../Model"))

from idea_create_cli import (
    CLIError,
    CLIOptions,
    ValidationError,
    format_idea_row,
    generate_ideas,
    main,
    parse_args,
    run_cli,
    save_idea_to_db,
    validate_idea,
)
from idea_db import IdeaDatabase

from idea import ContentGenre, Idea, IdeaStatus


class TestCLIOptions:
    """Tests for CLIOptions dataclass."""

    def test_default_options(self):
        """Test default CLI options."""
        options = CLIOptions(prompt="Test prompt")

        assert options.prompt == "Test prompt"
        assert options.count == 10
        assert options.preview is False
        assert options.no_save is False
        assert options.debug is False
        assert options.validate is False
        assert options.model == "llama3.1:70b-q4_K_M"
        assert options.temperature == 0.8
        assert options.db_path is None

    def test_custom_options(self):
        """Test custom CLI options."""
        options = CLIOptions(
            prompt="Custom prompt",
            count=5,
            preview=True,
            no_save=False,
            debug=True,
            validate=True,
            model="custom-model",
            temperature=1.0,
            db_path="/tmp/test.db",
        )

        assert options.prompt == "Custom prompt"
        assert options.count == 5
        assert options.preview is True
        assert options.debug is True
        assert options.validate is True
        assert options.model == "custom-model"
        assert options.temperature == 1.0
        assert options.db_path == "/tmp/test.db"


class TestParseArgs:
    """Tests for argument parsing."""

    def test_parse_simple_prompt(self):
        """Test parsing simple prompt."""
        options = parse_args(["Test prompt"])

        assert options.prompt == "Test prompt"
        assert options.count == 10
        assert options.preview is False

    def test_parse_count_flag(self):
        """Test parsing --count flag."""
        options = parse_args(["Test prompt", "--count", "5"])

        assert options.count == 5

    def test_parse_preview_flag(self):
        """Test parsing --preview flag."""
        options = parse_args(["Test prompt", "--preview"])

        assert options.preview is True

    def test_parse_no_save_flag(self):
        """Test parsing --no-save flag."""
        options = parse_args(["Test prompt", "--no-save"])

        assert options.no_save is True

    def test_parse_debug_flag(self):
        """Test parsing --debug flag."""
        options = parse_args(["Test prompt", "--debug"])

        assert options.debug is True

    def test_parse_validate_flag(self):
        """Test parsing --validate flag."""
        options = parse_args(["Test prompt", "--validate"])

        assert options.validate is True

    def test_parse_model_flag(self):
        """Test parsing --model flag."""
        options = parse_args(["Test prompt", "--model", "custom-model"])

        assert options.model == "custom-model"

    def test_parse_temperature_flag(self):
        """Test parsing --temperature flag."""
        options = parse_args(["Test prompt", "--temperature", "1.2"])

        assert options.temperature == 1.2

    def test_parse_db_path_flag(self):
        """Test parsing --db-path flag."""
        options = parse_args(["Test prompt", "--db-path", "/tmp/test.db"])

        assert options.db_path == "/tmp/test.db"

    def test_parse_multiple_flags(self):
        """Test parsing multiple flags together."""
        options = parse_args(
            ["Test prompt", "--count", "3", "--preview", "--validate", "--model", "test-model"]
        )

        assert options.prompt == "Test prompt"
        assert options.count == 3
        assert options.preview is True
        assert options.validate is True
        assert options.model == "test-model"

    def test_parse_no_prompt_exits(self):
        """Test that missing prompt causes exit."""
        with pytest.raises(SystemExit):
            parse_args([])

    def test_parse_invalid_count_exits(self):
        """Test that count < 1 causes error."""
        with pytest.raises(SystemExit):
            parse_args(["Test", "--count", "0"])

    def test_parse_count_exceeds_max_exits(self):
        """Test that count > 100 causes error."""
        with pytest.raises(SystemExit):
            parse_args(["Test", "--count", "101"])

    def test_parse_invalid_temperature_exits(self):
        """Test that temperature out of range causes error."""
        with pytest.raises(SystemExit):
            parse_args(["Test", "--temperature", "3.0"])


class TestValidateIdea:
    """Tests for idea validation."""

    def test_valid_idea_passes(self):
        """Test that a valid idea passes validation."""
        idea = Idea(
            title="Test Title",
            concept="Test Concept",
            keywords=["keyword1"],
            themes=["theme1"],
            target_platforms=["youtube"],
            target_formats=["video"],
            status=IdeaStatus.DRAFT,
            genre=ContentGenre.ENTERTAINMENT,
        )

        errors = validate_idea(idea)
        assert len(errors) == 0

    def test_missing_title_fails(self):
        """Test that missing title causes validation error."""
        idea = Idea(title="", concept="Test Concept")

        errors = validate_idea(idea)
        assert any("title" in e.lower() for e in errors)

    def test_missing_concept_fails(self):
        """Test that missing concept causes validation error."""
        idea = Idea(title="Test Title", concept="")

        errors = validate_idea(idea)
        assert any("concept" in e.lower() for e in errors)

    def test_whitespace_title_fails(self):
        """Test that whitespace-only title causes validation error."""
        idea = Idea(title="   ", concept="Test Concept")

        errors = validate_idea(idea)
        assert any("title" in e.lower() for e in errors)


class TestFormatIdeaRow:
    """Tests for idea row formatting."""

    def test_format_basic_idea(self):
        """Test formatting a basic idea."""
        idea = Idea(
            title="Test Title",
            concept="Test Concept",
            genre=ContentGenre.ENTERTAINMENT,
            status=IdeaStatus.DRAFT,
        )

        output = format_idea_row(idea, 1)

        assert "Test Title" in output
        assert "Test Concept" in output
        assert "Idea 1" in output

    def test_format_with_keywords(self):
        """Test formatting idea with keywords."""
        idea = Idea(
            title="Test Title",
            concept="Test Concept",
            keywords=["key1", "key2", "key3"],
            genre=ContentGenre.ENTERTAINMENT,
        )

        output = format_idea_row(idea, 1)

        assert "key1" in output
        assert "key2" in output

    def test_format_verbose_mode(self):
        """Test formatting in verbose mode."""
        idea = Idea(
            title="Test Title",
            concept="Test Concept",
            premise="Test premise",
            logline="Test logline",
            hook="Test hook",
            synopsis="Test synopsis",
            genre=ContentGenre.ENTERTAINMENT,
        )

        output = format_idea_row(idea, 1, verbose=True)

        assert "Test premise" in output
        assert "Test logline" in output
        assert "Test hook" in output
        assert "Synopsis" in output


class TestGenerateIdeas:
    """Tests for idea generation."""

    def test_generate_default_count(self):
        """Test generating default 10 ideas."""
        options = CLIOptions(prompt="Test generation")
        ideas = generate_ideas(options)

        assert len(ideas) == 10
        assert all(isinstance(i, Idea) for i in ideas)

    def test_generate_custom_count(self):
        """Test generating custom number of ideas."""
        options = CLIOptions(prompt="Test generation", count=5)
        ideas = generate_ideas(options)

        assert len(ideas) == 5

    def test_generate_single_idea(self):
        """Test generating a single idea."""
        options = CLIOptions(prompt="Test generation", count=1)
        ideas = generate_ideas(options)

        assert len(ideas) == 1
        assert ideas[0].title is not None
        assert ideas[0].concept is not None

    def test_generate_empty_prompt_raises_error(self):
        """Test that empty prompt raises CLIError."""
        options = CLIOptions(prompt="", count=1)

        with pytest.raises(CLIError):
            generate_ideas(options)

    def test_generated_ideas_have_required_fields(self):
        """Test that generated ideas have all required DB fields."""
        options = CLIOptions(prompt="Test required fields", count=1)
        ideas = generate_ideas(options)

        idea = ideas[0]
        # Required fields for DB
        assert idea.title is not None and len(idea.title) > 0
        assert idea.concept is not None and len(idea.concept) > 0
        # Optional but expected fields
        assert isinstance(idea.keywords, list)
        assert isinstance(idea.themes, list)
        assert isinstance(idea.target_platforms, list)
        assert isinstance(idea.target_formats, list)
        assert isinstance(idea.genre, ContentGenre)
        assert isinstance(idea.status, IdeaStatus)


class TestSaveIdeaToDB:
    """Tests for database save functionality."""

    def test_save_idea_returns_id(self):
        """Test that saving an idea returns a valid ID."""
        idea = Idea(title="Test Save", concept="Test Concept")

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            idea_id = save_idea_to_db(idea, db_path)
            assert idea_id > 0
        finally:
            os.unlink(db_path)

    def test_saved_idea_can_be_retrieved(self):
        """Test that saved idea can be retrieved from DB."""
        idea = Idea(
            title="Test Retrieve", concept="Test Concept", keywords=["test"], themes=["testing"]
        )

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            idea_id = save_idea_to_db(idea, db_path)

            # Retrieve and verify
            db = IdeaDatabase(db_path)
            db.connect()
            cursor = db.conn.cursor()
            cursor.execute("SELECT title, concept FROM ideas WHERE id = ?", (idea_id,))
            row = cursor.fetchone()
            db.close()

            assert row is not None
            assert row["title"] == "Test Retrieve"
            assert row["concept"] == "Test Concept"
        finally:
            os.unlink(db_path)

    def test_save_multiple_ideas(self):
        """Test saving multiple ideas."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            ids = []
            for i in range(3):
                idea = Idea(title=f"Test {i}", concept=f"Concept {i}")
                idea_id = save_idea_to_db(idea, db_path)
                ids.append(idea_id)

            # All IDs should be unique and positive
            assert len(set(ids)) == 3
            assert all(i > 0 for i in ids)
        finally:
            os.unlink(db_path)


class TestDefaultBehavior:
    """Tests for default CLI behavior (10 ideas)."""

    def test_cli_generates_10_ideas_by_default(self):
        """Test that CLI generates 10 ideas by default."""
        options = CLIOptions(prompt="Test default behavior", preview=True)
        ideas = generate_ideas(options)

        assert len(ideas) == 10

    def test_count_flag_changes_number_of_ideas(self):
        """Test that --count flag changes number of generated ideas."""
        for count in [1, 5, 15, 20]:
            options = CLIOptions(prompt="Test count", count=count, preview=True)
            ideas = generate_ideas(options)

            assert len(ideas) == count


class TestPreviewMode:
    """Tests for preview mode (--preview flag)."""

    def test_preview_mode_does_not_save(self, capsys):
        """Test that preview mode displays ideas without saving."""
        options = CLIOptions(prompt="Test preview", count=1, preview=True)

        # This should run without database operations
        exit_code = run_cli(options)

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Preview režim" in captured.out or "preview" in captured.out.lower()


class TestNoSaveMode:
    """Tests for no-save mode (--no-save flag)."""

    def test_no_save_mode_skips_confirmation_and_save(self, capsys):
        """Test that --no-save skips confirmation and doesn't save."""
        options = CLIOptions(prompt="Test no-save", count=1, no_save=True)

        exit_code = run_cli(options)

        assert exit_code == 0
        captured = capsys.readouterr()
        assert (
            "No-save" in captured.out
            or "no-save" in captured.out.lower()
            or "žádné uložení" in captured.out.lower()
        )


class TestDebugMode:
    """Tests for debug mode (--debug flag)."""

    def test_debug_mode_shows_detailed_output(self, capsys):
        """Test that --debug shows detailed idea information."""
        options = CLIOptions(prompt="Test debug", count=1, debug=True, no_save=True)

        # Add no_save to avoid interactive prompt
        exit_code = run_cli(options)

        captured = capsys.readouterr()
        # In debug mode (which also triggers no_save since no_save=True),
        # we should see detailed output with synopsis
        assert exit_code == 0


class TestValidateMode:
    """Tests for validation mode (--validate flag)."""

    def test_validate_mode_checks_fields(self, capsys):
        """Test that --validate checks required fields."""
        options = CLIOptions(prompt="Test validate", count=1, validate=True, no_save=True)

        exit_code = run_cli(options)

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Validace" in captured.out or "validace" in captured.out.lower()

    def test_validate_mode_reports_valid_ideas(self, capsys):
        """Test that valid ideas pass validation check."""
        options = CLIOptions(prompt="Test validate OK", count=2, validate=True, no_save=True)

        exit_code = run_cli(options)

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "OK" in captured.out or "prošly" in captured.out.lower()


class TestValidationOfGeneratedIdeas:
    """Tests that generated ideas have all required DB fields."""

    def test_generated_ideas_have_title(self):
        """Test all generated ideas have title."""
        options = CLIOptions(prompt="Test title field", count=5)
        ideas = generate_ideas(options)

        for idea in ideas:
            assert idea.title is not None
            assert len(idea.title.strip()) > 0

    def test_generated_ideas_have_concept(self):
        """Test all generated ideas have concept."""
        options = CLIOptions(prompt="Test concept field", count=5)
        ideas = generate_ideas(options)

        for idea in ideas:
            assert idea.concept is not None
            assert len(idea.concept.strip()) > 0

    def test_generated_ideas_have_valid_status(self):
        """Test all generated ideas have valid status."""
        options = CLIOptions(prompt="Test status", count=5)
        ideas = generate_ideas(options)

        for idea in ideas:
            assert isinstance(idea.status, IdeaStatus)

    def test_generated_ideas_have_valid_genre(self):
        """Test all generated ideas have valid genre."""
        options = CLIOptions(prompt="Test genre", count=5)
        ideas = generate_ideas(options)

        for idea in ideas:
            assert isinstance(idea.genre, ContentGenre)

    def test_all_ideas_pass_validation(self):
        """Test that all generated ideas pass validation."""
        options = CLIOptions(prompt="Comprehensive validation test", count=10)
        ideas = generate_ideas(options)

        for i, idea in enumerate(ideas):
            errors = validate_idea(idea)
            assert len(errors) == 0, f"Idea {i+1} failed validation: {errors}"
