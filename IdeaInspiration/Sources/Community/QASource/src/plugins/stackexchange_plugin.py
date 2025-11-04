"""StackExchange plugin for scraping Q&A platforms."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
import time
from . import CommunitySourcePlugin, IdeaInspiration


class StackExchangePlugin(CommunitySourcePlugin):
    """Plugin for scraping questions from StackExchange sites.
    
    Uses StackExchange API v2.3 to fetch questions based on tags.
    """
    
    API_BASE_URL = "https://api.stackexchange.com/2.3"
    
    def __init__(self, config):
        """Initialize StackExchange plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        self.api_key = config.stackexchange_key
        self.sites = config.stackexchange_sites
        self.filter_tags = config.filter_tags
    
    def get_source_name(self) -> str:
        """Get the name of this source."""
        return "qa"
    
    def scrape(
        self,
        sites: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        max_questions: Optional[int] = None
    ) -> List[IdeaInspiration]:
        """Scrape questions from StackExchange sites.
        
        Args:
            sites: List of StackExchange sites (uses config if not provided)
            tags: List of tags to filter by (uses config if not provided)
            max_questions: Maximum questions to fetch (uses config if not provided)
            
        Returns:
            List of IdeaInspiration objects
        """
        # Use config values if not provided
        if sites is None:
            sites = self.sites
        if tags is None:
            tags = self.filter_tags
        if max_questions is None:
            max_questions = self.config.max_questions
        
        signals = []
        
        for site in sites:
            print(f"Fetching questions from {site}...")
            
            questions = self._fetch_questions(
                site=site,
                tags=tags,
                max_results=max_questions
            )
            
            signals.extend(questions)
            print(f"  Found {len(questions)} questions")
            
            # Respect API rate limits
            time.sleep(0.1)
        
        return signals
    
    def _fetch_questions(
        self,
        site: str,
        tags: List[str],
        max_results: int
    ) -> List[IdeaInspiration]:
        """Fetch questions from a StackExchange site.
        
        Args:
            site: Site name (e.g., 'stackoverflow')
            tags: Tags to filter by
            max_results: Maximum results to fetch
            
        Returns:
            List of IdeaInspiration objects
        """
        questions = []
        
        try:
            # Build query parameters
            params = {
                'site': site,
                'order': 'desc',
                'sort': 'activity',
                'pagesize': min(max_results, 100),  # API max is 100
                'tagged': ';'.join(tags),
                'filter': 'withbody'  # Include question body
            }
            
            if self.api_key:
                params['key'] = self.api_key
            
            # Make API request
            response = requests.get(
                f"{self.API_BASE_URL}/questions",
                params=params,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            for item in data.get('items', []):
                # Parse timestamp - handle invalid timestamps
                timestamp_unix = item.get('creation_date', 0)
                if timestamp_unix > 0:
                    timestamp = datetime.fromtimestamp(timestamp_unix).isoformat() + 'Z'
                else:
                    timestamp = ''  # Empty string for invalid/missing timestamps
                
                author = item.get('owner', {}).get('display_name', 'Unknown')
                question_tags = self.format_tags(item.get('tags', []) + ['qa', site, 'technology'])
                
                # Build metadata with string values
                metadata = {
                    'question_id': str(item.get('question_id', '')),
                    'site': site,
                    'score': str(item.get('score', 0)),
                    'answer_count': str(item.get('answer_count', 0)),
                    'view_count': str(item.get('view_count', 0)),
                    'is_answered': str(item.get('is_answered', False)),
                    'accepted_answer_id': str(item.get('accepted_answer_id', '')),
                }
                
                # Create IdeaInspiration using from_text factory method
                idea = IdeaInspiration.from_text(
                    title=item.get('title', ''),
                    description=f"Question from {site}",
                    text_content=item.get('body', ''),
                    keywords=question_tags,
                    metadata=metadata,
                    source_id=str(item.get('question_id', '')),
                    source_url=item.get('link', ''),
                    source_platform="qa_source",
                    source_created_by=author,
                    source_created_at=timestamp
                )
                
                questions.append(idea)
            
            # Check quota
            if 'quota_remaining' in data:
                print(f"  API quota remaining: {data['quota_remaining']}")
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching questions from {site}: {e}")
        
        return questions
