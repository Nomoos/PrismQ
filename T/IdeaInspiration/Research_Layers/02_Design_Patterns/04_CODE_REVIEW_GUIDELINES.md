# Code Review Guidelines - PrismQ.IdeaInspiration

**Last Updated**: 2025-11-14  
**Status**: Active

## Purpose

This document provides guidelines for conducting effective code reviews that enforce architectural conventions and maintain code quality in PrismQ.IdeaInspiration.

## Table of Contents

- [Code Review Philosophy](#code-review-philosophy)
- [Architecture Review](#architecture-review)
- [Code Quality Review](#code-quality-review)
- [Testing Review](#testing-review)
- [Documentation Review](#documentation-review)
- [Review Checklist](#review-checklist)
- [Common Issues and Solutions](#common-issues-and-solutions)
- [Providing Feedback](#providing-feedback)

---

## Code Review Philosophy

### Goals

1. **Maintain Architecture** - Ensure code follows layered architecture
2. **Ensure Quality** - Catch bugs, improve maintainability
3. **Share Knowledge** - Educate team on best practices
4. **Build Culture** - Foster excellence and continuous improvement

### Principles

- **Be Kind** - Focus on the code, not the person
- **Be Specific** - Point to exact lines and suggest alternatives
- **Be Educational** - Explain why, link to documentation
- **Be Timely** - Review within 24 hours when possible
- **Be Thorough** - Check all aspects, not just syntax

### Review Scope

Review for:
- ✅ **Architecture compliance** - Layer boundaries, dependencies
- ✅ **SOLID principles** - SRP, OCP, LSP, ISP, DIP
- ✅ **Code quality** - Style, maintainability, performance
- ✅ **Testing** - Coverage, quality of tests
- ✅ **Documentation** - Code comments, README updates

Don't nitpick:
- ❌ Personal style preferences (if follows conventions)
- ❌ Minor formatting (handled by automated tools)
- ❌ Unrelated issues (create separate issues)

---

## Architecture Review

### 1. Layer Compliance

**Check**: Is the code in the correct layer?

**Questions to Ask**:
- Does this belong in Sources, Model, Processing, or Infrastructure?
- Is it at the right level within a multi-tier structure?
- Does it follow the pattern for its layer?

**Example Issues**:

❌ **Bad** - Business logic in Model:
```python
# Model/idea_inspiration.py
class IdeaInspiration:
    def classify(self):
        # ❌ Classification logic in Model layer
        classifier = ContentClassifier()
        return classifier.classify(self)
```

**Feedback**:
> This violates layer boundaries. Model should be pure data with no business logic. Classification logic belongs in the Classification module. Please move this to `Classification/classifier.py` and call it from the application layer.
> 
> See: [ADR-001: Layered Architecture](./decisions/ADR-001-LAYERED_ARCHITECTURE.md#3-data-model-layer-model)

✅ **Good** - Proper layer separation:
```python
# Model/idea_inspiration.py
@dataclass
class IdeaInspiration:
    """Pure data model."""
    title: str
    description: str
    categories: Optional[List[str]] = None  # Enriched by Classification

# Classification/classifier.py
class ContentClassifier:
    def classify(self, idea: IdeaInspiration) -> IdeaInspiration:
        """Add classification data to IdeaInspiration."""
        categories = self._determine_categories(idea)
        return IdeaInspiration(**idea.__dict__, categories=categories)
```

---

### 2. Dependency Direction

**Check**: Do dependencies only flow downward?

**Allowed Flow**:
```
Application → Processing → Model → Collection → Infrastructure
```

**Questions to Ask**:
- Are all imports from lower layers?
- No upward dependencies (Model → Sources)?
- No peer dependencies (Classification ↔ Scoring)?

**Example Issues**:

❌ **Bad** - Upward dependency:
```python
# Model/idea_inspiration.py
from Classification import ContentClassifier  # ❌ Upper layer!

class IdeaInspiration:
    pass
```

**Feedback**:
> This creates an upward dependency from Model to Classification, which violates our layered architecture. Model should have no dependencies on other PrismQ modules.
> 
> **Solution**: Remove this import. If you need classification, call it from the application layer:
> ```python
> # Application layer
> idea = create_idea(...)
> classified_idea = classifier.classify(idea)
> ```
> 
> See: [ADR-001: Dependency Rules](./decisions/ADR-001-LAYERED_ARCHITECTURE.md#dependency-rules)

❌ **Bad** - Peer dependency:
```python
# Classification/classifier.py
from Scoring import ContentScorer  # ❌ Peer module!

class ContentClassifier:
    def classify_and_score(self, idea):
        # Combines classification and scoring
        pass
```

**Feedback**:
> Classification and Scoring are peer modules and should not depend on each other. This creates tight coupling.
> 
> **Solution**: Keep them independent. If you need both, orchestrate from application layer:
> ```python
> # Application layer
> classified = classifier.classify(idea)
> scored = scorer.score(classified)
> ```
> 
> See: [ADR-001: Processing Pipeline Layer](./decisions/ADR-001-LAYERED_ARCHITECTURE.md#4-processing-pipeline-layer-classification-scoring)

---

### 3. Dependency Injection

**Check**: Are dependencies injected rather than created?

**Questions to Ask**:
- Are dependencies passed to `__init__`?
- Does the class create its own dependencies?
- Can dependencies be easily mocked for testing?

**Example Issues**:

❌ **Bad** - Creating dependencies:
```python
class YouTubeWorker:
    def __init__(self):
        self.config = Config()  # ❌ Creates own config
        self.database = Database("/path/db.sqlite")  # ❌ Hard-coded
```

**Feedback**:
> This class creates its own dependencies, which violates the Dependency Inversion Principle. This makes testing difficult and couples the class to concrete implementations.
> 
> **Solution**: Inject dependencies via constructor:
> ```python
> class YouTubeWorker:
>     def __init__(self, config: Config, database: Database):
>         self.config = config
>         self.database = database
> ```
> 
> See: [SOLID Principles - DIP](./SOLID_PRINCIPLES.md#5-dependency-inversion-principle-dip)

---

### 4. Interface Segregation

**Check**: Are interfaces minimal and focused?

**Questions to Ask**:
- Does the interface have only essential methods?
- Are clients forced to implement unused methods?
- Could this be split into smaller interfaces?

**Example Issues**:

❌ **Bad** - Kitchen sink interface:
```python
class SourcePlugin(ABC):
    @abstractmethod
    def scrape(self): pass
    
    @abstractmethod
    def save_to_database(self): pass  # ❌ Not all plugins need this
    
    @abstractmethod
    def send_notification(self): pass  # ❌ Not all plugins need this
    
    @abstractmethod
    def validate_api_key(self): pass  # ❌ Not all plugins need this
```

**Feedback**:
> This interface is too large and forces implementations to provide methods they don't need, violating the Interface Segregation Principle.
> 
> **Solution**: Split into focused interfaces:
> ```python
> class SourcePlugin(ABC):
>     @abstractmethod
>     def scrape(self): pass  # Essential method only
> 
> class PersistablePlugin(ABC):
>     @abstractmethod
>     def save_to_database(self): pass
> 
> class NotifiablePlugin(ABC):
>     @abstractmethod
>     def send_notification(self): pass
> ```
> 
> See: [SOLID Principles - ISP](./SOLID_PRINCIPLES.md#4-interface-segregation-principle-isp)

---

### 5. Naming Conventions

**Check**: Do names follow layer-specific conventions?

**Questions to Ask**:
- Does the name follow the layer's pattern?
- Is the name descriptive and unambiguous?
- Does it match existing conventions?

**Example Issues**:

❌ **Bad** - Inconsistent naming:
```python
# Source/Video/YouTube/Channel/src/plugins/yt_chan.py
class YTChanPlugin:  # ❌ Abbreviations
    pass
```

**Feedback**:
> The class and file names don't follow our conventions for the Source layer.
> 
> **Solution**: Use full, descriptive names:
> ```python
> # Source/Video/YouTube/Channel/src/plugins/youtube_channel_plugin.py
> class YouTubeChannelPlugin(VideoPlugin):
>     pass
> ```
> 
> See: [Coding Conventions - Naming](./CODING_CONVENTIONS.md#naming-conventions)

---

## Code Quality Review

### 1. Single Responsibility Principle

**Check**: Does each class have one reason to change?

**Questions to Ask**:
- Can you describe the class's purpose in one sentence without "and"?
- Does the class mix multiple concerns?
- Should responsibilities be split into separate classes?

**Example Issues**:

❌ **Bad** - Multiple responsibilities:
```python
class YouTubeManager:
    """Does everything - BAD!"""
    
    def fetch_videos(self): pass
    def parse_response(self): pass
    def save_to_database(self): pass
    def send_notifications(self): pass
    def generate_reports(self): pass
```

**Feedback**:
> This class has too many responsibilities (API, parsing, persistence, notifications, reporting), violating SRP.
> 
> **Solution**: Split into focused classes:
> ```python
> class YouTubeAPIClient:
>     def fetch_videos(self): pass
> 
> class YouTubeParser:
>     def parse_response(self): pass
> 
> class VideoRepository:
>     def save_to_database(self): pass
> ```
> 
> See: [SOLID Principles - SRP](./SOLID_PRINCIPLES.md#1-single-responsibility-principle-srp)

---

### 2. Code Duplication (DRY)

**Check**: Is there duplicated code?

**Questions to Ask**:
- Is this logic already implemented elsewhere?
- Could shared code be extracted to a utility?
- Is the duplication intentional?

**Example Issues**:

❌ **Bad** - Duplicated logic:
```python
# In multiple plugins
class YouTubePlugin:
    def format_tags(self, tags):
        return [t.strip().lower() for t in tags if t.strip()]

class RedditPlugin:
    def format_tags(self, tags):
        return [t.strip().lower() for t in tags if t.strip()]
```

**Feedback**:
> Tag formatting logic is duplicated across plugins.
> 
> **Solution**: Extract to base class or utility:
> ```python
> class SourcePlugin(ABC):
>     def format_tags(self, tags: List[str]) -> List[str]:
>         """Format tags (default implementation)."""
>         return [t.strip().lower() for t in tags if t.strip()]
> ```
> 
> See: [SOLID Principles - DRY](./SOLID_PRINCIPLES.md#dry-dont-repeat-yourself)

---

### 3. Error Handling

**Check**: Are errors handled appropriately?

**Questions to Ask**:
- Are specific exceptions caught?
- Are errors logged with context?
- Is error handling too broad or too narrow?

**Example Issues**:

❌ **Bad** - Catching all exceptions:
```python
try:
    result = api_call()
except:  # ❌ Too broad
    pass  # ❌ Swallows all errors
```

**Feedback**:
> Catching all exceptions with bare `except:` is dangerous and makes debugging difficult.
> 
> **Solution**: Catch specific exceptions and log:
> ```python
> try:
>     result = api_call()
> except requests.HTTPError as e:
>     logger.error(f"API request failed: {e}")
>     raise
> except requests.Timeout:
>     logger.warning("API timeout, will retry")
>     return None
> ```

---

### 4. Type Hints

**Check**: Are type hints present and correct?

**Questions to Ask**:
- Do all public functions have type hints?
- Are type hints accurate?
- Are complex types properly imported?

**Example Issues**:

❌ **Bad** - Missing type hints:
```python
def process_task(self, task):  # ❌ No types
    return result  # ❌ No return type
```

**Feedback**:
> Functions should have type hints for parameters and return values.
> 
> **Solution**: Add complete type hints:
> ```python
> def process_task(self, task: Task) -> TaskResult:
>     """Process a task and return result."""
>     return result
> ```
> 
> See: [Coding Conventions - Type Hints](./CODING_CONVENTIONS.md#type-hints)

---

## Testing Review

### 1. Test Coverage

**Check**: Is there adequate test coverage?

**Questions to Ask**:
- Are all public methods tested?
- Are edge cases covered?
- Are error conditions tested?
- Is coverage >80%?

**Example Issues**:

❌ **Bad** - Only happy path tested:
```python
def test_classify_simple_case():
    """Only tests one simple case."""
    result = classifier.classify(simple_idea)
    assert result.categories is not None
```

**Feedback**:
> Test coverage is insufficient. Need tests for:
> - Edge cases (empty input, very long input)
> - Error conditions (invalid data, API failures)
> - Different input types
> 
> **Solution**: Add comprehensive tests:
> ```python
> def test_classify_empty_input():
>     """Test with empty input."""
>     with pytest.raises(ValueError):
>         classifier.classify(empty_idea)
> 
> def test_classify_long_text():
>     """Test with very long text."""
>     result = classifier.classify(long_idea)
>     assert len(result.categories) > 0
> ```

---

### 2. Test Quality

**Check**: Are tests well-written and maintainable?

**Questions to Ask**:
- Do tests follow Arrange-Act-Assert?
- Are tests independent (no order dependency)?
- Are test names descriptive?
- Are fixtures used appropriately?

**Example Issues**:

❌ **Bad** - Poorly structured test:
```python
def test_something():
    # No clear structure
    x = Thing()
    x.do_stuff()
    assert x.state == "good"
    y = x.other_thing()
    assert y
```

**Feedback**:
> Test structure is unclear. Use Arrange-Act-Assert pattern and descriptive names.
> 
> **Solution**:
> ```python
> def test_worker_processes_task_successfully():
>     """Worker processes valid task and returns success result."""
>     # Arrange
>     worker = YouTubeWorker(config)
>     task = Task(id=1, task_type="youtube_video")
>     
>     # Act
>     result = worker.process_task(task)
>     
>     # Assert
>     assert result.success
>     assert result.data is not None
> ```
> 
> See: [Coding Conventions - Testing](./CODING_CONVENTIONS.md#testing-conventions)

---

## Documentation Review

### 1. Code Documentation

**Check**: Is code properly documented?

**Questions to Ask**:
- Do classes have docstrings?
- Do public methods have docstrings?
- Are docstrings in Google style?
- Are complex algorithms explained?

**Example Issues**:

❌ **Bad** - Missing docstrings:
```python
class ContentClassifier:  # ❌ No docstring
    def classify(self, idea):  # ❌ No docstring
        # Complex logic with no explanation
        pass
```

**Feedback**:
> Classes and public methods need docstrings explaining purpose, parameters, and return values.
> 
> **Solution**:
> ```python
> class ContentClassifier:
>     """Classifies content into predefined categories.
>     
>     Uses NLP techniques to analyze content and assign
>     appropriate categories.
>     
>     Attributes:
>         config: Configuration object
>         categories: List of available categories
>     """
>     
>     def classify(self, idea: IdeaInspiration) -> IdeaInspiration:
>         """Classify an idea into categories.
>         
>         Args:
>             idea: The idea to classify
>             
>         Returns:
>             IdeaInspiration with categories field populated
>             
>         Raises:
>             ValueError: If idea title is empty
>         """
>         pass
> ```
> 
> See: [Coding Conventions - Docstrings](./CODING_CONVENTIONS.md#docstrings)

---

### 2. Documentation Updates

**Check**: Is documentation updated for changes?

**Questions to Ask**:
- Does README need updating?
- Are new features documented?
- Are API changes reflected in docs?
- Are examples still accurate?

**Example Issues**:

❌ **Bad** - Outdated documentation:
```python
# New parameter added but docs not updated
def process(self, task: Task, priority: int = 5):
    pass
```

**Feedback**:
> You added a new `priority` parameter but the docstring and README weren't updated.
> 
> **Solution**:
> 1. Update function docstring to document `priority`
> 2. Update README if it shows usage examples
> 3. Update API documentation if it exists

---

## Review Checklist

### Architecture ✓

- [ ] Code is in correct layer
- [ ] Dependencies flow downward only
- [ ] No circular dependencies
- [ ] No peer dependencies (Classification ↔ Scoring)
- [ ] Dependencies are injected, not created
- [ ] Depends on abstractions, not implementations

### SOLID Principles ✓

- [ ] Single Responsibility - one reason to change
- [ ] Open/Closed - open for extension, closed for modification
- [ ] Liskov Substitution - subclasses are substitutable
- [ ] Interface Segregation - minimal, focused interfaces
- [ ] Dependency Inversion - injected dependencies

### Code Quality ✓

- [ ] Follows naming conventions
- [ ] No code duplication (DRY)
- [ ] Proper error handling
- [ ] Type hints on all public functions
- [ ] No obvious bugs or logic errors
- [ ] Appropriate complexity (KISS)
- [ ] No premature optimization (YAGNI)

### Testing ✓

- [ ] Tests exist for new code
- [ ] Test coverage >80%
- [ ] Edge cases tested
- [ ] Error conditions tested
- [ ] Tests are independent
- [ ] Test names are descriptive
- [ ] Follows Arrange-Act-Assert

### Documentation ✓

- [ ] Classes have docstrings
- [ ] Public methods have docstrings
- [ ] Complex logic is commented
- [ ] README updated if needed
- [ ] Documentation is accurate

### Performance ✓

- [ ] No obvious performance issues
- [ ] Appropriate data structures used
- [ ] No unnecessary database queries
- [ ] Efficient algorithms

---

## Common Issues and Solutions

### Issue: Circular Dependencies

**Symptoms**: Module A imports Module B, Module B imports Module A

**Solution**: 
1. Extract common code to lower layer
2. Use dependency injection
3. Redesign interface boundaries

**Example**: See [ADR-001: Dependency Rules](./decisions/ADR-001-LAYERED_ARCHITECTURE.md#dependency-rules)

---

### Issue: God Classes

**Symptoms**: Class with >500 lines, >10 methods, multiple responsibilities

**Solution**:
1. Identify distinct responsibilities
2. Extract each into separate class
3. Use composition to combine

**Example**: See [SOLID Principles - SRP](./SOLID_PRINCIPLES.md#1-single-responsibility-principle-srp)

---

### Issue: Hard-Coded Dependencies

**Symptoms**: Classes create their own dependencies in `__init__`

**Solution**:
1. Add parameters to `__init__` for dependencies
2. Pass dependencies from caller
3. Use factory pattern if construction is complex

**Example**: See [SOLID Principles - DIP](./SOLID_PRINCIPLES.md#5-dependency-inversion-principle-dip)

---

### Issue: Missing Tests

**Symptoms**: Coverage <80%, no error case tests, no edge case tests

**Solution**:
1. Write tests for all public methods
2. Test happy path and error cases
3. Test edge cases and boundary conditions
4. Use coverage tool to identify gaps

---

### Issue: Poor Documentation

**Symptoms**: No docstrings, unclear README, outdated docs

**Solution**:
1. Add Google-style docstrings to all classes/methods
2. Update README using navigation hub pattern
3. Document complex logic with comments
4. Keep examples up-to-date

---

## Providing Feedback

### Feedback Structure

**Use this template**:

1. **Observation**: What you see
2. **Impact**: Why it matters
3. **Suggestion**: How to fix
4. **Reference**: Link to documentation

**Example**:
> **Observation**: This class creates its own Config object in `__init__`.
> 
> **Impact**: This violates Dependency Inversion Principle and makes testing difficult.
> 
> **Suggestion**: Inject Config via constructor parameter:
> ```python
> def __init__(self, config: Config):
>     self.config = config
> ```
> 
> **Reference**: [SOLID Principles - DIP](./SOLID_PRINCIPLES.md#5-dependency-inversion-principle-dip)

### Tone Guidelines

**Do**:
- ✅ Be specific and constructive
- ✅ Focus on the code, not the person
- ✅ Provide examples and alternatives
- ✅ Link to documentation
- ✅ Acknowledge good work

**Don't**:
- ❌ Use accusatory language ("You always...")
- ❌ Be vague ("This doesn't look right")
- ❌ Make it personal ("I don't like this")
- ❌ Nitpick minor style issues

### Approval Guidelines

**Approve when**:
- All critical issues resolved
- Architecture is sound
- Tests are adequate
- Documentation is complete
- Minor issues can be addressed later (note them)

**Request changes when**:
- Architecture violations
- Missing critical tests
- Significant bugs
- Major SOLID violations
- Security issues

**Comment (no approval) when**:
- Suggesting improvements
- Minor style issues
- Questions for clarification
- Nice-to-have changes

---

## Conclusion

Effective code reviews:
- ✅ Enforce architectural conventions
- ✅ Maintain code quality
- ✅ Share knowledge
- ✅ Build team culture

**Remember**: The goal is to improve the code and help each other grow, not to find fault.

---

## Related Documents

- [SOLID Principles](./SOLID_PRINCIPLES.md)
- [Coding Conventions](./CODING_CONVENTIONS.md)
- [ADR-001: Layered Architecture](./decisions/ADR-001-LAYERED_ARCHITECTURE.md)
- [Contributing Guide](./CONTRIBUTING.md)

---

**Maintained By**: Architecture Team  
**Last Updated**: 2025-11-14  
**Status**: Active
