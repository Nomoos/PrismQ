# Návrh dalšího vývoje - PrismQ Scripts
*Future Implementation Recommendations*

**Datum:** 2025-12-10  
**Verze:** 1.0  
**Navazuje na:** [FUNKCIONALITA_AKTUALNI.md](FUNKCIONALITA_AKTUALNI.md)

---

## 🎯 Executive Summary

Současně je **funkčních pouze 3 z 30 workflow stages** (10%). Tento dokument navrhuje **prioritizovaný plán** pro dokončení zbývajících 27 stages.

**Klíčová doporučení:**
1. ✅ Dokončit Text Pipeline (stages 04-20) - **PRIORITA 1**
2. 🔊 Implementovat Audio Pipeline (stages 21-25) - **PRIORITA 2**
3. 🎬 Implementovat Video Pipeline (stages 26-28) - **PRIORITA 3**
4. 📤 Implementovat Publishing & Analytics (stages 29-30) - **PRIORITA 4**

---

## 📋 Prioritizační matice

| Priorita | Stages | Důvod | Odhadovaná práce | Business value |
|-----------|--------|-------|------------------|----------------|
| **P0 - CRITICAL** | 04 | Blokuje celý workflow | 2-3 týdny | 🔴 CRITICAL |
| **P1 - HIGH** | 05-10 | Review & refinement loop | 4-6 týdnů | 🟠 HIGH |
| **P2 - MEDIUM** | 11-17 | Quality assurance | 3-4 týdny | 🟡 MEDIUM |
| **P3 - MEDIUM** | 18-20 | Text finalization | 2-3 týdny | 🟡 MEDIUM |
| **P4 - LOW** | 21-25 | Audio generation | 6-8 týdnů | 🟢 LOW |
| **P5 - LOW** | 26-28 | Video generation | 8-10 týdnů | 🟢 LOW |
| **P6 - LOW** | 29-30 | Publishing & metrics | 2-4 týdny | 🟢 LOW |

**Celkem:** ~27-38 týdnů (~6-9 měsíců) pro kompletní implementaci

---

## 🚀 PRIORITA 0: Stage 04 - Script Generation (KRITICKÁ)

### 📍 Stage 04: Script.From.Title.Idea

**Status:** ⚠️ **BLOKUJE CELÝ WORKFLOW**

**Proč je kritická:**
- Bez stage 04 nelze pokračovat v žádném dalším kroku
- Stages 05-30 závisí na scriptech generovaných v stage 04
- Je to "missing link" mezi ideou/titulkem a zbytkem pipeline

**Co implementovat:**

```
T/Script/From/Title/Idea/src/
├── __init__.py
├── script_from_title_idea_interactive.py  # Hlavní aplikace
├── script_from_title_idea_service.py      # Service layer
├── ai_script_generator.py                  # AI generování scriptů
├── script_structurer.py                    # Strukturování scriptů
├── script_validator.py                     # Validace kvality
└── requirements.txt                        # Dependencies
```

**Funkční požadavky:**
1. ✅ Načíst Idea z databáze
2. ✅ Načíst Title z databáze
3. ✅ Generovat Script pomocí AI (Ollama)
4. ✅ Strukturovat script (úvod, tělo, závěr)
5. ✅ Validovat kvalitu scriptu
6. ✅ Uložit Script do databáze
7. ✅ Preview režim pro testování
8. ✅ Continuous mode

**AI integrace:**
- Model: qwen3:32b (již používán)
- Input: Idea + Title
- Output: Strukturovaný Script
- Format: Markdown s sekcemi

**Odhadovaná práce:** 2-3 týdny  
**Business value:** 🔴 KRITICKÁ

---

## 🎯 PRIORITA 1: Stages 05-10 - Review & Refinement Loop

### Přehled stages:

```
05 → Review.Title.From.Script.Idea
06 → Review.Script.From.Title.Idea
07 → Review.Title.From.Script
08 → Title.From.Script.Review.Title
09 → Script.From.Title.Review.Script
10 → Review.Script.From.Title
```

**Účel:** Iterativní zlepšování titulku a scriptu pomocí AI review

### 🔄 Review Loop Pattern

**Obecný pattern pro všechny review stages:**

```python
# Pseudo-kód review loop
def review_stage(input_data):
    1. Load data from database
    2. Generate AI review using Ollama
    3. Score quality (0-100)
    4. Identify issues
    5. Generate suggestions
    6. Save review to database
    7. Return review object
```

### Stage 05: Review.Title.From.Script.Idea

**Implementovat:**
```
T/Review/Title/From/Script/Idea/src/
├── title_review_service.py
├── ai_title_reviewer.py
├── review_scorer.py
└── requirements.txt
```

