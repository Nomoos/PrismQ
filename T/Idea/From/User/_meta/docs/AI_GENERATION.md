# AI-Powered Idea Creation with Local LLMs

**Generate 10 Ideas by default from topics/descriptions using local AI models optimized for RTX 5090**

This guide covers how to use the AI-powered Idea Creation module to generate multiple, high-quality Ideas using local Large Language Models (LLMs) through Ollama.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Configuration](#configuration)
4. [Usage Examples](#usage-examples)
5. [AI Models for RTX 5090](#ai-models-for-rtx-5090)
6. [Fallback Mode](#fallback-mode)
7. [API Reference](#api-reference)

---

## Quick Start

```python
from PrismQ.T.Idea.From.User import IdeaCreator

# Create 10 ideas (default) using local AI
creator = IdeaCreator()
ideas = creator.create_from_title("The Future of AI")

print(f"Created {len(ideas)} ideas")  # Output: Created 10 ideas
```

---

## Prerequisites

### 1. Install Ollama

**Linux/macOS:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download and install from [ollama.com/download](https://ollama.com/download)

### 2. Download an AI Model

For RTX 5090 (recommended):
```bash
# Best overall quality (22GB VRAM)
ollama pull llama3.1:70b-q4_K_M

# Best for creative writing (23GB VRAM)
ollama pull qwen2.5:72b-q4_K_M

# Fast with great instruction following (18GB VRAM)
ollama pull command-r:35b
```

For smaller GPUs:
```bash
# Good quality, lower memory (8GB VRAM)
ollama pull llama3.2:8b

# Balanced performance (16GB VRAM)
ollama pull llama3.1:13b
```

### 3. Start Ollama Server

```bash
ollama serve
```

The server runs on `http://localhost:11434` by default.

---

## Configuration

### Default Configuration (RTX 5090 Optimized)

```python
from PrismQ.T.Idea.From.User import IdeaCreator, CreationConfig

# Default config: 10 ideas, AI enabled, Llama 3.1 70B
config = CreationConfig(
    use_ai=True,                        # Enable AI generation
    ai_model="llama3.1:70b-q4_K_M",    # Model name
    ai_temperature=0.8,                 # Creativity (0.0-2.0)
    default_num_ideas=10                # Default number of ideas
)

creator = IdeaCreator(config)
```

### Custom Configuration

```python
# Use a different model
config = CreationConfig(
    ai_model="qwen2.5:72b-q4_K_M",     # Creative writing model
    ai_temperature=0.9,                 # Higher creativity
    default_num_ideas=15                # More ideas
)

# Disable AI (use fallback)
config = CreationConfig(use_ai=False)

# Custom story length
config = CreationConfig(
    min_story_length=200,               # Longer synopses
    max_story_length=2000
)
```

---

## Usage Examples

### Example 1: Default Usage (10 Ideas)

```python
from PrismQ.T.Idea.From.User import IdeaCreator

creator = IdeaCreator()

# Creates 10 ideas by default
ideas = creator.create_from_title("The Future of AI")

for i, idea in enumerate(ideas, 1):
    print(f"\n{i}. {idea.title}")
    print(f"   Concept: {idea.concept}")
    print(f"   Keywords: {', '.join(idea.keywords)}")
```

### Example 2: Custom Number of Ideas

```python
# Create 5 ideas instead of 10
ideas = creator.create_from_title(
    "Quantum Computing Explained",
    num_ideas=5
)
```

### Example 3: From Description

```python
description = """
Explore the ethical implications of AI in healthcare, focusing on 
privacy concerns, bias in algorithms, and the balance between 
innovation and patient safety.
"""

ideas = creator.create_from_description(
    description,
    num_ideas=10
)
```

### Example 4: With Platform Targeting

```python
from PrismQ.T.Idea.Model import ContentGenre

ideas = creator.create_from_title(
    "Social Media Trends 2024",
    num_ideas=10,
    target_platforms=["youtube", "tiktok", "instagram"],
    target_formats=["video", "short-form"],
    genre=ContentGenre.ENTERTAINMENT,
    length_target="60 seconds"
)
```

### Example 5: Batch Processing

```python
topics = [
    "AI in Education",
    "Sustainable Technology", 
    "Future of Work"
]

all_ideas = []
for topic in topics:
    ideas = creator.create_from_title(topic, num_ideas=3)
    all_ideas.extend(ideas)

print(f"Created {len(all_ideas)} total ideas")  # 9 ideas
```

---

## AI Models for RTX 5090

### Recommended Models (24GB+ VRAM)

| Model | VRAM | Speed | Best For |
|-------|------|-------|----------|
| **llama3.1:70b-q4_K_M** | 22GB | 15-25 tok/s | All-around best |
| **qwen2.5:72b-q4_K_M** | 23GB | 12-20 tok/s | Creative writing |
| **command-r:35b** | 18GB | 25-35 tok/s | Structured output |
| **mixtral:8x7b-q4_K_M** | 20GB | 20-30 tok/s | Balanced performance |

### Alternative Models

```python
# For lower memory systems (12-16GB VRAM)
config = CreationConfig(ai_model="llama3.1:13b")

# For fastest generation (8GB VRAM)
config = CreationConfig(ai_model="llama3.2:8b")

# For technical content
config = CreationConfig(ai_model="deepseek-coder:33b-q4_K_M")
```

---

## Fallback Mode

When Ollama is not available, the system automatically falls back to placeholder generation:

```python
# AI will be attempted first, then fallback automatically
creator = IdeaCreator()
ideas = creator.create_from_title("My Topic")

# Or explicitly disable AI
config = CreationConfig(use_ai=False)
creator = IdeaCreator(config)
```

**Fallback Behavior:**
- Uses template-based generation
- Still creates all narrative fields
- Suitable for testing and development
- Lower quality than AI generation

---

## API Reference

### IdeaCreator

```python
class IdeaCreator:
    """Create Ideas using AI or fallback generation."""
    
    def __init__(self, config: Optional[CreationConfig] = None):
        """Initialize with optional configuration."""
    
    def create_from_title(
        self,
        title: str,
        num_ideas: int = None,  # Default: 10 from config
        target_platforms: Optional[List[str]] = None,
        target_formats: Optional[List[str]] = None,
        genre: Optional[ContentGenre] = None,
        length_target: Optional[str] = None,
        **kwargs
    ) -> List[Idea]:
        """Create multiple Ideas from a title."""
    
    def create_from_description(
        self,
        description: str,
        num_ideas: int = None,  # Default: 10 from config
        target_platforms: Optional[List[str]] = None,
        target_formats: Optional[List[str]] = None,
        genre: Optional[ContentGenre] = None,
        length_target: Optional[str] = None,
        **kwargs
    ) -> List[Idea]:
        """Create multiple Ideas from a description."""
```

### CreationConfig

```python
@dataclass
class CreationConfig:
    """Configuration for idea creation."""
    
    # Content length
    min_title_length: int = 20
    max_title_length: int = 100
    min_story_length: int = 100
    max_story_length: int = 1000
    
    # Variation
    variation_degree: Literal["low", "medium", "high"] = "medium"
    include_all_fields: bool = True
    
    # AI settings
    use_ai: bool = True
    ai_model: str = "llama3.1:70b-q4_K_M"
    ai_temperature: float = 0.8
    default_num_ideas: int = 10  # Default: 10 ideas
```

### AIConfig

```python
@dataclass
class AIConfig:
    """AI model configuration."""
    
    model: str = "llama3.1:70b-q4_K_M"
    api_base: str = "http://localhost:11434"
    temperature: float = 0.8
    max_tokens: int = 2000
    timeout: int = 120
```

---

## Performance Tips

### RTX 5090 Optimization

1. **Use quantized models** (q4_K_M) for best balance of quality/speed
2. **Set appropriate temperature**: 0.7-0.8 for balanced, 0.9-1.0 for creative
3. **Monitor VRAM usage**: Keep 2-3GB free for system operations
4. **Use batch processing**: Generate multiple topics in sequence

### Generation Speed

- **Llama 3.1 70B**: ~15-25 tokens/sec on RTX 5090
- **Qwen 2.5 72B**: ~12-20 tokens/sec on RTX 5090
- **Command-R 35B**: ~25-35 tokens/sec on RTX 5090

Generating 10 ideas with full narratives typically takes:
- **70B models**: 2-4 minutes
- **35B models**: 1-2 minutes
- **13B models**: 30-60 seconds

---

## Troubleshooting

### Ollama Connection Errors

```
WARNING: Ollama not available: Connection refused
```

**Solution:**
1. Ensure Ollama is installed
2. Start the server: `ollama serve`
3. Check it's running: `curl http://localhost:11434/api/tags`

### Model Not Found

```
RuntimeError: Failed to generate ideas: model not found
```

**Solution:**
```bash
ollama pull llama3.1:70b-q4_K_M
```

### Out of Memory

```
Error: CUDA out of memory
```

**Solution:**
- Use a smaller model (e.g., `llama3.1:13b`)
- Reduce max_tokens in config
- Close other GPU-intensive applications

---

## See Also

- **[AI Generation Examples](../_meta/examples/ai_creation_examples.py)** - Complete code examples
- **[Local AI Generation Guide](../../../Model/_meta/docs/LOCAL_AI_GENERATION.md)** - Ollama setup guide
- **[Creation Tests](../_meta/tests/test_creation.py)** - Test suite with examples
- **[Main README](../README.md)** - Creation module overview

---

## License

Part of PrismQ - Proprietary - All Rights Reserved - Copyright (c) 2025
