# Kontrola běhu modulu: PrismQ.T.Review.Content.From.Title

## 🎯 Účel modulu
Finální review obsahu (Content) proti titulku bez závislosti na Idea. Modul validuje title-content pair jako standalone entitu, připravuje pro detailní quality reviews (grammar, tone, content quality).

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Databáze (tabulka Story)
- **Typ dat:** Story objekty ve stavu "PrismQ.T.Review.Content.From.Title"
- **Povinné hodnoty:**
  - Story s title a content fieldy
- **Nepovinné hodnoty:**
  - `--preview`, `--debug` flags
- **Očekávané předpoklady:**
  - Stories prošlé modulem 07 nebo 09
  - Běžící Ollama server
  - Přístup k databázi

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Načtení Stories k final review** - Stories ve stavu "PrismQ.T.Review.Content.From.Title"
2. **Comprehensive AI review:**
   - Hodnocení content-title alignment
   - Celková kvalita content
   - Readability a flow
   - Target audience fit
   - Engagement potential
3. **Vyhodnocení:**
   - Pass → "PrismQ.T.Review.Content.Grammar" (modul 11 - začátek detailed reviews)
   - Conditional pass → Pokračování s poznámkami
   - Fail → Návrat k regeneraci (modul 09)
4. **Update Story a přechod do detail review phase**

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:** Story objekty připravené pro detailed quality reviews
- **Formát výstupu:** Databáze (updated Stories), final review reports
- **Vedlejší efekty:** Quality gate metrics, overall story quality score
- **Chování při chybě:** Retry nebo return to regeneration

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul 07 nebo 09 - předchozí review/regeneration
- Ollama server, databáze

**Výstupní závislosti:**
- Modul 11 (PrismQ.T.Review.Content.Grammar) - start detailed reviews
- Případně modul 09 - pokud fail

---

## 📝 Poznámky / Rizika

**Poznámky:**
- Poslední "big picture" review před detailed checks
- Quality gate před expensive detailed reviews
- Může ušetřit čas skipnutím bad content z detailed reviews

**Rizika:**
- False passes mohou propustit low-quality content do detailed reviews
- False fails mohou zahazovat good content

**Doporučení:**
- Calibrovat review thresholds based na downstream feedback
- Tracking pass/fail rates a downstream quality scores
- Human sampling pro quality assurance
