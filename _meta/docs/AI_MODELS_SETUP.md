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

### 📚 Modely optimalizované pro tvorbu příběhů

Pro kreativní psaní a tvorbu příběhů existují specializované modely s lepším výkonem než obecné LLM:

#### 🧪 Reálné testy modelů (English YA Fiction)

Na základě interního testování PrismQ s anglickými příběhy pro US/CA publikum:

| Model | Test příběh | Skóre | Struktura | Dialog | Postavy | Napětí | Konzistence | Čitelnost | Poznámka |
|-------|-------------|-------|-----------|--------|---------|--------|-------------|-----------|----------|
| **qwen2.5:32b (EN)** | The Lighthouse Keeper's Secret | **7.8/10** | 8 | 9 | 6.5 | 8 | 7 | 7.5 | 7 | 🏆 Překvapivě čisté, soudržné, čtivé — mnohem lepší než CZ |
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
ollama pull qwen2.5:32b

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
ollama pull qwen2.5:32b
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
    model="qwen2.5:32b",
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
ollama pull qwen2.5:32b

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
ollama pull qwen2.5:32b
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
    
    def __init__(self, model: str = "qwen2.5:32b"):
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
generator = MovingWindowGenerator("qwen2.5:32b")
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
| **PrismQ.T.Idea.Creation** | ❌ Ne | Krátký výstup (koncept) |
| **PrismQ.T.Story.From.Idea** | ⚠️ Volitelně | Pro detailnější Story Bible |
| **PrismQ.T.Title.From.Idea** | ❌ Ne | Krátký výstup (titulky) |
| **PrismQ.T.Script.From.Title.Idea** | ✅ **ANO** | 🏆 **HLAVNÍ USE CASE** |
| **PrismQ.T.Script.From.Title.Review.Script** | ✅ **ANO** | Refinement dlouhého scriptu |
| **PrismQ.T.Story.Polish** | ✅ **ANO** | Finální polish dlouhého textu |
| Review stages | ❌ Ne | Analytické, ne generativní |

#### 🏆 Primární integrace: Script Generation

```
PrismQ.T.Script.From.Title.Idea
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
PrismQ.T.Review.Title.By.Script.Idea
```

#### Návrh integrace do PrismQ.T.Script

**Nový modul:** `T/Script/From/Idea/Title/MovingWindow/`

```python
# T/Script/From/Idea/Title/MovingWindow/generator.py

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
    Moving Window Script Generator pro PrismQ.T.Script.From.Title.Idea
    
    Integrace do workflow:
    - Input: Idea + Title z předchozích stages
    - Output: Script v1 (dlouhý text bez memory drift)
    """
    
    def __init__(
        self, 
        model: str = "qwen2.5:32b",
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
        Hlavní entry point pro PrismQ.T.Script.From.Title.Idea
        
        Args:
            idea: Idea objekt z PrismQ.T.Idea.Creation
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
    Entry point pro PrismQ.T.Script.From.Title.Idea s Moving Window.
    
    Použití:
        from T.Script.From.Idea.Title.MovingWindow import script_from_idea_title_moving_window
        
        script = script_from_idea_title_moving_window(idea, title)
    """
    generator = PrismQMovingWindowScript(
        model="qwen2.5:32b",
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
│  1. Idea.Creation                                           │
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
│  5. Review.Title.By.Script.Idea                             │
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
