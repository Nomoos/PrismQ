"""Spotify Trending source plugin for scraping trending podcast episodes.

This plugin uses the Spotify Web API (via Spotipy) to scrape trending podcasts,
providing comprehensive metadata extraction.
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from . import SourcePlugin, IdeaInspiration


class SpotifyTrendingPlugin(SourcePlugin):
    """Plugin for scraping trending podcast episodes from Spotify using Web API."""
    
    def __init__(self, config):
        """Initialize Spotify trending plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        
        # Check if credentials are configured
        if not self.config.spotify_client_id or not self.config.spotify_client_secret:
            raise ValueError(
                "Spotify credentials not configured. "
                "Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in your .env file. "
                "Get them from https://developer.spotify.com/dashboard"
            )
        
        # Initialize Spotify client
        self.sp = self._init_spotify_client()
    
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "spotify_trending"
    
    def _init_spotify_client(self) -> spotipy.Spotify:
        """Initialize Spotify API client.
        
        Returns:
            Spotipy client instance
        """
        client_credentials_manager = SpotifyClientCredentials(
            client_id=self.config.spotify_client_id,
            client_secret=self.config.spotify_client_secret
        )
        return spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    def scrape(self, top_n: Optional[int] = None, market: str = "US") -> List[IdeaInspiration]:
        """Scrape trending podcast episodes from Spotify.
        
        Args:
            top_n: Number of episodes to scrape (optional, uses config if not provided)
            market: Market/region code (default: "US")
        
        Returns:
            List of IdeaInspiration objects
        """
        ideas = []
        
        if top_n is None:
            top_n = getattr(self.config, 'spotify_trending_max_episodes', 10)
        
        print(f"Scraping trending podcast episodes from Spotify...")
        
        try:
            # Get featured playlists which often include popular podcasts
            # Note: Spotify doesn't have a direct "trending podcasts" endpoint,
            # so we use new releases and featured content as proxies
            
            # Get new podcast episodes
            new_episodes = self._get_new_episodes(limit=top_n, market=market)
            
            for episode in new_episodes:
                idea = self._episode_to_idea(episode)
                if idea:
                    idea = self._transform_episode_to_idea(idea)
                    ideas.append(idea)
        
        except Exception as e:
            print(f"Error scraping trending podcasts: {e}")
        
        return ideas
    
    def _get_new_episodes(self, limit: int = 10, market: str = "US") -> List[Dict[str, Any]]:
        """Get new podcast episodes from Spotify.
        
        Args:
            limit: Maximum number of episodes to fetch
            market: Market/region code
        
        Returns:
            List of episode dictionaries
        """
        episodes = []
        
        try:
            # Search for popular podcasts across different categories
            # This is a workaround since Spotify doesn't have a trending endpoint
            categories = ["society & culture", "business", "comedy", "news", "true crime"]
            episodes_per_category = max(1, limit // len(categories))
            
            for category in categories:
                # Search for shows in this category
                results = self.sp.search(
                    q=f'"{category}"',
                    type='show',
                    market=market,
                    limit=5
                )
                
                if results and 'shows' in results and results['shows']['items']:
                    for show in results['shows']['items'][:2]:  # Top 2 shows per category
                        # Get episodes from this show
                        show_id = show['id']
                        show_episodes = self.sp.show_episodes(
                            show_id,
                            market=market,
                            limit=episodes_per_category
                        )
                        
                        if show_episodes and 'items' in show_episodes:
                            for episode in show_episodes['items']:
                                # Enrich episode with show data
                                episode['show'] = {
                                    'name': show['name'],
                                    'publisher': show['publisher'],
                                    'total_episodes': show.get('total_episodes', 0)
                                }
                                episodes.append(episode)
                                
                                if len(episodes) >= limit:
                                    return episodes[:limit]
        
        except Exception as e:
            print(f"Error fetching new episodes: {e}")
        
        return episodes[:limit]
    
    def _episode_to_idea(self, episode: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert Spotify episode data to idea format.
        
        Args:
            episode: Spotify episode data
        
        Returns:
            Idea dictionary or None if conversion fails
        """
        try:
            # Extract basic information
            episode_id = episode.get('id')
            title = episode.get('name', 'Untitled Episode')
            description = episode.get('description', '')
            
            # Extract tags from show and episode
            tags = []
            
            if 'show' in episode:
                show = episode['show']
                tags.append(show.get('name', ''))
                tags.append(show.get('publisher', ''))
            
            # Build idea dictionary
            idea = {
                'source': 'spotify_podcasts',
                'source_id': episode_id,
                'title': title,
                'description': description,
                'tags': tags,
                'show': episode.get('show', {}),
                'metrics': {
                    'duration_ms': episode.get('duration_ms', 0),
                    'release_date': episode.get('release_date', ''),
                    'language': episode.get('language', ''),
                    'explicit': episode.get('explicit', False)
                },
                'universal_metrics': {
                    'engagement_estimate': 5.0  # Base estimate, can be enhanced
                }
            }
            
            return idea
        
        except Exception as e:
            print(f"Error converting episode to idea: {e}")
            return None
    
    def _transform_episode_to_idea(self, episode_data: Dict[str, Any]) -> IdeaInspiration:
        """Transform Spotify episode data to IdeaInspiration object.
        
        Args:
            episode_data: Episode data dictionary
            
        Returns:
            IdeaInspiration object
        """
        title = episode_data.get('title', 'Untitled Episode')
        description = episode_data.get('description', '')
        tags = episode_data.get('tags', [])
        
        # Extract metrics and move to metadata as strings
        metrics = episode_data.get('metrics', {})
        show_data = episode_data.get('show', {})
        universal_metrics = episode_data.get('universal_metrics', {})
        
        metadata = {
            'episode_id': episode_data.get('source_id', ''),
            'duration_ms': str(metrics.get('duration_ms', 0)),
            'release_date': str(metrics.get('release_date', '')),
            'language': str(metrics.get('language', '')),
            'explicit': str(metrics.get('explicit', False)),
            'show_name': str(show_data.get('name', '')),
            'show_publisher': str(show_data.get('publisher', '')),
            'show_total_episodes': str(show_data.get('total_episodes', 0)),
            'engagement_estimate': str(universal_metrics.get('engagement_estimate', 5.0)),
            'source': episode_data.get('source', 'spotify_podcasts'),
        }
        
        # Create IdeaInspiration using from_audio factory method
        idea = IdeaInspiration.from_audio(
            title=title,
            description=description,
            transcription='',  # Transcription would need to be added separately
            keywords=tags,
            metadata=metadata,
            source_id=episode_data.get('source_id', ''),
            source_url=f"https://open.spotify.com/episode/{episode_data.get('source_id', '')}",
            source_platform="spotify_podcasts",
            source_created_by=show_data.get('publisher', ''),
            source_created_at=str(metrics.get('release_date', ''))
        )
        
        return idea
