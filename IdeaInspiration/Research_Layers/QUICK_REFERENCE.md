# Quick Reference: Separation of Concerns at Each Level

**🎯 Purpose**: Quick reference for developers implementing layered architecture patterns

---

## 📚 Document Guide

| Document | Size | Purpose | Audience |
|----------|------|---------|----------|
| **SUMMARY.md** | 7KB | Executive overview | Decision-makers, Team leads |
| **SEPARATION_OF_CONCERNS_LAYERED_ARCHITECTURE.md** | 48KB | Complete analysis | Developers, Architects |
| **README.md** | 4KB | Navigation guide | All team members |
| **This file** | Quick reference | Developers |

---

## ⭐ Key Takeaways (30-Second Version)

✅ **Current Architecture**: 4.5/5 - Excellent layer separation  
✅ **Pattern Usage**: Template Method + Strategy patterns work great  
✅ **No Layer Skipping**: Clean dependency chains  
⚠️ **Priority Fix**: Add semantic exception classes  

---

## 🏗️ Architecture Layers (Remember This!)

```
Layer 4: Orchestration    → ContentFunnel, Pipelines
         ↓ uses
Layer 3: Platform Sources → YouTubeSource, SpotifyClient
         ↓ inherits from
Layer 2: Base Classes     → BaseAudioClient, BaseVideoSource
         ↓ uses
Layer 1: External Libs    → requests.Session, APIs
```

**Rule**: Only talk to the layer **directly below** you!

---

## 📋 Checklist: Adding a New Source

When adding a new audio/video source, follow this pattern:

### ✅ Step 1: Identify the Layer
- [ ] Platform-specific? → Extends BaseAudioClient or BaseVideoSource
- [ ] Generic infrastructure? → Add to base classes
- [ ] Orchestration? → Use in ContentFunnel

### ✅ Step 2: Implement Required Methods

**For Audio Sources** (extends BaseAudioClient):
```python
class NewAudioClient(BaseAudioClient):
    def get_audio_metadata(self, audio_id: str) -> AudioMetadata:
        """Implement platform-specific fetch"""
        pass
    
    def search_audio(self, query: str, limit: int) -> List[AudioMetadata]:
        """Implement platform-specific search"""
        pass
```

**For Video Sources** (extends BaseVideoSource):
```python
class NewVideoSource(BaseVideoSource):
    def fetch_videos(self, query, limit, filters) -> List[Dict[str, Any]]:
        """Implement platform-specific fetch"""
        pass
    
    def get_video_details(self, video_id: str) -> Dict[str, Any]:
        """Implement platform-specific details"""
        pass
```

### ✅ Step 3: Use Base Class Features

**You get for free from base class**:
- ✅ HTTP session with retry logic
- ✅ Rate limiting (token bucket algorithm)
- ✅ Error handling (use `_make_request()`)
- ✅ Session cleanup (`close()`)

### ✅ Step 4: Keep It Platform-Specific

**DO put in your class**:
- ✅ Platform-specific authentication (OAuth, API keys)
- ✅ Platform-specific endpoints
- ✅ Platform-specific data parsing
- ✅ Platform-specific error codes

**DON'T put in your class**:
- ❌ Generic HTTP logic (use base class)
- ❌ Generic rate limiting (use base class)
- ❌ Generic retry logic (use base class)
- ❌ Generic caching (use CacheManager when available)

---

## 🚨 Common Anti-Patterns to Avoid

### ❌ Layer Skipping
```python
# BAD: Orchestration layer directly using requests
class ContentProcessor:
    def process_video(self, url):
        response = requests.get(url)  # ❌ Skip base + source layers
```

```python
# GOOD: Use adjacent layer
class ContentProcessor:
    def __init__(self, video_source: VideoSource):
        self.video_source = video_source  # ✅ Use source layer
    
    def process_video(self, video_id):
        details = self.video_source.get_video_details(video_id)
```

