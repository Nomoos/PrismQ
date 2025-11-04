"""HackerNews Type-based plugin for scraping Ask HN and Show HN posts."""

import requests
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
from . import SourcePlugin, IdeaInspiration


class HNTypePlugin(SourcePlugin):
    """Plugin for scraping type-specific posts (Ask HN, Show HN) from HackerNews.
    
    Uses HackerNews official Firebase API with filtering.
    Follows Open/Closed Principle (OCP) - open for extension, closed for modification.
    """
    
    def __init__(self, config):
        """Initialize HackerNews type-based plugin.
        
        Args:
            config: Configuration object with HN API settings
        """
        super().__init__(config)
        self.api_base_url = config.hn_api_base_url
        self.timeout = config.hn_request_timeout
    
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "hackernews_type"
    
    def _fetch_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a single item from HackerNews API.
        
        Args:
            item_id: HackerNews item ID
            
        Returns:
            Item data dictionary or None if request fails
        """
        try:
            url = f"{self.api_base_url}/item/{item_id}.json"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"  ✗ Failed to fetch item {item_id}: {e}")
            return None
    
    def _item_to_idea(self, item: Dict[str, Any], filter_type: str) -> Optional[Dict[str, Any]]:
        """Convert HackerNews item to idea format.
        
        Args:
            item: HackerNews item data
            filter_type: Type filter ('ask', 'show', or None)
            
        Returns:
            Idea dictionary or None if item is invalid
        """
        if not item or item.get('deleted') or item.get('dead'):
            return None
        
        item_id = item.get('id')
        title = item.get('title', '')
        text = item.get('text', '')
        url = item.get('url', '')
        item_type = item.get('type', 'story')
        score = item.get('score', 0)
        descendants = item.get('descendants', 0)
        by = item.get('by', '')
        time = item.get('time', 0)
        
        # Apply type filtering
        title_lower = title.lower()
        if filter_type == 'ask' and not title_lower.startswith('ask hn'):
            return None
        if filter_type == 'show' and not title_lower.startswith('show hn'):
            return None
        
        # Build tags
        tags = [item_type]
        
        # Add type-specific tags
        if title_lower.startswith('ask hn'):
            tags.append('Ask HN')
        elif title_lower.startswith('show hn'):
            tags.append('Show HN')
        elif title_lower.startswith('tell hn'):
            tags.append('Tell HN')
        
        # Extract domain from URL if present
        if url:
            try:
                domain = urlparse(url).netloc
                if domain:
                    # Remove www. prefix
                    domain = domain.replace('www.', '')
                    tags.append(domain)
            except Exception:
                pass
        
        return {
            'source_id': str(item_id),
            'title': title,
            'description': text if text else '',
            'tags': self.format_tags(tags),
            'metrics': item  # Store full item data for metrics calculation
        }
    
    def scrape(self, filter_type: Optional[str] = None, limit: Optional[int] = None) -> List[IdeaInspiration]:
        """Scrape type-filtered stories from HackerNews.
        
        Args:
            filter_type: Type filter ('ask', 'show', or None for all)
            limit: Maximum number of stories to scrape (uses config if not provided)
            
        Returns:
            List of idea dictionaries
        """
        if filter_type == 'ask':
            return self.scrape_ask(limit=limit)
        elif filter_type == 'show':
            return self.scrape_show(limit=limit)
        else:
            # Default: scrape from top stories and filter
            return self.scrape_type_filtered(filter_type=filter_type, limit=limit)
    
    def scrape_ask(self, limit: Optional[int] = None) -> List[IdeaInspiration]:
        """Scrape Ask HN posts.
        
        Args:
            limit: Maximum number of posts to scrape
            
        Returns:
            List of IdeaInspiration objects
        """
        return self.scrape_type_filtered(filter_type='ask', limit=limit)
    
    def scrape_show(self, limit: Optional[int] = None) -> List[IdeaInspiration]:
        """Scrape Show HN posts.
        
        Args:
            limit: Maximum number of posts to scrape
            
        Returns:
            List of IdeaInspiration objects
        """
        return self.scrape_type_filtered(filter_type='show', limit=limit)
    
    def scrape_type_filtered(self, filter_type: Optional[str] = None, limit: Optional[int] = None) -> List[IdeaInspiration]:
        """Scrape type-filtered stories from HackerNews.
        
        Args:
            filter_type: Type filter ('ask', 'show', or None)
            limit: Maximum number of stories to scrape (uses config if not provided)
            
        Returns:
            List of IdeaInspiration objects
        """
        ideas = []
        
        if limit is None:
            limit = self.config.hn_type_max_posts
        
        filter_label = filter_type.upper() if filter_type else "type-filtered"
        print(f"Scraping {limit} {filter_label} stories from HackerNews...")
        
        try:
            # Get top story IDs - we'll filter from top stories
            # In practice, we need to fetch more than limit to get enough filtered results
            fetch_limit = limit * 5  # Fetch 5x to ensure we get enough after filtering
            url = f"{self.api_base_url}/topstories.json"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            story_ids = response.json()[:fetch_limit]
            
            print(f"Fetching from {len(story_ids)} story IDs...")
            
            # Fetch each story and filter
            for item_id in story_ids:
                if len(ideas) >= limit:
                    break
                    
                item = self._fetch_item(item_id)
                if item:
                    idea = self._item_to_idea(item, filter_type)
                    if idea:
                        idea = self._transform_story_to_idea(idea, filter_type)
                        ideas.append(idea)
                        score = item.get('score', 0)
                        print(f"  ✓ {item.get('title', '')[:60]}... (score: {score})")
            
            print(f"\nSuccessfully scraped {len(ideas)} {filter_label} stories")
            
        except requests.RequestException as e:
            print(f"Error fetching {filter_label} stories: {e}")
        
        return ideas
    
    def _transform_story_to_idea(self, story_data: Dict[str, Any], filter_type: Optional[str] = None) -> IdeaInspiration:
        """Transform HackerNews story data to IdeaInspiration object.
        
        Args:
            story_data: Story data dictionary
            filter_type: Type filter applied ('ask', 'show', or None)
            
        Returns:
            IdeaInspiration object
        """
        title = story_data.get('title', 'Untitled')
        description = story_data.get('description', '')
        tags = story_data.get('tags', [])
        
        # Extract metrics from the full item data and move to metadata as strings
        metrics = story_data.get('metrics', {})
        
        metadata = {
            'story_id': story_data.get('source_id', ''),
            'score': str(metrics.get('score', 0)),
            'descendants': str(metrics.get('descendants', 0)),
            'by': str(metrics.get('by', '')),
            'time': str(metrics.get('time', '')),
            'type': str(metrics.get('type', 'story')),
            'source': 'hackernews_type',
        }
        
        # Add filter type if present
        if filter_type:
            metadata['filter_type'] = filter_type
        
        # Add URL if present
        if metrics.get('url'):
            metadata['story_url'] = str(metrics['url'])
        
        # Create IdeaInspiration using from_text factory method
        idea = IdeaInspiration.from_text(
            title=title,
            description=description,
            text_content=description,
            keywords=tags,
            metadata=metadata,
            source_id=story_data.get('source_id', ''),
            source_url=f"https://news.ycombinator.com/item?id={story_data.get('source_id', '')}",
            source_platform="hackernews",
            source_created_by=str(metrics.get('by', '')),
            source_created_at=str(metrics.get('time', ''))
        )
        
        return idea
