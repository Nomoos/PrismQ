# Local AI Generation Guide

**Generating Ideas from IdeaInspiration using Local AI Models**

This guide covers how to use local AI models (LLMs) to generate Idea objects from IdeaInspiration sources or from interactive user input. The Idea module is designed to work seamlessly with local models like Ollama, LM Studio, or other OpenAI-compatible APIs.

---

## Table of Contents

1. [Overview](#overview)
2. [Setup Local AI Environment](#setup-local-ai-environment)
3. [Generation Methods](#generation-methods)
4. [From IdeaInspiration Sources](#from-ideainspiration-sources)
5. [Interactive Generation](#interactive-generation)
6. [Batch Generation](#batch-generation)
7. [Best Practices](#best-practices)
8. [Example Scripts](#example-scripts)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The Idea generation process leverages local AI models to:
- **Distill multiple IdeaInspirations** into cohesive Ideas
- **Generate Ideas interactively** from topics or descriptions
- **Create multiple Idea variations** for A/B testing
- **Enrich Ideas** with AI-generated fields (synopsis, themes, character notes, etc.)

### Why Local AI?

- ✅ **Privacy**: Your content stays on your machine
- ✅ **Cost**: No API fees or usage limits
- ✅ **Speed**: Fast generation with GPU acceleration
- ✅ **Customization**: Fine-tune models for your specific use case
- ✅ **Offline**: Works without internet connection

---

## Setup Local AI Environment

### Option 1: Ollama (Recommended)

**Install Ollama:**
```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download/windows
# Install and add to PATH
```

**Pull a recommended model:**
```bash
# Fast, good quality (8GB VRAM/RAM required)
ollama pull llama3.2:8b

# Better quality, needs more memory (16GB VRAM/RAM required)
ollama pull llama3.1:70b

# Best for creative writing (32GB VRAM/RAM required)
ollama pull mixtral:8x7b

# High-end models for RTX 4090/5090 (24GB VRAM)
ollama pull llama3.1:70b-q4_K_M  # Quantized for 24GB VRAM
ollama pull qwen2.5:72b-q4_K_M   # Excellent for long-form content
ollama pull command-r:35b        # Great instruction following
```

**Start Ollama server:**
```bash
ollama serve
# Server runs on http://localhost:11434
```

**GPU Acceleration:**
- Ollama automatically detects and uses NVIDIA GPUs (CUDA)
- AMD GPUs supported via ROCm on Linux
- Apple Silicon uses Metal acceleration
- CPU fallback available but much slower

### Option 2: LM Studio

1. Download from https://lmstudio.ai/
2. Install and open LM Studio
3. Download a model (e.g., "Meta-Llama-3.1-8B-Instruct")
4. Start local server (enable OpenAI compatible API)
5. Server runs on http://localhost:1234

### Option 3: Text-generation-webui

```bash
git clone https://github.com/oobabooga/text-generation-webui
cd text-generation-webui
./start_linux.sh  # or start_windows.bat, start_macos.sh
```

Enable API mode and use http://localhost:5000

---

## RTX 5090 Optimization Guide (Windows)

### Hardware Specifications

The NVIDIA RTX 5090 (expected specs based on leaks, verify with official release):
- **VRAM**: 24-32GB GDDR7
- **CUDA Cores**: ~21,000
- **Memory Bandwidth**: ~1TB/s
- **Optimal Use**: Large language models with high throughput

### Recommended Models for RTX 5090

#### Tier 1: Maximum Quality (24GB+ VRAM)

**Best Overall Choice:**
```bash
# Llama 3.1 70B (Quantized Q4_K_M)
ollama pull llama3.1:70b-q4_K_M
# VRAM: ~22GB | Speed: 15-25 tokens/sec | Quality: Excellent
```

**Best for Creative Writing:**
```bash
# Qwen 2.5 72B (Quantized Q4_K_M)
ollama pull qwen2.5:72b-q4_K_M
# VRAM: ~23GB | Speed: 12-20 tokens/sec | Quality: Superior for long-form
```

**Best for Instruction Following:**
```bash
# Command R 35B
ollama pull command-r:35b
# VRAM: ~18GB | Speed: 25-35 tokens/sec | Quality: Excellent for structured output
```

**Best for Code and Technical:**
```bash
# DeepSeek Coder 33B
ollama pull deepseek-coder:33b-q4_K_M
# VRAM: ~17GB | Speed: 25-30 tokens/sec | Quality: Top-tier for technical content
```

#### Tier 2: Balanced Performance (12-20GB VRAM)

```bash
# Llama 3.1 13B (Full precision)
ollama pull llama3.1:13b
# VRAM: ~13GB | Speed: 40-60 tokens/sec | Quality: Very good

# Mixtral 8x7B
ollama pull mixtral:8x7b-q4_K_M
# VRAM: ~16GB | Speed: 30-45 tokens/sec | Quality: Excellent for creative content

# Mistral Small (22B)
ollama pull mistral-small:22b-q4_K_M
# VRAM: ~14GB | Speed: 35-50 tokens/sec | Quality: Great general purpose
```

#### Tier 3: Fast Generation (6-12GB VRAM)

```bash
# Llama 3.2 8B (Fast iteration)
ollama pull llama3.2:8b
# VRAM: ~8GB | Speed: 60-100 tokens/sec | Quality: Good for drafts

# Phi-3 Medium 14B
ollama pull phi3:14b-q4_K_M
# VRAM: ~9GB | Speed: 50-80 tokens/sec | Quality: Excellent efficiency
```

### Windows-Specific Setup

#### 1. Install CUDA Toolkit (if not already installed)

```powershell
# Download CUDA Toolkit from NVIDIA
# https://developer.nvidia.com/cuda-downloads
# Version 12.x recommended

# Verify installation
nvcc --version
nvidia-smi
```

#### 2. Configure Ollama for RTX 5090

```powershell
# Set environment variables for optimal performance
$env:OLLAMA_NUM_GPU=1
$env:OLLAMA_GPU_OVERHEAD=2048  # 2GB overhead for Windows
$env:OLLAMA_MAX_LOADED_MODELS=2  # Load multiple models if VRAM allows

# Start Ollama
ollama serve
```

#### 3. Monitor GPU Usage

```powershell
# Real-time monitoring
nvidia-smi -l 1  # Update every second

# Check specific metrics
nvidia-smi --query-gpu=utilization.gpu,utilization.memory,memory.used,memory.free --format=csv -l 1
```

### Performance Optimization Tips

#### 1. Context Window Optimization

```python
# For long-form content generation
context_length = 8192  # RTX 5090 can handle larger contexts

# Adjust based on model
# - 70B models: 4096-8192 tokens
# - 33B models: 8192-16384 tokens  
# - 13B models: 16384-32768 tokens
```

#### 2. Batch Processing

```python
# Generate multiple Ideas in parallel (RTX 5090 can handle it)
import concurrent.futures

def generate_idea_batch(prompts: list[str], max_workers: int = 3):
    """
    RTX 5090 can run multiple smaller models or process multiple
    requests to the same large model efficiently.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(generate_idea, prompt) for prompt in prompts]
        return [f.result() for f in concurrent.futures.as_completed(futures)]
```

#### 3. Temperature and Sampling Settings

```python
# For RTX 5090, you can afford higher quality settings
generation_params = {
    "temperature": 0.8,        # Creativity level
    "top_p": 0.92,            # Nucleus sampling
    "top_k": 40,              # Diversity
    "repeat_penalty": 1.1,    # Avoid repetition
    "num_ctx": 8192,          # Context window (RTX 5090 handles well)
    "num_predict": 2048,      # Max tokens to generate
}
```

### Model Selection Matrix

| Use Case | Model | VRAM | Speed | Quality | Notes |
|----------|-------|------|-------|---------|-------|
| **Reddit Stories** | llama3.1:70b-q4_K_M | 22GB | Fast | ★★★★★ | Best authenticity |
| **Creative Fiction** | qwen2.5:72b-q4_K_M | 23GB | Medium | ★★★★★ | Superior narratives |
| **Educational Content** | command-r:35b | 18GB | Fast | ★★★★☆ | Structured output |
| **Technical/Code** | deepseek-coder:33b | 17GB | Fast | ★★★★★ | Best for tutorials |
| **Fast Iteration** | llama3.2:8b | 8GB | Very Fast | ★★★☆☆ | Draft generation |
| **Multi-language** | qwen2.5:32b-q4_K_M | 16GB | Fast | ★★★★☆ | Best for non-English |

### Troubleshooting RTX 5090

#### Issue: "Out of memory" error

**Solutions:**
```powershell
# 1. Use quantized models
ollama pull llama3.1:70b-q4_K_M  # Instead of full precision

# 2. Reduce context window
$env:OLLAMA_NUM_CTX=4096

# 3. Increase GPU overhead
$env:OLLAMA_GPU_OVERHEAD=3072  # Allocate 3GB for Windows + apps

# 4. Close other GPU applications
# Check: Task Manager → Performance → GPU
```

#### Issue: Slow generation speed

**Solutions:**
```powershell
# 1. Verify GPU is being used
ollama run llama3.1:70b-q4_K_M "test" --verbose

# 2. Update NVIDIA drivers
# Download latest Game Ready or Studio drivers

# 3. Disable Windows Game Mode (can interfere)
# Settings → Gaming → Game Mode → Off

# 4. Set high performance power plan
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
```

#### Issue: Model not using full VRAM

**Solutions:**
```powershell
# Force Ollama to use more VRAM
$env:OLLAMA_MAX_VRAM=28  # GB, adjust based on your 5090 VRAM

# Check current usage
nvidia-smi
```

### Performance Benchmarks (Estimated)

Based on RTX 4090 performance + 5090 improvements:

| Model | Tokens/Second | Time for 500-word Idea |
|-------|---------------|------------------------|
| llama3.1:70b-q4_K_M | 20-25 | ~30-40 seconds |
| qwen2.5:72b-q4_K_M | 15-22 | ~40-50 seconds |
| command-r:35b | 30-40 | ~20-25 seconds |
| mixtral:8x7b | 40-55 | ~15-20 seconds |
| llama3.2:8b | 80-120 | ~8-12 seconds |

*Note: Actual performance depends on Windows version, drivers, and system configuration.*

### Sources and Verification

**Hardware Information:**
- NVIDIA RTX 5090 specifications: [NVIDIA Official](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/)
- GPU architecture details: Blackwell Architecture White Paper

**Software Compatibility:**
- Ollama Windows support: [Official Documentation](https://github.com/ollama/ollama/blob/main/docs/windows.md)
- CUDA compatibility: [CUDA Toolkit Documentation](https://docs.nvidia.com/cuda/)

**Model Performance:**
- Ollama model library: [https://ollama.com/library](https://ollama.com/library)
- Community benchmarks: [Ollama Discord](https://discord.gg/ollama)
- Model cards on Hugging Face for detailed specifications

**Optimization Guidelines:**
- NVIDIA GPU optimization guide: [NVIDIA Developer Zone](https://developer.nvidia.com/blog/)
- Ollama performance tuning: [GitHub Issues and Discussions](https://github.com/ollama/ollama/discussions)

---

## Generation Methods

### Method 1: From IdeaInspiration Sources

Generate Ideas by fusing multiple IdeaInspiration objects.

### Method 2: Interactive Generation

Generate Ideas from scratch via conversation with the AI.

### Method 3: Batch Generation

Generate multiple Idea variations for testing and refinement.

---

## From IdeaInspiration Sources

### Single Inspiration → Single Idea

**Use Case:** Transform one trending topic into an Idea.

```python
import requests
import json
from idea_inspiration import IdeaInspiration
from idea import Idea, IdeaStatus, ContentGenre

# Load IdeaInspiration from database
inspiration = IdeaInspiration(
    title="Digital Privacy Crisis in 2024",
    description="Data breaches affecting millions",
    content="Recent data breach exposed personal info of 50M users...",
    keywords=["privacy", "cybersecurity", "data breach"],
    source_platform="reddit",
    category="technology",
    score=85
)

# Prepare prompt for AI
prompt = f"""You are a creative content strategist. Transform this inspiration into a detailed Idea for multi-format content (text, audio, video).

Input IdeaInspiration:
- Title: {inspiration.title}
- Description: {inspiration.description}
- Keywords: {', '.join(inspiration.keywords)}
- Category: {inspiration.category}

Generate a complete Idea with these fields:
1. title: Catchy, engaging title for the content
2. concept: Core concept (2-3 sentences)
3. synopsis: 2-3 paragraph summary for quick understanding
4. story_premise: Narrative foundation for storytelling
5. keywords: 5-10 relevant keywords (include original + new)
6. themes: 3-5 core themes to explore
7. outline: Structured content outline (numbered sections)
8. skeleton: High-level framework (e.g., "Hook → Explain → Teach → Apply → Conclude")
9. target_demographics: Who is this for? (e.g., "Tech-savvy millennials, privacy advocates, ages 25-40")
10. genre: One of: true_crime, mystery, horror, documentary, educational, entertainment, lifestyle, technology
11. character_notes: If applicable, describe key people/personas
12. setting_notes: Context, environment, world-building
13. tone_guidance: Detailed tone/mood guidance
14. length_target: Target length (e.g., "15-20 min video / 2500-3000 words")

Output valid JSON only, no additional text."""

# Call local AI model
response = requests.post('http://localhost:11434/api/generate', 
    json={
        "model": "llama3.2:8b",
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
)

ai_output = json.loads(response.json()['response'])

# Create Idea from AI output
idea = Idea(
    idea_id=f"idea-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
    title=ai_output['title'],
    concept=ai_output['concept'],
    synopsis=ai_output.get('synopsis', ''),
    story_premise=ai_output.get('story_premise', ''),
    keywords=ai_output['keywords'],
    themes=ai_output.get('themes', []),
    outline=ai_output.get('outline', ''),
    skeleton=ai_output.get('skeleton', ''),
    target_demographics=ai_output.get('target_demographics', ''),
    genre=ContentGenre[ai_output['genre'].upper()],
    character_notes=ai_output.get('character_notes', ''),
    setting_notes=ai_output.get('setting_notes', ''),
    tone_guidance=ai_output.get('tone_guidance', ''),
    length_target=ai_output.get('length_target', ''),
    target_platforms=["youtube", "medium", "spotify"],
    target_formats=["text", "audio", "video"],
    inspiration_ids=[inspiration.source_id] if inspiration.source_id else [],
    status=IdeaStatus.DRAFT,
    version=1,
    created_by="ai-generator",
    created_at=datetime.now().isoformat()
)

print(f"Generated Idea: {idea.title}")
```

### Multiple Inspirations → Single Idea (Fusion)

**Use Case:** Combine 3-5 trending topics into one original Idea.

```python
from typing import List
from idea_inspiration import IdeaInspiration
from idea import Idea

def fuse_inspirations_with_ai(inspirations: List[IdeaInspiration], 
                               model_url: str = "http://localhost:11434") -> Idea:
    """Fuse multiple IdeaInspirations into a single Idea using AI."""
    
    # Aggregate data from inspirations
    all_keywords = []
    all_themes = []
    inspiration_summaries = []
    
    for insp in inspirations:
        all_keywords.extend(insp.keywords)
        inspiration_summaries.append(
            f"- {insp.title}: {insp.description}"
        )
    
    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = [x for x in all_keywords if not (x in seen or seen.add(x))]
    
    # Create fusion prompt
    prompt = f"""You are a creative content strategist specializing in fusing multiple concepts into original ideas.

Input Sources ({len(inspirations)} inspirations):
{chr(10).join(inspiration_summaries)}

Common Keywords: {', '.join(unique_keywords[:15])}

Your Task: Fuse these inspirations into ONE original, cohesive Idea that:
1. Combines the most interesting aspects of all sources
2. Creates something NEW and UNIQUE (not just a summary)
3. Has universal appeal across text, audio, and video formats
4. Targets multiple platforms (YouTube, Spotify, Medium, TikTok)

Generate complete Idea with all required fields as JSON:
{{
  "title": "Catchy title for the fused concept",
  "concept": "Core concept in 2-3 sentences",
  "synopsis": "2-3 paragraph summary",
  "story_premise": "Narrative foundation for storytelling",
  "keywords": ["keyword1", "keyword2", ...],
  "themes": ["theme1", "theme2", "theme3"],
  "outline": "1. Section\\n2. Section\\n3. Section",
  "skeleton": "Framework (e.g., Hook → Build → Reveal → Conclude)",
  "target_demographics": "Target audience description",
  "genre": "educational/documentary/entertainment/etc",
  "character_notes": "Key personas or characters if applicable",
  "setting_notes": "Context and environment",
  "tone_guidance": "Detailed tone/mood guidance",
  "length_target": "15-20 min videos / 2500-3500 words"
}}

Output valid JSON only."""

    # Call AI
    response = requests.post(f'{model_url}/api/generate',
        json={
            "model": "llama3.2:8b",
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.7,  # Creative but coherent
                "top_p": 0.9
            }
        }
    )
    
    ai_output = json.loads(response.json()['response'])
    
    # Create Idea with factory method
    idea = Idea.from_inspirations(
        inspirations=inspirations,
        title=ai_output['title'],
        concept=ai_output['concept'],
        synopsis=ai_output.get('synopsis', ''),
        story_premise=ai_output.get('story_premise', ''),
        keywords=ai_output.get('keywords', unique_keywords),
        themes=ai_output.get('themes', []),
        outline=ai_output.get('outline', ''),
        skeleton=ai_output.get('skeleton', ''),
        target_demographics=ai_output.get('target_demographics', ''),
        genre=ContentGenre[ai_output['genre'].upper()],
        character_notes=ai_output.get('character_notes', ''),
        setting_notes=ai_output.get('setting_notes', ''),
        tone_guidance=ai_output.get('tone_guidance', ''),
        length_target=ai_output.get('length_target', ''),
        target_platforms=["youtube", "spotify", "medium", "tiktok"],
        target_formats=["text", "audio", "video"],
        created_by="ai-fusion-generator"
    )
    
    return idea

# Example usage
inspirations = [insp1, insp2, insp3, insp4, insp5]
fused_idea = fuse_inspirations_with_ai(inspirations)
print(f"Fused Idea: {fused_idea.title}")
print(f"From {len(fused_idea.inspiration_ids)} sources")
```

---

## Interactive Generation

### From Topic/Description

**Use Case:** User provides a topic, AI generates complete Idea interactively.

```python
def generate_idea_interactive(topic: str, 
                               additional_context: str = "",
                               num_ideas: int = 1,
                               model_url: str = "http://localhost:11434") -> List[Idea]:
    """Generate Ideas interactively from a topic or description."""
    
    prompt = f"""You are a creative content strategist. Generate {num_ideas} unique Idea(s) for the following topic.

Topic: {topic}

Additional Context: {additional_context if additional_context else "None provided"}

For each Idea, generate complete details as JSON with these fields:
- title: Engaging title
- concept: Core concept (2-3 sentences)
- synopsis: 2-3 paragraph summary
- story_premise: Narrative foundation
- keywords: 8-12 relevant keywords
- themes: 3-5 core themes
- outline: Numbered content structure (5-7 sections)
- skeleton: High-level framework
- target_demographics: Target audience
- genre: One of [true_crime, mystery, horror, documentary, educational, entertainment, lifestyle, technology]
- character_notes: Key personas/characters
- setting_notes: Context and environment
- tone_guidance: Tone/mood across content
- length_target: Format specifications

Output as JSON array if multiple ideas, single JSON object if one idea.
Valid JSON only, no additional text."""

    response = requests.post(f'{model_url}/api/generate',
        json={
            "model": "llama3.2:8b",
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.8,  # More creative
                "top_p": 0.9,
                "top_k": 50
            }
        }
    )
    
    ai_output = json.loads(response.json()['response'])
    
    # Handle single or multiple ideas
    if isinstance(ai_output, list):
        ideas_data = ai_output
    else:
        ideas_data = [ai_output]
    
    ideas = []
    for idx, data in enumerate(ideas_data[:num_ideas]):
        idea = Idea(
            idea_id=f"idea-interactive-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{idx}",
            title=data['title'],
            concept=data['concept'],
            synopsis=data.get('synopsis', ''),
            story_premise=data.get('story_premise', ''),
            keywords=data.get('keywords', []),
            themes=data.get('themes', []),
            outline=data.get('outline', ''),
            skeleton=data.get('skeleton', ''),
            target_demographics=data.get('target_demographics', ''),
            genre=ContentGenre[data['genre'].upper()],
            character_notes=data.get('character_notes', ''),
            setting_notes=data.get('setting_notes', ''),
            tone_guidance=data.get('tone_guidance', ''),
            length_target=data.get('length_target', ''),
            target_platforms=["youtube", "spotify", "medium", "tiktok"],
            target_formats=["text", "audio", "video"],
            inspiration_ids=[],  # No source inspirations
            status=IdeaStatus.DRAFT,
            version=1,
            created_by="ai-interactive-generator",
            created_at=datetime.now().isoformat(),
            purpose="Generated interactively from topic"
        )
        ideas.append(idea)
    
    return ideas

# Example: Generate 3 Ideas for a topic
topic = "The psychology of viral content and social media addiction"
context = "Target audience: content creators, marketers, general audience interested in psychology"

ideas = generate_idea_interactive(
    topic=topic,
    additional_context=context,
    num_ideas=3
)

for i, idea in enumerate(ideas, 1):
    print(f"\n{i}. {idea.title}")
    print(f"   Genre: {idea.genre.value}")
    print(f"   Themes: {', '.join(idea.themes)}")
```

### Conversational Refinement

**Use Case:** Iteratively refine an Idea through conversation.

```python
def refine_idea_conversationally(idea: Idea, 
                                  user_feedback: str,
                                  model_url: str = "http://localhost:11434") -> Idea:
    """Refine an existing Idea based on user feedback."""
    
    prompt = f"""You are a creative content strategist. Refine this Idea based on user feedback.

Current Idea:
- Title: {idea.title}
- Concept: {idea.concept}
- Synopsis: {idea.synopsis}
- Themes: {', '.join(idea.themes)}
- Outline: {idea.outline}
- Skeleton: {idea.skeleton}

User Feedback: {user_feedback}

Generate a REFINED version addressing the feedback. Output complete Idea as JSON with all fields.
Keep what works, improve what doesn't. Output valid JSON only."""

    response = requests.post(f'{model_url}/api/generate',
        json={
            "model": "llama3.2:8b",
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
    )
    
    ai_output = json.loads(response.json()['response'])
    
    # Create new version
    refined_idea = idea.create_new_version(
        title=ai_output.get('title', idea.title),
        concept=ai_output.get('concept', idea.concept),
        synopsis=ai_output.get('synopsis', idea.synopsis),
        story_premise=ai_output.get('story_premise', idea.story_premise),
        keywords=ai_output.get('keywords', idea.keywords),
        themes=ai_output.get('themes', idea.themes),
        outline=ai_output.get('outline', idea.outline),
        skeleton=ai_output.get('skeleton', idea.skeleton),
        character_notes=ai_output.get('character_notes', idea.character_notes),
        setting_notes=ai_output.get('setting_notes', idea.setting_notes),
        tone_guidance=ai_output.get('tone_guidance', idea.tone_guidance),
        status=IdeaStatus.VALIDATED
    )
    
    return refined_idea

# Example
feedback = "Make it more focused on practical tips, less theoretical. Add real-world examples."
refined = refine_idea_conversationally(original_idea, feedback)
print(f"Refined Idea v{refined.version}: {refined.title}")
```

---

## Batch Generation

### Generate Multiple Variations

**Use Case:** Create 5-10 Idea variations for A/B testing.

```python
def batch_generate_variations(base_topic: str,
                               num_variations: int = 5,
                               diversity_level: float = 0.8,
                               model_url: str = "http://localhost:11434") -> List[Idea]:
    """Generate multiple Idea variations for testing."""
    
    ideas = []
    
    for i in range(num_variations):
        prompt = f"""Generate Idea #{i+1} of {num_variations} for this topic. 
Each Idea should be UNIQUE and DIVERSE.

Topic: {base_topic}

Variation Strategy for Idea #{i+1}:
- Try a different genre/angle
- Target different demographics
- Use different tone/style
- Explore unique themes

Generate complete Idea as JSON with all fields. Make it distinctly different from previous iterations.
Output valid JSON only."""

        response = requests.post(f'{model_url}/api/generate',
            json={
                "model": "llama3.2:8b",
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": diversity_level,  # Higher = more diverse
                    "top_p": 0.95,
                    "top_k": 60
                }
            }
        )
        
        ai_output = json.loads(response.json()['response'])
        
        idea = Idea(
            idea_id=f"idea-batch-{datetime.now().strftime('%Y%m%d')}-v{i+1}",
            title=ai_output['title'],
            concept=ai_output['concept'],
            synopsis=ai_output.get('synopsis', ''),
            story_premise=ai_output.get('story_premise', ''),
            keywords=ai_output.get('keywords', []),
            themes=ai_output.get('themes', []),
            outline=ai_output.get('outline', ''),
            skeleton=ai_output.get('skeleton', ''),
            target_demographics=ai_output.get('target_demographics', ''),
            genre=ContentGenre[ai_output['genre'].upper()],
            character_notes=ai_output.get('character_notes', ''),
            setting_notes=ai_output.get('setting_notes', ''),
            tone_guidance=ai_output.get('tone_guidance', ''),
            length_target=ai_output.get('length_target', ''),
            target_platforms=["youtube", "spotify", "medium"],
            target_formats=["text", "audio", "video"],
            inspiration_ids=[],
            status=IdeaStatus.DRAFT,
            version=1,
            created_by=f"ai-batch-generator-v{i+1}",
            created_at=datetime.now().isoformat()
        )
        
        ideas.append(idea)
        print(f"Generated variation {i+1}/{num_variations}: {idea.title}")
    
    return ideas

# Example
variations = batch_generate_variations(
    base_topic="Future of remote work and digital nomad lifestyle",
    num_variations=5,
    diversity_level=0.85  # High diversity
)

print(f"\nGenerated {len(variations)} unique variations:")
for v in variations:
    print(f"  - {v.title} ({v.genre.value})")
```

---

## Best Practices

### 1. Prompt Engineering

**Good Prompts:**
- Specific field requirements
- Clear output format (JSON)
- Context about target audience
- Examples of desired output

**Bad Prompts:**
- Vague instructions
- No format specification
- Missing field requirements

### 2. Model Selection

| Model | RAM | Speed | Quality | Best For |
|-------|-----|-------|---------|----------|
| llama3.2:3b | 4GB | Fast | Good | Quick drafts, batch generation |
| llama3.2:8b | 8GB | Medium | Very Good | General purpose, recommended |
| llama3.1:70b | 16GB+ | Slow | Excellent | Final Ideas, complex fusion |
| mixtral:8x7b | 32GB | Medium | Excellent | Creative writing, long-form |

### 3. Temperature Settings

- **0.3-0.5**: Focused, consistent (refinement)
- **0.6-0.7**: Balanced (general generation)
- **0.8-0.9**: Creative, diverse (brainstorming)

### 4. Error Handling

```python
def safe_ai_generation(prompt: str, max_retries: int = 3) -> dict:
    """Generate with retry logic."""
    for attempt in range(max_retries):
        try:
            response = requests.post('http://localhost:11434/api/generate',
                json={"model": "llama3.2:8b", "prompt": prompt, "format": "json"},
                timeout=60
            )
            return json.loads(response.json()['response'])
        except (json.JSONDecodeError, KeyError, requests.Timeout) as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt == max_retries - 1:
                raise
    return {}
```

### 5. Quality Validation

```python
def validate_idea_completeness(idea: Idea) -> bool:
    """Check if AI-generated Idea is complete."""
    required_fields = [
        'title', 'concept', 'synopsis', 'keywords', 
        'themes', 'outline', 'skeleton'
    ]
    
    for field in required_fields:
        value = getattr(idea, field)
        if not value or (isinstance(value, (list, str)) and len(value) == 0):
            print(f"Warning: Missing or empty field: {field}")
            return False
    
    return True
```

---

## Example Scripts

### Complete Generation Pipeline

```python
#!/usr/bin/env python3
"""Complete Idea generation pipeline using local AI."""

import requests
import json
from datetime import datetime
from typing import List
from idea import Idea, IdeaStatus, ContentGenre
from idea_db import IdeaDatabase
from idea_inspiration import IdeaInspiration

def generate_ideas_pipeline(inspirations: List[IdeaInspiration],
                            interactive_topic: str = None,
                            num_ideas: int = 1) -> List[Idea]:
    """Complete pipeline for Idea generation."""
    
    ideas = []
    
    # Method 1: From IdeaInspiration sources
    if inspirations:
        print(f"Fusing {len(inspirations)} IdeaInspirations...")
        fused_idea = fuse_inspirations_with_ai(inspirations)
        ideas.append(fused_idea)
    
    # Method 2: Interactive generation
    if interactive_topic:
        print(f"Generating {num_ideas} Idea(s) from topic...")
        interactive_ideas = generate_idea_interactive(
            topic=interactive_topic,
            num_ideas=num_ideas
        )
        ideas.extend(interactive_ideas)
    
    # Save to database
    db = IdeaDatabase("idea.db")
    db.connect()
    db.create_tables()
    
    for idea in ideas:
        idea_id = db.insert_idea(idea.to_dict())
        print(f"Saved Idea: {idea_id} - {idea.title}")
    
    db.close()
    
    return ideas

# Example usage
if __name__ == "__main__":
    # Load inspirations from database (example)
    inspirations = [...]  # Load from IdeaInspiration database
    
    # Generate Ideas
    generated_ideas = generate_ideas_pipeline(
        inspirations=inspirations[:5],  # Fuse first 5
        interactive_topic="The future of AI in content creation",
        num_ideas=3  # Generate 3 variations
    )
    
    print(f"\n✅ Generated {len(generated_ideas)} Ideas total")
```

---

## Troubleshooting

### Model Not Responding

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
pkill ollama && ollama serve
```

### Out of Memory

- Use smaller model (llama3.2:3b)
- Reduce batch size
- Enable offloading to CPU:
  ```bash
  OLLAMA_NUM_GPU=0 ollama serve
  ```

### JSON Parsing Errors

- Add `"format": "json"` to request
- Validate AI output before parsing:
  ```python
  try:
      data = json.loads(ai_response)
  except json.JSONDecodeError:
      # Retry with stricter prompt
      pass
  ```

### Slow Generation

- Use faster model (llama3.2:3b)
- Enable GPU acceleration
- Reduce `num_ctx` (context length):
  ```json
  {"options": {"num_ctx": 2048}}
  ```

---

## See Also

- [AI_GENERATION.md](AI_GENERATION.md) - AI story generation best practices
- [FIELDS.md](FIELDS.md) - Complete field reference
- [QUICK_START.md](QUICK_START.md) - Basic setup and usage
- [MULTI_FORMAT.md](MULTI_FORMAT.md) - Universal content generation

---

## Summary

**Quick Start Checklist:**
1. ✅ Install Ollama or LM Studio
2. ✅ Pull recommended model (llama3.2:8b)
3. ✅ Choose generation method (fusion/interactive/batch)
4. ✅ Run generation script
5. ✅ Validate and save Ideas to database

**Key Takeaways:**
- Local AI provides privacy, speed, and cost savings
- Three methods: fusion from inspirations, interactive, batch variations
- Use appropriate temperature settings for desired creativity level
- Always validate AI output before saving to database
- Iterate and refine Ideas based on feedback

Start with interactive generation to get familiar, then move to fusion and batch generation for production workflows.

---

## Related Documentation

- **[Reddit Story Generation](./REDDIT_STORIES.md)** - Specialized guide for creating Reddit stories
- **[AI Generation Guide](./AI_GENERATION.md)** - Best practices for AI content generation
- **[Field Reference](./FIELDS.md)** - Complete field documentation
- **[Multi-Format Content](./MULTI_FORMAT.md)** - Adapting Ideas for text/audio/video
- **[Quick Start](./QUICK_START.md)** - Get started with basic usage

---

## Sources and References

**Ollama Documentation:**
- Official Ollama documentation: [https://github.com/ollama/ollama](https://github.com/ollama/ollama)
- Model library and specifications: [https://ollama.com/library](https://ollama.com/library)
- Windows setup guide: [https://github.com/ollama/ollama/blob/main/docs/windows.md](https://github.com/ollama/ollama/blob/main/docs/windows.md)

**LM Studio:**
- Official website: [https://lmstudio.ai/](https://lmstudio.ai/)
- Documentation: Available within application

**NVIDIA GPU Optimization:**
- CUDA Toolkit: [https://developer.nvidia.com/cuda-toolkit](https://developer.nvidia.com/cuda-toolkit)
- RTX series specifications: [https://www.nvidia.com/en-us/geforce/graphics-cards/](https://www.nvidia.com/en-us/geforce/graphics-cards/)
- GPU optimization guides: [NVIDIA Developer Zone](https://developer.nvidia.com/)

**Model Information:**
- Llama 3.x documentation: Meta AI Research
- Qwen 2.5 information: Alibaba Cloud
- Mixtral documentation: Mistral AI
- Model cards on Hugging Face: [https://huggingface.co/models](https://huggingface.co/models)

**Performance Benchmarking:**
- Community benchmarks: [Ollama Discord Server](https://discord.gg/ollama)
- LLM performance comparisons: [Artificial Analysis](https://artificialanalysis.ai/)

---

## License

Proprietary - All Rights Reserved © 2025 PrismQ
