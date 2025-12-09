"""Integration tests for dual-save database pattern.

This test demonstrates the dual-save architecture where Source modules
save to both their source-specific database AND the central IdeaInspiration
database.
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add Model path for imports
model_path = Path(__file__).resolve().parents[2] / "Model"
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from idea_inspiration import IdeaInspiration
from idea_inspiration_db import IdeaInspirationDatabase


class MockSourceDatabase:
    """Mock source-specific database for testing."""

    def __init__(self, db_path):
        self.db_path = db_path
        self.records = []

    def insert_resource(self, source, source_id, title, content, **kwargs):
        """Mock insert for source-specific database."""
        self.records.append(
            {"source": source, "source_id": source_id, "title": title, "content": content, **kwargs}
        )
        return True

    def count_by_source(self, source):
        """Mock count by source."""
        return len([r for r in self.records if r["source"] == source])


@pytest.fixture
def temp_central_db():
    """Create a temporary central database for testing."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".db") as f:
        db_path = f.name

    yield db_path

    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def temp_source_db():
    """Create a temporary source-specific database for testing."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".db") as f:
        db_path = f.name

    yield db_path

    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


class TestDualSavePattern:
    """Tests for the dual-save database pattern."""

    def test_creative_source_dual_save(self, temp_source_db, temp_central_db):
        """Test dual-save pattern for Creative source (e.g., LyricSnippets)."""
        # Initialize databases
        source_db = MockSourceDatabase(temp_source_db)
        central_db = IdeaInspirationDatabase(temp_central_db, interactive=False)

        # Simulate plugin returning IdeaInspiration
        idea = IdeaInspiration.from_text(
            title="Bohemian Rhapsody - Queen",
            description="Lyric snippet from Queen",
            text_content="Is this the real life? Is this just fantasy?",
            keywords=["lyrics", "queen", "genius"],
            metadata={"song_id": "12345", "artist_name": "Queen", "pageviews": "5000000"},
            source_id="genius-12345",
            source_url="https://genius.com/12345",
            source_created_by="Queen",
        )

        # DUAL-SAVE: Save to both databases
        # 1. Source-specific database
        source_saved = source_db.insert_resource(
            source="genius",
            source_id=idea.source_id,
            title=idea.title,
            content=idea.content,
            tags=",".join(idea.keywords),
        )

        # 2. Central database
        central_saved = central_db.insert(idea)

        # Verify both saves
        assert source_saved is True
        assert central_saved is not None

        # Verify source database
        assert source_db.count_by_source("genius") == 1

        # Verify central database
        assert central_db.count() == 1
        retrieved = central_db.get_by_source_id("genius-12345")
        assert retrieved is not None
        assert retrieved.title == "Bohemian Rhapsody - Queen"
        assert retrieved.metadata["song_id"] == "12345"

    def test_signal_source_dual_save(self, temp_source_db, temp_central_db):
        """Test dual-save pattern for Signal source (e.g., GoogleTrends)."""
        # Initialize databases
        source_db = MockSourceDatabase(temp_source_db)
        central_db = IdeaInspirationDatabase(temp_central_db, interactive=False)

        # Simulate plugin returning IdeaInspiration
        idea = IdeaInspiration.from_text(
            title="AI Trends",
            description="Trending search topic",
            text_content="Artificial Intelligence and Machine Learning",
            keywords=["ai", "machine-learning", "technology"],
            metadata={
                "signal_type": "trend",
                "temporal": {"peak_date": "2025-01-15", "velocity": 0.85},
                "metrics": {"search_volume": 1000000, "growth_rate": 0.45},
            },
            source_id="google-trends-ai-2025",
            source_created_at="2025-01-15",
        )

        # DUAL-SAVE
        # 1. Source-specific database (signals table)
        source_saved = source_db.insert_resource(
            source="google_trends",
            source_id=idea.source_id,
            title=idea.title,
            content=idea.content,
            signal_type="trend",
            tags=",".join(idea.keywords),
        )

        # 2. Central database
        central_saved = central_db.insert(idea)

        # Verify both saves
        assert source_saved is True
        assert central_saved is not None
        assert central_db.count() == 1

        # Verify metadata preservation
        retrieved = central_db.get_by_source_id("google-trends-ai-2025")
        assert retrieved.metadata["signal_type"] == "trend"
        assert "temporal" in retrieved.metadata
        assert retrieved.metadata["temporal"]["velocity"] == 0.85

    def test_event_source_dual_save(self, temp_source_db, temp_central_db):
        """Test dual-save pattern for Event source (e.g., CalendarHolidays)."""
        # Initialize databases
        source_db = MockSourceDatabase(temp_source_db)
        central_db = IdeaInspirationDatabase(temp_central_db, interactive=False)

        # Simulate event data converted to IdeaInspiration
        idea = IdeaInspiration.from_text(
            title="Christmas Day",
            description="holiday event in US",
            text_content="Christmas Day",
            keywords=["holiday", "US", "christmas"],
            metadata={
                "event_type": "holiday",
                "date": "2025-12-25",
                "country": "US",
                "scope": "national",
                "importance": "major",
            },
            source_id="calendar-christmas-2025-us",
            source_created_at="2025-12-25",
            category="event",
        )

        # DUAL-SAVE
        # 1. Source-specific database (events table)
        source_saved = source_db.insert_resource(
            source="calendar_holidays",
            source_id=idea.source_id,
            title=idea.title,
            content=idea.content,
            event_type="holiday",
            tags=",".join(idea.keywords),
        )

        # 2. Central database
        central_saved = central_db.insert(idea)

        # Verify both saves
        assert source_saved is True
        assert central_saved is not None
        assert central_db.count() == 1

        # Verify category
        retrieved = central_db.get_by_source_id("calendar-christmas-2025-us")
        assert retrieved.category == "event"
        assert retrieved.metadata["event_type"] == "holiday"

    def test_multiple_sources_unified_query(self, temp_central_db):
        """Test that multiple sources can be queried together."""
        # Initialize central database
        central_db = IdeaInspirationDatabase(temp_central_db, interactive=False)

        # Add ideas from different sources
        sources = [
            IdeaInspiration.from_text(
                title="Lyric 1", text_content="Content", source_id="lyric-1", category="creative"
            ),
            IdeaInspiration.from_text(
                title="Trend 1", text_content="Content", source_id="trend-1", category="signal"
            ),
            IdeaInspiration.from_text(
                title="Event 1", text_content="Content", source_id="event-1", category="event"
            ),
        ]

        # Save all to central database
        for idea in sources:
            central_db.insert(idea)

        # Unified queries
        all_ideas = central_db.get_all()
        assert len(all_ideas) == 3

        # Filter by category
        creative_ideas = central_db.get_all(category="creative")
        assert len(creative_ideas) == 1
        assert creative_ideas[0].title == "Lyric 1"

        # Count by category
        assert central_db.count(category="signal") == 1
        assert central_db.count(category="event") == 1
        assert central_db.count() == 3

    def test_batch_save_performance(self, temp_central_db):
        """Test batch save for better performance."""
        central_db = IdeaInspirationDatabase(temp_central_db, interactive=False)

        # Create multiple ideas
        ideas = [
            IdeaInspiration.from_text(
                title=f"Idea {i}", text_content=f"Content {i}", source_id=f"batch-{i}"
            )
            for i in range(100)
        ]

        # Batch save
        inserted_count = central_db.insert_batch(ideas)

        assert inserted_count == 100
        assert central_db.count() == 100

    def test_source_specific_metadata_preservation(self, temp_central_db):
        """Test that source-specific metadata is preserved in central DB."""
        central_db = IdeaInspirationDatabase(temp_central_db, interactive=False)

        # Creative source with specific metadata
        creative_idea = IdeaInspiration.from_text(
            title="Song Lyric",
            text_content="Lyric content",
            source_id="song-1",
            metadata={"pageviews": "1000000", "artist_id": "12345", "album": "Greatest Hits"},
        )

        central_db.insert(creative_idea)

        # Retrieve and verify metadata
        retrieved = central_db.get_by_source_id("song-1")
        assert retrieved.metadata["pageviews"] == "1000000"
        assert retrieved.metadata["artist_id"] == "12345"
        assert retrieved.metadata["album"] == "Greatest Hits"

    def test_different_content_types(self, temp_central_db):
        """Test that different content types are saved correctly."""
        central_db = IdeaInspirationDatabase(temp_central_db, interactive=False)

        # Text content
        text_idea = IdeaInspiration.from_text(
            title="Article", text_content="Article content", source_id="text-1"
        )

        # Video content
        video_idea = IdeaInspiration.from_video(
            title="Video", subtitle_text="Video subtitles", source_id="video-1"
        )

        # Audio content
        audio_idea = IdeaInspiration.from_audio(
            title="Podcast", transcription="Podcast transcription", source_id="audio-1"
        )

        # Save all
        central_db.insert(text_idea)
        central_db.insert(video_idea)
        central_db.insert(audio_idea)

        # Query by source type
        text_results = central_db.get_all(source_type="text")
        video_results = central_db.get_all(source_type="video")
        audio_results = central_db.get_all(source_type="audio")

        assert len(text_results) == 1
        assert len(video_results) == 1
        assert len(audio_results) == 1
        assert central_db.count() == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
