# Kontrola běhu modulu: PrismQ.A.Normalized

## 🎯 Účel modulu
Audio normalizace podle LUFS standardu. Modul normalizuje hlasitost audio na konzistentní úroveň (typicky -16 LUFS pro podcast, -14 LUFS pro YouTube), zajišťuje konzistentní listening experience.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Audio soubory z modulu 22
- **Typ dat:** Raw audio files (WAV/MP3)
- **Povinné hodnoty:**
  - Validated voiceover audio
  - Target LUFS level (-16, -14, atd.)
- **Nepovinné hodnoty:**
  - `--preview`, `--debug` flags
  - Peak limiting threshold
- **Očekávané předpoklady:**
  - Audio files z modulu 22
  - FFmpeg nebo audio processing library
  - Přístup k databázi

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Load audio** - Načtení audio z storage
2. **LUFS measurement:**
   - Measure current integrated LUFS
   - Measure dynamic range
   - Identify peaks
3. **Normalization:**
   - Calculate gain adjustment
   - Apply loudness normalization (target LUFS)
   - Peak limiting (prevent clipping)
   - True peak limiting
4. **Validation:**
   - Verify LUFS target achieved
   - Check for artifacts/distortion
   - Validate dynamic range preserved
5. **Export:**
   - Save normalized audio
   - Generate waveform visualization
6. **Update Story:**
   - Uložení normalized audio path
   - State změna na "PrismQ.A.Enhancement" (modul 24)

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:** LUFS-normalized audio files
- **Formát výstupu:** Audio files, waveform images
- **Vedlejší efekty:** Audio metrics (before/after LUFS)
- **Chování při chybě:** Re-normalize s adjusted parameters

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul 22 - validated audio
- FFmpeg nebo audio processing library (pyloudnorm, librosa)
- Databáze

**Výstupní závislosti:**
- Modul 24 (PrismQ.A.Enhancement)

---

## 📝 Poznámky / Rizika

**Poznámky:**
- LUFS standard critical pro cross-platform consistency
- Different platforms mají different LUFS recommendations
- True peak limiting prevents clipping

**Rizika:**
- Over-normalization může cause pumping/distortion
- Dynamic range reduction může affect quality
- Platform-specific LUFS targets

**Doporučení:**
- Platform-specific normalization profiles
- Quality check post-normalization
- Preserve original dynamic range kde possible