**Funkce:**
- Porovná Title vs. Script + Idea
- Zjistí nesrovnalosti
- Navrhne vylepšení
- Skóruje kvalitu (0-100)

---

### Stage 06: Review.Script.From.Title.Idea

**Implementovat:**
```
T/Review/Script/From/Title/Idea/src/
├── script_review_service.py
├── ai_script_reviewer.py
├── consistency_checker.py
└── requirements.txt
```

**Funkce:**
- Porovná Script vs. Title + Idea
- Zjistí odchylky od záměru
- Kontrola konzistence
- Skóruje kvalitu

---

### Stage 07: Review.Title.From.Script

**Implementovat:**
```
T/Review/Title/From/Script/src/
├── title_script_review_service.py
├── alignment_checker.py
└── requirements.txt
```

**Funkce:**
- Finální review titulku proti scriptu
- Kontrola alignment
- Doporučení pro úpravy

---

### Stage 08: Title.From.Script.Review.Title

**Implementovat:**
```
T/Title/From/Script/Review/Title/src/
├── title_refiner.py
├── ai_title_improver.py
└── requirements.txt
```

**Funkce:**
- Vylepší Title na základě review
- AI-powered refinement
- Zachová původní záměr

---

### Stage 09: Script.From.Title.Review.Script

**Implementovat:**
```
T/Script/From/Title/Review/Script/src/
├── script_refiner.py
├── ai_script_improver.py
└── requirements.txt
```

**Funkce:**
- Vylepší Script na základě review
- Implementuje suggestions
- Udržuje konzistenci

---

### Stage 10: Review.Script.From.Title

**Implementovat:**
```
T/Review/Script/From/Title/src/
├── final_review_service.py
├── quality_checker.py
└── requirements.txt
```

**Funkce:**
- Finální review před QA
- Kontrola konzistence
- Approval/rejection

---

**Odhadovaná práce pro stages 05-10:** 4-6 týdnů  
**Business value:** 🟠 HIGH - Zajišťuje kvalitu obsahu

---

## 📝 PRIORITA 2: Stages 11-17 - Quality Assurance Pipeline

### Přehled stages:

```
11 → Review.Script.Grammar
12 → Review.Script.Tone
13 → Review.Script.Content
14 → Review.Script.Consistency
15 → Review.Script.Editing
16 → Review.Title.Readability
17 → Review.Script.Readability
```

**Účel:** Specializované QA checks pro grammar, tone, content, style

### 🔍 QA Pattern

**Obecný pattern pro QA stages:**

```python
def qa_check(script_or_title):
    1. Load from database
    2. Run specialized check (grammar/tone/content/etc.)
    3. Generate detailed report
    4. Score 0-100
    5. List issues with line numbers
    6. Suggest fixes
    7. Save report to database
    8. Return pass/fail + score
```

### Implementace stages 11-17

**Struktura pro každý stage:**
```
T/Review/Script/{Aspect}/src/
├── {aspect}_checker.py       # Main checker
├── ai_{aspect}_analyzer.py   # AI analysis
├── {aspect}_rules.py          # Rules/patterns
└── requirements.txt
```

**Aspects:**
- Grammar - Gramatická kontrola
- Tone - Kontrola tónu (formal/informal/neutral)
- Content - Faktická správnost
- Consistency - Konzistence stylu
- Editing - Finální editace
- Readability (Title) - Čitelnost titulku
- Readability (Script) - Čitelnost scriptu

### Speciální požadavky:

**Grammar Check (11):**
- Integrace s LanguageTool nebo podobným
- České i anglické texty
- Report s line numbers

**Tone Check (12):**
- Detekce tónu pomocí AI
- Srovnání s požadovaným tónem z Idea
- Consistency check

**Content Check (13):**
- Faktická kontrola (pokud možno)
- Logická konzistence
- Chybějící informace

**Consistency Check (14):**
- Terminologie
- Styl psaní
- Formátování

**Editing Check (15):**
- Final pass
- Typos, spacing
- Formátování

**Readability Checks (16-17):**
- Flesch Reading Ease
- Sentence length analysis
- Complexity metrics

**Odhadovaná práce:** 3-4 týdny  
**Business value:** 🟡 MEDIUM - Zajišťuje profesionalitu

---

## 📚 PRIORITA 3: Stages 18-20 - Story Finalization

### Stage 18: Story.Review

**Status:** ⚠️ Částečná implementace existuje (`T/Story/Review/`)

