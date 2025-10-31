"""Community signal processor for transforming raw data to unified format."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .sentiment_analyzer import SentimentAnalyzer


class CommunityProcessor:
    """Processes community signals into unified format.
    
    Follows Single Responsibility Principle by focusing on data transformation.
    Depends on SentimentAnalyzer abstraction (Dependency Inversion Principle).
    """
    
    def __init__(self, sentiment_analyzer: Optional[SentimentAnalyzer] = None):
        """Initialize community processor.
        
        Args:
            sentiment_analyzer: Sentiment analyzer instance (injected dependency)
        """
        self.sentiment_analyzer = sentiment_analyzer or SentimentAnalyzer()
    
    def process_comment(
        self,
        text: str,
        author: str,
        source: str,
        source_id: str,
        platform: str,
        parent_content: Optional[str] = None,
        upvotes: int = 0,
        replies: int = 0,
        timestamp: Optional[datetime] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a comment into unified community signal format.
        
        Args:
            text: Comment text
            author: Comment author username
            source: Source name (e.g., 'user_feedback')
            source_id: Unique identifier for the comment
            platform: Platform name (e.g., 'youtube', 'instagram')
            parent_content: ID of parent content (video, post, etc.)
            upvotes: Number of upvotes/likes
            replies: Number of replies
            timestamp: When the comment was posted
            category: Content category
            
        Returns:
            Unified community signal dictionary
        """
        # Analyze sentiment
        sentiment_result = self.sentiment_analyzer.analyze(text)
        
        # Extract topics (simple keyword extraction)
        topics = self._extract_topics(text)
        
        # Detect intent
        intent = self._detect_intent(text)
        
        # Calculate universal metrics
        engagement_score = self._calculate_engagement_score(upvotes, replies)
        relevance_score = self._calculate_relevance_score(sentiment_result, topics)
        actionability = self._calculate_actionability(intent, text)
        
        return {
            'source': source,
            'source_id': source_id,
            'content': {
                'type': 'comment',
                'text': text,
                'title': None,  # Comments don't have titles
                'author': author
            },
            'context': {
                'platform': platform,
                'parent_content': parent_content,
                'category': category,
                'timestamp': timestamp.isoformat() if timestamp else None
            },
            'metrics': {
                'upvotes': upvotes,
                'replies': replies,
                'reactions': {}  # Platform-specific reactions can be added
            },
            'analysis': {
                'sentiment': sentiment_result['sentiment'],
                'sentiment_score': sentiment_result['sentiment_score'],
                'topics': topics,
                'intent': intent
            },
            'universal_metrics': {
                'engagement_score': engagement_score,
                'relevance_score': relevance_score,
                'actionability': actionability
            }
        }
    
    def process_question(
        self,
        text: str,
        title: str,
        author: str,
        source: str,
        source_id: str,
        platform: str,
        upvotes: int = 0,
        answers: int = 0,
        views: int = 0,
        timestamp: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a question into unified community signal format.
        
        Args:
            text: Question body text
            title: Question title
            author: Question author username
            source: Source name (e.g., 'qa')
            source_id: Unique identifier for the question
            platform: Platform name (e.g., 'stackoverflow', 'quora')
            upvotes: Number of upvotes
            answers: Number of answers
            views: Number of views
            timestamp: When the question was posted
            tags: Question tags
            category: Content category
            
        Returns:
            Unified community signal dictionary
        """
        # Analyze sentiment
        sentiment_result = self.sentiment_analyzer.analyze(text)
        
        # Extract topics (use tags if available, otherwise extract from text)
        topics = tags if tags else self._extract_topics(f"{title} {text}")
        
        # Calculate universal metrics
        engagement_score = self._calculate_engagement_score(upvotes, answers, views)
        relevance_score = self._calculate_relevance_score(sentiment_result, topics)
        actionability = self._calculate_actionability('question', text)
        
        return {
            'source': source,
            'source_id': source_id,
            'content': {
                'type': 'question',
                'text': text,
                'title': title,
                'author': author
            },
            'context': {
                'platform': platform,
                'parent_content': None,
                'category': category,
                'timestamp': timestamp.isoformat() if timestamp else None
            },
            'metrics': {
                'upvotes': upvotes,
                'replies': answers,
                'reactions': {'views': views}
            },
            'analysis': {
                'sentiment': sentiment_result['sentiment'],
                'sentiment_score': sentiment_result['sentiment_score'],
                'topics': topics,
                'intent': 'question'
            },
            'universal_metrics': {
                'engagement_score': engagement_score,
                'relevance_score': relevance_score,
                'actionability': actionability
            }
        }
    
    def _extract_topics(self, text: str, max_topics: int = 5) -> List[str]:
        """Extract topics from text using simple keyword extraction.
        
        Args:
            text: Text to extract topics from
            max_topics: Maximum number of topics to return
            
        Returns:
            List of topic keywords
        """
        # Simple implementation - extract common content-related keywords
        # In production, this would use more sophisticated NLP (spaCy, NLTK, etc.)
        
        # Common stop words to ignore
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
            'can', 'could', 'may', 'might', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        # Split and clean words
        words = text.lower().split()
        words = [w.strip('.,!?;:()[]{}"\'-') for w in words]
        
        # Filter out stop words and short words
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Count frequency
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        topics = [word for word, freq in top_keywords[:max_topics]]
        
        return topics
    
    def _detect_intent(self, text: str) -> str:
        """Detect the intent of the text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Intent label: 'question', 'suggestion', 'complaint', 'praise'
        """
        text_lower = text.lower()
        
        # Question indicators
        if any(word in text_lower for word in ['?', 'how', 'what', 'why', 'when', 'where', 'who']):
            return 'question'
        
        # Suggestion indicators
        if any(word in text_lower for word in ['should', 'could', 'would like', 'suggest', 'recommend', 'idea']):
            return 'suggestion'
        
        # Complaint indicators
        if any(word in text_lower for word in ['bad', 'terrible', 'awful', 'problem', 'issue', 'broken', 'fix']):
            return 'complaint'
        
        # Praise indicators
        if any(word in text_lower for word in ['great', 'awesome', 'love', 'amazing', 'excellent', 'thank']):
            return 'praise'
        
        # Default to general feedback
        return 'feedback'
    
    def _calculate_engagement_score(
        self,
        upvotes: int = 0,
        replies: int = 0,
        views: int = 0
    ) -> float:
        """Calculate engagement score from metrics.
        
        Args:
            upvotes: Number of upvotes
            replies: Number of replies
            views: Number of views
            
        Returns:
            Engagement score (0-10)
        """
        # Weighted sum of engagement metrics
        # Normalize to 0-10 scale
        score = (upvotes * 2 + replies * 1.5 + views * 0.01)
        return min(score / 10, 10.0)
    
    def _calculate_relevance_score(
        self,
        sentiment_result: Dict[str, Any],
        topics: List[str]
    ) -> float:
        """Calculate relevance score based on sentiment and topics.
        
        Args:
            sentiment_result: Sentiment analysis result
            topics: Extracted topics
            
        Returns:
            Relevance score (0-10)
        """
        # Base score from number of topics
        topic_score = min(len(topics) * 2, 6)
        
        # Boost for confident sentiment
        sentiment_boost = sentiment_result.get('confidence', 0) * 4
        
        return min(topic_score + sentiment_boost, 10.0)
    
    def _calculate_actionability(self, intent: str, text: str) -> float:
        """Calculate how actionable the content is for content creation.
        
        Args:
            intent: Detected intent
            text: Original text
            
        Returns:
            Actionability score (0-10)
        """
        # Questions and suggestions are more actionable
        intent_scores = {
            'question': 8.0,
            'suggestion': 9.0,
            'complaint': 6.0,
            'praise': 4.0,
            'feedback': 5.0
        }
        
        base_score = intent_scores.get(intent, 5.0)
        
        # Longer, more detailed content is more actionable
        length_bonus = min(len(text) / 100, 2.0)
        
        return min(base_score + length_bonus, 10.0)
