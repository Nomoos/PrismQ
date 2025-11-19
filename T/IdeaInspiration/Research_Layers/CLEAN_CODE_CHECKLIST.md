# Clean Code Checklist

A practical checklist for writing clean, maintainable Python code in PrismQ.IdeaInspiration.

## Before You Write Code

### 🎯 Understand the Requirement
- [ ] I understand what problem I'm solving
- [ ] I know the expected inputs and outputs
- [ ] I've reviewed existing similar code in the project
- [ ] I've checked if a solution already exists

### 📐 Design First
- [ ] I've identified which layer this code belongs to
- [ ] I've defined the abstractions (Protocols) I'll use
- [ ] I've planned how to inject dependencies
- [ ] I've considered how to test this code

## Writing Code

### 1. Naming ✅

- [ ] **Classes**: PascalCase and noun-based
  - ✅ `VideoProcessor`, `IdeaRepository`, `CategoryClassifier`
  - ❌ `ProcessVideo`, `Ideas`, `classify_category`

- [ ] **Functions/Methods**: snake_case and verb-based
  - ✅ `calculate_score()`, `fetch_videos()`, `save_idea()`
  - ❌ `score()`, `videos()`, `idea()` (too vague)

- [ ] **Variables**: snake_case and descriptive
  - ✅ `video_count`, `max_retry_attempts`, `api_key`
  - ❌ `vc`, `mra`, `key` (too cryptic)

- [ ] **Constants**: UPPER_CASE
  - ✅ `MAX_CONNECTIONS`, `DEFAULT_TIMEOUT`, `API_BASE_URL`

- [ ] **Boolean variables**: Start with `is_`, `has_`, `can_`, `should_`
  - ✅ `is_valid`, `has_permission`, `can_retry`, `should_update`
  - ❌ `valid`, `permission`, `retry` (ambiguous)

### 2. Functions ✅

- [ ] **Single Responsibility**: Function does ONE thing
  ```python
  # ✅ GOOD: Separate responsibilities
  def fetch_video(url): pass
  def parse_video(data): pass
  def save_video(video): pass
  
  # ❌ BAD: Does too much
  def fetch_and_parse_and_save_video(url): pass
  ```

- [ ] **Function length**: Ideally < 20 lines, max 50 lines
- [ ] **Function depth**: Max 2-3 levels of nesting
  ```python
  # ❌ BAD: Too deep nesting
  if condition1:
      if condition2:
          if condition3:
              if condition4:
                  # Too deep!
  
  # ✅ GOOD: Extract or use early returns
  if not condition1:
      return
  if not condition2:
      return
  # Continue...
  ```

- [ ] **Parameters**: Max 3-4 parameters (use dataclass for more)
  ```python
  # ❌ BAD: Too many parameters
  def create_video(id, title, desc, url, duration, views, likes, dislikes):
      pass
  
  # ✅ GOOD: Use dataclass
  @dataclass
  class VideoData:
      id: str
      title: str
      # ... other fields
  
  def create_video(data: VideoData):
      pass
  ```

- [ ] **Return type**: Consistent and predictable
  - Always return same type
  - Use `Optional[T]` if might return None
  - Document what None means

### 3. Classes ✅

- [ ] **Single Responsibility**: Class has ONE reason to change
- [ ] **Composition over inheritance**: Prefer composition
- [ ] **Dependencies injected**: Don't create dependencies inside class
  ```python
  # ❌ BAD: Creates dependency inside
  class VideoService:
      def __init__(self):
          self._repository = VideoRepository()  # Hard-coded!
  
  # ✅ GOOD: Dependency injected
  class VideoService:
      def __init__(self, repository: VideoRepository):
          self._repository = repository
  ```

- [ ] **Protocol/ABC for contracts**: Define interfaces
  ```python
  # ✅ GOOD: Protocol defines contract
  class VideoRepository(Protocol):
      def save(self, video: Video) -> str: ...
  ```

### 4. Comments & Documentation ✅

- [ ] **Code is self-documenting**: Names explain intent
- [ ] **Comments explain WHY, not WHAT**
  ```python
  # ❌ BAD: States the obvious
  x = x + 1  # Increment x
  
  # ✅ GOOD: Explains why
  x = x + 1  # Account for 1-based indexing in legacy API
  ```

- [ ] **Docstrings on all public functions/classes**
  ```python
  def calculate_score(title: str, keywords: List[str]) -> float:
      """Calculate relevance score based on keyword matches.
      
      Args:
          title: Video title to analyze
          keywords: List of keywords to match
      
      Returns:
          Score between 0.0 and 1.0
      
      Example:
          >>> calculate_score("Python Tutorial", ["python", "tutorial"])
          1.0
      """
  ```

- [ ] **Type hints on all functions**
  ```python
  # ✅ GOOD: Complete type hints
  def fetch_videos(url: str, limit: int = 10) -> List[Video]:
      pass
  ```

### 5. Error Handling ✅

- [ ] **Specific exceptions**: Catch specific exceptions, not bare `except`
  ```python
  # ❌ BAD: Catches everything
  try:
      process()
  except:
      pass
  
  # ✅ GOOD: Specific exceptions
  try:
      process()
  except NetworkError as e:
      logger.error(f"Network error: {e}")
      raise ProcessingError("Failed to process") from e
  ```

- [ ] **Don't swallow errors**: Always handle or re-raise
- [ ] **Use exception chaining**: `raise ... from e`
- [ ] **Custom exceptions for domain errors**
  ```python
  class VideoNotFoundError(Exception):
      """Raised when video is not found."""
      pass
  ```

### 6. SOLID Principles ✅