### ❌ Platform Logic in Base Class
```python
# BAD: YouTube-specific logic in base class
class BaseVideoSource:
    def fetch_videos(self):
        # ❌ YouTube-specific parsing
        if 'youtube.com' in url:
            video_id = url.split('v=')[1]
```

```python
# GOOD: Platform logic in platform class
class YouTubeSource(BaseVideoSource):
    def fetch_videos(self):
        # ✅ YouTube-specific in YouTube class
        video_id = self._parse_youtube_url(url)
```

### ❌ Duplicating Infrastructure
```python
# BAD: Each client has its own session management
class SpotifyClient:
    def __init__(self):
        # ❌ Duplicating session logic
        self.session = requests.Session()
        retry = Retry(...)
        # ...
```

```python
# GOOD: Inherit from base class
class SpotifyClient(BaseAudioClient):
    def __init__(self, ...):
        super().__init__(...)  # ✅ Gets session from base
```

---

## 🎨 Design Pattern Quick Guide

### When to Use Template Method
**Pattern**: Base class defines workflow, subclasses override steps

**Use When**:
- Multiple classes follow similar process
- Want to enforce consistent workflow
- Need to centralize common logic

**Example in Codebase**: BaseAudioClient

### When to Use Strategy
**Pattern**: Swap algorithms at runtime via dependency injection

**Use When**:
- Need runtime flexibility
- Multiple algorithms for same task
- Want to avoid inheritance

**Example in Codebase**: ContentFunnel with Protocols

### When to Use Composition
**Pattern**: Build functionality with components instead of inheritance

**Use When**:
- Cross-cutting concerns (logging, caching)
- Feature doesn't fit inheritance tree
- Want maximum flexibility

**Example in Codebase**: Utility functions, future CacheManager

---

## 🔧 Priority Improvements (From Research)

### P1: Do These First (6-7 hours total)

1. **Semantic Exceptions** (1-2h)
   ```python
   # Create: Source/src/core/exceptions.py
   class FetchFailedException(SourceException): pass
   class RateLimitExceeded(SourceException): pass
   ```

2. **Error Translation** (2-3h)
   ```python
   # Update: BaseAudioClient._make_request()
   except requests.ConnectionError as e:
       raise FetchFailedException(f"Network error: {e}") from e
   ```

3. **Architecture Docs** (1-2h)
   - Document layer boundaries
   - Add guidelines for new sources

---

## 📊 Quick Metrics

| Metric | Score | Notes |
|--------|-------|-------|
| Layer Separation | ⭐⭐⭐⭐⭐ | Excellent |
| No Layer Skipping | ⭐⭐⭐⭐⭐ | Clean chains |
| Code Reusability | ⭐⭐⭐⭐⭐ | Minimal duplication |
| Design Patterns | ⭐⭐⭐⭐⭐ | Well implemented |
| Error Handling | ⭐⭐⭐⭐ | Can improve |
| **Overall** | **⭐⭐⭐⭐½** | **4.5/5** |

---

## 🔗 Related Resources

- **Full Analysis**: `SEPARATION_OF_CONCERNS_LAYERED_ARCHITECTURE.md`
- **Executive Summary**: `SUMMARY.md`
- **Code Examples**: See sections in main document
- **Internal Docs**: `_meta/docs/ARCHITECTURE.md`
- **SOLID Review**: `_meta/docs/code_reviews/SOLID_REVIEW_CORE_MODULES.md`

---

## 💡 Remember

> "Each layer should talk only to the layer directly below it, encapsulate logic at the appropriate level, and maximize code reuse through inheritance and composition."

**Questions?** See the full research document or create an issue.
# Quick Reference - Testing and Mocking Patterns

## 🎯 Core Concept

**Test each layer in isolation by mocking its dependencies**

```
Your Code
    ↓ (inject)
Protocol Interface
    ↓ (implement)
Mock (for tests) | Real (for production)
```

## 📚 Documentation Overview

