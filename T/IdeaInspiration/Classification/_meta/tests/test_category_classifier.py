"""Tests for primary category classifier."""

import pytest
from src.classification import CategoryClassifier, PrimaryCategory, CategoryResult


class TestCategoryClassifier:
    """Test category classification functionality."""
    
    def test_initialization(self):
        """Test classifier initialization."""
        classifier = CategoryClassifier()
        assert classifier is not None
    
    def test_classify_storytelling_high_confidence(self):
        """Test classification of clear storytelling content."""
        classifier = CategoryClassifier()
        
        result = classifier.classify(
            title="My AITA Story - Was I Wrong?",
            description="This is my true story about what happened last week",
            tags=['storytime', 'aita', 'confession']
        )
        
        assert result.category == PrimaryCategory.STORYTELLING
        assert result.confidence > 0.3
        assert len(result.indicators) > 0
        assert any('aita' in ind.lower() for ind in result.indicators)
    
    def test_classify_storytelling_with_tifu(self):
        """Test classification of TIFU-style content."""
        classifier = CategoryClassifier()
        
        result = classifier.classify(
            title="TIFU by telling my boss the truth",
            description="Today I messed up when I decided to be honest"
        )
        
        assert result.category == PrimaryCategory.STORYTELLING
        assert result.confidence > 0.2
    
    def test_classify_entertainment_comedy(self):
        """Test classification of comedy/entertainment content."""
        classifier = CategoryClassifier()
        
        result = classifier.classify(
            title="Funniest Meme Compilation 2024",
            description="Watch these hilarious memes that will make you laugh",
            tags=['comedy', 'funny', 'memes']
        )
        
        assert result.category == PrimaryCategory.ENTERTAINMENT
        assert result.confidence > 0.3
        assert any('meme' in ind.lower() or 'funny' in ind.lower() for ind in result.indicators)
    
    def test_classify_entertainment_prank(self):
        """Test classification of prank content."""
        classifier = CategoryClassifier()
        
        result = classifier.classify(
            title="Epic Prank on My Friend!",
            description="This prank went viral! Watch his reaction"
        )
        
        assert result.category == PrimaryCategory.ENTERTAINMENT
        assert result.confidence > 0.2
    
    def test_classify_education_tutorial(self):
        """Test classification of educational/tutorial content."""
        classifier = CategoryClassifier()
        
        result = classifier.classify(
            title="How to Learn Python in 60 Seconds",
            description="Quick tutorial on Python programming basics",
            tags=['tutorial', 'education', 'howto']
        )
        
        assert result.category == PrimaryCategory.EDUCATION
        assert result.confidence > 0.3
        assert any('tutorial' in ind.lower() or 'how to' in ind.lower() for ind in result.indicators)
    
    def test_classify_education_facts(self):
        """Test classification of educational facts content."""
        classifier = CategoryClassifier()
        
        result = classifier.classify(
            title="Amazing Science Facts You Didn't Know",
            description="Did you know these facts about the universe?"
        )
        
        assert result.category == PrimaryCategory.EDUCATION
        assert result.confidence > 0.2
    
    def test_classify_lifestyle_vlog(self):
        """Test classification of lifestyle/vlog content."""
        classifier = CategoryClassifier()
        
        result = classifier.classify(
            title="Day in My Life as a Student",
            description="Follow my daily routine and lifestyle",
            tags=['vlog', 'daily life', 'lifestyle']
        )
        
        assert result.category == PrimaryCategory.LIFESTYLE
        assert result.confidence > 0.3
    
    def test_classify_lifestyle_grwm(self):
        """Test classification of Get Ready With Me content."""
        classifier = CategoryClassifier()
        
        result = classifier.classify(
            title="Get Ready With Me - Morning Routine",
            description="My morning makeup and outfit routine"
        )
        
        assert result.category == PrimaryCategory.LIFESTYLE
        assert result.confidence > 0.2
    
    def test_classify_gaming_gameplay(self):
        """Test classification of gaming content."""
        classifier = CategoryClassifier()
        
        result = classifier.classify(
            title="Fortnite Gameplay - Epic Victory Royale",
            description="Watch this amazing gaming montage and highlights",
            tags=['gaming', 'fortnite', 'gameplay']
        )
        
        assert result.category == PrimaryCategory.GAMING
        assert result.confidence > 0.3
    
    def test_classify_gaming_speedrun(self):
        """Test classification of speedrun content."""
        classifier = CategoryClassifier()
        
        result = classifier.classify(
            title="Minecraft Speedrun World Record",
            description="New speedrun record in Minecraft"
        )
        
        assert result.category == PrimaryCategory.GAMING
        assert result.confidence > 0.2
    
    def test_classify_challenges_trend(self):
        """Test classification of challenge/trend content."""
        classifier = CategoryClassifier()
        
        result = classifier.classify(
            title="Trying the Viral TikTok Challenge",
            description="This trending challenge is everywhere!",
            tags=['challenge', 'trending', 'viral']
        )
        
        assert result.category == PrimaryCategory.CHALLENGES_TRENDS
        assert result.confidence > 0.3
    
    def test_classify_reviews_unboxing(self):
        """Test classification of review/unboxing content."""
        classifier = CategoryClassifier()
        
        result = classifier.classify(
            title="iPhone 15 Unboxing and Review",
            description="My honest opinion and first impressions",
            tags=['review', 'unboxing', 'product review']
        )
        
        assert result.category == PrimaryCategory.REVIEWS_COMMENTARY
        assert result.confidence > 0.3
    
    def test_classify_reviews_commentary(self):
        """Test classification of commentary content."""
        classifier = CategoryClassifier()
        
        result = classifier.classify(
            title="My Thoughts on the New Movie",
            description="Commentary and analysis of the film"
        )
        
        assert result.category == PrimaryCategory.REVIEWS_COMMENTARY
        assert result.confidence > 0.2
    
    def test_classify_unusable_music(self):
        """Test classification of music content as unusable."""
        classifier = CategoryClassifier()
        
        result = classifier.classify(
            title="Cover of Popular Song",
            description="Singing my favorite music",
            tags=['music', 'cover', 'singing']
        )
        
        assert result.category == PrimaryCategory.UNUSABLE
        assert result.confidence > 0.2
    
    def test_classify_unusable_asmr(self):
        """Test classification of ASMR content as unusable."""
        classifier = CategoryClassifier()
        
        result = classifier.classify(
            title="ASMR Relaxation Video",
            description="Satisfying ASMR sounds for relaxation"
        )
        
        assert result.category == PrimaryCategory.UNUSABLE
        assert result.confidence > 0.2
    
    def test_classify_unusable_sports(self):
        """Test classification of sports content as unusable."""
        classifier = CategoryClassifier()
        
        result = classifier.classify(
            title="Best Football Goals Compilation",
            description="Amazing sports highlights from this season"
        )
        
        assert result.category == PrimaryCategory.UNUSABLE
        assert result.confidence > 0.2
    
    def test_classify_unusable_pets(self):
        """Test classification of pet content as unusable."""
        classifier = CategoryClassifier()
        
        result = classifier.classify(
            title="Cute Cat Videos Compilation",
            description="Adorable pet moments"
        )
        
        assert result.category == PrimaryCategory.UNUSABLE
        assert result.confidence > 0.1
    
    def test_classify_empty_content_defaults_to_unusable(self):
        """Test that empty content defaults to unusable."""
        classifier = CategoryClassifier()
        
        result = classifier.classify(
            title="",
            description=""
        )
        
        assert result.category == PrimaryCategory.UNUSABLE
        assert result.confidence == 0.5
        assert "no clear indicators" in result.indicators[0]
    
    def test_classify_from_metadata(self):
        """Test classification from metadata dictionary."""
        classifier = CategoryClassifier()
        
        metadata = {
            'title': 'My Story Time - True Experience',
            'description': 'Let me tell you about my crazy experience',
            'tags': ['story', 'true story'],
            'subtitle_text': 'So this happened to me last week'
        }
        
        result = classifier.classify_from_metadata(metadata)
        
        assert result.category == PrimaryCategory.STORYTELLING
        assert result.confidence > 0.3
    
    def test_category_result_structure(self):
        """Test CategoryResult namedtuple structure."""
        classifier = CategoryClassifier()
        
        result = classifier.classify(
            title="Test Video Title",
            description="Test description"
        )
        
        assert hasattr(result, 'category')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'indicators')
        assert hasattr(result, 'secondary_matches')
        assert isinstance(result.category, PrimaryCategory)
        assert isinstance(result.confidence, float)
        assert isinstance(result.indicators, list)
        assert isinstance(result.secondary_matches, dict)
    
    def test_confidence_range(self):
        """Test that confidence is always between 0 and 1."""
        classifier = CategoryClassifier()
        
        # Test with very strong indicators
        result = classifier.classify(
            title="AITA Story Time Tutorial Gaming Challenge Review",
            description="Story gaming tutorial challenge review unboxing",
            tags=['story', 'gaming', 'tutorial', 'challenge', 'review']
        )
        
        assert 0.0 <= result.confidence <= 1.0
    
    def test_secondary_matches(self):
        """Test that secondary matches are captured."""
        classifier = CategoryClassifier()
        
        # Content with mixed indicators
        result = classifier.classify(
            title="Gaming Story - My Experience",
            description="Story about my gaming experience"
        )
        
        # Should have storytelling as primary, but might have gaming as secondary
        assert result.category in [PrimaryCategory.STORYTELLING, PrimaryCategory.GAMING]
        # Secondary matches may or may not be present depending on threshold
        assert isinstance(result.secondary_matches, dict)
    
    def test_multiple_videos_batch(self):
        """Test classifying multiple videos."""
        classifier = CategoryClassifier()
        
        videos = [
            {'title': 'Story Time - AITA', 'description': 'My story', 'tags': ['story']},
            {'title': 'Funny Meme', 'description': 'Comedy video', 'tags': ['funny']},
            {'title': 'How to Code', 'description': 'Tutorial', 'tags': ['tutorial']},
            {'title': 'My Vlog', 'description': 'Daily life', 'tags': ['vlog']},
            {'title': 'Gaming Clip', 'description': 'Gameplay', 'tags': ['gaming']},
        ]
        
        results = [classifier.classify_from_metadata(v) for v in videos]
        
        assert len(results) == 5
        assert results[0].category == PrimaryCategory.STORYTELLING
        assert results[1].category == PrimaryCategory.ENTERTAINMENT
        assert results[2].category == PrimaryCategory.EDUCATION
        assert results[3].category == PrimaryCategory.LIFESTYLE
        assert results[4].category == PrimaryCategory.GAMING