- [ ] **S**ingle Responsibility: Each class has one reason to change
- [ ] **O**pen/Closed: Open for extension, closed for modification (use Protocols)
- [ ] **L**iskov Substitution: Subtypes can replace base types
- [ ] **I**nterface Segregation: Small, focused interfaces
- [ ] **D**ependency Inversion: Depend on abstractions (Protocols), inject dependencies

### 7. DRY (Don't Repeat Yourself) ✅

- [ ] **No duplicated code**: Extract common logic
  ```python
  # ❌ BAD: Duplicated
  def save_video(video):
      timestamp = datetime.now().isoformat()
      video.updated_at = timestamp
      db.save(video)
  
  def save_channel(channel):
      timestamp = datetime.now().isoformat()  # Duplicated!
      channel.updated_at = timestamp
      db.save(channel)
  
  # ✅ GOOD: Extract common logic
  def add_timestamp(obj):
      obj.updated_at = datetime.now().isoformat()
      return obj
  
  def save_video(video):
      db.save(add_timestamp(video))
  ```

- [ ] **Extract magic numbers**: Use named constants
  ```python
  # ❌ BAD: Magic numbers
  if retries > 3:
      pass
  
  # ✅ GOOD: Named constant
  MAX_RETRIES = 3
  if retries > MAX_RETRIES:
      pass
  ```

### 8. Testing ✅

- [ ] **Code is testable**: Can test in isolation
- [ ] **Dependencies are mockable**: Use protocols for dependencies
- [ ] **Test one thing at a time**: Unit tests focus on one unit
- [ ] **Test edge cases**: Empty inputs, None values, boundaries
- [ ] **Test error cases**: Invalid inputs, exceptions

## Code Review

### Self-Review Before Committing

- [ ] Run formatter: `black .`
- [ ] Run linter: `flake8 .`
- [ ] Run type checker: `mypy .`
- [ ] Run tests: `pytest`
- [ ] Review the diff: Does it make sense?
- [ ] Check for debug code: Remove `print()`, `breakpoint()`

### Reviewing Others' Code

- [ ] **Is it understandable?** Can I understand it in < 5 minutes?
- [ ] **Is it tested?** Are there unit tests?
- [ ] **Does it follow SOLID?** Check principles
- [ ] **Is it documented?** Docstrings and comments
- [ ] **Are names clear?** No cryptic abbreviations
- [ ] **Is it necessary?** Could it be simpler?

## Common Anti-Patterns to Avoid

### ❌ God Class
```python
# ❌ BAD: Does everything
class VideoManager:
    def fetch(self): pass
    def parse(self): pass
    def validate(self): pass
    def save(self): pass
    def notify(self): pass
    def log(self): pass
```

### ❌ Long Parameter List
```python
# ❌ BAD: Too many parameters
def create_video(id, title, desc, url, duration, views, likes, dislikes, tags, category):
    pass

# ✅ GOOD: Use dataclass
@dataclass
class VideoData:
    id: str
    title: str
    # ... other fields

def create_video(data: VideoData):
    pass
```

### ❌ Nested Ifs
```python
# ❌ BAD: Deep nesting
if user:
    if user.is_active:
        if user.has_permission:
            if video:
                # Do something

# ✅ GOOD: Early returns
if not user:
    return
if not user.is_active:
    return
if not user.has_permission:
    return
if not video:
    return
# Do something
```

### ❌ Mutable Default Arguments
```python
# ❌ BAD: Mutable default
def add_video(video, videos=[]):  # Dangerous!
    videos.append(video)
    return videos

# ✅ GOOD: Use None
def add_video(video, videos=None):
    if videos is None:
        videos = []
    videos.append(video)
    return videos
```

### ❌ Bare Except
```python
# ❌ BAD: Catches everything
try:
    process()
except:  # Too broad!
    pass

# ✅ GOOD: Specific exceptions
try:
    process()
except (NetworkError, TimeoutError) as e:
    logger.error(f"Error: {e}")
    raise
```

## Quick Reference Card

Print this and keep it visible:

```
CLEAN CODE CHECKLIST
====================

NAMING
✅ Classes: PascalCase (VideoProcessor)
✅ Functions: snake_case (calculate_score)
✅ Variables: snake_case (video_count)
✅ Constants: UPPER_CASE (MAX_RETRIES)
✅ Booleans: is_*, has_*, can_*

FUNCTIONS
✅ < 20 lines ideal, < 50 max
✅ < 4 parameters
✅ Single responsibility
✅ Type hints on everything
✅ Docstring on public functions

CLASSES
✅ Single responsibility
✅ Inject dependencies
✅ Use Protocols for contracts
✅ Composition over inheritance

CODE QUALITY
✅ DRY - Don't Repeat Yourself
✅ KISS - Keep It Simple
✅ YAGNI - You Aren't Gonna Need It
✅ SOLID - All 5 principles

BEFORE COMMIT
✅ black . (format)
✅ flake8 . (lint)
✅ mypy . (type check)
✅ pytest (test)
✅ Review diff
```

## Resources

- **SOLID Principles**: `02_Design_Patterns/01_SOLID_PRINCIPLES_GUIDE.md`
- **PEP 8 Standards**: `PEP8_STANDARDS.md`
- **Code Examples**: `02_Design_Patterns/examples/`
- **Testing Guide**: `03_Testing/TESTING_STRATEGY.md`

## Daily Practice

1. **Read clean code**: Review examples in this repo
2. **Write clean code**: Apply principles in your work
3. **Review code**: Use this checklist for reviews
4. **Refactor**: Improve code you touch
5. **Share**: Teach others these principles

---

**Remember**: Clean code is not written once - it's refactored continuously.
**Goal**: Code that is easy to read, understand, modify, and test.

**Last Updated**: 2025-11-14
