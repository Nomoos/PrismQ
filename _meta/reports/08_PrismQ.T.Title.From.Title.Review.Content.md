# Kontrola běhu modulu: PrismQ.T.Title.From.Title.Review.Content

## 🎯 Účel modulu
Regenerace titulku na základě review feedbacku. Pokud původní titulek neprošel review (z modulu 05 nebo 07), tento modul vytvoří nový, vylepšený titulek reflektující review komentáře a content.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Databáze (tabulka Story)
- **Typ dat:** Story objekty ve stavu "PrismQ.T.Title.From.Title.Review.Content"
- **Povinné hodnoty:**
  - Story s původním title
  - Story s content
  - Review feedback z předchozího review kroku
- **Nepovinné hodnoty:**
  - `--preview`, `--debug` flags
- **Očekávané předpoklady:**
  - Stories s failed title review (z modulu 05 nebo 07)
  - Běžící Ollama server
  - Přístup k databázi

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Načtení Stories k re-generování** - Stories ve stavu "PrismQ.T.Title.From.Title.Review.Content"
2. **Příprava pro regeneraci:**
   - Načtení původního title
   - Načtení review feedback (issues, suggestions)
   - Načtení content pro kontext
3. **AI-powered title regeneration:**
   - Prompt obsahující:
     - Původní titulek (co nefungovalo)
     - Review feedback (proč nefungovalo)
     - Content (co má titulek reprezentovat)
     - Požadavky na vylepšení
   - Generování nového, vylepšeného titulku
4. **Scoring nového titulku** - použití stejných kritérií jako v modulu 03
5. **Update Story:**
   - Nastavení nového title
   - Změna stavu na "PrismQ.T.Review.Content.From.Title" (modul 10)
   - Uložení metadata (regeneration count, feedback applied)
6. **Uložení do databáze a reportování**

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:** Story objekty s regenerovanými titulky
- **Formát výstupu:** Databáze (updated Stories s novými titles)
- **Vedlejší efekty:** Regeneration metrics, comparison logs
- **Chování při chybě:** Retry, použití fallback title, nebo manual intervention request

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul 05 nebo 07 - source failed review
- Ollama server, databáze

**Výstupní závislosti:**
- Modul 10 (PrismQ.T.Review.Content.From.Title) - další review krok

---

## 📝 Poznámky / Rizika

**Poznámky:**
- Regeneration loop protection - max 3 pokusy
- Tracking improvement metrics (before/after scores)
- Learning from review feedback pro future generování

**Rizika:**
- Nekonečná regeneration loop (ošetřeno max attempts)
- Degradace kvality při opakovaných regeneracích
- Ztráta původního creative direction

**Doporučení:**
- Manual review pro Stories s více než 2 regeneracemi
- A/B testing original vs regenerated titles
- Implementovat učení z feedback patterns
