# PrismQ - Platforma pro tvorbu obsahu

**Postupná tvorba obsahu ve více formátech: Text → Audio → Video**

PrismQ je komplexní platforma pro tvorbu obsahu, která transformuje nápady do víceformátového obsahu prostřednictvím sekvenčního obohacovacího workflow. Každý formát staví na předchozím a umožňuje postupnou publikaci napříč textovými, audio a video platformami.

## 🔄 Další kroky a paralelní spouštění

Pro aktuální úkoly sprintu a příkazy pro paralelní spouštění viz:
- **[PARALLEL_RUN_NEXT.md](./_meta/issues/PARALLEL_RUN_NEXT.md)** - Aktuální úkoly MVP sprintu a plán paralelního spouštění
- **[PARALLEL_RUN_NEXT_FULL.md](./_meta/issues/PARALLEL_RUN_NEXT_FULL.md)** - Kompletní rozpad problémů a přiřazení workerů

## 📚 Hlavní moduly

### [T - Pipeline pro generování textu](./T/README.md)
**Jmenný prostor**: `PrismQ.T`

Základ pipeline pro obsah. Transformuje nápady do vysoce kvalitního textového obsahu optimalizovaného pro blogy, články a sociální média.

- Vývoj nápadů a vytváření osnov
- Tvorba a revize skriptů
- Publikace a optimalizace textu
- SEO a správa metadat

**[→ Prozkoumat T modul](./T/README.md)**

---

### [A - Pipeline pro generování audia](./A/README.md)
**Jmenný prostor**: `PrismQ.A`

Druhá fáze postupného obohacování. Transformuje publikovaný text na profesionální audio obsah pro podcastové platformy.

- Nahrávání a revize hlasového komentáře
- Zpracování a normalizace audia
- Publikace a distribuce podcastů
- Optimalizace specifická pro jednotlivé platformy

**[→ Prozkoumat A modul](./A/README.md)**

---

### [V - Pipeline pro generování videa](./V/README.md)
**Jmenný prostor**: `PrismQ.V`

Závěrečná fáze workflow. Kombinuje publikované audio se synchronizovanými vizuály pro video platformy.

- Plánování scén a návrh klíčových snímků
- Generování vizuálních assetů
- Skládání a editace videa
- Publikace videa na více platformách (YouTube, TikTok, Instagram)

**[→ Prozkoumat V modul](./V/README.md)**

---

### [Client - Webové rozhraní pro správu](./Client/README.md)
**Jmenný prostor**: `PrismQ.Client`

Webový systém pro správu fronty úkolů sloužící ke koordinaci workflow tvorby obsahu.

- Správa fronty úkolů (Backend/Frontend)
- Koordinace workerů
- Sledování pokroku a monitoring
- Připraveno pro produkční nasazení

**[→ Prozkoumat Client modul](./Client/README.md)**

---

## 🎯 Sekvenční workflow

```
IdeaInspiration (Inspirace nápadu)
    ↓
Text Pipeline (T) → PublishedText (Publikovaný text)
    ↓
Audio Pipeline (A) → PublishedAudio (Publikované audio)
    ↓
Video Pipeline (V) → PublishedVideo (Publikované video)
    ↓
Analytics → IdeaInspiration (zpětná vazba)
```

Každý formát může být publikován nezávisle:
- **Pouze text**: Nejrychlejší publikace (hodiny až dny)
- **Text + Audio**: Střední časový horizont (dny až týden)
- **Kompletní víceformátový obsah**: Plná produkce (týdny)

## 📖 Dokumentace a zdroje

### Výzkum a strategie
Základní výzkumné a strategické plánovací dokumenty.

- **[Výzkumné dokumenty](./_meta/research/)** - Výzkum tvorby obsahu
  - [Stavy workflow tvorby obsahu](./_meta/research/content-production-workflow-states.md)
  - [Optimalizace metadat YouTube](./_meta/research/youtube-metadata-optimization-smart-strategy.md)
  - [Výzkum populárních mediálních platforem](./_meta/research/popular-media-platforms-research.md)
  - [Obsahové platformy podle kategorie a věku](./_meta/research/content-platforms-by-category-and-age.md)
  - [Strategie pro teenagerské publikum](./_meta/research/teen-audience-platform-strategy.md)
