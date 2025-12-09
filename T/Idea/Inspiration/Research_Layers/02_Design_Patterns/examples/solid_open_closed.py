#!/usr/bin/env python3
"""
Open/Closed Principle (OCP) - Examples

PRINCIPLE: Software entities should be open for extension, but closed for modification.

You should be able to add new functionality without changing existing code.
Use abstractions (Protocols, Abstract Base Classes) to achieve this.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Protocol

# =============================================================================
# Example 1: Good OCP - Using Protocol for Extension
# =============================================================================


@dataclass
class Video:
    """Video data model."""

    id: str
    title: str
    url: str
    platform: str


class VideoScraper(Protocol):
    """
    Protocol defines contract for video scrapers.
    New scrapers can be added WITHOUT modifying existing code.
    """

    def scrape(self, url: str) -> List[Video]:
        """Scrape videos from URL."""
        ...


class YouTubeScraper:
    """YouTube scraper implementation."""

    def scrape(self, url: str) -> List[Video]:
        """Scrape YouTube videos."""
        print(f"Scraping YouTube: {url}")
        return [Video(id="yt-1", title="Python Tutorial", url=url, platform="youtube")]


class TikTokScraper:
    """TikTok scraper implementation - NEW, doesn't modify existing code."""

    def scrape(self, url: str) -> List[Video]:
        """Scrape TikTok videos."""
        print(f"Scraping TikTok: {url}")
        return [Video(id="tt-1", title="Dance Video", url=url, platform="tiktok")]


class VideoProcessor:
    """
    ✅ GOOD: Open for extension (new scrapers), closed for modification.
    This class never needs to change when we add new platforms.
    """

    def __init__(self, scraper: VideoScraper):
        self._scraper = scraper

    def process(self, url: str) -> List[Video]:
        """Process videos from any scraper."""
        return self._scraper.scrape(url)


# =============================================================================
# Example 2: Good OCP - Strategy Pattern for Scoring
# =============================================================================


class ScoringStrategy(Protocol):
    """Protocol for scoring strategies - extensible without modification."""

    def calculate_score(self, video: Video) -> float:
        """Calculate relevance score for video."""
        ...


class KeywordScoring:
    """Score based on keywords in title."""

    def __init__(self, keywords: List[str]):
        self._keywords = keywords

    def calculate_score(self, video: Video) -> float:
        """Score based on keyword matches."""
        matches = sum(1 for kw in self._keywords if kw.lower() in video.title.lower())
        return min(matches / len(self._keywords), 1.0)


class LengthScoring:
    """Score based on title length - NEW strategy."""

    def calculate_score(self, video: Video) -> float:
        """Score based on title length."""
        # Prefer titles between 40-60 characters
        length = len(video.title)
        if 40 <= length <= 60:
            return 1.0
        elif length < 40:
            return length / 40
        else:
            return 60 / length


class VideoScorer:
    """
    ✅ GOOD: Can use any scoring strategy without modification.
    Add new strategies without changing this class.
    """

    def __init__(self, strategy: ScoringStrategy):
        self._strategy = strategy

    def score(self, video: Video) -> float:
        """Score video using configured strategy."""
        return self._strategy.calculate_score(video)


# =============================================================================
# Example 3: Good OCP - Filter Chain (Extensible)
# =============================================================================


class VideoFilter(ABC):
    """Abstract base class for video filters."""

    @abstractmethod
    def filter(self, videos: List[Video]) -> List[Video]:
        """Filter videos based on criteria."""
        pass


class PlatformFilter(VideoFilter):
    """Filter by platform."""

    def __init__(self, allowed_platforms: List[str]):
        self._allowed_platforms = allowed_platforms

    def filter(self, videos: List[Video]) -> List[Video]:
        """Keep only videos from allowed platforms."""
        return [v for v in videos if v.platform in self._allowed_platforms]


class TitleLengthFilter(VideoFilter):
    """Filter by title length - NEW filter, no modification needed."""

    def __init__(self, min_length: int, max_length: int):
        self._min_length = min_length
        self._max_length = max_length

    def filter(self, videos: List[Video]) -> List[Video]:
        """Keep only videos within title length range."""
        return [v for v in videos if self._min_length <= len(v.title) <= self._max_length]


class FilterChain:
    """
    ✅ GOOD: Extensible filter chain.
    Add new filters without modifying this class.
    """

    def __init__(self, filters: List[VideoFilter]):
        self._filters = filters

    def apply(self, videos: List[Video]) -> List[Video]:
        """Apply all filters in sequence."""
        result = videos
        for f in self._filters:
            result = f.filter(result)
        return result


# =============================================================================
# Demonstration
# =============================================================================


def demonstrate_ocp():
    """Demonstrate Open/Closed Principle."""
    print("\n" + "=" * 70)
    print("DEMONSTRATING OPEN/CLOSED PRINCIPLE")
    print("=" * 70)

    # 1. Scraper Extension
    print("\n1. Video Scraper - Open for Extension:")
    youtube = YouTubeScraper()
    processor_yt = VideoProcessor(youtube)
    videos_yt = processor_yt.process("https://youtube.com/channel/example")
    print(f"   Processed {len(videos_yt)} YouTube videos")

    # Add NEW scraper without modifying VideoProcessor
    tiktok = TikTokScraper()
    processor_tt = VideoProcessor(tiktok)
    videos_tt = processor_tt.process("https://tiktok.com/@example")
    print(f"   Processed {len(videos_tt)} TikTok videos")
    print("   ✅ Added new platform without modifying VideoProcessor!")

    # 2. Scoring Extension
    print("\n2. Scoring Strategy - Open for Extension:")
    video = Video(id="1", title="Python Tutorial for Beginners", url="url", platform="youtube")

    # Use keyword scoring
    keyword_scorer = VideoScorer(KeywordScoring(["python", "tutorial"]))
    score1 = keyword_scorer.score(video)
    print(f"   Keyword score: {score1:.2f}")

    # Add NEW scoring without modifying VideoScorer
    length_scorer = VideoScorer(LengthScoring())
    score2 = length_scorer.score(video)
    print(f"   Length score: {score2:.2f}")
    print("   ✅ Added new scoring strategy without modifying VideoScorer!")

    # 3. Filter Extension
    print("\n3. Filter Chain - Open for Extension:")
    all_videos = [
        Video("1", "Short", "url1", "youtube"),
        Video("2", "Medium length title here", "url2", "tiktok"),
        Video("3", "Very long title with lots of words to make it lengthy", "url3", "youtube"),
    ]

    # Use platform filter
    platform_filter = PlatformFilter(["youtube"])
    filtered1 = platform_filter.filter(all_videos)
    print(f"   After platform filter: {len(filtered1)} videos")

    # Add NEW filter without modifying FilterChain
    chain = FilterChain(
        [PlatformFilter(["youtube"]), TitleLengthFilter(min_length=10, max_length=50)]
    )
    filtered2 = chain.apply(all_videos)
    print(f"   After filter chain: {len(filtered2)} videos")
    print("   ✅ Added new filter without modifying FilterChain!")

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS:")
    print("✅ Use Protocols/ABC to define contracts")
    print("✅ Depend on abstractions, not concrete implementations")
    print("✅ Add new functionality by creating new classes, not modifying existing ones")
    print("✅ Existing code remains stable and tested")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    demonstrate_ocp()
