"""Google Play Store scraper plugin using google-play-scraper."""

import time
from typing import List, Dict, Any
from . import CommercePlugin

try:
    from google_play_scraper import app, collection, search
    GOOGLE_PLAY_AVAILABLE = True
except ImportError:
    GOOGLE_PLAY_AVAILABLE = False


class GooglePlayPlugin(CommercePlugin):
    """Plugin for scraping top charts from Google Play Store."""

    def __init__(self, config):
        """Initialize Google Play plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        
        if not GOOGLE_PLAY_AVAILABLE:
            raise ValueError("google-play-scraper not installed. Install with: pip install google-play-scraper")
        
        self.country = config.google_play_country
        self.language = config.google_play_language
        self.categories = config.app_store_categories
        self.max_apps = config.app_store_max_apps
        self.delay = config.app_store_delay_seconds

    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "google_play_top_charts"

    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape top apps from Google Play Store.
        
        Returns:
            List of app dictionaries
        """
        apps = []
        
        for category in self.categories:
            print(f"Scraping Google Play category: {category}")
            
            try:
                category_apps = self._scrape_category(category)
                apps.extend(category_apps)
                
                # Respect rate limits
                time.sleep(self.delay)
                
            except Exception as e:
                print(f"Error scraping category {category}: {e}")
                continue
        
        return apps

    def _scrape_category(self, category: str) -> List[Dict[str, Any]]:
        """Scrape apps from a specific category.
        
        Args:
            category: Category identifier
            
        Returns:
            List of app dictionaries
        """
        apps_data = []
        
        try:
            # Map common category names to Google Play category IDs
            category_map = {
                'games': 'GAME',
                'productivity': 'PRODUCTIVITY',
                'social-networking': 'SOCIAL',
                'entertainment': 'ENTERTAINMENT',
                'education': 'EDUCATION',
                'tools': 'TOOLS',
                'communication': 'COMMUNICATION'
            }
            
            category_id = category_map.get(category.lower(), category.upper())
            
            # Get top free apps in category
            top_apps = collection(
                collection='TOP_FREE',
                category=category_id,
                results=min(self.max_apps, 120),  # API limit
                lang=self.language,
                country=self.country
            )
            
            # Get detailed info for each app
            for i, app_preview in enumerate(top_apps[:self.max_apps]):
                try:
                    app_details = app(
                        app_preview['appId'],
                        lang=self.language,
                        country=self.country
                    )
                    
                    app_data = self._transform_app_data(app_details, category, i + 1)
                    apps_data.append(app_data)
                    
                    # Small delay between detail requests
                    time.sleep(0.2)
                    
                except Exception as e:
                    print(f"Error getting details for app {app_preview.get('appId')}: {e}")
                    continue
            
        except Exception as e:
            print(f"Error scraping Google Play category {category}: {e}")
        
        return apps_data

    def _transform_app_data(self, app_details: Dict[str, Any], category: str, rank: int) -> Dict[str, Any]:
        """Transform Google Play app data to standardized format.
        
        Args:
            app_details: App details from google-play-scraper
            category: Category name
            rank: App rank in category
            
        Returns:
            Standardized app dictionary
        """
        return {
            'app_id': app_details.get('appId', ''),
            'title': app_details.get('title', ''),
            'brand': app_details.get('developer', ''),
            'developer': app_details.get('developer', ''),
            'category': category,
            'price': app_details.get('price', 0.0),
            'currency': app_details.get('currency', 'USD'),
            'description': app_details.get('description', ''),
            'category_rank': rank,
            'rating': app_details.get('score', 0.0),
            'review_count': app_details.get('ratings', 0),
            'installs': app_details.get('installs', ''),
            'installs_min': app_details.get('minInstalls', 0),
            'installs_max': app_details.get('maxInstalls', 0),
            'in_stock': True,
            'first_available': app_details.get('released', ''),
            'last_updated': app_details.get('updated', ''),
            'platform_specific': {
                'platform': 'google_play',
                'content_rating': app_details.get('contentRating', ''),
                'ad_supported': app_details.get('adSupported', False),
                'in_app_purchases': app_details.get('offersIAP', False),
                'developer_id': app_details.get('developerId', ''),
                'developer_email': app_details.get('developerEmail', ''),
                'url': app_details.get('url', ''),
                'icon': app_details.get('icon', ''),
                'screenshots': app_details.get('screenshots', []),
                'video': app_details.get('video', ''),
                'genre': app_details.get('genre', ''),
                'genre_id': app_details.get('genreId', ''),
                'version': app_details.get('version', ''),
                'size': app_details.get('size', ''),
                'android_version': app_details.get('androidVersion', ''),
            }
        }
