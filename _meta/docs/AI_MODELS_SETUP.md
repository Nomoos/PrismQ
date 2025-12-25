# AI Models Setup Guide

**Document Type**: Setup Guide  
**Scope**: Project-wide  
**Last Updated**: 2025-12-05

## Overview

PrismQ uses local LLM models through Ollama for AI-powered content generation and SEO metadata optimization. This guide covers how to set up Ollama and configure AI models for use with PrismQ.

### 🏆 Primary Local AI Model: Qwen 3:30B

**PrismQ uses Qwen 3:30B as the primary local AI model** for all generation and review tasks. This model provides the best balance of quality, speed, and VRAM efficiency for RTX 5090 systems.

| Aspect | Qwen 3:30B |
|--------|------------|
| **Role** | Primary local AI for generation & review |
| **Parameters** | 30B |
| **VRAM Usage** | ~19GB (fits comfortably in RTX 5090 32GB) |
| **Quality** | ⭐⭐⭐⭐⭐ |
| **Speed** | Fast |
| **Best For** | Script generation, Story review, Title creation, Idea generation |

```bash
# Quick start - Pull the primary model
ollama pull qwen3:32b
```

## Prerequisites

- Windows, macOS, or Linux operating system
- At least 16GB RAM (32GB recommended for larger models)
- GPU with sufficient VRAM for model inference (RTX 5090 with 32GB VRAM recommended)
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

## Step 2 – Pull the Qwen 3:30B Model (Primary)

**Qwen 3:30B is the primary local AI model for PrismQ.** It handles all generation and review tasks with excellent quality.

In your terminal, run:

```bash
ollama pull qwen3:32b
```

This will download approximately 19GB of model weights. The download time depends on your internet connection speed.

### Test the Model

After the download finishes, verify the installation:

```bash
ollama run qwen3:32b
```

You'll drop into an interactive prompt. Try something like:

```
Write a dark, emotional horror story opening set in a small Czech town at night.
```

If it responds with quality output, Qwen 3:30B is correctly installed.

### Qwen 3 Model Variants

| Model | Size | VRAM Required | Use Case |
|-------|------|---------------|----------|
| `qwen3:8b` | ~5GB | 8GB | Lighter weight, faster inference |
| `qwen3:14b` | ~9GB | 16GB | Good balance for mid-range GPUs |
| **`qwen3:32b`** | **~19GB** | **24GB+** | **🏆 PRIMARY - Best quality for RTX 5090** |
| `qwen3:72b` | ~45GB | 48GB+ | Premium quality, requires multi-GPU or quantization |

### Alternative: Qwen 2.5 Models (Legacy)

For systems that cannot run Qwen 3, Qwen 2.5 variants are available:

| Model | Size | VRAM Required | Use Case |
|-------|------|---------------|----------|
| `qwen2.5:7b` | ~4.5GB | 8GB | Lighter weight, faster inference |
| `qwen2.5:14b` | ~9GB | 16GB | Good balance of quality and speed |
| `qwen3:32b` | ~20GB | 24GB+ | High quality alternative |

```bash
# Legacy fallback
ollama pull qwen2.5:14b
```

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

### 🏆 Primary Model: Qwen 3:30B

**Qwen 3:30B is the recommended primary model for all PrismQ tasks on RTX 5090.**

| Aspect | Qwen 3:30B |
|--------|------------|
| **Parameters** | 30B |
| **VRAM Usage** | ~19GB |
| **Story Quality** | ⭐⭐⭐⭐⭐ |
| **Speed** | Fast |
| **Context** | 32K tokens |
| **Strengths** | Creative writing, review, generation |

```bash
# Install primary model
ollama pull qwen3:32b
```

### Recommended Models for RTX 5090

| Model | Parameters | VRAM Usage | Story Quality | Speed | Best For |
|-------|------------|------------|---------------|-------|----------|
| **🏆 Qwen3:30b** | 30B | ~19GB | ⭐⭐⭐⭐⭐ | Fast | **PRIMARY - All PrismQ tasks** |
| **Qwen3:72b-q4** | 72B | ~45GB | ⭐⭐⭐⭐⭐ | Medium | Premium quality with quantization |
| **Qwen2.5:32b** | 32B | ~20GB | ⭐⭐⭐⭐⭐ | Medium | Legacy fallback |
| **Llama3.3:70b-q4** | 70B | ~40GB | ⭐⭐⭐⭐⭐ | Slow | Alternative for specific tasks |

### Qwen 3 vs Qwen 2.5 Comparison

| Aspect | Qwen 2.5 | Qwen 3 | Improvement |
|--------|----------|--------|-------------|
| **Long-term coherence** | Good | Excellent | +40% |
| **English quality** | Good | Excellent | +35% |
| **World-building rules** | Moderate | Strong | Less hallucinations |
| **Dramatic structure** | Good | Excellent | +40% |
| **Lyrical imagery** | Moderate | Strong | +40% |
| **Emotional depth** | Good | Excellent | +30% |
| **Natural dialogue** | Good | Excellent | +35% |

> **Conclusion:** Qwen 3:30B provides ~30-40% improvement over Qwen 2.5:32b for creative writing tasks.

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
ollama pull qwen3:32b
```

> **Poznámka ke Q6_K:** I když Q6_K nabízí ~98.5% kvality, vyžaduje ~54GB VRAM pro 70B model. Na RTX 5090 (32GB) by musel použít CPU offloading, což dramaticky zpomalí inference. Pro vaši sestavu doporučuji Q4_K_M - ztráta kvality je minimální (~5%) a rychlost bude výrazně lepší.

### Model Recommendations by PrismQ Task

**Primary Model: Qwen 3:30B** is used for all PrismQ tasks for consistency and optimal performance.

| Task | Primary Model | Alternative | Why |
|------|---------------|-------------|-----|
| **Idea Generation** | **Qwen3:30b** | Llama 3.3:70b | Strong creative reasoning, diverse ideas |
| **Title Creation** | **Qwen3:30b** | Qwen2.5:14b | Fast, concise outputs, good for iteration |
| **Script Writing** | **Qwen3:30b** | Qwen2.5:32b | Best narrative quality, instruction following |
| **Review/Editing** | **Qwen3:30b** | Llama 3.3:70b | Superior analytical and reasoning capabilities |
| **SEO Metadata** | **Qwen3:30b** | Llama 3.1:70b-q4 | Consistent, structured outputs |

> **Note:** Using a single model (Qwen 3:30B) for all tasks avoids VRAM reloading delays and maintains consistency across the workflow.

#### Task-Specific Configuration:

```python
from T.Publishing.SEO.Keywords import AIConfig

# Primary model for all tasks
PRIMARY_MODEL = "qwen3:32b"

# Idea Generation - creative, diverse
idea_config = AIConfig(
    model=PRIMARY_MODEL,
    temperature=0.8,  # Higher for creativity
    enable_ai=True
)

# Title Creation - fast iteration
title_config = AIConfig(
    model=PRIMARY_MODEL,
    temperature=0.5,
    enable_ai=True
)

# Script Writing - high quality narrative
script_config = AIConfig(
    model=PRIMARY_MODEL,
    temperature=0.7,
    max_tokens=4000,
    enable_ai=True
)

