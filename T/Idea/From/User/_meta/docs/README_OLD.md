# T/Idea/From/User - AI-Powered Idea Creation Module

**Namespace**: `PrismQ.T.Idea.From.User`

The Creation module generates **10 Ideas by default** from simple inputs like titles or descriptions using **local AI models** (Ollama) optimized for RTX 5090 and other high-end GPUs. It creates rich, detailed Ideas with variable-length content and comprehensive narrative structure.

## Recent Updates ✨

**SOLID Architecture Refactoring** - Complete redesign following SOLID principles:
- **Externalized Configuration**: Flavors defined in `data/flavors.json` (39 flavors)
- **Service-Oriented**: `FlavorLoader`, `IdeaGenerator`, `FlavorSelector` classes
- **Single Responsibility**: Each class does one thing well
- **Open/Closed**: Extended through configuration, not code modification
- **Clean Separation**: Code and data in separate files
- **110% Test Coverage**: All functionality verified

**Flavors System Migration** - Transitioned from variant-centric to flavor-centric interface:
- **39 curated flavors** (streamlined from 93 variants)
- **Automatic weighted selection** optimized for primary audience (13-17 young women in US/Canada)
- **Custom audience flavors** for different demographics
- **Scoring system** rates flavors for audience fit (0.0-10.0)
- **Clean API**: Simple, intuitive function calls

**[→ See Flavors Migration Guide](./_meta/docs/FLAVORS_MIGRATION.md) for details**

## Purpose

Transform minimal input (title or description) into multiple, fully-formed Ideas with comprehensive narrative structure, targeting information, and content specifications using advanced AI models.

## Key Features

- **Flavor-Based Generation**: 110 thematic flavors with weighted selection for target audiences
- **AI-Powered Generation**: Uses local LLMs (Qwen 3.30b default, optimized for idea refinement) via Ollama
- **Direct Input Passthrough**: Input text flows directly to AI prompt without parsing, extraction, or validation
- **Audience Optimization**: Custom flavors for specific demographics (teen girls, US women, Maine youth, etc.)
- **Flavor Scoring**: Rate flavors for audience fit with automated scoring system
- **Custom Prompt Templates**: Flexible templating system with multiple placeholder formats
- **Default 10 Ideas**: Generates 10 high-quality ideas by default (Path 2: Manual Creation)
- **RTX 5090 Optimized**: Configured for best models on high-end GPUs
- **Intelligent Fallback**: Automatically falls back when AI unavailable
- **Batch Generation**: Create multiple Ideas from single input
- **Variable Length**: Generate titles and stories with flexible length
- **Multi-Format Ready**: Ideas optimized for text, audio, and video
- **Platform Targeting**: Automatic platform-specific optimization

## Quick Start

### Using Flavors (Recommended)

```python
from PrismQ.T.Idea.From.User.src.flavors import (
    get_top_flavors_for_audience,
    score_flavor_for_audience,
    list_flavors_by_audience
)

# Get top flavors for your audience
top_flavors = get_top_flavors_for_audience(
    audience='13-17 young women US/Canada',
    count=10
)

print("Top flavors for primary audience:")
for flavor in top_flavors:
    score = score_flavor_for_audience(flavor)
    print(f"  [{score:.1f}] {flavor}")

# Filter by specific audience
teen_flavors = list_flavors_by_audience('teen girls')
print(f"\nTeen girl flavors: {len(teen_flavors)}")
```

### Using Idea Creator (Original)

```python
from PrismQ.T.Idea.From.User import IdeaCreator

# Create 10 ideas (default) using local AI
creator = IdeaCreator()
ideas = creator.create_from_title("The Future of AI")

print(f"Created {len(ideas)} ideas")  # Output: Created 10 ideas
```

## AI-Powered Generation

**[→ Complete AI Generation Guide](./AI_GENERATION.md)**

### Prerequisites

1. **Install Ollama**: https://ollama.com/
2. **Pull the model**: `ollama pull qwen3:32b`
3. **Start server**: `ollama serve`