| Document | Purpose | Size |
|----------|---------|------|
| [README.md](./README.md) | Overview and navigation | 269 lines |
| [TESTING_STRATEGY.md](./TESTING_STRATEGY.md) | Comprehensive strategy | 954 lines |
| [TESTING_EXAMPLES.md](./TESTING_EXAMPLES.md) | Copy-paste examples | 1492 lines |
| [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) | Refactoring guide | 894 lines |

---

## 🚀 Quick Start (30 seconds)

### 1. Define Protocol

```python
from typing import Protocol, Optional, Dict, Any

class IDataFetcher(Protocol):
    def fetch(self, id: str) -> Optional[Dict[str, Any]]:
        """Fetch data by ID."""
        ...
```

### 2. Implement Protocol

```python
class APIDataFetcher:
    def fetch(self, id: str) -> Optional[Dict[str, Any]]:
        response = requests.get(f'https://api.example.com/{id}')
        return response.json()
```

### 3. Inject Dependency

```python
class DataProcessor:
    def __init__(self, fetcher: IDataFetcher):
        self.fetcher = fetcher
    
    def process(self, id: str):
        data = self.fetcher.fetch(id)
        # Process data...
```

### 4. Create Mock

```python
class MockDataFetcher:
    def __init__(self, mock_data: Dict[str, Any]):
        self.mock_data = mock_data
    
    def fetch(self, id: str) -> Optional[Dict[str, Any]]:
        return self.mock_data
```

### 5. Test

```python
def test_processor():
    mock = MockDataFetcher({'id': '123', 'value': 'test'})
    processor = DataProcessor(mock)
    
    result = processor.process('123')
    
    assert result is not None
```

---

## 🎨 Common Patterns

### Pattern: HTTP Client

```python
# Protocol
class IHTTPClient(Protocol):
    def get(self, url: str) -> Dict: ...

# Mock
class MockHTTPClient:
    def __init__(self, response: Dict):
        self.response = response
        self.call_count = 0
    
    def get(self, url: str) -> Dict:
        self.call_count += 1
        return self.response

# Test
def test_api_client():
    mock = MockHTTPClient({'status': 'ok'})
    client = APIClient(http_client=mock)
    
    result = client.fetch_data()
    assert result['status'] == 'ok'
    assert mock.call_count == 1
```

### Pattern: Database

```python
# Protocol
class IDatabase(Protocol):
    def save(self, data: Dict) -> bool: ...
    def get(self, id: str) -> Optional[Dict]: ...

# Mock
class MockDatabase:
    def __init__(self):
        self.data = {}
        self.save_count = 0
    
    def save(self, data: Dict) -> bool:
        self.save_count += 1
        self.data[data['id']] = data
        return True
    
    def get(self, id: str) -> Optional[Dict]:
        return self.data.get(id)

# Test
def test_data_service():
    mock_db = MockDatabase()
    service = DataService(database=mock_db)
    
    service.save_item({'id': '1', 'name': 'Test'})
    
    assert mock_db.save_count == 1
    assert mock_db.data['1']['name'] == 'Test'
```

### Pattern: File System

```python
# Protocol
class IFileReader(Protocol):
    def read(self, path: str) -> str: ...

# Mock
class MockFileReader:
    def __init__(self, mock_content: str):
        self.mock_content = mock_content
        self.reads = []
    
    def read(self, path: str) -> str:
        self.reads.append(path)
        return self.mock_content

# Test
def test_config_loader():
    mock = MockFileReader('{"key": "value"}')
    loader = ConfigLoader(file_reader=mock)
    
    config = loader.load('config.json')
    
    assert config['key'] == 'value'
    assert 'config.json' in mock.reads
```

---

## 🧪 Test Structure (AAA Pattern)

```python
def test_something():
    # Arrange - Set up test data and mocks
    mock_fetcher = MockFetcher({'data': 'value'})
    processor = DataProcessor(fetcher=mock_fetcher)
    
    # Act - Execute the code under test
    result = processor.process('test-id')
    
    # Assert - Verify expected outcomes
    assert result['data'] == 'value'
    assert mock_fetcher.call_count == 1
```

---

## 🎯 Pytest Fixtures

