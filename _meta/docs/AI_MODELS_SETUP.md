# AI Models Setup Guide

**Document Type**: Setup Guide  
**Scope**: Project-wide  
**Last Updated**: 2025-12-05

## Overview

PrismQ uses local LLM models through Ollama for AI-powered content generation and SEO metadata optimization. This guide covers how to set up Ollama and configure AI models for use with PrismQ.

## Prerequisites

- Windows, macOS, or Linux operating system
- At least 16GB RAM (32GB recommended for larger models)
- GPU with sufficient VRAM for model inference (optional but recommended)
- Stable internet connection for model downloads

## Step 1 – Install Ollama

Download and install Ollama from the official website:

**Download Link**: https://ollama.com/download

### Windows Installation
1. Download the Windows installer from the link above
2. Run the installer and follow the prompts
3. Ollama will be available as a system service

### macOS Installation
1. Download the macOS app from the link above
2. Drag Ollama to your Applications folder
3. Launch Ollama from Applications

### Linux Installation
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Step 2 – Pull the Qwen2.5-14B Model

Ollama has an official Qwen2.5 entry in its library, including a 14B variant. This is the recommended model for PrismQ content generation tasks.

In your terminal, run:

```bash
ollama pull qwen2.5:14b
```

This will download approximately 9GB of model weights. The download time depends on your internet connection speed.

### Alternative Models

Depending on your hardware capabilities, you can also use these models:

| Model | Size | VRAM Required | Use Case |
|-------|------|---------------|----------|
| `qwen2.5:7b` | ~4.5GB | 8GB | Lighter weight, faster inference |
| `qwen2.5:14b` | ~9GB | 16GB | **Recommended** - Best balance of quality and speed |
| `qwen2.5:32b` | ~20GB | 24GB+ | Highest quality, requires high-end GPU |
| `llama3.1:70b-q4_K_M` | ~40GB | 48GB+ | SEO-specific tasks (used in Keywords module) |

## Step 3 – Test the Model

After the download finishes, verify the installation:

```bash
ollama run qwen2.5:14b
```

You'll enter an interactive prompt. Try a test query:

```
Write a dark, emotional horror story opening set in a small Czech town at night.
```

If it responds with a story, Qwen2.5-14B is correctly installed. Type `/bye` to exit.

## Step 4 – Python Integration

### Install the Ollama Python Package

```bash
pip install ollama
```

### Minimal Python Script

Create a file named `story_test.py`:

```python
import ollama

prompt = "Write the first 500 words of a psychological horror story told in first person."

response = ollama.chat(
    model="qwen2.5:14b",
    messages=[
        {"role": "user", "content": prompt}
    ]
)

print(response["message"]["content"])
```

Run it:

```bash
python story_test.py
```

This directly uses your local Qwen2.5-14B via Ollama's HTTP API on `localhost:11434`.

## PrismQ Integration

### Using AI in SEO Metadata Generation

PrismQ's SEO Keywords module already supports Ollama integration. Example usage:

```python
from T.Publishing.SEO.Keywords import process_content_seo, AIConfig

# Configure to use Qwen2.5-14B
config = AIConfig(
    model="qwen2.5:14b",
    api_base="http://localhost:11434",
    temperature=0.3,
    enable_ai=True
)

result = process_content_seo(
    title="Your Content Title",
    script="Your content script...",
    use_ai=True,
    ai_config=config,
    brand_name="Your Brand"
)

print(result['meta_description'])
print(result['title_tag'])
```

### Default AI Configuration

The default configuration in PrismQ uses:
- **Model**: `llama3.1:70b-q4_K_M` (for SEO tasks)
- **API Base**: `http://localhost:11434`
- **Temperature**: 0.3 (lower for more consistent output)

You can customize these settings using the `AIConfig` class.

## Troubleshooting

### Ollama Not Running

If you see errors about Ollama being unavailable:

1. **Windows**: Check if Ollama is running in the system tray
2. **macOS**: Launch Ollama from Applications
3. **Linux**: Start the service with `ollama serve`

### Model Not Found

If a model is not found, pull it first:

```bash
ollama pull qwen2.5:14b
```

### Out of Memory Errors

If you encounter memory errors:
- Use a smaller model variant (e.g., `qwen2.5:7b` instead of `qwen2.5:14b`)
- Close other GPU-intensive applications
- Increase system swap space

### Slow Response Times

For faster inference:
- Ensure you're using GPU acceleration (NVIDIA CUDA or Apple Metal)
- Consider using quantized model variants
- Reduce `max_tokens` in the configuration

## API Reference

Ollama exposes a REST API at `http://localhost:11434`. Key endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/generate` | POST | Generate text completion |
| `/api/chat` | POST | Chat-style completion |
| `/api/tags` | GET | List available models |
| `/api/pull` | POST | Download a model |

### Example API Call

```python
import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen2.5:14b",
        "prompt": "Write a short story about...",
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 500
        }
    },
    timeout=30
)

result = response.json()
print(result["response"])
```

## Related Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System architecture overview
- **[T Module README](../../T/README.md)** - Text generation pipeline
- **[AI Metadata Generator](../../T/Publishing/SEO/Keywords/ai_metadata_generator.py)** - SEO AI integration

## Version History

### 1.0.0 (2025-12-05)
- Initial documentation
- Ollama installation instructions
- Qwen2.5-14B model setup
- Python integration examples
