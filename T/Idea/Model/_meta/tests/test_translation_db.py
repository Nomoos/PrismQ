"""Tests for database translation management."""

import os
import tempfile

import pytest

from src.idea import ContentGenre, Idea
from src.idea_db import IdeaDatabase
from src.story_translation import StoryTranslation, TranslationStatus


class TestDatabaseTranslationOperations:
    """Test translation database operations."""

    @pytest.fixture
    def db(self):
        """Create temporary database for testing."""
        # Create temp file
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)

        # Setup database
        db = IdeaDatabase(path)
        db.connect()
        db.create_tables()

        yield db

        # Cleanup
        db.close()
        os.unlink(path)

    @pytest.fixture
    def sample_story_id(self, db):
        """Create a sample story and return its ID."""
        idea = Idea(
            title="The Echo",
            concept="A girl hears her own voice from the future",
            original_language="en",
            genre=ContentGenre.HORROR,
        )
        story_id = db.insert_idea(idea.to_dict())
        return story_id

    def test_insert_translation(self, db, sample_story_id):
        """Test inserting a translation."""
        translation = StoryTranslation(
            story_id=sample_story_id,
            language_code="cs",
            title="Echo",
            text="Včera v noci jsem se probudila...",
            translator_id="AI-Translator-GPT4",
        )

        translation_id = db.insert_translation(translation.to_dict())

        assert translation_id is not None
        assert translation_id > 0

    def test_get_translation(self, db, sample_story_id):
        """Test retrieving a translation."""
        translation = StoryTranslation(
            story_id=sample_story_id,
            language_code="cs",
            title="Echo",
            text="Czech text here",
            translator_id="AI-Translator",
        )

        db.insert_translation(translation.to_dict())

        retrieved = db.get_translation(sample_story_id, "cs")

        assert retrieved is not None
        assert retrieved["story_id"] == sample_story_id
        assert retrieved["language_code"] == "cs"
        assert retrieved["title"] == "Echo"
        assert retrieved["text"] == "Czech text here"
        assert retrieved["translator_id"] == "AI-Translator"

    def test_get_nonexistent_translation(self, db, sample_story_id):
        """Test retrieving non-existent translation returns None."""
        result = db.get_translation(sample_story_id, "fr")
        assert result is None

    def test_get_all_translations(self, db, sample_story_id):
        """Test getting all translations for a story."""
        # Insert multiple translations
        languages = ["cs", "es", "de", "fr"]
        for lang in languages:
            translation = StoryTranslation(
                story_id=sample_story_id,
                language_code=lang,
                title=f"Title in {lang}",
                text=f"Text in {lang}",
            )
            db.insert_translation(translation.to_dict())

        translations = db.get_all_translations(sample_story_id)

        assert len(translations) == 4
        retrieved_langs = [t["language_code"] for t in translations]
        assert set(retrieved_langs) == set(languages)

    def test_get_translations_by_status(self, db, sample_story_id):
        """Test filtering translations by status."""
        # Insert translations with different statuses
        draft_trans = StoryTranslation(
            story_id=sample_story_id,
            language_code="cs",
            title="Draft",
            text="Text",
            status=TranslationStatus.DRAFT,
        )
        db.insert_translation(draft_trans.to_dict())

        approved_trans = StoryTranslation(
            story_id=sample_story_id,
            language_code="es",
            title="Approved",
            text="Text",
            status=TranslationStatus.APPROVED,
        )
        db.insert_translation(approved_trans.to_dict())

        # Get drafts
        drafts = db.get_translations_by_status("draft")
        assert len(drafts) >= 1
        assert any(t["language_code"] == "cs" for t in drafts)

        # Get approved
        approved = db.get_translations_by_status("approved")
        assert len(approved) >= 1
        assert any(t["language_code"] == "es" for t in approved)

    def test_update_translation(self, db, sample_story_id):
        """Test updating a translation."""
        translation = StoryTranslation(
            story_id=sample_story_id,
            language_code="de",
            title="Original Title",
            text="Original text",
            status=TranslationStatus.DRAFT,
            iteration_count=0,
        )

        db.insert_translation(translation.to_dict())

        # Update it
        translation.update_content(title="Updated Title", text="Updated text")
        translation.status = TranslationStatus.PENDING_REVIEW
        translation.iteration_count = 1

        success = db.update_translation(sample_story_id, "de", translation.to_dict())

        assert success is True

        # Verify update
        updated = db.get_translation(sample_story_id, "de")
        assert updated["title"] == "Updated Title"
        assert updated["text"] == "Updated text"
        assert updated["status"] == "pending_review"
        assert updated["iteration_count"] == 1

    def test_delete_translation(self, db, sample_story_id):
        """Test deleting a translation."""
        translation = StoryTranslation(
            story_id=sample_story_id, language_code="fr", title="French", text="Texte français"
        )

        db.insert_translation(translation.to_dict())

        # Verify it exists
        assert db.get_translation(sample_story_id, "fr") is not None

        # Delete it
        success = db.delete_translation(sample_story_id, "fr")
        assert success is True

        # Verify it's gone
        assert db.get_translation(sample_story_id, "fr") is None

    def test_get_available_languages(self, db, sample_story_id):
        """Test getting list of available languages."""
        # Initially no translations
        languages = db.get_available_languages(sample_story_id)
        assert len(languages) == 0

        # Add translations
        for lang in ["cs", "es", "de"]:
            translation = StoryTranslation(
                story_id=sample_story_id,
                language_code=lang,
                title=f"Title {lang}",
                text=f"Text {lang}",
            )
            db.insert_translation(translation.to_dict())

        # Get languages
        languages = db.get_available_languages(sample_story_id)
        assert len(languages) == 3
        assert set(languages) == {"cs", "de", "es"}  # Should be sorted

    def test_unique_constraint(self, db, sample_story_id):
        """Test that story_id + language_code must be unique."""
        translation1 = StoryTranslation(
            story_id=sample_story_id, language_code="cs", title="First", text="First text"
        )

        db.insert_translation(translation1.to_dict())

        # Try to insert duplicate
        translation2 = StoryTranslation(
            story_id=sample_story_id, language_code="cs", title="Second", text="Second text"
        )

        with pytest.raises(Exception):  # SQLite will raise an IntegrityError
            db.insert_translation(translation2.to_dict())

    def test_cascade_delete(self, db, sample_story_id):
        """Test that deleting story deletes its translations."""
        # Add translations
        for lang in ["cs", "es", "de"]:
            translation = StoryTranslation(
                story_id=sample_story_id,
                language_code=lang,
                title=f"Title {lang}",
                text=f"Text {lang}",
            )
            db.insert_translation(translation.to_dict())

        # Verify translations exist
        assert len(db.get_available_languages(sample_story_id)) == 3

        # Delete the story
        db.delete_idea(sample_story_id)

        # Translations should be gone (CASCADE DELETE)
        assert len(db.get_available_languages(sample_story_id)) == 0


