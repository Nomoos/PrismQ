# Issue 503: Implement Builder Module for Source Data Transformation

**Type**: Feature Enhancement
**Priority**: High
**Status**: New
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

## Description

Create a dedicated Builder module (`PrismQ.IdeaInspiration.Builder`) to handle platform-specific transformations from raw source data (YouTube, Reddit, Genius, etc.) into clean IdeaInspiration domain objects. This centralizes transformation logic and separates concerns between data collection (Sources) and data modeling (Builder).

## Current State Analysis

Currently, Source plugins directly create IdeaInspiration objects:
- ✅ Works for simple transformations
- ❌ Transformation logic scattered across plugins
- ❌ Duplicate code for similar transformations
- ❌ Hard to test transformation logic separately
- ❌ No centralized metadata enrichment
- ❌ Inconsistent handling of source-specific fields

**Example from LyricSnippets:**
```python
# Transformation logic in plugin
idea = IdeaInspiration.from_text(
    title=f"{result.get('title', 'Unknown')} - {artist_name}",
    description=f"Lyric snippet from {artist_name}",
    text_content=snippet,
    keywords=tags,
    metadata=metadata,
    source_id=str(song_id),
    # ... direct construction
)
```

## Goals

1. **Centralized Transformation Logic**
   - Single place for source-to-IdeaInspiration transformations
   - Reusable builder classes for each platform
   - Consistent transformation patterns

2. **Separation of Concerns**
   - Sources focus on data collection (API calls, scraping)
   - Builders focus on data transformation
   - Clean architecture with clear boundaries

3. **Enhanced Metadata Processing**
   - Platform-specific metadata extraction
   - Metadata enrichment and normalization
   - Contextual category score calculation
   - Automatic tag generation

4. **Testability**
   - Test transformations without API calls
   - Mock builders for Source testing
   - Comprehensive transformation test coverage

5. **Extensibility**
   - Easy to add new platform builders
   - Configurable transformation pipelines
   - Support for custom transformation rules

## Proposed Architecture

### Module Structure

```
PrismQ.IdeaInspiration/
└── Builder/
    ├── src/
    │   ├── __init__.py
    │   ├── base_builder.py          # Abstract builder interface
    │   ├── builders/
    │   │   ├── __init__.py
    │   │   ├── youtube_builder.py   # YouTube transformations
    │   │   ├── reddit_builder.py    # Reddit transformations
    │   │   ├── genius_builder.py    # Genius/lyrics transformations
    │   │   ├── twitter_builder.py   # Twitter/X transformations
    │   │   └── generic_builder.py   # Generic/default transformations
    │   ├── enrichers/
    │   │   ├── __init__.py
    │   │   ├── metadata_enricher.py # Metadata enhancement
    │   │   ├── tag_generator.py     # Automatic tag generation
    │   │   └── category_scorer.py   # Contextual score calculation
    │   └── validators/
    │       ├── __init__.py
    │       └── data_validator.py    # Input validation
    ├── tests/
    │   ├── test_youtube_builder.py
    │   ├── test_reddit_builder.py
    │   └── test_enrichers.py
    ├── README.md
    ├── pyproject.toml
    └── requirements.txt
```

### Base Builder Interface

```python
# src/base_builder.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from idea_inspiration import IdeaInspiration

class BaseBuilder(ABC):
    """Abstract base class for source data builders."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize builder with optional configuration."""
        self.config = config or {}
    
    @abstractmethod
    def build(self, source_data: Dict[str, Any]) -> IdeaInspiration:
        """Transform source data into IdeaInspiration object.
        
        Args:
            source_data: Raw data from source platform
            
        Returns:
            IdeaInspiration domain object
        """
        pass
    
    def build_batch(self, source_data_list: List[Dict[str, Any]]) -> List[IdeaInspiration]:
        """Transform multiple source data items.
        
        Args:
            source_data_list: List of raw data from source platform
            
        Returns:
            List of IdeaInspiration domain objects
        """
        return [self.build(data) for data in source_data_list]
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Get the platform name this builder handles."""
        pass
    
    def validate_input(self, source_data: Dict[str, Any]) -> bool:
        """Validate source data before transformation.
        
        Args:
            source_data: Raw data to validate
            
        Returns:
            True if valid, False otherwise
        """
        return True  # Override in subclasses
```

### YouTube Builder Example

