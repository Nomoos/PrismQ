# Batch Processing for Scoring and Classification Modules

## Overview

The Scoring and Classification modules now support batch processing of IdeaInspiration objects. This allows you to process multiple content items in a single operation, making it efficient for bulk processing scenarios.

## Key Features

### Scoring Module
- **Input**: List of IdeaInspiration objects (JSON array)
- **Output**: Same list with `score` field populated
- **Default behavior**: Processes all IdeaInspiration rows without a score
- **Score range**: 0-100 (integer)

### Classification Module
- **Input**: List of IdeaInspiration objects (JSON array)
- **Output**: Same list with `category` and `subcategory_relevance` fields populated
- **Default behavior**: Processes all IdeaInspiration rows without classification
- **Categories**: 8 primary categories (Storytelling, Entertainment, Education, Lifestyle, Gaming, Challenges, Reviews, Unusable)

## Usage

### Python API

#### Scoring
```python
from src.scoring import ScoringEngine
from Model.idea_inspiration import IdeaInspiration

# Initialize engine
engine = ScoringEngine()

# Create list of IdeaInspiration objects
ideas = [
    IdeaInspiration(
        title="Article 1",
        description="Description 1",
        content="Content 1...",
        keywords=["keyword1"],
        source_type=ContentType.TEXT
    ),
    # ... more ideas
]

# Score batch
score_breakdowns = engine.score_idea_inspiration_batch(ideas)

# Update original objects with scores
for idea, breakdown in zip(ideas, score_breakdowns):
    idea.score = int(breakdown.overall_score)
```

#### Classification
```python
from src.classification import TextClassifier
from Model.idea_inspiration import IdeaInspiration

# Initialize classifier
classifier = TextClassifier()

# Create list of IdeaInspiration objects
ideas = [
    IdeaInspiration(
        title="Story Title",
        description="Story description",
        content="Story content...",
        keywords=["story"],
        source_type=ContentType.TEXT
    ),
    # ... more ideas
]

# Classify batch
enrichments = classifier.enrich_batch(ideas)

# Update original objects with classifications
for idea, enrichment in zip(ideas, enrichments):
    idea.category = enrichment.category.value
    for tag in enrichment.tags:
        idea.subcategory_relevance[tag] = int(enrichment.category_confidence * 100)
```

### Command Line Interface (CLI)

Both modules provide CLI interfaces that accept JSON input via stdin and output JSON via stdout.

#### Scoring CLI
```bash
# Using echo
echo '[{"title":"Test","description":"Test","content":"Test content","keywords":[],"source_type":"text"}]' | \
  python3 Scoring/src/cli.py

# Using file
cat input.json | python3 Scoring/src/cli.py > output.json

# Using Python script
python3 test_data_generator.py | python3 Scoring/src/cli.py
```

#### Classification CLI
```bash
# Using echo
echo '[{"title":"My Story","description":"A story","content":"This happened...","keywords":["story"],"source_type":"text"}]' | \
  python3 Classification/src/cli.py

# Using file
cat input.json | python3 Classification/src/cli.py > output.json

# Using Python script
python3 test_data_generator.py | python3 Classification/src/cli.py
```

#### Combined Workflow
Process data through both modules sequentially:

```bash
# Generate test data -> Classify -> Score -> Save
python3 generate_test_data.py | \
  python3 Classification/src/cli.py | \
  python3 Scoring/src/cli.py > \
  processed_output.json
```

## JSON Format

### Input Format
```json
[
  {
    "title": "Article Title",
    "description": "Article description",
    "content": "Full article content...",
    "keywords": ["keyword1", "keyword2"],
    "source_type": "text",
    "metadata": {},
    "source_id": null,
    "source_url": null,
    "source_platform": null,
    "source_created_by": null,
    "source_created_at": null,
    "score": null,
    "category": null,
    "subcategory_relevance": {},
    "contextual_category_scores": {}
  }
]
```

### Output Format (After Scoring)
```json
[
  {
    "title": "Article Title",
    "description": "Article description",
    "content": "Full article content...",
    "keywords": ["keyword1", "keyword2"],
    "source_type": "text",
    "metadata": {},
    "source_id": null,
    "source_url": null,
    "source_platform": null,
    "source_created_by": null,
    "source_created_at": null,
    "score": 75,  // Updated
    "category": null,
    "subcategory_relevance": {},
    "contextual_category_scores": {}
  }
]
```

