# Template Guide for Module Reports

## 📋 Purpose
This template provides a standardized structure for documenting module behavior and data flow in the PrismQ pipeline.

## 🎯 When to Use
Use this template when:
- Creating documentation for a new module
- Updating existing module documentation
- Ensuring consistency across all module reports

## 📂 Template Files
- **`_template.md`** - Base template with structure and placeholders
- **`TEMPLATE_GUIDE.md`** (this file) - Detailed guide for writing reports
- **`_includes/`** - Directory with reusable snippets for common formatting patterns

## 📖 Template Structure

### 1. Header
```markdown
# Kontrola běhu modulu: [MODULE_NAME]
```
- Replace `[MODULE_NAME]` with the full module path (e.g., `PrismQ.T.Idea.From.User`)

### 2. 🎯 Účel modulu (Purpose)
Describe:
- What the module does (high-level overview)
- Why it exists in the pipeline
- Its role in the overall system

### 3. 📥 Vstupy (Inputs)
Document all inputs:

**Zdroj vstupu:** Where data comes from
- Examples: Databáze (tabulka Story), Uživatel (CLI), API volání

**Typ dat:** Data types and formats
- Examples: Text, Story objekty, JSON, Audio files

**Povinné hodnoty:** Required inputs (must be present)
- List each required field/parameter
- Include validation requirements

**Nepovinné hodnoty:** Optional inputs
- List flags (--preview, --debug)
- List optional parameters with defaults

**Očekávané předpoklady:** Prerequisites
- System dependencies (Ollama server, Python environment)
- Data prerequisites (existing records in database)
- Service availability requirements

### 4. ⚙️ Zpracování (Processing)
Step-by-step processing flow:
1. **Initialization:** Environment setup, connection establishment
2. **Data Loading:** How data is loaded and validated
3. **Processing:** Core logic, transformations, AI calls
4. **Validation:** Quality checks, error handling
5. **Output Generation:** How outputs are created
6. **Storage:** How results are persisted
7. **Cleanup:** Resource cleanup, connection closing

**Tips:**
- Number each major step
- Use bold for step names
- Include sub-steps with bullet points or indentation
- Mention continuous mode, preview mode behavior
- Document error handling at each critical step

### 5. 📤 Výstupy (Outputs)
Document all outputs:

**Primární výstup:** Main deliverable of the module
- What is the core result?
- Where is it stored/sent?

**Formát výstupu:** Output format and structure
- Console output format
- Database schema changes
- File formats (JSON, CSV, audio, video)
- API responses

**Vedlejší efekty:** Side effects
- Created files/directories
- Database updates
- Service state changes
- Log files
- Metrics/statistics

**Chování při chybě:** Error behavior
- What happens on different error types?
- Rollback behavior
- Retry logic
- User notifications

### 6. 🔗 Vazby a závislosti (Dependencies)

**Vstupní závislosti:** What this module depends on
- Previous modules in pipeline (with module numbers)
- External services (Ollama, APIs)
- System dependencies (Python, libraries)
- Database tables/schemas
- Configuration files

**Výstupní závislosti:** What depends on this module
- Next modules in pipeline (with module numbers)
- Database tables populated
- Files created for downstream use

### 7. 📝 Poznámky / Rizika (Notes/Risks)

**Poznámky:** Implementation notes
- Key design decisions
- Performance characteristics
- Mode variations (preview, continuous)
- Recent changes or improvements
- Important configuration options

**Rizika:** Potential risks and issues
- **Risk name:** Description and impact
- Include severity level if applicable
- AI availability, database locks, memory consumption, etc.

**Doporučení:** Recommendations
- Best practices for using the module
- Monitoring suggestions
- Performance optimization tips
- Testing recommendations

## 💡 Best Practices

### Writing Style
- Use clear, concise Czech language
- Be specific and technical
- Include concrete examples
- Use consistent terminology
- Reference other modules by number and name

### Formatting
- Use emoji icons as section markers (consistent with template)
- Use bold for emphasis on key terms
- Use code blocks for technical references
- Use bullet points for lists
- Use numbered lists for sequential steps

### Content Guidelines
- **Be comprehensive:** Cover all important aspects
- **Be accurate:** Ensure technical details are correct
- **Be current:** Update when module changes
- **Be helpful:** Include context that aids understanding
- **Cross-reference:** Link to related modules, docs

### What to Include
✅ All input parameters and their validation rules
✅ Complete processing steps (even if obvious)
✅ All outputs and side effects
✅ Error handling behavior
✅ Dependencies (both directions)
✅ Performance characteristics
✅ Known limitations and risks

### What to Avoid
❌ Vague descriptions ("does some processing")
❌ Outdated information
❌ Incomplete error scenarios
❌ Missing cross-references
❌ Implementation details that change frequently

## 🔄 Updating Reports

When updating an existing report:
1. Check if structure matches current template
2. Add missing sections if needed
3. Update outdated information
4. Verify all cross-references are correct
5. Update "Poznámky" section with recent changes
6. Keep "Rizika" section current with known issues

## 📚 Examples

**Template Example:**
- **`EXAMPLE_REPORT.md`** - Complete example using the template with all sections filled

**Real Module Reports:**
- `01_PrismQ.T.Idea.From.User.md` - Complex module with AI integration
- `02_PrismQ.T.Story.From.Idea.md` - Simple transformation module
- `20_PrismQ.T.Publishing.md` - Multi-output publishing module
- `30_PrismQ.M.Analytics.md` - Analytics and reporting module

## ✅ Checklist

Before finalizing a report, verify:
- [ ] Module name is correct in header
- [ ] Purpose section explains why module exists
- [ ] All inputs are documented with types and requirements
- [ ] Processing steps are complete and in order
- [ ] All outputs and side effects are listed
- [ ] Dependencies are bidirectional (input and output)
- [ ] Risks section covers main concerns
- [ ] Recommendations provide actionable advice
- [ ] Cross-references to other modules are correct
- [ ] No placeholder text remains (e.g., [TODO])

---

*Template version: 1.0*
*Last updated: 2026-01-02*
