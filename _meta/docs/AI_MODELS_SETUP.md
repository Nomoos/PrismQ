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

### Alternative Qwen2.5 Models

Depending on your hardware capabilities, you can use different Qwen2.5 variants:

| Model | Size | VRAM Required | Use Case |
|-------|------|---------------|----------|
| `qwen2.5:7b` | ~4.5GB | 8GB | Lighter weight, faster inference |
| `qwen2.5:14b` | ~9GB | 16GB | **Recommended** - Best balance of quality and speed |
| `qwen2.5:32b` | ~20GB | 24GB+ | Highest quality, requires high-end GPU |

### Other Supported Models

PrismQ also supports other Ollama models. For SEO-specific tasks, the Keywords module uses:

| Model | Size | VRAM Required | Use Case |
|-------|------|---------------|----------|
| `llama3.1:70b-q4_K_M` | ~40GB | 48GB+ | SEO metadata generation (Keywords module default) |

To pull this model:
```bash
ollama pull llama3.1:70b-q4_K_M
```

## Model Comparison for High-End Systems (RTX 5090)

For users with an NVIDIA RTX 5090 (32GB VRAM), you have access to the most powerful local AI models. Here's a comprehensive comparison for story writing and content generation:

### Recommended Models for RTX 5090

| Model | Parameters | VRAM Usage | Story Quality | Speed | Best For |
|-------|------------|------------|---------------|-------|----------|
| **Qwen2.5:32b** | 32B | ~20GB | ⭐⭐⭐⭐⭐ | Medium | **Best overall for creative writing** |
| **Qwen2.5:14b** | 14B | ~9GB | ⭐⭐⭐⭐ | Fast | Balanced quality and speed |
| **Llama3.1:70b-q4** | 70B | ~40GB | ⭐⭐⭐⭐⭐ | Slow | Highest quality, requires quantization |
| **Llama3.3:70b** | 70B | ~40GB | ⭐⭐⭐⭐⭐ | Slow | Latest Llama, improved reasoning |
| **Mistral-Large** | 123B | ~32GB | ⭐⭐⭐⭐⭐ | Slow | Complex narratives |
| **DeepSeek-V2** | 236B | ~32GB | ⭐⭐⭐⭐ | Medium | Long-form content |

### Llama 3.1 405B vs Llama 3.3 70B

| Aspect | Llama 3.1 — 405B | Llama 3.3 — 70B |
|--------|------------------|-----------------|
| **Parameters** | 405B | 70B |
| **VRAM Required** | ~200GB+ (requires multi-GPU or cloud) | ~40GB (Q4 quantized) |
| **Context Length** | 128K tokens | 128K tokens |
| **Quality** | ⭐⭐⭐⭐⭐ (best-in-class) | ⭐⭐⭐⭐⭐ (excellent) |
| **Speed** | Very Slow | Medium |
| **Local RTX 5090** | ❌ Too large | ✅ With quantization |
| **Ollama Support** | ❌ Cloud/API only | ✅ `ollama pull llama3.3:70b` |

### Understanding Quantization

**Co je kvantizace?** Kvantizace je technika komprese modelu, která snižuje přesnost vah (např. z 16-bit na 4-bit). To výrazně zmenší velikost modelu a VRAM požadavky.

#### Kompletní přehled kvantizačních variant

| Kvantizace | Kvalita vs Originál | VRAM (70B model) | Rychlost | Doporučení |
|------------|---------------------|------------------|----------|------------|
| **FP16** (bez kvantizace) | 100% | ~140GB | Nejpomalejší | ❌ Příliš velké pro RTX 5090 |
| **Q8_0** (8-bit) | ~99.5% | ~70GB | Pomalá | ❌ Příliš velké pro RTX 5090 |
| **Q6_K** (6-bit) | ~98.5% | ~54GB | Střední | ⚠️ Na hranici, může fungovat s offloadingem |
| **Q5_K_M** (5-bit) | ~97% | ~47GB | Rychlá | ✅ Dobrá volba pro kvalitu |
| **Q5_K_S** (5-bit small) | ~96% | ~45GB | Rychlá | ✅ Dobrá alternativa |
| **Q4_K_M** (4-bit medium) | ~95% | ~40GB | Velmi rychlá | ✅ **DOPORUČENO pro RTX 5090** |
| **Q4_K_S** (4-bit small) | ~94% | ~38GB | Velmi rychlá | ✅ Nejrychlejší kvalitní varianta |
| **Q3_K_M** (3-bit) | ~90% | ~33GB | Extrémně rychlá | ⚠️ Znatelná ztráta kvality |
| **IQ4_XS** (4-bit i-quant) | ~94.5% | ~36GB | Velmi rychlá | ✅ Moderní alternativa k Q4 |

#### 🏆 Finální doporučení pro RTX 5090 (32GB VRAM)

**Pro maximální kvalitu:** `Q4_K_M` nebo `Q5_K_S`
- Q4_K_M nabízí nejlepší poměr kvalita/VRAM pro 32GB karty
- Rozdíl mezi Q4_K_M a Q6_K je v praxi téměř nepostřehnutelný pro kreativní psaní
- Q6_K je příliš velký pro RTX 5090 bez CPU offloadingu

