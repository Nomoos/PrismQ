"""Spotify API client for audio content integration."""

from typing import List, Optional, Dict
from datetime import datetime
import logging
import base64
import time
from Audio.src.clients.base_client import BaseAudioClient, AudioMetadata
from Audio.src.clients.utils import sanitize_metadata

logger = logging.getLogger(__name__)


class SpotifyClient(BaseAudioClient):
    """Client for Spotify Web API integration."""

    # API endpoints
    BASE_URL = "https://api.spotify.com/v1"
    AUTH_URL = "https://accounts.spotify.com/api/token"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        rate_limit_per_minute: int = 50,
        **kwargs,
    ) -> None:
        """
        Initialize Spotify client.

        Args:
            client_id: Spotify app client ID
            client_secret: Spotify app client secret
            rate_limit_per_minute: API rate limit (default 50/min)
            **kwargs: Additional arguments passed to BaseAudioClient
        """
        super().__init__(
            api_key=None,  # Spotify uses OAuth, not API key
            rate_limit_per_minute=rate_limit_per_minute,
            **kwargs,
        )

        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0

        # Authenticate on initialization
        self._authenticate()

        logger.info("SpotifyClient initialized and authenticated")

    def _authenticate(self) -> None:
        """Authenticate with Spotify using client credentials flow."""
        # Check if token is still valid
        if self._access_token and time.time() < self._token_expires_at:
            return

        # Prepare authentication
        auth_str = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_str.encode("ascii")
        auth_b64 = base64.b64encode(auth_bytes).decode("ascii")

        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {"grant_type": "client_credentials"}

        try:
            response = self._make_request(
                method="POST", url=self.AUTH_URL, headers=headers, data=data
            )

            token_data = response.json()
            self._access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)
            # Refresh 1 min early
            self._token_expires_at = time.time() + expires_in - 60

            logger.info("Spotify authentication successful")

        except Exception as e:
            logger.error(f"Spotify authentication failed: {e}")
            raise

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with current access token."""
        self._authenticate()  # Refresh if needed
        return {"Authorization": f"Bearer {self._access_token}"}

    def get_audio_metadata(self, audio_id: str) -> AudioMetadata:
        """
        Fetch metadata for a Spotify track or episode.

        Args:
            audio_id: Spotify track or episode ID

        Returns:
            AudioMetadata with normalized Spotify data
        """
        # Try as track first
        try:
            return self._get_track_metadata(audio_id)
        except Exception as e:
            logger.debug(f"Not a track, trying as episode: {e}")

        # Try as episode (podcast)
        try:
            return self._get_episode_metadata(audio_id)
        except Exception as e:
            logger.error(f"Failed to fetch Spotify metadata for {audio_id}: {e}")
            raise

    def _get_track_metadata(self, track_id: str) -> AudioMetadata:
        """Fetch metadata for a Spotify track."""
        url = f"{self.BASE_URL}/tracks/{track_id}"

        response = self._make_request(
            method="GET", url=url, headers=self._get_headers()
        )

        track = response.json()

        return AudioMetadata(
            title=track["name"],
            creator=", ".join(artist["name"] for artist in track["artists"]),
            duration_seconds=(
                track["duration_ms"] // 1000 if track.get("duration_ms") else None
            ),
            description=None,  # Tracks don't have descriptions
            published_at=None,  # Use album release date if available
            audio_url=track.get("preview_url"),  # 30-second preview
            thumbnail_url=(
                track["album"]["images"][0]["url"] if track["album"]["images"] else None
            ),
            genres=None,  # Would need separate artist lookup
            language=None,
            explicit=track.get("explicit", False),
            platform="spotify",
            platform_id=track["id"],
            metadata=sanitize_metadata(
                {
                    "album": track["album"]["name"],
                    "album_id": track["album"]["id"],
                    "artist_ids": [artist["id"] for artist in track["artists"]],
                    "popularity": track.get("popularity"),
                    "track_number": track.get("track_number"),
                    "external_urls": track.get("external_urls", {}).get("spotify"),
                }
            ),
        )

    def _get_episode_metadata(self, episode_id: str) -> AudioMetadata:
        """Fetch metadata for a Spotify podcast episode."""
        url = f"{self.BASE_URL}/episodes/{episode_id}"

        response = self._make_request(
            method="GET", url=url, headers=self._get_headers()
        )

        episode = response.json()

        # Parse published date
        published_at = None
        if episode.get("release_date"):
            try:
                published_at = datetime.fromisoformat(
                    episode["release_date"] + "T00:00:00Z"
                )
            except Exception:
                pass

        return AudioMetadata(
            title=episode["name"],
            creator=(episode["show"]["name"] if episode.get("show") else "Unknown"),
            duration_seconds=(
                episode["duration_ms"] // 1000 if episode.get("duration_ms") else None
            ),
            description=episode.get("description"),
            published_at=published_at,
            audio_url=episode.get("audio_preview_url"),
            thumbnail_url=(
                episode["images"][0]["url"] if episode.get("images") else None
            ),
            genres=None,
            language=episode.get("language"),
            explicit=episode.get("explicit", False),
            platform="spotify",
            platform_id=episode["id"],
            metadata=sanitize_metadata(
                {
                    "show_name": (
                        episode["show"]["name"] if episode.get("show") else None
                    ),
                    "show_id": (episode["show"]["id"] if episode.get("show") else None),
                    "external_urls": episode.get("external_urls", {}).get("spotify"),
                    "release_date": episode.get("release_date"),
                }
            ),
        )

    def search_audio(
        self, query: str, limit: int = 10, search_type: str = "track"
    ) -> List[AudioMetadata]:
        """
        Search Spotify for audio content.

        Args:
            query: Search query
            limit: Maximum results (1-50)
            search_type: Search type ('track', 'episode', or 'track,episode')

        Returns:
            List of AudioMetadata objects
        """
        url = f"{self.BASE_URL}/search"

        params = {"q": query, "type": search_type, "limit": min(limit, 50)}

        response = self._make_request(
            method="GET", url=url, headers=self._get_headers(), params=params
        )

        results = response.json()
        metadata_list = []

        # Process tracks
        if "tracks" in results:
            for track in results["tracks"]["items"]:
                try:
                    metadata = AudioMetadata(
                        title=track["name"],
                        creator=", ".join(
                            artist["name"] for artist in track["artists"]
                        ),
                        duration_seconds=(
                            track["duration_ms"] // 1000
                            if track.get("duration_ms")
                            else None
                        ),
                        thumbnail_url=(
                            track["album"]["images"][0]["url"]
                            if track["album"]["images"]
                            else None
                        ),
                        platform="spotify",
                        platform_id=track["id"],
                        explicit=track.get("explicit", False),
                        metadata={
                            "type": "track",
                            "popularity": track.get("popularity"),
                        },
                    )
                    metadata_list.append(metadata)
                except Exception as e:
                    logger.warning(f"Failed to parse track result: {e}")

        # Process episodes
        if "episodes" in results:
            for episode in results["episodes"]["items"]:
                try:
                    metadata = AudioMetadata(
                        title=episode["name"],
                        creator=(
                            episode["show"]["name"]
                            if episode.get("show")
                            else "Unknown"
                        ),
                        duration_seconds=(
                            episode["duration_ms"] // 1000
                            if episode.get("duration_ms")
                            else None
                        ),
                        description=episode.get("description"),
                        thumbnail_url=(
                            episode["images"][0]["url"]
                            if episode.get("images")
                            else None
                        ),
                        platform="spotify",
                        platform_id=episode["id"],
                        language=episode.get("language"),
                        explicit=episode.get("explicit", False),
                        metadata={"type": "episode"},
                    )
                    metadata_list.append(metadata)
                except Exception as e:
                    logger.warning(f"Failed to parse episode result: {e}")

        return metadata_list
