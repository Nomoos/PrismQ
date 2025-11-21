# 03_Testing - Testing Strategy & Examples

**Purpose**: Comprehensive testing strategies, examples, and implementation guides for layered architecture testing

---

## 📚 Documents in This Section

### 🎯 TESTING_STRATEGY.md
**Size**: 954 lines | **Read Time**: 45 min

**Comprehensive testing and mocking strategy**:

**Core Principles**:
- Testability by design
- Interface testing (Protocol-based)
- Mock dependencies for isolation
- AAA pattern (Arrange-Act-Assert)

**Layer Testing Architecture**:
```
Application Layer (CLI, Workers)
    ↓ (mock domain services)
Domain Layer (ContentFunnel, Processors)
    ↓ (mock infrastructure)
Infrastructure Layer (API Clients, Database)
    ↓ (mock external services)
Foundation Layer (Models, Schemas)
```

**Dependency Injection Patterns**:
- Protocol-based injection
- Optional dependencies
- Factory pattern injection

**Mocking Strategies**:
- Manual mock classes
- unittest.mock usage
- pytest fixtures
- requests-mock for HTTP

**When to Read**: Essential for all developers writing tests

---

### 💻 TESTING_EXAMPLES.md
**Size**: 1,492 lines | **Read Time**: 60 min

**Copy-paste-ready implementation examples**:

**Examples Included**:
1. **Protocol-Based Testing** - Video fetcher example
2. **API Client Testing** - HTTP client with rate limiting
3. **Database Layer Testing** - Task queue with SQLite
4. **Content Processing Testing** - ContentFunnel comprehensive tests

**Features**:
- Complete code examples
- Test suites with fixtures
- Success and error path testing
- Call tracking verification
- Edge case handling

**When to Read**: When writing tests - practical implementation guide

---

### 📖 IMPLEMENTATION_GUIDE.md
**Size**: 894 lines | **Read Time**: 35 min

**Step-by-step implementation and refactoring guide**:

**Topics**:
- How to refactor existing code for testability
- How to add Protocols to existing classes
- Migration strategies for untested code
- Common pitfalls and solutions

**Process**:
1. Identify dependencies
2. Define Protocols
3. Add injection points
4. Create mocks
5. Write tests

**When to Read**: Refactoring existing code for testability

---

### 📝 RESEARCH_SUMMARY.md
**Size**: 370 lines | **Read Time**: 8 min

**Executive summary of testing research**:
- Key findings
- Protocol-based dependency injection
- Layer testing architecture
- Mock implementation patterns
- Recommendations and benefits

**When to Read**: Quick overview of testing approach

---

### 🧪 test_worker_protocol.py
**Size**: 244 lines | **Code Example**

**Practical test example** demonstrating worker protocol testing

**When to Use**: Reference implementation for worker tests

---

## 🎯 Quick Start Paths

### For New Developers (90 min)
1. **Start**: RESEARCH_SUMMARY.md (8 min)
2. **Learn**: TESTING_STRATEGY.md - Core Principles section (15 min)
3. **Practice**: TESTING_EXAMPLES.md - First example (20 min)
4. **Apply**: Write a simple test (30 min)
5. **Reference**: Keep TESTING_EXAMPLES.md bookmarked

### For Experienced Developers (60 min)
1. **Quick Read**: RESEARCH_SUMMARY.md (8 min)
2. **Review**: TESTING_EXAMPLES.md (30 min)
3. **Apply**: Implement pattern in your code (30 min)

### For Refactoring Existing Code (45 min)
1. **Read**: IMPLEMENTATION_GUIDE.md (35 min)
2. **Apply**: Follow step-by-step guide (60+ min)
3. **Reference**: TESTING_EXAMPLES.md for patterns

---

## 🔑 Core Concepts

### Protocol-Based Dependency Injection

**Pattern**: Define Protocol → Implement → Inject → Mock → Test

```python
# 1. Define Protocol
class IDataFetcher(Protocol):
    def fetch(self, id: str) -> Optional[Dict]: ...

# 2. Implement
class APIDataFetcher:
    def fetch(self, id: str) -> Optional[Dict]:
        # Real implementation
        pass

# 3. Inject
class DataProcessor:
    def __init__(self, fetcher: IDataFetcher):
        self.fetcher = fetcher

# 4. Mock
class MockDataFetcher:
    def fetch(self, id: str) -> Optional[Dict]:
        return {'id': id, 'data': 'test'}

# 5. Test
def test_processor():
    mock = MockDataFetcher()
    processor = DataProcessor(mock)
    result = processor.process('123')
    assert result is not None
```

### AAA Testing Pattern

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

### Layer Isolation Testing

**Key Principle**: Mock the layer directly below you

```python
# Infrastructure Layer - Mock external services
class TestAPIClient:
    def test_fetch(self, mock_http_session):  # Mock requests
        client = APIClient(session=mock_http_session)
        result = client.fetch('id')
        assert result is not None

# Domain Layer - Mock infrastructure
class TestContentProcessor:
    def test_process(self, mock_api_client):  # Mock API client
        processor = ContentProcessor(client=mock_api_client)
        result = processor.process('id')
        assert result is not None

# Application Layer - Mock domain
class TestWorker:
    def test_work(self, mock_processor):  # Mock processor
        worker = Worker(processor=mock_processor)
        worker.do_work()
        assert mock_processor.called
```

