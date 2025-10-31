"""Genius API plugin for scraping lyric snippets."""

from typing import List, Dict, Any, Optional
from . import SourcePlugin, IdeaInspiration
import re


class GeniusPlugin(SourcePlugin):
    """Plugin for scraping lyric snippets from Genius API."""

    def __init__(self, config):
        """Initialize Genius plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        
        if not config.genius_api_key:
            raise ValueError("Genius API key not configured")
        
        try:
            import lyricsgenius
            self.genius = lyricsgenius.Genius(
                config.genius_api_key,
                timeout=15,
                retries=3
            )
            # Reduce verbosity
            self.genius.verbose = False
            self.genius.remove_section_headers = True
        except ImportError:
            raise ValueError("lyricsgenius package not installed. Install with: pip install lyricsgenius")

    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "genius"

    def scrape(self, search_query: Optional[str] = None, max_results: Optional[int] = None) -> List[IdeaInspiration]:
        """Scrape lyric snippets from Genius.
        
        Args:
            search_query: Optional search query (default: trending songs)
            max_results: Maximum number of results (default: from config)
            
        Returns:
            List of IdeaInspiration objects
        """
        resources = []
        
        try:
            max_results = max_results or self.config.genius_max_results
            
            # If no search query, use chart songs
            if not search_query:
                search_query = "trending"
            
            # Search for songs
            search_results = self.genius.search_songs(search_query, per_page=min(max_results, 50))
            
            if not search_results or 'hits' not in search_results:
                return resources
            
            hits = search_results['hits'][:max_results]
            
            for hit in hits:
                try:
                    result = hit.get('result', {})
                    song_id = result.get('id')
                    
                    if not song_id:
                        continue
                    
                    # Get song details
                    song = self.genius.song(song_id)
                    
                    if not song:
                        continue
                    
                    # Extract lyric snippet (first verse or chorus)
                    lyrics = song.get('lyrics', '')
                    snippet = self._extract_snippet(lyrics)
                    
                    # Get artist info
                    artist = result.get('primary_artist', {})
                    artist_name = artist.get('name', 'Unknown')
                    
                    # Extract tags
                    tags = self._extract_tags(result)
                    
                    # Build metadata with string values
                    metadata = {
                        'song_id': str(song_id),
                        'artist_id': str(artist.get('id', '')),
                        'artist_name': artist_name,
                        'url': result.get('url', ''),
                        'pageviews': str(result.get('stats', {}).get('pageviews', 0)),
                        'language': result.get('language', 'en'),
                    }
                    
                    # Create IdeaInspiration using from_text factory method (lyrics are text)
                    idea = IdeaInspiration.from_text(
                        title=f"{result.get('title', 'Unknown')} - {artist_name}",
                        description=f"Lyric snippet from {artist_name}",
                        text_content=snippet,
                        keywords=tags,
                        metadata=metadata,
                        source_id=str(song_id),
                        source_url=result.get('url', ''),
                        source_created_by=artist_name,
                        source_created_at=''  # Genius API doesn't provide release date in search
                    )
                    resources.append(idea)
                    
                except Exception as e:
                    print(f"Error processing song {hit}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping Genius: {e}")
        
        return resources

    def _extract_snippet(self, lyrics: str, max_lines: int = 8) -> str:
        """Extract a meaningful snippet from full lyrics.
        
        Args:
            lyrics: Full lyrics text
            max_lines: Maximum number of lines in snippet
            
        Returns:
            Lyric snippet
        """
        if not lyrics:
            return ""
        
        # Split into lines and remove empty lines
        lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
        
        # Look for chorus markers
        chorus_start = -1
        for i, line in enumerate(lines):
            if '[chorus' in line.lower() or '[hook' in line.lower():
                chorus_start = i + 1
                break
        
        # If chorus found, extract from there
        if chorus_start > 0 and chorus_start < len(lines):
            snippet_lines = []
            for i in range(chorus_start, len(lines)):
                line = lines[i]
                # Stop at next section marker
                if line.startswith('[') and line.endswith(']'):
                    break
                snippet_lines.append(line)
                if len(snippet_lines) >= max_lines:
                    break
            
            if snippet_lines:
                return '\n'.join(snippet_lines)
        
        # Otherwise, take first few lines (after removing section headers)
        snippet_lines = []
        for line in lines:
            # Skip section headers
            if line.startswith('[') and line.endswith(']'):
                continue
            snippet_lines.append(line)
            if len(snippet_lines) >= max_lines:
                break
        
        return '\n'.join(snippet_lines)

    def _extract_tags(self, result: Dict[str, Any]) -> List[str]:
        """Extract tags from Genius song result.
        
        Args:
            result: Song result from Genius API
            
        Returns:
            List of tag strings
        """
        tags = ['lyrics', 'genius']
        
        # Add artist name as tag
        artist = result.get('primary_artist', {})
        if artist and artist.get('name'):
            tags.append(artist['name'].lower().replace(' ', '_'))
        
        # Add language if available
        if result.get('language'):
            tags.append(result['language'])
        
        return tags

    def get_song_by_title(self, title: str, artist: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a specific song by title and optionally artist.
        
        Args:
            title: Song title
            artist: Optional artist name
            
        Returns:
            Song resource dictionary or None
        """
        try:
            # Search for the song
            search_query = f"{title} {artist}" if artist else title
            song = self.genius.search_song(title, artist)
            
            if not song:
                return None
            
            # Extract snippet
            lyrics = song.lyrics if hasattr(song, 'lyrics') else ""
            snippet = self._extract_snippet(lyrics)
            
            resource = {
                'source_id': str(song.id),
                'title': f"{song.title} - {song.artist}",
                'content': snippet,
                'tags': f"lyrics,genius,{song.artist.lower().replace(' ', '_')}",
                'metrics': {
                    'id': song.id,
                    'title': song.title,
                    'primary_artist': {'name': song.artist},
                    'url': song.url,
                    'stats': {
                        'pageviews': getattr(song, 'stats', {}).get('pageviews', 0) if hasattr(song, 'stats') else 0
                    }
                }
            }
            
            return resource
            
        except Exception as e:
            print(f"Error getting song '{title}': {e}")
            return None
