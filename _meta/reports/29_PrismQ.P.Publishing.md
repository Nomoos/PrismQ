# Kontrola běhu modulu: PrismQ.P.Publishing

**Účel:** Multi-platform publishing orchestration — koordinované publikování text/audio/video napříč platformami se synchronizovaným release.

---

## 📥 Vstup
- **Zdroj:** Databáze (Stories s finálními assets)
- **Data:** Text (modul 20), audio (modul 25), video (modul 28), publishing metadata
- **Předpoklady:** Alespoň jeden content typ ready, přístup k publishing APIs všech platforem

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Publishing preparation — verify assets ready, validate metadata, platform requirements check
3. Coordinated publishing — Phase 1: blog/YouTube/Apple Podcasts; Phase 2: Medium/Spotify/social; Phase 3: RSS/email/aggregators
4. Cross-platform linking — blog↔audio↔video cross-references, social posts s links
5. Cross-promotion — platform-specific teasers (Twitter thread, Instagram carousel, LinkedIn post, FB clip)
6. SEO & analytics — sitemap submit, UTM tracking, cross-platform attribution
7. [Uložení výsledků](shared/databazova_integrace.md) — update Story: all publishing URLs, `state="FullyPublished"`, platform status

---

## 📤 Výstup
- **Primární:** Content published napříč všemi platformami s cross-platform link network
- **DB změny:** Tabulka `Story` — all publishing URLs, `state="FullyPublished"`, publishing timestamp, platform status
- **Další krok:** Modul 30 (PrismQ.M.Analytics)
