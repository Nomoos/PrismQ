"""Benchmark tests for Classification module.

These benchmarks measure the performance of classification operations including:
- Category classification
- Story detection
- Batch processing
- Text classification

Run with: pytest bench_classification.py -v --benchmark-only
"""

import sys
from pathlib import Path

# Add Classification module to path
classification_path = Path(__file__).parent.parent.parent.parent / "Classification" / "src"
sys.path.insert(0, str(classification_path))

import pytest
from classification import CategoryClassifier, PrimaryCategory, StoryDetector


class TestCategoryClassification:
    """Benchmarks for category classification."""

    @pytest.fixture
    def classifier(self):
        """Create a category classifier instance."""
        return CategoryClassifier()

    @pytest.fixture
    def sample_video(self):
        """Sample video metadata."""
        return {
            "title": "My AITA Story - Was I Wrong?",
            "description": "Let me tell you about what happened yesterday. This is my true story.",
            "tags": ["storytime", "aita", "confession", "true story"],
        }

    def test_bench_classify_single(self, benchmark, classifier, sample_video):
        """Benchmark single video classification."""

        def classify():
            return classifier.classify_from_metadata(sample_video)

        result = benchmark(classify)
        assert result.category is not None
        assert 0 <= result.confidence <= 1

    def test_bench_classify_gaming(self, benchmark, classifier):
        """Benchmark gaming video classification."""
        gaming_video = {
            "title": "Fortnite Epic Victory Royale",
            "description": "Watch this amazing gaming highlight and clutch moment!",
            "tags": ["gaming", "fortnite", "gameplay", "victory"],
        }

        def classify():
            return classifier.classify_from_metadata(gaming_video)

        result = benchmark(classify)
        assert result.category == PrimaryCategory.GAMING

    def test_bench_classify_tutorial(self, benchmark, classifier):
        """Benchmark tutorial video classification."""
        tutorial_video = {
            "title": "How to Learn Python in 60 Seconds",
            "description": "Quick tutorial on Python programming basics for beginners.",
            "tags": ["tutorial", "education", "programming", "python"],
        }

        def classify():
            return classifier.classify_from_metadata(tutorial_video)

        result = benchmark(classify)
        assert result.category == PrimaryCategory.TUTORIAL

    def test_bench_classify_varied_content(self, benchmark, classifier):
        """Benchmark classification with varied content types."""
        videos = [
            {
                "title": "Funny Meme Compilation",
                "description": "Hilarious memes",
                "tags": ["comedy", "memes"],
            },
            {
                "title": "Morning Routine GRWM",
                "description": "Get ready with me",
                "tags": ["vlog", "lifestyle"],
            },
            {
                "title": "iPhone Unboxing Review",
                "description": "Tech review",
                "tags": ["review", "tech"],
            },
            {
                "title": "ASMR Relaxation",
                "description": "Satisfying sounds",
                "tags": ["asmr", "relaxation"],
            },
        ]

        def classify_multiple():
            results = []
            for video in videos:
                result = classifier.classify_from_metadata(video)
                results.append(result)
            return results

        results = benchmark(classify_multiple)
        assert len(results) == 4


class TestStoryDetection:
    """Benchmarks for story detection."""

    @pytest.fixture
    def detector(self):
        """Create a story detector instance."""
        return StoryDetector(confidence_threshold=0.3)

    @pytest.fixture
    def story_video(self):
        """Sample story video metadata."""
        return {
            "title": "My AITA Story - Was I Wrong?",
            "description": "Let me tell you about what happened yesterday. This is my true story.",
            "tags": ["storytime", "aita", "confession", "true story"],
        }

    @pytest.fixture
    def non_story_video(self):
        """Sample non-story video metadata."""
        return {
            "title": "Funniest Meme Compilation 2024",
            "description": "Watch these hilarious memes that will make you laugh!",
            "tags": ["comedy", "funny", "memes", "entertainment"],
        }

    def test_bench_detect_story(self, benchmark, detector, story_video):
        """Benchmark story detection on story content."""

        def detect():
            return detector.detect_from_metadata(story_video)

        is_story, confidence, indicators = benchmark(detect)
        assert is_story is True
        assert confidence > 0.3

    def test_bench_detect_non_story(self, benchmark, detector, non_story_video):
        """Benchmark story detection on non-story content."""

        def detect():
            return detector.detect_from_metadata(non_story_video)

        is_story, confidence, indicators = benchmark(detect)
        assert is_story is False

    def test_bench_detect_mixed_content(self, benchmark, detector):
        """Benchmark story detection on mixed content."""
        videos = [
            {
                "title": "My True Story - AITA",
                "description": "This happened to me",
                "tags": ["storytime", "true"],
            },
            {
                "title": "Gaming Compilation",
                "description": "Epic moments",
                "tags": ["gaming", "highlights"],
            },
            {
                "title": "Reddit Confession",
                "description": "I need to confess",
                "tags": ["confession", "reddit"],
            },
            {
                "title": "Tutorial Video",
                "description": "How to code",
                "tags": ["tutorial", "education"],
            },
        ]

        def detect_multiple():
            results = []
            for video in videos:
                is_story, conf, indicators = detector.detect_from_metadata(video)
                results.append((is_story, conf))
            return results

        results = benchmark(detect_multiple)
        assert len(results) == 4