```python
# src/builders/youtube_builder.py
from ..base_builder import BaseBuilder
from idea_inspiration import IdeaInspiration

class YouTubeBuilder(BaseBuilder):
    """Builder for transforming YouTube data to IdeaInspiration."""
    
    def get_platform_name(self) -> str:
        return "youtube"
    
    def validate_input(self, source_data: Dict[str, Any]) -> bool:
        """Validate YouTube data has required fields."""
        required = ['id', 'snippet']
        return all(key in source_data for key in required)
    
    def build(self, source_data: Dict[str, Any]) -> IdeaInspiration:
        """Transform YouTube video data to IdeaInspiration.
        
        Expected source_data structure:
        {
            'id': 'video_id',
            'snippet': {
                'title': 'Video Title',
                'description': 'Video Description',
                'channelTitle': 'Channel Name',
                'publishedAt': '2025-01-15T12:00:00Z',
                'tags': ['tag1', 'tag2']
            },
            'statistics': {
                'viewCount': '1000000',
                'likeCount': '50000',
                'commentCount': '2000'
            },
            'contentDetails': {
                'duration': 'PT10M30S'
            },
            'transcript': 'Video transcript text...'  # Optional
        }
        """
        if not self.validate_input(source_data):
            raise ValueError("Invalid YouTube data structure")
        
        snippet = source_data['snippet']
        stats = source_data.get('statistics', {})
        
        # Extract and normalize metadata
        metadata = {
            'video_id': source_data['id'],
            'channel_title': snippet.get('channelTitle', ''),
            'channel_id': snippet.get('channelId', ''),
            'view_count': str(stats.get('viewCount', '0')),
            'like_count': str(stats.get('likeCount', '0')),
            'comment_count': str(stats.get('commentCount', '0')),
            'duration': source_data.get('contentDetails', {}).get('duration', ''),
            'published_at': snippet.get('publishedAt', ''),
            'platform': 'youtube'
        }
        
        # Generate keywords from tags + automatic extraction
        keywords = snippet.get('tags', [])[:10]  # Limit to 10 tags
        
        # Use transcript if available, otherwise description
        content = source_data.get('transcript', '') or snippet.get('description', '')
        
        # Build IdeaInspiration
        return IdeaInspiration.from_video(
            title=snippet.get('title', 'Untitled'),
            description=snippet.get('description', '')[:500],  # First 500 chars
            subtitle_text=content,
            keywords=keywords,
            metadata=metadata,
            source_id=source_data['id'],
            source_url=f"https://www.youtube.com/watch?v={source_data['id']}",
            source_created_by=snippet.get('channelTitle', ''),
            source_created_at=snippet.get('publishedAt', '')
        )
```

### Genius Builder Example

```python
# src/builders/genius_builder.py
class GeniusBuilder(BaseBuilder):
    """Builder for transforming Genius lyrics data to IdeaInspiration."""
    
    def get_platform_name(self) -> str:
        return "genius"
    
    def build(self, source_data: Dict[str, Any]) -> IdeaInspiration:
        """Transform Genius song data to IdeaInspiration.
        
        Expected source_data structure:
        {
            'id': 12345,
            'title': 'Song Title',
            'primary_artist': {
                'name': 'Artist Name',
                'id': 678
            },
            'lyrics': 'Full lyrics text...',
            'url': 'https://genius.com/...',
            'stats': {
                'pageviews': 1000000,
                'hot': 500
            },
            'language': 'en'
        }
        """
        artist = source_data.get('primary_artist', {})
        artist_name = artist.get('name', 'Unknown')
        
        # Extract lyric snippet (first verse or chorus)
        lyrics = source_data.get('lyrics', '')
        snippet = self._extract_snippet(lyrics)
        
        # Build metadata
        metadata = {
            'song_id': str(source_data['id']),
            'artist_id': str(artist.get('id', '')),
            'artist_name': artist_name,
            'pageviews': str(source_data.get('stats', {}).get('pageviews', 0)),
            'language': source_data.get('language', 'en'),
            'platform': 'genius'
        }
        
        # Generate tags
        keywords = ['lyrics', 'genius', artist_name.lower().replace(' ', '_')]
        if source_data.get('language'):
            keywords.append(source_data['language'])
        
        return IdeaInspiration.from_text(
            title=f"{source_data.get('title', 'Unknown')} - {artist_name}",
            description=f"Lyric snippet from {artist_name}",
            text_content=snippet,
            keywords=keywords,
            metadata=metadata,
            source_id=str(source_data['id']),
            source_url=source_data.get('url', ''),
            source_created_by=artist_name
        )
    
    def _extract_snippet(self, lyrics: str, max_lines: int = 8) -> str:
        """Extract meaningful snippet from full lyrics."""
        # Snippet extraction logic
        # ... (move from plugin to builder)
```

