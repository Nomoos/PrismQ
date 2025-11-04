"""Google Trends plugin for scraping trending search queries."""

import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pytrends.request import TrendReq
from . import SignalPlugin, IdeaInspiration


class GoogleTrendsPlugin(SignalPlugin):
    """Plugin for scraping signals from Google Trends."""
    
    def __init__(self, config):
        """Initialize Google Trends plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        
        # Initialize pytrends
        self.pytrends = TrendReq(
            hl=config.google_trends_language,
            tz=0,  # UTC timezone
            timeout=(10, 25)  # (connect timeout, read timeout)
        )
    
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "google_trends"
    
    def scrape(self, keywords: Optional[List[str]] = None) -> List[IdeaInspiration]:
        """Scrape trending queries from Google Trends.
        
        Args:
            keywords: Optional list of keywords to check trends for
            
        Returns:
            List of IdeaInspiration objects
        """
        signals = []
        
        try:
            # Get trending searches
            trending = self._get_trending_searches()
            signals.extend(trending)
            
            # If keywords provided, get trends for those too
            if keywords:
                keyword_trends = self._get_keyword_trends(keywords)
                signals.extend(keyword_trends)
            
        except Exception as e:
            print(f"Error scraping Google Trends: {e}")
        
        return signals
    
    def _get_trending_searches(self) -> List[IdeaInspiration]:
        """Get current trending searches.
        
        Returns:
            List of IdeaInspiration objects
        """
        signals = []
        
        try:
            # Get trending searches for configured region
            trending_df = self.pytrends.trending_searches(
                pn=self.config.google_trends_region
            )
            
            # Process each trending query
            for idx, row in trending_df.iterrows():
                if idx >= self.config.google_trends_max_results:
                    break
                
                query = str(row[0])
                tags = self.format_tags(['google', 'search', 'trend', self.config.google_trends_region.lower()])
                
                # Build metadata with string values
                metadata = {
                    'region': self.config.google_trends_region,
                    'rank': str(idx + 1),
                    'volume_estimate': str(100 - idx),  # Rough approximation
                    'signal_type': 'trend',
                    'first_seen': datetime.now(timezone.utc).isoformat() + 'Z',
                    'current_status': 'rising',
                }
                
                # Create IdeaInspiration using from_text factory method
                idea = IdeaInspiration.from_text(
                    title=query,
                    description=f"Trending search query in {self.config.google_trends_region}",
                    text_content=f"Search trend: {query}",
                    keywords=tags,
                    metadata=metadata,
                    source_id=f"{query}_{self.config.google_trends_region}_{datetime.now(timezone.utc).strftime('%Y%m%d%H')}",
                    source_url=f"https://trends.google.com/trends/explore?q={query}&geo={self.config.google_trends_region}",
                    source_platform="google_trends",
                    source_created_by="Google Trends",
                    source_created_at=datetime.now(timezone.utc).isoformat() + 'Z'
                )
                
                signals.append(idea)
            
            print(f"Found {len(signals)} trending searches")
            
        except Exception as e:
            print(f"Error getting trending searches: {e}")
        
        return signals
    
    def _get_keyword_trends(self, keywords: List[str]) -> List[IdeaInspiration]:
        """Get trend data for specific keywords.
        
        Args:
            keywords: List of keywords to check
            
        Returns:
            List of IdeaInspiration objects
        """
        signals = []
        
        try:
            # Process keywords in batches of 5 (Google Trends API limit)
            batch_size = 5
            for i in range(0, len(keywords), batch_size):
                batch = keywords[i:i+batch_size]
                
                # Build payload
                self.pytrends.build_payload(
                    batch,
                    cat=0,
                    timeframe=self.config.google_trends_timeframe,
                    geo=self.config.google_trends_region,
                    gprop=''
                )
                
                # Get interest over time
                interest_df = self.pytrends.interest_over_time()
                
                if interest_df.empty:
                    continue
                
                # Process each keyword
                for keyword in batch:
                    if keyword not in interest_df.columns:
                        continue
                    
                    # Get latest value
                    latest_value = int(interest_df[keyword].iloc[-1])
                    
                    # Calculate velocity (change from previous period)
                    velocity = 0.0
                    if len(interest_df) > 1:
                        prev_value = interest_df[keyword].iloc[-2]
                        if prev_value > 0:
                            velocity = ((latest_value - prev_value) / prev_value) * 100
                    
                    tags = self.format_tags(['google', 'search', 'trend', self.config.google_trends_region.lower(), 'keyword'])
                    
                    # Build metadata with string values
                    metadata = {
                        'region': self.config.google_trends_region,
                        'timeframe': self.config.google_trends_timeframe,
                        'volume': str(latest_value),
                        'velocity': str(round(velocity, 2)),
                        'signal_type': 'trend',
                        'first_seen': datetime.now(timezone.utc).isoformat() + 'Z',
                        'current_status': 'rising' if velocity > 0 else 'declining',
                    }
                    
                    # Create IdeaInspiration using from_text factory method
                    idea = IdeaInspiration.from_text(
                        title=keyword,
                        description=f"Search trend for '{keyword}' in {self.config.google_trends_region}",
                        text_content=f"Keyword trend: {keyword}",
                        keywords=tags,
                        metadata=metadata,
                        source_id=f"{keyword}_{self.config.google_trends_region}_{datetime.now(timezone.utc).strftime('%Y%m%d%H')}",
                        source_url=f"https://trends.google.com/trends/explore?q={keyword}&geo={self.config.google_trends_region}",
                        source_platform="google_trends",
                        source_created_by="Google Trends",
                        source_created_at=datetime.now(timezone.utc).isoformat() + 'Z'
                    )
                    
                    signals.append(idea)
                
                # Rate limiting - be nice to Google
                time.sleep(self.config.retry_delay_seconds)
            
            print(f"Found trends for {len(signals)} keywords")
            
        except Exception as e:
            print(f"Error getting keyword trends: {e}")
        
        return signals
    
    def get_related_queries(self, keyword: str) -> List[str]:
        """Get related queries for a keyword.
        
        Args:
            keyword: Keyword to get related queries for
            
        Returns:
            List of related query strings
        """
        related = []
        
        try:
            # Build payload
            self.pytrends.build_payload(
                [keyword],
                cat=0,
                timeframe=self.config.google_trends_timeframe,
                geo=self.config.google_trends_region,
                gprop=''
            )
            
            # Get related queries
            related_df = self.pytrends.related_queries()
            
            if keyword in related_df and related_df[keyword]['top'] is not None:
                queries_df = related_df[keyword]['top']
                related = queries_df['query'].tolist()
            
        except Exception as e:
            print(f"Error getting related queries: {e}")
        
        return related