class TestPrimaryCategory:
    """Test PrimaryCategory enum."""
    
    def test_category_enum_values(self):
        """Test that all categories exist."""
        assert PrimaryCategory.STORYTELLING
        assert PrimaryCategory.ENTERTAINMENT
        assert PrimaryCategory.EDUCATION
        assert PrimaryCategory.LIFESTYLE
        assert PrimaryCategory.GAMING
        assert PrimaryCategory.CHALLENGES_TRENDS
        assert PrimaryCategory.REVIEWS_COMMENTARY
        assert PrimaryCategory.UNUSABLE
    
    def test_is_usable_for_stories(self):
        """Test is_usable_for_stories property."""
        assert PrimaryCategory.STORYTELLING.is_usable_for_stories is True
        assert PrimaryCategory.ENTERTAINMENT.is_usable_for_stories is True
        assert PrimaryCategory.EDUCATION.is_usable_for_stories is True
        assert PrimaryCategory.LIFESTYLE.is_usable_for_stories is True
        assert PrimaryCategory.GAMING.is_usable_for_stories is True
        assert PrimaryCategory.CHALLENGES_TRENDS.is_usable_for_stories is True
        assert PrimaryCategory.REVIEWS_COMMENTARY.is_usable_for_stories is True
        assert PrimaryCategory.UNUSABLE.is_usable_for_stories is False
    
    def test_category_descriptions(self):
        """Test that all categories have descriptions."""
        for category in PrimaryCategory:
            assert category.description
            assert len(category.description) > 10
    
    def test_category_value_names(self):
        """Test category value names are correct."""
        assert PrimaryCategory.STORYTELLING.value == "Storytelling"
        assert PrimaryCategory.ENTERTAINMENT.value == "Entertainment"
        assert PrimaryCategory.EDUCATION.value == "Education / Informational"
        assert PrimaryCategory.LIFESTYLE.value == "Lifestyle / Vlog"
        assert PrimaryCategory.GAMING.value == "Gaming"
        assert PrimaryCategory.CHALLENGES_TRENDS.value == "Challenges & Trends"
        assert PrimaryCategory.REVIEWS_COMMENTARY.value == "Reviews & Commentary"
        assert PrimaryCategory.UNUSABLE.value == "Unusable"
