# Classification Module - API Reference

## CategoryClassifier

Primary category classifier for content.

### Class Definition

```python
class CategoryClassifier:
    """Classifies content into primary categories optimized for short-form video."""
```

### Methods

#### `classify()`

Classify content based on text fields.

```python
def classify(
    title: str,
    description: str = "",
    tags: List[str] = None,
    subtitle_text: str = ""
) -> CategoryResult
```

**Parameters:**
- `title` (str): Content title (required)
- `description` (str): Content description (optional)
- `tags` (List[str]): Content tags/keywords (optional)
- `subtitle_text` (str): Subtitle or transcript text (optional)

**Returns:**
- `CategoryResult`: Named tuple with classification results

**Example:**
```python
result = classifier.classify(
    title="My AITA Story",
    description="True story about...",
    tags=['story', 'aita'],
    subtitle_text="Let me tell you..."
)
```

#### `classify_from_metadata()`

Classify content from metadata dictionary.

```python
def classify_from_metadata(metadata: Dict) -> CategoryResult
```

**Parameters:**
- `metadata` (Dict): Dictionary containing title, description, tags, subtitle_text

**Returns:**
- `CategoryResult`: Named tuple with classification results

**Example:**
```python
result = classifier.classify_from_metadata({
    'title': 'Gaming Highlights',
    'tags': ['gaming', 'gameplay']
})
```

## StoryDetector

Binary classifier for story-based content.

### Class Definition

```python
class StoryDetector:
    """Detects if content contains story elements."""
    
    def __init__(confidence_threshold: float = 0.3):
        """Initialize detector with confidence threshold."""
```

### Methods

#### `detect()`

Detect if content is a story.

```python
def detect(
    title: str,
    description: str = "",
    tags: List[str] = None,
    subtitle_text: str = ""
) -> Tuple[bool, float, List[str]]
```

**Parameters:**
- `title` (str): Content title (required)
- `description` (str): Content description (optional)
- `tags` (List[str]): Content tags/keywords (optional)
- `subtitle_text` (str): Subtitle or transcript text (optional)

**Returns:**
- Tuple of:
  - `is_story` (bool): Whether content is a story
  - `confidence` (float): Confidence score (0.0-1.0)
  - `indicators` (List[str]): Matched story indicators

**Example:**
```python
is_story, confidence, indicators = detector.detect(
    title="My True Story",
    tags=['storytime']
)
```

#### `detect_from_metadata()`

Detect story from metadata dictionary.

```python
def detect_from_metadata(metadata: Dict) -> Tuple[bool, float, List[str]]
```

## TextClassifier

Unified text classifier working with IdeaInspiration model.

### Class Definition

```python
class TextClassifier:
    """Generalized text classifier for IdeaInspiration objects."""
```

### Methods

#### `classify()`

Classify IdeaInspiration object.

```python
def classify(inspiration: IdeaInspiration) -> TextClassificationResult
```

**Parameters:**
- `inspiration` (IdeaInspiration): IdeaInspiration object to classify

**Returns:**
- `TextClassificationResult`: Detailed classification results

## Data Models

### PrimaryCategory (Enum)

```python
class PrimaryCategory(Enum):
    STORYTELLING = "Storytelling"
    ENTERTAINMENT = "Entertainment"
    EDUCATION = "Education / Informational"
    LIFESTYLE = "Lifestyle / Vlog"
    GAMING = "Gaming"
    CHALLENGES_TRENDS = "Challenges & Trends"
    REVIEWS_COMMENTARY = "Reviews & Commentary"
    UNUSABLE = "Unusable"
```

**Properties:**
- `is_usable_for_stories` (bool): Whether category is usable for story generation
- `description` (str): Detailed category description

### CategoryResult (NamedTuple)

```python
class CategoryResult(NamedTuple):
    category: PrimaryCategory          # Primary category
    confidence: float                  # Confidence score (0.0-1.0)
    indicators: List[str]              # List of matched indicators
    secondary_matches: Dict[PrimaryCategory, float]  # Other category matches
```

### IdeaInspiration

```python
class IdeaInspiration:
    """Unified data model for content across different media types."""
    
    title: str
    description: str
    content: str
    keywords: List[str]
    source_type: str  # 'text', 'video', 'audio'
    # ... additional fields
```

### IdeaInspirationExtractor

```python
class IdeaInspirationExtractor:
    """Extract IdeaInspiration from different source types."""
    
    def extract_from_video(...) -> IdeaInspiration
    def extract_from_text(...) -> IdeaInspiration
    def extract_from_audio(...) -> IdeaInspiration
```

### IdeaInspirationBuilder

```python
class IdeaInspirationBuilder:
    """Build IdeaInspiration objects with fluent API."""
    
    def set_title(title: str) -> IdeaInspirationBuilder
    def set_description(description: str) -> IdeaInspirationBuilder
    def set_content(content: str) -> IdeaInspirationBuilder
    def add_keyword(keyword: str) -> IdeaInspirationBuilder
    def set_source_type(source_type: str) -> IdeaInspirationBuilder
    def build() -> IdeaInspiration
```

## Version History

- **v2.1.0** - Added generalized text classification with IdeaInspiration model
- **v2.0.0** - Added primary category classifier with 8-category taxonomy
- **v1.0.0** - Initial story detector from YouTubeShortsSource migration

## Support

For complete examples and detailed documentation, see:
- [User Guide](./USER_GUIDE.md)
- [Setup Guide](./SETUP.md)
- [GitHub Repository](https://github.com/PrismQDev/PrismQ.IdeaInspiration.Classification)
