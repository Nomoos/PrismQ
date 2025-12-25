# Kontrola běhu modulu: PrismQ.A.Voiceover

## 🎯 Účel modulu
Generování voiceover audio z publikovaného textového obsahu. Modul převádí text na mluvenou řeč pomocí TTS (Text-to-Speech) technologie, vytváří audio nahrávky připravené pro další zpracování.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Databáze (Stories s published text)
- **Typ dat:** Text content z publikovaných Stories
- **Povinné hodnoty:**
  - Published Story s clean content textem
  - Target voice parameters (hlas, rychlost, tón)
- **Nepovinné hodnoty:**
  - `--preview`, `--debug` flags
  - Custom pronunciation dictionary
  - SSML markup pro emphasis
- **Očekávané předpoklady:**
  - Stories publikované modulem 20
  - Přístup k TTS API/služby (Azure TTS, Google TTS, ElevenLabs, atd.)
  - Přístup k databázi
  - Storage pro audio soubory

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Načtení Stories** - Stories s published text bez audio
2. **Text preprocessing:**
   - Odstranění HTML markup
   - Konverze special characters
   - Pronunciation corrections
   - SSML markup injection (emphasis, pauses)
   - Sentence segmentation pro natural speech
3. **Voice selection:**
   - Výběr narratorského hlasu (muž/žena, věk, accent)
   - Nastavení speaking rate
   - Nastavení pitch a tone
   - Volume normalization target
4. **TTS generation:**
   - Split text na segments (pokud dlouhý)
   - Pro každý segment:
     - Volání TTS API
     - Generování audio
     - Validace quality
   - Concatenate segments (pokud multiple)
5. **Audio post-processing:**
   - Silence trimming (začátek/konec)
   - Basic noise reduction
   - Format conversion (MP3, WAV)
6. **Storage:**
   - Uložení audio souboru
   - Generování URL/path
7. **Update Story:**
   - Uložení audio URL/path
   - State změna na "PrismQ.A.Narrator" (modul 22)

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:** Audio soubory (WAV/MP3) s voiceover
- **Formát výstupu:** 
  - Audio files na storage
  - Databáze (updated Stories s audio paths)
- **Vedlejší efekty:** 
  - TTS usage metrics
  - Audio quality reports
- **Chování při chybě:** 
  - TTS API error: Retry, fallback voice
  - Quality issues: Regenerate with adjusted parameters

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul 20 (PrismQ.T.Publishing) - source published text
- TTS API (Azure, Google, ElevenLabs, atd.)
- Audio storage (filesystem, S3, atd.)
- Databáze

**Výstupní závislosti:**
- Modul 22 (PrismQ.A.Narrator) - narrator selection/validation
- Audio soubory pro další processing

---

## 📝 Poznámky / Rizika

**Poznámky:**
- TTS quality varies by provider a voice
- Natural-sounding voices jsou expensive (neural TTS)
- Long content může vyžadovat segmentation
- Pronunciation dictionary critical pro správné výslovnosti
- SSML markup umožňuje better control nad prosody

**Rizika:**
- **TTS cost**: Neural voices jsou expensive per character
- **Quality variance**: Některé voices lepší než jiné
- **Pronunciation errors**: TTS může špatně vyslovovat names, terms
- **Unnatural pauses**: TTS nemusí dobře handling sentence flow
- **Accent mismatch**: Voice accent nemusí matchovat target audience

**Doporučení:**
- Test multiple TTS providers pro quality comparison
- Build pronunciation dictionary
- Use SSML pro emphasis a natural pauses
- Quality check sampling
- A/B testing různých voices
- Cost optimization (cheaper voices pro drafts)
