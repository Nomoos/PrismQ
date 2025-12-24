# Report přechodů stavů - PrismQ Moduly

**Komplexní dokumentace stavových přechodů pro všechny moduly platformy PrismQ**

> **Verze**: 1.0  
> **Vytvořeno**: 2025-12-04  
> **Jazyk**: Čeština

---

## Obsah

1. [Přehled architektury](#přehled-architektury)
2. [T Modul - Generování textu](#t-modul---generování-textu)
3. [A Modul - Generování audia](#a-modul---generování-audia)
4. [V Modul - Generování videa](#v-modul---generování-videa)
5. [P Modul - Publikování](#p-modul---publikování)
6. [M Modul - Metriky a analytika](#m-modul---metriky-a-analytika)
7. [Shrnutí přechodů](#shrnutí-přechodů)

---

## Přehled architektury

PrismQ implementuje sekvenční workflow pro tvorbu obsahu s postupným obohacováním formátů:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PrismQ Stavový automat                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   T (Text)  ──►  A (Audio)  ──►  V (Video)  ──►  P (Publikování)  ──►  M   │
│                                                                    (Metriky)│
│                                        │                                     │
│                                        ▼                                     │
│                              T.IdeaInspiration                               │
│                              (zpětná vazba)                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Základní principy přechodů

| Princip | Popis |
|---------|-------|
| **Sekvenční pipeline** | T → A → V → P → M (lineární tok mezi hlavními moduly) |
| **Kvalitní kontrolní body** | Explicitní kritéria přijetí při každém přechodu |
| **Iterativní vylepšování** | Smyčky a zpětnovazební cykly v rámci každého modulu |
| **Postupná publikace** | Možnost uvolnění obsahu v jakékoli fázi |
| **Zpětná vazba** | M modul poskytuje metriky zpět do T.IdeaInspiration |

---

## T Modul - Generování textu

**Jmenný prostor**: `PrismQ.T`

### Přehled stavů

T modul obsahuje **18 hlavních stavů** organizovaných do iterativního workflow s cykly společného vylepšování.

### Diagram přechodů stavů

```mermaid
stateDiagram-v2
    [*] --> IdeaCreation
    
    IdeaCreation --> StoryFromIdea
    StoryFromIdea --> TitleFromIdea
    TitleFromIdea --> ContentFromTitleIdea
    ContentFromTitleIdea --> ReviewTitleByContentIdea
    
    ReviewTitleByContentIdea --> ReviewContentByTitleIdea
    ReviewContentByTitleIdea --> ReviewTitleByContent
    
    ReviewTitleByContent --> TitleFromContentReviewTitle
    ReviewTitleByContent --> ReviewContentByTitle
    
    TitleFromContentReviewTitle --> ContentFromTitleReviewContent
    ContentFromTitleReviewContent --> ReviewTitleByContent
    
    ReviewContentByTitle --> ContentFromTitleReviewContent
    ReviewContentByTitle --> ReviewContentGrammar
    
    ReviewContentGrammar --> ReviewContentTone
    ReviewContentGrammar --> ContentFromTitleReviewContent
    
    ReviewContentTone --> ReviewContentContent
    ReviewContentTone --> ContentFromTitleReviewContent
    
    ReviewContentContent --> ReviewContentConsistency
    ReviewContentContent --> ContentFromTitleReviewContent
    
    ReviewContentConsistency --> ReviewContentEditing
    ReviewContentConsistency --> ContentFromTitleReviewContent
    
    ReviewContentEditing --> ReviewTitleReadability
    ReviewContentEditing --> ContentFromTitleReviewContent
    
    ReviewTitleReadability --> ReviewContentReadability
    ReviewTitleReadability --> TitleFromContentReviewTitle
    
    ReviewContentReadability --> StoryReview
    ReviewContentReadability --> ContentFromTitleReviewContent
    
    StoryReview --> StoryPolish
    StoryReview --> Publishing
    
    StoryPolish --> StoryReview
    
    Publishing --> [*]
```

### Tabulka stavů a přechodů

#### Fáze 1: Vytvoření nápadu

| Stav | Název | Fáze | Umístění | Přechod na |
|------|-------|------|----------|------------|
| IdeaCreation | PrismQ.T.Idea.Creation | 1 | T/Idea/Creation/ | StoryFromIdea |
| StoryFromIdea | PrismQ.T.Story.From.Idea | 1.5 | T/Story/From/Idea/ | TitleFromIdea |
| TitleFromIdea | PrismQ.T.Title.From.Idea | 2 | T/Title/From/Idea/ | ContentFromTitleIdea |
| ContentFromTitleIdea | PrismQ.T.Content.From.Title.Idea | 3 | T/Content/From/Idea/Title/ | ReviewTitleByContentIdea |

**Popis přechodů:**
- `IdeaCreation → StoryFromIdea`: Vytvoření 10 příběhů z jednoho nápadu
- `StoryFromIdea → TitleFromIdea`: Generování titulku v1 z nápadu
- `TitleFromIdea → ContentFromTitleIdea`: Generování obsahu v1 z titulku a nápadu
- `ContentFromTitleIdea → ReviewTitleByContentIdea`: Zahájení revizního cyklu

#### Fáze 2: Revize titulku a obsahu

| Stav | Název | Fáze | Přechod na (schváleno) | Přechod na (zamítnuto) |
|------|-------|------|------------------------|------------------------|
| ReviewTitleByContentIdea | PrismQ.T.Review.Title.From.Content.Idea | 4 | ReviewContentByTitleIdea | - |
| ReviewContentByTitleIdea | PrismQ.T.Review.Content.From.Title.Idea | 5 | ReviewTitleByContent | - |
| ReviewTitleByContent | PrismQ.T.Review.Title.From.Content | 6 | ReviewContentByTitle | TitleFromContentReviewTitle |
| TitleFromContentReviewTitle | PrismQ.T.Title.From.Content.Review.Title | 7 | ContentFromTitleReviewContent | - |
| ContentFromTitleReviewContent | PrismQ.T.Content.From.Title.Review.Content | 8 | ReviewTitleByContent | - |
| ReviewContentByTitle | PrismQ.T.Review.Content.From.Title | 9 | ReviewContentGrammar | ContentFromTitleReviewContent |

**Iterativní smyčka:**
```
ReviewTitleByContent
    ├─ schváleno → ReviewContentByTitle
    └─ zamítnuto → TitleFromContentReviewTitle → ContentFromTitleReviewContent → ReviewTitleByContent
```

#### Fáze 3: Kvalitní revize (lokální AI)

| Stav | Název | Fáze | Přechod na (projde) | Přechod na (selže) |
|------|-------|------|--------------------|--------------------|
| ReviewContentGrammar | PrismQ.T.Review.Content.Grammar | 10 | ReviewContentTone | ContentFromTitleReviewContent |
| ReviewContentTone | PrismQ.T.Review.Content.Tone | 11 | ReviewContentContent | ContentFromTitleReviewContent |
| ReviewContentContent | PrismQ.T.Review.Content.Content | 12 | ReviewContentConsistency | ContentFromTitleReviewContent |
| ReviewContentConsistency | PrismQ.T.Review.Content.Consistency | 13 | ReviewContentEditing | ContentFromTitleReviewContent |
| ReviewContentEditing | PrismQ.T.Review.Content.Editing | 14 | ReviewTitleReadability | ContentFromTitleReviewContent |
| ReviewTitleReadability | PrismQ.T.Review.Title.Readability | 15 | ReviewContentReadability | TitleFromContentReviewTitle |
| ReviewContentReadability | PrismQ.T.Review.Content.Readability | 16 | StoryReview | ContentFromTitleReviewContent |

**Sekvenční kvalitní kontroly:**
```
ReviewContentGrammar
    ├─ projde → ReviewContentTone
    │               ├─ projde → ReviewContentContent
    │               │               ├─ projde → ReviewContentConsistency
    │               │               │               └─ ... → ReviewContentEditing → ReviewTitleReadability → ReviewContentReadability
    │               │               └─ selže → ContentFromTitleReviewContent
    │               └─ selže → ContentFromTitleReviewContent
    └─ selže → ContentFromTitleReviewContent
```

#### Fáze 4: Expertní revize (GPT)

| Stav | Název | Fáze | Přechod na (schváleno) | Přechod na (zamítnuto) |
|------|-------|------|------------------------|------------------------|
| StoryReview | PrismQ.T.Story.Review | 17 | Publishing | StoryPolish |
| StoryPolish | PrismQ.T.Story.Polish | 18 | StoryReview | - |

**Expertní smyčka:**
```
StoryReview
    ├─ schváleno → Publishing → [*]
    └─ zamítnuto → StoryPolish → StoryReview (iterace dokud není schváleno)
```

### Kvalitní kontrolní body (T modul)

| Kontrolní bod | Fáze | Popis |
|---------------|------|-------|
| Soulad titulek-obsah (počáteční) | 4-6 | Zajištění počátečního souladu titulku a obsahu s nápadem |
| Soulad titulek-obsah (upřesněný) | 8-10 | Zajištění upřesněného souladu titulku a obsahu |
| Lokální AI kvalitní revize | 10-16 | Sedmidimenzionální hodnocení kvality |
| Expertní revize | 17-18 | GPT-based holistická revize |

### Výstup T modulu

| Výstup | Popis |
|--------|-------|
| PublishedText | SEO-optimalizovaný publikovaný text |
| → PrismQ.A.Voiceover | Vstup pro audio pipeline |

---

## A Modul - Generování audia

**Jmenný prostor**: `PrismQ.A`

### Přehled stavů

A modul transformuje publikovaný text na profesionální audio obsah s následujícími hlavními stavy:

### Diagram přechodů stavů

```mermaid
stateDiagram-v2
    [*] --> PublishedText
    
    PublishedText --> Voiceover
    PublishedText --> Archived
    
    Voiceover --> VoiceoverReview
    Voiceover --> PublishedText
    Voiceover --> Archived
    
    VoiceoverReview --> VoiceoverApproved
    VoiceoverReview --> Voiceover
    VoiceoverReview --> PublishedText
    VoiceoverReview --> Archived
    
    VoiceoverApproved --> Normalization
    VoiceoverApproved --> VoiceoverReview
    VoiceoverApproved --> Archived
    
    Normalization --> Enhancement
    Normalization --> VoiceoverApproved
    
    Enhancement --> AudioPublishing
    Enhancement --> Normalization
    
    AudioPublishing --> PublishedAudio
    AudioPublishing --> VoiceoverApproved
    AudioPublishing --> Archived
    
    PublishedAudio --> AnalyticsReviewAudio
    PublishedAudio --> ScenePlanning
    PublishedAudio --> Archived
    
    AnalyticsReviewAudio --> Archived
    AnalyticsReviewAudio --> IdeaInspiration
```

### Tabulka stavů a přechodů

| Stav | Název | Vstup | Přechod na | Popis |
|------|-------|-------|------------|-------|
| PublishedText | PrismQ.T.PublishedText | T modul | Voiceover, Archived | Vstupní stav z T modulu |
| Voiceover | PrismQ.A.Voiceover | PublishedText | VoiceoverReview, PublishedText, Archived | Nahrávání hlasu z publikovaného textu |
| VoiceoverReview | PrismQ.A.Voiceover.Review | Voiceover | VoiceoverApproved, Voiceover, PublishedText, Archived | Kontrola kvality nahrávky |
| VoiceoverApproved | PrismQ.A.Voiceover.Approved | VoiceoverReview | Normalization, VoiceoverReview, Archived | Schválená nahrávka |
| Normalization | PrismQ.A.Normalized | VoiceoverApproved | Enhancement, VoiceoverApproved | Normalizace hlasitosti (LUFS) |
| Enhancement | PrismQ.A.Enhancement | Normalization | AudioPublishing, Normalization | EQ, komprese, finální úpravy |
| AudioPublishing | PrismQ.A.Publishing | Enhancement | PublishedAudio, VoiceoverApproved, Archived | Publikace na audio platformy |
| PublishedAudio | PrismQ.A.PublishedAudio | AudioPublishing | ScenePlanning, AnalyticsReviewAudio, Archived | Publikované audio |
| AnalyticsReviewAudio | PrismQ.A.Analytics.Review | PublishedAudio | IdeaInspiration, Archived | Analýza výkonu audia |

### Přechody revizí (A modul)

**Zpětné přechody:**
```
VoiceoverReview → Voiceover: Potřeba přenahrání
VoiceoverReview → PublishedText: Problém se zdrojovým textem
Voiceover → PublishedText: Chyby objevené během nahrávání
AudioPublishing → VoiceoverApproved: Problémy s audio souborem
```

### Kvalitní kontrolní body (A modul)

| Kontrolní bod | Stav | Kritéria |
|---------------|------|----------|
| Kvalita nahrávky | VoiceoverReview | Čistota zvuku, správná výslovnost, tempo |
| Technické standardy | Normalization | -16 LUFS (Spotify/Apple Podcasts) |
| Finální kvalita | AudioPublishing | Formát MP3 (320kbps), metadata |

### Výstup A modulu

| Výstup | Popis |
|--------|-------|
| PublishedAudio | Profesionální podcast/audio obsah |
| → PrismQ.V.ScenePlanning | Vstup pro video pipeline |
| → PrismQ.M.Analytics | Metriky výkonu |

---

## V Modul - Generování videa

**Jmenný prostor**: `PrismQ.V`

### Přehled stavů

V modul kombinuje publikované audio se synchronizovanými vizuály pro video platformy.

### Diagram přechodů stavů

```mermaid
stateDiagram-v2
    [*] --> PublishedAudio
    
    PublishedAudio --> ScenePlanning
    PublishedAudio --> Archived
    
    ScenePlanning --> KeyframePlanning
    ScenePlanning --> PublishedAudio
    ScenePlanning --> Archived
    
    KeyframePlanning --> KeyframeGeneration
    KeyframePlanning --> ScenePlanning
    KeyframePlanning --> Archived
    
    KeyframeGeneration --> VideoAssembly
    KeyframeGeneration --> KeyframePlanning
    KeyframeGeneration --> Archived
    
    VideoAssembly --> VideoReview
    VideoAssembly --> KeyframeGeneration
    VideoAssembly --> Archived
    
    VideoReview --> VideoFinalized
    VideoReview --> VideoAssembly
    VideoReview --> KeyframeGeneration
    VideoReview --> Archived
    
    VideoFinalized --> PublishPlanning
    VideoFinalized --> VideoReview
    VideoFinalized --> Archived
    
    PublishPlanning --> PublishedVideo
    PublishPlanning --> VideoFinalized
    PublishPlanning --> Archived
    
    PublishedVideo --> AnalyticsReviewVideo
    PublishedVideo --> Archived
    
    AnalyticsReviewVideo --> Archived
    AnalyticsReviewVideo --> IdeaInspiration
```

### Tabulka stavů a přechodů

| Stav | Název | Fáze | Přechod vpřed | Přechod zpět |
|------|-------|------|---------------|--------------|
| PublishedAudio | PrismQ.A.PublishedAudio | Vstup | ScenePlanning | Archived |
| ScenePlanning | PrismQ.V.Scene.Planning | Vizuální plánování | KeyframePlanning | PublishedAudio |
| KeyframePlanning | PrismQ.V.Keyframe.Planning | Specifikace klíčových snímků | KeyframeGeneration | ScenePlanning |
| KeyframeGeneration | PrismQ.V.Keyframe.Generation | Generování vizuálů | VideoAssembly | KeyframePlanning |
| VideoAssembly | PrismQ.V.Video.Assembly | Sestavení videa | VideoReview | KeyframeGeneration |
| VideoReview | PrismQ.V.Video.Review | Revize kvality | VideoFinalized | VideoAssembly, KeyframeGeneration |
| VideoFinalized | PrismQ.V.Video.Finalized | Finalizace | PublishPlanning | VideoReview |
| PublishPlanning | PrismQ.V.Publish.Planning | Plánování publikace | PublishedVideo | VideoFinalized |
| PublishedVideo | PrismQ.V.PublishedVideo | Výstup | AnalyticsReviewVideo | Archived |
| AnalyticsReviewVideo | PrismQ.V.Analytics.Review | Analýza | IdeaInspiration | Archived |

### Sekvenční přechody (V modul)

**Lineární postup:**
```
PublishedAudio
    → ScenePlanning (plánování scén na základě audia)
    → KeyframePlanning (identifikace klíčových vizuálních momentů)
    → KeyframeGeneration (generování vizuálních assetů)
    → VideoAssembly (sestavení timeline)
    → VideoReview (kontrola kvality)
    → VideoFinalized (schválení)
    → PublishPlanning (strategie publikace)
    → PublishedVideo (výstup)
```

**Zpětné přechody:**
```
VideoReview → VideoAssembly: Problémy se sestavením
VideoReview → KeyframeGeneration: Problémy s vizuálními assety
KeyframePlanning → ScenePlanning: Revize struktury scén
ScenePlanning → PublishedAudio: Problémy s časováním audia
```

### Platformové specifikace (V modul)

| Platforma | Formát | Rozlišení | Speciální požadavky |
|-----------|--------|-----------|---------------------|
| YouTube | 16:9 | 1920x1080 | Miniatury, kapitoly, SEO |
| TikTok | 9:16 | 1080x1920 | Háček v prvních 3 sekundách |
| Instagram Reels | 9:16 | 1080x1920 | Titulky, krátký formát |
| YouTube Shorts | 9:16 | 1080x1920 | Max 60 sekund |

### Výstup V modulu

| Výstup | Popis |
|--------|-------|
| PublishedVideo | Kompletní video s audiem + vizuály |
| → PrismQ.P.Publishing | Vstup pro bulk publikaci |
| → PrismQ.M.Analytics | Metriky výkonu |

---

## P Modul - Publikování

**Jmenný prostor**: `PrismQ.P`

### Přehled stavů

P modul koordinuje hromadnou distribuci napříč více platformami po dokončení obsahu.

### Diagram přechodů stavů

```mermaid
stateDiagram-v2
    [*] --> ContentReady
    
    state ContentReady {
        PublishedText --> Publishing
        PublishedAudio --> Publishing
        PublishedVideo --> Publishing
    }
    
    Publishing --> Planning
    
    Planning --> Scheduling
    Planning --> ContentReady
    
    Scheduling --> Distribution
    Scheduling --> Planning
    
    Distribution --> Published
    Distribution --> Scheduling
    
    Published --> Archived
    Published --> Analytics
    
    Analytics --> IdeaInspiration
    Analytics --> Archived
```

### Tabulka stavů a přechodů

| Stav | Název | Vstup | Přechod na | Popis |
|------|-------|-------|------------|-------|
| ContentReady | PrismQ.P.Content.Ready | T/A/V | Publishing | Připravený obsah (text/audio/video) |
| Publishing | PrismQ.P.Publishing | ContentReady | Planning | Zahájení publikačního procesu |
| Planning | PrismQ.P.Publishing.Planning | Publishing | Scheduling, ContentReady | Plánování strategie publikace |
| Scheduling | PrismQ.P.Publishing.Scheduling | Planning | Distribution, Planning | Nastavení časování a pořadí |
| Distribution | PrismQ.P.Publishing.Distribution | Scheduling | Published, Scheduling | Provedení publikace |
| Published | PrismQ.P.Published | Distribution | Analytics, Archived | Publikovaný obsah napříč platformami |
| Analytics | PrismQ.P.Analytics | Published | IdeaInspiration, Archived | Sledování výkonu |

### Vstupní zdroje (P modul)

```
PrismQ.T.PublishedText ─┐
PrismQ.A.PublishedAudio ─┼→ PrismQ.P.Publishing → Multi-Platform Distribution
PrismQ.V.PublishedVideo ─┘
```

### Publikační strategie

| Typ obsahu | Časový rámec | Platformy |
|------------|--------------|-----------|
| Pouze text | Hodiny až dny | Medium, Substack, Blog, LinkedIn, Twitter/X |
| Text + Audio | Dny až týden | + Spotify, Apple Podcasts, SoundCloud |
| Kompletní multi-formát | Týdny | + YouTube, TikTok, Instagram Reels |

### Příklad multi-formátové kampaně

```
Den 1: Text (blog, sociální snippety)
    ↓
Den 3: Audio (podcastová epizoda)
    ↓
Den 7: Video (YouTube, krátké klipy)
    ↓
Průběžně: Křížová propagace napříč platformami
```

---

## M Modul - Metriky a analytika

**Jmenný prostor**: `PrismQ.M`

### Přehled architektury

M modul je **průřezový meta-modul**, který monitoruje výkon publikovaného obsahu napříč všemi formáty.

### Diagram přechodů stavů

```mermaid
stateDiagram-v2
    [*] --> DataCollection
    
    state DataCollection {
        TextMetrics: T.PublishedText metriky
        AudioMetrics: A.PublishedAudio metriky
        VideoMetrics: V.PublishedVideo metriky
        PlatformMetrics: P.Published metriky
    }
    
    DataCollection --> Analytics
    
    Analytics --> ABTesting
    Analytics --> Insights
    
    ABTesting --> Insights
    
    Insights --> Recommendations
    Insights --> Reporting
    
    Recommendations --> IdeaInspiration
    
    Reporting --> Archived
```

### Tabulka stavů a přechodů

| Stav | Název | Vstup | Přechod na | Popis |
|------|-------|-------|------------|-------|
| DataCollection | PrismQ.M.Data.Collection | T/A/V/P | Analytics | Sběr metrik z publikovaného obsahu |
| Analytics | PrismQ.M.Analytics | DataCollection | ABTesting, Insights | Analýza výkonu |
| ABTesting | PrismQ.M.ABTesting | Analytics | Insights | Testování variant |
| Insights | PrismQ.M.Insights | Analytics, ABTesting | Recommendations, Reporting | Generování poznatků |
| Recommendations | PrismQ.M.Recommendations | Insights | IdeaInspiration | Doporučení pro obsah |
| Reporting | PrismQ.M.Reporting | Insights | Archived | Reporty výkonu |

### Zdroje dat (M modul)

```
┌─ T.PublishedText metriky ────┐
├─ A.PublishedAudio metriky ───┤
├─ V.PublishedVideo metriky ───┼→ M.Analytics → M.Insights → T.IdeaInspiration
└─ P.Published platform metriky┘
```

### Kategorie metrik

#### Textové metriky
| Kategorie | Metriky |
|-----------|---------|
| Zapojení | Zobrazení, čtení, doba čtení, hloubka scrollování |
| Interakce | Lajky, komentáře, sdílení, tlesky |
| SEO | Pozice ve vyhledávání, organický traffic, zpětné odkazy |
| Konverze | E-mailové přihlášky, proklikovost |

#### Audio metriky
| Kategorie | Metriky |
|-----------|---------|
| Zapojení | Přehrání, stažení, míra dokončení |
| Růst | Odběratelé, sledující, hodnocení epizody |
| Retence | Průměrná doba poslechu, body odpojení |
| Platforma | Spotify streamy, Apple Podcasts stažení |

#### Video metriky
| Kategorie | Metriky |
|-----------|---------|
| Výkon | Zobrazení, doba sledování, průměrná doba zobrazení |
| Zapojení | Lajky, komentáře, sdílení, uložení |
| Objevování | CTR, imprese, traffic z vyhledávání |
| Retence | Křivka retence publika, míra opakovaného sledování |

### Zpětnovazební smyčka

```
Poznatky z metrik informují budoucí obsah:

1. Vysoce výkonná témata → Více obsahu v dané oblasti
2. Preference publika → Úpravy formátu a stylu
3. Výkon platformy → Rozhodování o alokaci zdrojů
4. Vzorce zapojení → Optimalizace času publikace
5. Mezery v obsahu → Průzkum nových témat
```

---

## Shrnutí přechodů

### Celkový tok pipeline

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           PrismQ Kompletní workflow                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  IdeaInspiration                                                                 │
│       │                                                                          │
│       ▼                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ T MODUL: 18 stavů                                                       │    │
│  │ IdeaCreation → StoryFromIdea → TitleFromIdea → ContentFromTitleIdea      │    │
│  │     → ReviewTitleByContentIdea → ReviewContentByTitleIdea                 │    │
│  │     → ReviewTitleByContent ↔ TitleFromContentReviewTitle                  │    │
│  │     → ContentFromTitleReviewContent ↔ ReviewContentByTitle                 │    │
│  │     → ReviewContentGrammar → ReviewContentTone → ReviewContentContent      │    │
│  │     → ReviewContentConsistency → ReviewContentEditing                     │    │
│  │     → ReviewTitleReadability → ReviewContentReadability                  │    │
│  │     → StoryReview ↔ StoryPolish → Publishing                            │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│       │ PublishedText                                                            │
│       ▼                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ A MODUL: 8 hlavních stavů                                               │    │
│  │ Voiceover → VoiceoverReview → VoiceoverApproved                         │    │
│  │     → Normalization → Enhancement → AudioPublishing → PublishedAudio    │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│       │ PublishedAudio                                                           │
│       ▼                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ V MODUL: 9 hlavních stavů                                               │    │
│  │ ScenePlanning → KeyframePlanning → KeyframeGeneration                   │    │
│  │     → VideoAssembly → VideoReview → VideoFinalized                      │    │
│  │     → PublishPlanning → PublishedVideo                                  │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│       │ PublishedVideo                                                           │
│       ▼                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ P MODUL: 5 hlavních stavů                                               │    │
│  │ Publishing → Planning → Scheduling → Distribution → Published           │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│       │ Published (multi-platform)                                               │
│       ▼                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ M MODUL: 6 hlavních stavů (průřezový)                                   │    │
│  │ DataCollection → Analytics → ABTesting → Insights → Recommendations     │    │
│  │     → Reporting                                                          │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│       │ Recommendations                                                          │
│       ▼                                                                          │
│  IdeaInspiration (zpětná vazba)                                                  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Statistika přechodů

| Modul | Počet stavů | Lineární přechody | Zpětné přechody | Smyčky |
|-------|-------------|-------------------|-----------------|--------|
| T | 18 | 16 | 11 | 3 |
| A | 8 | 7 | 4 | 1 |
| V | 9 | 8 | 5 | 2 |
| P | 5 | 4 | 2 | 0 |
| M | 6 | 5 | 1 | 0 |
| **Celkem** | **46** | **40** | **23** | **6** |

### Typy přechodů

| Typ přechodu | Popis | Příklad |
|--------------|-------|---------|
| **Lineární** | Postup vpřed při splnění podmínek | ContentDraft → ContentReview |
| **Zpětný** | Návrat na předchozí stav pro revizi | ContentReview → ContentDraft |
| **Smyčka** | Iterativní cyklus do schválení | StoryReview ↔ StoryPolish |
| **Archivace** | Předčasné ukončení | [Jakýkoli stav] → Archived |
| **Zpětná vazba** | Informace pro budoucí obsah | Analytics → IdeaInspiration |

### Kvalitní kontrolní body (všechny moduly)

| Modul | Kontrolní bod | Účel |
|-------|---------------|------|
| T | Soulad titulek-obsah | Zajištění konzistence |
| T | Lokální AI revize (7x) | Automatizovaná kvalita |
| T | Expertní GPT revize | Profesionální standard |
| A | Revize nahrávky | Kvalita hlasu |
| A | Normalizace LUFS | Technické standardy |
| V | Revize videa | Kvalita sestavení |
| V | Finalizace | Schválení před publikací |
| P | Distribuce | Úspěšná publikace |
| M | Insights | Validace poznatků |

---

## Závěr

Tento report dokumentuje přechody stavů pro všechny moduly platformy PrismQ:

1. **T Modul** implementuje nejsložitější workflow s 18 stavy a 3 iterativními smyčkami
2. **A Modul** zpracovává audio s důrazem na kvalitu a normalizaci
3. **V Modul** kombinuje audio s vizuály pro více platforem
4. **P Modul** koordinuje hromadnou distribuci
5. **M Modul** poskytuje průřezovou analytiku a zpětnou vazbu

Celkový systém obsahuje **46 stavů** s **40 lineárními přechody**, **23 zpětnými přechody** a **6 iterativními smyčkami**, což umožňuje robustní a flexibilní tvorbu obsahu s důrazem na kvalitu.

---

**Verze**: 1.0  
**Vytvořeno**: 2025-12-04  
**Součást**: PrismQ Content Production Platform

---

**Navigace**: [← Hlavní README](../../README.md) | [← Workflow](../WORKFLOW_CS.md) | [T Modul →](../../T/README.md) | [A Modul →](../../A/README.md) | [V Modul →](../../V/README.md)
