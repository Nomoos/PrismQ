"""Tests for StoryTranslation model and multi-language support."""

from datetime import datetime

import pytest

from src.story_translation import StoryTranslation, TranslationStatus


class TestStoryTranslationBasic:
    """Test basic StoryTranslation functionality."""

    def test_create_basic_translation(self):
        """Test creating a basic translation."""
        translation = StoryTranslation(
            story_id=42,
            language_code="cs",
            title="Testovací Příběh",
            text="Toto je testovací text příběhu v češtině.",
        )

        assert translation.story_id == 42
        assert translation.language_code == "cs"
        assert translation.title == "Testovací Příběh"
        assert translation.text == "Toto je testovací text příběhu v češtině."
        assert translation.status == TranslationStatus.DRAFT
        assert translation.iteration_count == 0
        assert translation.max_iterations == 2
        assert translation.translator_id is None
        assert translation.reviewer_id is None
        assert translation.feedback_history == []
        assert translation.last_feedback == ""
        assert translation.meaning_verified is False
        assert translation.translated_from == "en"
        assert translation.version == 1
        assert translation.created_at is not None
        assert translation.updated_at is not None
        assert translation.approved_at is None
        assert translation.published_at is None

    def test_create_with_all_fields(self):
        """Test creating translation with all fields."""
        translation = StoryTranslation(
            story_id=42,
            language_code="es",
            title="Historia de Prueba",
            text="Este es el texto de prueba en español.",
            status=TranslationStatus.APPROVED,
            iteration_count=1,
            max_iterations=3,
            translator_id="AI-Translator-GPT4",
            reviewer_id="AI-Reviewer-Claude",
            feedback_history=[{"iteration": 1, "issues": []}],
            last_feedback="Approved",
            meaning_verified=True,
            translated_from="en",
            version=2,
            notes="Test translation",
        )

        assert translation.story_id == 42
        assert translation.language_code == "es"
        assert translation.status == TranslationStatus.APPROVED
        assert translation.iteration_count == 1
        assert translation.max_iterations == 3
        assert translation.translator_id == "AI-Translator-GPT4"
        assert translation.reviewer_id == "AI-Reviewer-Claude"
        assert translation.meaning_verified is True
        assert translation.version == 2

    def test_timestamps_auto_generated(self):
        """Test that timestamps are automatically generated."""
        translation = StoryTranslation(
            story_id=1, language_code="de", title="Test", text="Test text"
        )

        assert translation.created_at is not None
        assert translation.updated_at is not None

        # Verify ISO format
        try:
            datetime.fromisoformat(translation.created_at)
            datetime.fromisoformat(translation.updated_at)
        except ValueError:
            pytest.fail("Timestamps should be in ISO format")