# Review/Editing - analytical
review_config = AIConfig(
    model=PRIMARY_MODEL,
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

### 📚 Modely optimalizované pro tvorbu příběhů

Pro kreativní psaní a tvorbu příběhů existují specializované modely s lepším výkonem než obecné LLM:

#### 🧪 Reálné testy modelů (English YA Fiction)

Na základě interního testování PrismQ s anglickými příběhy pro US/CA publikum:

| Model | Test příběh | Skóre | Struktura | Dialog | Postavy | Napětí | Konzistence | Čitelnost | Poznámka |
|-------|-------------|-------|-----------|--------|---------|--------|-------------|-----------|----------|
| **qwen3:32b (EN)** | The Lighthouse Keeper's Secret | **7.8/10** | 8 | 9 | 6.5 | 8 | 7 | 7.5 | 7 | 🏆 Překvapivě čisté, soudržné, čtivé — mnohem lepší než CZ |
| **mistral-nemo:12b (EN)** | The Whispering Grove | **7.5/10** | 8 | 9 | 6 | 7.5 | 6 | 7 | 6 | Angličtina výrazně zvedá kvalitu, dobré YA-fantasy |

> **Klíčové zjištění:** Anglická verze výrazně převyšuje českou u obou modelů. Pro US/CA publikum doporučujeme vždy generovat v angličtině.

#### 🏆 Finální doporučení pro English YA Fiction

Na základě testů doporučujeme pro **americké/kanadské teen publikum**:

| Priorita | Model | Skóre | Nejlepší pro |
|----------|-------|-------|--------------|
| **#1** | **Qwen2.5:32b** | 7.8/10 | Family Drama, Teen Drama, Mystery |
| **#2** | **Mistral-Nemo:12b** | 7.5/10 | YA Fantasy, Slice of Life, Reddit Stories |

```bash
# Primární model pro EN YA content
ollama pull qwen3:32b

# Sekundární/rychlejší model
ollama pull mistral-nemo:12b
```

#### 🔍 Srovnání 32B modelů pro kreativní psaní

| Model | Fine-tuning | Kvalita prózy | Kontext | Angličtina | Ollama | Benchmarks |
|-------|-------------|---------------|---------|------------|--------|------------|
| **Qwen2.5:32b-Instruct** | General | ⭐⭐⭐⭐⭐ | 32K | Výborná | ✅ | MMLU: 83.5 |
| **Yi-1.5-34B-Chat** | Chat/Creative | ⭐⭐⭐⭐⭐ | 32K | Výborná | ✅ | MMLU: 81.2 |
| **DeepSeek-V2-Lite (27B)** | General | ⭐⭐⭐⭐ | 128K | Dobrá | ✅ | MMLU: 79.8 |
| **Mixtral-8x7B (47B MoE)** | Instruct | ⭐⭐⭐⭐⭐ | 32K | Výborná | ✅ | MMLU: 81.1 |
| **Command-R (35B)** | RAG/Chat | ⭐⭐⭐⭐ | 128K | Výborná | ✅ | MMLU: 78.5 |

#### 📖 Fine-tuned modely pro kreativní psaní (32B třída)

| Model | Specializace | Kvalita | VRAM | Zdroj |
|-------|--------------|---------|------|-------|
| **Nous-Hermes-2-Yi-34B** | Creative writing, RP | ⭐⭐⭐⭐⭐ | ~22GB | HuggingFace |
| **Airoboros-34B** | Creative, storytelling | ⭐⭐⭐⭐⭐ | ~22GB | HuggingFace |
| **Dolphin-2.6-Yi-34B** | Uncensored creative | ⭐⭐⭐⭐⭐ | ~22GB | HuggingFace |
| **Goliath-120B** (merged) | Premium creative | ⭐⭐⭐⭐⭐ | ~70GB | HuggingFace |
| **Chronos-Hermes-34B** | Long-form fiction | ⭐⭐⭐⭐⭐ | ~22GB | HuggingFace |
| **StellarBright-Qwen2.5-32B** | Creative writing | ⭐⭐⭐⭐⭐ | ~20GB | HuggingFace |

> **Poznámka:** Fine-tuned modely pro kreativní psaní často překonávají větší obecné modely v kvalitě narativu.

#### 🎯 Doporučení pro cílové publikum: Teen/Young Adult (10-20, US ženy)

Pro americké a kanadské anglicky mluvící publikum (především mladé ženy 10-20 let):

| Žánr | 🏆 Doporučený model | Alternativa | Proč |
|------|---------------------|-------------|------|
| **Reddit Stories** | Nous-Hermes-2-Yi-34B | Qwen2.5:32b | Autentický Reddit styl, relatable |
| **Family Drama** | Qwen2.5:32b | Airoboros-34B | Emocionální hloubka, realistické dialogy |
| **Teen Drama** | Dolphin-2.6-Yi-34B | Nous-Hermes-2-Yi-34B | Teen hlas, moderní slang |
| **Teen Stories** | Nous-Hermes-2-Yi-34B | Mistral-Nemo | YA narativ, engagement |
| **Romance (YA)** | Chronos-Hermes-34B | Qwen2.5:32b | Emotivní, clean romance |
| **Thriller/Mystery** | Qwen2.5:32b | Command-R | Napětí, twist endings |
| **AITA/Confession** | Nous-Hermes-2-Yi-34B | Dolphin-2.6-Yi-34B | Autentický POV |
| **Slice of Life** | Mistral-Nemo | Qwen2.5:32b | Každodenní situace, relatability |

#### 🏆 TOP 3 pro Teen/YA obsah na RTX 5090

**1. Nous-Hermes-2-Yi-34B** - Nejlepší pro Reddit/Teen stories
```bash
ollama pull nous-hermes2:yi-34b-q4_K_M
```
- Specializovaný na creative writing a roleplay
- Přirozený teen dialog a POV
- Výborný pro AITA, relationship drama, confession stories
- ~22GB VRAM (Q4)

**2. Qwen2.5:32b** - Univerzální vysoká kvalita
```bash
ollama pull qwen3:32b
```
- Nejlepší balance kvality a rychlosti
- Výborná angličtina, emotivní próza
- Ideální pro family drama, romance
- ~20GB VRAM

**3. Dolphin-2.6-Yi-34B** - Pro autentický teen hlas
```bash
ollama pull dolphin2.6:yi-34b-q4_K_M
```
- Uncensored, přirozené dialogy
- Moderní slang a teen expressions
- Vhodný pro edgier teen drama
- ~22GB VRAM (Q4)

#### 📊 Statistiky a benchmarky 32B modelů (creative writing)

Na základě komunitních testů a r/LocalLLaMA:

| Model | Reddit Stories | Dialogy | Emotivnost | Konzistence | Celkově |
|-------|----------------|---------|------------|-------------|---------|
| Nous-Hermes-2-Yi-34B | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **#1** |
| Qwen2.5:32b | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **#2** |
| Airoboros-34B | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **#3** |
| Yi-34B-Chat | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **#4** |

#### Konfigurace pro Teen/YA content

```python
from T.Publishing.SEO.Keywords import AIConfig

# Reddit Stories / AITA style
reddit_config = AIConfig(
    model="nous-hermes2:yi-34b-q4_K_M",
    temperature=0.85,           # Vyšší pro autenticitu
    max_tokens=3000,
    enable_ai=True
)

# Teen Drama / Family Drama
drama_config = AIConfig(
    model="qwen3:32b",
    temperature=0.75,
    max_tokens=4000,
    enable_ai=True
)

# Teen Stories (YA fiction)
teen_stories_config = AIConfig(
    model="nous-hermes2:yi-34b-q4_K_M",
    temperature=0.8,
    max_tokens=5000,           # Delší kapitoly
    enable_ai=True
)
```

#### Instalace modelů pro Teen/YA content

```bash
# Kompletní sada pro Teen/YA publikum na RTX 5090

# 1. Primární pro Reddit stories a teen drama
ollama pull nous-hermes2:yi-34b-q4_K_M

# 2. Univerzální vysoká kvalita
ollama pull qwen3:32b

# 3. Pro edgier teen content
ollama pull dolphin2.6:yi-34b-q4_K_M

# 4. Pro dlouhé série
ollama pull yi:34b-chat-q4_K_M
```

> **Tip pro US teen publikum:** Používejte `temperature=0.8-0.9` pro autentičtější dialogy. Teen content vyžaduje současný slang, pop culture reference a relatable situace.

#### Srovnání modelů pro psaní příběhů

| Model | Parametry | VRAM | Kvalita příběhů | Kontext | Ollama | Doporučení |
|-------|-----------|------|-----------------|---------|--------|------------|
| **Mistral-Nemo-Instruct-2407** | 12B | ~8GB | ⭐⭐⭐⭐⭐ | 128K | ✅ | 🏆 **NEJLEPŠÍ pro příběhy** |
| **Qwen2.5:32b** | 32B | ~20GB | ⭐⭐⭐⭐⭐ | 32K | ✅ | Výborná kvalita, versatilní |
| **Llama-3.1-Storm-8B** | 8B | ~6GB | ⭐⭐⭐⭐ | 8K | ✅ | Kreativní, rychlý |
| **Nous-Hermes-2-Mixtral** | 47B | ~28GB | ⭐⭐⭐⭐⭐ | 32K | ✅ | Nejlepší MoE pro příběhy |
| **Yi-34B-Chat** | 34B | ~22GB | ⭐⭐⭐⭐⭐ | 200K | ✅ | Extrémní kontext |
| **DeepSeek-Coder-V2-Lite** | 16B | ~10GB | ⭐⭐⭐⭐ | 128K | ✅ | Dobrý pro dialogy |
| **MPT-7B-StoryWriter** | 7B | ~8GB | ⭐⭐⭐⭐ | 65K | ❌ | Specializovaný na romány |
| **Fimbulvetr-11B** | 11B | ~8GB | ⭐⭐⭐⭐⭐ | 8K | ⚠️ | Výjimečný pro RP/fiction |

#### 🏆 Top 3 doporučené modely pro příběhy na RTX 5090

**1. Mistral-Nemo-Instruct-2407** - Nejlepší volba
```bash
ollama pull mistral-nemo:12b
```
- 128K tokenů kontextu (perfektní pro dlouhé příběhy)
- Výjimečná kreativita a koherence
- Optimalizováno pro narativní úlohy
- Vejde se do 32GB VRAM bez kvantizace

**2. Nous-Hermes-2-Mixtral-8x7B** - Premium kvalita
```bash
ollama pull nous-hermes2-mixtral:8x7b-q4_K_M
```
- MoE architektura (efektivní využití parametrů)
- Špičková kvalita prózy
- Vyžaduje ~28GB VRAM

**3. Yi-34B-Chat** - Pro extrémně dlouhé příběhy
```bash
ollama pull yi:34b-chat-q4_K_M
```
- 200K tokenů kontextu (nejdelší)
- Ideální pro romány a série
- Vyžaduje ~22GB VRAM (Q4)

#### Specializované modely pro různé žánry

| Žánr | Doporučený model | Alternativa |
|------|------------------|-------------|
| **Horror/Dark Fantasy** | Mistral-Nemo | Fimbulvetr-11B |
| **Romantika** | Qwen2.5:32b | Yi-34B-Chat |
| **Sci-Fi** | Nous-Hermes-2-Mixtral | DeepSeek-V2 |
| **Detektivky** | Llama 3.3:70b | Mistral-Nemo |
| **Dětské příběhy** | Qwen2.5:14b | Mistral-Nemo |
| **Epická fantasy** | Yi-34B-Chat | Nous-Hermes-2 |
| **Krátké povídky** | Mistral-Nemo | Qwen2.5:32b |
| **Dialogy/Scénáře** | Llama 3.3:70b | Qwen2.5:32b |

#### Instalace nejlepších modelů pro příběhy

```bash
# Kompletní sada pro profesionální tvorbu příběhů na RTX 5090

# 1. Primární model pro příběhy (doporučeno)
ollama pull mistral-nemo:12b

# 2. Pro dlouhé romány
ollama pull yi:34b-chat-q4_K_M

# 3. Pro premium kvalitu prózy
ollama pull nous-hermes2-mixtral:8x7b-q4_K_M

# 4. Univerzální záloha
ollama pull qwen3:32b
```

#### Konfigurace pro tvorbu příběhů

```python
from T.Publishing.SEO.Keywords import AIConfig

# Optimální konfigurace pro kreativní psaní příběhů
story_writing_config = AIConfig(
    model="mistral-nemo:12b",  # Nejlepší pro příběhy
    api_base="http://localhost:11434",
    temperature=0.8,           # Vyšší pro kreativitu
    max_tokens=4000,           # Dlouhé kapitoly
    enable_ai=True
)

# Pro velmi dlouhé příběhy (romány)
novel_config = AIConfig(
    model="yi:34b-chat-q4_K_M",
    temperature=0.7,
    max_tokens=8000,           # Celé kapitoly
    enable_ai=True
)

# Pro dialogy a scénáře
dialogue_config = AIConfig(
    model="llama3.3:70b-q4_K_M",
    temperature=0.6,           # Konzistentnější dialogy
    max_tokens=2000,
    enable_ai=True
)
```

> **Tip pro tvorbu příběhů:** Používejte vyšší `temperature` (0.7-0.9) pro kreativnější výstup. Pro konzistentní postavy a zápletky udržujte kontext a používejte modely s dlouhým kontextovým oknem (Yi-34B, Mistral-Nemo).

### 📖 Moving Window Text Generation (Profesionální pipeline pro romány)

Osvědčená metoda pro psaní dlouhých textů (romány, fanfikce, série) bez pádu kvality.

#### 🎯 Základní princip

Model **nikdy negeneruje celý text najednou**. Místo toho generuje "bloky" (250–600 slov) a po každém bloku:
1. Shrnutí (summary)
2. Extrakce klíčových faktů
3. Plán dalšího děje
4. Re-injekce postav a tónu

#### ⭐ Profesionální Pipeline (6 kroků)

**🔹 Krok 1 — Outline (kostra příběhu)**

```
Write a detailed story outline of 10–18 beats.
Include:
- setting
- main character arc
- emotional beats
- conflict escalation
- climax
- resolution
Keep it high-level.
```
> Použij nejsilnější model (GPT-5.1 / Claude Sonnet)

**🔹 Krok 2 — Story Bible (pravidla příběhu)**

Zůstává v kontextu celou dobu:
- Jména, motivace postav
- Jazykové preference
- Tone guide
- Zakázané halucinace
- Pravidla světa

**🔹 Krok 3 — Moving Window Writing**

| Model | Window Size |
|-------|-------------|
| **Qwen 32B** | 1000–1500 tokenů |
| **Mistral 12B** | 500–800 tokenů |

**Proces pro každý blok:**

```
1️⃣ GENERATE BLOCK (300–500 slov)
   → Model napíše další segment příběhu

2️⃣ SUMMARIZE BLOCK (150–250 slov)
   → Shrnutí slouží jako kondenzovaná paměť

3️⃣ EXTRACT FACTS ("story memory")
   Facts so far:
   - Clara moved to Willow Creek to escape city life.
   - Found Evelyn's letters in attic.
   - House shows supernatural behavior.
   - Primary emotional tone: melancholy + suspense.

4️⃣ DIRECTIVE (návod na další blok)
   Next segment should:
   - escalate tension
   - introduce secondary character
   - foreshadow climax
   - avoid info dumps
   - keep consistent voice

5️⃣ REINJEKCE
   Do promptu dáš:
   - Story bible
   - Shrnutí + fakta posledních bloků
   - Directive
   - Ukázka stylu
   → "Now continue the story."

6️⃣ OPAKUJ
   Dokud nemáš desítky tisíc slov.
```

#### 📊 Výsledky Moving Window vs Standard Generation

| Metoda | Max délka | Kvalita | Memory drift | Opakování |
|--------|-----------|---------|--------------|-----------|
| **Standard** | 1500–3000 slov | Klesá | ⚠️ Vysoký | ⚠️ Časté |
| **Moving Window** | 50 000+ slov | Stabilní | ✅ Žádný | ✅ Žádné |

**Zlepšení s Moving Window:**
- ✅ Žádný pád kvality
- ✅ Žádný memory drift
- ✅ Žádné kruhové opakování
- ✅ Lepší pacing a drama
- ✅ Konzistentní voice
- ✅ 2–3× vyšší originalita a hloubka

#### 🚀 Qwen 3 vs Qwen 2.5

| Aspekt | Qwen 2.5 | Qwen 3 | Zlepšení |
|--------|----------|--------|----------|
| Dlouhodobá koherence | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | +40% |
| Angličtina | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | +25% |
| Světová pravidla (méně halucinací) | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | +35% |
| Dramatická výstavba | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | +30% |
| Lyrika a imagery | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | +40% |
| Práce s emocemi | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | +30% |
| Přirozená řeč | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | +25% |

> **Qwen 3 32B** → srovnatelný s GPT-3.5 Turbo v angličtině  
> **Qwen 3 72B/110B** → blízko GPT-4.1 stylu tvorby příběhů

#### 🧩 Doporučené Pipeline pro dlouhé příběhy

**🟢 Level 1 — Lokální (bez cloudu)**
```
Qwen 3 72B → moving window → story bible → external summarizer
```
*Výsledek: Kompletní román*

**🟣 Level 2 — Hybrid (nejlepší cena/kvalita)**
```
1. Qwen 2.5-32B EN nebo Mistral 12B: draft
2. GPT-5.1 / Sonnet: review + rewrite
3. Czech translation (if needed)
4. Final polish GPT-5.1
```
*Funguje SKVĚLE pro PrismQ workflow*

**🔵 Level 3 — Nejvyšší kvalita**
```
1. GPT-5.1: outline + story bible
2. Qwen 3 32B: long draft generation
3. GPT-5.1: deep literary rewrite
4. GPT-5.1: final author-level polish
```
*Výsledek: Kvalita profesionální povídkové tvorby*

#### 💻 PrismQ Moving Window Implementation

```python
from T.Publishing.SEO.Keywords import AIConfig

class MovingWindowGenerator:
    """Moving Window generator pro dlouhé příběhy."""
    
    def __init__(self, model: str = "qwen3:32b"):
        self.config = AIConfig(
            model=model,
            api_base="http://localhost:11434",
            temperature=0.75,
            enable_ai=True
        )
        self.story_bible = ""
        self.facts = []
        self.summaries = []
    
    def set_story_bible(self, bible: str):
        """Nastaví Story Bible pro celý příběh."""
        self.story_bible = bible
    
    def generate_block(self, directive: str, window_size: int = 1200):
        """Generuje jeden blok příběhu."""
        context = self._build_context(directive)
        # Generate with context
        return self._call_model(context, window_size)
    
    def _build_context(self, directive: str) -> str:
        """Sestaví kontext pro generování."""
        recent_summaries = self.summaries[-3:]  # Poslední 3 shrnutí
        recent_facts = self.facts[-10:]  # Posledních 10 faktů
        
        return f'''
Story Bible:
{self.story_bible}

Recent Summaries:
{chr(10).join(recent_summaries)}

Story Facts:
{chr(10).join(recent_facts)}

Directive:
{directive}

Now continue the story:
'''

# Použití:
generator = MovingWindowGenerator("qwen3:32b")
generator.set_story_bible("""
Characters: Clara (28, melancholic), Evelyn (ghost, mysterious)
Setting: Willow Creek, haunted Victorian house
Tone: Gothic, suspenseful, emotional
Rules: No explicit violence, slow burn mystery
""")

# Generování bloků
block1 = generator.generate_block("Introduce Clara arriving at the house")
# ... summarize, extract facts, continue
```

#### 📋 Checklist pro Moving Window

- [ ] Story Bible připraven
- [ ] Outline hotový (10–18 beats)
- [ ] Window size nastaven podle modelu
- [ ] Summarizer nakonfigurován
- [ ] Fact extractor připraven
- [ ] Directive template vytvořen

### 🔗 Integrace Moving Window do PrismQ Workflow

Moving Window technika se hodí do **specifických kroků** PrismQ pipeline:

#### Kde použít Moving Window v PrismQ.T

| Stage | Moving Window? | Důvod |
|-------|----------------|-------|
| **PrismQ.T.Idea.From.User** | ❌ Ne | Krátký výstup (koncept) |
| **PrismQ.T.Story.From.Idea** | ⚠️ Volitelně | Pro detailnější Story Bible |
| **PrismQ.T.Title.From.Idea** | ❌ Ne | Krátký výstup (titulky) |
| **PrismQ.T.Content.From.Title.Idea** | ✅ **ANO** | 🏆 **HLAVNÍ USE CASE** |
| **PrismQ.T.Content.From.Title.Review.Script** | ✅ **ANO** | Refinement dlouhého scriptu |
| **PrismQ.T.Story.Polish** | ✅ **ANO** | Finální polish dlouhého textu |
| Review stages | ❌ Ne | Analytické, ne generativní |

#### 🏆 Primární integrace: Script Generation

```
PrismQ.T.Content.From.Title.Idea
    ↓
┌─────────────────────────────────────────────────────┐
│ 📖 MOVING WINDOW INTEGRATION                        │
├─────────────────────────────────────────────────────┤
│ 1. Načti Idea + Title jako "Story Bible"            │
│ 2. Vygeneruj Outline (10-18 beats) z Idea           │
│ 3. Pro každý beat:                                  │
│    a) Generate Block (300-500 slov)                 │
│    b) Summarize Block                               │
│    c) Extract Facts                                 │
│    d) Prepare Directive pro další beat              │
│    e) Reinjekce context + continue                  │
│ 4. Spojení bloků → Script v1                        │
└─────────────────────────────────────────────────────┘
    ↓
PrismQ.T.Review.Title.From.Script.Idea
```

#### Návrh integrace do PrismQ.T.Content

**Nový modul:** `T/Content/From/Idea/Title/MovingWindow/`

```python
# T/Content/From/Idea/Title/MovingWindow/generator.py

from dataclasses import dataclass
from typing import List, Optional
import ollama

@dataclass
class StoryBeat:
    """Jeden beat (segment) příběhu."""
    number: int
    directive: str
    content: str = ""
    summary: str = ""
    facts: List[str] = None

class PrismQMovingWindowScript:
    """
    Moving Window Script Generator pro PrismQ.T.Content.From.Title.Idea
    
    Integrace do workflow:
    - Input: Idea + Title z předchozích stages
    - Output: Script v1 (dlouhý text bez memory drift)
    """
    
    def __init__(
        self, 
        model: str = "qwen3:32b",
        window_size: int = 1200,  # tokens
        block_words: int = 400    # target words per block
    ):
        self.model = model
        self.window_size = window_size
        self.block_words = block_words
        self.story_bible = ""
        self.outline: List[StoryBeat] = []
        self.generated_blocks: List[str] = []
        self.summaries: List[str] = []
        self.facts: List[str] = []
    
    def from_idea_and_title(self, idea: dict, title: str) -> str:
        """
        Hlavní entry point pro PrismQ.T.Content.From.Title.Idea
        
        Args:
            idea: Idea objekt z PrismQ.T.Idea.From.User
            title: Title z PrismQ.T.Title.From.Idea
            
        Returns:
            Kompletní Script v1
        """
        # 1. Build Story Bible from Idea
        self.story_bible = self._build_story_bible(idea, title)
        
        # 2. Generate Outline (10-18 beats)
        self.outline = self._generate_outline(idea, title)
        
        # 3. Generate each beat using Moving Window
        for beat in self.outline:
            block = self._generate_block(beat)
            self.generated_blocks.append(block)
            
            # Summarize and extract facts
            summary = self._summarize_block(block)
            self.summaries.append(summary)
            
            facts = self._extract_facts(block)
            self.facts.extend(facts)
        
        # 4. Combine into final script
        return self._combine_script()
    
    def _build_story_bible(self, idea: dict, title: str) -> str:
        """Vytvoří Story Bible z Idea a Title."""
        return f'''
# Story Bible

## Title
{title}

## Core Concept
{idea.get("concept", "")}

## Target Audience
{idea.get("audience", "Teen/YA, 10-20, US women")}

## Tone
{idea.get("tone", "Engaging, emotional, relatable")}

## Characters
{idea.get("characters", "")}

## Setting
{idea.get("setting", "")}

## Rules
- No explicit content
- Consistent voice throughout
- Relatable situations for target audience
- Clear emotional arc
'''
    
    def _generate_outline(self, idea: dict, title: str) -> List[StoryBeat]:
        """Generuje 10-18 beat outline."""
        prompt = f'''Based on this idea and title, create a detailed story outline.

Title: {title}
Concept: {idea.get("concept", "")}

Write exactly 12 beats (story segments) that form a complete narrative arc:
- Beat 1-2: Setup and introduction
- Beat 3-4: Rising action begins
- Beat 5-6: Complications
- Beat 7-8: Midpoint twist
- Beat 9-10: Escalation
- Beat 11: Climax
- Beat 12: Resolution

For each beat, provide a 1-2 sentence directive of what should happen.
'''
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse response into StoryBeat objects
        return self._parse_outline(response["message"]["content"])
    
    def _generate_block(self, beat: StoryBeat) -> str:
        """Generuje jeden blok pomocí Moving Window."""
        # Build context from recent summaries and facts
        recent_context = self._build_recent_context()
        
        prompt = f'''
{self.story_bible}

## Previous Context
{recent_context}

## Current Directive (Beat {beat.number})
{beat.directive}

## Instructions
Write the next segment of the story (~{self.block_words} words).
- Continue naturally from previous context
- Follow the directive
- Maintain consistent voice and tone
- End at a natural pause point

Now continue the story:
'''
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            options={"num_predict": self.window_size}
        )
        
        return response["message"]["content"]
    
    def _build_recent_context(self) -> str:
        """Sestaví kontext z posledních shrnutí a faktů."""
        recent_summaries = self.summaries[-3:] if self.summaries else []
        recent_facts = self.facts[-15:] if self.facts else []
        
        context = ""
        if recent_summaries:
            context += "### Recent Summaries\n"
            context += "\n".join(recent_summaries)
            context += "\n\n"
        
        if recent_facts:
            context += "### Story Facts So Far\n"
            context += "\n".join(f"- {fact}" for fact in recent_facts)
        
        return context if context else "This is the beginning of the story."
    
    def _summarize_block(self, block: str) -> str:
        """Vytvoří shrnutí bloku."""
        prompt = f'''Summarize this story segment in 2-3 sentences:

{block}

Summary:'''
        
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            options={"num_predict": 200}
        )
        
        return response["message"]["content"]
    
    def _extract_facts(self, block: str) -> List[str]:
        """Extrahuje klíčová fakta z bloku."""
        prompt = f'''Extract 3-5 key facts from this story segment.
Format as simple bullet points.

{block}

Facts:'''
        
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            options={"num_predict": 300}
        )
        
        # Parse bullet points
        lines = response["message"]["content"].strip().split("\n")
        return [line.strip("- ").strip() for line in lines if line.strip()]
    
    def _combine_script(self) -> str:
        """Spojí všechny bloky do finálního scriptu."""
        return "\n\n".join(self.generated_blocks)
    
    def _parse_outline(self, outline_text: str) -> List[StoryBeat]:
        """Parsuje outline text do StoryBeat objektů."""
        beats = []
        lines = outline_text.strip().split("\n")
        beat_num = 0
        
        for line in lines:
            line = line.strip()
            if line and any(line.startswith(f"Beat {i}") or line.startswith(f"{i}.") or line.startswith(f"{i}:") for i in range(1, 19)):
                beat_num += 1
                directive = line.split(":", 1)[-1].strip() if ":" in line else line
                beats.append(StoryBeat(number=beat_num, directive=directive))
        
        return beats if beats else [StoryBeat(number=1, directive="Write the story")]


# Integrace do PrismQ workflow
def script_from_idea_title_moving_window(idea: dict, title: str) -> str:
    """
    Entry point pro PrismQ.T.Content.From.Title.Idea s Moving Window.
    
    Použití:
        from T.Script.From.Idea.Title.MovingWindow import script_from_idea_title_moving_window
        
        script = script_from_idea_title_moving_window(idea, title)
    """
    generator = PrismQMovingWindowScript(
        model="qwen3:32b",
        window_size=1200,
        block_words=400
    )
    return generator.from_idea_and_title(idea, title)
```

#### Konfigurace pro různé délky scriptu

| Délka scriptu | Počet beats | Block size | Celkem slov |
|---------------|-------------|------------|-------------|
| **Krátký** (Reddit story) | 5-8 | 300 slov | 1,500-2,400 |
| **Střední** (Short story) | 10-12 | 400 slov | 4,000-4,800 |
| **Dlouhý** (Novella) | 15-20 | 500 slov | 7,500-10,000 |
| **Velmi dlouhý** (Novel chapter) | 20-30 | 600 slov | 12,000-18,000 |

#### Doporučený workflow s Moving Window

```
┌─────────────────────────────────────────────────────────────┐
│                    PrismQ.T Pipeline                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Idea.From.User                                           │
│       ↓                                                     │
│  2. Story.From.Idea (creates Story Bible)                   │
│       ↓                                                     │
│  3. Title.From.Idea                                         │
│       ↓                                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 4. Script.From.Title.Idea                            │   │
│  │    ┌─────────────────────────────────────────────┐   │   │
│  │    │ 📖 MOVING WINDOW GENERATOR                  │   │   │
│  │    │                                             │   │   │
│  │    │  • Story Bible ← Idea + Title               │   │   │
│  │    │  • Outline (12 beats)                       │   │   │
│  │    │  • For each beat:                           │   │   │
│  │    │    → Generate Block                         │   │   │
│  │    │    → Summarize                              │   │   │
│  │    │    → Extract Facts                          │   │   │
│  │    │    → Prepare Directive                      │   │   │
│  │    │  • Combine → Script v1                      │   │   │
│  │    └─────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│       ↓                                                     │
│  5. Review.Title.From.Script.Idea                             │
│       ↓                                                     │
│  6-16. Quality Reviews (Grammar, Tone, Content...)          │
│       ↓                                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 17-18. Story.Review + Story.Polish                   │   │
│  │    (Moving Window pro Polish refinement)             │   │
│  └─────────────────────────────────────────────────────┘   │
│       ↓                                                     │
│  Publishing                                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Kdy použít Moving Window vs Standard Generation

| Situace | Metoda | Důvod |
|---------|--------|-------|
| Reddit Stories (<2000 slov) | Standard | Rychlejší, kontext stačí |
| Short Stories (2000-5000 slov) | Moving Window | Prevence memory drift |
| Novellas (5000-15000 slov) | Moving Window | **Povinné** |
| Novel chapters (15000+ slov) | Moving Window | **Povinné** |
| Title generation | Standard | Krátký výstup |
| Reviews | Standard | Analytické, ne generativní |
| Script refinement | Moving Window | Zachování konzistence |

For RTX 5090 with 32GB VRAM, we recommend:

```bash
# Best quality for story writing
ollama pull qwen3:32b

# Alternative for SEO and metadata
ollama pull llama3.1:70b-q4_K_M
```

**PrismQ Configuration for RTX 5090:**

```python
from T.Publishing.SEO.Keywords import AIConfig

# High-quality story generation config
story_config = AIConfig(
    model="qwen3:32b",
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
manager.ensure_model_loaded("qwen3:32b")  # Primary local model

# Všechny následující dotazy použijí již načtený model
```

#### Doporučená strategie pro celý PrismQ workflow

| Fáze | Model | Důvod |
|------|-------|-------|
| **Idea → Title → Script → Review** | `qwen3:32b` | 🏆 Jeden model pro celý workflow, bez přepínání |
| **SEO Metadata** (volitelně) | `qwen3:32b` | Konzistentní výstupy |

> **Tip:** Pro maximální efektivitu používejte jeden model (Qwen 3:30B) pro celý běh. Přepínání mezi modely vyžaduje uvolnění a načtení ~20-40GB dat, což trvá 10-30 sekund.

### Optimální konfigurace pro Ryzen 9 9900X3D + RTX 5090

Pro váš konkrétní hardware (AMD Ryzen 9 9900X3D + RTX 5090 32GB):

| Parametr | Doporučená hodnota | Důvod |
|----------|-------------------|-------|
| **Model** | `qwen3:32b` | 🏆 Primary local model, plně využije RTX 5090 |
| **VRAM Usage** | ~19GB | Dostatek prostoru pro context |
| **Context Length** | 8192-32768 | Využije 3D V-Cache pro KV cache |
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
ollama run qwen3:32b
```

You'll enter an interactive prompt. Try a test query:

```
Write a dark, emotional horror story opening set in a small Czech town at night.
```

If it responds with a story, Qwen 3:30B is correctly installed. Type `/bye` to exit.

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
    model="qwen3:32b",  # Primary local AI model
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

This directly uses your local Qwen 3:30B via Ollama's HTTP API on `localhost:11434`.

## PrismQ Integration

### Using AI in SEO Metadata Generation

PrismQ's SEO Keywords module already supports Ollama integration. Example usage:

```python
from T.Publishing.SEO.Keywords import process_content_seo, AIConfig

# Configure to use Qwen 3:30B (primary local model)
config = AIConfig(
    model="qwen3:32b",
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

---

## 🚀 After-Completion Feature / Future Enhancement

> **Poznámka od GPT:** Následující sekce popisuje budoucí rozšíření PrismQ systému, která navazují na Moving Window techniku dokumentovanou výše. Tyto funkce jsou navrženy jako nadstavba současné architektury bez breaking changes.

### 1) Moving-Window Engine pro dlouhé generování skriptů

Do budoucna lze nad textovým modulem PrismQ (`T → Script`) postavit specializovaný **moving-window engine**, který bude generovat příběhy nebo scénáře po blocích (300–600 slov) místo jednorázového dlouhého výstupu. 

**Klíčové vlastnosti:**
- Využívá **outline** a **story bible** vytvořené silným modelem (GPT-5.1 / Sonnet)
- Vede lokální modely (Qwen / Mistral) přes sekvenční generování
- Proces: shrnutí → extrakce faktů → plánování dalšího děje
- **Výsledek:** Lokální modely produkují delší a kvalitnější text bez ztráty konzistence

```
┌─────────────────────────────────────────────────────────────┐
│           MOVING-WINDOW ENGINE (Future)                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  GPT-5.1/Sonnet                                             │
│       │                                                     │
│       ├── Outline (10-18 beats)                             │
│       └── Story Bible                                       │
│              │                                              │
│              ▼                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Local Model (Qwen/Mistral) - Moving Window Loop    │   │
│  │                                                      │   │
│  │  Block 1 → Summary → Facts → Directive → Block 2    │   │
│  │  Block 2 → Summary → Facts → Directive → Block 3    │   │
│  │  ...                                                 │   │
│  │  Block N → Final Script                              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2) Story Bible, Block Memory a Directives jako nové datové vrstvy

Do struktury PrismQ lze doplnit volitelné budoucí objekty, které budou tvořit **persistentní "paměť" příběhu**:

| Objekt | Popis | Ukládání |
|--------|-------|----------|
| **StoryOutline** | Kostra příběhu (10-18 beats) | `T/{id}/Text/outline.json` |
| **StoryBible** | Postavy, pravidla, tone guide | `T/{id}/Text/bible.json` |
| **StoryBlock** | Jednotlivé bloky textu | `T/{id}/Text/blocks/` |
| **BlockSummary** | Shrnutí každého bloku | `T/{id}/Text/blocks/{n}/summary.txt` |
| **BlockFacts** | Extrahovaná fakta | `T/{id}/Text/blocks/{n}/facts.json` |
| **BlockDirective** | Instrukce pro další blok | `T/{id}/Text/blocks/{n}/directive.txt` |

**Ukládání a řízení:**
- Artefakty ukládány do `T/{id}/Text/...`
- Metadatově řízeny přes SQLite (`db.s3db`)
- Umožňuje sledovat a řídit dlouhodobou kontinuitu textu

**Integrace:**
```python
# Budoucí datová struktura
class StoryMemory:
    outline: StoryOutline        # 10-18 beats
    bible: StoryBible            # Characters, rules, tone
    blocks: List[StoryBlock]     # Generated blocks
    
class StoryBlock:
    number: int
    content: str                 # 300-600 slov
    summary: str                 # Kondenzovaná paměť
    facts: List[str]             # Klíčová fakta
    directive: str               # Instrukce pro další blok
```

> **Důležité:** Přidání těchto objektů rozšíří PrismQ o možnost sledovat a řídit dlouhodobou kontinuitu textu, **aniž by se měnila současná architektura** – jde o nadstavbu, ne o zásah do existujícího workflow.

### 3) Orchestrace blokového psaní jako volitelný Script-Draft mód

Moving-window systém může být v budoucnu zaveden jako **alternativní nebo pokročilý režim** pro fázi `T.Script`:

**Kdy se aktivuje:**
- Uživatel chce generovat dlouhé scénáře (5000+ slov)
- Povídky nebo podcastové epizody
- Serialized content (série)

**Zachování kompatibility:**
```
Současné workflow (beze změn):
    Idea → Title → Script → Reviews → Refinements

Nový "Loop Mode" (volitelný):
    Idea → Title → Script[Loop Mode] → Reviews → Refinements
                        │
                        ├── Block 1 → Summary → Facts
                        ├── Block 2 → Summary → Facts
                        ├── Block 3 → Summary → Facts
                        └── ... → Final Script
```

**Klíčové vlastnosti Loop Mode:**
- Sekvenčně orchestruje: **generování bloku → shrnutí → fakta → direktiva → další blok**
- Aktivuje se pouze na vyžádání
- **Žádné breaking changes** v současném workflow
- Umožní PrismQ růst směrem k robustnímu systémovému psaní delších textů

**Navržený API interface:**

```python
# Současný způsob (zachován)
script = Script.from_title_idea(title, idea)

# Nový Loop Mode (budoucí rozšíření)
script = Script.from_title_idea(
    title, 
    idea,
    mode="loop",           # Aktivuje Moving Window
    block_size=400,        # Slov na blok
    target_length=5000     # Celková délka
)
```

### 4) Integrating Iterative Text Refinement in the PrismQ Pipeline

> **Research Summary:** Tento výzkum popisuje, jak implementovat iterativní vylepšování textu v PrismQ při respektování SOLID principů.

#### 🎯 Základní principy

**Striktní oddělení odpovědností:**

| Typ modulu | Příklady | Funkce |
|------------|----------|--------|
| **Generation/Rewrite** | `Script.From.Title.Idea`, `Title.From.Script.Review.Title` | Produkují nebo přepisují text |
| **Review** | `Review.Script.From.Title`, `Review.Title.From.Script.Idea` | Pouze analyzují, nikdy nemění text |

**SOLID iterativní pipeline:**
```
Review = Diagnóza (score, issues, suggestions)
Rewrite = Léčba (aplikace změn na základě review)
```

#### 📍 Kde použít iterativní refinement v PrismQ

**2.1 Idea / Concept Generation**
```
Idea.Inspiration / Idea.Fusion / Idea.From.User
    ↓
Review (clarity, story arc potential, brand fit)
    ↓
Refine chosen idea (optional)
```

**2.2 Title Generation**
```
Title.From.Idea
    ↓
Review.Title.From.Script.Idea (SEO, VO-friendliness, tone)
    ↓
Title.From.Script.Review.Title (refinement loop)
```

**2.3 Script / Outline Generation** (hlavní use case)
```
Script.From.Title.Idea
    ↓
┌────────────────────────────────────────┐
│  ITERATIVE REFINEMENT LOOP             │
├────────────────────────────────────────┤
│  1. Review.Script.Grammar              │
│  2. Review.Script.Readability          │
│  3. Review.Script.Tone                 │
│  4. Review.Script.VO.Friendliness      │
│  5. Review.Script.Consistency          │
│       ↓                                │
│  Script.From.Title.Review.Script       │
│  (aplicuje změny z reviews)            │
│       ↓                                │
│  Loop until all reviews pass           │
└────────────────────────────────────────┘
    ↓
Final Script
```

**2.4 Voiceover Text Refinement**
```
Script (raw)
    ↓
Review.Script.VO.Friendliness
    - Pacing pro čtení nahlas
    - Sentence length pro breathing
    - Pronunciation issues
    ↓
Script.VO.Polish
    ↓
Final VO-ready text
```

#### 🔄 Iterativní smyčka - Implementace

```python
# Příklad iterativního refinement v PrismQ
class IterativeScriptRefinement:
    """
    Iterativní refinement pro Script s SOLID principy.
    
    Review moduly = pouze diagnóza
    Rewrite moduly = pouze léčba
    """
    
    MAX_ITERATIONS = 5
    QUALITY_THRESHOLD = 8.0  # Minimum score pro pass
    
    def __init__(self, script: str, title: str, idea: dict):
        self.script = script
        self.title = title
        self.idea = idea
        self.iteration = 0
        self.reviews = []
    
    def refine(self) -> str:
        """Hlavní refinement loop."""
        while self.iteration < self.MAX_ITERATIONS:
            self.iteration += 1
            
            # 1. REVIEW PHASE (diagnosis only)
            review_results = self._run_all_reviews()
            self.reviews.append(review_results)
            
            # 2. CHECK IF PASSED
            if self._all_reviews_passed(review_results):
                return self.script  # ✅ Quality threshold reached
            
            # 3. REWRITE PHASE (treatment)
            self.script = self._apply_refinements(review_results)
        
        return self.script  # Max iterations reached
    
    def _run_all_reviews(self) -> dict:
        """Spustí všechny review moduly (žádné změny textu)."""
        return {
            "grammar": Review.Script.Grammar(self.script),
            "readability": Review.Script.Readability(self.script),
            "tone": Review.Script.Tone(self.script, self.idea),
            "vo_friendliness": Review.Script.VO.Friendliness(self.script),
            "consistency": Review.Script.Consistency(self.script, self.idea),
        }
    
    def _all_reviews_passed(self, reviews: dict) -> bool:
        """Kontrola, zda všechny reviews prošly."""
        return all(
            review.score >= self.QUALITY_THRESHOLD 
            for review in reviews.values()
        )
    
    def _apply_refinements(self, reviews: dict) -> str:
        """Aplikuje refinement na základě review výsledků."""
        # Agreguje issues ze všech reviews
        all_issues = []
        for review in reviews.values():
            all_issues.extend(review.issues)
        
        # Volá rewrite modul s issues
        return Script.From.Title.Review.Script(
            script=self.script,
            title=self.title,
            issues=all_issues,
            suggestions=[r.suggestions for r in reviews.values()]
        )
```

#### 📊 Review Module Interface

```python
@dataclass
class ReviewResult:
    """Standardní výstup review modulu (SOLID - pouze diagnóza)."""
    
    score: float           # 0.0 - 10.0
    passed: bool           # score >= threshold
    issues: List[str]      # Seznam nalezených problémů
    suggestions: List[str] # Návrhy na zlepšení
    metrics: dict          # Detailní metriky
    
    # Review NIKDY neobsahuje:
    # - modified_text
    # - new_text
    # - corrections

# Příklad použití
grammar_review = Review.Script.Grammar(script)
# Returns:
# ReviewResult(
#     score=7.5,
#     passed=False,
#     issues=["Run-on sentence in paragraph 3", "Missing comma before 'and'"],
#     suggestions=["Split long sentences", "Add punctuation"],
#     metrics={"sentence_count": 45, "avg_length": 18.5}
# )
```

#### 🎛️ Konfigurace iterativního refinement

```python
# Konfigurace pro různé quality levels
REFINEMENT_CONFIGS = {
    "draft": {
        "max_iterations": 2,
        "quality_threshold": 6.0,
        "reviews": ["grammar", "readability"]
    },
    "standard": {
        "max_iterations": 3,
        "quality_threshold": 7.5,
        "reviews": ["grammar", "readability", "tone", "consistency"]
    },
    "premium": {
        "max_iterations": 5,
        "quality_threshold": 8.5,
        "reviews": ["grammar", "readability", "tone", "consistency", "vo_friendliness"]
    },
    "voiceover": {
        "max_iterations": 5,
        "quality_threshold": 9.0,
        "reviews": ["grammar", "readability", "vo_friendliness", "pacing", "pronunciation"]
    }
}
```

#### 🔗 Integrace s Moving Window

Iterativní refinement se kombinuje s Moving Window pro dlouhé texty:

```
┌─────────────────────────────────────────────────────────────┐
│  COMBINED PIPELINE: Moving Window + Iterative Refinement   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  FOR EACH BLOCK:                                            │
│    1. Generate Block (300-500 words)                        │
│    2. ┌─────────────────────────────────────┐              │
│       │  ITERATIVE REFINEMENT (per block)   │              │
│       │  - Review.Grammar                   │              │
│       │  - Review.Tone                      │              │
│       │  - Review.Consistency               │              │
│       │  → Refine until pass                │              │
│       └─────────────────────────────────────┘              │
│    3. Summarize Block                                       │
│    4. Extract Facts                                         │
│    5. Prepare Directive                                     │
│    6. Continue to next block                                │
│                                                             │
│  FINAL:                                                     │
│    - Combine all refined blocks                             │
│    - Final full-text review                                 │
│    - VO-friendliness pass                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 📋 Checklist pro implementaci

- [ ] Standardizovat `ReviewResult` interface pro všechny review moduly
- [ ] Review moduly nikdy nemění text (SOLID)
- [ ] Rewrite moduly přijímají issues + suggestions jako input
- [ ] Konfigurovat `max_iterations` a `quality_threshold` per use case
- [ ] Integrovat s Moving Window pro dlouhé texty
- [ ] VO-friendliness jako finální quality gate

### 5) Local AI Review Prompt for Qwen 3:30B

> **Recommended Model:** Qwen 3:30B for local AI generation and review tasks on RTX 5090.

This is the standard prompt for local AI story review using Qwen 3:30B. Use this prompt to get critical, actionable feedback on story drafts.

#### 📝 Story Review Prompt Template

```
Write a critical review of the following story that focuses exclusively on its biggest flaws in structure, pacing, worldbuilding, logic, thematic execution, and character development.

Requirements:

Length: Maximum 1200 words. Do NOT exceed.

Tone: analytical, objective, constructive; avoid excessive praise.

Do NOT summarize the entire plot.

Focus your critique on:

Major pacing and narrative-flow issues

Worldbuilding inconsistencies or contradictions

Logical gaps in the story's rules or mechanics

Underdeveloped or unclear character motivations

Thematic weaknesses or missed opportunities

Structural problems that reduce emotional impact

Use specific examples from the story for each flaw.

Provide actionable suggestions explaining how the author can improve or fix each issue.

Avoid:

Superlatives

Unjustified praise

Invention of scenes not present in the text

Vague criticism without evidence

Structure your review as follows:

Introduction: brief statement of what the story attempts to accomplish

Major Flaws: bullet points or subsections with evidence

Suggestions for Improvement: clear and practical

Conclusion: short summary of why the weaknesses matter

Final Score: Give a numerical score 0–100% based on overall effectiveness in light of its flaws

Readiness Statement:

If the score is 75% or higher, explicitly state: "This story is ready for final polish."

If the score is below 75%, explicitly state: "This story is not yet ready for final polish."

Now analyze the following story:
[INSERT STORY HERE]
```

#### 🔧 Usage in PrismQ

```python
import ollama

def review_story_local(story_text: str) -> dict:
    """
    Review a story using local Qwen 3:30B model.
    
    Args:
        story_text: The complete story text to review
        
    Returns:
        dict with review, score, and readiness status
    """
    
    REVIEW_PROMPT = """Write a critical review of the following story that focuses exclusively on its biggest flaws in structure, pacing, worldbuilding, logic, thematic execution, and character development.

Requirements:
- Length: Maximum 1200 words. Do NOT exceed.
- Tone: analytical, objective, constructive; avoid excessive praise.
- Do NOT summarize the entire plot.

Focus your critique on:
- Major pacing and narrative-flow issues
- Worldbuilding inconsistencies or contradictions
- Logical gaps in the story's rules or mechanics
- Underdeveloped or unclear character motivations
- Thematic weaknesses or missed opportunities
- Structural problems that reduce emotional impact

Use specific examples from the story for each flaw.
Provide actionable suggestions explaining how the author can improve or fix each issue.

Avoid:
- Superlatives
- Unjustified praise
- Invention of scenes not present in the text
- Vague criticism without evidence

Structure your review as follows:
1. Introduction: brief statement of what the story attempts to accomplish
2. Major Flaws: bullet points or subsections with evidence
3. Suggestions for Improvement: clear and practical
4. Conclusion: short summary of why the weaknesses matter
5. Final Score: Give a numerical score 0–100% based on overall effectiveness in light of its flaws

Readiness Statement:
- If the score is 75% or higher, explicitly state: "This story is ready for final polish."
- If the score is below 75%, explicitly state: "This story is not yet ready for final polish."

Now analyze the following story:
"""
    
    response = ollama.chat(
        model="qwen3:32b",  # Qwen 3:30B for local review
        messages=[
            {"role": "user", "content": REVIEW_PROMPT + story_text}
        ]
    )
    
    review_text = response["message"]["content"]
    
    # Parse score from review
    import re
    score_match = re.search(r'(\d+)%', review_text)
    score = int(score_match.group(1)) if score_match else 0
    
    return {
        "review": review_text,
        "score": score,
        "ready_for_polish": score >= 75,
        "model": "qwen3:32b"
    }
```

#### 📊 Integration with Iterative Refinement

This review prompt integrates with the iterative refinement pipeline:

```
Story Draft
    ↓
┌─────────────────────────────────────────┐
│  LOCAL REVIEW (Qwen 3:30B)              │
│  - Critical analysis                     │
│  - Score 0-100%                          │
│  - Actionable suggestions                │
└─────────────────────────────────────────┘
    ↓
Score >= 75%? ──→ YES → "Ready for final polish"
    │
    NO
    ↓
┌─────────────────────────────────────────┐
│  REWRITE (apply suggestions)            │
│  - Fix major flaws                       │
│  - Address pacing issues                 │
│  - Strengthen character motivations      │
└─────────────────────────────────────────┘
    ↓
Loop back to LOCAL REVIEW
```

#### ⚙️ Ollama Setup for Qwen 3:30B

```bash
# Pull Qwen 3:30B model
ollama pull qwen3:32b

# Or with specific quantization for RTX 5090 (32GB VRAM)
ollama pull qwen3:32b-q4_K_M

# Set keep-alive for efficient batch processing
export OLLAMA_KEEP_ALIVE=60m
```

### Roadmap implementace

| Fáze | Funkce | Priorita | Závislosti |
|------|--------|----------|------------|
| **Phase 1** | StoryOutline + StoryBible objekty | 🟢 Vysoká | Žádné |
| **Phase 2** | StoryBlock + Memory persistence | 🟡 Střední | Phase 1 |
| **Phase 3** | Moving-Window Engine | 🟡 Střední | Phase 1, 2 |
| **Phase 4** | Loop Mode v T.Script | 🟠 Nízká | Phase 1, 2, 3 |
| **Phase 5** | GPT-5.1 orchestrace | 🟠 Nízká | Phase 1-4 |
| **Phase 6** | ReviewResult interface standardizace | 🟢 Vysoká | Žádné |
| **Phase 7** | Iterative Refinement Loop | 🟡 Střední | Phase 6 |
| **Phase 8** | VO-Friendliness review modul | 🟡 Střední | Phase 6 |
| **Phase 9** | Combined MW + IR pipeline | 🟠 Nízká | Phase 3, 7 |
| **Phase 10** | Local AI Review with Qwen 3:30B | 🟢 Vysoká | Phase 6 |

---

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
