# Kontrola běhu modulů - PrismQ Pipeline

Tento adresář obsahuje detailní dokumentaci toku dat pro všechny moduly v PrismQ content production pipeline.

## 📚 Struktura dokumentace

Každý modul má vlastní soubor s kompletním popisem běhu:

**Legenda implementace:**
- ✅ = Modul je plně implementován (má `src/` složku s kódem)
- ⬜ = Modul zatím není implementován (pouze dokumentace)

### 🎯 Text Modules (T) - Moduly 01-20

#### Generování obsahu (01-04)
- ✅ **[01_PrismQ.T.Idea.From.User](01_PrismQ.T.Idea.From.User.md)** - Vytváření nápadů (Idea objektů) z textového vstupu pomocí AI
- ✅ **[02_PrismQ.T.Story.From.Idea](02_PrismQ.T.Story.From.Idea.md)** - Vytváření Story objektů z existujících Ideas
- ✅ **[03_PrismQ.T.Title.From.Idea](03_PrismQ.T.Title.From.Idea.md)** - Generování titulků pro Story objekty na základě Ideas
- ✅ **[04_PrismQ.T.Content.From.Idea.Title](04_PrismQ.T.Content.From.Idea.Title.md)** - Generování textového obsahu (Content v1 / Script) z titulku a nápadu

#### Review a validace - První kolo (05-10)
- ⬜ **[05_PrismQ.T.Review.Title.From.Content.Idea](05_PrismQ.T.Review.Title.From.Content.Idea.md)** - Review titulku proti obsahu a původnímu nápadu
- ⬜ **[06_PrismQ.T.Review.Content.From.Title.Idea](06_PrismQ.T.Review.Content.From.Title.Idea.md)** - Review obsahu proti titulku a původnímu nápadu
- ⬜ **[07_PrismQ.T.Review.Title.From.Content](07_PrismQ.T.Review.Title.From.Content.md)** - Finální review titulku proti obsahu (bez Idea závislosti)
- ✅ **[08_PrismQ.T.Title.From.Title.Review.Content](08_PrismQ.T.Title.From.Title.Review.Content.md)** - Regenerace titulku na základě review feedbacku
- ✅ **[09_PrismQ.T.Content.From.Title.Content.Review](09_PrismQ.T.Content.From.Title.Content.Review.md)** - Regenerace obsahu na základě review feedbacku
- ✅ **[10_PrismQ.T.Review.Content.From.Title](10_PrismQ.T.Review.Content.From.Title.md)** - Finální review obsahu proti titulku

#### Detailní quality reviews (11-17)
- ⬜ **[11_PrismQ.T.Review.Content.Grammar](11_PrismQ.T.Review.Content.Grammar.md)** - Detailní gramatická kontrola obsahu
- ✅ **[12_PrismQ.T.Review.Content.Tone](12_PrismQ.T.Review.Content.Tone.md)** - Kontrola tónu a stylu obsahu
- ⬜ **[13_PrismQ.T.Review.Content.Content](13_PrismQ.T.Review.Content.Content.md)** - Kontrola faktické správnosti a kvality obsahu
- ✅ **[14_PrismQ.T.Review.Content.Consistency](14_PrismQ.T.Review.Content.Consistency.md)** - Kontrola stylové a strukturální konzistence
- ✅ **[15_PrismQ.T.Review.Content.Editing](15_PrismQ.T.Review.Content.Editing.md)** - Finální editační průchod obsahu
- ✅ **[16_PrismQ.T.Review.Title.Readability](16_PrismQ.T.Review.Title.Readability.md)** - Kontrola čitelnosti a srozumitelnosti titulku
- ✅ **[17_PrismQ.T.Review.Content.Readability](17_PrismQ.T.Review.Content.Readability.md)** - Kontrola čitelnosti a srozumitelnosti obsahu

#### Expert review a finalizace (18-20)
- ⬜ **[18_PrismQ.T.Story.Review](18_PrismQ.T.Story.Review.md)** - Expert GPT review celé Story
- ⬜ **[19_PrismQ.T.Story.Polish](19_PrismQ.T.Story.Polish.md)** - Finální polish a optimalizace Story před publikováním
- ⬜ **[20_PrismQ.T.Publishing](20_PrismQ.T.Publishing.md)** - Publikování finálního textového obsahu na cílové platformy

