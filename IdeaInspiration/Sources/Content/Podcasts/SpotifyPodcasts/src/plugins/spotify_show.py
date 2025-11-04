"""Spotify Show source plugin for scraping episodes from specific shows.

This plugin uses the Spotify Web API (via Spotipy) to scrape episodes from
a specific podcast show.
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List, Dict, Any, Optional
from . import SourcePlugin, IdeaInspiration


class SpotifyShowPlugin(SourcePlugin):
    """Plugin for scraping episodes from a specific podcast show on Spotify."""
    
    def __init__(self, config):
        """Initialize Spotify show plugin.
        
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
        return "spotify_show"
    
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
    
    def scrape(self, show_id: str, top_n: Optional[int] = None, market: str = "US") -> List[IdeaInspiration]:
        """Scrape episodes from a specific podcast show.
        
        Args:
            show_id: Spotify show ID or URI (e.g., "4rOoJ6Egrf8K2IrywzwOMk" or "spotify:show:...")
            top_n: Number of episodes to scrape (optional, uses config if not provided)
            market: Market/region code (default: "US")
        
        Returns:
            List of IdeaInspiration objects
        """
        ideas = []
        
        if top_n is None:
            top_n = getattr(self.config, 'spotify_show_max_episodes', 10)
        
        # Extract show ID from URI if needed
        if show_id.startswith('spotify:show:'):
            show_id = show_id.split(':')[-1]
        
        print(f"Scraping episodes from show: {show_id}")
        
        try:
            # Get show information
            show = self.sp.show(show_id, market=market)
            
            if not show:
                print(f"Show not found: {show_id}")
                return ideas
            
            print(f"  Show: {show['name']}")
            print(f"  Publisher: {show['publisher']}")
            print(f"  Total episodes: {show.get('total_episodes', 'unknown')}")
            
            # Get episodes from the show
            episodes = self.sp.show_episodes(show_id, market=market, limit=top_n)
            
            if episodes and 'items' in episodes:
                for episode in episodes['items']:
                    # Enrich episode with show data
                    episode['show'] = {
                        'name': show['name'],
                        'publisher': show['publisher'],
                        'total_episodes': show.get('total_episodes', 0)
                    }
                    
                    idea = self._episode_to_idea(episode)
                    if idea:
                        idea = self._transform_episode_to_idea(idea)
                        ideas.append(idea)
        
        except Exception as e:
            print(f"Error scraping show '{show_id}': {e}")
        
        return ideas[:top_n]
    
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
            
            # Extract tags from show
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
                    'engagement_estimate': 5.0  # Base estimate
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