**Co udělat:**
1. ✅ Propojit existující `review.py` s workflow
2. ✅ Přidat `expert_review.py` integraci
3. ✅ Vytvořit batch script wrappers
4. ✅ Testování a dokumentace

**Odhadovaná práce:** 1 týden

---

### Stage 19: Story.Polish

**Status:** ⚠️ Částečná implementace (`T/Story/Polish/polish.py`)

**Co udělat:**
1. ✅ Propojit s workflow
2. ✅ AI-powered polishing
3. ✅ Final touch-ups
4. ✅ Batch scripts

**Odhadovaná práce:** 1 týden

---

### Stage 20: Publishing (Text)

**Status:** ⚠️ Publishing komponenty existují, nejsou připojeny

**Existující komponenty:**
```
T/Publishing/
├── ContentExport/content_export.py
├── Formatter/
│   ├── Blog/blog_formatter.py
│   └── Social/*.py (twitter, linkedin, etc.)
├── SEO/
│   ├── Keywords/*.py
│   └── Taxonomy/*.py
└── ReportGeneration/report_generation.py
```

**Co udělat:**
1. ✅ Integrovat existující komponenty
2. ✅ Vytvořit unified publishing service
3. ✅ Multi-platform export (blog, social media)
4. ✅ SEO optimization
5. ✅ Report generation
6. ✅ Batch scripts

**Odhadovaná práce:** 1-2 týdny

---

**Celková práce pro stages 18-20:** 2-3 týdny  
**Business value:** 🟡 MEDIUM - Kompletuje Text pipeline

---

## 🔊 PRIORITA 4: Stages 21-25 - Audio Generation Pipeline

### Status: ❌ Kompletně neimplementováno

### Co je třeba vytvořit:

```
A/
├── Voiceover/
│   ├── src/
│   │   ├── text_to_speech.py
│   │   ├── voice_selector.py
│   │   └── tts_service.py
│   └── requirements.txt
├── Narrator/
│   ├── src/
│   │   ├── narrator_manager.py
│   │   └── voice_profiles.py
│   └── requirements.txt
├── Normalized/
│   ├── src/
│   │   ├── audio_normalizer.py
│   │   └── lufs_processor.py
│   └── requirements.txt
├── Enhancement/
│   ├── src/
│   │   ├── audio_enhancer.py
│   │   ├── eq_processor.py
│   │   └── compressor.py
│   └── requirements.txt
└── Publishing/
    ├── src/
    │   ├── audio_publisher.py
    │   ├── rss_generator.py
    │   └── platform_uploader.py
    └── requirements.txt
```

### Stage 21: Voiceover

**Technologie:**
- **TTS Engine:** OpenAI TTS, ElevenLabs, nebo lokální Coqui TTS
- **Format:** WAV/MP3
- **Quality:** 44.1kHz, 16-bit minimum

**Funkce:**
- Load Script from database
- Convert text to speech
- Multiple voice options
- Preview režim
- Save audio file + metadata

---

### Stage 22: Narrator Selection

**Funkce:**
- Voice profile management
- A/B testing different voices
- User preferences
- Quality scoring

---

### Stage 23: Audio Normalization

**Technologie:**
- **Python:** pydub, ffmpeg-python
- **LUFS:** -16 LUFS for podcasts, -14 LUFS for YouTube

**Funkce:**
- Loudness normalization
- Peak limiting
- LUFS analysis
- Batch processing

---

### Stage 24: Audio Enhancement

**Technologie:**
- **Python:** pydub, librosa, soundfile
- **Processing:** EQ, compression, noise reduction

**Funkce:**
- EQ adjustment
- Dynamic range compression
- Noise reduction (if needed)
- Final mastering

---

### Stage 25: Audio Publishing

**Platformy:**
- Spotify (RSS)
- Apple Podcasts (RSS)
- YouTube (audio only)
- SoundCloud
- Custom RSS feed

**Funkce:**
- Generate RSS feed
- Upload to platforms
- Metadata tagging
- Analytics tracking

---

**Odhadovaná práce:** 6-8 týdnů  
**Business value:** 🟢 LOW - Rozšiřuje formáty obsahu

---

## 🎬 PRIORITA 5: Stages 26-28 - Video Generation Pipeline

### Status: ⚠️ Pouze ukázkový kód

### Co je třeba implementovat:

```
V/
├── Scene/
│   ├── src/
│   │   ├── scene_planner.py
│   │   ├── script_analyzer.py
│   │   └── scene_generator.py
│   └── requirements.txt
├── Keyframe/
│   ├── src/
│   │   ├── keyframe_planner.py
│   │   ├── image_generator.py     # Stable Diffusion
│   │   └── keyframe_manager.py
│   └── requirements.txt
└── Video/
    ├── src/
    │   ├── video_assembler.py
    │   ├── timeline_builder.py
    │   └── renderer.py
    └── requirements.txt
```

