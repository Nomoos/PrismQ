# Kontrola běhu modulu: PrismQ.A.Normalized

**Účel:** Audio normalizace hlasitosti podle LUFS standardu (-16 LUFS podcast, -14 LUFS YouTube) pro konzistentní listening experience.

---

## 📥 Vstup
- **Zdroj:** Audio soubory z modulu 22
- **Data:** Validated voiceover audio (WAV/MP3), target LUFS level
- **Předpoklady:** Audio z modulu 22, FFmpeg nebo audio processing library (pyloudnorm, librosa)

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. LUFS measurement — current integrated LUFS, dynamic range, peaks
3. Normalization — gain adjustment, loudness normalization na target LUFS, peak limiting, true peak limiting
4. Validace — LUFS target achieved, artifacts/distortion check, dynamic range preserved
5. Export — save normalized audio, generate waveform visualization
6. [Uložení výsledků](shared/databazova_integrace.md) — update Story: normalized audio path, `state="PrismQ.A.Enhancement"`

---

## 📤 Výstup
- **Primární:** LUFS-normalized audio soubory
- **DB změny:** Tabulka `Story` — normalized audio path, LUFS metrics, `state="PrismQ.A.Enhancement"`
- **Další krok:** Modul 24 (PrismQ.A.Enhancement)
