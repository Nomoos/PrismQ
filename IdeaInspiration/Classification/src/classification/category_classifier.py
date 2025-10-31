"""Primary category classifier for short-form vertical video content.

This classifier identifies the primary content category from 8 defined categories
optimized for short-form vertical video platforms (YouTube Shorts, TikTok, etc.).

The classifier uses weighted keyword analysis to categorize content and can
distinguish between content types that are usable vs. unusable for story generation.
"""

from typing import Dict, List, Optional
from .categories import PrimaryCategory, CategoryResult


class CategoryClassifier:
    """Classifies content into primary categories for short-form video."""
    
    # Keywords for each category with weights (higher = stronger indicator)
    CATEGORY_KEYWORDS = {
        PrimaryCategory.STORYTELLING: {
            # High confidence (weight 3)
            'story': 3, 'storytime': 3, 'narrative': 3, 'tale': 3,
            'aita': 3, 'am i the': 3, 'tifu': 3, 'confession': 3,
            'true story': 3, 'real story': 3, 'my story': 3,
            
            # Medium confidence (weight 2)
            'pov': 2, 'backstory': 2, 'experience': 2, 'happened to me': 2,
            'storytime': 2, 'let me tell you': 2, 'story time': 2,
            'creepypasta': 2, 'confessional': 2, 'relationship': 2,
            
            # Low confidence (weight 1)
            'drama': 1, 'betrayed': 1, 'revenge': 1, 'caught': 1,
        },
        
        PrimaryCategory.ENTERTAINMENT: {
            # High confidence
            'meme': 3, 'comedy': 3, 'funny': 3, 'prank': 3,
            'fail': 3, 'fails': 3, 'reaction': 3, 'roast': 3,
            
            # Medium confidence
            'hilarious': 2, 'laugh': 2, 'joke': 2, 'humor': 2,
            'parody': 2, 'skit': 2, 'vine': 2, 'memes': 2,
            'comedy skit': 2, 'funny moment': 2,
            
            # Low confidence
            'entertaining': 1, 'fun': 1, 'amusing': 1,
        },
        
        PrimaryCategory.EDUCATION: {
            # High confidence
            'tutorial': 3, 'how to': 3, 'explained': 3, 'learn': 3,
            'education': 3, 'lesson': 3, 'guide': 3, 'teaching': 3,
            
            # Medium confidence
            'tips': 2, 'tricks': 2, 'hack': 2, 'facts': 2,
            'did you know': 2, 'science': 2, 'history': 2, 'math': 2,
            'explainer': 2, 'informational': 2, 'productivity': 2,
            
            # Low confidence
            'info': 1, 'fact': 1, 'knowledge': 1,
        },
        
        PrimaryCategory.LIFESTYLE: {
            # High confidence
            'vlog': 3, 'daily life': 3, 'day in my life': 3, 'routine': 3,
            'get ready with me': 3, 'grwm': 3,
            
            # Medium confidence
            'beauty': 2, 'makeup': 2, 'fashion': 2, 'outfit': 2,
            'fitness': 2, 'workout': 2, 'recipe': 2, 'cooking': 2,
            'travel': 2, 'lifestyle': 2, 'skincare': 2, 'haul': 2,
            
            # Low confidence
            'food': 1, 'style': 1, 'wellness': 1,
        },
        
        PrimaryCategory.GAMING: {
            # High confidence
            'gameplay': 3, 'gaming': 3, 'game': 3, 'playthrough': 3,
            'speedrun': 3, 'lets play': 3,
            
            # Medium confidence
            'highlight': 2, 'clutch': 2, 'montage': 2, 'walkthrough': 2,
            'boss fight': 2, 'gaming clip': 2, 'stream highlight': 2,
            'fortnite': 2, 'minecraft': 2, 'valorant': 2, 'cod': 2,
            
            # Low confidence
            'gamer': 1, 'game clip': 1, 'win': 1,
        },
        
        PrimaryCategory.CHALLENGES_TRENDS: {
            # High confidence
            'challenge': 3, 'trend': 3, 'trending': 3, 'viral': 3,
            'tiktok trend': 3, 'challenge accepted': 3,
            
            # Medium confidence
            'dance challenge': 2, 'ar effect': 2, 'filter': 2,
            'duet': 2, 'trending sound': 2, 'viral trend': 2,
            'tiktok challenge': 2,
            
            # Low confidence
            'popular': 1, 'latest trend': 1,
        },
        
        PrimaryCategory.REVIEWS_COMMENTARY: {
            # High confidence
            'review': 3, 'unboxing': 3, 'opinion': 3, 'commentary': 3,
            'reaction video': 3, 'product review': 3,
            
            # Medium confidence
            'thoughts on': 2, 'my take': 2, 'analysis': 2, 'critique': 2,
            'rating': 2, 'first impression': 2, 'worth it': 2,
            
            # Low confidence
            'discuss': 1, 'opinion on': 1,
        },
        
        PrimaryCategory.UNUSABLE: {
            # Music & Performance
            'music': 2, 'song': 2, 'cover': 2, 'singing': 2, 'dance': 2,
            'lip sync': 2, 'performance': 2, 'music video': 2,
            
            # ASMR
            'asmr': 3, 'relaxation': 2, 'satisfying': 2, 'slime': 2,
            
            # Promotional
            'sponsored': 3, 'ad': 2, 'advertisement': 2, 'promo': 2,
            'brand': 1, 'collab': 1,
            
            # Pets & Animals
            'pet': 2, 'dog': 1, 'cat': 1, 'animal': 2, 'cute pet': 2,
            
            # Sports
            'sports': 2, 'goal': 1, 'match': 1, 'football': 1, 'basketball': 1,
            'soccer': 1, 'training': 1,
            
            # News & Current Events
            'breaking news': 3, 'news': 2, 'politics': 2, 'election': 2,
            'current events': 2,
        },
    }
    
    def __init__(self):
        """Initialize the category classifier."""
        pass
    
    def classify(
        self,
        title: str,
        description: str = "",
        tags: Optional[List[str]] = None,
        subtitle_text: str = ""
    ) -> CategoryResult:
        """Classify content into a primary category.
        
        Args:
            title: Content title
            description: Content description
            tags: List of tags/hashtags
            subtitle_text: Subtitle/caption text
        
        Returns:
            CategoryResult with primary category, confidence, and indicators
        """
        tags = tags or []
        
        # Calculate scores for each category
        category_scores: Dict[PrimaryCategory, float] = {}
        category_indicators: Dict[PrimaryCategory, List[str]] = {
            cat: [] for cat in PrimaryCategory
        }
        
        # Combine all text for analysis
        title_lower = title.lower()
        desc_lower = description.lower()
        tags_lower = [tag.lower() for tag in tags]
        subtitle_lower = subtitle_text.lower()[:500]  # First 500 chars
        
        # Score each category
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = 0.0
            
            # Check title (highest weight)
            for keyword, weight in keywords.items():
                if keyword in title_lower:
                    score += weight * 1.5  # Title gets 1.5x multiplier
                    category_indicators[category].append(f"title: {keyword}")
            
            # Check description
            for keyword, weight in keywords.items():
                if keyword in desc_lower:
                    score += weight * 1.0
                    category_indicators[category].append(f"description: {keyword}")
            
            # Check tags
            for tag in tags_lower:
                for keyword, weight in keywords.items():
                    if keyword in tag:
                        score += weight * 1.2  # Tags get 1.2x multiplier
                        category_indicators[category].append(f"tag: {keyword}")
            
            # Check subtitles
            for keyword, weight in keywords.items():
                if keyword in subtitle_lower:
                    score += weight * 0.8  # Subtitles get 0.8x multiplier
                    category_indicators[category].append(f"subtitle: {keyword}")
            
            category_scores[category] = score
        
        # Find the category with highest score
        if not category_scores or max(category_scores.values()) == 0:
            # No matches found - default to Unusable
            return CategoryResult(
                category=PrimaryCategory.UNUSABLE,
                confidence=0.5,
                indicators=["no clear indicators found"],
                secondary_matches={}
            )
        
        # Get primary category (highest score)
        primary_category = max(category_scores, key=category_scores.get)
        primary_score = category_scores[primary_category]
        
        # Calculate confidence (normalize to 0-1 range)
        # Confidence is based on score relative to maximum possible score
        max_possible_score = 20.0  # Reasonable upper bound
        confidence = min(primary_score / max_possible_score, 1.0)
        
        # Get secondary matches (other categories with significant scores)
        secondary_matches = {
            cat: score
            for cat, score in category_scores.items()
            if cat != primary_category and score >= 2.0
        }
        
        return CategoryResult(
            category=primary_category,
            confidence=confidence,
            indicators=category_indicators[primary_category][:5],  # Top 5 indicators
            secondary_matches=secondary_matches
        )
    
    def classify_from_metadata(self, metadata: Dict) -> CategoryResult:
        """Classify content from metadata dictionary.
        
        Args:
            metadata: Dictionary with 'title', 'description', 'tags', 'subtitle_text' keys
        
        Returns:
            CategoryResult with primary category and confidence
        """
        return self.classify(
            title=metadata.get('title', ''),
            description=metadata.get('description', ''),
            tags=metadata.get('tags', []),
            subtitle_text=metadata.get('subtitle_text', '')
        )
