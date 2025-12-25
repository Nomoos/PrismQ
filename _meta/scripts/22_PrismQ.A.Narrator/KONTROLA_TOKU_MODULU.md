# Kontrola běhu modulu: PrismQ.A.Narrator

## 🎯 Účel modulu
Výběr a validace narratorského hlasu. Modul hodnotí kvalitu vygenerovaného voiceover, vybírá nejlepší narrator voice varianty, a zajišťuje konzistenci hlasu napříč projekty.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Databáze a audio storage
- **Typ dat:** Audio soubory z modulu 21, voice metadata
- **Povinné hodnoty:**
  - Generated voiceover audio
  - Voice parameters použité v generování
  - Story metadata (target audience)
- **Nepovinné hodnoty:**
  - `--preview`, `--debug` flags
  - Multiple voice variants pro comparison
- **Očekávané předpoklady:**
  - Audio soubory z modulu 21
  - Přístup k audio analysis tools
  - Přístup k databázi

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Načtení audio files** - Audio z modulu 21
2. **Voice quality analysis:**
   - Clarity assessment
   - Natural-ness scoring
   - Emotion appropriateness
   - Pace evaluation
   - Pronunciation accuracy check
3. **Audience fit validation:**
   - Voice matches target demographic?
   - Tone appropriate pro content type?
   - Accent acceptable pro audience?
4. **Consistency check:**
   - Voice matches previous projects (pokud series)?
   - Consistent quality across segments?
5. **Selection decision:**
   - Accept voice as-is
   - Request regeneration s different voice
   - Flag pro human narrator (pokud quality insufficient)
6. **Update Story:**
   - Uložení narrator validation results
   - State změna na "PrismQ.A.Normalized" (modul 23)

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:** Validated narrator choice
- **Formát výstupu:** Databáze (narrator metadata, validation results)
- **Vedlejší efekty:** Voice quality metrics
- **Chování při chybě:** Request regeneration nebo human narrator

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul 21 - voiceover audio
- Audio analysis tools
- Databáze

**Výstupní závislosti:**
- Modul 23 (PrismQ.A.Normalized)

---

## 📝 Poznámky / Rizika

**Poznámky:**
- Voice selection critical pro audience engagement
- Consistency important pro series/brand
- Quality threshold může vary by content type

**Rizika:**
- Subjektivita v voice quality assessment
- Cultural preferences v voice characteristics
- Inconsistency across projects

**Doporučení:**
- Build voice library s proven voices
- A/B testing voices s real audience
- Consistency guidelines pro series
