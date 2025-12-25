# Kontrola běhu modulu: PrismQ.T.Story.Polish

## 🎯 Účel modulu
Finální polish a optimalizace Story před publikováním. Modul provádí last-minute improvements, SEO optimalizaci, a zajišťuje, že Story je v nejlepší možné formě pro publikaci.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Databáze (tabulka Story)
- **Typ dat:** Story objekty ve stavu "PrismQ.T.Story.Polish"
- **Povinné hodnoty:**
  - Story s title a content fieldy
  - Expert review feedback z modulu 18
- **Nepovinné hodnoty:** `--preview`, `--debug` flags
- **Očekávané předpoklady:**
  - Stories prošlé expert review (modul 18)
  - Běžící Ollama server
  - SEO tools/APIs (optional)
  - Přístup k databázi

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Načtení Stories** - dotaz na stav "PrismQ.T.Story.Polish"
2. **Final polish improvements:**
   - Aplikace expert review suggestions (high priority items)
   - Last-minute wording improvements
   - Enhancement emotional hooks
   - Strengthening call-to-action (pokud applicable)
   - Final flow optimization
3. **SEO optimization:**
   - Keyword density check a optimization
   - Meta description generation
   - Title SEO optimization (pokud needed)
   - Internal linking suggestions (pokud applicable)
   - Alt text pro images (pokud budou)
4. **Format optimization:**
   - Proper heading hierarchy (H1, H2, H3)
   - Paragraph breaks pro optimal readability
   - List formatting (bullet points, numbered lists)
   - Emphasis (bold, italic) pro key points
5. **Final quality checks:**
   - One last grammar pass
   - Final readability check
   - Consistency verification
   - Brand voice alignment
6. **Metadata preparation:**
   - Publication date/time
   - Categories/tags
   - Author attribution
   - Copyright info
7. **Update Story:**
   - Apply all polishing changes
   - Uložení polished version
   - State změna na "PrismQ.T.Publishing" (modul 20)

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:** Fully polished, publication-ready Story
- **Formát výstupu:** 
  - Databáze (updated Stories s polished content)
  - SEO metadata
  - Publishing metadata
- **Vedlejší efekty:** 
  - Polish improvement metrics
  - SEO scores
  - Final quality scores
- **Chování při chybě:** Manual polish request

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul 18 - expert review s improvement suggestions
- Ollama server
- SEO tools (keyword research, SEO analyzers)
- Databáze

**Výstupní závislosti:**
- Modul 20 (PrismQ.T.Publishing) - publikování Story

---

## 📝 Poznámky / Rizika

**Poznámky:**
- Last opportunity pro content changes před publikací
- Balance mezi improvements a maintaining authenticity
- SEO optimization nesmí compromitovat readability
- Polish by měl být subtle, ne dramatic rewrite
- Focus na high-impact improvements
- Metadata preparation critical pro publishing

**Rizika:**
- **Over-polishing**: Ztráta authenticity a voice
- **SEO over-optimization**: Keyword stuffing, unnatural text
- **Time consumption**: Polish může být time-consuming
- **Subjective improvements**: Co je "better" může být sporné
- **Last-minute errors**: Changes mohou introduce new mistakes

**Doporučení:**
- Light touch - subtle improvements only
- SEO optimization limits (avoid keyword stuffing)
- Final automated checks po polishing
- Human approval pro significant changes
- Version control - keep pre-polish version
- A/B testing polished vs unpolished content
- Track polish impact on engagement metrics
- Implement polish guidelines/checklists
- Time limit on polish phase (avoid perfection paralysis)
