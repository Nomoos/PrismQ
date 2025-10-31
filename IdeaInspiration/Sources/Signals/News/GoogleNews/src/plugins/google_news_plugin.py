"""GoogleNews plugin for scraping news signals."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import time
from . import SignalPlugin


class GoogleNewsPlugin(SignalPlugin):
    """Plugin for scraping news signals from Google News."""
    
    def __init__(self, config):
        """Initialize Google News plugin."""
        super().__init__(config)
        self.api = None
        self._initialize_api()
    
    def _initialize_api(self):
        """Initialize Google News API client."""
        try:
            # Import gnews here to avoid import errors if not installed
            from gnews import GNews
            
            # Initialize GNews with language and region from config
            language = getattr(self.config, 'language', 'en')
            country = getattr(self.config, 'google_news_region', 'US')
            
            # Extract just the language code (e.g., 'en' from 'en-US')
            lang_code = language.split('-')[0] if '-' in language else language
            
            self.api = GNews(
                language=lang_code,
                country=country,
                max_results=10
            )
            print(f"Google News API initialized successfully (language={lang_code}, country={country})")
        except ImportError:
            print("Warning: gnews not installed. Install with: pip install gnews")
            print("Running in stub mode - will return sample data")
            self.api = None
        except Exception as e:
            print(f"Warning: Could not initialize Google News API: {e}")
            print("Running in stub mode - will return sample data")
            self.api = None
    
    def get_source_name(self) -> str:
        """Get the name of this source."""
        return "google_news"
    
    def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Scrape news signals from Google News.
        
        Args:
            **kwargs: Additional parameters
                - limit: Maximum number of news items to fetch (default: from config)
                - topic: Specific topic to search for (optional)
                - keywords: Keywords to search for (optional)
        
        Returns:
            List of signal dictionaries
        """
        signals = []
        
        # Get configuration with fallbacks
        max_results = getattr(self.config, 'max_results', None) or \
                     getattr(self.config, 'google_news_max_results', 25)
        limit = kwargs.get('limit', max_results)
        topic = kwargs.get('topic', None)
        keywords = kwargs.get('keywords', None)
        
        try:
            if self.api is None:
                # Stub mode: return sample data for testing
                print("Running in stub mode - returning sample news data")
                signals = self._get_sample_news(limit)
            else:
                # Real implementation with gnews
                if keywords:
                    # Search for specific keywords
                    signals = self._search_news(keywords, limit)
                elif topic:
                    # Get news for specific topic
                    signals = self._get_topic_news(topic, limit)
                else:
                    # Get top headlines
                    signals = self._get_top_news(limit)
            
            print(f"Successfully scraped {len(signals)} news signals from Google News")
            
        except Exception as e:
            print(f"Error scraping Google News: {e}")
            import traceback
            traceback.print_exc()
        
        return signals
    
    def _get_top_news(self, limit: int) -> List[Dict[str, Any]]:
        """
        Fetch top news headlines.
        
        Args:
            limit: Maximum number of articles
        
        Returns:
            List of signal dictionaries
        """
        signals = []
        
        try:
            print("Fetching top news headlines from Google News...")
            news_items = self.api.get_top_news()
            
            for item in news_items[:limit]:
                signal = self._create_signal(item)
                if signal:
                    signals.append(signal)
                    
        except Exception as e:
            print(f"Error fetching top news: {e}")
        
        return signals
    
    def _search_news(self, keywords: str, limit: int) -> List[Dict[str, Any]]:
        """
        Search for news by keywords.
        
        Args:
            keywords: Search keywords
            limit: Maximum number of articles
        
        Returns:
            List of signal dictionaries
        """
        signals = []
        
        try:
            print(f"Searching Google News for: {keywords}")
            news_items = self.api.get_news(keywords)
            
            for item in news_items[:limit]:
                signal = self._create_signal(item, keywords=keywords)
                if signal:
                    signals.append(signal)
                    
        except Exception as e:
            print(f"Error searching news for '{keywords}': {e}")
        
        return signals
    
    def _get_topic_news(self, topic: str, limit: int) -> List[Dict[str, Any]]:
        """
        Get news for a specific topic.
        
        Args:
            topic: News topic
            limit: Maximum number of articles
        
        Returns:
            List of signal dictionaries
        """
        signals = []
        
        try:
            print(f"Fetching news for topic: {topic}")
            # Use search for topics
            news_items = self.api.get_news(topic)
            
            for item in news_items[:limit]:
                signal = self._create_signal(item, topic=topic)
                if signal:
                    signals.append(signal)
                    
        except Exception as e:
            print(f"Error fetching topic news for '{topic}': {e}")
        
        return signals
    
    def _get_sample_news(self, limit: int) -> List[Dict[str, Any]]:
        """
        Get sample news data for testing/stub mode.
        
        Args:
            limit: Number of sample articles to generate
        
        Returns:
            List of sample signal dictionaries
        """
        sample_news = [
            {
                'title': 'Tech Giants Announce Major AI Breakthrough',
                'description': 'Leading technology companies unveil new artificial intelligence capabilities that could transform industries.',
                'publisher': 'Tech News Daily',
                'url': 'https://example.com/ai-breakthrough',
                'published_date': datetime.now(timezone.utc).isoformat() + 'Z'
            },
            {
                'title': 'Global Markets React to Economic Data',
                'description': 'Stock markets worldwide show mixed reactions following latest economic indicators release.',
                'publisher': 'Financial Times',
                'url': 'https://example.com/markets',
                'published_date': datetime.now(timezone.utc).isoformat() + 'Z'
            },
            {
                'title': 'Climate Summit Reaches Historic Agreement',
                'description': 'World leaders commit to ambitious new targets for reducing carbon emissions.',
                'publisher': 'Global News',
                'url': 'https://example.com/climate',
                'published_date': datetime.now(timezone.utc).isoformat() + 'Z'
            },
            {
                'title': 'New Study Reveals Health Benefits of Exercise',
                'description': 'Research shows regular physical activity has more benefits than previously thought.',
                'publisher': 'Health Today',
                'url': 'https://example.com/health',
                'published_date': datetime.now(timezone.utc).isoformat() + 'Z'
            },
            {
                'title': 'Space Agency Announces New Mission',
                'description': 'Next-generation spacecraft to explore distant planets in ambitious new program.',
                'publisher': 'Space News',
                'url': 'https://example.com/space',
                'published_date': datetime.now(timezone.utc).isoformat() + 'Z'
            },
            {
                'title': 'Education Reform Bill Passes Legislature',
                'description': 'Major changes to education system approved after months of debate.',
                'publisher': 'Education Weekly',
                'url': 'https://example.com/education',
                'published_date': datetime.now(timezone.utc).isoformat() + 'Z'
            },
            {
                'title': 'Sports Team Wins Championship',
                'description': 'Underdog team clinches title in dramatic final game.',
                'publisher': 'Sports Daily',
                'url': 'https://example.com/sports',
                'published_date': datetime.now(timezone.utc).isoformat() + 'Z'
            },
            {
                'title': 'Entertainment Awards Show Highlights',
                'description': 'Surprising winners and memorable moments from annual awards ceremony.',
                'publisher': 'Entertainment News',
                'url': 'https://example.com/entertainment',
                'published_date': datetime.now(timezone.utc).isoformat() + 'Z'
            },
        ]
        
        signals = []
        for news_data in sample_news[:limit]:
            signal = self._create_signal(news_data)
            signals.append(signal)
        
        return signals
    
    def _create_signal(self, news_item: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Create a signal dictionary from news item data.
        
        Args:
            news_item: Raw news data from Google News or sample
            **kwargs: Additional context (keywords, topic)
        
        Returns:
            Signal dictionary in unified format
        """
        # Extract data with fallbacks for different possible field names
        title = news_item.get('title', 'Unknown')
        description = news_item.get('description', news_item.get('summary', ''))
        publisher = news_item.get('publisher', news_item.get('source', 'Unknown'))
        url = news_item.get('url', news_item.get('link', ''))
        
        # Handle published date
        published_date = news_item.get('published_date', news_item.get('published date', None))
        if not published_date:
            published_date = datetime.now(timezone.utc).isoformat() + 'Z'
        elif not isinstance(published_date, str):
            published_date = str(published_date)
        
        # Generate unique source_id
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H')
        # Use first few words of title for ID
        title_slug = ''.join(c if c.isalnum() else '_' for c in title.lower())[:30]
        source_id = f"{title_slug}_{timestamp}"
        
        # Calculate signal strength based on title/description length and freshness
        signal_strength = self._calculate_signal_strength(title, description)
        
        # Determine tags
        tags = ['google_news', 'news']
        if kwargs.get('keywords'):
            tags.append('search')
        if kwargs.get('topic'):
            tags.append(kwargs['topic'])
        
        # Extract publisher object if it's a dict
        if isinstance(publisher, dict):
            publisher_name = publisher.get('title', publisher.get('name', 'Unknown'))
        else:
            publisher_name = str(publisher)
        
        return {
            'source_id': source_id,
            'signal_type': 'news',
            'name': title,
            'description': description[:500] if description else '',  # Truncate long descriptions
            'tags': tags,
            'metrics': {
                'volume': 100,  # Base volume for news signals
                'velocity': 0.0,  # Would need historical data
                'acceleration': 0.0,  # Would need historical data
                'geographic_spread': ['global']
            },
            'temporal': {
                'first_seen': published_date,
                'peak_time': None,
                'current_status': 'active'
            },
            'extra': {
                'platform': 'google_news',
                'publisher': publisher_name,
                'url': url,
                'keywords': kwargs.get('keywords'),
                'topic': kwargs.get('topic')
            }
        }
    
    def _calculate_signal_strength(self, title: str, description: str) -> float:
        """
        Calculate signal strength based on content.
        
        Args:
            title: Article title
            description: Article description
        
        Returns:
            Signal strength (0-10)
        """
        # Simple heuristic: longer, more detailed articles = higher strength
        title_len = len(title) if title else 0
        desc_len = len(description) if description else 0
        
        # Normalize to 0-10 scale
        strength = min(10.0, (title_len + desc_len) / 50)
        
        return round(strength, 2)
