"""Integration tests for SEO Keywords module."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(project_root))

import pytest
from T.Publishing.SEO.Keywords import (
    process_content_seo,
    extract_keywords,
    generate_seo_metadata,
    KeywordExtractor,
    MetadataGenerator,
    KeywordExtractionResult,
    SEOMetadata
)


@pytest.fixture
def sample_content():
    """Sample content for testing."""
    return {
        "title": "Complete Guide to Python Programming for Beginners",
        "script": """
        Python is one of the most popular programming languages in the world. 
        Learning Python programming opens doors to exciting careers in software 
        development, data science, machine learning, and web development.
        
        Python's simple syntax makes it an ideal programming language for beginners.
        The Python programming community is large and supportive, providing countless
        tutorials, libraries, and frameworks. Many beginners start their programming
        journey with Python because of its readability and versatility.
        
        To learn Python effectively, practice coding regularly and work on real
        projects. Start with basic concepts like variables, loops, and functions,
        then progress to more advanced topics. Python programming skills are highly
        valued in the tech industry, and mastering Python can lead to numerous
        job opportunities in software engineering and data analysis.
        
        The best way to become proficient in Python is through consistent practice
        and building real-world applications. Join online communities, contribute
        to open source projects, and never stop learning. Python's extensive
        standard library and third-party packages make it suitable for everything
        from simple scripts to complex applications.
        """
    }


class TestModuleExports:
    """Test that all expected exports are available."""
    
    def test_classes_exported(self):
        """Test that classes are properly exported."""
        assert KeywordExtractor is not None
        assert MetadataGenerator is not None
        assert KeywordExtractionResult is not None
        assert SEOMetadata is not None
    
    def test_functions_exported(self):
        """Test that functions are properly exported."""
        assert extract_keywords is not None
        assert generate_seo_metadata is not None
        assert process_content_seo is not None


class TestProcessContentSEO:
    """Test the main process_content_seo function."""
    
    def test_process_content_basic(self, sample_content):
        """Test basic content SEO processing."""
        result = process_content_seo(
            title=sample_content["title"],
            script=sample_content["script"]
        )
        
        assert isinstance(result, dict)
        
        # Check all expected keys are present
        expected_keys = [
            'primary_keywords', 'secondary_keywords', 'keyword_scores',
            'keyword_density', 'related_keywords', 'meta_description',
            'title_tag', 'og_title', 'og_description', 'quality_score',
            'recommendations', 'extraction_method', 'total_words',
            'generation_timestamp'
        ]
        
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"
    
    def test_process_content_with_all_params(self, sample_content):
        """Test processing with all parameters."""
        result = process_content_seo(
            title=sample_content["title"],
            script=sample_content["script"],
            extraction_method="hybrid",
            primary_count=7,
            secondary_count=15,
            brand_name="CodeAcademy",
            include_related=True
        )
        
        assert len(result['primary_keywords']) <= 7
        assert len(result['secondary_keywords']) <= 15
        assert result['extraction_method'] == "hybrid"
        assert "CodeAcademy" in result['title_tag'] or len(result['title_tag']) <= 60
    
    def test_process_content_keywords_extracted(self, sample_content):
        """Test that keywords are properly extracted."""
        result = process_content_seo(
            title=sample_content["title"],
            script=sample_content["script"]
        )
        
        assert len(result['primary_keywords']) > 0
        assert len(result['secondary_keywords']) > 0
        
        # Should extract relevant keywords
        all_keywords = result['primary_keywords'] + result['secondary_keywords']
        keywords_str = " ".join(all_keywords)
        assert "python" in keywords_str
        assert any(term in keywords_str for term in ["programming", "learn", "code"])
    
    def test_process_content_metadata_generated(self, sample_content):
        """Test that SEO metadata is properly generated."""
        result = process_content_seo(
            title=sample_content["title"],
            script=sample_content["script"]
        )
        
        # Meta description should be within range
        desc_len = len(result['meta_description'])
        assert 120 <= desc_len <= 180  # With some tolerance
        
        # Title tag should be within limit
        title_len = len(result['title_tag'])
        assert title_len <= 70
        
        # OG metadata should be present
        assert len(result['og_title']) > 0
        assert len(result['og_description']) > 0
    
    def test_process_content_quality_score(self, sample_content):
        """Test that quality score is calculated."""
        result = process_content_seo(
            title=sample_content["title"],
            script=sample_content["script"]
        )
        
        assert 0 <= result['quality_score'] <= 100
        # With good content, should score reasonably well
        assert result['quality_score'] >= 40
    
    def test_process_content_recommendations(self, sample_content):
        """Test that recommendations are provided."""
        result = process_content_seo(
            title=sample_content["title"],
            script=sample_content["script"]
        )
        
        assert isinstance(result['recommendations'], list)
        assert len(result['recommendations']) > 0
    
    def test_process_content_related_keywords(self, sample_content):
        """Test related keyword suggestions."""
        result = process_content_seo(
            title=sample_content["title"],
            script=sample_content["script"],
            include_related=True
        )
        
        assert 'related_keywords' in result
        assert isinstance(result['related_keywords'], list)
        # Should have some related keywords
        assert len(result['related_keywords']) > 0
    
    def test_process_content_without_related(self, sample_content):
        """Test processing without related keywords."""
        result = process_content_seo(
            title=sample_content["title"],
            script=sample_content["script"],
            include_related=False
        )
        
        assert result['related_keywords'] == []


class TestExtractionMethods:
    """Test different extraction methods."""
    
    def test_tfidf_method(self, sample_content):
        """Test TF-IDF extraction method."""
        result = process_content_seo(
            title=sample_content["title"],
            script=sample_content["script"],
            extraction_method="tfidf"
        )
        
        assert result['extraction_method'] == "tfidf"
        assert len(result['primary_keywords']) > 0
    
    def test_frequency_method(self, sample_content):
        """Test frequency extraction method."""
        result = process_content_seo(
            title=sample_content["title"],
            script=sample_content["script"],
            extraction_method="frequency"
        )
        
        assert result['extraction_method'] == "frequency"
        assert len(result['primary_keywords']) > 0
    
    def test_hybrid_method(self, sample_content):
        """Test hybrid extraction method."""
        result = process_content_seo(
            title=sample_content["title"],
            script=sample_content["script"],
            extraction_method="hybrid"
        )
        
        assert result['extraction_method'] == "hybrid"
        assert len(result['primary_keywords']) > 0
    
    def test_methods_produce_different_results(self, sample_content):
        """Test that different methods can produce different results."""
        tfidf_result = process_content_seo(
            title=sample_content["title"],
            script=sample_content["script"],
            extraction_method="tfidf"
        )
        
        freq_result = process_content_seo(
            title=sample_content["title"],
            script=sample_content["script"],
            extraction_method="frequency"
        )
        
        # Methods may produce different top keywords
        # (though there will be overlap with good content)
        assert tfidf_result['extraction_method'] != freq_result['extraction_method']


class TestContentVariations:
    """Test with various content types."""
    
    def test_short_content(self):
        """Test with short content."""
        result = process_content_seo(
            title="Python Basics",
            script="Learn Python programming. Python is easy to learn and powerful for beginners."
        )
        
        assert len(result['primary_keywords']) > 0
        assert len(result['meta_description']) > 0
    
    def test_technical_content(self):
        """Test with technical content."""
        result = process_content_seo(
            title="Machine Learning with Python",
            script="""
            Machine learning algorithms enable computers to learn from data.
            Python provides excellent libraries for machine learning including
            scikit-learn, TensorFlow, and PyTorch. Deep learning neural networks
            can solve complex problems in computer vision and natural language processing.
            """
        )
        
        keywords_str = " ".join(result['primary_keywords'] + result['secondary_keywords'])
        assert any(term in keywords_str for term in ["machine", "learning", "python"])
    
    def test_blog_style_content(self):
        """Test with blog-style content."""
        result = process_content_seo(
            title="10 Tips for Learning Python Fast",
            script="""
            Want to learn Python quickly? Here are my top tips. First, practice
            coding every day. Second, build real projects. Third, join a community.
            Python is easier to learn when you have support and practical experience.
            """
        )
        
        assert len(result['primary_keywords']) > 0
        assert "python" in " ".join(result['primary_keywords'] + result['secondary_keywords'])


class TestBrandIntegration:
    """Test brand name integration."""
    
    def test_with_brand_name(self, sample_content):
        """Test processing with brand name."""
        result = process_content_seo(
            title=sample_content["title"],
            script=sample_content["script"],
            brand_name="PythonMaster"
        )
        
        # Brand should appear in title tag or title is within limit
        assert "PythonMaster" in result['title_tag'] or len(result['title_tag']) <= 60
    
    def test_without_brand_name(self, sample_content):
        """Test processing without brand name."""
        result = process_content_seo(
            title=sample_content["title"],
            script=sample_content["script"]
        )
        
        assert len(result['title_tag']) > 0
        # Should be based on original title
        assert any(word in result['title_tag'] for word in ["Python", "Guide", "Programming"])


class TestKeywordDensity:
    """Test keyword density analysis."""
    
    def test_density_calculated(self, sample_content):
        """Test that keyword density is calculated."""
        result = process_content_seo(
            title=sample_content["title"],
            script=sample_content["script"]
        )
        
        assert len(result['keyword_density']) > 0
        
        # Density values should be reasonable
        for density in result['keyword_density'].values():
            assert 0 <= density <= 10  # Max 10% seems reasonable
    
    def test_density_correlates_with_keywords(self, sample_content):
        """Test that density matches extracted keywords."""
        result = process_content_seo(
            title=sample_content["title"],
            script=sample_content["script"]
        )
        
        # Primary keywords should have density entries
        for keyword in result['primary_keywords'][:3]:
            assert keyword in result['keyword_density']


class TestKeywordScores:
    """Test keyword scoring."""
    
    def test_scores_present(self, sample_content):
        """Test that keyword scores are included."""
        result = process_content_seo(
            title=sample_content["title"],
            script=sample_content["script"]
        )
        
        assert len(result['keyword_scores']) > 0
    
    def test_scores_valid_range(self, sample_content):
        """Test that scores are in valid range."""
        result = process_content_seo(
            title=sample_content["title"],
            script=sample_content["script"]
        )
        
        # Scores should be between 0 and 1
        for score in result['keyword_scores'].values():
            assert 0 <= score <= 1


class TestEndToEndWorkflow:
    """Test complete end-to-end SEO workflow."""
    
    def test_complete_workflow(self, sample_content):
        """Test complete SEO processing workflow."""
        # Process content
        result = process_content_seo(
            title=sample_content["title"],
            script=sample_content["script"],
            extraction_method="hybrid",
            primary_count=5,
            secondary_count=10,
            brand_name="LearnPython",
            include_related=True
        )
        
        # Verify complete output
        assert isinstance(result, dict)
        
        # Keywords extracted
        assert len(result['primary_keywords']) > 0
        assert len(result['secondary_keywords']) > 0
        assert len(result['related_keywords']) > 0
        
        # Metadata generated
        assert len(result['meta_description']) >= 120
        assert len(result['title_tag']) > 0
        assert len(result['og_title']) > 0
        assert len(result['og_description']) > 0
        
        # Quality assessed
        assert result['quality_score'] > 0
        assert len(result['recommendations']) > 0
        
        # Verify metadata quality
        assert len(result['meta_description']) > 0  # Has content
        assert not result['title_tag'].startswith(' ')  # No leading space
        assert not result['title_tag'].endswith(' ')  # No trailing space
    
    def test_workflow_produces_consistent_results(self, sample_content):
        """Test that workflow produces consistent results."""
        result1 = process_content_seo(
            title=sample_content["title"],
            script=sample_content["script"],
            extraction_method="tfidf"
        )
        
        result2 = process_content_seo(
            title=sample_content["title"],
            script=sample_content["script"],
            extraction_method="tfidf"
        )
        
        # Should produce same results with same inputs
        assert result1['primary_keywords'] == result2['primary_keywords']
        assert result1['meta_description'] == result2['meta_description']


class TestPerformance:
    """Test performance requirements."""
    
    def test_processing_speed(self, sample_content):
        """Test that processing completes quickly."""
        import time
        
        start_time = time.time()
        result = process_content_seo(
            title=sample_content["title"],
            script=sample_content["script"]
        )
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should complete in under 2 seconds (requirement from spec)
        assert processing_time < 2.0
        assert result is not None


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_content(self):
        """Test with empty content."""
        result = process_content_seo(
            title="",
            script=""
        )
        
        assert isinstance(result, dict)
        assert 'meta_description' in result
    
    def test_minimal_content(self):
        """Test with minimal content."""
        result = process_content_seo(
            title="Test",
            script="Test."
        )
        
        assert isinstance(result, dict)
        assert len(result['meta_description']) > 0
    
    def test_unicode_content(self):
        """Test with unicode characters."""
        result = process_content_seo(
            title="Python Programming: 編程教程",
            script="Learn Python with examples. Café, naïve, 日本語"
        )
        
        assert isinstance(result, dict)
        assert len(result['primary_keywords']) > 0
