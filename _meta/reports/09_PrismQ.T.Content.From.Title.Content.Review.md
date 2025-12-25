# Kontrola běhu modulu: PrismQ.T.Content.From.Title.Content.Review

## 🎯 Účel modulu
Regenerace obsahu (Content) na základě review feedbacku. Pokud původní content neprošel review (z modulu 06), tento modul vytvoří nový, vylepšený content reflektující review komentáře a title.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Databáze (tabulka Story)
- **Typ dat:** Story objekty ve stavu "PrismQ.T.Content.From.Title.Content.Review"
- **Povinné hodnoty:**
  - Story s title
  - Story s původním content
  - Review feedback z modulu 06
- **Nepovinné hodnoty:**
  - `--preview`, `--debug` flags
- **Očekávané předpoklady:**
  - Stories s failed content review
  - Běžící Ollama server
  - Přístup k databázi

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Načtení Stories k re-generování** - Stories ve stavu "PrismQ.T.Content.From.Title.Content.Review"
2. **Analýza review feedback:**
   - Extrakce konkrétních issues z review
   - Identifikace oblastí pro vylepšení
   - Zachování fungujících částí
3. **AI-powered content regeneration:**
   - Prompt obsahující:
     - Původní content (co nefungovalo)
     - Review feedback (specifické problémy)
     - Title (co má content splňovat)
     - Požadavky na vylepšení
   - Generování vylepšeného obsahu
4. **Validace nového content:**
   - Kontrola délky (~300 slov, max 175s)
   - Strukturovanost (intro, body, conclusion)
   - Kvalita textu
5. **Update Story:**
   - Nastavení nového content
   - Změna stavu na "PrismQ.T.Review.Content.From.Title" (modul 10)
6. **Uložení a reportování**

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:** Story objekty s regenerovaným obsahem
- **Formát výstupu:** Databáze (updated Stories), improvement reports
- **Vedlejší efekty:** Regeneration metrics, quality comparison
- **Chování při chybě:** Retry, manual intervention request

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul 06 - source failed content review
- Ollama server, databáze

**Výstupní závislosti:**
- Modul 10 (PrismQ.T.Review.Content.From.Title) - další review

---

## 📝 Poznámky / Rizika

**Poznámky:**
- Max 3 regeneration attempts (loop protection)
- Tracking quality improvement metrics
- Preserving good parts of original content kde možné

**Rizika:**
- Content může ztratit originalitu při regeneraci
- Regeneration loop možná
- Performance overhead při opakovaných regeneracích

**Doporučení:**
- Human review pro multiple regenerations
- Differential regeneration (pouze problematické části)
- Learning from patterns v review feedback
