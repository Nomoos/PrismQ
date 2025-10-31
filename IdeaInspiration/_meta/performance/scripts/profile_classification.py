"""Profile Classification module performance.

This script profiles classification operations including:
- Category classification
- Story detection
- Batch processing
"""

import sys
from pathlib import Path

# Add paths
script_dir = Path(__file__).parent
perf_dir = script_dir.parent
sys.path.insert(0, str(perf_dir))

from profiling_utils import CPUProfiler, MemoryProfiler, time_function

# Add Classification module to path
classification_path = perf_dir.parent.parent / "Classification" / "src"
sys.path.insert(0, str(classification_path))

from classification import CategoryClassifier, StoryDetector


@time_function
def profile_category_classification():
    """Profile category classification."""
    print("\n📊 Profiling Category Classification...")
    
    classifier = CategoryClassifier()
    cpu_profiler = CPUProfiler(output_dir=str(perf_dir / "reports" / "cpu"))
    mem_profiler = MemoryProfiler(output_dir=str(perf_dir / "reports" / "memory"))
    
    def test_classification():
        # Create diverse test videos
        videos = []
        
        # Story videos
        for i in range(100):
            videos.append({
                'title': f'My AITA Story {i}',
                'description': f'True story about what happened {i}',
                'tags': ['storytime', 'aita', 'confession'],
            })
        
        # Gaming videos
        for i in range(100):
            videos.append({
                'title': f'Epic Gaming Moment {i}',
                'description': f'Watch this gameplay {i}',
                'tags': ['gaming', 'gameplay', 'highlights'],
            })
        
        # Tutorial videos
        for i in range(100):
            videos.append({
                'title': f'How to Learn Python {i}',
                'description': f'Tutorial for beginners {i}',
                'tags': ['tutorial', 'education', 'programming'],
            })
        
        # Comedy videos
        for i in range(100):
            videos.append({
                'title': f'Funny Compilation {i}',
                'description': f'Hilarious memes {i}',
                'tags': ['comedy', 'funny', 'memes'],
            })
        
        # ASMR videos
        for i in range(100):
            videos.append({
                'title': f'ASMR Relaxation {i}',
                'description': f'Satisfying sounds {i}',
                'tags': ['asmr', 'relaxation', 'satisfying'],
            })
        
        # Classify all videos
        results = []
        for video in videos:
            result = classifier.classify_from_metadata(video)
            results.append(result)
        
        return len(results)
    
    # CPU profiling
    result, cpu_report = cpu_profiler.profile(test_classification)
    print(f"  ✓ CPU profile: {cpu_report}")
    
    # Memory profiling
    result, mem_report, peak_mb, increase_mb = mem_profiler.profile(test_classification)
    print(f"  ✓ Memory profile: {mem_report}")
    print(f"    Peak memory: {peak_mb:.2f} MB")
    print(f"    Memory increase: {increase_mb:.2f} MB")


@time_function
def profile_story_detection():
    """Profile story detection."""
    print("\n📊 Profiling Story Detection...")
    
    detector = StoryDetector(confidence_threshold=0.3)
    cpu_profiler = CPUProfiler(output_dir=str(perf_dir / "reports" / "cpu"))
    mem_profiler = MemoryProfiler(output_dir=str(perf_dir / "reports" / "memory"))
    
    def test_detection():
        # Create diverse test videos
        videos = []
        
        # Story videos
        for i in range(200):
            videos.append({
                'title': f'My True Story {i}',
                'description': f'This happened to me {i}',
                'tags': ['storytime', 'true story', 'confession'],
            })
        
        # Non-story videos
        for i in range(200):
            videos.append({
                'title': f'Gaming Highlights {i}',
                'description': f'Epic moments {i}',
                'tags': ['gaming', 'highlights', 'compilation'],
            })
        
        # Detect stories
        results = []
        for video in videos:
            is_story, confidence, indicators = detector.detect_from_metadata(video)
            results.append((is_story, confidence))
        
        return len(results)
    
    # CPU profiling
    result, cpu_report = cpu_profiler.profile(test_detection)
    print(f"  ✓ CPU profile: {cpu_report}")
    
    # Memory profiling
    result, mem_report, peak_mb, increase_mb = mem_profiler.profile(test_detection)
    print(f"  ✓ Memory profile: {mem_report}")
    print(f"    Peak memory: {peak_mb:.2f} MB")
    print(f"    Memory increase: {increase_mb:.2f} MB")


@time_function
def profile_full_pipeline():
    """Profile full classification + detection pipeline."""
    print("\n📊 Profiling Full Pipeline...")
    
    classifier = CategoryClassifier()
    detector = StoryDetector(confidence_threshold=0.3)
    cpu_profiler = CPUProfiler(output_dir=str(perf_dir / "reports" / "cpu"))
    mem_profiler = MemoryProfiler(output_dir=str(perf_dir / "reports" / "memory"))
    
    def test_pipeline():
        # Create diverse test videos
        videos = []
        
        categories = [
            ('Story', ['storytime', 'aita', 'confession']),
            ('Gaming', ['gaming', 'gameplay', 'highlights']),
            ('Tutorial', ['tutorial', 'education', 'howto']),
            ('Comedy', ['comedy', 'funny', 'memes']),
            ('ASMR', ['asmr', 'relaxation', 'satisfying']),
            ('Vlog', ['vlog', 'daily', 'lifestyle']),
            ('Review', ['review', 'unboxing', 'tech']),
        ]
        
        for cat_name, tags in categories:
            for i in range(50):
                videos.append({
                    'title': f'{cat_name} Video {i}',
                    'description': f'Description for {cat_name} {i}',
                    'tags': tags,
                })
        
        # Run full pipeline
        results = []
        for video in videos:
            # Classify
            category_result = classifier.classify_from_metadata(video)
            
            # Detect story
            is_story, confidence, indicators = detector.detect_from_metadata(video)
            
            results.append({
                'category': category_result.category,
                'category_confidence': category_result.confidence,
                'is_story': is_story,
                'story_confidence': confidence,
            })
        
        return len(results)
    
    # CPU profiling
    result, cpu_report = cpu_profiler.profile(test_pipeline)
    print(f"  ✓ CPU profile: {cpu_report}")
    
    # Memory profiling
    result, mem_report, peak_mb, increase_mb = mem_profiler.profile(test_pipeline)
    print(f"  ✓ Memory profile: {mem_report}")
    print(f"    Peak memory: {peak_mb:.2f} MB")
    print(f"    Memory increase: {increase_mb:.2f} MB")


def main():
    """Main entry point."""
    print("=" * 80)
    print("  Classification Module Performance Profiling")
    print("=" * 80)
    
    profile_category_classification()
    profile_story_detection()
    profile_full_pipeline()
    
    print("\n" + "=" * 80)
    print("  Classification Module Profiling Complete")
    print("=" * 80)
    print("\nReports saved to:")
    print(f"  CPU: {perf_dir / 'reports' / 'cpu'}")
    print(f"  Memory: {perf_dir / 'reports' / 'memory'}")


if __name__ == "__main__":
    main()
