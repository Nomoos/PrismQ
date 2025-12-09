"""Profile Scoring module performance.

This script profiles scoring operations including:
- YouTube score calculation
- Universal Content Score calculation
- Text-based scoring
- IdeaInspiration enrichment
"""

import sys
from pathlib import Path

# Add paths
script_dir = Path(__file__).parent
perf_dir = script_dir.parent
sys.path.insert(0, str(perf_dir))

from profiling_utils import CPUProfiler, MemoryProfiler, time_function

# Add Scoring module to path
scoring_path = perf_dir.parent.parent / "Scoring" / "src"
sys.path.insert(0, str(scoring_path))

from scoring import ScoringEngine


class MockIdeaInspiration:
    """Mock IdeaInspiration for testing."""

    def __init__(self, title, description, text_content, metadata=None):
        self.title = title
        self.description = description
        self.text_content = text_content
        self.metadata = metadata or {}
        self.content_type = "text"


@time_function
def profile_youtube_scoring():
    """Profile YouTube score calculation."""
    print("\n📊 Profiling YouTube Scoring...")

    engine = ScoringEngine()
    cpu_profiler = CPUProfiler(output_dir=str(perf_dir / "reports" / "cpu"))
    mem_profiler = MemoryProfiler(output_dir=str(perf_dir / "reports" / "memory"))

    def test_youtube():
        videos = [
            {
                "statistics": {
                    "viewCount": str(100 * i),
                    "likeCount": str(10 * i),
                    "commentCount": str(i),
                }
            }
            for i in range(1, 1001)
        ]

        results = []
        for video in videos:
            score, details = engine.calculate_youtube_score(video)
            results.append(score)

        return len(results)

    # CPU profiling
    result, cpu_report = cpu_profiler.profile(test_youtube)
    print(f"  ✓ CPU profile: {cpu_report}")

    # Memory profiling
    result, mem_report, peak_mb, increase_mb = mem_profiler.profile(test_youtube)
    print(f"  ✓ Memory profile: {mem_report}")
    print(f"    Peak memory: {peak_mb:.2f} MB")
    print(f"    Memory increase: {increase_mb:.2f} MB")


@time_function
def profile_universal_content_score():
    """Profile Universal Content Score calculation."""
    print("\n📊 Profiling Universal Content Score...")

    engine = ScoringEngine()
    cpu_profiler = CPUProfiler(output_dir=str(perf_dir / "reports" / "cpu"))
    mem_profiler = MemoryProfiler(output_dir=str(perf_dir / "reports" / "memory"))

    def test_ucs():
        metrics_list = [
            {
                "views": 1000 * i,
                "likes": 50 * i,
                "comments": 10 * i,
                "shares": 5 * i,
                "saves": 2 * i,
                "average_watch_time": 45,
                "video_length": 60,
                "channel_median_views": 500 * i,
                "conversions": i,
            }
            for i in range(1, 501)
        ]

        results = []
        for metrics in metrics_list:
            result = engine.calculate_universal_content_score(metrics)
            results.append(result["universal_content_score"])

        return len(results)

    # CPU profiling
    result, cpu_report = cpu_profiler.profile(test_ucs)
    print(f"  ✓ CPU profile: {cpu_report}")

    # Memory profiling
    result, mem_report, peak_mb, increase_mb = mem_profiler.profile(test_ucs)
    print(f"  ✓ Memory profile: {mem_report}")
    print(f"    Peak memory: {peak_mb:.2f} MB")
    print(f"    Memory increase: {increase_mb:.2f} MB")


@time_function
def profile_text_scoring():
    """Profile text-based scoring."""
    print("\n📊 Profiling Text Scoring...")

    engine = ScoringEngine()
    cpu_profiler = CPUProfiler(output_dir=str(perf_dir / "reports" / "cpu"))
    mem_profiler = MemoryProfiler(output_dir=str(perf_dir / "reports" / "memory"))

    def test_text():
        ideas = []

        # Short texts
        for i in range(100):
            ideas.append(
                MockIdeaInspiration(
                    title=f"Short Title {i}",
                    description=f"Short description {i}",
                    text_content=f"This is a short piece of text for testing. Item {i}.",
                )
            )

        # Medium texts
        for i in range(100):
            ideas.append(
                MockIdeaInspiration(
                    title=f"Medium Title {i}",
                    description=f"Medium description {i}",
                    text_content=" ".join([f"Sentence {j} for item {i}." for j in range(50)]),
                )
            )

        # Long texts
        for i in range(100):
            ideas.append(
                MockIdeaInspiration(
                    title=f"Long Title {i}",
                    description=f"Long description {i}",
                    text_content=" ".join([f"Sentence {j} for item {i}." for j in range(200)]),
                )
            )

        results = []
        for idea in ideas:
            score_breakdown = engine.score_idea_inspiration(idea)
            results.append(score_breakdown.overall_score)

        return len(results)

    # CPU profiling
    result, cpu_report = cpu_profiler.profile(test_text)
    print(f"  ✓ CPU profile: {cpu_report}")

    # Memory profiling
    result, mem_report, peak_mb, increase_mb = mem_profiler.profile(test_text)
    print(f"  ✓ Memory profile: {mem_report}")
    print(f"    Peak memory: {peak_mb:.2f} MB")
    print(f"    Memory increase: {increase_mb:.2f} MB")


def main():
    """Main entry point."""
    print("=" * 80)
    print("  Scoring Module Performance Profiling")
    print("=" * 80)

    profile_youtube_scoring()
    profile_universal_content_score()
    profile_text_scoring()

    print("\n" + "=" * 80)
    print("  Scoring Module Profiling Complete")
    print("=" * 80)
    print("\nReports saved to:")
    print(f"  CPU: {perf_dir / 'reports' / 'cpu'}")
    print(f"  Memory: {perf_dir / 'reports' / 'memory'}")


if __name__ == "__main__":
    main()