### Stage 26: Scene Planning

**Funkce:**
- Analyzovat Script
- Rozdělit na scenes
- Určit visual elements
- Timing pro každou scénu

---

### Stage 27: Keyframe Generation

**Technologie:**
- **Stable Diffusion:** Pro generování obrázků
- **DALL-E / Midjourney API:** Alternativy
- **Lokální:** ComfyUI nebo Automatic1111

**Funkce:**
- Generate keyframes z popisů scén
- Consistent style across frames
- Preview režim
- Batch generation

---

### Stage 28: Video Assembly

**Technologie:**
- **Python:** moviepy, ffmpeg-python
- **Format:** MP4, 1080p minimum

**Funkce:**
- Combine audio + keyframes
- Add transitions
- Add subtitles (optional)
- Render final video
- Preview režim

---

**Odhadovaná práce:** 8-10 týdnů  
**Business value:** 🟢 LOW - Nejsložitější, ale přidává nejvíc value

---

## 📤 PRIORITA 6: Stages 29-30 - Publishing & Analytics

### Stage 29: Multi-platform Publishing

**Platformy:**
- YouTube
- TikTok
- Instagram Reels
- Facebook
- LinkedIn
- Twitter/X

**Funkce:**
- Upload video/audio/text
- Platform-specific formatting
- Scheduling
- Metadata optimization
- Cross-posting

**Odhadovaná práce:** 2-3 týdny

---

### Stage 30: Metrics & Analytics

**Co měřit:**
- Views, likes, shares
- Engagement rate
- Watch time
- Click-through rate
- Conversion metrics
- A/B test results

**Funkce:**
- Collect metrics from all platforms
- Aggregate analytics
- Generate reports
- Feed back to Idea generation (feedback loop)
- Dashboard visualization

**Odhadovaná práce:** 1-2 týdny

---

**Celková práce pro stages 29-30:** 2-4 týdny  
**Business value:** 🟢 LOW - Důležité pro měření úspěchu

---

## 🗓️ Doporučený Timeline

### Fáze 1: Text Pipeline Completion (3-4 měsíce)

**Milestones:**
```
Week 1-3:   Stage 04 - Script Generation ✅
Week 4-9:   Stages 05-10 - Review Loop ✅
Week 10-13: Stages 11-17 - QA Pipeline ✅
Week 14-16: Stages 18-20 - Finalization ✅
```

**Výstup:** Funkční Text Pipeline (stages 01-20)

---

### Fáze 2: Audio Pipeline (2 měsíce)

**Milestones:**
```
Week 17-20: Stages 21-23 - TTS + Normalization ✅
Week 21-24: Stages 24-25 - Enhancement + Publishing ✅
```

**Výstup:** Funkční Audio Pipeline (stages 21-25)

---

### Fáze 3: Video Pipeline (2-3 měsíce)

**Milestones:**
```
Week 25-28: Stage 26 - Scene Planning ✅
Week 29-32: Stage 27 - Keyframe Generation ✅
Week 33-36: Stage 28 - Video Assembly ✅
```

**Výstup:** Funkční Video Pipeline (stages 26-28)

---

### Fáze 4: Distribution & Analytics (1 měsíc)

**Milestones:**
```
Week 37-39: Stage 29 - Publishing ✅
Week 40-41: Stage 30 - Analytics ✅
Week 42:    Integration testing ✅
```

**Výstup:** Kompletní PrismQ Platform

---

**Total: ~9-10 měsíců pro kompletní implementaci**

---

## 🎯 Quick Wins (Rychlé úspěchy)

### 1. Stage 04 (2-3 týdny)

**Proč:** Odblokuje celý workflow  
**Effort:** Medium  
**Impact:** 🔴 CRITICAL

---

### 2. Stages 05-07 (2-3 týdny)

**Proč:** Základní review loop  
**Effort:** Medium  
**Impact:** 🟠 HIGH

---

### 3. Propojit existující komponenty (1 týden)

**Co:**
- Story Review (stage 18)
- Story Polish (stage 19)
- Publishing komponenty (stage 20)

**Proč:** Kód již existuje, jen chybí propojení  
**Effort:** Low  
**Impact:** 🟡 MEDIUM

---

## 🔧 Technické doporučení

### 1. Standardizace patterns

**Vytvořit:**
```
T/_meta/templates/
├── service_template.py        # Template pro service layer
├── interactive_template.py    # Template pro CLI
├── ai_generator_template.py   # Template pro AI integration
└── batch_template.bat         # Template pro batch skripty
```