---

## 📊 Testing Metrics & Goals

### Coverage Targets
| Component | Target | Priority |
|-----------|--------|----------|
| Business Logic | 95%+ | High |
| Infrastructure | 85%+ | High |
| Integration Points | 80%+ | Medium |
| Utilities | 90%+ | Medium |

### Speed Targets
- **Unit Tests**: <1ms per test (no I/O)
- **Integration Tests**: 100ms-1s per test
- **Full Suite**: <1 minute

### Quality Targets
- **Flaky Tests**: 0 (100% deterministic)
- **Test Isolation**: 100% independent
- **Reliability**: Same results every run

---

## 🛠️ Common Testing Scenarios

### Testing Success Path
```python
def test_successful_operation():
    mock = MockService(should_succeed=True)
    service = Service(mock)
    result = service.operation()
    assert result.success is True
```

### Testing Error Handling
```python
def test_handles_failure_gracefully():
    mock = MockService(should_fail=True)
    service = Service(mock)
    result = service.operation()
    assert result.success is False
```

### Testing Exceptions
```python
def test_raises_on_invalid_input():
    mock = MockService()
    service = Service(mock)
    with pytest.raises(ValueError):
        service.operation('invalid')
```

### Testing Call Tracking
```python
def test_calls_dependency_correctly():
    mock = MockService()
    service = Service(mock)
    service.operation('test-id')
    
    assert mock.call_count == 1
    assert mock.last_call_args == ('test-id',)
```

---

## 🔧 pytest Commands Reference

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

# Run fast tests only
pytest -m "not slow"

# Run tests matching pattern
pytest -k "test_video"
```

---

## 🎨 Mock Patterns Quick Reference

### Simple Mock
```python
class MockService:
    def __init__(self, return_value):
        self.return_value = return_value
        self.called = False
    
    def operation(self):
        self.called = True
        return self.return_value
```

### Mock with Call Tracking
```python
class MockService:
    def __init__(self):
        self.calls = []
    
    def operation(self, arg):
        self.calls.append(arg)
        return {'status': 'ok'}
```

### Mock with State
```python
class MockDatabase:
    def __init__(self):
        self.data = {}
    
    def save(self, item):
        self.data[item['id']] = item
    
    def get(self, id):
        return self.data.get(id)
```

### Mock with Failure Simulation
```python
class MockService:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
    
    def operation(self):
        if self.should_fail:
            raise ServiceException("Operation failed")
        return {'status': 'ok'}
```

---

## ✅ Testing Checklist

### Before Writing Code
- [ ] Identify all dependencies
- [ ] Define Protocol for each dependency
- [ ] Plan injection strategy
- [ ] Consider testing approach

### While Writing Code
- [ ] Accept dependencies via constructor
- [ ] Use Protocol types for parameters
- [ ] Avoid hardcoded dependencies
- [ ] Keep side effects isolated

### While Writing Tests
- [ ] Create mock implementations
- [ ] Test happy path
- [ ] Test error paths
- [ ] Test edge cases
- [ ] Verify call tracking
- [ ] Check coverage

---

## 🚫 Common Mistakes to Avoid

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

## 🔗 Related Documentation

### Within Research_Layers
- [01_Architecture](../01_Architecture) - Understanding layers to test
- [02_Design_Patterns](../02_Design_Patterns) - SOLID principles for testability
- [05_Templates](../05_Templates) - Templates with test examples

### External
- Main README: [/Research_Layers/README.md](../README.md)
- [PEP 544 - Protocols](https://peps.python.org/pep-0544/)
- [pytest Documentation](https://docs.pytest.org/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

---

## 💡 Pro Tips

1. **Start Small** - Begin with one class, master the pattern
2. **Test First** - Write tests before implementation (TDD)
3. **Keep Mocks Simple** - Don't over-engineer mock implementations
4. **Use Fixtures** - Share setup code via pytest fixtures
5. **Document Intent** - Write clear docstrings
6. **Test Errors** - Always test error paths
7. **Run Often** - Run tests frequently during development
8. **Check Coverage** - Use coverage reports to find gaps

---

## 📝 Document Priority

### Must Read (60 min)
1. ⭐ RESEARCH_SUMMARY.md (8 min)
2. ⭐ TESTING_STRATEGY.md - Core sections (20 min)
3. ⭐ TESTING_EXAMPLES.md - First 2 examples (30 min)

### Should Read (45 min)
4. TESTING_EXAMPLES.md - All examples (60 min total)
5. IMPLEMENTATION_GUIDE.md - When refactoring (35 min)

### Reference
6. test_worker_protocol.py - Code example
7. pytest commands and patterns (as needed)

---

**Last Updated**: 2025-11-14  
**Status**: Complete and Production Ready  
**Maintained By**: Testing & Quality Team

**Ready to test?** Start with RESEARCH_SUMMARY.md then dive into TESTING_EXAMPLES.md!