- **[Výzkum audia](./A/Narrator/_meta/research/)** - Výzkum vypravěče a hlasového komentáře
  - [Výchozí profil hlasu vypravěče](./A/Narrator/_meta/research/default-narrator-voice-profile.md) - Šablona vypravěče v první osobě (teenagerská dívka)
- **[Návrhy](./_meta/proposals/)** - Architektonické a designové návrhy
  - [Reorganizace modulů](./_meta/proposals/module-reorganization.md)
- **[Dokumentace](./_meta/docs/)** - Celoplošná projektová dokumentace
  - [Nastavení AI modelů](./_meta/docs/AI_MODELS_SETUP.md) - Průvodce nastavením Ollama a Qwen2.5
  - [Databázové objekty](./_meta/docs/DATABASE.md) - Schéma databáze a reference modelů
  - [Průvodce storytellingem](./_meta/docs/STORYTELLING_GUIDE.md)

### Dokumentace workflow
- **[WORKFLOW.md](./_meta/WORKFLOW.md)** - Kompletní dokumentace stavového automatu
  - Fáze workflow a přechody stavů
  - Model postupného obohacování
  - Kvalitní kontrolní body a osvědčené postupy
  - **[Ultra-Clean Pipeline](./_meta/docs/workflow/ultra-clean-pipeline.md)** - Zjednodušená reprezentace běhu

## 🏗️ Struktura projektu

```
PrismQ/
├── T/                  # Pipeline pro generování textu
│   ├── Idea/          # Vývoj nápadů
│   ├── Script/        # Tvorba a revize skriptů
│   ├── Title/         # Optimalizace titulků
│   ├── Publishing/    # Publikace textu
│   ├── Review/        # Revize a editace
│   └── _meta/         # Metadata modulu
├── A/                  # Pipeline pro generování audia
│   ├── Voiceover/     # Nahrávání hlasu
│   ├── Narrator/      # Výběr vypravěče
│   ├── Normalized/    # Normalizace audia
│   ├── Enhancement/   # Vylepšení audia
│   ├── Publishing/    # Publikace audia
│   └── _meta/         # Metadata modulu
├── V/                  # Pipeline pro generování videa
│   ├── Scene/         # Plánování scén
│   ├── Keyframe/      # Generování klíčových snímků
│   ├── Video/         # Skládání videa
│   └── _meta/         # Metadata modulu
├── P/                  # Modul publikování
│   └── _meta/         # Metadata modulu
├── M/                  # Modul metrik/analytiky
│   └── _meta/         # Metadata modulu
├── Client/            # Webové rozhraní pro správu
│   ├── Backend/       # Backend API (TaskManager)
│   ├── Frontend/      # Frontend UI (TaskManager)
│   └── _meta/         # Metadata modulu
├── src/           # Správa prostředí a konfigurace
│   ├── config.py      # Centralizovaná konfigurace
│   ├── tests/         # Testovací sada
│   └── README.md      # Dokumentace konfigurace src
└── _meta/             # Celoplošná metadata projektu
    ├── docs/         # Dokumentace
    ├── research/     # Výzkumné dokumenty
    ├── proposals/    # Designové návrhy
    └── WORKFLOW.md   # Dokumentace stavového automatu
```

## 📁 Struktura pracovního adresáře

PrismQ používá standardizovaný pracovní adresář pro všechna runtime data a výstupy:

- **Windows**: `C:\PrismQ` (permanentní umístění MVP)
- **Unix-like**: `~/PrismQ` (domovský adresář uživatele)

Pracovní adresář obsahuje:

```
C:\PrismQ/              # Pracovní adresář (Windows) nebo ~/PrismQ (Unix)
├── .env                # Konfigurace (spravováno src modulem)
├── db.s3db             # Databáze
├── T/{id}/             # Textový obsah podle ID
│   ├── {Platform}/    # Výstup specifický pro platformu
│   └── Text/          # Finální textový obsah
├── A/{id}/             # Audio obsah podle ID
│   ├── {Platform}/    # Výstup specifický pro platformu
│   └── Audio/         # Finální audio soubory
├── V/{id}/             # Video obsah podle ID
│   ├── {Platform}/    # Výstup specifický pro platformu
│   └── Video/         # Finální video soubory
├── P/                  # Záznamy o publikování (podle hierarchie data)
│   └── {Year}/{Month}/{day-range}/{day}/{hour}/{id}/{platform}/
└── M/                  # Data metrik (podle hierarchie data)
    └── {Year}/{Month}/{day-range}/{day}/{hour}/{id}/Metrics/{platform}/
```

