# Kontrola běhu modulu: PrismQ.V.Scene

## 🎯 Účel modulu
Plánování video scén z obsahu. Modul analyzuje published content a vytváří scene breakdown - rozděluje content na logické scény, definuje visual concepts pro každou scénu, a připravuje scénář pro video produkci.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Databáze (published Stories s text content)
- **Typ dat:** Text content, audio (pokud už existuje)
- **Povinné hodnoty:**
  - Published Story text
  - Target video duration
- **Nepovinné hodnoty:**
  - `--preview`, `--debug` flags
  - Visual style guidelines
  - Brand guidelines
- **Očekávané předpoklady:**
  - Published content z modulu 20
  - AI pro scene analysis
  - Přístup k databázi

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Content analysis:**
   - Parse content structure (intro, body, conclusion)
   - Identify key concepts a ideas
   - Extract visual keywords
2. **Scene breakdown:**
   - Divide content do logical scenes (typicky 5-10 scén pro 120s video)
   - Calculate duration per scene
   - Identify transitions
3. **Visual concept generation:**
   - Pro každou scénu:
     - Generate visual description
     - Identify key visual elements
     - Define mood/tone
     - Suggest color palette
     - Image/video suggestions
4. **Scene script:**
   - Assign narration text per scene
   - Define on-screen text/titles
   - Specify transitions
   - Note timing
5. **Output scene plan:**
   - Scene-by-scene breakdown
   - Visual concepts
   - Timing a transitions
6. **Update Story:**
   - Uložení scene plan
   - State změna na "PrismQ.V.Keyframe" (modul 27)

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:** Scene plan s visual concepts
- **Formát výstupu:** Structured scene data (JSON), storyboard document
- **Vedlejší efekty:** Visual concept library
- **Chování při chybě:** Manual scene planning request

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul 20 (PrismQ.T.Publishing) - published text
- AI pro scene analysis
- Databáze

**Výstupní závislosti:**
- Modul 27 (PrismQ.V.Keyframe) - keyframe generation

---

## 📝 Poznámky / Rizika

**Poznámky:**
- Scene planning critical pro video coherence
- Typical 120s video = 5-10 scén
- Visual concepts guide keyframe generation
- Scene duration should match narration

**Rizika:**
- Too many scenes může být disjointed
- Too few scenes může být monotonous
- Visual concepts may not translate well

**Doporučení:**
- Template scene structures pro different content types
- Visual style consistency guidelines
- Human review scene plans
- A/B testing different scene structures