### Basic Fixture

```python
import pytest

@pytest.fixture
def mock_database():
    """Provide mock database for tests."""
    return MockDatabase()

def test_with_fixture(mock_database):
    service = DataService(database=mock_database)
    service.save({'id': '1'})
    assert mock_database.save_count == 1
```

### Fixture with Parameters

```python
@pytest.fixture
def mock_fetcher():
    """Factory fixture for custom mock data."""
    def _create_fetcher(data):
        return MockFetcher(data)
    return _create_fetcher

def test_with_custom_data(mock_fetcher):
    fetcher = mock_fetcher({'custom': 'data'})
    result = fetcher.fetch('id')
    assert result['custom'] == 'data'
```

### Fixture Cleanup

```python
@pytest.fixture
def database_connection():
    """Provide database with cleanup."""
    db = Database(':memory:')
    yield db
    db.close()  # Cleanup after test

def test_with_cleanup(database_connection):
    database_connection.save({'id': '1'})
    # db.close() called automatically after test
```

---

## 🔍 Common Test Scenarios

### Testing Success Path

```python
def test_successful_fetch():
    mock = MockFetcher({'status': 'success', 'data': 'value'})
    client = Client(fetcher=mock)
    
    result = client.fetch_data('123')
    
    assert result['status'] == 'success'
```

### Testing Error Handling

```python
def test_fetch_failure():
    mock = MockFetcher(should_fail=True)
    client = Client(fetcher=mock)
    
    result = client.fetch_data('123')
    
    assert result is None  # Should handle gracefully
```

### Testing with Exceptions

```python
def test_fetch_raises_exception():
    mock = MockFetcher(should_raise=ValueError("Invalid ID"))
    client = Client(fetcher=mock)
    
    with pytest.raises(ValueError, match="Invalid ID"):
        client.fetch_data('invalid')
```

### Testing Call Tracking

```python
def test_fetcher_called_correctly():
    mock = MockFetcher({'data': 'value'})
    client = Client(fetcher=mock)
    
    client.fetch_data('test-id')
    
    assert mock.call_count == 1
    assert mock.last_id == 'test-id'
```

### Testing Multiple Calls

```python
def test_batch_processing():
    mock = MockFetcher({'data': 'value'})
    processor = BatchProcessor(fetcher=mock)
    
    processor.process_batch(['id1', 'id2', 'id3'])
    
    assert mock.call_count == 3
    assert mock.call_ids == ['id1', 'id2', 'id3']
```

---

## 🛠️ Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific file
pytest tests/test_processor.py

# Run specific test
pytest tests/test_processor.py::test_success

# Run with coverage
pytest --cov=src --cov-report=html

# Run only unit tests
pytest -m unit
```

### Test Markers

```python
# In test file
@pytest.mark.unit
def test_something():
    pass

@pytest.mark.integration
def test_integration():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass
```

```bash
# Run by marker
pytest -m unit          # Only unit tests
pytest -m integration   # Only integration tests
pytest -m "not slow"    # Skip slow tests
```

---

## ✅ Checklist for New Code

Before writing code:
- [ ] Identify dependencies (API, DB, files, time, etc.)
- [ ] Define Protocol for each dependency
- [ ] Plan how to inject dependencies

While writing code:
- [ ] Accept dependencies via constructor
- [ ] Use Protocol types for parameters
- [ ] Avoid hardcoded dependencies
- [ ] Keep side effects isolated

While writing tests:
- [ ] Create mock implementations
- [ ] Test happy path
- [ ] Test error paths
- [ ] Test edge cases
- [ ] Verify call tracking

---

## 🚫 Common Mistakes

### ❌ Don't: Hardcode Dependencies

```python
class Processor:
    def process(self):
        fetcher = APIFetcher()  # Can't mock!
        data = fetcher.fetch()
```

### ✅ Do: Inject Dependencies

```python
class Processor:
    def __init__(self, fetcher: IFetcher):
        self.fetcher = fetcher  # Can mock!
    
    def process(self):
        data = self.fetcher.fetch()
