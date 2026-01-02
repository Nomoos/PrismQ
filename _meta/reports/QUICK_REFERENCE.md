# Quick Reference - Module Report Template

## 🚀 Quick Start
1. Copy `_template.md` to new file: `XX_PrismQ.Module.Name.md`
2. Replace `[MODULE_NAME]` with your module name
3. Fill in all sections (remove placeholder text)
4. See `EXAMPLE_REPORT.md` for a complete example
5. Review `TEMPLATE_GUIDE.md` for detailed instructions

## 📋 Section Checklist

### ✅ Required Sections (must have)
- [ ] Header: `# Kontrola běhu modulu: [MODULE_NAME]`
- [ ] 🎯 Účel modulu
- [ ] 📥 Vstupy (Inputs)
  - [ ] Zdroj vstupu
  - [ ] Typ dat
  - [ ] Povinné hodnoty
  - [ ] Nepovinné hodnoty
  - [ ] Očekávané předpoklady
- [ ] ⚙️ Zpracování (Processing)
  - [ ] Numbered steps (1, 2, 3...)
  - [ ] Bold step names
- [ ] 📤 Výstupy (Outputs)
  - [ ] Primární výstup
  - [ ] Formát výstupu
  - [ ] Vedlejší efekty
  - [ ] Chování při chybě
- [ ] 🔗 Vazby a závislosti
  - [ ] Vstupní závislosti
  - [ ] Výstupní závislosti
- [ ] 📝 Poznámky / Rizika
  - [ ] Poznámky
  - [ ] Rizika
  - [ ] Doporučení

### 🔧 Optional Subsections (use when relevant)
- [ ] Dokumentace (in Dependencies section)
- [ ] Klíčové změny (in Notes section)

## 💡 Quick Tips

### Writing Style
- ✅ Clear, concise Czech
- ✅ Technical and specific
- ✅ Include concrete examples
- ❌ Avoid vague descriptions
- ❌ Don't leave placeholder text

### Formatting
- Use `---` to separate major sections
- Use bold `**Text:**` for subsection names
- Use bullet points `-` for lists
- Use numbered lists `1.` for sequential steps
- Use emoji icons as section markers (🎯📥⚙️📤🔗📝)

### Cross-References
- Reference modules by number: "Modul 01", "Modul 20"
- Include full module name: "PrismQ.T.Idea.From.User"
- Link to related docs when applicable

### Common Patterns

**Input sources:**
- `Databáze (tabulka Story)`
- `Uživatel (CLI vstup)`
- `API volání`
- `Soubory na disku`

**Data types:**
- `Text (plain text, JSON)`
- `Story objekty`
- `Audio soubory (WAV, MP3)`
- `Video soubory (MP4)`

**Prerequisites:**
- `Běžící Ollama server`
- `Python 3.12+ environment`
- `Přístup k databázi`
- `Dostupný AI model`

**Processing steps (common):**
1. Inicializace prostředí
2. Načtení dat
3. Zpracování/Generování
4. Validace
5. Uložení výsledků
6. Reportování
7. Cleanup

**Error handling:**
- `RuntimeError - ukončení`
- `Retry mechanismus (3x)`
- `Rollback transakce`
- `Skip a pokračování`
- `Fallback na preview režim`

## 🔍 Validation Checklist

Before submitting:
- [ ] All placeholders replaced (no `[...]` text)
- [ ] Module name correct in header
- [ ] All required sections present
- [ ] Cross-references are correct
- [ ] Dependencies listed both directions
- [ ] No typos or formatting errors
- [ ] Example code (if any) is correct
- [ ] Risks are realistic and actionable
- [ ] Recommendations are helpful

## 📚 Resources

- **Base template**: `_template.md`
- **Detailed guide**: `TEMPLATE_GUIDE.md`
- **Complete example**: `EXAMPLE_REPORT.md`
- **This quick ref**: `QUICK_REFERENCE.md`

## ⚡ Common Mistakes to Avoid

❌ Forgetting to replace `[MODULE_NAME]` in header
❌ Missing prerequisite information
❌ Incomplete error handling documentation
❌ Vague processing steps ("does processing...")
❌ Missing cross-references to related modules
❌ No dependency information
❌ Leaving placeholder text in final version
❌ Inconsistent formatting (mixing styles)

## 🎯 Key Questions to Answer

Your report should answer:
1. What does this module do? (Purpose)
2. What data does it need? (Inputs)
3. How does it work? (Processing)
4. What does it produce? (Outputs)
5. What does it depend on? (Dependencies)
6. What could go wrong? (Risks)
7. How to use it best? (Recommendations)

---

*Quick reference version: 1.0*
*Last updated: 2026-01-02*
