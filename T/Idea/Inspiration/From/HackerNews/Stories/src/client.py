"""HackerNews API client.

Provides a clean interface to the HackerNews Firebase API.
Follows SOLID principles with single responsibility for API communication.
"""

import logging
import time
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class HackerNewsClient:
    """Client for HackerNews API.

    Follows SOLID principles:
    - SRP: Only handles HackerNews API communication
    - OCP: Can be extended for new endpoints
    - DIP: Depends on abstractions (requests library)

    HackerNews API Documentation: https://github.com/HackerNews/API
    """

    API_BASE = "https://hacker-news.firebaseio.com/v0"

    def __init__(self, timeout: int = 10, rate_limit_delay: float = 0.1):
        """Initialize HackerNews API client.

        Args:
            timeout: Request timeout in seconds (default: 10)
            rate_limit_delay: Delay between requests in seconds (default: 0.1)
        """
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "PrismQ.IdeaInspiration/1.0"})

    def get_top_stories(self, limit: Optional[int] = None) -> List[int]:
        """Fetch top story IDs.

        Args:
            limit: Maximum number of story IDs to return

        Returns:
            List of story IDs
        """
        return self._get_story_ids("topstories", limit)

    def get_best_stories(self, limit: Optional[int] = None) -> List[int]:
        """Fetch best story IDs.

        Args:
            limit: Maximum number of story IDs to return

        Returns:
            List of story IDs
        """
        return self._get_story_ids("beststories", limit)

    def get_new_stories(self, limit: Optional[int] = None) -> List[int]:
        """Fetch new story IDs.

        Args:
            limit: Maximum number of story IDs to return

        Returns:
            List of story IDs
        """
        return self._get_story_ids("newstories", limit)

    def get_ask_stories(self, limit: Optional[int] = None) -> List[int]:
        """Fetch Ask HN story IDs.

        Args:
            limit: Maximum number of story IDs to return

        Returns:
            List of story IDs
        """
        return self._get_story_ids("askstories", limit)

    def get_show_stories(self, limit: Optional[int] = None) -> List[int]:
        """Fetch Show HN story IDs.

        Args:
            limit: Maximum number of story IDs to return

        Returns:
            List of story IDs
        """
        return self._get_story_ids("showstories", limit)

    def get_job_stories(self, limit: Optional[int] = None) -> List[int]:
        """Fetch job story IDs.

        Args:
            limit: Maximum number of story IDs to return

        Returns:
            List of story IDs
        """
        return self._get_story_ids("jobstories", limit)

    def _get_story_ids(self, endpoint: str, limit: Optional[int]) -> List[int]:
        """Fetch story IDs from endpoint.

        Args:
            endpoint: API endpoint name (e.g., 'topstories')
            limit: Optional limit on number of IDs

        Returns:
            List of story IDs

        Raises:
            requests.RequestException: If API request fails
        """
        url = f"{self.API_BASE}/{endpoint}.json"

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            story_ids = response.json()

            if limit:
                story_ids = story_ids[:limit]

            logger.debug(f"Fetched {len(story_ids)} story IDs from {endpoint}")

            # Rate limiting
            time.sleep(self.rate_limit_delay)

            return story_ids

        except Exception as e:
            logger.error(f"Failed to fetch {endpoint}: {e}")
            raise

    def get_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Fetch item (story, comment, etc.) by ID.

        Args:
            item_id: Item ID

        Returns:
            Item data dictionary or None if not found
        """
        url = f"{self.API_BASE}/item/{item_id}.json"

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # Rate limiting
            time.sleep(self.rate_limit_delay)

            return response.json()

        except Exception as e:
            logger.warning(f"Failed to fetch item {item_id}: {e}")
            return None

    def get_items(self, item_ids: List[int]) -> List[Dict[str, Any]]:
        """Fetch multiple items by IDs.

        Args:
            item_ids: List of item IDs

        Returns:
            List of item data dictionaries (skips items that fail to fetch)
        """
        items = []
        for item_id in item_ids:
            item = self.get_item(item_id)
            if item:
                items.append(item)
        return items

    def get_max_item_id(self) -> int:
        """Get maximum item ID.

        Returns:
            Maximum item ID

        Raises:
            requests.RequestException: If API request fails
        """
        url = f"{self.API_BASE}/maxitem.json"

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch max item ID: {e}")
            raise

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Fetch user profile by username.

        Args:
            username: HackerNews username

        Returns:
            User data dictionary or None if not found
        """
        url = f"{self.API_BASE}/user/{username}.json"

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # Rate limiting
            time.sleep(self.rate_limit_delay)

            return response.json()

        except Exception as e:
            logger.warning(f"Failed to fetch user {username}: {e}")
            return None

    def close(self):
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


__all__ = ["HackerNewsClient"]
