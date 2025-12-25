# Kontrola běhu modulu: PrismQ.T.Review.Content.From.Title.Idea

## 🎯 Účel modulu
Review vygenerovaného obsahu (Content) proti titulku a původnímu nápadu. Modul validuje, zda Content odpovídá titulku a original Idea, kontroluje kvalitu, relevanci a konzistenci.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Databáze (tabulka Story)
- **Typ dat:** Story objekty ve stavu "PrismQ.T.Review.Content.From.Title.Idea"
- **Povinné hodnoty:**
  - Story s title a content fieldy
  - Platná idea_id reference
- **Nepovinné hodnoty:**
  - `--preview`, `--debug` flags
- **Očekávané předpoklady:**
  - Stories prošlé modulem 05 (title review passed)
  - Běžící Ollama server
  - Přístup k databázi

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Načtení Stories k review** - dotaz na stav "PrismQ.T.Review.Content.From.Title.Idea"
2. **AI content review:**
   - Hodnocení relevance content k titulku
   - Kontrola consistency s Idea
   - Hodnocení kvality a struktury content
   - Identifikace problémů
3. **Vyhodnocení a rozhodnutí:**
   - Pass → Změna stavu na "PrismQ.T.Review.Title.From.Content" (modul 07)
   - Fail → Změna stavu na "PrismQ.T.Content.From.Title.Content.Review" (modul 09 - regenerace content)
4. **Update Story a reportování**

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:** Story objekty s content review metadaty, přesunuty do příslušného stavu
- **Formát výstupu:** Databáze (updated Stories), konzolový výstup (review results)
- **Vedlejší efekty:** Review metrics, logs
- **Chování při chybě:** Retry, skip nebo fail podle typu chyby

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul 05 (PrismQ.T.Review.Title.From.Content.Idea) - předchozí review
- Ollama server, databáze

**Výstupní závislosti:**
- Modul 07 (PrismQ.T.Review.Title.From.Content) - pokud pass
- Modul 09 (PrismQ.T.Content.From.Title.Content.Review) - pokud fail

---

## 📝 Poznámky / Rizika

**Poznámky:**
- Druhý review krok v multi-stage review
- Fokus na kvalitu a relevanci content
- Může identifikovat potřebu content regenerace

**Rizika:**
- AI subjektivita v hodnocení kvality
- False positives/negatives možné
- Performance overhead z AI volání

**Doporučení:**
- Human sampling pro calibraci review kritérií
- Tracking content quality trends
- Implementovat kvalitativní metriky