### Metadata Enricher

```python
# src/enrichers/metadata_enricher.py
class MetadataEnricher:
    """Enriches IdeaInspiration metadata with additional context."""
    
    def enrich(self, idea: IdeaInspiration) -> IdeaInspiration:
        """Add enriched metadata to IdeaInspiration."""
        # Add computed fields
        enriched_metadata = idea.metadata.copy()
        
        # Add text statistics
        enriched_metadata['word_count'] = str(len(idea.content.split()))
        enriched_metadata['char_count'] = str(len(idea.content))
        
        # Add timestamp
        if not idea.metadata.get('enriched_at'):
            enriched_metadata['enriched_at'] = datetime.utcnow().isoformat()
        
        # Return new IdeaInspiration with enriched metadata
        return IdeaInspiration.from_dict({
            **idea.to_dict(),
            'metadata': enriched_metadata
        })
```

## Integration with Sources

### Before (Plugin directly creates IdeaInspiration):
```python
# In plugin
class GeniusPlugin:
    def scrape(self) -> List[IdeaInspiration]:
        results = self.genius.search()
        ideas = []
        for result in results:
            # Transformation logic in plugin
            idea = IdeaInspiration.from_text(...)
            ideas.append(idea)
        return ideas
```

### After (Plugin uses Builder):
```python
# In plugin
from Builder.src.builders.genius_builder import GeniusBuilder

class GeniusPlugin:
    def __init__(self, config):
        self.config = config
        self.builder = GeniusBuilder()  # Inject builder
    
    def scrape(self) -> List[IdeaInspiration]:
        results = self.genius.search()  # Get raw data
        
        # Builder handles transformation
        ideas = self.builder.build_batch(results)
        return ideas
```

## Implementation Steps

1. **Phase 1: Core Infrastructure** (Week 1)
   - Create Builder module structure
   - Implement BaseBuilder interface
   - Add validation framework

2. **Phase 2: Platform Builders** (Week 2-3)
   - Implement YouTubeBuilder
   - Implement GeniusBuilder
   - Implement RedditBuilder
   - Implement TwitterBuilder

3. **Phase 3: Enrichers** (Week 3)
   - Metadata enricher
   - Tag generator
   - Category scorer

4. **Phase 4: Integration** (Week 4)
   - Migrate LyricSnippets to use Builder
   - Update other Source plugins
   - Ensure backward compatibility

5. **Phase 5: Testing** (Week 4-5)
   - Unit tests for each builder
   - Integration tests with Sources
   - Validation tests

6. **Phase 6: Documentation** (Week 5)
   - Builder usage guide
   - Platform-specific transformation docs
   - Migration guide for existing sources

## Benefits

1. **Separation of Concerns**
   - Sources: Data collection
   - Builders: Data transformation
   - Model: Data representation

2. **Code Reuse**
   - Centralized transformation logic
   - Shared enrichment utilities
   - Consistent patterns

3. **Testability**
   - Test transformations independently
   - Mock builders easily
   - Better test coverage

4. **Maintainability**
   - Single place to update transformation logic
   - Easier to add new platforms
   - Clearer code organization

5. **Quality**
   - Consistent data quality
   - Automated enrichment
   - Input validation

## Related Issues

- Issue #500: Repository Pattern (data access layer)
- Model module: IdeaInspiration (domain model)
- Sources modules: Data collection

## Success Criteria

- [ ] Builder module structure created
- [ ] At least 4 platform builders implemented
- [ ] Metadata enricher working
- [ ] 2+ Source modules migrated to use Builder
- [ ] Comprehensive test coverage (>90%)
- [ ] Documentation complete
- [ ] No breaking changes to existing code

## Estimated Effort

5 weeks (1 developer)

## Best Practices References

Based on research:
- Builder pattern for complex object construction
- ETL pattern: Extract (Sources), Transform (Builder), Load (Repository)
- Domain-Driven Design: Separate domain from infrastructure
- Clean Architecture: Dependencies point inward

## Notes

The Builder module mentioned in Model/README.md is currently aspirational. This issue proposes its actual implementation to centralize and improve source data transformation logic.