```bash
# 🏆 NEJLEPŠÍ VOLBA pro RTX 5090 32GB - Llama 3.3 70B Q4_K_M
ollama pull llama3.3:70b-q4_K_M

# Alternativa pro o něco vyšší kvalitu (pomalejší)
ollama pull llama3.3:70b-q5_K_S

# Pro Qwen2.5 32B (vejde se celý bez kvantizace)
ollama pull qwen2.5:32b
```

> **Poznámka ke Q6_K:** I když Q6_K nabízí ~98.5% kvality, vyžaduje ~54GB VRAM pro 70B model. Na RTX 5090 (32GB) by musel použít CPU offloading, což dramaticky zpomalí inference. Pro vaši sestavu doporučuji Q4_K_M - ztráta kvality je minimální (~5%) a rychlost bude výrazně lepší.

### Model Recommendations by PrismQ Task

| Task | Best Model | Alternative | Why |
|------|------------|-------------|-----|
| **Idea Generation** | Llama 3.3:70b | Qwen2.5:32b | Strong creative reasoning, diverse ideas |
| **Title Creation** | Qwen2.5:14b | Llama 3.3:70b | Fast, concise outputs, good for iteration |
| **Script Writing** | Qwen2.5:32b | Llama 3.1:70b-q4 | Best narrative quality, instruction following |
| **Review/Editing** | Llama 3.3:70b | Llama 3.1:70b-q4 | Superior analytical and reasoning capabilities |
| **SEO Metadata** | Llama 3.1:70b-q4 | Qwen2.5:14b | Consistent, structured outputs |

#### Task-Specific Configuration:

```python
from T.Publishing.SEO.Keywords import AIConfig

# Idea Generation - creative, diverse
idea_config = AIConfig(
    model="llama3.3:70b",
    temperature=0.8,  # Higher for creativity
    enable_ai=True
)

# Title Creation - fast iteration
title_config = AIConfig(
    model="qwen2.5:14b",
    temperature=0.5,
    enable_ai=True
)

# Script Writing - high quality narrative
script_config = AIConfig(
    model="qwen2.5:32b",
    temperature=0.7,
    max_tokens=4000,
    enable_ai=True
)

# Review/Editing - analytical
review_config = AIConfig(
    model="llama3.3:70b",
    temperature=0.3,  # Lower for consistent analysis
    enable_ai=True
)
```

#### When to Use Llama 3.1 405B:
- Cloud/API access (Together AI, Fireworks, Groq)
- Maximum quality requirements
- Complex reasoning tasks
- Enterprise production workflows

#### When to Use Llama 3.3 70B:
- **Recommended for local RTX 5090** ✅
- Best balance of quality and local inference
- Reviews and analytical tasks
- Idea generation with strong reasoning

```bash
# Install Llama 3.3 70B for local use
ollama pull llama3.3:70b-q4_K_M
```

### MPT-7B-StoryWriter (HuggingFace)

