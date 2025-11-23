"""Tests for AI-powered SEO metadata generator (POST-001).

Tests the prompt engineering and AI integration for SEO metadata generation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from T.Publishing.SEO.Keywords.ai_metadata_generator import (
    AIMetadataGenerator,
    AIConfig,
    generate_ai_seo_metadata
)
from T.Publishing.SEO.Keywords.metadata_generator import SEOMetadata


class TestAIConfig:
    """Test AI configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = AIConfig()
        assert config.model == "llama3.1:70b-q4_K_M"
        assert config.api_base == "http://localhost:11434"
        assert config.temperature == 0.3
        assert config.max_tokens == 500
        assert config.timeout == 30
        assert config.enable_ai is True
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = AIConfig(
            model="llama3.1:8b",
            temperature=0.5,
            enable_ai=False
        )
        assert config.model == "llama3.1:8b"
        assert config.temperature == 0.5
        assert config.enable_ai is False


class TestAIMetadataGenerator:
    """Test AI metadata generator."""
    
    @pytest.fixture
    def generator(self):
        """Create generator with AI disabled for testing."""
        config = AIConfig(enable_ai=False)
        return AIMetadataGenerator(config=config)
    
    @pytest.fixture
    def sample_content(self):
        """Sample content for testing."""
        return {
            'title': "How to Learn Python Programming in 2024",
            'script': "Python is a versatile programming language that's perfect for beginners. "
                     "With its simple syntax and powerful libraries, you can build web applications, "
                     "automate tasks, analyze data, and even create AI models. This comprehensive guide "
                     "will walk you through everything you need to know to master Python programming. "
                     "From basic syntax to advanced concepts, we'll cover data structures, functions, "
                     "object-oriented programming, and popular frameworks like Django and Flask.",
            'primary_keywords': ["python", "programming", "learn", "beginners", "guide"],
            'secondary_keywords': ["syntax", "libraries", "data", "web", "applications"]
        }
    
    def test_generator_initialization(self):
        """Test generator initialization."""
        config = AIConfig(enable_ai=False)
        generator = AIMetadataGenerator(config=config, brand_name="TechEdu")
        
        assert generator.config == config
        assert generator.brand_name == "TechEdu"
        assert generator.include_brand is True
        assert generator.available is False  # AI disabled
    
    def test_check_ollama_availability_disabled(self):
        """Test availability check when AI is disabled."""
        config = AIConfig(enable_ai=False)
        generator = AIMetadataGenerator(config=config)
        
        assert generator.available is False
    
    @patch('requests.get')
    def test_check_ollama_availability_success(self, mock_get):
        """Test availability check when Ollama is running."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        config = AIConfig(enable_ai=True)
        generator = AIMetadataGenerator(config=config)
        
        assert generator.available is True
    
    @patch('requests.get')
    def test_check_ollama_availability_failure(self, mock_get):
        """Test availability check when Ollama is not running."""
        mock_get.side_effect = Exception("Connection refused")
        
        config = AIConfig(enable_ai=True)
        generator = AIMetadataGenerator(config=config)
        
        assert generator.available is False
    
    def test_fallback_meta_description(self, generator, sample_content):
        """Test fallback meta description generation."""
        description = generator._fallback_meta_description(
            title=sample_content['title'],
            script=sample_content['script'],
            keywords=sample_content['primary_keywords']
        )
        
        assert isinstance(description, str)
        assert 150 <= len(description) <= 160
        assert len(description) > 0
    
    def test_fallback_title_tag(self, generator, sample_content):
        """Test fallback title tag generation."""
        generator.brand_name = "TechEdu"
        title_tag = generator._fallback_title_tag(
            title=sample_content['title'],
            keywords=sample_content['primary_keywords']
        )
        
        assert isinstance(title_tag, str)
        assert len(title_tag) <= 60
        assert "TechEdu" in title_tag
    
    def test_fallback_title_tag_without_brand(self, generator, sample_content):
        """Test fallback title tag without brand."""
        generator.brand_name = None
        title_tag = generator._fallback_title_tag(
            title=sample_content['title'],
            keywords=sample_content['primary_keywords']
        )
        
        assert isinstance(title_tag, str)
        assert len(title_tag) <= 60
    
    def test_generate_meta_description_fallback(self, generator, sample_content):
        """Test meta description generation with fallback."""
        description = generator.generate_meta_description(
            title=sample_content['title'],
            script=sample_content['script'],
            primary_keywords=sample_content['primary_keywords']
        )
        
        assert isinstance(description, str)
        assert 140 <= len(description) <= 170  # Allow slight variance
    
    def test_generate_title_tag_fallback(self, generator, sample_content):
        """Test title tag generation with fallback."""
        title_tag = generator.generate_title_tag(
            title=sample_content['title'],
            primary_keywords=sample_content['primary_keywords']
        )
        
        assert isinstance(title_tag, str)
        assert len(title_tag) <= 70  # Allow slight variance for brand
    
    def test_suggest_related_keywords_no_ai(self, generator, sample_content):
        """Test related keywords when AI is not available."""
        keywords = generator.suggest_related_keywords(
            title=sample_content['title'],
            script=sample_content['script'],
            primary_keywords=sample_content['primary_keywords']
        )
        
        # Should return empty list when AI is not available
        assert isinstance(keywords, list)
        assert len(keywords) == 0
    
    def test_generate_og_description_fallback(self, generator, sample_content):
        """Test OG description generation with fallback."""
        meta_description = "Learn Python programming in 2024 with this comprehensive guide for beginners. Master syntax, libraries, data structures, and popular frameworks."
        
        og_description = generator.generate_og_description(
            title=sample_content['title'],
            script=sample_content['script'],
            meta_description=meta_description,
            primary_keywords=sample_content['primary_keywords']
        )
        
        assert isinstance(og_description, str)
        assert len(og_description) <= 210  # Allow slight variance
    
    def test_extract_meta_description(self, generator):
        """Test extraction of meta description from AI response."""
        # With prefix
        response = "Meta Description: This is a test description"
        extracted = generator._extract_meta_description(response)
        assert extracted == "This is a test description"
        
        # Without prefix
        response = "This is a test description"
        extracted = generator._extract_meta_description(response)
        assert extracted == "This is a test description"
        
        # With quotes
        response = '"This is a test description"'
        extracted = generator._extract_meta_description(response)
        assert extracted == "This is a test description"
    
    def test_extract_title_tag(self, generator):
        """Test extraction of title tag from AI response."""
        # With prefix
        response = "Optimized Title: Test Title"
        extracted = generator._extract_title_tag(response)
        assert "Test Title" in extracted
        
        # Without prefix
        response = "Test Title"
        extracted = generator._extract_title_tag(response)
        assert "Test Title" in extracted
    
    def test_extract_title_tag_with_brand(self, generator):
        """Test title tag extraction with brand addition."""
        generator.brand_name = "TechEdu"
        generator.include_brand = True
        
        response = "Python Guide"
        extracted = generator._extract_title_tag(response)
        
        assert "Python Guide" in extracted
        assert "TechEdu" in extracted
    
    def test_extract_keywords_list_json(self, generator):
        """Test extraction of keywords from JSON response."""
        response = '["keyword1", "keyword2", "keyword3"]'
        keywords = generator._extract_keywords_list(response)
        
        assert isinstance(keywords, list)
        assert len(keywords) == 3
        assert "keyword1" in keywords
    
    def test_extract_keywords_list_text(self, generator):
        """Test extraction of keywords from text response."""
        response = """
        - keyword1
        - keyword2
        - keyword3
        """
        keywords = generator._extract_keywords_list(response)
        
        assert isinstance(keywords, list)
        assert len(keywords) >= 3
    
    def test_extract_og_description(self, generator):
        """Test extraction of OG description from AI response."""
        # With prefix
        response = "OG Description: This is a social media description"
        extracted = generator._extract_og_description(response)
        assert extracted == "This is a social media description"
        
        # Without prefix
        response = "This is a social media description"
        extracted = generator._extract_og_description(response)
        assert extracted == "This is a social media description"
    
    @patch('requests.post')
    def test_call_ollama_success(self, mock_post):
        """Test successful Ollama API call."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Generated content"}
        mock_post.return_value = mock_response
        
        config = AIConfig(enable_ai=True)
        generator = AIMetadataGenerator(config=config)
        generator.available = True  # Force availability for test
        
        result = generator._call_ollama("Test prompt")
        assert result == "Generated content"
    
    @patch('requests.post')
    def test_call_ollama_failure(self, mock_post):
        """Test failed Ollama API call."""
        mock_post.side_effect = Exception("Connection error")
        
        config = AIConfig(enable_ai=True)
        generator = AIMetadataGenerator(config=config)
        generator.available = True  # Force availability for test
        
        with pytest.raises(RuntimeError):
            generator._call_ollama("Test prompt")