**Benefit:** Konzistence a rychlejší vývoj

---

### 2. Shared utilities

**Vytvořit:**
```
T/_shared/
├── database.py           # Database utilities
├── ollama_client.py      # Shared Ollama client
├── validation.py         # Shared validators
├── scoring.py            # Shared scoring logic
└── logging.py            # Shared logging
```

**Benefit:** Reusability a DRY principle

---

### 3. Testing framework

**Implementovat:**
```
_meta/tests/
├── integration/          # Integration tests
├── e2e/                  # End-to-end tests
└── performance/          # Performance tests
```

**Benefit:** Kvalita a confidence v kódu

---

### 4. CI/CD Pipeline

**Implementovat:**
```
.github/workflows/
├── test.yml              # Run tests on PR
├── validate.yml          # Validate mermaid diagrams
└── deploy.yml            # Deploy on merge
```

**Benefit:** Automatizace a quality gates

---

## 📊 ROI Analysis

### Fáze 1 (Text Pipeline): HIGH ROI

**Proč:**
- Dokončí 20/30 stages (67%)
- Využívá existující AI infrastrukturu
- Nejmenší technická složitost
- Nejvyšší business value

**Cost:** 3-4 měsíce  
**Return:** Kompletní text production platform

---

### Fáze 2 (Audio Pipeline): MEDIUM ROI

**Proč:**
- Rozšiřuje formáty (text → audio)
- Střední technická složitost
- TTS služby jsou mature
- Podcast audience je velké

**Cost:** 2 měsíce  
**Return:** Multi-format content

---

### Fáze 3 (Video Pipeline): LOWER ROI (ale highest impact)

**Proč:**
- Nejvyšší technická složitost
- Vyžaduje Stable Diffusion nebo API
- Render time je dlouhý
- Ale video má největší reach

**Cost:** 2-3 měsíce  
**Return:** Premium video content

---

### Fáze 4 (Publishing & Analytics): HIGH ROI

**Proč:**
- Kritické pro distribution
- Měření úspěchu
- Feedback loop pro zlepšování
- Nízká technická složitost

**Cost:** 1 měsíc  
**Return:** Data-driven improvement

---

## ✅ Action Items

### Immediate (tento týden):

- [ ] Vytvořit Stage 04 Python moduly
- [ ] Vytvořit templates pro budoucí stages
- [ ] Setup shared utilities
- [ ] Dokumentovat architecture patterns

### Short-term (tento měsíc):

- [ ] Dokončit Stage 04
- [ ] Implementovat Stages 05-07 (review loop)
- [ ] Propojit existující komponenty (18-20)
- [ ] Setup testing framework

### Medium-term (3 měsíce):

- [ ] Dokončit Stages 08-17
- [ ] Dokončit Text Pipeline (01-20)
- [ ] Začít Audio Pipeline planning
- [ ] End-to-end testing Text Pipeline

### Long-term (9 měsíců):

- [ ] Dokončit Audio Pipeline (21-25)
- [ ] Dokončit Video Pipeline (26-28)
- [ ] Dokončit Publishing & Analytics (29-30)
- [ ] Kompletní platform testing
- [ ] Production deployment

---

## 🎓 Závěr

### Klíčová doporučení:

1. ✅ **Začít se Stage 04** - Kritická pro pokračování
2. ✅ **Fokus na Text Pipeline** - Nejvyšší ROI
3. ✅ **Standardizovat patterns** - Zrychlí budoucí vývoj
4. ✅ **Využít existující kód** - Propojit Publishing komponenty
5. ✅ **Iterativní přístup** - Fáze po fázi, ne vše najednou

### Success Metrics:

- **3 měsíce:** Text Pipeline kompletní (stages 01-20) ✅
- **5 měsíců:** + Audio Pipeline (stages 21-25) ✅
- **8 měsíců:** + Video Pipeline (stages 26-28) ✅
- **9 měsíců:** Kompletní platform (stages 01-30) ✅

### Největší rizika:

1. ⚠️ **Scope creep** - Držet se plánu, nerozšiřovat features
2. ⚠️ **AI model changes** - Ollama updates mohou zlomit kód
3. ⚠️ **Video complexity** - Stable Diffusion integrace je náročná
4. ⚠️ **Platform API changes** - Publishing platforms mění API

---

**Next step:** Začít implementací Stage 04 - Script Generation

---

*Tento dokument byl vytvořen analýzou současného stavu a best practices.*  
*Pro technické detaily viz [FUNKCIONALITA_AKTUALNI.md](FUNKCIONALITA_AKTUALNI.md)*