class TestTranslationFeedbackLoop:
    """Test feedback loop functionality."""

    def test_add_feedback_with_issues(self):
        """Test adding feedback with issues found."""
        translation = StoryTranslation(
            story_id=42, language_code="cs", title="Test", text="Original text"
        )

        translation.add_feedback(
            reviewer_id="AI-Reviewer-1",
            issues=["Missing context in paragraph 2", "Tone mismatch in conclusion"],
            suggestions=["Add contextual phrase", "Adjust tone to match original"],
            meaning_score=75,
            notes="Good attempt but needs revision",
        )

        assert translation.iteration_count == 1
        assert translation.reviewer_id == "AI-Reviewer-1"
        assert translation.status == TranslationStatus.REVISION_NEEDED
        assert translation.meaning_verified is False
        assert len(translation.feedback_history) == 1
        assert translation.feedback_history[0]["reviewer_id"] == "AI-Reviewer-1"
        assert len(translation.feedback_history[0]["issues"]) == 2
        assert translation.last_feedback == "Iteration 1: 2 issues found"
        assert translation.approved_at is None

    def test_add_feedback_approved(self):
        """Test adding feedback that approves translation."""
        translation = StoryTranslation(
            story_id=42, language_code="fr", title="Test", text="Texte français"
        )

        translation.add_feedback(
            reviewer_id="AI-Reviewer-1",
            issues=[],
            suggestions=[],
            meaning_score=95,
            notes="Perfect translation, meaning preserved",
        )

        assert translation.iteration_count == 1
        assert translation.status == TranslationStatus.APPROVED
        assert translation.meaning_verified is True
        assert translation.approved_at is not None
        assert len(translation.feedback_history) == 1

    def test_feedback_loop_multiple_iterations(self):
        """Test multiple feedback iterations."""
        translation = StoryTranslation(
            story_id=42, language_code="de", title="Test", text="Original"
        )

        # First iteration - needs revision
        translation.add_feedback(
            reviewer_id="AI-Reviewer-1", issues=["Issue 1"], suggestions=["Fix 1"], meaning_score=70
        )
        assert translation.iteration_count == 1
        assert translation.status == TranslationStatus.REVISION_NEEDED

        # Second iteration - still needs revision
        translation.add_feedback(
            reviewer_id="AI-Reviewer-1", issues=["Issue 2"], suggestions=["Fix 2"], meaning_score=80
        )
        assert translation.iteration_count == 2
        assert translation.status == TranslationStatus.REVISION_NEEDED

        # Third iteration - approved
        translation.add_feedback(
            reviewer_id="AI-Reviewer-1", issues=[], suggestions=[], meaning_score=92
        )
        assert translation.iteration_count == 3
        assert translation.status == TranslationStatus.APPROVED
        assert translation.meaning_verified is True
        assert len(translation.feedback_history) == 3

    def test_can_request_revision(self):
        """Test checking if revision is allowed."""
        translation = StoryTranslation(
            story_id=42, language_code="cs", title="Test", text="Text", max_iterations=2
        )

        # Initially can request
        assert translation.can_request_revision() is True

        # After first iteration
        translation.add_feedback("reviewer", ["issue"], ["fix"])
        assert translation.iteration_count == 1
        assert translation.can_request_revision() is True

        # After second iteration (max reached)
        translation.add_feedback("reviewer", ["issue"], ["fix"])
        assert translation.iteration_count == 2
        assert translation.can_request_revision() is False

    def test_max_iterations_limit(self):
        """Test that max_iterations limits feedback loop."""
        translation = StoryTranslation(
            story_id=42, language_code="es", title="Test", text="Text", max_iterations=2
        )

        # Can add feedback up to max_iterations
        translation.add_feedback("reviewer", ["issue1"], [])
        translation.add_feedback("reviewer", ["issue2"], [])

        # Reached max - can still add more but should stop externally
        assert translation.iteration_count == 2
        assert not translation.can_request_revision()


class TestTranslationWorkflow:
    """Test translation workflow states."""

    def test_submit_for_review(self):
        """Test submitting translation for review."""
        translation = StoryTranslation(story_id=42, language_code="cs", title="Test", text="Text")

        assert translation.status == TranslationStatus.DRAFT

        translation.submit_for_review()

        assert translation.status == TranslationStatus.PENDING_REVIEW
        assert translation.updated_at is not None

    def test_approve_translation(self):
        """Test approving translation."""
        translation = StoryTranslation(story_id=42, language_code="fr", title="Test", text="Texte")

        translation.approve(reviewer_id="AI-Reviewer-1")

        assert translation.status == TranslationStatus.APPROVED
        assert translation.meaning_verified is True
        assert translation.reviewer_id == "AI-Reviewer-1"
        assert translation.approved_at is not None

    def test_publish_approved_translation(self):
        """Test publishing an approved translation."""
        translation = StoryTranslation(
            story_id=42,
            language_code="de",
            title="Test",
            text="Text",
            status=TranslationStatus.APPROVED,
        )

        translation.publish()

        assert translation.status == TranslationStatus.PUBLISHED
        assert translation.published_at is not None

    def test_publish_unapproved_raises_error(self):
        """Test that publishing unapproved translation raises error."""
        translation = StoryTranslation(
            story_id=42,
            language_code="cs",
            title="Test",
            text="Text",
            status=TranslationStatus.DRAFT,
        )

        with pytest.raises(ValueError, match="Cannot publish translation that is not approved"):
            translation.publish()

    def test_update_content(self):
        """Test updating translation content."""
        translation = StoryTranslation(
            story_id=42, language_code="cs", title="Original Title", text="Original text", version=1
        )

        translation.update_content(title="Updated Title", text="Updated text")

        assert translation.title == "Updated Title"
        assert translation.text == "Updated text"
        assert translation.version == 2

    def test_update_content_partial(self):
        """Test updating only title or text."""
        translation = StoryTranslation(
            story_id=42, language_code="es", title="Title", text="Text", version=1
        )

        # Update only title
        translation.update_content(title="New Title")
        assert translation.title == "New Title"
        assert translation.text == "Text"
        assert translation.version == 2

        # Update only text
        translation.update_content(text="New Text")
        assert translation.title == "New Title"
        assert translation.text == "New Text"
        assert translation.version == 3


