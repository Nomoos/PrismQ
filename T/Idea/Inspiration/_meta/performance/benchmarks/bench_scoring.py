"""Benchmark tests for Scoring module.

These benchmarks measure the performance of scoring operations including:
- YouTube score calculation
- Universal Content Score calculation
- Text-based scoring
- IdeaInspiration enrichment

Run with: pytest bench_scoring.py -v --benchmark-only
"""

import sys
from pathlib import Path

# Add Scoring module to path
scoring_path = Path(__file__).parent.parent.parent.parent / "Scoring" / "src"
sys.path.insert(0, str(scoring_path))

import pytest
from scoring import ScoringEngine


class MockIdeaInspiration:
    """Mock IdeaInspiration for testing."""

    def __init__(self, title, description, text_content, metadata=None):
        self.title = title
        self.description = description
        self.text_content = text_content
        self.metadata = metadata or {}
        self.content_type = "text"


class TestYouTubeScoring:
    """Benchmarks for YouTube video scoring."""

    @pytest.fixture
    def engine(self):
        """Create a scoring engine instance."""
        return ScoringEngine()

    @pytest.fixture
    def sample_video_data(self):
        """Sample YouTube video data."""
        return {
            "statistics": {"viewCount": "1000000", "likeCount": "50000", "commentCount": "1000"}
        }

    def test_bench_youtube_score_calculation(self, benchmark, engine, sample_video_data):
        """Benchmark YouTube score calculation."""

        def calc_score():
            return engine.calculate_youtube_score(sample_video_data)

        score, details = benchmark(calc_score)
        assert score > 0

    def test_bench_youtube_score_varied_data(self, benchmark, engine):
        """Benchmark YouTube scoring with varied data sizes."""
        videos = [
            {"statistics": {"viewCount": "100", "likeCount": "10", "commentCount": "1"}},
            {"statistics": {"viewCount": "10000", "likeCount": "500", "commentCount": "50"}},
            {"statistics": {"viewCount": "1000000", "likeCount": "50000", "commentCount": "1000"}},
            {
                "statistics": {
                    "viewCount": "10000000",
                    "likeCount": "500000",
                    "commentCount": "10000",
                }
            },
        ]

        def calc_multiple():
            results = []
            for video in videos:
                score, details = engine.calculate_youtube_score(video)
                results.append(score)
            return results

        scores = benchmark(calc_multiple)
        assert len(scores) == 4


class TestUniversalContentScore:
    """Benchmarks for Universal Content Score calculation."""

    @pytest.fixture
    def engine(self):
        """Create a scoring engine instance."""
        return ScoringEngine()

    @pytest.fixture
    def sample_metrics(self):
        """Sample content metrics."""
        return {
            "views": 1000000,
            "likes": 50000,
            "comments": 1000,
            "shares": 5000,
            "saves": 2000,
            "average_watch_time": 45,
            "video_length": 60,
            "channel_median_views": 500000,
            "conversions": 1000,
        }

    def test_bench_ucs_calculation(self, benchmark, engine, sample_metrics):
        """Benchmark Universal Content Score calculation."""

        def calc_ucs():
            return engine.calculate_universal_content_score(sample_metrics)

        result = benchmark(calc_ucs)
        assert "universal_content_score" in result
        assert result["universal_content_score"] > 0

    def test_bench_ucs_minimal_metrics(self, benchmark, engine):
        """Benchmark UCS with minimal metrics."""
        minimal_metrics = {
            "views": 10000,
            "likes": 500,
        }

        def calc_ucs():
            return engine.calculate_universal_content_score(minimal_metrics)

        result = benchmark(calc_ucs)
        assert "universal_content_score" in result

    def test_bench_ucs_full_metrics(self, benchmark, engine, sample_metrics):
        """Benchmark UCS with full metrics set."""

        def calc_ucs():
            return engine.calculate_universal_content_score(sample_metrics)

        result = benchmark(calc_ucs)
        assert all(
            key in result
            for key in [
                "universal_content_score",
                "engagement_rate",
                "watch_through_rate",
                "relative_performance_index",
            ]
        )


