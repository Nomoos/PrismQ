# Signals Sources Implementation Guide

## Overview

This guide provides a template for implementing the remaining Signal sources based on the proven GoogleTrendsSource implementation.

## Implementation Status

### ✅ ALL SOURCES COMPLETED (13/13 - 100%)

All signal sources have been fully implemented with comprehensive functionality, tests, and documentation.

**Trends (2/2):**
- ✅ **GoogleTrendsSource** - Full implementation with tests, CLI, and documentation
- ✅ **TrendsFileSource** - Complete implementation

**Hashtags (2/2):**
- ✅ **TikTokHashtagSource** - Complete implementation
- ✅ **InstagramHashtagSource** - Complete implementation

**News (2/2):**
- ✅ **GoogleNewsSource** - Complete implementation
- ✅ **NewsApiSource** - Complete implementation

**Sounds (2/2):**
- ✅ **TikTokSoundsSource** - Complete implementation
- ✅ **InstagramAudioTrendsSource** - Complete implementation

**Memes (2/2):**
- ✅ **MemeTrackerSource** - Complete implementation
- ✅ **KnowYourMemeSource** - Complete implementation

**Challenges (1/1):**
- ✅ **SocialChallengeSource** - Complete implementation

**Locations (1/1):**
- ✅ **GeoLocalTrendsSource** - Complete implementation

**Date Completed:** 2025-10-30

Each source includes:
- Complete directory structure with all required files
- Plugin implementation with stub mode support
- Comprehensive test suite (3+ test files, >80% coverage target)
- CLI interface (scrape, list, stats, export, clear commands)
- Full documentation (README.md with usage examples)
- Configuration files (pyproject.toml, requirements.txt, .env.example)

## Implementation Template

Each Signal source should follow this proven structure:

```
SourceName/
├── src/
│   ├── __init__.py
│   ├── cli.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── metrics.py
│   │   └── signal_processor.py
│   └── plugins/
│       ├── __init__.py
│       └── [source_name]_plugin.py
├── tests/
│   ├── __init__.py
│   ├── test_database.py
│   ├── test_[source_name]_plugin.py
│   └── test_metrics.py
├── pyproject.toml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Step-by-Step Implementation Guide

### Step 1: Copy Template
```bash
# Copy the GoogleTrends implementation as a template
cp -r Sources/Signals/Trends/GoogleTrends Sources/Signals/[Category]/[SourceName]
cd Sources/Signals/[Category]/[SourceName]
```

### Step 2: Update Configuration Files

#### pyproject.toml
- Update `name` to match new source
- Update `description`
- Update `keywords`
- Add source-specific dependencies

#### requirements.txt
- Add source-specific libraries (e.g., TikTokApi, newsapi-python, etc.)

#### .env.example
- Update configuration variables for the specific source
- Update region/language settings as needed

### Step 3: Implement Core Modules

#### src/core/config.py
- Keep the same structure
- Update configuration variable names to match the source
- Add source-specific configuration options

#### src/core/database.py
- Can reuse as-is (it's generic for signals)
- Optionally add source-specific query methods

#### src/core/metrics.py
- Update `from_[source_name]` classmethod
- Implement source-specific metric calculations
- Maintain universal metric mappings

#### src/core/signal_processor.py
- Implement `process_[source_name]_signal` method
- Map source-specific data to unified signal format

### Step 4: Implement Plugin

#### src/plugins/[source_name]_plugin.py

Template:
```python
"""[Source Name] plugin for scraping [signal type]."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
# Import source-specific library here
from . import SignalPlugin


class [SourceName]Plugin(SignalPlugin):
    """Plugin for scraping signals from [Source Name]."""
    
    def __init__(self, config):
        """Initialize [Source Name] plugin."""
        super().__init__(config)
        # Initialize source-specific API/library
        self.api = None  # Initialize your API client here
    
    def get_source_name(self) -> str:
        """Get the name of this source."""
        return "[source_name]"
    
    def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        """Scrape signals from [Source Name]."""
        signals = []
        
        try:
            # Implement scraping logic here
            # 1. Fetch data from API
            # 2. Process each item
            # 3. Create signal dictionaries
            # 4. Return signals list
            pass
        except Exception as e:
            print(f"Error scraping [Source Name]: {e}")
        
        return signals
    
    def _create_signal(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a signal dictionary from item data."""
        return {
            'source_id': f"{item_data['id']}_{datetime.now(timezone.utc).strftime('%Y%m%d%H')}",
            'signal_type': '[signal_type]',  # trend, hashtag, meme, etc.
            'name': item_data['name'],
            'description': item_data.get('description', ''),
            'tags': ['tag1', 'tag2'],
            'metrics': {
                'volume': item_data.get('volume', 0),
                'velocity': 0.0,
                'acceleration': 0.0,
                'geographic_spread': []
            },
            'temporal': {
                'first_seen': datetime.now(timezone.utc).isoformat() + 'Z',
                'peak_time': None,
                'current_status': 'rising'
            }
        }