class TestFeedbackHistorySerialization:
    """Test feedback history JSON serialization."""

    @pytest.fixture
    def db(self):
        """Create temporary database for testing."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)

        db = IdeaDatabase(path)
        db.connect()
        db.create_tables()

        yield db

        db.close()
        os.unlink(path)

    @pytest.fixture
    def sample_story_id(self, db):
        """Create a sample story."""
        idea = Idea(title="Test Story", concept="Test", original_language="en")
        return db.insert_idea(idea.to_dict())

    def test_feedback_history_roundtrip(self, db, sample_story_id):
        """Test that feedback history is preserved through database."""
        translation = StoryTranslation(
            story_id=sample_story_id, language_code="cs", title="Test", text="Text"
        )

        # Add feedback
        translation.add_feedback(
            reviewer_id="AI-Reviewer",
            issues=["Issue 1", "Issue 2"],
            suggestions=["Fix 1", "Fix 2"],
            meaning_score=75,
            notes="Needs work",
        )

        # Insert
        db.insert_translation(translation.to_dict())

        # Retrieve
        retrieved = db.get_translation(sample_story_id, "cs")

        # Verify feedback history preserved
        assert len(retrieved["feedback_history"]) == 1
        feedback = retrieved["feedback_history"][0]
        assert feedback["reviewer_id"] == "AI-Reviewer"
        assert len(feedback["issues"]) == 2
        assert feedback["issues"][0] == "Issue 1"
        assert len(feedback["suggestions"]) == 2
        assert feedback["meaning_score"] == 75
        assert feedback["notes"] == "Needs work"


class TestCompleteTranslationWorkflow:
    """Test complete translation workflow with database."""

    @pytest.fixture
    def db(self):
        """Create temporary database for testing."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)

        db = IdeaDatabase(path)
        db.connect()
        db.create_tables()

        yield db

        db.close()
        os.unlink(path)

    def test_complete_translation_workflow(self, db):
        """Test complete workflow from story creation to published translation."""
        # 1. Create original story in English
        original = Idea(
            title="The Echo",
            concept="A girl hears her own voice",
            synopsis="A teenager discovers she can hear her future self...",
            original_language="en",
            genre=ContentGenre.HORROR,
        )
        story_id = db.insert_idea(original.to_dict())

        # 2. Create Czech translation
        czech = StoryTranslation(
            story_id=story_id,
            language_code="cs",
            title="Echo",
            text="Teenager objeví, že může slyšet svůj budoucí hlas...",
            translator_id="AI-Translator-GPT4",
            translated_from="en",
        )
        db.insert_translation(czech.to_dict())

        # 3. Submit for review
        czech.submit_for_review()
        db.update_translation(story_id, "cs", czech.to_dict())

        # Verify status
        retrieved = db.get_translation(story_id, "cs")
        assert retrieved["status"] == "pending_review"

        # 4. First review - needs revision
        czech = StoryTranslation.from_dict(retrieved)
        czech.add_feedback(
            reviewer_id="AI-Reviewer-Claude",
            issues=["Tone doesn't match original suspense"],
            suggestions=["Increase tension in opening"],
            meaning_score=78,
        )
        db.update_translation(story_id, "cs", czech.to_dict())

        # Verify iteration
        retrieved = db.get_translation(story_id, "cs")
        assert retrieved["status"] == "revision_needed"
        assert retrieved["iteration_count"] == 1

        # 5. Translator revises
        czech = StoryTranslation.from_dict(retrieved)
        czech.update_content(
            text="Teenager zjistí, že slyší svůj budoucí hlas - varující ji před smrtí..."
        )
        czech.submit_for_review()
        db.update_translation(story_id, "cs", czech.to_dict())

        # 6. Second review - approved
        retrieved = db.get_translation(story_id, "cs")
        czech = StoryTranslation.from_dict(retrieved)
        czech.add_feedback(
            reviewer_id="AI-Reviewer-Claude",
            issues=[],
            suggestions=[],
            meaning_score=93,
            notes="Perfect! Suspense preserved.",
        )
        db.update_translation(story_id, "cs", czech.to_dict())

        # Verify approved
        retrieved = db.get_translation(story_id, "cs")
        assert retrieved["status"] == "approved"
        assert retrieved["meaning_verified"] is True
        assert retrieved["iteration_count"] == 2

        # 7. Publish translation
        czech = StoryTranslation.from_dict(retrieved)
        czech.publish()
        db.update_translation(story_id, "cs", czech.to_dict())

        # Final verification
        retrieved = db.get_translation(story_id, "cs")
        assert retrieved["status"] == "published"
        assert retrieved["published_at"] is not None

        # 8. Add another language (Spanish)
        spanish = StoryTranslation(
            story_id=story_id,
            language_code="es",
            title="El Eco",
            text="Una adolescente descubre que puede oír su voz futura...",
            translator_id="AI-Translator-GPT4",
            translated_from="en",
        )
        db.insert_translation(spanish.to_dict())

        # Verify both languages available
        languages = db.get_available_languages(story_id)
        assert set(languages) == {"cs", "es"}

        # Verify both can be retrieved
        cs_trans = db.get_translation(story_id, "cs")
        es_trans = db.get_translation(story_id, "es")
        assert cs_trans["status"] == "published"
        assert es_trans["status"] == "draft"


