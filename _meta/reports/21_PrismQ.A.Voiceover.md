# Kontrola běhu modulu: PrismQ.A.Voiceover

**Účel:** Generování voiceover audio z publikovaného textu pomocí TTS technologie (Azure/Google/ElevenLabs).

---

## 📥 Vstup
- **Zdroj:** Databáze (Stories s published text)
- **Data:** Clean text content, target voice parametry (hlas, rychlost, tón)
- **Předpoklady:** Stories publikované modulem 20, přístup k TTS API, audio storage

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Text preprocessing — HTML removal, special characters, pronunciation corrections, SSML markup, sentence segmentation
3. Voice selection — narrator hlas (muž/žena, věk, accent), speaking rate, pitch, tone
4. TTS generation — split na segmenty, volání TTS API, validace kvality, concatenation
5. Audio post-processing — silence trimming, basic noise reduction, format conversion (MP3/WAV)
6. [Uložení výsledků](shared/databazova_integrace.md) — uložení audio souboru, update Story: audio URL/path, `state="PrismQ.A.Narrator"`

---

## 📤 Výstup
- **Primární:** Audio soubory (WAV/MP3) s voiceover
- **DB změny:** Tabulka `Story` — audio path/URL, `state="PrismQ.A.Narrator"`
- **Další krok:** Modul 22 (PrismQ.A.Narrator)
