# Qwen Model Comparison and Selection

## Hardware Context
- **Target GPU**: NVIDIA RTX 5090
- **VRAM**: 32GB

## Selected Model: qwen3:32b

### Model Specifications

- **Parameters**: 32 billion
- **Architecture**: Qwen 3 (latest generation)
- **VRAM Usage**: ~18-20GB (4-bit quantization)
- **Context Window**: 128K tokens
- **Release**: Latest Qwen 3 generation
- **Best For**: Balanced performance, idea refinement, structured output
- **Ollama Pull**: `ollama pull qwen3:32b`

## Model Performance

| Feature | qwen3:32b |
|---------|-----------|
| Parameters | 32B |
| VRAM (4-bit) | ~18-20GB |
| RTX 5090 Compatible | ✅ Yes (32GB available) |
| Context Length | 128K |
| Generation Speed | Excellent |
| Prompt Following | Excellent |
| Structured Output | Excellent |
| Idea Refinement | Excellent |

## Why qwen3:32b?

**Use `qwen3:32b`** as the default model for the following reasons:

1. **Official Model**: `qwen3:32b` is the official Qwen 3 model designation for Ollama
2. **Perfect Fit**: 18-20GB VRAM usage fits comfortably in RTX 5090's 32GB
3. **Latest Generation**: Qwen 3 architecture with improved instruction following
4. **Optimized for Tasks**: 
   - Idea refinement and rewriting
   - Structured 5-sentence output
   - Conceptual analysis without descriptive drift
   - Flavor-guided generation

5. **Performance**: 
   - Fast inference on RTX 5090
   - Excellent prompt adherence
   - Minimal hallucination
   - Strong reasoning capabilities

## Model Naming

- **Ollama**: `qwen3:32b`
- **HuggingFace**: `Qwen/Qwen3-32B`
- **Parameters**: 32 billion
- **Version**: Qwen 3 (third generation)

## Setup Command

```bash
ollama pull qwen3:32b
ollama serve
```

## Configuration

```python
from ai_generator import AIConfig

config = AIConfig(
    model="qwen3:32b",  # Default model for RTX 5090
    temperature=0.8,
    max_tokens=2000
)
```

## Conclusion

**Default Model: `qwen3:32b`**

This is the optimal choice for:
- RTX 5090 with 32GB VRAM
- Idea refinement workflows
- Prompt templates optimized for Qwen 3
- Production use with weighted flavor selection
- All PrismQ modules (Idea, Title, Script generation)