class TestPromptEngineering:
    """Test prompt engineering quality."""
    
    @pytest.fixture
    def generator(self):
        """Create generator for prompt testing."""
        config = AIConfig(enable_ai=False)
        return AIMetadataGenerator(config=config)
    
    @pytest.fixture
    def sample_content(self):
        """Sample content for testing."""
        return {
            'title': "Complete Guide to Machine Learning",
            'script': "Machine learning is a subset of artificial intelligence that enables "
                     "computers to learn from data without explicit programming. " * 10,
            'keywords': ["machine learning", "ai", "data science", "algorithms"]
        }
    
    def test_meta_description_prompt_structure(self, generator, sample_content):
        """Test meta description prompt structure."""
        prompt = generator._create_meta_description_prompt(
            title=sample_content['title'],
            script=sample_content['script'],
            keywords=sample_content['keywords'],
            target_length=155
        )
        
        # Check prompt contains key elements
        assert "expert SEO specialist" in prompt.lower()
        assert sample_content['title'] in prompt
        assert "150-160 characters" in prompt
        assert "primary keyword" in prompt.lower()
        assert "call-to-action" in prompt.lower()
        
        # Check keywords are included
        for keyword in sample_content['keywords'][:3]:
            assert keyword in prompt.lower()
    
    def test_title_tag_prompt_structure(self, generator, sample_content):
        """Test title tag prompt structure."""
        prompt = generator._create_title_tag_prompt(
            title=sample_content['title'],
            keywords=sample_content['keywords'],
            brand_name="TechBrand"
        )
        
        # Check prompt contains key elements
        assert "expert SEO specialist" in prompt.lower()
        assert "title tag" in prompt.lower()
        assert sample_content['title'] in prompt
        assert "TechBrand" in prompt
        assert "60 characters" in prompt or "characters" in prompt
        
        # Check keywords are mentioned
        assert any(kw in prompt.lower() for kw in sample_content['keywords'][:3])
    
    def test_related_keywords_prompt_structure(self, generator, sample_content):
        """Test related keywords prompt structure."""
        prompt = generator._create_related_keywords_prompt(
            title=sample_content['title'],
            script=sample_content['script'],
            keywords=sample_content['keywords'],
            max_count=10
        )
        
        # Check prompt contains key elements
        assert "SEO specialist" in prompt.lower()
        assert "related keywords" in prompt.lower()
        assert sample_content['title'] in prompt
        assert "JSON array" in prompt
        
        # Check it asks for the right number
        assert "10" in prompt
    
    def test_og_description_prompt_structure(self, generator, sample_content):
        """Test OG description prompt structure."""
        meta_desc = "A comprehensive guide to understanding machine learning and AI."
        
        prompt = generator._create_og_description_prompt(
            title=sample_content['title'],
            script=sample_content['script'],
            meta_description=meta_desc,
            keywords=sample_content['keywords']
        )
        
        # Check prompt contains key elements
        assert "social media" in prompt.lower()
        assert "Open Graph" in prompt or "OG" in prompt
        assert sample_content['title'] in prompt
        assert meta_desc in prompt
        assert "200 characters" in prompt


