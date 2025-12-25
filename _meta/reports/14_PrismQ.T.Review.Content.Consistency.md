# Kontrola běhu modulu: PrismQ.T.Review.Content.Consistency

## 🎯 Účel modulu
Kontrola stylové a strukturální konzistence obsahu. Modul validuje, že content má konzistentní formátování, strukturu, naming, a stylistiku napříč celým textem.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Databáze (tabulka Story)
- **Typ dat:** Story objekty ve stavu "PrismQ.T.Review.Content.Consistency"
- **Povinné hodnoty:** Story s content fieldem
- **Nepovinné hodnoty:** `--preview`, `--debug` flags, style guides
- **Očekávané předpoklady:**
  - Stories prošlé modulem 13 (content quality check)
  - Běžící Ollama server
  - Přístup k databázi

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Načtení Stories** - dotaz na stav "PrismQ.T.Review.Content.Consistency"
2. **Consistency checks:**
   - **Naming consistency**: Stejná jména/termíny používány konsistentně
   - **Formatting consistency**: Jednotné formátování (bold, italic, lists)
   - **Structure consistency**: Sekce mají podobnou strukturu
   - **Tense consistency**: Minulý/přítomný/budoucí čas konsistentní
   - **POV consistency**: První/druhá/třetí osoba konsistentní
   - **Capitalization consistency**: Konzistentní kapitalizace
   - **Number format consistency**: Čísla jako cifry vs. slova
3. **Internal reference check:**
   - Cross-references v textu jsou správné
   - Není-li contradictory information
4. **Style guide compliance:**
   - Adherence k style guide (pokud existuje)
5. **Update Story:**
   - Uložení consistency report
   - State změna na "PrismQ.T.Review.Content.Editing" (modul 15)

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:** Story s consistency assessment
- **Formát výstupu:** Databáze (updated Stories), consistency reports
- **Vedlejší efekty:** Consistency metrics, style violations log
- **Chování při chybě:** Auto-fix minor issues, flag major ones

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul 13 - content quality check
- Ollama server, style guides, databáze

**Výstupní závislosti:**
- Modul 15 (PrismQ.T.Review.Content.Editing)

---

## 📝 Poznámky / Rizika

**Poznámky:**
- Některé consistency issues lze auto-fix
- Style guides mohou být complex a detailní
- Internal consistency důležitější než external style guide adherence

**Rizika:**
- Over-correction může ztratit stylistic variety
- Style guide může být příliš rigidní
- False positives při intentional style variations

**Doporučení:**
- Auto-fix pouze obvious issues
- Allow style variations kde appropriate
- Human review pro major consistency issues
