"""Integration tests for Sprint 4 features.

This module contains integration tests for the three main Sprint 4 features:
- POST-001: SEO Keywords & Optimization
- POST-003: Blog Format Optimization
- POST-005: Batch Idea Processing

Tests focus on:
1. End-to-end workflow integration
2. Cross-module data flow
3. Batch processing with SEO and formatting
4. Performance with realistic loads
5. Error handling and edge cases
"""

import sys
from pathlib import Path
import pytest
import asyncio
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Import Sprint 4 modules
from T.Publishing.SEO.Keywords import (
    process_content_seo,
    extract_keywords,
    generate_seo_metadata,
    KeywordExtractor,
    MetadataGenerator,
)
from T.Script.Formatter.Blog import (
    BlogFormatter,
    BlogFormattedContent,
    format_blog,
    export_for_platform,
)
from T.Idea.Batch import (
    BatchProcessor,
    BatchConfig,
    ProcessingMode,
    RetryHandler,
    RetryConfig,
    ReportGenerator,
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_script():
    """Sample script content for testing."""
    return """
    Python Programming: A Comprehensive Guide for Beginners
    
    Python is one of the most popular programming languages in the world today.
    Learning Python opens doors to exciting careers in software development, 
    data science, machine learning, and web development.
    
    Why Learn Python?
    
    Python's simple syntax makes it an ideal programming language for beginners.
    The Python programming community is large and supportive, providing countless
    tutorials, libraries, and frameworks. Many beginners start their programming
    journey with Python because of its readability and versatility.
    
    Getting Started with Python
    
    To learn Python effectively, practice coding regularly and work on real
    projects. Start with basic concepts like variables, loops, and functions,
    then progress to more advanced topics. Python programming skills are highly
    valued in the tech industry, and mastering Python can lead to numerous
    job opportunities in software engineering and data analysis.
    
    Best Practices for Learning
    
    The best way to become proficient in Python is through consistent practice
    and building real-world applications. Join online communities, contribute
    to open source projects, and never stop learning. Python's extensive
    standard library and third-party packages make it suitable for everything
    from simple scripts to complex applications.
    """


@pytest.fixture
def sample_title():
    """Sample title for testing."""
    return "Python Programming: A Comprehensive Guide for Beginners"


@pytest.fixture
def sample_ideas_batch():
    """Sample batch of ideas for testing."""
    return [
        {
            "id": f"idea-{i:03d}",
            "title": f"Python Tutorial {i}",
            "script": f"Learn Python programming with this comprehensive tutorial {i}. " * 20
        }
        for i in range(20)
    ]


# ============================================================================
# Integration Tests: Script → Blog Format → SEO
# ============================================================================

@pytest.mark.integration
class TestScriptToBlogToSEO:
    """Test integration between script formatting and SEO optimization."""
    
    def test_format_then_seo_basic(self, sample_title, sample_script):
        """Test basic workflow: format script as blog, then optimize SEO."""
        # Step 1: Format script as blog
        blog_result = format_blog(
            script=sample_script,
            title=sample_title,
            content_id="test-001"
        )
        
        assert isinstance(blog_result, BlogFormattedContent)
        assert blog_result.formatted_content is not None
        assert len(blog_result.formatted_content) > 0
        assert blog_result.success is True
        
        # Step 2: Apply SEO optimization to formatted blog
        seo_result = process_content_seo(
            title=sample_title,
            script=blog_result.formatted_content
        )
        
        assert len(seo_result['primary_keywords']) > 0
        assert len(seo_result['meta_description']) >= 120
        assert 'python' in ' '.join(seo_result['primary_keywords']).lower()
    
    def test_format_with_seo_metadata_integration(self, sample_title, sample_script):
        """Test that blog formatting preserves SEO-relevant content."""
        # Format blog first
        blog_result = format_blog(
            script=sample_script,
            title=sample_title,
            content_id="test-002",
            platform="medium"
        )
        
        # Extract SEO from original
        seo_original = process_content_seo(
            title=sample_title,
            script=sample_script
        )
        
        # Extract SEO from formatted
        seo_formatted = process_content_seo(
            title=sample_title,
            script=blog_result.formatted_content
        )
        
        # Keywords should be similar (allowing some variation)
        original_keywords = set(seo_original['primary_keywords'][:3])
        formatted_keywords = set(seo_formatted['primary_keywords'][:3])
        overlap = original_keywords.intersection(formatted_keywords)
        
        # At least 2 of top 3 keywords should overlap
        assert len(overlap) >= 2
    
    def test_platform_specific_blog_with_seo(self, sample_title, sample_script):
        """Test platform-specific formatting maintains SEO quality."""
        platforms = ["medium", "wordpress", "ghost"]
        
        for i, platform in enumerate(platforms):
            # Format for specific platform
            blog_result = format_blog(
                script=sample_script,
                title=sample_title,
                content_id=f"test-003-{i}",
                platform=platform
            )
            
            # Optimize SEO
            seo_result = process_content_seo(
                title=sample_title,
                script=blog_result.formatted_content
            )
            
            # Each platform should maintain good SEO
            assert len(seo_result['primary_keywords']) >= 3
            assert seo_result['quality_score'] > 40
            assert len(seo_result['meta_description']) >= 120
    
    def test_blog_metadata_with_seo_metadata(self, sample_title, sample_script):
        """Test that blog and SEO metadata complement each other."""
        # Get blog with metadata
        blog_result = format_blog(
            script=sample_script,
            title=sample_title,
            content_id="test-004"
        )
        
        # Get SEO metadata
        seo_result = process_content_seo(
            title=sample_title,
            script=sample_script
        )
        
        # Blog metadata
        assert blog_result.metadata.word_count > 0
        assert blog_result.metadata.reading_time is not None
        
        # SEO metadata
        assert seo_result['total_words'] > 0
        
        # Word counts should be reasonably close (within 30% due to formatting)
        blog_words = blog_result.metadata.word_count
        seo_words = seo_result['total_words']
        diff_ratio = abs(blog_words - seo_words) / max(blog_words, seo_words)
        assert diff_ratio < 0.3


# ============================================================================
# Integration Tests: Batch Processing with Blog & SEO
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
class TestBatchProcessingIntegration:
    """Test batch processing with blog formatting and SEO optimization."""
    
    async def test_batch_process_with_blog_formatting(self, sample_ideas_batch):
        """Test batch processing ideas with blog formatting."""
        async def process_with_blog(idea):
            """Process idea: format as blog."""
            await asyncio.sleep(0.01)  # Simulate processing
            
            blog_result = format_blog(
                script=idea['script'],
                title=idea['title'],
                content_id="test-005",
            )
            
            return {
                'idea_id': idea['id'],
                'blog_content': blog_result.formatted_content,
                'word_count': blog_result.metadata.word_count,
                'success': True
            }
        
        config = BatchConfig(
            max_concurrent=5,
            mode=ProcessingMode.PARALLEL,
            retry_attempts=1
        )
        processor = BatchProcessor(config)
        
        report = await processor.process_batch(
            ideas=sample_ideas_batch,
            process_func=process_with_blog
        )
        
        assert report.total_items == 20
        assert report.success_count == 20
        assert report.failure_count == 0
    
    async def test_batch_process_with_seo_optimization(self, sample_ideas_batch):
        """Test batch processing ideas with SEO optimization."""
        async def process_with_seo(idea):
            """Process idea: optimize SEO."""
            await asyncio.sleep(0.01)  # Simulate processing
            
            seo_result = process_content_seo(
                title=idea['title'],
                script=idea['script']
            )
            
            return {
                'idea_id': idea['id'],
                'keywords': seo_result['primary_keywords'],
                'quality_score': seo_result['quality_score'],
                'success': True
            }
        
        config = BatchConfig(
            max_concurrent=5,
            mode=ProcessingMode.PARALLEL,
            retry_attempts=1
        )
        processor = BatchProcessor(config)
        
        report = await processor.process_batch(
            ideas=sample_ideas_batch,
            process_func=process_with_seo
        )
        
        assert report.total_items == 20
        assert report.success_count == 20
        assert report.failure_count == 0
    
    async def test_batch_complete_pipeline(self, sample_ideas_batch):
        """Test batch processing with complete pipeline: Blog → SEO."""
        async def process_complete_pipeline(idea):
            """Process idea through complete pipeline."""
            await asyncio.sleep(0.02)  # Simulate processing
            
            # Step 1: Format as blog
            blog_result = format_blog(
                script=idea['script'],
                title=idea['title'],
                content_id="test-006",
            )
            
            # Step 2: Optimize SEO
            seo_result = process_content_seo(
                title=idea['title'],
                script=blog_result.formatted_content
            )
            
            return {
                'idea_id': idea['id'],
                'blog_word_count': blog_result.metadata.word_count,
                'seo_keywords': seo_result['primary_keywords'][:3],
                'seo_quality': seo_result['quality_score'],
                'success': True
            }
        
        config = BatchConfig(
            max_concurrent=5,
            mode=ProcessingMode.PARALLEL,
            retry_attempts=1
        )
        processor = BatchProcessor(config)
        
        report = await processor.process_batch(
            ideas=sample_ideas_batch,
            process_func=process_complete_pipeline
        )
        
        assert report.total_items == 20
        assert report.success_count == 20
        assert report.failure_count == 0
        assert report.total_duration > 0
    
    async def test_batch_with_error_handling(self):
        """Test batch processing with error handling in pipeline."""
        # Create test data with some that will fail
        test_ideas = [
            {"id": f"idea-{i}", "title": "Test" if i % 5 != 0 else "", "script": "Content"}
            for i in range(10)
        ]
        
        async def process_with_validation(idea):
            """Process with validation that can fail."""
            await asyncio.sleep(0.01)
            
            if not idea['title']:
                raise ValueError("Empty title")
            
            # Format blog
            blog_result = format_blog(
                script=idea['script'],
                title=idea['title'],
                content_id="test-007",
            )
            
            return {'idea_id': idea['id'], 'success': True}
        
        config = BatchConfig(
            max_concurrent=3,
            mode=ProcessingMode.PARALLEL,
            retry_attempts=1
        )
        processor = BatchProcessor(config)
        
        report = await processor.process_batch(
            ideas=test_ideas,
            process_func=process_with_validation
        )
        
        # Should have some failures (empty titles)
        assert report.failure_count > 0
        assert report.success_count + report.failure_count == report.total_items


# ============================================================================
# Integration Tests: Performance & Scalability
# ============================================================================

@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceIntegration:
    """Test performance and scalability of integrated features."""
    
    def test_seo_performance_with_blog_format(self, sample_title, sample_script):
        """Test that blog formatting + SEO completes in acceptable time."""
        import time
        
        start = time.time()
        
        # Format as blog
        blog_result = format_blog(
            script=sample_script,
            title=sample_title,
            content_id="test-008",
        )
        
        # Optimize SEO
        seo_result = process_content_seo(
            title=sample_title,
            script=blog_result.formatted_content
        )
        
        elapsed = time.time() - start
        
        # Combined operation should complete in under 3 seconds
        assert elapsed < 3.0
        assert seo_result['quality_score'] > 0
    
    @pytest.mark.asyncio
    async def test_batch_processing_speed(self):
        """Test batch processing meets performance requirements."""
        # Create 50 test ideas
        ideas = [
            {
                "id": f"idea-{i:03d}",
                "title": f"Test Title {i}",
                "script": f"Test content for idea {i}. " * 30
            }
            for i in range(50)
        ]
        
        async def process_fast(idea):
            """Fast processing function."""
            await asyncio.sleep(0.01)
            blog_result = format_blog(
                script=idea['script'],
                title=idea['title'],
                content_id="test-009",
            )
            return {'id': idea['id'], 'success': True}
        
        config = BatchConfig(
            max_concurrent=10,
            mode=ProcessingMode.PARALLEL,
            retry_attempts=1
        )
        processor = BatchProcessor(config)
        
        import time
        start = time.time()
        
        report = await processor.process_batch(
            ideas=ideas,
            process_func=process_fast
        )
        
        elapsed = time.time() - start
        
        # 50 items with concurrency=10 should complete in reasonable time
        assert report.success_count == 50
        assert elapsed < 10.0  # Should be much faster with concurrency
    
    def test_multiple_platform_exports(self, sample_title, sample_script):
        """Test exporting to multiple platforms maintains performance."""
        platforms = ["medium", "wordpress", "ghost", "dev.to"]
        
        import time
        start = time.time()
        
        for platform in platforms:
            exported = export_for_platform(
                script=sample_script,
                title=sample_title,
                content_id=f"test-010-{platform}",
                platform=platform
            )
            
            assert exported is not None
            assert exported.success is True
        
        elapsed = time.time() - start
        
        # All 4 platforms should export in under 2 seconds total
        assert elapsed < 2.0


# ============================================================================
# Integration Tests: Data Flow & Consistency
# ============================================================================

@pytest.mark.integration
class TestDataFlowConsistency:
    """Test data consistency across integrated modules."""
    
    def test_keyword_consistency_across_formats(self, sample_title, sample_script):
        """Test that keywords remain consistent across different formats."""
        # Get SEO for original
        seo_original = process_content_seo(
            title=sample_title,
            script=sample_script
        )
        
        # Format for different platforms
        platforms = ["medium", "wordpress", "ghost"]
        platform_keywords = {}
        
        for platform in platforms:
            blog_result = format_blog(
                script=sample_script,
                title=sample_title,
                content_id="test-011",
                platform=platform
            )
            
            seo_platform = process_content_seo(
                title=sample_title,
                script=blog_result.formatted_content
            )
            
            platform_keywords[platform] = set(seo_platform['primary_keywords'][:5])
        
        # Top keywords should have significant overlap across platforms
        base_keywords = set(seo_original['primary_keywords'][:5])
        
        for platform, keywords in platform_keywords.items():
            overlap = base_keywords.intersection(keywords)
            # At least 3 of top 5 should overlap
            assert len(overlap) >= 3, f"Platform {platform} has insufficient keyword overlap"
    
    def test_metadata_consistency(self, sample_title, sample_script):
        """Test metadata consistency between blog and SEO."""
        blog_result = format_blog(
            script=sample_script,
            title=sample_title,
            content_id="test-012",
        )
        
        seo_result = process_content_seo(
            title=sample_title,
            script=sample_script
        )
        
        # Both should report similar content metrics
        blog_words = blog_result.metadata.word_count
        seo_words = seo_result['total_words']
        
        # Should be within 30% of each other (formatting can change word count)
        diff_ratio = abs(blog_words - seo_words) / max(blog_words, seo_words)
        assert diff_ratio < 0.3
    
    @pytest.mark.asyncio
    async def test_batch_result_consistency(self):
        """Test that batch processing produces consistent results."""
        ideas = [
            {"id": "test-1", "title": "Python Guide", "script": "Learn Python programming." * 20}
        ] * 5  # Same idea 5 times
        
        async def process_idea(idea):
            """Process single idea."""
            await asyncio.sleep(0.01)
            
            blog = format_blog(script=idea['script'], title=idea['title'], content_id=idea['id'])
            seo = process_content_seo(title=idea['title'], script=blog.formatted_content)
            
            return {
                'keywords': seo['primary_keywords'][:3],
                'quality': seo['quality_score'],
                'word_count': blog.metadata.word_count
            }
        
        config = BatchConfig(
            max_concurrent=3,
            mode=ProcessingMode.PARALLEL,
            retry_attempts=1
        )
        processor = BatchProcessor(config)
        
        report = await processor.process_batch(
            ideas=ideas,
            process_func=process_idea
        )
        
        assert report.success_count == 5
        
        # Note: Results should be consistent but we can't directly check
        # the results dict from the batch processor in this version


# ============================================================================
# Integration Tests: Edge Cases & Error Handling
# ============================================================================

@pytest.mark.integration
class TestEdgeCasesIntegration:
    """Test edge cases in integrated workflows."""
    
    def test_minimal_content_through_pipeline(self):
        """Test minimal content through complete pipeline."""
        minimal_title = "Test"
        minimal_script = "Test content."
        
        # Should not crash
        blog_result = format_blog(
            script=minimal_script,
            title=minimal_title,
            content_id="test-014",
        )
        
        seo_result = process_content_seo(
            title=minimal_title,
            script=blog_result.formatted_content
        )
        
        assert isinstance(blog_result, BlogFormattedContent)
        assert isinstance(seo_result, dict)
    
    def test_large_content_through_pipeline(self):
        """Test large content through complete pipeline."""
        large_title = "Comprehensive Python Guide for Beginners"
        large_script = "Python programming is important. " * 1000  # ~5000 words
        
        blog_result = format_blog(
            script=large_script,
            title=large_title,
            content_id="test-015",
        )
        
        seo_result = process_content_seo(
            title=large_title,
            script=blog_result.formatted_content
        )
        
        # Should handle large content
        assert blog_result.metadata.word_count > 1000
        assert len(seo_result['primary_keywords']) > 0
    
    def test_special_characters_through_pipeline(self):
        """Test special characters are handled correctly."""
        special_title = "Python 101: \"Learn\" & 'Master' Programming"
        special_script = "Learn Python™ with examples® and tutorials©. Café, naïve, résumé."
        
        blog_result = format_blog(
            script=special_script,
            title=special_title,
            content_id="test-016",
        )
        
        seo_result = process_content_seo(
            title=special_title,
            script=blog_result.formatted_content
        )
        
        # Should handle special characters without crashing
        assert len(blog_result.formatted_content) > 0
        assert len(seo_result['primary_keywords']) > 0
    
    @pytest.mark.asyncio
    async def test_batch_with_mixed_quality_content(self):
        """Test batch processing with varying content quality."""
        mixed_ideas = [
            {"id": "good-1", "title": "Python Programming Guide", "script": "Learn Python. " * 100},
            {"id": "short-1", "title": "Test", "script": "Test."},
            {"id": "good-2", "title": "Web Development", "script": "Build websites. " * 100},
            {"id": "empty-1", "title": "Empty", "script": ""},
        ]
        
        async def process_mixed(idea):
            """Process with tolerance for varying quality."""
            await asyncio.sleep(0.01)
            
            blog = format_blog(script=idea['script'], title=idea['title'], content_id=idea['id'])
            seo = process_content_seo(title=idea['title'], script=idea['script'])
            
            return {'id': idea['id'], 'success': True}
        
        config = BatchConfig(
            max_concurrent=2,
            mode=ProcessingMode.PARALLEL,
            retry_attempts=1
        )
        processor = BatchProcessor(config)
        
        report = await processor.process_batch(
            ideas=mixed_ideas,
            process_func=process_mixed
        )
        
        # Should complete without crashes
        assert report.total_items == 4
        assert report.processed_items == 4


# ============================================================================
# Integration Tests: End-to-End Workflow
# ============================================================================

@pytest.mark.integration
class TestEndToEndWorkflow:
    """Test complete end-to-end workflow scenarios."""
    
    def test_complete_content_pipeline(self, sample_title, sample_script):
        """Test complete content pipeline from script to published format."""
        # Step 1: Format as blog
        blog_result = format_blog(
            script=sample_script,
            title=sample_title,
            content_id="test-018",
            platform="medium"
        )
        
        # Step 2: Optimize SEO
        seo_result = process_content_seo(
            title=sample_title,
            script=blog_result.formatted_content,
            extraction_method="hybrid",
            include_related=True
        )
        
        # Step 3: Export for platform (which is same as format_blog with platform specified)
        exported = format_blog(
            script=sample_script,
            title=sample_title,
            content_id="test-020",
            platform="medium"
        )
        
        # Verify complete pipeline
        assert blog_result.metadata.word_count > 0
        assert len(seo_result['primary_keywords']) >= 3
        assert seo_result['quality_score'] > 0
        assert len(seo_result['meta_description']) >= 120
        assert exported is not None
        assert exported.success is True
    
    @pytest.mark.asyncio
    async def test_batch_multi_platform_workflow(self):
        """Test batch processing for multiple platforms."""
        ideas = [
            {"id": f"idea-{i}", "title": f"Guide {i}", "script": f"Content {i}. " * 50}
            for i in range(10)
        ]
        
        platforms = ["medium", "wordpress", "ghost"]
        
        async def process_multi_platform(idea):
            """Process idea for multiple platforms."""
            await asyncio.sleep(0.02)
            
            results = {}
            for platform in platforms:
                blog = format_blog(
                    script=idea['script'],
                    title=idea['title'],
                    content_id="test-019",
                    platform=platform
                )
                
                seo = process_content_seo(
                    title=idea['title'],
                    script=blog.formatted_content
                )
                
                results[platform] = {
                    'word_count': blog.metadata.word_count,
                    'keywords': seo['primary_keywords'][:3],
                    'quality': seo['quality_score']
                }
            
            return {'id': idea['id'], 'platforms': results, 'success': True}
        
        config = BatchConfig(
            max_concurrent=5,
            mode=ProcessingMode.PARALLEL,
            retry_attempts=1
        )
        processor = BatchProcessor(config)
        
        report = await processor.process_batch(
            ideas=ideas,
            process_func=process_multi_platform
        )
        
        assert report.success_count == 10
        assert report.failure_count == 0