---

### 🎵 Audio Modules (A) - Moduly 21-25

- ⬜ **[21_PrismQ.A.Voiceover](21_PrismQ.A.Voiceover.md)** - Generování voiceover audio z publikovaného textu pomocí TTS
- ⬜ **[22_PrismQ.A.Narrator](22_PrismQ.A.Narrator.md)** - Výběr a validace narratorského hlasu
- ⬜ **[23_PrismQ.A.Normalized](23_PrismQ.A.Normalized.md)** - Audio normalizace podle LUFS standardu
- ⬜ **[24_PrismQ.A.Enhancement](24_PrismQ.A.Enhancement.md)** - Audio enhancement (EQ, compression, de-essing, noise reduction)
- ⬜ **[25_PrismQ.A.Publishing](25_PrismQ.A.Publishing.md)** - Publikování finálního audio na podcast platformy

---

### 🎬 Video Modules (V) - Moduly 26-28

- ⬜ **[26_PrismQ.V.Scene](26_PrismQ.V.Scene.md)** - Plánování video scén z obsahu
- ⬜ **[27_PrismQ.V.Keyframe](27_PrismQ.V.Keyframe.md)** - Generování keyframe obrázků pro video scény pomocí AI
- ⬜ **[28_PrismQ.V.Video](28_PrismQ.V.Video.md)** - Assembly finálního video z audio, keyframes a transitions

---

### 🌐 Publishing Module (P) - Modul 29

- ⬜ **[29_PrismQ.P.Publishing](29_PrismQ.P.Publishing.md)** - Multi-platform publishing orchestration

---

### 📊 Analytics Module (M) - Modul 30

- ⬜ **[30_PrismQ.M.Analytics](30_PrismQ.M.Analytics.md)** - Sběr, analýza a reportování metrik z publikovaného obsahu

---

## 📖 Formát dokumentace

Všechny reporty používají zjednodušený technický template.

**Template soubory:**
- **[_template.md](_template.md)** - Template pro nové reporty

**Sdílené sekce:**
- **[shared/inicializace_prostredi.md](shared/inicializace_prostredi.md)** - Inicializace prostředí
- **[shared/databazova_integrace.md](shared/databazova_integrace.md)** - Databázová integrace
- **[shared/ollama_ai_integrace.md](shared/ollama_ai_integrace.md)** - Ollama AI integrace
- **[shared/continuous_mode.md](shared/continuous_mode.md)** - Continuous mode
- **[shared/zpracovani_chyb.md](shared/zpracovani_chyb.md)** - Zpracování chyb

Každý report obsahuje:

- **Účel** - Jedna věta popisující účel modulu
- **📥 Vstup** - Zdroj dat, typ, předpoklady
- **⚙️ Zpracování** - Kroky zpracování s odkazy na sdílené sekce
- **📤 Výstup** - Primární výstup, DB změny, další krok

---

## 🔄 Tok dat v pipeline

```
01. Idea Creation
    ↓
02. Story From Idea (vytvoří 10 Stories)
    ↓
03. Title From Idea
    ↓
04. Content From Idea + Title
    ↓
05-10. Review & Regeneration Loops
    ↓
11-17. Detailed Quality Reviews
    ↓
18. Expert Story Review
    ↓
19. Story Polish
    ↓
20. Text Publishing
    ↓
    ├─→ 21-25. Audio Pipeline
    ├─→ 26-28. Video Pipeline
    └─→ 29. Multi-Platform Publishing
         ↓
    30. Analytics & Metrics
```

---

## 📈 Statistiky

- **Celkem modulů**: 30 (✅ všechny zdokumentovány)
- **Text pipeline**: 20 modulů
- **Audio pipeline**: 5 modulů
- **Video pipeline**: 3 moduly
- **Publishing**: 1 modul
- **Analytics**: 1 modul
- **Režim:** Pouze run mode (žádný preview/debug)

---

*Dokumentace aktualizována: 2026-02-24*
