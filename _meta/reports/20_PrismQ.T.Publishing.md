# Kontrola běhu modulu: PrismQ.T.Publishing

**Účel:** Publikování textového obsahu na cílové platformy s generováním SEO metadata, social media postů a multi-format exportem.

---

## 📥 Vstup
- **Zdroj:** Databáze (tabulka `Story`)
- **Data:** Story ve stavu `PrismQ.T.Publishing` s polished title, content a SEO metadata
- **Předpoklady:** Stories prošlé polish (modul 19), přístup k publishing APIs (WordPress, social media)

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Format conversion — HTML (blog), social media snippets (Twitter/FB/LinkedIn), email newsletter, plain text
3. SEO finalizace — meta title, meta description (~155 znaků), keywords, OpenGraph, Twitter Card, Schema.org
4. Social media content — platformově specifické posty, hashtag suggestions
5. Publishing — upload na CMS (WordPress API), schedule publikace, social media posting
6. [Uložení výsledků](shared/databazova_integrace.md) — update Story: publishing URLs, `state="Published"/"TextPublished"`, timestamp

---

## 📤 Výstup
- **Primární:** Published Story na cílových platformách (blog, social media)
- **DB změny:** Tabulka `Story` — publishing URLs, `state="Published"/"TextPublished"`, publishing timestamp
- **Další krok:** Modul 21 (PrismQ.A.Voiceover), Modul 26 (PrismQ.V.Scene), Modul 30 (PrismQ.M.Analytics)
