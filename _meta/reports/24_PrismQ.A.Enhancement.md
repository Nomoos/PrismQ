# Kontrola běhu modulu: PrismQ.A.Enhancement

**Účel:** Profesionální audio enhancement — EQ, komprese, de-essing a noise reduction pro finální production kvalitu.

---

## 📥 Vstup
- **Zdroj:** Normalized audio z modulu 23
- **Data:** LUFS-normalized audio soubory (WAV/MP3)
- **Předpoklady:** Audio z modulu 23, audio processing tools (FFmpeg, SoX)

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Noise reduction — background noise, click/pop removal, hum removal
3. EQ — high-pass filter (low-end rumble), presence boost (speech frequencies), de-harshness
4. Compression — dynamic range compression, voice leveling
5. De-essing — reduce harsh sibilance ('s' sounds)
6. Final touches — subtle reverb, stereo widening, fade in/out
7. Quality validation — artifact check, frequency response, A/B comparison
8. [Uložení výsledků](shared/databazova_integrace.md) — save enhanced audio, update Story: `state="PrismQ.A.Publishing"`

---

## 📤 Výstup
- **Primární:** Professionally enhanced audio soubory
- **DB změny:** Tabulka `Story` — enhanced audio path, `state="PrismQ.A.Publishing"`
- **Další krok:** Modul 25 (PrismQ.A.Publishing)