```

---

### ❌ Don't: Test Implementation

```python
def test_uses_requests():
    with patch('requests.get') as mock:
        client.fetch()
        mock.assert_called()  # Testing internal detail
```

### ✅ Do: Test Behavior

```python
def test_fetches_data():
    mock = MockFetcher({'data': 'value'})
    client = Client(mock)
    
    result = client.fetch()
    
    assert result['data'] == 'value'  # Testing outcome
```

---

### ❌ Don't: Share Mocks Between Tests

```python
mock = MockDatabase()  # Shared!

def test_one():
    save_data(mock)
    assert mock.count == 1

def test_two():
    save_data(mock)
    assert mock.count == 1  # Fails! Count is 2
```

### ✅ Do: Create Fresh Mocks

```python
@pytest.fixture
def mock_db():
    return MockDatabase()  # Fresh for each test

def test_one(mock_db):
    save_data(mock_db)
    assert mock_db.count == 1

def test_two(mock_db):
    save_data(mock_db)
    assert mock_db.count == 1  # Correct!
```

---

## 📊 Test Coverage Goals

| Component | Target Coverage |
|-----------|----------------|
| Business Logic | 95%+ |
| Infrastructure | 85%+ |
| Integration Points | 80%+ |
| Utilities | 90%+ |

```bash
# Check coverage
pytest --cov=src --cov-report=term-missing

# Fail if below threshold
pytest --cov=src --cov-fail-under=80
```

---

## 🎓 Learning Path

1. **Start Here**: Read [README.md](./README.md) (5 min)
2. **Core Concepts**: Read "Core Principles" in [TESTING_STRATEGY.md](./TESTING_STRATEGY.md) (10 min)
3. **First Example**: Read "Protocol-Based Testing" in [TESTING_EXAMPLES.md](./TESTING_EXAMPLES.md) (15 min)
4. **Practice**: Copy example and modify for your use case (30 min)
5. **Deep Dive**: Read full [TESTING_STRATEGY.md](./TESTING_STRATEGY.md) (30 min)
6. **Refactoring**: Read [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) when needed

**Total Time**: ~90 minutes to full proficiency

---

## 🔗 Quick Links

### Within This Directory
- [Full Testing Strategy](./TESTING_STRATEGY.md)
- [Practical Examples](./TESTING_EXAMPLES.md)
- [Implementation Guide](./IMPLEMENTATION_GUIDE.md)
- [Directory Overview](./README.md)

### Related Documentation
- [Architecture Overview](../../docs/ARCHITECTURE.md)
- [SOLID Principles Review](../../docs/code_reviews/SOLID_REVIEW_CORE_MODULES.md)
- [Contributing Guidelines](../../docs/CONTRIBUTING.md)

### External Resources
- [PEP 544 - Protocols](https://peps.python.org/pep-0544/)
- [pytest Documentation](https://docs.pytest.org/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

---

## 💡 Pro Tips

1. **Start Small**: Begin with one class/module, master the pattern
2. **Test First**: Write tests before implementation (TDD)
3. **Keep Mocks Simple**: Don't over-engineer mock implementations
4. **Use Fixtures**: Share setup code via pytest fixtures
5. **Document Intent**: Write clear docstrings explaining what's tested
6. **Test Errors**: Always test error paths, not just happy paths
7. **Run Often**: Run tests frequently during development
8. **Review Coverage**: Check coverage reports to find gaps

---

## 📞 Getting Help

1. **Check Examples**: Most questions answered in [TESTING_EXAMPLES.md](./TESTING_EXAMPLES.md)
2. **Search Existing Tests**: Look at tests in `_meta/tests/` for patterns
3. **Ask Team**: Consult with developers who've used these patterns
4. **Refer to Docs**: Full details in [TESTING_STRATEGY.md](./TESTING_STRATEGY.md)

---

**Last Updated**: 2025-11-14  
**Maintained By**: PrismQ Development Team
**Version**: 1.0  
**Status**: Production Ready
