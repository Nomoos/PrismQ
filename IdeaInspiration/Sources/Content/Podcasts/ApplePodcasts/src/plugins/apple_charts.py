"""Apple Podcasts Charts plugin for scraping trending podcasts.

This plugin scrapes podcast charts from Apple Podcasts using iTunes Search API
and podcastindex (if available).
"""

import json
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from . import SourcePlugin, IdeaInspiration


class AppleChartsPlugin(SourcePlugin):
    """Plugin for scraping podcasts from Apple Podcasts charts."""
    
    # iTunes Search API endpoints
    ITUNES_SEARCH_API = "https://itunes.apple.com/search"
    ITUNES_LOOKUP_API = "https://itunes.apple.com/lookup"
    
    def __init__(self, config):
        """Initialize Apple Charts plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        self.region = getattr(config, 'apple_podcasts_region', 'us')
        self.max_shows = getattr(config, 'apple_podcasts_max_shows', 20)
        self.max_episodes = getattr(config, 'apple_podcasts_max_episodes', 10)
    
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "apple_podcasts_charts"
    
    def scrape(self, **kwargs) -> List[IdeaInspiration]:
        """Scrape podcasts from Apple Podcasts charts.
        
        Returns:
            List of idea dictionaries
        """
        genre = kwargs.get('genre', 'all')
        top_n = kwargs.get('top_n', self.max_shows)
        
        return self.scrape_charts(genre=genre, top_n=top_n)
    
    def scrape_charts(self, genre: str = "all", top_n: Optional[int] = None) -> List[IdeaInspiration]:
        """Scrape top podcasts from Apple Podcasts charts.
        
        Args:
            genre: Genre/category to filter (default: "all")
            top_n: Number of shows to scrape (default: config value)
        
        Returns:
            List of IdeaInspiration objects
        """
        ideas = []
        
        if top_n is None:
            top_n = self.max_shows
        
        print(f"Scraping Apple Podcasts charts (region: {self.region}, genre: {genre})...")
        
        # Search for podcasts in the specified genre
        podcasts = self._search_podcasts(genre=genre, limit=top_n)
        
        if not podcasts:
            print(f"No podcasts found for genre: {genre}")
            return ideas
        
        print(f"Found {len(podcasts)} podcasts")
        
        # For each podcast, get episodes
        for i, podcast in enumerate(podcasts, 1):
            print(f"  [{i}/{len(podcasts)}] Processing: {podcast.get('collectionName', 'Unknown')}")
            
            collection_id = podcast.get('collectionId')
            if not collection_id:
                continue
            
            # Get episodes for this podcast
            episodes = self._get_podcast_episodes(collection_id, limit=self.max_episodes)
            
            # Convert episodes to idea format
            for episode in episodes:
                idea = self._episode_to_idea(episode, podcast)
                if idea:
                    idea = self._transform_episode_to_idea(idea)
                    ideas.append(idea)
        
        print(f"Total episodes scraped: {len(ideas)}")
        return ideas
    
    def _search_podcasts(self, genre: str = "all", limit: int = 20) -> List[Dict[str, Any]]:
        """Search for podcasts using iTunes Search API.
        
        Args:
            genre: Genre/category filter
            limit: Maximum number of results
            
        Returns:
            List of podcast dictionaries
        """
        params = {
            'term': 'podcast',
            'media': 'podcast',
            'entity': 'podcast',
            'country': self.region,
            'limit': min(limit, 200)  # iTunes API max is 200
        }
        
        # Add genre if specified
        if genre and genre != "all":
            params['genreId'] = self._get_genre_id(genre)
        
        try:
            response = requests.get(self.ITUNES_SEARCH_API, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return data.get('results', [])
        except requests.RequestException as e:
            print(f"Error searching podcasts: {e}")
            return []
    
    def _get_podcast_episodes(self, collection_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get episodes for a specific podcast.
        
        Args:
            collection_id: iTunes collection ID
            limit: Maximum number of episodes
            
        Returns:
            List of episode dictionaries
        """
        params = {
            'id': collection_id,
            'entity': 'podcastEpisode',
            'limit': min(limit, 200)
        }
        
        try:
            response = requests.get(self.ITUNES_LOOKUP_API, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = data.get('results', [])
            # First result is usually the podcast itself, rest are episodes
            episodes = [r for r in results if r.get('kind') == 'podcast-episode']
            
            return episodes[:limit]
        except requests.RequestException as e:
            print(f"Error getting episodes for collection {collection_id}: {e}")
            return []
    
    def _episode_to_idea(self, episode: Dict[str, Any], podcast: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert episode data to idea format.
        
        Args:
            episode: Episode data from iTunes API
            podcast: Podcast data from iTunes API
            
        Returns:
            Idea dictionary or None
        """
        # Extract basic information
        track_id = episode.get('trackId')
        if not track_id:
            return None
        
        title = episode.get('trackName', '')
        description = episode.get('description', '') or episode.get('shortDescription', '')
        
        # Extract metrics
        metrics = {
            'rating': podcast.get('averageUserRating'),
            'rating_count': podcast.get('userRatingCount'),
            'duration_ms': episode.get('trackTimeMillis'),
            'release_date': episode.get('releaseDate'),
            'show': {
                'name': podcast.get('collectionName'),
                'artist': podcast.get('artistName'),
                'rating': podcast.get('averageUserRating')
            },
            'genres': episode.get('genres', []),
            'country': episode.get('country', self.region),
            'platform_specific': {
                'track_id': track_id,
                'collection_id': podcast.get('collectionId'),
                'artist_id': podcast.get('artistId'),
                'feed_url': episode.get('feedUrl') or podcast.get('feedUrl'),
                'artwork_url': episode.get('artworkUrl600') or podcast.get('artworkUrl600'),
            }
        }
        
        # Extract tags from genres and categories
        tags = []
        if episode.get('genres'):
            tags.extend(episode['genres'])
        if podcast.get('collectionName'):
            tags.append(podcast['collectionName'])
        
        return {
            'source': 'apple_podcasts',
            'source_id': str(track_id),
            'title': title,
            'description': description,
            'tags': tags,
            'metrics': metrics
        }
    
    def _get_genre_id(self, genre: str) -> Optional[int]:
        """Get iTunes genre ID for a genre name.
        
        Args:
            genre: Genre name
            
        Returns:
            Genre ID or None
        """
        # Common podcast genre IDs
        genre_map = {
            'arts': 1301,
            'business': 1321,
            'comedy': 1303,
            'education': 1304,
            'fiction': 1483,
            'government': 1511,
            'health': 1512,
            'history': 1487,
            'kids': 1305,
            'leisure': 1502,
            'music': 1310,
            'news': 1489,
            'religion': 1314,
            'science': 1315,
            'society': 1324,
            'sports': 1316,
            'technology': 1318,
            'true_crime': 1488,
            'tv': 1309,
        }
        
        return genre_map.get(genre.lower())
    
    def _transform_episode_to_idea(self, episode_data: Dict[str, Any]) -> IdeaInspiration:
        """Transform Apple Podcasts episode data to IdeaInspiration object.
        
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
        show_data = metrics.get('show', {})
        platform_specific = metrics.get('platform_specific', {})
        
        metadata = {
            'episode_id': episode_data.get('source_id', ''),
            'rating': str(metrics.get('rating', '')),
            'rating_count': str(metrics.get('rating_count', '')),
            'duration_ms': str(metrics.get('duration_ms', 0)),
            'release_date': str(metrics.get('release_date', '')),
            'show_name': str(show_data.get('name', '')),
            'show_artist': str(show_data.get('artist', '')),
            'show_rating': str(show_data.get('rating', '')),
            'country': str(metrics.get('country', '')),
            'track_id': str(platform_specific.get('track_id', '')),
            'collection_id': str(platform_specific.get('collection_id', '')),
            'artist_id': str(platform_specific.get('artist_id', '')),
            'source': episode_data.get('source', 'apple_podcasts'),
        }
        
        # Add optional fields
        if platform_specific.get('feed_url'):
            metadata['feed_url'] = str(platform_specific['feed_url'])
        if platform_specific.get('artwork_url'):
            metadata['artwork_url'] = str(platform_specific['artwork_url'])
        
        # Add genres
        genres = metrics.get('genres', [])
        if isinstance(genres, list):
            for idx, genre in enumerate(genres[:3]):  # Limit to 3 genres
                metadata[f'genre_{idx+1}'] = str(genre)
        
        # Create IdeaInspiration using from_audio factory method
        idea = IdeaInspiration.from_audio(
            title=title,
            description=description,
            transcription='',  # Transcription would need to be added separately
            keywords=tags,
            metadata=metadata,
            source_id=episode_data.get('source_id', ''),
            source_url=f"https://podcasts.apple.com/podcast/id{platform_specific.get('collection_id', '')}",
            source_platform="apple_podcasts",
            source_created_by=show_data.get('artist', ''),
            source_created_at=str(metrics.get('release_date', ''))
        )
        
        return idea
