# Kontrola běhu modulu: PrismQ.A.Publishing

## 🎯 Účel modulu
Publikování finálního audio na cílové platformy. Modul uploaduje audio soubory na podcast platformy, YouTube (jako audio track), Spotify, Apple Podcasts, RSS feeds, a jiné audio distribution channels.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Enhanced audio z modulu 24
- **Typ dat:** High-quality audio files (MP3, AAC)
- **Povinné hodnoty:**
  - Enhanced, production-ready audio
  - Metadata (title, description, episode number)
  - Cover art/thumbnail
- **Nepovinné hodnoty:**
  - `--preview`, `--debug` flags
  - Target platforms (Spotify, Apple, YouTube, RSS)
  - Scheduling parameters
- **Očekávané předpoklady:**
  - Audio z modulu 24
  - Přístup k publishing APIs (podcast hosting, streaming platforms)
  - Cover art připravený
  - Přístup k databázi

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Prepare publishing package:**
   - Audio file (MP3 optimalizovaný pro streaming)
   - Metadata (title, description, tags)
   - Cover art (1400x1400 pro podcast, 1280x720 pro YouTube thumbnail)
   - Show notes/transcript
   - Timestamps/chapters (pokud applicable)
2. **Podcast platforms:**
   - Upload na podcast hosting (Buzzsprout, Libsyn, Anchor)
   - Update RSS feed
   - Submit na Apple Podcasts, Spotify, Google Podcasts
   - Add episode notes a show links
3. **Streaming platforms:**
   - Upload na YouTube (audio s static image nebo waveform video)
   - Upload na SoundCloud
   - Distribute via DistroKid/TuneCore (pokud music)
4. **Website integration:**
   - Embed audio player na web
   - Create episode page
   - Add download links
5. **Social media:**
   - Create audiogram snippets (waveform animations)
   - Post announcements s links
   - Create shareable clips
6. **Analytics setup:**
   - Tracking pixels/codes
   - UTM parameters v links
   - Platform-specific analytics
7. **Post-publishing:**
   - Generate shareable links
   - Create promo materials
   - Email notifications
8. **Update Story:**
   - Uložení publishing URLs
   - State změna na "AudioPublished"
   - Publishing timestamp

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:**
  - Published audio na podcast platforms
  - YouTube audio upload
  - RSS feed updated
  - Streaming platform presence
  
- **Formát výstupu:**
  - MP3/AAC na hosting platforms
  - RSS feed XML
  - Platform-specific metadata
  - Social media audiograms
  
- **Vedlejší efekty:**
  - RSS feed updated
  - Social media posts
  - Analytics tracking active
  - Email notifications sent
  - Publishing reports
  
- **Chování při chybě:**
  - API error: Retry s backoff
  - Upload failed: Rollback, log, alert
  - Partial failure: Continue s successful platforms

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul 24 - enhanced audio
- Podcast hosting APIs (Buzzsprout, Anchor, atd.)
- Streaming APIs (YouTube, SoundCloud)
- RSS feed generator
- Social media APIs
- Databáze

**Výstupní závislosti:**
- Modul 30 (PrismQ.M.Analytics) - trackuje audio performance
- Video pipeline může use published audio

---

## 📝 Poznámky / Rizika

**Poznámky:**
- Multi-platform publishing maximizes reach
- RSS feed je core pro podcast distribution
- YouTube audio umožňuje monetization
- Audiograms critical pro social media promotion
- Scheduling allows optimal publish times
- Chapters/timestamps improve listener experience

**Rizika:**
- **API failures**: Platforms mohou být down
- **Format requirements**: Different platforms různé audio specs
- **Approval delays**: Některé platformy review před live
- **RSS feed issues**: Malformed RSS může break podcast apps
- **Metadata errors**: Chybné metadata mohou affect discoverability
- **File size limits**: Platformy mají upload limits

**Doporučení:**
- Robust retry logic pro all API calls
- Pre-validate audio files proti platform requirements
- Test RSS feed s validators
- Dry-run mode pro testing
- Multi-stage publishing (critical platforms first)
- Backup audio files long-term
- Monitor platform analytics
- Cross-promote across platforms
- Build email list pro direct audience
- Regular check RSS feed health
- Quality check listening po publish
