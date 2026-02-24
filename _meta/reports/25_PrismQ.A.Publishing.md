# Kontrola běhu modulu: PrismQ.A.Publishing

**Účel:** Publikování audio na podcast platformy, streaming služby a social media s metadaty a cover artem.

---

## 📥 Vstup
- **Zdroj:** Enhanced audio z modulu 24
- **Data:** Production-ready audio (MP3/AAC), metadata (title, description, episode number), cover art
- **Předpoklady:** Audio z modulu 24, přístup k publishing APIs (podcast hosting, streaming), cover art

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Příprava publishing package — optimalizovaný MP3, metadata, cover art (1400x1400 podcast, 1280x720 YouTube), show notes, chapters
3. Podcast publishing — upload na hosting (Buzzsprout/Libsyn/Anchor), update RSS feed, submit Apple/Spotify/Google Podcasts
4. Streaming — upload YouTube (audio + static image), SoundCloud
5. Social media — audiogram snippets (waveform animations), announcement posts, shareable clips
6. [Uložení výsledků](shared/databazova_integrace.md) — update Story: publishing URLs, `state="AudioPublished"`, timestamp

---

## 📤 Výstup
- **Primární:** Published audio na podcast/streaming platformách
- **DB změny:** Tabulka `Story` — audio publishing URLs, `state="AudioPublished"`, publishing timestamp
- **Další krok:** Modul 30 (PrismQ.M.Analytics)
