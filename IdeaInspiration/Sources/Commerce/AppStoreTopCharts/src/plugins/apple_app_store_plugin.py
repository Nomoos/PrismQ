"""Apple App Store scraper plugin using app-store-scraper."""

import time
from typing import List, Dict, Any
from . import CommercePlugin, IdeaInspiration

try:
    from app_store_scraper import AppStore
    APP_STORE_AVAILABLE = True
except ImportError:
    APP_STORE_AVAILABLE = False


class AppleAppStorePlugin(CommercePlugin):
    """Plugin for scraping top charts from Apple App Store."""

    def __init__(self, config):
        """Initialize Apple App Store plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        
        if not APP_STORE_AVAILABLE:
            raise ValueError("app-store-scraper not installed. Install with: pip install app-store-scraper")
        
        self.country = config.app_store_country
        self.categories = config.app_store_categories
        self.max_apps = config.app_store_max_apps
        self.delay = config.app_store_delay_seconds

    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "apple_app_store_top_charts"

    def scrape(self) -> List[IdeaInspiration]:
        """Scrape top apps from Apple App Store.
        
        Returns:
            List of IdeaInspiration objects
        """
        apps = []
        
        for category in self.categories:
            print(f"Scraping App Store category: {category}")
            
            try:
                category_apps = self._scrape_category(category)
                apps.extend(category_apps)
                
                # Respect rate limits
                time.sleep(self.delay)
                
            except Exception as e:
                print(f"Error scraping category {category}: {e}")
                continue
        
        return apps

    def _scrape_category(self, category: str) -> List[IdeaInspiration]:
        """Scrape apps from a specific category.
        
        Args:
            category: Category name
            
        Returns:
            List of IdeaInspiration objects
        """
        apps_data = []
        
        try:
            # Create an AppStore instance for the category
            # Note: app-store-scraper requires a search term, so we use the category name
            app_store = AppStore(
                country=self.country,
                app_name=category
            )
            
            # Scrape app data
            app_store.review(how_many=self.max_apps)
            
            # Transform the apps
            for i, app_info in enumerate(app_store.reviews[:self.max_apps], 1):
                try:
                    app_idea = self._transform_app_to_idea(app_info, category, i)
                    if app_idea:
                        apps_data.append(app_idea)
                except Exception as e:
                    print(f"Error transforming app data: {e}")
                    continue
            
        except Exception as e:
            print(f"Error scraping App Store category {category}: {e}")
        
        return apps_data

    def _transform_app_to_idea(self, app_info: Dict[str, Any], category: str, rank: int) -> IdeaInspiration:
        """Transform Apple App Store data to IdeaInspiration object.
        
        Args:
            app_info: App info from app-store-scraper
            category: Category name
            rank: App rank in category
            
        Returns:
            IdeaInspiration object
        """
        # Note: app-store-scraper primarily provides review data
        # For production, you would need to use Apple's RSS feeds or Search API
        
        app_title = app_info.get('title', app_info.get('appName', 'Unknown App'))
        developer = app_info.get('developer', app_info.get('userName', 'Unknown Developer'))
        tags = self.format_tags(['apple_app_store', 'app', category, developer])
        
        # Build metadata with string values
        metadata = {
            'app_id': app_info.get('appId', ''),
            'developer': developer,
            'category': category,
            'category_rank': str(rank),
            'rating': str(app_info.get('rating', 0.0)),
            'country': self.country,
            'date': app_info.get('date', ''),
            'platform': 'apple_app_store',
            'review_title': app_info.get('title', ''),
            'is_edited': str(app_info.get('isEdited', False)),
        }
        
        # Build description from review and app name
        description = f"{app_title} by {developer} - Rank #{rank} in {category}"
        
        # Create IdeaInspiration using from_text factory method (app descriptions are text)
        idea = IdeaInspiration.from_text(
            title=app_title,
            description=description,
            text_content=app_info.get('review', ''),  # Use review text as content
            keywords=tags,
            metadata=metadata,
            source_id=app_info.get('appId', ''),
            source_url='',  # Not available in review data
            source_created_by=developer,
            source_created_at=app_info.get('date', '')
        )
        
        return idea

    def scrape_with_rss(self, category: str = 'games') -> List[IdeaInspiration]:
        """Alternative scraping method using Apple's RSS feeds.
        
        Apple provides RSS feeds for top apps that don't require authentication.
        This is a more reliable method for production use.
        
        Args:
            category: Category identifier
            
        Returns:
            List of IdeaInspiration objects
        """
        import requests
        
        apps_data = []
        
        # RSS feed URL for top free apps
        # Reference: https://rss.applemarketingtools.com/
        rss_url = f"https://rss.applemarketingtools.com/api/v2/{self.country}/apps/top-free/{self.max_apps}/{category}.json"
        
        try:
            response = requests.get(rss_url)
            response.raise_for_status()
            data = response.json()
            
            # Parse RSS feed data
            feed = data.get('feed', {})
            results = feed.get('results', [])
            
            for i, app_info in enumerate(results, 1):
                developer = app_info.get('artistName', 'Unknown Developer')
                app_title = app_info.get('name', 'Unknown App')
                tags = self.format_tags(['apple_app_store', 'app', 'rss', category, developer])
                
                # Build metadata with string values
                metadata = {
                    'app_id': app_info.get('id', ''),
                    'artist_id': app_info.get('artistId', ''),
                    'artist_url': app_info.get('artistUrl', ''),
                    'artwork_url': app_info.get('artworkUrl100', ''),
                    'bundle_id': app_info.get('bundleId', ''),
                    'content_advisory_rating': app_info.get('contentAdvisoryRating', ''),
                    'url': app_info.get('url', ''),
                    'category': category,
                    'category_rank': str(i),
                    'price': '0.0',  # Free apps
                    'currency': 'USD',
                    'country': self.country,
                    'platform': 'apple_app_store',
                }
                
                # Add genres if available
                genres = app_info.get('genres', [])
                if genres:
                    metadata['genres'] = ','.join([str(g.get('name', '')) for g in genres if isinstance(g, dict)])
                
                # Create IdeaInspiration using from_text factory method
                idea = IdeaInspiration.from_text(
                    title=app_title,
                    description=f"{app_title} by {developer} - Rank #{i} in {category} (Free Apps)",
                    text_content=app_info.get('description', ''),
                    keywords=tags,
                    metadata=metadata,
                    source_id=app_info.get('id', ''),
                    source_url=app_info.get('url', ''),
                    source_created_by=developer,
                    source_created_at=app_info.get('releaseDate', '')
                )
                apps_data.append(idea)
            
        except Exception as e:
            print(f"Error scraping RSS feed: {e}")
        
        return apps_data
