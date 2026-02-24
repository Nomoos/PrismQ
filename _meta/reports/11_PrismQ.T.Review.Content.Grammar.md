# Kontrola běhu modulu: PrismQ.T.Review.Content.Grammar

**Účel:** Detailní AI kontrola gramatiky, pravopisu, interpunkce a syntaxe obsahu s auto-korekcí triviálních chyb.

---

## 📥 Vstup
- **Zdroj:** Databáze (tabulka `Story`)
- **Data:** Story ve stavu `PrismQ.T.Review.Content.Grammar` s content fieldem
- **Předpoklady:** Stories prošlé modulem 10, běžící Ollama server nebo grammar checking služby

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Načtení Stories ve stavu `PrismQ.T.Review.Content.Grammar`
3. [AI grammar check](shared/ollama_ai_integrace.md) — pravopis, gramatika, interpunkce, syntaxe, typos
4. Generování correction suggestions (popis, umístění, návrh, severity: critical/warning/suggestion)
5. Auto-correction triviálních chyb, flagování non-trivial pro manual review
6. [Uložení výsledků](shared/databazova_integrace.md) — update Story: grammar report, `state="PrismQ.T.Review.Content.Tone"`

---

## 📤 Výstup
- **Primární:** Story s grammar review report a případnými korekcemi
- **DB změny:** Tabulka `Story` — grammar review metadata, `state="PrismQ.T.Review.Content.Tone"`
- **Další krok:** Modul 12 (PrismQ.T.Review.Content.Tone)
