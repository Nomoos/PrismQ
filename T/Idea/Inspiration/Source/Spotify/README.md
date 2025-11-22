# Spotify Audio Source

Integration module for Spotify music and podcast content via Spotify Web API.

## Overview

This module provides access to Spotify's extensive music catalog and podcast library through the official Spotify Web API.

**Status**: Foundation Complete ✅  
**API**: Spotify Web API v1  
**Authentication**: OAuth 2.0 Client Credentials

## Features

- **Track Search** - Search for songs, albums, artists
- **Playlist Access** - Get playlist contents and metadata
- **Podcast Support** - Access podcast shows and episodes
- **Audio Features** - Get audio analysis and features
- **Rate Limiting** - Built-in rate limiting (50 req/min)
- **OAuth Handling** - Automatic token refresh

## Quick Start

```python
from Spotify.src import SpotifyClient

# Initialize client
client = SpotifyClient(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Search for tracks
results = client.search_audio("Python programming", limit=10)
for track in results:
    print(f"{track.title} by {track.creator}")

# Get track metadata
metadata = client.get_audio_metadata("track_id")
print(f"Duration: {metadata.duration_seconds}s")
```

## Configuration

Set environment variables or pass directly:

```bash
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

## API Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Copy Client ID and Client Secret
4. Set redirect URI (for web apps)

## Rate Limits

- **Free Tier**: 180 requests per minute (burst)
- **Sustained**: 50-60 requests per minute recommended
- **Auto-retry**: Built-in handling for 429 errors

## Dependencies

- `requests>=2.31.0` - HTTP client
- `python-dotenv>=1.0.0` - Environment variables

## Testing

```bash
cd Source/Spotify
pytest _meta/tests/
```

## Documentation

- [Spotify Web API Documentation](https://developer.spotify.com/documentation/web-api)
- [Audio Module Documentation](../README.md)

## License

Part of PrismQ.T.Idea.Inspiration project - Proprietary