The [MPT-7B-StoryWriter](https://huggingface.co/mosaicml/mpt-7b-storywriter) is a specialized model fine-tuned specifically for story writing with an impressive 65K context length.

| Aspect | MPT-7B-StoryWriter | Qwen2.5:32b |
|--------|-------------------|-------------|
| **Parameters** | 7B | 32B |
| **VRAM Required** | ~8GB | ~20GB |
| **Context Length** | 65,536 tokens | 32,768 tokens |
| **Story Quality** | ⭐⭐⭐⭐ (specialized) | ⭐⭐⭐⭐⭐ (general) |
| **Inference Speed** | Very Fast | Medium |
| **Ollama Support** | ❌ (requires manual setup) | ✅ Native |
| **Best Use Case** | Long-form novels, extended narratives | All creative content |

#### When to Choose MPT-7B-StoryWriter:
- Writing very long stories (novels, extended series)
- Need 65K context for maintaining consistency
- Prefer faster inference over raw quality
- Working with HuggingFace Transformers directly

#### When to Choose Qwen2.5:32b:
- General creative writing (stories, scripts, dialogue)
- Need better instruction following
- Prefer easy Ollama integration
- Want highest quality output

### RTX 5090 Optimal Configuration

For RTX 5090 with 32GB VRAM, we recommend:

```bash
# Best quality for story writing
ollama pull qwen2.5:32b

# Alternative for SEO and metadata
ollama pull llama3.1:70b-q4_K_M
```

**PrismQ Configuration for RTX 5090:**

```python
from T.Publishing.SEO.Keywords import AIConfig

# High-quality story generation config
story_config = AIConfig(
    model="qwen2.5:32b",
    api_base="http://localhost:11434",
    temperature=0.7,  # Higher for creative writing
    max_tokens=2000,
    enable_ai=True
)

# SEO metadata config
seo_config = AIConfig(
    model="llama3.1:70b-q4_K_M",
    api_base="http://localhost:11434",
    temperature=0.3,  # Lower for consistent SEO output
    enable_ai=True
)
```

### Optimalizace načítání modelu (Model Loading Optimization)

Pro zamezení opakovaného načítání modelu do VRAM během běhu PrismQ:

#### Ollama Keep-Alive nastavení

Ollama standardně udržuje model v paměti 5 minut po posledním dotazu. Pro delší workflow:

```bash
# Nastavte OLLAMA_KEEP_ALIVE na delší dobu (např. 60 minut)
export OLLAMA_KEEP_ALIVE=60m

# Nebo permanentně v .bashrc / .zshrc
echo 'export OLLAMA_KEEP_ALIVE=60m' >> ~/.bashrc
```

**Windows (PowerShell):**
```powershell
# Nastavte proměnnou prostředí
$env:OLLAMA_KEEP_ALIVE = "60m"

# Nebo permanentně
[System.Environment]::SetEnvironmentVariable("OLLAMA_KEEP_ALIVE", "60m", "User")
```

#### PrismQ Model Manager (doporučený přístup)

Pro optimální výkon použijte jednotný model pro celý workflow:

```python
import ollama

class PrismQModelManager:
    """Správce modelu pro efektivní využití VRAM."""
    
    _instance = None
    _current_model = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def ensure_model_loaded(self, model_name: str):
        """Načte model pouze pokud ještě není v paměti."""
        if self._current_model != model_name:
            # Warmup dotaz pro načtení modelu do VRAM
            ollama.chat(
                model=model_name,
                messages=[{"role": "user", "content": "Hello"}],
                options={"num_predict": 1}
            )
            self._current_model = model_name
            print(f"Model {model_name} načten do VRAM")
        return self._current_model

# Použití na začátku workflow
manager = PrismQModelManager.get_instance()
manager.ensure_model_loaded("qwen2.5:32b")

# Všechny následující dotazy použijí již načtený model
```

#### Doporučená strategie pro celý PrismQ workflow

| Fáze | Model | Důvod |
|------|-------|-------|
| **Idea → Title → Script → Review** | `qwen2.5:32b` | Jeden model pro celý workflow, bez přepínání |
| **SEO Metadata** (volitelně) | Přepnout na `llama3.3:70b-q4_K_M` | Pouze pokud je nutná lepší SEO kvalita |

> **Tip:** Pro maximální efektivitu používejte jeden model pro celý běh. Přepínání mezi modely vyžaduje uvolnění a načtení ~20-40GB dat, což trvá 10-30 sekund.

### Optimální konfigurace pro Ryzen 9 9900X3D + RTX 5090

Pro váš konkrétní hardware (AMD Ryzen 9 9900X3D + RTX 5090 32GB):

| Parametr | Doporučená hodnota | Důvod |
|----------|-------------------|-------|
| **Model** | `qwen2.5:32b` nebo `llama3.3:70b-q4_K_M` | Plně využije 32GB VRAM |
| **Kvantizace (70B)** | Q4_K_M | Optimální pro 32GB VRAM |
| **Context Length** | 8192-16384 | Využije 3D V-Cache pro KV cache |
| **Batch Size** | 1 | Standardní pro generování |
| **GPU Layers** | All (auto) | Celý model na GPU |

```bash
# Optimální Ollama konfigurace pro Ryzen 9 9900X3D + RTX 5090
export OLLAMA_NUM_PARALLEL=1          # Jeden request najednou
export OLLAMA_KEEP_ALIVE=60m          # Model zůstane v paměti
export OLLAMA_MAX_LOADED_MODELS=1     # Jeden model najednou (šetří VRAM)

# Spusťte Ollama
ollama serve
```

**Využití 3D V-Cache (141MB):**
Ryzen 9 9900X3D má masivní L3 cache, která pomáhá s:
- Rychlejším tokenizačním pre/post-processingem
- Efektivnějším CPU offloadingem (pokud potřebný)
- Nižší latencí při komunikaci s GPU

### Using MPT-7B-StoryWriter with HuggingFace

If you prefer the specialized MPT-7B-StoryWriter model:

```bash
pip install transformers torch accelerate
```

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "mosaicml/mpt-7b-storywriter"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True
)

prompt = "Write the opening chapter of a dark horror story set in a small Czech town:"
inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

outputs = model.generate(
    **inputs,
    max_new_tokens=1000,
    temperature=0.7,
    do_sample=True
)

print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

> **Note**: MPT-7B-StoryWriter requires manual setup with HuggingFace Transformers and is not directly supported by Ollama. For easier integration with PrismQ, we recommend Qwen2.5:32b.

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

The default configuration in PrismQ varies by module:
- **SEO Keywords Module**: Uses `llama3.1:70b-q4_K_M` (optimized for SEO tasks)
- **General Content Generation**: Recommended `qwen2.5:14b` (best for creative writing)

Common settings:
- **API Base**: `http://localhost:11434`
- **Temperature**: 0.3 (lower for more consistent output)

You can customize these settings using the `AIConfig` class to match your model choice.

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
- **[SEO Keywords Module](../../T/Publishing/SEO/Keywords/README.MD)** - SEO Keywords module documentation

## Version History

### 1.0.0 (2025-12-05)
- Initial documentation
- Ollama installation instructions
- Qwen2.5-14B model setup
- Python integration examples