### Output Format (After Classification)
```json
[
  {
    "title": "My Story",
    "description": "A personal story",
    "content": "This happened to me...",
    "keywords": ["story", "personal"],
    "source_type": "text",
    "metadata": {},
    "source_id": null,
    "source_url": null,
    "source_platform": null,
    "source_created_by": null,
    "source_created_at": null,
    "score": null,
    "category": "Storytelling",  // Updated
    "subcategory_relevance": {    // Updated
      "story": 95,
      "personal": 95,
      "happened": 95
    },
    "contextual_category_scores": {}
  }
]
```

## Integration with PrismQ Modules

The modules can be registered in a module registry and can be executed through a web interface or command line.

### Module Configuration
```json
{
  "id": "scoring",
  "name": "Content Scoring",
  "description": "Score content quality and engagement metrics. Processes list of IdeaInspiration objects and returns same list with score filled.",
  "category": "Processing",
  "version": "1.0.0",
  "script_path": "../../Scoring/src/cli.py",
  "parameters": [],
  "tags": ["scoring", "processing", "quality", "engagement"],
  "status": "active",
  "enabled": true
}
```

## Testing

### Unit Tests
```bash
# Scoring batch processing tests
python3 Scoring/_meta/tests/test_batch_processing.py

# Classification batch processing tests
python3 Classification/_meta/tests/test_batch_processing.py
```

### Integration Tests
```bash
# CLI integration tests
python3 _meta/tests/test_cli_integration.py
```

### Manual Testing
```bash
# Test scoring
python3 Scoring/test_batch_input.py | python3 Scoring/src/cli.py

# Test classification
python3 Classification/test_batch_input.py | python3 Classification/src/cli.py
```

## Performance Considerations

- **Batch Size**: Both modules can handle large batches efficiently. Recommended batch size: 100-1000 items
- **Memory**: Each IdeaInspiration object consumes minimal memory (~1-5 KB depending on content size)
- **Processing Time**: 
  - Scoring: ~0.01-0.05 seconds per item
  - Classification: ~0.01-0.03 seconds per item
- **Parallelization**: Currently sequential; can be parallelized for very large batches

## Error Handling

Both CLIs handle errors gracefully:

- **Invalid JSON**: Returns error message in JSON format
- **Empty input**: Returns empty array `[]`
- **Malformed objects**: Skips invalid items and continues processing
- **Processing errors**: Logs error but continues with remaining items

## Examples

See the test files for complete examples:
- `Scoring/test_batch_input.py` - Scoring examples
- `Classification/test_batch_input.py` - Classification examples
- `_meta/tests/test_cli_integration.py` - Integration examples

## API Reference

### ScoringEngine

```python
class ScoringEngine:
    def score_idea_inspiration(self, idea_inspiration) -> ScoreBreakdown:
        """Score a single IdeaInspiration object."""
        
    def score_idea_inspiration_batch(self, idea_inspirations: List) -> List[ScoreBreakdown]:
        """Score multiple IdeaInspiration objects."""
```

### TextClassifier

```python
class TextClassifier:
    def enrich(self, inspiration: IdeaInspirationLike) -> ClassificationEnrichment:
        """Enrich a single IdeaInspiration object."""
        
    def enrich_batch(self, inspirations: List[IdeaInspirationLike]) -> List[ClassificationEnrichment]:
        """Enrich multiple IdeaInspiration objects."""
        
    def classify(self, inspiration: IdeaInspirationLike) -> ClassificationEnrichment:
        """Alias for enrich()."""
        
    def classify_batch(self, inspirations: List[IdeaInspirationLike]) -> List[ClassificationEnrichment]:
        """Alias for enrich_batch()."""
```

## Troubleshooting

### Import Errors
Make sure all required modules are in the Python path:
```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/PrismQ.T.Idea.Inspiration"
```

### Missing Dependencies
Install required dependencies:
```bash
pip install python-dotenv
```

### CLI Not Finding Modules
Run CLI from the repository root:
```bash
cd /path/to/PrismQ.T.Idea.Inspiration
python3 Scoring/src/cli.py < input.json
```

## Future Enhancements

- Database integration for bulk processing from DB
- Async/parallel processing for large batches
- Progress reporting for long-running batches
- Filtering options (e.g., only process items without scores)
- Batch update API endpoints for Web Client
