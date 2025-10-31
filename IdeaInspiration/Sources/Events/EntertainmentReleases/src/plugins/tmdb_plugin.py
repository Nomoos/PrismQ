"""TMDB entertainment releases plugin."""

import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from . import SourcePlugin


class TMDBPlugin(SourcePlugin):
    """Plugin for scraping entertainment releases using TMDB API."""
    
    API_BASE_URL = "https://api.themoviedb.org/3"
    
    def __init__(self, config):
        """Initialize TMDB plugin."""
        super().__init__(config)
        self.api_key = getattr(config, 'tmdb_api_key', '')
        if not self.api_key:
            raise ValueError("TMDB API key is required. Get one at https://www.themoviedb.org/settings/api")
    
    def get_source_name(self) -> str:
        return "tmdb"
    
    def scrape(
        self,
        media_type: Optional[str] = None,
        region: Optional[str] = None,
        upcoming: bool = True,
        max_releases: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Scrape entertainment releases from TMDB."""
        releases = []
        
        if max_releases is None:
            max_releases = getattr(self.config, 'max_releases', 50)
        
        if media_type is None:
            media_type = getattr(self.config, 'default_media_type', 'movie')
        
        if region is None:
            region = getattr(self.config, 'default_region', 'US')
        
        if upcoming and media_type == 'movie':
            movie_releases = self._get_upcoming_movies(region, max_releases)
            releases.extend(movie_releases)
        elif media_type == 'tv':
            tv_releases = self._get_popular_tv(max_releases)
            releases.extend(tv_releases)
        
        return releases[:max_releases]
    
    def _get_upcoming_movies(self, region: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get upcoming movie releases."""
        releases = []
        
        try:
            response = requests.get(
                f"{self.API_BASE_URL}/movie/upcoming",
                params={'api_key': self.api_key, 'region': region, 'page': 1},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data and 'results' in data:
                for movie in data['results'][:limit]:
                    processed_release = self._process_movie(movie)
                    if processed_release:
                        releases.append(processed_release)
        
        except Exception as e:
            print(f"Error getting upcoming movies: API request failed")
        
        return releases
    
    def _get_popular_tv(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get popular TV shows."""
        releases = []
        
        try:
            response = requests.get(
                f"{self.API_BASE_URL}/tv/popular",
                params={'api_key': self.api_key, 'page': 1},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data and 'results' in data:
                for show in data['results'][:limit]:
                    processed_release = self._process_tv_show(show)
                    if processed_release:
                        releases.append(processed_release)
        
        except Exception as e:
            print(f"Error getting TV shows: API request failed")
        
        return releases
    
    def _process_movie(self, movie: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process raw movie data from API."""
        if not movie:
            return None
        
        # Determine importance based on popularity and vote count
        popularity = movie.get('popularity', 0)
        vote_average = movie.get('vote_average', 0)
        
        importance = 'moderate'
        if popularity > 100 and vote_average > 7:
            importance = 'blockbuster'
        elif popularity > 50:
            importance = 'major'
        elif popularity < 10:
            importance = 'indie'
        
        # Determine scope (worldwide by default for API results)
        scope = 'worldwide'
        
        # Build release data
        release_data = {
            'id': str(movie.get('id')),
            'name': movie.get('title', ''),
            'date': movie.get('release_date', ''),
            'media_type': 'movie',
            'scope': scope,
            'importance': importance,
            'genre': movie.get('genre_ids', []),
            'rating': movie.get('vote_average', 0),
            'popularity': popularity,
            'overview': movie.get('overview', ''),
            'poster_path': movie.get('poster_path', ''),
            'backdrop_path': movie.get('backdrop_path', ''),
            'franchise': False,  # Would need additional API call to determine
            'audience_size_estimate': self._estimate_audience(importance, scope),
        }
        
        return release_data
    
    def _process_tv_show(self, show: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process raw TV show data from API."""
        if not show:
            return None
        
        popularity = show.get('popularity', 0)
        vote_average = show.get('vote_average', 0)
        
        importance = 'moderate'
        if popularity > 100 and vote_average > 7:
            importance = 'major'
        elif popularity < 10:
            importance = 'indie'
        
        scope = 'worldwide'
        
        # Use first air date or estimate next episode date
        air_date = show.get('first_air_date', datetime.now().strftime('%Y-%m-%d'))
        
        release_data = {
            'id': str(show.get('id')),
            'name': show.get('name', ''),
            'date': air_date,
            'media_type': 'tv',
            'scope': scope,
            'importance': importance,
            'genre': show.get('genre_ids', []),
            'rating': show.get('vote_average', 0),
            'popularity': popularity,
            'overview': show.get('overview', ''),
            'poster_path': show.get('poster_path', ''),
            'backdrop_path': show.get('backdrop_path', ''),
            'franchise': False,
            'audience_size_estimate': self._estimate_audience(importance, scope),
        }
        
        return release_data
    
    def _estimate_audience(self, importance: str, scope: str) -> int:
        """Estimate audience size for a release."""
        base_audience = {
            'worldwide': 100_000_000,
            'limited': 10_000_000,
            'exclusive': 1_000_000
        }
        
        importance_mult = {
            'blockbuster': 5.0,
            'major': 2.0,
            'moderate': 1.0,
            'indie': 0.3
        }
        
        base = base_audience.get(scope, 10_000_000)
        mult = importance_mult.get(importance, 1.0)
        
        return int(base * mult)