class TestBatchClassification:
    """Benchmarks for batch classification operations."""

    @pytest.fixture
    def classifier(self):
        """Create a category classifier instance."""
        return CategoryClassifier()

    @pytest.fixture
    def detector(self):
        """Create a story detector instance."""
        return StoryDetector(confidence_threshold=0.3)

    @pytest.fixture
    def batch_videos(self):
        """Create a batch of videos for testing."""
        return [
            {
                "title": f"Video Title {i}",
                "description": f"Description for video {i}",
                "tags": ["tag1", "tag2", "tag3"],
            }
            for i in range(10)
        ]

    def test_bench_batch_classify_10(self, benchmark, classifier, batch_videos):
        """Benchmark classifying 10 videos."""

        def classify_batch():
            results = []
            for video in batch_videos:
                result = classifier.classify_from_metadata(video)
                results.append(result)
            return results

        results = benchmark(classify_batch)
        assert len(results) == 10

    def test_bench_batch_detect_10(self, benchmark, detector, batch_videos):
        """Benchmark story detection on 10 videos."""

        def detect_batch():
            results = []
            for video in batch_videos:
                is_story, conf, indicators = detector.detect_from_metadata(video)
                results.append((is_story, conf))
            return results

        results = benchmark(detect_batch)
        assert len(results) == 10

    def test_bench_batch_classify_100(self, benchmark, classifier):
        """Benchmark classifying 100 videos."""
        videos = [
            {
                "title": f"Video {i}",
                "description": f"Description {i}",
                "tags": ["general"],
            }
            for i in range(100)
        ]

        def classify_batch():
            results = []
            for video in videos:
                result = classifier.classify_from_metadata(video)
                results.append(result)
            return results

        results = benchmark(classify_batch)
        assert len(results) == 100

    def test_bench_full_pipeline(self, benchmark, classifier, detector):
        """Benchmark full classification + detection pipeline."""
        videos = [
            {
                "title": "My Story - AITA",
                "description": "True story about what happened",
                "tags": ["storytime", "aita"],
            },
            {
                "title": "Gaming Highlights",
                "description": "Epic gameplay",
                "tags": ["gaming", "highlights"],
            },
            {
                "title": "Tutorial: Learn Python",
                "description": "Programming guide",
                "tags": ["tutorial", "education"],
            },
            {
                "title": "Reddit Confession",
                "description": "I need to share this",
                "tags": ["confession", "reddit"],
            },
        ] * 5  # 20 videos total

        def full_pipeline():
            results = []
            for video in videos:
                # Classify
                category_result = classifier.classify_from_metadata(video)

                # Detect story
                is_story, confidence, indicators = detector.detect_from_metadata(video)

                results.append(
                    {
                        "category": category_result.category,
                        "category_confidence": category_result.confidence,
                        "is_story": is_story,
                        "story_confidence": confidence,
                    }
                )
            return results

        results = benchmark(full_pipeline)
        assert len(results) == 20


class TestEdgeCases:
    """Benchmarks for edge cases and error handling."""

    @pytest.fixture
    def classifier(self):
        """Create a category classifier instance."""
        return CategoryClassifier()

    def test_bench_empty_metadata(self, benchmark, classifier):
        """Benchmark classification with minimal metadata."""
        minimal = {
            "title": "",
            "description": "",
            "tags": [],
        }

        def classify():
            return classifier.classify_from_metadata(minimal)

        result = benchmark(classify)
        assert result.category is not None

    def test_bench_long_text(self, benchmark, classifier):
        """Benchmark classification with very long text."""
        long_video = {
            "title": "Title " * 100,
            "description": "Description " * 500,
            "tags": [f"tag{i}" for i in range(50)],
        }

        def classify():
            return classifier.classify_from_metadata(long_video)

        result = benchmark(classify)
        assert result.category is not None

    def test_bench_special_characters(self, benchmark, classifier):
        """Benchmark classification with special characters."""
        special_video = {
            "title": "🎮 Gaming Video!!! [EPIC] 😎",
            "description": "Check this out!!! 🔥🔥🔥",
            "tags": ["gaming", "🎮", "epic!!!"],
        }

        def classify():
            return classifier.classify_from_metadata(special_video)

        result = benchmark(classify)
        assert result.category is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark-only"])
