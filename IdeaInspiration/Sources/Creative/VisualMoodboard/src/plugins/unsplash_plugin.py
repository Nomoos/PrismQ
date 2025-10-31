"""Unsplash API plugin for scraping visual inspiration."""

from typing import List, Dict, Any, Optional
from . import SourcePlugin


class UnsplashPlugin(SourcePlugin):
    """Plugin for scraping visual resources from Unsplash API."""

    def __init__(self, config):
        """Initialize Unsplash plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        
        if not config.unsplash_access_key:
            raise ValueError("Unsplash Access Key not configured")
        
        try:
            from unsplash.api import Api
            from unsplash.auth import Auth
            
            # Initialize Unsplash API client
            auth = Auth(config.unsplash_access_key, "", "", "")
            self.api = Api(auth)
        except ImportError:
            raise ValueError("python-unsplash package not installed. Install with: pip install python-unsplash")

    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "unsplash"

    def scrape(self, query: Optional[str] = None, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scrape visual resources from Unsplash.
        
        Args:
            query: Optional search query (default: curated/trending)
            max_results: Maximum number of results (default: from config)
            
        Returns:
            List of visual resource dictionaries
        """
        resources = []
        
        try:
            max_results = max_results or self.config.unsplash_max_results
            per_page = min(max_results, 30)  # Unsplash API limit
            
            if query:
                # Search for photos
                photos = self.api.search.photos(query, per_page=per_page)
                photo_list = photos.get('results', [])
            else:
                # Get curated photos
                photo_list = self.api.photo.curated(per_page=per_page)
            
            for photo in photo_list[:max_results]:
                try:
                    resource = {
                        'source_id': photo.id,
                        'title': photo.description or photo.alt_description or f"Photo by {photo.user.name}",
                        'url': photo.urls.regular,
                        'tags': self._extract_tags(photo),
                        'metrics': self._build_metrics(photo)
                    }
                    resources.append(resource)
                    
                except Exception as e:
                    print(f"Error processing photo {getattr(photo, 'id', 'unknown')}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping Unsplash: {e}")
        
        return resources

    def _extract_tags(self, photo) -> str:
        """Extract tags from Unsplash photo.
        
        Args:
            photo: Photo object from Unsplash API
            
        Returns:
            Comma-separated tag string
        """
        tags = ['visual', 'unsplash']
        
        # Add category if available
        if hasattr(photo, 'categories') and photo.categories:
            for cat in photo.categories:
                if hasattr(cat, 'title'):
                    tags.append(cat.title.lower().replace(' ', '_'))
        
        # Add color
        if hasattr(photo, 'color') and photo.color:
            tags.append(f"color_{photo.color.replace('#', '')}")
        
        return ','.join(tags)

    def _build_metrics(self, photo) -> Dict[str, Any]:
        """Build metrics dictionary from Unsplash photo.
        
        Args:
            photo: Photo object from Unsplash API
            
        Returns:
            Metrics dictionary
        """
        metrics = {
            'id': photo.id,
            'width': photo.width if hasattr(photo, 'width') else None,
            'height': photo.height if hasattr(photo, 'height') else None,
            'color': photo.color if hasattr(photo, 'color') else None,
            'description': photo.description if hasattr(photo, 'description') else None,
            'alt_description': photo.alt_description if hasattr(photo, 'alt_description') else None,
            'urls': {
                'raw': photo.urls.raw if hasattr(photo, 'urls') else None,
                'full': photo.urls.full if hasattr(photo, 'urls') else None,
                'regular': photo.urls.regular if hasattr(photo, 'urls') else None,
                'small': photo.urls.small if hasattr(photo, 'urls') else None,
                'thumb': photo.urls.thumb if hasattr(photo, 'urls') else None,
            } if hasattr(photo, 'urls') else {},
            'user': {
                'name': photo.user.name if hasattr(photo, 'user') else None,
                'username': photo.user.username if hasattr(photo, 'user') else None,
                'portfolio_url': photo.user.portfolio_url if hasattr(photo, 'user') and hasattr(photo.user, 'portfolio_url') else None,
            } if hasattr(photo, 'user') else {},
            'likes': photo.likes if hasattr(photo, 'likes') else 0,
            'downloads': getattr(photo, 'downloads', 0),
        }
        
        return metrics

    def get_photo_by_id(self, photo_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific photo by ID.
        
        Args:
            photo_id: Unsplash photo ID
            
        Returns:
            Visual resource dictionary or None
        """
        try:
            photo = self.api.photo.get(photo_id)
            
            if not photo:
                return None
            
            resource = {
                'source_id': photo.id,
                'title': photo.description or photo.alt_description or f"Photo by {photo.user.name}",
                'url': photo.urls.regular,
                'tags': self._extract_tags(photo),
                'metrics': self._build_metrics(photo)
            }
            
            return resource
            
        except Exception as e:
            print(f"Error getting photo '{photo_id}': {e}")
            return None

    def get_random_photos(self, count: int = 10, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get random photos optionally filtered by query.
        
        Args:
            count: Number of random photos
            query: Optional search query filter
            
        Returns:
            List of visual resource dictionaries
        """
        resources = []
        
        try:
            photos = self.api.photo.random(count=count, query=query)
            
            # API returns single photo or list depending on count
            if not isinstance(photos, list):
                photos = [photos]
            
            for photo in photos:
                try:
                    resource = {
                        'source_id': photo.id,
                        'title': photo.description or photo.alt_description or f"Photo by {photo.user.name}",
                        'url': photo.urls.regular,
                        'tags': self._extract_tags(photo),
                        'metrics': self._build_metrics(photo)
                    }
                    resources.append(resource)
                except Exception as e:
                    print(f"Error processing photo: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error getting random photos: {e}")
        
        return resources