class TestTextScoring:
    """Benchmarks for text-based scoring."""

    @pytest.fixture
    def engine(self):
        """Create a scoring engine instance."""
        return ScoringEngine()

    @pytest.fixture
    def sample_text_idea(self):
        """Sample text-based IdeaInspiration."""
        return MockIdeaInspiration(
            title="Introduction to Machine Learning",
            description="A comprehensive guide to ML basics and fundamentals.",
            text_content="""
            Machine learning is a subset of artificial intelligence that enables systems
            to learn and improve from experience. This guide covers the fundamental concepts
            including supervised learning, unsupervised learning, and reinforcement learning.
            You'll discover how to apply these techniques to real-world problems and build
            intelligent applications. The field combines statistics, computer science, and
            domain expertise to create powerful predictive models.
            """
            * 3,  # Make it longer
        )

    def test_bench_text_scoring(self, benchmark, engine, sample_text_idea):
        """Benchmark text quality scoring."""

        def score_text():
            return engine.score_idea_inspiration(sample_text_idea)

        result = benchmark(score_text)
        assert result.overall_score > 0

    def test_bench_short_text(self, benchmark, engine):
        """Benchmark scoring short text."""
        short_idea = MockIdeaInspiration(
            title="Quick Tip",
            description="A brief tip.",
            text_content="This is a short piece of text for testing.",
        )

        def score_short():
            return engine.score_idea_inspiration(short_idea)

        result = benchmark(score_short)
        assert result.overall_score >= 0

    def test_bench_long_text(self, benchmark, engine):
        """Benchmark scoring long text content."""
        long_text = " ".join(["This is sentence number {}.".format(i) for i in range(500)])
        long_idea = MockIdeaInspiration(
            title="Comprehensive Guide to Everything",
            description="An extensive guide covering multiple topics.",
            text_content=long_text,
        )

        def score_long():
            return engine.score_idea_inspiration(long_idea)

        result = benchmark(score_long)
        assert result.overall_score > 0


class TestVideoWithEngagement:
    """Benchmarks for video content with engagement metrics."""

    @pytest.fixture
    def engine(self):
        """Create a scoring engine instance."""
        return ScoringEngine()

    @pytest.fixture
    def video_idea(self):
        """Sample video IdeaInspiration with engagement."""
        return MockIdeaInspiration(
            title="Python Programming Tutorial for Beginners",
            description="Learn Python from scratch with hands-on examples.",
            text_content="""
            Welcome to this Python programming tutorial. In this video, we'll cover the basics
            of Python including variables, data types, and control structures. Python is an
            excellent language for beginners because of its simple syntax and readability.
            We'll also explore functions, loops, and how to write clean, maintainable code.
            """,
            metadata={
                "statistics": {"viewCount": "500000", "likeCount": "25000", "commentCount": "500"},
                "channel": "CodeMaster",
                "published_at": "2024-01-01",
            },
        )

    def test_bench_video_comprehensive_scoring(self, benchmark, engine, video_idea):
        """Benchmark comprehensive video scoring with engagement."""

        def score_video():
            return engine.score_idea_inspiration(video_idea)

        result = benchmark(score_video)
        assert result.overall_score > 0
        assert result.engagement_score > 0


class TestBatchScoring:
    """Benchmarks for batch scoring operations."""

    @pytest.fixture
    def engine(self):
        """Create a scoring engine instance."""
        return ScoringEngine()

    @pytest.fixture
    def batch_ideas(self):
        """Create a batch of ideas for scoring."""
        ideas = []
        for i in range(10):
            ideas.append(
                MockIdeaInspiration(
                    title=f"Title {i}",
                    description=f"Description for item {i}",
                    text_content=f"Content for item {i}. " * 20,
                )
            )
        return ideas

    def test_bench_batch_10_items(self, benchmark, engine, batch_ideas):
        """Benchmark scoring 10 items."""

        def score_batch():
            results = []
            for idea in batch_ideas:
                result = engine.score_idea_inspiration(idea)
                results.append(result)
            return results

        results = benchmark(score_batch)
        assert len(results) == 10

    def test_bench_batch_100_items(self, benchmark, engine):
        """Benchmark scoring 100 items."""
        ideas = [
            MockIdeaInspiration(
                title=f"Item {i}",
                description=f"Description {i}",
                text_content=f"Content {i}. " * 10,
            )
            for i in range(100)
        ]

        def score_batch():
            results = []
            for idea in ideas:
                result = engine.score_idea_inspiration(idea)
                results.append(result)
            return results

        results = benchmark(score_batch)
        assert len(results) == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark-only"])