class TestTranslationSerialization:
    """Test serialization and deserialization."""

    def test_to_dict(self):
        """Test converting translation to dictionary."""
        translation = StoryTranslation(
            story_id=42,
            language_code="cs",
            title="Test",
            text="Text",
            status=TranslationStatus.APPROVED,
            translator_id="AI-Translator",
            iteration_count=1,
        )

        data = translation.to_dict()

        assert isinstance(data, dict)
        assert data["story_id"] == 42
        assert data["language_code"] == "cs"
        assert data["title"] == "Test"
        assert data["text"] == "Text"
        assert data["status"] == "approved"  # Converted to string
        assert data["translator_id"] == "AI-Translator"
        assert data["iteration_count"] == 1

    def test_from_dict(self):
        """Test creating translation from dictionary."""
        data = {
            "story_id": 42,
            "language_code": "fr",
            "title": "Titre",
            "text": "Texte",
            "status": "pending_review",
            "iteration_count": 2,
            "translator_id": "AI-Trans",
            "reviewer_id": "AI-Rev",
            "version": 3,
        }

        translation = StoryTranslation.from_dict(data)

        assert translation.story_id == 42
        assert translation.language_code == "fr"
        assert translation.title == "Titre"
        assert translation.text == "Texte"
        assert translation.status == TranslationStatus.PENDING_REVIEW
        assert translation.iteration_count == 2
        assert translation.translator_id == "AI-Trans"
        assert translation.reviewer_id == "AI-Rev"
        assert translation.version == 3

    def test_roundtrip_serialization(self):
        """Test that to_dict -> from_dict preserves data."""
        original = StoryTranslation(
            story_id=42,
            language_code="de",
            title="German Title",
            text="German text with ümlaut",
            status=TranslationStatus.REVISION_NEEDED,
            iteration_count=1,
            max_iterations=2,
            translator_id="AI-Trans-1",
            reviewer_id="AI-Rev-1",
            feedback_history=[{"iteration": 1, "issues": ["Issue 1"]}],
            last_feedback="Needs work",
            meaning_verified=False,
            translated_from="en",
            version=2,
            notes="Test notes",
        )

        # Roundtrip
        data = original.to_dict()
        restored = StoryTranslation.from_dict(data)

        # Compare key fields
        assert restored.story_id == original.story_id
        assert restored.language_code == original.language_code
        assert restored.title == original.title
        assert restored.text == original.text
        assert restored.status == original.status
        assert restored.iteration_count == original.iteration_count
        assert restored.max_iterations == original.max_iterations
        assert restored.translator_id == original.translator_id
        assert restored.reviewer_id == original.reviewer_id
        assert restored.feedback_history == original.feedback_history
        assert restored.last_feedback == original.last_feedback
        assert restored.meaning_verified == original.meaning_verified
        assert restored.translated_from == original.translated_from
        assert restored.version == original.version
        assert restored.notes == original.notes


