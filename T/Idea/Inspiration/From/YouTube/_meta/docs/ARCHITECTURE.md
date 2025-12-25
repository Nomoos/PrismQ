# YouTube Shorts Module - Architecture

**Platform Focus**: Windows 10/11 with NVIDIA RTX 5090  
**Last Updated**: 2025-11-04

## Overview

The YouTube Shorts Source module is designed following SOLID principles to provide a maintainable, extensible scraping solution optimized for Windows platforms. The architecture supports multiple scraping strategies (trending, channel, keyword) through a plugin-based system.

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│ YouTube Shorts Source Module (Windows Optimized)                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Plugin Layer (Scraping Strategies)                           │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │                                                              │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐           │  │
│  │  │ Trending   │  │ Channel    │  │ Search     │           │  │
│  │  │ Plugin     │  │ Plugin     │  │ Plugin     │           │  │
│  │  │            │  │            │  │ (Issue     │           │  │
│  │  │ (Trending  │  │ (yt-dlp    │  │  #300)     │           │  │
│  │  │  page)     │  │  channel)  │  │            │           │  │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘           │  │
│  │        │                │                │                  │  │
│  │        └────────────────┴────────────────┘                 │  │
│  │                         │                                   │  │
│  │                 ┌───────▼────────┐                         │  │
│  │                 │ SourcePlugin   │ (Abstract Base)         │  │
│  │                 │ Interface      │                         │  │
│  │                 └───────┬────────┘                         │  │
│  └─────────────────────────┼──────────────────────────────────┘  │
│                            │                                      │
│  ┌─────────────────────────▼──────────────────────────────────┐  │
│  │ Core Layer (Business Logic - SOLID Compliant)              │  │
│  ├──────────────────────────────────────────────────────────┬─┤  │
│  │                                                            │  │
│  │  ┌──────────────┐  ┌───────────────┐  ┌───────────────┐ │  │
│  │  │ Config       │  │ IdeaProcessor │  │ Universal     │ │  │
│  │  │              │  │               │  │ Metrics       │ │  │
│  │  │ (.env)       │  │ (Transform)   │  │ (Calculate)   │ │  │
│  │  └──────┬───────┘  └───────┬───────┘  └───────┬───────┘ │  │
│  │         │                   │                   │          │  │
│  └─────────┼───────────────────┼───────────────────┼──────────┘  │
│            │                   │                   │             │
│  ┌─────────▼───────────────────▼───────────────────▼──────────┐  │
│  │ Data Layer (Persistence)                                   │  │
│  ├────────────────────────────────────────────────────────────┤  │
│  │                                                            │  │
│  │  ┌──────────────┐                                         │  │
│  │  │ Database     │                                         │  │
│  │  │ (SQLite)     │                                         │  │
│  │  │              │                                         │  │
│  │  │ Windows Path:│                                         │  │
│  │  │ .\youtube_   │                                         │  │
│  │  │ shorts.db    │                                         │  │
│  │  └──────────────┘                                         │  │
│  │                                                            │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ CLI Interface (Click Framework)                          │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │                                                           │   │
│  │  Commands: run, scrape-channel, scrape-trending,         │   │
│  │           scrape-keyword, stats, export, process          │   │
│  │                                                           │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

## SOLID Principles Implementation

### Single Responsibility Principle (SRP)

Each class has one clear responsibility:

#### Config (`src/core/config.py`)
**Responsibility**: Load and manage configuration from .env files

```python
class Config:
    """Manages module configuration from .env files (Windows compatible)"""
    
    def __init__(self, env_file: str = ".env"):
        # Windows path handling
        from pathlib import Path
        env_path = Path(env_file).resolve()
        
        from dotenv import load_dotenv
        load_dotenv(env_path)
        
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.database_path = os.getenv('DATABASE_PATH', './youtube_shorts.db')
        self.max_results = int(os.getenv('YOUTUBE_MAX_RESULTS', '50'))
```

**Single Responsibility**: Configuration loading and environment variable management only.

#### Database (`src/core/database.py`)
**Responsibility**: Handle database operations and persistence

```python
class Database:
    """Manages SQLite database operations (Windows file paths)"""
    
    def __init__(self, db_path: str):
        from pathlib import Path
        self.db_path = Path(db_path).resolve()  # Windows absolute path
        self._ensure_db_exists()
    
    def insert_idea(self, idea: dict) -> None:
        """Insert single IdeaInspiration record"""
        pass
    
    def get_ideas(self, limit: int = 100) -> list:
        """Retrieve IdeaInspiration records"""
        pass
```

**Single Responsibility**: Database CRUD operations only.

#### UniversalMetrics (`src/core/metrics.py`)
**Responsibility**: Calculate and normalize platform metrics

```python
class UniversalMetrics:
    """Calculate universal engagement metrics for cross-platform analysis"""
    
    @staticmethod
    def from_youtube(raw_data: dict) -> 'UniversalMetrics':
        """Transform YouTube metrics to universal format"""
        pass
    
    def calculate_engagement_rate(self) -> float:
        """Calculate engagement percentage"""
        pass
```

**Single Responsibility**: Metric calculation and normalization only.

#### IdeaProcessor (`src/core/idea_processor.py`)
**Responsibility**: Transform scraped data to IdeaInspiration format

```python
class IdeaProcessor:
    """Transform platform-specific data to IdeaInspiration model"""
    
    @staticmethod
    def transform(source: str, source_id: str, **kwargs) -> dict:
        """Transform to standardized IdeaInspiration format"""
        pass
```

**Single Responsibility**: Data transformation only.

---

### Open/Closed Principle (OCP)

The module is **open for extension** (new plugins) but **closed for modification** (base classes don't change).

#### SourcePlugin (Abstract Base Class)

```python
# src/plugins/__init__.py
from abc import ABC, abstractmethod

class SourcePlugin(ABC):
    """Abstract base class for YouTube scraping plugins"""
    
    def __init__(self, config: Config):
        self.config = config
    
    @abstractmethod
    def scrape(self, **kwargs) -> list[dict]:
        """Scrape YouTube data and return IdeaInspiration records"""
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Return unique source identifier"""
        pass
```

#### Extension Example: Adding a New Plugin

To add a new scraping strategy (e.g., playlist scraping):

```python
# src/plugins/youtube_playlist_plugin.py
from src.plugins import SourcePlugin

class YouTubePlaylistPlugin(SourcePlugin):
    """Scrape Shorts from YouTube playlists"""
    
    def scrape(self, playlist_url: str, **kwargs) -> list[dict]:
        # Implementation
        pass
    
    def get_source_name(self) -> str:
        return "youtube_shorts_playlist"
```

**No modification** to existing code required - just add new plugin file.

---

### Liskov Substitution Principle (LSP)

All plugin implementations can substitute the base `SourcePlugin` interface.

```python
# src/cli.py
def execute_scraping(plugin: SourcePlugin, **params):
    """Execute scraping with any plugin (polymorphism)"""
    ideas = plugin.scrape(**params)
    
    for idea in ideas:
        db.insert_idea(idea)
    
    print(f"✓ Scraped {len(ideas)} ideas from {plugin.get_source_name()}")

# All these work interchangeably
trending_plugin = YouTubeTrendingPlugin(config)
channel_plugin = YouTubeChannelPlugin(config)
search_plugin = YouTubeSearchPlugin(config)

execute_scraping(trending_plugin, max_results=50)
execute_scraping(channel_plugin, channel_url="@channel", top_n=50)
execute_scraping(search_plugin, query="ideas", max_results=50)
```

**Substitutability**: Any plugin can replace any other without breaking the system.

---

### Interface Segregation Principle (ISP)

The `SourcePlugin` interface is minimal - only two methods required:

```python
class SourcePlugin(ABC):
    @abstractmethod
    def scrape(self, **kwargs) -> list[dict]:
        """Only required method #1"""
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Only required method #2"""
        pass
```

**No fat interfaces** - plugins only implement what they need.

---

### Dependency Inversion Principle (DIP)

High-level modules depend on abstractions (interfaces), not concrete implementations.

#### CLI depends on SourcePlugin abstraction

```python
# src/cli.py
def run(mode: str, **params):
    config = Config()
    db = Database(config.database_path)
    
    # Depend on abstraction (SourcePlugin), not concrete class
    plugin: SourcePlugin
    
    if mode == 'trending':
        plugin = YouTubeTrendingPlugin(config)  # Concrete injected
    elif mode == 'channel':
        plugin = YouTubeChannelPlugin(config)   # Concrete injected
    
    # Work with abstraction
    ideas = plugin.scrape(**params)
```

#### Dependency Injection

All dependencies are injected through constructors:

```python
# Plugins receive Config via constructor injection
plugin = YouTubeChannelPlugin(config)

# Database receives path via constructor injection
db = Database(config.database_path)
```

**Inversion**: CLI doesn't instantiate Config/Database internally - they're injected.

---

## Plugin Architecture

### Base Plugin Interface

All scrapers implement the `SourcePlugin` interface:

```python
class SourcePlugin(ABC):
    """Abstract base class for all YouTube scrapers"""
    
    def __init__(self, config: Config):
        """Inject configuration dependency"""
        self.config = config
    
    @abstractmethod
    def scrape(self, **kwargs) -> list[dict]:
        """
        Scrape YouTube data and return IdeaInspiration records
        
        Returns:
            list[dict]: IdeaInspiration records
        """
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """
        Return unique source identifier
        
        Returns:
            str: Source name (e.g., 'youtube_shorts_trending')
        """
        pass
```

### Plugin Implementations

#### 1. YouTubeTrendingPlugin

**Source**: `src/plugins/youtube_trending_plugin.py`

**Purpose**: Scrape YouTube Shorts trending page

**Strategy**: Uses web scraping (BeautifulSoup or Selenium) to extract trending Shorts

**Advantages**:
- No API key required
- No quota limits
- Discovers viral content

**Windows Considerations**:
- ChromeDriver required for Selenium (Windows executable)
- Chrome/Edge browser installed

**Usage**:
```python
plugin = YouTubeTrendingPlugin(config)
ideas = plugin.scrape(max_results=50)
```

---

#### 2. YouTubeChannelPlugin

**Source**: `src/plugins/youtube_channel_plugin.py`

**Purpose**: Scrape Shorts from specific YouTube channels

**Strategy**: Uses yt-dlp library for channel scraping

**Advantages**:
- Rich metadata (views, likes, comments)
- Subtitle extraction
- No API quota
- Reliable and maintained (yt-dlp)

**Windows Considerations**:
- FFmpeg required (Windows binary)
- Handles Windows paths automatically

**Usage**:
```python
plugin = YouTubeChannelPlugin(config)
ideas = plugin.scrape(
    channel_url="@SnappyStories_1",
    top_n=50
)
```

**Implementation Details**:
```python
class YouTubeChannelPlugin(SourcePlugin):
    def scrape(self, channel_url: str, top_n: int = 50):
        ydl_opts = {
            'extract_flat': False,
            'playlist_items': f'1-{top_n}',
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'quiet': True,
            # Windows temp directory
            'outtmpl': '%(id)s.%(ext)s',
            'paths': {'temp': str(Path.home() / 'AppData' / 'Local' / 'Temp')}
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Scrape channel shorts
            info = ydl.extract_info(f"{channel_url}/shorts", download=False)
            
            ideas = []
            for entry in info['entries']:
                # Transform and process
                idea = self._process_entry(entry)
                ideas.append(idea)
        
        return ideas
```

---

#### 3. YouTubeSearchPlugin (Issue #300 - Not Yet Implemented)

**Source**: `src/plugins/youtube_search_plugin.py` (planned)

**Purpose**: Search YouTube Shorts by keywords

**Strategy**: YouTube Data API v3 search

**Status**: **Not Yet Implemented** (Issue #300)

**Current Behavior**: Falls back to trending results

**Workaround**:
```python
if mode == 'keyword':
    print("WARNING: Keyword search not yet implemented")
    plugin = YouTubeTrendingPlugin(config)  # Fallback
    ideas = plugin.scrape(max_results=max_results)
```

**Planned Implementation**:
```python
class YouTubeSearchPlugin(SourcePlugin):
    def scrape(self, query: str, max_results: int = 50):
        # Use YouTube Data API v3
        youtube = build('youtube', 'v3', developerKey=self.config.youtube_api_key)
        
        request = youtube.search().list(
            part='snippet',
            q=query,
            type='video',
            videoDuration='short',
            maxResults=max_results
        )
        
        response = request.execute()
        # Process and return ideas
```

**Blocked By**: YouTube API quota limits, requires careful implementation.

---

## Configuration Management

### Windows .env File Loading

The `Config` class handles Windows-specific path considerations:

```python
# src/core/config.py
from pathlib import Path
import os
from dotenv import load_dotenv

class Config:
    def __init__(self, env_file: str = ".env"):
        # Handle Windows paths (backslashes)
        env_path = Path(env_file)
        
        if not env_path.is_absolute():
            # Resolve relative to current working directory
            env_path = Path.cwd() / env_path
        
        # Load .env file
        load_dotenv(env_path)
        
        # Configuration with Windows-friendly defaults
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY', '')
        
        # Database path - Windows default
        default_db = str(Path.cwd() / 'youtube_shorts.db')
        self.database_path = os.getenv('DATABASE_PATH', default_db)
        
        # Numeric configs
        self.max_results = int(os.getenv('YOUTUBE_MAX_RESULTS', '50'))
        self.max_video_length = int(os.getenv('MAX_VIDEO_LENGTH', '180'))
        
        # Working directory (Windows path)
        self.working_dir = Path(os.getenv('WORKING_DIR', '.')).resolve()
```

### Environment Variables

**Required on Windows**:
```env
# YouTube API (optional for trending/channel modes)
YOUTUBE_API_KEY=your_api_key_here

# Database (Windows path - backslashes or forward slashes work)
DATABASE_PATH=C:\Users\YourName\Projects\youtube_shorts.db
# Or relative path
DATABASE_PATH=.\youtube_shorts.db

# Scraping limits
YOUTUBE_MAX_RESULTS=50
MAX_VIDEO_LENGTH=180

# Working directory (Windows path)
WORKING_DIR=C:\Users\YourName\Projects\YouTube
```

**PowerShell Environment Setup**:
```powershell
# Set environment variables for current session
$env:YOUTUBE_API_KEY = "your_key_here"
$env:DATABASE_PATH = ".\youtube_shorts.db"

# Or load from .env file
py -3.10 -m src.cli run --env-file .env
```

---

## Database Integration

### Schema

```sql
CREATE TABLE idea_inspirations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    source_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    tags TEXT,  -- JSON array
    score REAL DEFAULT 0.0,
    score_dictionary TEXT,  -- JSON object with detailed metrics
    raw_data TEXT,  -- Full JSON of original data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevent duplicates
    UNIQUE(source, source_id)
);

-- Index for fast lookups
CREATE INDEX idx_source_source_id ON idea_inspirations(source, source_id);
CREATE INDEX idx_created_at ON idea_inspirations(created_at);
CREATE INDEX idx_score ON idea_inspirations(score);
```

### Windows SQLite Integration

```python
# src/core/database.py
import sqlite3
from pathlib import Path

class Database:
    def __init__(self, db_path: str):
        # Windows path resolution
        self.db_path = Path(db_path).resolve()
        
        # Create parent directories if they don't exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._ensure_db_exists()
    
    def _get_connection(self):
        """Get SQLite connection with Windows optimizations"""
        conn = sqlite3.connect(str(self.db_path))
        
        # Enable WAL mode for better concurrency on Windows
        conn.execute("PRAGMA journal_mode=WAL")
        
        # Use memory for temp tables (faster on NVMe SSD)
        conn.execute("PRAGMA temp_store=MEMORY")
        
        return conn
    
    def insert_idea(self, idea: dict):
        """Insert IdeaInspiration record (handles duplicates)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO idea_inspirations 
                (source, source_id, title, description, tags, score, score_dictionary, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                idea['source'],
                idea['source_id'],
                idea['title'],
                idea.get('description', ''),
                json.dumps(idea.get('tags', [])),
                idea.get('score', 0.0),
                json.dumps(idea.get('score_dictionary', {})),
                json.dumps(idea.get('raw_data', {}))
            ))
            conn.commit()
        except sqlite3.IntegrityError:
            # Duplicate - skip silently
            pass
        finally:
            conn.close()
```

### Windows Performance Optimizations

```python
# Enable Write-Ahead Logging (WAL) for concurrent access
conn.execute("PRAGMA journal_mode=WAL")

# Use memory for temporary storage (faster on Windows NVMe SSD)
conn.execute("PRAGMA temp_store=MEMORY")

# Increase cache size (256MB for RTX 5090 workstation)
conn.execute("PRAGMA cache_size=-262144")  # Negative = KB

# Synchronous mode for better write performance
conn.execute("PRAGMA synchronous=NORMAL")
```

---

## Design Patterns

### 1. Abstract Factory Pattern

**Pattern**: `SourcePlugin` as factory interface

**Implementation**:
```python
# Factory function to create plugins
def create_plugin(mode: str, config: Config) -> SourcePlugin:
    """Factory for creating scraper plugins"""
    
    if mode == 'trending':
        return YouTubeTrendingPlugin(config)
    elif mode == 'channel':
        return YouTubeChannelPlugin(config)
    elif mode == 'keyword':
        return YouTubeSearchPlugin(config)
    else:
        raise ValueError(f"Unknown mode: {mode}")

# Usage
plugin = create_plugin('channel', config)
ideas = plugin.scrape(channel_url="@channel")
```

---

### 2. Strategy Pattern

**Pattern**: Different scraping strategies via plugins

**Implementation**:
```python
# Context
class Scraper:
    def __init__(self, strategy: SourcePlugin):
        self.strategy = strategy
    
    def execute(self, **params):
        return self.strategy.scrape(**params)

# Strategies
trending_strategy = YouTubeTrendingPlugin(config)
channel_strategy = YouTubeChannelPlugin(config)

# Execution
scraper = Scraper(channel_strategy)
ideas = scraper.execute(channel_url="@channel")
```

---

### 3. Dependency Injection

**Pattern**: Dependencies injected through constructors

**Implementation**:
```python
# Dependencies
config = Config()  # Configuration
db = Database(config.database_path)  # Database

# Inject into plugins
plugin = YouTubeChannelPlugin(config)  # Config injected

# Inject into processors
processor = IdeaProcessor(db)  # Database injected
```

---

### 4. Repository Pattern

**Pattern**: Database abstraction for data access

**Implementation**:
```python
class IdeaRepository:
    """Repository for IdeaInspiration data access"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def add(self, idea: dict):
        self.db.insert_idea(idea)
    
    def find_by_source(self, source: str):
        return self.db.get_ideas(filters={'source': source})
    
    def find_by_score(self, min_score: float):
        return self.db.get_ideas(filters={'score__gte': min_score})
```

---

### 5. Builder Pattern

**Pattern**: Config builder for complex configuration

**Implementation**:
```python
class ConfigBuilder:
    """Builder for Config objects"""
    
    def __init__(self):
        self._config = {}
    
    def with_api_key(self, key: str):
        self._config['YOUTUBE_API_KEY'] = key
        return self
    
    def with_database(self, path: str):
        self._config['DATABASE_PATH'] = path
        return self
    
    def build(self) -> Config:
        # Save to temp .env
        env_path = Path.cwd() / '.env.temp'
        with open(env_path, 'w') as f:
            for key, value in self._config.items():
                f.write(f"{key}={value}\n")
        
        return Config(str(env_path))

# Usage
config = (ConfigBuilder()
    .with_api_key('your_key')
    .with_database('./test.db')
    .build())
```

---

## Windows Platform Optimizations

### 1. NVMe SSD Optimization

**Target**: Fast read/write for RTX 5090 workstation

```python
# SQLite optimizations for NVMe SSD
conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
conn.execute("PRAGMA synchronous=NORMAL")  # Faster writes
conn.execute("PRAGMA cache_size=-262144")  # 256MB cache
conn.execute("PRAGMA temp_store=MEMORY")  # Memory temp storage
```

### 2. GPU-Ready Architecture (Future)

**Plan**: Integrate NVIDIA RTX 5090 for ML classification

```python
# Future GPU integration point
class GPUClassifier:
    """GPU-accelerated classification (RTX 5090)"""
    
    def __init__(self):
        import torch
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    def classify(self, ideas: list[dict]):
        # Use RTX 5090 for batch classification
        pass
```

### 3. Windows-Specific Dependencies

**Required Windows Tools**:
- **FFmpeg**: Video processing (yt-dlp dependency)
- **Chrome/Edge**: Web scraping (Selenium)
- **ChromeDriver**: Browser automation

**Installation** (PowerShell as Administrator):
```powershell
# Install Chocolatey (package manager)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install dependencies
choco install ffmpeg
choco install chromedriver

# Verify installations
ffmpeg -version
chromedriver --version
```

---

## Integration with PrismQ Ecosystem

### IdeaInspiration Model

**Transform to standardized format**:

```python
# src/core/idea_processor.py
class IdeaProcessor:
    @staticmethod
    def transform(source: str, source_id: str, title: str, **kwargs) -> dict:
        """Transform to IdeaInspiration model format"""
        
        return {
            'source': source,
            'source_id': source_id,
            'title': title,
            'description': kwargs.get('description', ''),
            'tags': kwargs.get('tags', []),
            'score': kwargs.get('score', 0.0),
            'score_dictionary': kwargs.get('metrics', {}).to_dict(),
            'raw_data': kwargs.get('raw_data', {}),
            'created_at': datetime.utcnow().isoformat()
        }
```

### Module Interactions

```
YouTube Shorts Module
    ↓ IdeaInspiration records
Classification Module
    ↓ Classified ideas
Scoring Module
    ↓ Scored ideas
Central Database
```

---

## Testing Architecture

### Unit Tests

**Location**: `tests/`

**Coverage**: Aim for >80%

**Example**:
```python
# tests/test_youtube_channel_plugin.py
def test_channel_scraping():
    config = Config(env_file='.env.test')
    plugin = YouTubeChannelPlugin(config)
    
    ideas = plugin.scrape(channel_url="@SnappyStories_1", top_n=5)
    
    assert len(ideas) <= 5
    assert all('source_id' in idea for idea in ideas)
```

### Integration Tests

**Testing on Windows**:
```python
# tests/test_windows_integration.py
def test_windows_paths():
    # Test Windows path handling
    config = Config()
    db_path = Path(config.database_path)
    
    assert db_path.is_absolute()
    assert str(db_path).startswith('C:\\') or str(db_path).startswith('D:\\')
```

---

## Performance Characteristics

**Windows RTX 5090 Platform**:

- **Scraping Speed**: 1-2 seconds/Short (network bound)
- **Database Writes**: 200+ inserts/second (NVMe SSD)
- **Memory Usage**: 200-500 MB (yt-dlp + metadata)
- **CPU Usage**: Low (I/O bound)
- **GPU Usage**: None (future: ML classification)

---

## Related Documentation

- **[EXECUTION_FLOW.md](./EXECUTION_FLOW.md)** - Complete execution flow from UI to database
- **[KNOWN_ISSUES.md](./KNOWN_ISSUES.md)** - Known limitations and platform issues
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Common problems and solutions
- **[Module README](../README.md)** - Quick start and usage guide

---

**Platform**: Windows 10/11 (Primary)  
**GPU**: NVIDIA RTX 5090  
**Python**: 3.10.x (Required)  
**Last Updated**: 2025-11-04