Viz [src/README.md](./src/README.md) pro kompletní dokumentaci konfigurace.

## 🤖 Lokální AI model

PrismQ používá **Qwen 3:30B** (`qwen3:32b`) jako výchozí lokální AI model pro generování obsahu a SEO optimalizaci. Tento model běží lokálně přes [Ollama](https://ollama.com/) a poskytuje výborný poměr mezi kvalitou a rychlostí.

### Rychlá instalace

```bash
# 1. Nainstalujte Ollama
# Navštivte: https://ollama.com/

# 2. Stáhněte výchozí model
ollama pull qwen3:32b

# 3. Spusťte server
ollama serve
```

### Proč Qwen 3:30B?
- Silné schopnosti uvažování a sledování instrukcí
- Vhodný pro generování obsahu a SEO úlohy
- Dobrý poměr mezi velikostí modelu a rychlostí inference
- Silná vícejazyčná podpora
- Funguje dobře na běžném hardwaru

Pro detailní možnosti konfigurace AI viz [dokumentace AI metadat](./T/Publishing/SEO/Keywords/_meta/docs/AI_METADATA.md).

## 🚀 Rychlý start

1. **Prozkoumejte pipeline**: Začněte s [T/README.md](./T/README.md) pro pochopení generování textu
2. **Nakonfigurujte prostředí**: Viz [src/README.md](./src/README.md) pro nastavení
3. **Nastavte AI modely**: Viz [Nastavení AI modelů](./_meta/docs/AI_MODELS_SETUP.md) pro konfiguraci Ollama a Qwen2.5
4. **Prohlédněte si workflow**: Přečtěte si [WORKFLOW.md](./_meta/WORKFLOW.md) pro kompletní stavový automat
5. **Prostudujte výzkum**: Procházejte [_meta/research/](./_meta/research/) pro strategické poznatky
6. **Použijte Client**: Podívejte se na [Client/README.md](./Client/README.md) pro nastavení webového rozhraní

## 🔄 Architektura stavového automatu

PrismQ implementuje **komplexní workflow stavového automatu** napříč pěti hlavními moduly:

### Tok pipeline: T → A → V → P → M

```
┌─────────────────────────────────────────────────────────────────┐
│                    Stavový automat PrismQ                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  T (Text)  →  A (Audio)  →  V (Video)  →  P (Publikování) → M (Metriky/Analytika)                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Popis modulů

1. **T (Generování textu)**
   - **Účel**: Transformace nápadů do vysoce kvalitního textového obsahu
   - **Stavový automat**: 16fázový iterativní workflow s cykly společného vylepšování
   - **Klíčové stavy**: Idea.Creation → Title.Draft → Script.Draft → Revize → Vylepšení → Vybrušování → Publikování
   - **Kvalitní kontrolní body**: Schválení titulku, schválení skriptu, validace čitelnosti
   - **Výstup**: SEO-optimalizovaný publikovaný text
   - **struktura uvnitř pracovního adresáře** T/{id}/{Platform}, T/{id}/Text (zde bude hotový text)
   - **[📄 Zobrazit dokumentaci T stavového automatu](./T/STATE_MACHINE.md)** *(Připravuje se)*

2. **A (Generování audia)**
   - **Účel**: Konverze publikovaného textu na profesionální audio obsah
   - **Stavový automat**: Generování hlasu, vylepšení a publikace podcastu *(K implementaci)*
   - **Vstup**: Publikovaný text z modulu T
   - **Výstup**: Profesionální audio soubory, podcastové epizody
   - **struktura uvnitř pracovního adresáře** A/{id}/{Platform}, A/{id}/Audio
   - **[📄 Zobrazit dokumentaci A stavového automatu](./A/STATE_MACHINE.md)** *(Připravuje se)*

3. **V (Generování videa)**
   - **Účel**: Kombinace audia s vizuály pro video platformy
   - **Stavový automat**: Plánování scén, generování klíčových snímků, skládání videa *(K implementaci)*
   - **Vstup**: Publikované audio z modulu A
   - **Výstup**: Videa optimalizovaná pro platformy (YouTube, TikTok, Instagram)
   - **struktura uvnitř pracovního adresáře** V/{id}/{Platform}, V/{id}/Video
   - **[📄 Zobrazit dokumentaci V stavového automatu](./V/STATE_MACHINE.md)** *(Připravuje se)*

4. **P (Publikování)**
   - **Účel**: Hromadná distribuce napříč platformami po dokončení obsahu
   - **Stavový automat**: Publikování na více platformách, plánování, křížové zveřejňování *(K implementaci)*
   - **Vstup**: Dokončený obsah z modulů T, A, V
   - **Výstup**: Publikovaný obsah napříč všemi cílovými platformami
   - **struktura uvnitř pracovního adresáře** P/{Year}/{Month}/{00-10/10-20/20-end}/{day}/{hour}/{id}/{platform}
   - **[📄 Zobrazit dokumentaci P stavového automatu](./P/STATE_MACHINE.md)** *(Připravuje se)*

5. **M (Metriky/Analytika)**
   - **Účel**: Monitorování výkonu publikovaného obsahu
   - **Typ**: Meta-modul (monitoruje publikovaný obsah z T/A/V/P)
   - **Funkce**: Sledování výkonu publikovaného obsahu, sběr KPI, metriky zapojení, výsledky A/B testování
   - **Výstup**: Poznatky zpětně směřující do generování nápadů
   - **Zpětnovazební smyčka pro inspiraci** 
     - **Sběr dat o výkonu z publikovaných věcí** 
   - **struktura uvnitř pracovního adresáře** M/{Year}/{Month}/{00-10/10-20/20-end}/{day}/{hour}/{id}/Metrics/{platform}
   - **[📄 Zobrazit dokumentaci M stavového automatu](./M/STATE_MACHINE.md)** *(Připravuje se)*

### Principy stavového automatu

- **Sekvenční pipeline**: T → A → V → P (každá fáze staví na předchozí)
- **Kvalitní kontrolní body**: Explicitní kritéria přijetí při každém přechodu
- **Iterativní vylepšování**: Smyčky a zpětnovazební cykly v rámci každého modulu
- **Postupná publikace**: Uvolnění v jakékoli fázi na základě cílů
- **Průřezová observabilita**: Modul M sleduje metriky napříč všemi fázemi
- **Sledování verzí**: Dynamické verzování (v1, v2, v3+) s neomezenými iteracemi

### Aktuální stav implementace

✅ **T modul**: Kompletní 16fázový iterativní workflow s MVP dokumentací  
🔄 **A modul**: Návrh stavového automatu v procesu  
🔄 **V modul**: Návrh stavového automatu v procesu  
🔄 **P modul**: Fáze plánování architektury  
🔄 **M modul**: Fáze definice frameworku metrik

---

## 🔄 Model postupného obohacování

PrismQ používá přístup **sekvenčního obohacování formátů**:

1. **Text nejprve**: Rychlá publikace, SEO výhody, okamžitý dosah
2. **Audio jako druhé**: Zvýšené zapojení, distribuce podcastů
3. **Video nakonec**: Maximální dopad, optimalizace platformy

Každá fáze používá předchozí formát jako svůj základ:
- Audio čte z **publikovaného textu** (ne z konceptů skriptů)
- Video synchronizuje s **publikovaným audiem** (ne se surovými nahrávkami)
- Analytika z každého formátu informuje budoucí obsah

## 📊 Klíčové vlastnosti

- ✅ **Postupná publikace**: Uvolnění obsahu v každé fázi
- ✅ **Kvalitní kontrolní body**: Revize a schválení při každém přechodu
- ✅ **Optimalizace formátu**: Zpracování specifické pro platformu
- ✅ **Integrace analytiky**: Data o výkonu se vrací do vytváření nápadů
- ✅ **Flexibilní workflow**: Zastavení v jakékoli fázi na základě cílů
- ✅ **Organizace jmenného prostoru**: Jasné hranice modulů

## 📄 Licence

Proprietární - Všechna práva vyhrazena - Copyright (c) 2025 PrismQ

---

**Začněte prozkoumávat**: [T modul](./T/README.md) | [A modul](./A/README.md) | [V modul](./V/README.md) | [Client](./Client/README.md) | [Workflow](./_meta/WORKFLOW.md)
