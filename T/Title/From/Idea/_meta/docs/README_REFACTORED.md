# PrismQ.T.Title.From.Idea - AI Title Generation Module

## Overview

This module generates emotionally resonant, book-style titles from Ideas using AI. The module has been refactored following SOLID principles with small, single-purpose files.

## ⚠️ Important: AI-Only Title Generation

**The literary-focused AI prompt is the ONLY approved method for generating titles in this system.**

Template-based title generation (`title_generator.py`) is **DEPRECATED** and should not be used for new code.

## Architecture

The module follows SOLID principles with clear separation of concerns:

```
T/Title/From/Idea/src/
├── ai_title_generator.py      # Main orchestrator (USE THIS)
├── prompt_loader.py            # Prompt template loading
├── ollama_client.py            # Ollama API communication
├── title_scorer.py             # Title quality scoring
├── title_variant.py            # Title data model
├── title_generator.py          # DEPRECATED (template-based)
└── story_title_service.py      # Story workflow integration
```

### Module Responsibilities

| Module | Responsibility | Lines | Purpose |
|--------|---------------|-------|---------|
| `ai_title_generator.py` | Orchestration | ~280 | Coordinates title generation workflow |
| `prompt_loader.py` | File I/O | ~60 | Loads prompt templates from disk |
| `ollama_client.py` | API Communication | ~115 | Handles Ollama HTTP requests |
| `title_scorer.py` | Evaluation | ~107 | Scores title quality |
| `title_variant.py` | Data Model | ~40 | Represents title variants |

## SOLID Principles Applied

### Single Responsibility Principle
Each class has exactly one reason to change:
- `PromptLoader`: Only changes if prompt file format changes
- `OllamaClient`: Only changes if API interface changes
- `TitleScorer`: Only changes if scoring criteria change
- `AITitleGenerator`: Only changes if workflow changes

### Open/Closed Principle
Components are open for extension but closed for modification:
- Dependency injection allows replacing components without changing code
- New scoring strategies can be added by extending `TitleScorer`
- New prompt sources can be added by extending `PromptLoader`

### Dependency Inversion Principle
High-level module (`AITitleGenerator`) depends on abstractions:
- Injects `OllamaClient`, `PromptLoader`, `TitleScorer` as dependencies
- Can swap implementations for testing or different providers

## Usage

### Basic Usage

```python
from T.Title.From.Idea.src import AITitleGenerator
from T.Idea.Model.src.idea import Idea

# Create an idea
idea = Idea(
    title="Pet Connection",
    concept="A story about a pet who understands unspoken emotions..."
)

# Generate titles
generator = AITitleGenerator()
variants = generator.generate_from_idea(idea, num_variants=5)

# Use the titles
for variant in variants:
    print(f"{variant.text} (score: {variant.score:.2f}, style: {variant.style})")
```

### Advanced Usage with Dependency Injection

```python
from T.Title.From.Idea.src import (
    AITitleGenerator,
    OllamaClient,
    OllamaConfig,
    PromptLoader,
    TitleScorer,
    ScoringConfig
)

# Custom Ollama configuration
ollama_config = OllamaConfig(
    model="llama3:70b",
    api_base="http://localhost:11434",
    timeout=120
)
ollama_client = OllamaClient(ollama_config)

# Custom scoring configuration
scoring_config = ScoringConfig(
    ideal_length_min=40,
    ideal_length_max=60
)
scorer = TitleScorer(scoring_config)

# Inject dependencies
generator = AITitleGenerator(
    ollama_client=ollama_client,
    scorer=scorer
)

variants = generator.generate_from_idea(idea)
```

### Convenience Function

```python
from T.Title.From.Idea.src import generate_titles_from_idea

# Quick generation with defaults
variants = generate_titles_from_idea(idea, num_variants=10)
```

## The Literary-Focused Prompt

The module uses a carefully crafted prompt that emphasizes:

- **Emotional essence** over plot description
- **Symbolism and subtext** over literal meaning
- **Book-style, intimate titles** for narrative videos
- **Metaphor and dual meaning**
- **Atmospheric mood** and internal conflict

The prompt generates titles in the 45-52 character range (ideal for short-form video platforms) that feel like they belong on haunting, intimate novels.

## Configuration

### TitleGeneratorConfig

```python
@dataclass
class TitleGeneratorConfig:
    num_variants: int = 10           # Number of titles to generate
    temperature_min: float = 0.6     # Minimum randomization
    temperature_max: float = 0.8     # Maximum randomization
```

### OllamaConfig

```python
@dataclass
class OllamaConfig:
    model: str = "qwen3:32b"         # Ollama model name
    api_base: str = "http://localhost:11434"  # API endpoint
    max_tokens: int = 2000           # Maximum response length
    timeout: int = 60                # Request timeout (seconds)
```

### ScoringConfig

```python
@dataclass
class ScoringConfig:
    ideal_length_min: int = 45       # Ideal minimum length
    ideal_length_max: int = 52       # Ideal maximum length
    ideal_score: float = 0.95        # Score for ideal titles
    # ... more scoring thresholds
```

## Error Handling

The module uses `AIUnavailableError` to indicate when title generation cannot proceed:

```python
from T.Title.From.Idea.src import AITitleGenerator, AIUnavailableError

generator = AITitleGenerator()

try:
    variants = generator.generate_from_idea(idea)
except AIUnavailableError as e:
    print(f"AI service unavailable: {e}")
    # Wait and retry, or alert user
```

## Testing

The module includes comprehensive tests for all components:

```bash
# Run all tests
pytest T/Title/From/Idea/_meta/tests/

# Run specific test file
pytest T/Title/From/Idea/_meta/tests/test_refactored_modules.py

# Run with verbose output
pytest T/Title/From/Idea/_meta/tests/ -v
```

## Migration from Template-Based Generation

If you're using the old `TitleGenerator` class, migrate to `AITitleGenerator`:

### Before (DEPRECATED)
```python
from T.Title.From.Idea.src import TitleGenerator

generator = TitleGenerator()
variants = generator.generate_from_idea(idea)
```

### After (RECOMMENDED)
```python
from T.Title.From.Idea.src import AITitleGenerator

generator = AITitleGenerator()
variants = generator.generate_from_idea(idea)
```

The `TitleVariant` data model remains the same, so existing code that uses variants will continue to work.

## Requirements

- Python 3.8+
- Ollama running locally with qwen3:32b model (or custom model)
- requests library for HTTP communication

## Development

### Adding a New Component

Thanks to dependency injection, adding new components is straightforward:

1. Create a new class following Single Responsibility Principle
2. Inject it into `AITitleGenerator` constructor
3. Use it in the generation workflow

Example: Adding a custom title filter:

```python
class TitleFilter:
    def filter(self, variants: List[TitleVariant]) -> List[TitleVariant]:
        # Custom filtering logic
        return filtered_variants

# Use it
generator = AITitleGenerator(title_filter=TitleFilter())
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests with coverage
pytest T/Title/From/Idea/_meta/tests/ --cov=T/Title/From/Idea/src
```

## Future Enhancements

Potential improvements that maintain SOLID principles:

- **Multiple prompt strategies**: Create `PromptStrategy` interface with implementations
- **Title validation**: Add `TitleValidator` component for quality checks
- **Caching layer**: Add `TitleCache` to reduce API calls
- **Async generation**: Support concurrent title generation

All can be added through dependency injection without modifying existing code.

## Support

For issues or questions:
1. Check the test files for usage examples
2. Review the inline documentation in each module
3. Consult the main PrismQ documentation

## License

Part of the PrismQ project.