class TestGenerateAISEOMetadata:
    """Test convenience function for AI-powered metadata generation."""
    
    @pytest.fixture
    def sample_data(self):
        """Sample data for testing."""
        return {
            'title': "Ultimate Python Tutorial for Beginners",
            'script': "Python is an amazing programming language. " * 20,
            'primary_keywords': ["python", "tutorial", "beginners", "programming"],
            'secondary_keywords': ["learning", "code", "syntax", "examples"],
            'keyword_density': {"python": 2.5, "tutorial": 1.8}
        }
    
    def test_generate_ai_seo_metadata_fallback(self, sample_data):
        """Test AI metadata generation with fallback."""
        config = AIConfig(enable_ai=False)
        
        metadata = generate_ai_seo_metadata(
            title=sample_data['title'],
            script=sample_data['script'],
            primary_keywords=sample_data['primary_keywords'],
            secondary_keywords=sample_data['secondary_keywords'],
            keyword_density=sample_data['keyword_density'],
            config=config,
            brand_name="TechEdu"
        )
        
        # Check metadata structure
        assert isinstance(metadata, SEOMetadata)
        assert metadata.meta_description != ""
        assert metadata.title_tag != ""
        assert len(metadata.primary_keywords) > 0
        assert metadata.quality_score >= 0
        assert metadata.quality_score <= 100
    
    def test_generate_ai_seo_metadata_with_brand(self, sample_data):
        """Test metadata generation with brand name."""
        config = AIConfig(enable_ai=False)
        
        metadata = generate_ai_seo_metadata(
            title=sample_data['title'],
            script=sample_data['script'],
            primary_keywords=sample_data['primary_keywords'],
            secondary_keywords=sample_data['secondary_keywords'],
            keyword_density=sample_data['keyword_density'],
            config=config,
            brand_name="CodeMaster"
        )
        
        assert "CodeMaster" in metadata.title_tag
    
    def test_generate_ai_seo_metadata_without_related(self, sample_data):
        """Test metadata generation without related keywords."""
        config = AIConfig(enable_ai=False)
        
        metadata = generate_ai_seo_metadata(
            title=sample_data['title'],
            script=sample_data['script'],
            primary_keywords=sample_data['primary_keywords'],
            secondary_keywords=sample_data['secondary_keywords'],
            keyword_density=sample_data['keyword_density'],
            config=config,
            generate_related=False
        )
        
        assert isinstance(metadata.related_keywords, list)