### Recommended Models

| Model | VRAM | Best For |
|-------|------|----------|
| `qwen3:32b` | ~20GB | Qwen 3 32B - idea refinement (default) |
| `qwen2.5:72b-q4_K_M` | 23GB | Creative writing (larger) |
| `llama3.1:70b-q4_K_M` | 22GB | All-around alternative |

## Workflow Position

```
Path 2: Manual Creation
    ↓
Input Text → Direct to AI Prompt (No Parsing) → 10 Candidate Ideas
    ↓
Multiple Ideas with full narrative structure
```

**Note**: Input text is passed directly to the AI prompt template without any parsing, extraction, validation, or cleaning. The AI receives your exact input text as provided.

## Usage Examples

### Example 1: Default Usage (10 Ideas with AI)

```python
from PrismQ.T.Idea.From.User import IdeaCreator

creator = IdeaCreator()

# Creates 10 ideas by default using AI
ideas = creator.create_from_title("The Future of AI")

for i, idea in enumerate(ideas, 1):
    print(f"{i}. {idea.title}")
    print(f"   Keywords: {', '.join(idea.keywords)}")
```

### Example 2: Custom Number of Ideas

```python
# Create 5 ideas instead of 10
ideas = creator.create_from_title(
    "Quantum Computing",
    num_ideas=5
)
```

### Example 3: From Description

```python
description = """
Explore the ethical implications of AI in healthcare, focusing on 
privacy concerns and algorithm bias.
"""

ideas = creator.create_from_description(
    description,
    num_ideas=10,
    genre=ContentGenre.EDUCATIONAL
)
```

### Example 4: With Platform Targeting

```python
ideas = creator.create_from_title(
    "Social Media Trends 2024",
    num_ideas=10,
    target_platforms=["youtube", "tiktok", "instagram"],
    target_formats=["video", "short-form"],
    genre=ContentGenre.ENTERTAINMENT,
    length_target="60 seconds"
)
```

### Example 5: Custom AI Configuration

```python
from PrismQ.T.Idea.From.User import IdeaCreator, CreationConfig

# Configure for RTX 5090 with specific model
config = CreationConfig(
    use_ai=True,
    ai_model="qwen2.5:72b-q4_K_M",  # Creative writing model
    ai_temperature=0.9,              # Higher creativity
    default_num_ideas=15             # More ideas
)

creator = IdeaCreator(config)
ideas = creator.create_from_title("Creative Story Ideas")
```

### Example 6: Custom Prompt Templates (New!)

The module now supports flexible custom prompt templates for advanced AI usage:

```python
from PrismQ.T.Idea.From.User.src.ai_generator import AIIdeaGenerator

# Initialize AI generator
generator = AIIdeaGenerator()

# Use a pre-made template by name
result = generator.generate_with_custom_prompt(
    input_text="The Vanishing Tide",
    prompt_template_name="idea_improvement"
)

# Or use an inline template
custom_template = """
Task: Improve this story concept.

Concept: {input}

Output an enhanced version with stronger hooks and clearer themes.
"""

result = generator.generate_with_custom_prompt(
    input_text="My story idea",
    prompt_template=custom_template
)
```

**See [CUSTOM_PROMPTS.md](./CUSTOM_PROMPTS.md) for complete guide**

### Example 7: Fallback Mode (No AI)

```python
# Disable AI to use placeholder generation
config = CreationConfig(use_ai=False)
creator = IdeaCreator(config)

ideas = creator.create_from_title("Test Topic", num_ideas=3)
```

## Configuration Options

```python
@dataclass
class CreationConfig:
    # Content length
    min_title_length: int = 20
    max_title_length: int = 100
    min_story_length: int = 100
    max_story_length: int = 1000
    
    # Variation
    variation_degree: Literal["low", "medium", "high"] = "medium"
    include_all_fields: bool = True
    
    # AI settings
    use_ai: bool = True                        # Enable AI generation
    ai_model: str = "qwen3:32b"               # Model name (Qwen 3 32B default)
    ai_temperature: float = 0.8                # Creativity (0.0-2.0)
    default_num_ideas: int = 10                # Default: 10 ideas
```

