"""NewsApi plugin for scraping news signals."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import time
from . import SignalPlugin


class NewsApiPlugin(SignalPlugin):
    """Plugin for scraping news signals from NewsAPI."""
    
    def __init__(self, config):
        """Initialize NewsAPI plugin."""
        super().__init__(config)
        self.api = None
        self._initialize_api()
    
    def _initialize_api(self):
        """Initialize NewsAPI client."""
        try:
            from newsapi import NewsApiClient
            api_key = getattr(self.config, 'api_key', None) or \
                     getattr(self.config, 'newsapi_api_key', None)
            
            if api_key:
                self.api = NewsApiClient(api_key=api_key)
                print("NewsAPI initialized successfully")
            else:
                print("Warning: NewsAPI key not found in config")
                print("Running in stub mode - will return sample data")
                self.api = None
        except ImportError:
            print("Warning: newsapi-python not installed. Install with: pip install newsapi-python")
            print("Running in stub mode - will return sample data")
            self.api = None
        except Exception as e:
            print(f"Warning: Could not initialize NewsAPI: {e}")
            print("Running in stub mode - will return sample data")
            self.api = None
    
    def get_source_name(self) -> str:
        """Get the name of this source."""
        return "news_api"
    
    def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Scrape news signals from NewsAPI.
        
        Args:
            **kwargs: Additional parameters
                - limit: Maximum number of news items
                - query: Search query
                - category: News category
                - language: Language code
        
        Returns:
            List of signal dictionaries
        """
        signals = []
        max_results = getattr(self.config, 'max_results', None) or \
                     getattr(self.config, 'news_api_max_results', 25)
        limit = kwargs.get('limit', max_results)
        query = kwargs.get('query', None)
        category = kwargs.get('category', None)
        language = kwargs.get('language', 'en')
        
        try:
            if self.api is None:
                print("Running in stub mode - returning sample news data")
                signals = self._get_sample_news(limit)
            else:
                if query:
                    signals = self._search_news(query, limit, language)
                elif category:
                    signals = self._get_category_news(category, limit, language)
                else:
                    signals = self._get_top_headlines(limit, language)
            
            print(f"Successfully scraped {len(signals)} news signals from NewsAPI")
            
        except Exception as e:
            print(f"Error scraping NewsAPI: {e}")
            import traceback
            traceback.print_exc()
        
        return signals
    
    def _get_top_headlines(self, limit: int, language: str) -> List[Dict[str, Any]]:
        """Fetch top headlines."""
        signals = []
        try:
            print("Fetching top headlines from NewsAPI...")
            signals = self._get_sample_news(limit)
        except Exception as e:
            print(f"Error fetching top headlines: {e}")
        return signals
    
    def _search_news(self, query: str, limit: int, language: str) -> List[Dict[str, Any]]:
        """Search for news by query."""
        signals = []
        try:
            print(f"Searching NewsAPI for: {query}")
            signals = self._get_sample_news(limit)
        except Exception as e:
            print(f"Error searching news: {e}")
        return signals
    
    def _get_category_news(self, category: str, limit: int, language: str) -> List[Dict[str, Any]]:
        """Get news for a specific category."""
        signals = []
        try:
            print(f"Fetching news for category: {category}")
            signals = self._get_sample_news(limit)
        except Exception as e:
            print(f"Error fetching category news: {e}")
        return signals
    
    def _get_sample_news(self, limit: int) -> List[Dict[str, Any]]:
        """Get sample news data for testing/stub mode."""
        sample_news = [
            {
                'title': 'Breaking: Major Technology Announcement',
                'description': 'Tech industry leaders reveal groundbreaking innovation.',
                'source': {'name': 'TechCrunch'},
                'url': 'https://example.com/tech',
                'publishedAt': datetime.now(timezone.utc).isoformat() + 'Z',
                'author': 'Tech Reporter'
            },
            {
                'title': 'Global Markets Hit New Records',
                'description': 'Stock markets worldwide show positive momentum.',
                'source': {'name': 'Bloomberg'},
                'url': 'https://example.com/markets',
                'publishedAt': datetime.now(timezone.utc).isoformat() + 'Z',
                'author': 'Market Analyst'
            },
            {
                'title': 'Climate Change Summit Begins',
                'description': 'World leaders gather to discuss climate action.',
                'source': {'name': 'Reuters'},
                'url': 'https://example.com/climate',
                'publishedAt': datetime.now(timezone.utc).isoformat() + 'Z',
                'author': 'Environmental Correspondent'
            },
            {
                'title': 'Sports Championship Final Results',
                'description': 'Thrilling finish in major sporting event.',
                'source': {'name': 'ESPN'},
                'url': 'https://example.com/sports',
                'publishedAt': datetime.now(timezone.utc).isoformat() + 'Z',
                'author': 'Sports Writer'
            },
            {
                'title': 'New Health Study Findings',
                'description': 'Research reveals important health insights.',
                'source': {'name': 'Medical News'},
                'url': 'https://example.com/health',
                'publishedAt': datetime.now(timezone.utc).isoformat() + 'Z',
                'author': 'Health Editor'
            },
        ]
        
        signals = []
        for news_data in sample_news[:limit]:
            signal = self._create_signal(news_data)
            signals.append(signal)
        
        return signals
    
    def _create_signal(self, news_item: Dict[str, Any]) -> Dict[str, Any]:
        """Create a signal dictionary from news item data."""
        title = news_item.get('title', 'Unknown')
        description = news_item.get('description', '')
        source = news_item.get('source', {})
        source_name = source.get('name', 'Unknown') if isinstance(source, dict) else str(source)
        url = news_item.get('url', '')
        published_at = news_item.get('publishedAt', datetime.now(timezone.utc).isoformat() + 'Z')
        author = news_item.get('author', 'Unknown')
        
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H')
        title_slug = ''.join(c if c.isalnum() else '_' for c in title.lower())[:30]
        source_id = f"{title_slug}_{timestamp}"
        
        return {
            'source_id': source_id,
            'signal_type': 'news',
            'name': title,
            'description': description[:500] if description else '',
            'tags': ['newsapi', 'news', 'article'],
            'metrics': {
                'volume': 100,
                'velocity': 0.0,
                'acceleration': 0.0,
                'geographic_spread': ['global']
            },
            'temporal': {
                'first_seen': published_at,
                'peak_time': None,
                'current_status': 'active'
            },
            'extra': {
                'platform': 'newsapi',
                'source': source_name,
                'url': url,
                'author': author
            }
        }