```

### Step 5: Update CLI

#### src/cli.py
- Update command descriptions
- Update option names/descriptions as needed
- Keep the same command structure (scrape, list, stats, export, clear)

### Step 6: Write Tests

#### tests/test_[source_name]_plugin.py
- Test source name
- Test scraping returns list
- Test signal structure
- Test error handling
- Mock the API calls

#### tests/test_database.py
- Can reuse from template (generic)

#### tests/test_metrics.py
- Test `from_[source_name]` method
- Test metric calculations specific to source

### Step 7: Update README
- Update module name and description
- Update usage examples
- Update configuration options
- Document source-specific features

### Step 8: Run Tests
```bash
pip install -e .
pip install pytest pytest-cov
python -m pytest tests/ -v --cov=src
```

## Common Patterns

### API Authentication
Many sources require API keys. Add to .env.example:
```bash
[SOURCE]_API_KEY=your_api_key_here
```

Load in config.py:
```python
self.api_key = self._get_or_default("[SOURCE]_API_KEY", "")
```

### Rate Limiting
Implement delays between API calls:
```python
import time
time.sleep(self.config.retry_delay_seconds)
```

### Error Handling
Always wrap API calls in try/except:
```python
try:
    data = self.api.get_data()
except Exception as e:
    print(f"Error: {e}")
    return []
```

### Signal Type Mapping
- `'trend'` - Search trends, rising queries
- `'hashtag'` - Hashtag usage and trends
- `'meme'` - Viral memes and formats
- `'challenge'` - Social media challenges
- `'sound'` - Trending audio/music
- `'location'` - Geographic trends
- `'news'` - News and events

## Source-Specific Notes

### TikTokHashtagSource
- Library: `TikTokApi`
- Challenges: Requires async/await patterns
- Data: Hashtag views, usage count, related hashtags

### GoogleNewsSource
- Library: `feedparser` or `gnews`
- Data: Headlines, article URLs, publication times

### NewsApiSource
- Library: `newsapi-python`
- Requires: API key
- Data: Articles, sources, categories

### InstagramHashtagSource
- Library: `instagram-private-api` or `instaloader`
- Challenges: Authentication required
- Data: Post counts, engagement rates

### MemeTrackerSource
- May require web scraping (BeautifulSoup)
- Track meme propagation across platforms

### KnowYourMemeSource
- Web scraping with `requests` + `BeautifulSoup`
- Parse meme entries, origin, spread

## Quality Checklist

For each implementation:
- [ ] Follows SOLID principles
- [ ] Has comprehensive tests (>80% coverage)
- [ ] Has CLI with all standard commands
- [ ] Has proper documentation
- [ ] Uses unified signal format
- [ ] Handles errors gracefully
- [ ] Implements deduplication
- [ ] Has .env.example with all config options
- [ ] Passes all tests
- [ ] No security vulnerabilities in dependencies

## Getting Help

Reference implementations:
- **GoogleTrendsSource**: `Sources/Signals/Trends/GoogleTrends/`
- **YouTube Shorts**: `Sources/Content/Shorts/YouTube/` (different category but similar architecture)

For questions or issues, consult the SOLID principles documentation in `_meta/docs/SOLID_PRINCIPLES.md`.
