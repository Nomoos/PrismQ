# T/Idea/Creation - AI-Powered Idea Creation Module

**Namespace**: `PrismQ.T.Idea.Creation`

The Creation module generates **10 Ideas by default** from simple inputs like titles or descriptions using **local AI models** (Ollama) optimized for RTX 5090 and other high-end GPUs. It creates rich, detailed Ideas with variable-length content and comprehensive narrative structure.

## Purpose

Transform minimal input (title or description) into multiple, fully-formed Ideas with comprehensive narrative structure, targeting information, and content specifications using advanced AI models.

## Key Features

- **AI-Powered Generation**: Uses local LLMs (Llama 3.1 70B, Qwen 2.5, etc.) via Ollama
- **Default 10 Ideas**: Generates 10 high-quality ideas by default (Path 2: Manual Creation)
- **RTX 5090 Optimized**: Configured for best models on high-end GPUs
- **Intelligent Fallback**: Automatically falls back when AI unavailable
- **Batch Generation**: Create multiple Ideas from single input
- **Variable Length**: Generate titles and stories with flexible length
- **Multi-Format Ready**: Ideas optimized for text, audio, and video
- **Platform Targeting**: Automatic platform-specific optimization

## Quick Start

```python
from PrismQ.T.Idea.Creation import IdeaCreator

# Create 10 ideas (default) using local AI
creator = IdeaCreator()
ideas = creator.create_from_title("The Future of AI")

print(f"Created {len(ideas)} ideas")  # Output: Created 10 ideas
```

## AI-Powered Generation

**[→ Complete AI Generation Guide](./AI_GENERATION.md)**

### Prerequisites

1. **Install Ollama**: https://ollama.com/
2. **Pull a model**: `ollama pull llama3.1:70b-q4_K_M`
3. **Start server**: `ollama serve`

### Recommended Models for RTX 5090

| Model | VRAM | Best For |
|-------|------|----------|
| `llama3.1:70b-q4_K_M` | 22GB | All-around best (default) |
| `qwen2.5:72b-q4_K_M` | 23GB | Creative writing |
| `command-r:35b` | 18GB | Structured output |

## Workflow Position

```
Path 2: Manual Creation
    ↓
Title/Description → AI Generation (Ollama) → 10 Candidate Ideas
    ↓
Multiple Ideas with full narrative structure
```

## Usage Examples

### Example 1: Default Usage (10 Ideas with AI)

```python
from PrismQ.T.Idea.Creation import IdeaCreator

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
from PrismQ.T.Idea.Creation import IdeaCreator, CreationConfig

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

### Example 6: Fallback Mode (No AI)

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
    ai_model: str = "llama3.1:70b-q4_K_M"     # Model name
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

## Module Metadata

### Documentation
- **[AI Generation Guide](./AI_GENERATION.md)** - Complete AI setup and usage
- **[Local AI Setup](../Model/_meta/docs/LOCAL_AI_GENERATION.md)** - Ollama configuration

### Examples
- **[AI Examples](../_meta/examples/ai_creation_examples.py)** - Complete code examples
- **[Usage Examples](./_meta/examples/)** - Additional examples

### Tests
- **[Test Suite](./_meta/tests/test_creation.py)** - 40 tests including AI tests

## Troubleshooting

### Ollama Not Available
If Ollama is not running, the system automatically uses fallback generation:
```
WARNING: Ollama not available, using fallback
```

**Solution**: Start Ollama server: `ollama serve`

### Model Not Found
```bash
ollama pull llama3.1:70b-q4_K_M
```

### Out of Memory
Use a smaller model:
```python
config = CreationConfig(ai_model="llama3.1:13b")
```

## Navigation

**[← Back to Idea](../README.md)** | **[→ AI Generation Guide](./AI_GENERATION.md)** | **[→ Model Module](../Model/)** | **[→ Fusion Module](../Fusion/)**

---

*Part of the PrismQ.T.Idea content development workflow*  
*Implements Path 2: Manual Creation with default 10 Ideas using local AI*