class TestIdeaOriginalLanguage:
    """Test original_language field in Idea model."""

    @pytest.fixture
    def db(self):
        """Create temporary database for testing."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)

        db = IdeaDatabase(path)
        db.connect()
        db.create_tables()

        yield db

        db.close()
        os.unlink(path)

    def test_idea_with_original_language(self, db):
        """Test creating idea with original_language field."""
        idea = Idea(
            title="Test Story",
            concept="Test concept",
            original_language="cs",  # Czech original
            genre=ContentGenre.EDUCATIONAL,
        )

        idea_id = db.insert_idea(idea.to_dict())

        retrieved = db.get_idea(idea_id)
        assert retrieved["original_language"] == "cs"

    def test_default_original_language(self, db):
        """Test that original_language defaults to 'en'."""
        idea = Idea(title="Test Story", concept="Test concept")

        assert idea.original_language == "en"

        idea_id = db.insert_idea(idea.to_dict())
        retrieved = db.get_idea(idea_id)
        assert retrieved["original_language"] == "en"

    def test_multilingual_story_management(self, db):
        """Test managing story with multiple translations."""
        # English original
        idea = Idea(
            title="The Echo",
            concept="Horror story about time",
            original_language="en",
            genre=ContentGenre.HORROR,
        )
        story_id = db.insert_idea(idea.to_dict())

        # Add translations
        translations_data = [
            ("cs", "Echo", "Czech text"),
            ("es", "El Eco", "Spanish text"),
            ("de", "Das Echo", "German text"),
            ("fr", "L'Écho", "French text"),
        ]

        for lang, title, text in translations_data:
            trans = StoryTranslation(
                story_id=story_id, language_code=lang, title=title, text=text, translated_from="en"
            )
            db.insert_translation(trans.to_dict())

        # Verify original language
        idea_data = db.get_idea(story_id)
        assert idea_data["original_language"] == "en"

        # Verify all translations reference original
        for lang, _, _ in translations_data:
            trans = db.get_translation(story_id, lang)
            assert trans["translated_from"] == "en"

        # Verify language list
        languages = db.get_available_languages(story_id)
        assert len(languages) == 4
        assert "cs" in languages
        assert "es" in languages
        assert "de" in languages
        assert "fr" in languages
