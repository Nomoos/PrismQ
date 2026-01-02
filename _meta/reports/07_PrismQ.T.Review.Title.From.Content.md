# Kontrola běhu modulu: PrismQ.T.Review.Title.From.Content

## 🎯 Účel modulu
Finální review titulku proti vygenerovanému obsahu (bez závislosti na původní Idea). Modul se zaměřuje čistě na konzistenci mezi titulkem a contentem, validuje relevanci a atraktivitu titulku pro daný obsah.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Databáze (tabulka Story)
- **Typ dat:** Story objekty ve stavu "PrismQ.T.Review.Title.From.Content"
- **Povinné hodnoty:**
  - Story s title a content fieldy
- **Nepovinné hodnoty:**
  - `--preview`, `--debug` flags
- **Očekávané předpoklady:**
  - Stories prošlé modulem 06 (content review passed)
  - Běžící Ollama server
  - Přístup k databázi

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Načtení Stories k review** - dotaz na stav "PrismQ.T.Review.Title.From.Content"
2. **AI title-content review:**
   - Hodnocení title-content match
   - Kontrola, zda titulek přesně reprezentuje obsah
   - Hodnocení atraktivity titulku
   - SEO a clickability faktory
3. **Vyhodnocení:**
   - Pass → "PrismQ.T.Review.Content.From.Title" (modul 10)
   - Fail → "PrismQ.T.Title.From.Title.Review.Content" (modul 08 - regenerace)
4. **Loop pro další Stories:**
   - V continuous mode: čekání 1ms mezi iteracemi, pokud není žádná Story, čekání 30 sekund a opakování dotazu
   - Možnost ukončení
5. **Update a reportování**
6. **Ošetření chyb:**
   - Žádné Stories k zpracování - informační zpráva, čekání 30 sekund a opakování (continuous mode)
   - AI nedostupný - error message, ukončení
   - Review parsing failed - retry, pak skip
   - DB errors - rollback, logování

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:** Story objekty s title review metadaty
- **Formát výstupu:** Databáze (updated Stories), review reports
- **Vedlejší efekty:** Review metrics, logs
- **Chování při chybě:** Retry, skip, nebo fail

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul 06 - předchozí review
- Ollama server, databáze

**Výstupní závislosti:**
- Modul 10 (PrismQ.T.Review.Content.From.Title) - pokud pass
- Modul 08 (PrismQ.T.Title.From.Title.Review.Content) - pokud fail

---

## 📝 Poznámky / Rizika

**Poznámky:**
- Fokus na title-content pair, bez Idea context
- Validuje praktickou použitelnost titulku
- Důležitý pro SEO a user engagement

**Rizika:**
- Subjektivita v hodnocení "atraktivity"
- Click-bait detection může být příliš přísná nebo benevolentní

**Doporučení:**
- A/B testing titles pro real-world validation
- Monitoring actual click-through rates