class TestTranslationEnums:
    """Test enum functionality."""

    def test_translation_status_values(self):
        """Test TranslationStatus enum values."""
        assert TranslationStatus.DRAFT.value == "draft"
        assert TranslationStatus.PENDING_REVIEW.value == "pending_review"
        assert TranslationStatus.REVISION_NEEDED.value == "revision_needed"
        assert TranslationStatus.APPROVED.value == "approved"
        assert TranslationStatus.PUBLISHED.value == "published"


class TestTranslationRepresentation:
    """Test string representation."""

    def test_repr(self):
        """Test __repr__ method."""
        translation = StoryTranslation(
            story_id=42,
            language_code="cs",
            title="Test",
            text="Text",
            status=TranslationStatus.APPROVED,
            iteration_count=2,
            max_iterations=2,
            meaning_verified=True,
        )

        repr_str = repr(translation)

        assert "StoryTranslation(" in repr_str
        assert "story_id=42" in repr_str
        assert "lang=cs" in repr_str
        assert "status=approved" in repr_str
        assert "iterations=2/2" in repr_str
        assert "verified=True" in repr_str


class TestMultiLanguageScenarios:
    """Test real-world multi-language scenarios."""

    def test_same_story_multiple_languages(self):
        """Test creating multiple translations for same story."""
        story_id = 42

        # English original
        en_title = "The Echo"
        en_text = "Last night I woke up... but my body kept sleeping."

        # Czech translation
        cs_translation = StoryTranslation(
            story_id=story_id,
            language_code="cs",
            title="Echo",
            text="Včera v noci jsem se probudila... ale mé tělo dál spalo.",
            translated_from="en",
        )

        # Spanish translation
        es_translation = StoryTranslation(
            story_id=story_id,
            language_code="es",
            title="El Eco",
            text="Anoche me desperté... pero mi cuerpo siguió durmiendo.",
            translated_from="en",
        )

        # German translation
        de_translation = StoryTranslation(
            story_id=story_id,
            language_code="de",
            title="Das Echo",
            text="Letzte Nacht bin ich aufgewacht... aber mein Körper schlief weiter.",
            translated_from="en",
        )

        # All share same story_id
        assert cs_translation.story_id == story_id
        assert es_translation.story_id == story_id
        assert de_translation.story_id == story_id

        # But different language codes
        assert cs_translation.language_code == "cs"
        assert es_translation.language_code == "es"
        assert de_translation.language_code == "de"

    def test_translation_feedback_workflow_complete(self):
        """Test complete translation workflow with feedback."""
        # Initial translation
        translation = StoryTranslation(
            story_id=42,
            language_code="cs",
            title="Kvantové Počítače",
            text="Jak kvantové počítače skutečně fungují...",
            translator_id="AI-Translator-GPT4",
        )

        # Submit for review
        translation.submit_for_review()
        assert translation.status == TranslationStatus.PENDING_REVIEW

        # First review - needs revision
        translation.add_feedback(
            reviewer_id="AI-Reviewer-Claude",
            issues=[
                "Technical term 'superposition' translated incorrectly",
                "Missing context in paragraph 3",
            ],
            suggestions=[
                "Use 'superpozice' instead of 'překrytí'",
                "Add phrase about quantum states",
            ],
            meaning_score=75,
            notes="Good structure but terminology needs work",
        )

        assert translation.status == TranslationStatus.REVISION_NEEDED
        assert translation.iteration_count == 1
        assert translation.can_request_revision() is True

        # Translator revises
        translation.update_content(text="Jak kvantové počítače skutečně fungují... superpozice...")
        translation.submit_for_review()

        # Second review - approved
        translation.add_feedback(
            reviewer_id="AI-Reviewer-Claude",
            issues=[],
            suggestions=[],
            meaning_score=92,
            notes="Perfect! Meaning preserved, terminology correct",
        )

        assert translation.status == TranslationStatus.APPROVED
        assert translation.meaning_verified is True
        assert translation.iteration_count == 2

        # Publish
        translation.publish()
        assert translation.status == TranslationStatus.PUBLISHED
        assert translation.published_at is not None