## Generated Idea Structure

Each AI-generated Idea includes:

- **Title**: Unique, compelling title
- **Concept**: Core concept or hook (1-2 sentences)
- **Premise**: Detailed explanation (2-3 sentences)
- **Logline**: One-sentence dramatic version
- **Hook**: Attention-grabbing opening
- **Synopsis**: Comprehensive summary (2-3 paragraphs)
- **Skeleton**: Key story points (5-7 items)
- **Outline**: Detailed structure with sections
- **Keywords**: 5-10 relevant keywords
- **Themes**: 3-5 main themes

## Performance

**RTX 5090 Generation Times** (10 ideas with full narratives):
- **Llama 3.1 70B**: 2-4 minutes (~15-25 tokens/sec)
- **Qwen 2.5 72B**: 2-4 minutes (~12-20 tokens/sec)
- **Command-R 35B**: 1-2 minutes (~25-35 tokens/sec)

## Module Documentation

### Core Documentation
- **[Flavors Migration Guide](./_meta/docs/FLAVORS_MIGRATION.md)** - Understanding the flavors system
- **[AI Generation Guide](./_meta/docs/AI_GENERATION.md)** - Complete AI setup and usage
- **[Custom Prompts Guide](./_meta/docs/CUSTOM_PROMPTS.md)** - Flexible templating system
- **[How It Works (CZ)](./_meta/docs/HOW_IT_WORKS.md)** - Detailed system explanation
- **[Flavor System Guide](./_meta/docs/FLAVOR_SYSTEM.md)** - Working with flavors

### Implementation & Review
- **[Implementation Notes](./_meta/docs/IMPLEMENTATION_NOTES.md)** - Technical details
- **[Implementation Summary](./_meta/docs/IMPLEMENTATION_SUMMARY.md)** - Overview
- **[Review Documents](./_meta/docs/REVIEW.md)** - Code reviews and feedback

### Reference
- **[Prompt Variations](./_meta/docs/PROMPT_VARIATIONS.md)** - Prompt engineering guide
- **[Quickstart Templates](./_meta/docs/QUICKSTART_TEMPLATES.md)** - Quick reference
- **[Qwen Model Selection](./_meta/docs/QWEN_MODEL_SELECTION.md)** - Model comparison

### External Links
- **[Local AI Setup](../Model/_meta/docs/LOCAL_AI_GENERATION.md)** - Ollama configuration

### Examples
- **[AI Examples](../_meta/examples/ai_creation_examples.py)** - Complete code examples
- **[Custom Prompt Examples](./_meta/examples/custom_prompt_example.py)** - NEW: Templating examples
- **[Usage Examples](./_meta/examples/)** - Additional examples

### Tests
- **[Test Suite](./_meta/tests/test_creation.py)** - 40 tests including AI tests
- **[Custom Prompt Tests](./_meta/tests/test_custom_prompts.py)** - NEW: 22 templating tests

## Troubleshooting

### Ollama Not Available
If Ollama is not running, the system automatically uses fallback generation:
```
WARNING: Ollama not available, using fallback
```

**Solution**: Start Ollama server: `ollama serve`

### Model Not Found
```bash
ollama pull qwen3:32b
```

### Out of Memory
Use a smaller model:
```python
config = CreationConfig(ai_model="llama3.1:13b")
```

## Navigation

**[← Back to Idea](../README.md)** | **[→ How It Works (CZ)](./HOW_IT_WORKS.md)** | **[→ AI Generation Guide](./AI_GENERATION.md)** | **[→ Model Module](../Model/)** | **[→ Fusion Module](../Fusion/)**

---

*Part of the PrismQ.T.Idea content development workflow*  
*Implements Path 2: Manual Creation with default 10 Ideas using local AI*