class TestAIQualityScore:
    """Test AI quality score calculation."""
    
    def test_quality_score_perfect(self):
        """Test quality score for perfect metadata."""
        from T.Publishing.SEO.Keywords.ai_metadata_generator import _calculate_ai_quality_score
        
        metadata = SEOMetadata(
            primary_keywords=["python", "tutorial", "beginners", "guide", "learn"],
            secondary_keywords=["code", "syntax", "examples", "programming", "language"],
            meta_description="A" * 155,  # Perfect length
            title_tag="Python Tutorial" + " | Brand",  # Within limit
            related_keywords=["ai", "ml", "data", "science", "analysis", "projects"],
            og_title="Python Tutorial",
            og_description="A" * 180
        )
        
        score = _calculate_ai_quality_score(metadata)
        assert score >= 80  # Should be high quality
    
    def test_quality_score_low(self):
        """Test quality score for poor metadata."""
        from T.Publishing.SEO.Keywords.ai_metadata_generator import _calculate_ai_quality_score
        
        metadata = SEOMetadata(
            primary_keywords=["python"],  # Only 1 keyword
            secondary_keywords=[],
            meta_description="Short",  # Too short
            title_tag="T",  # Very short
            related_keywords=[],
            og_title="",
            og_description=""
        )
        
        score = _calculate_ai_quality_score(metadata)
        assert score < 50  # Should be low quality


class TestAIRecommendations:
    """Test AI recommendations generation."""
    
    def test_recommendations_short_description(self):
        """Test recommendations for short description."""
        from T.Publishing.SEO.Keywords.ai_metadata_generator import _generate_ai_recommendations
        
        metadata = SEOMetadata(
            meta_description="Too short",
            title_tag="Good Title | Brand"
        )
        
        recommendations = _generate_ai_recommendations(metadata)
        assert len(recommendations) > 0
        assert any("short" in rec.lower() for rec in recommendations)
    
    def test_recommendations_long_title(self):
        """Test recommendations for long title."""
        from T.Publishing.SEO.Keywords.ai_metadata_generator import _generate_ai_recommendations
        
        metadata = SEOMetadata(
            meta_description="A" * 155,
            title_tag="A" * 70  # Too long
        )
        
        recommendations = _generate_ai_recommendations(metadata)
        assert len(recommendations) > 0
        assert any("title" in rec.lower() and "long" in rec.lower() for rec in recommendations)
    
    def test_recommendations_perfect(self):
        """Test recommendations for perfect metadata."""
        from T.Publishing.SEO.Keywords.ai_metadata_generator import _generate_ai_recommendations
        
        metadata = SEOMetadata(
            meta_description="A" * 155,
            title_tag="Perfect Title | Brand"
        )
        
        recommendations = _generate_ai_recommendations(metadata)
        assert len(recommendations) > 0
        # Should have at least the positive feedback
