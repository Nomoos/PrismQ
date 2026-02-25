# Module Report Template Solution

## 📋 Problem
The `_meta/reports/` directory contains 30+ module reports, all following the same standardized structure. Each report repeats the same section headers and formatting patterns, making it difficult to ensure consistency when creating new reports or updating existing ones.

## ✅ Solution
Created a centralized template system with comprehensive documentation to ensure all module reports follow the same standardized structure.

## 📁 Files Created

### Core Template Files
1. **`_template.md`** (1.7K)
   - Base template with structure and placeholders
   - Ready to copy and fill in for new modules
   - Contains all required sections with placeholder text

2. **`TEMPLATE_GUIDE.md`** (6.4K)
   - Comprehensive guide for writing reports
   - Detailed explanation of each section
   - Best practices and what to avoid
   - Writing style guidelines
   - Complete checklist

3. **`EXAMPLE_REPORT.md`** (7.8K)
   - Fully filled example report
   - Demonstrates correct usage of all sections
   - Shows proper formatting and style
   - Reference for report structure

4. **`QUICK_REFERENCE.md`** (3.8K)
   - Quick reference card for report writers
   - Section checklist
   - Common patterns and examples
   - Validation checklist
   - Key questions to answer

### Supporting Files
5. **`_includes/` directory**
   - Contains reusable snippets
   - `_section_separator.md` - Standard section separator pattern
   - `README.md` - Documentation for includes

6. **Updated `README.md`** (6.2K)
   - Added references to all template files
   - Documented the template system
   - Clear guidance on using templates

## 🎯 Benefits

### Consistency
- All reports follow identical structure
- Same section headers with emojis (🎯📥⚙️📤🔗📝)
- Standardized subsections within each section
- Uniform formatting patterns

### Ease of Use
- Copy `_template.md` and fill in the blanks
- `EXAMPLE_REPORT.md` shows exactly how it should look
- `QUICK_REFERENCE.md` for fast lookups
- `TEMPLATE_GUIDE.md` for detailed help

### Quality Assurance
- Checklist ensures no sections are missed
- Clear guidelines prevent common mistakes
- Examples show best practices
- Validation steps before submission

### Maintainability
- Central documentation of report structure
- Easy to update all reports if structure changes
- New team members can quickly learn the format
- Consistent documentation across all 30+ modules

## 📖 How to Use

### Creating a New Report
1. Copy `_template.md` to `XX_PrismQ.Module.Name.md`
2. Replace `[MODULE_NAME]` in header
3. Fill in all sections (remove placeholder text)
4. Check `EXAMPLE_REPORT.md` for reference
5. Use `QUICK_REFERENCE.md` for common patterns
6. Validate with checklist in `TEMPLATE_GUIDE.md`

### Updating Existing Reports
1. Compare existing report with `_template.md`
2. Add any missing sections
3. Ensure subsections match template structure
4. Update formatting to match standard
5. Verify cross-references are correct

## 🔍 Template Structure

All reports follow this structure:

```
# Kontrola běhu modulu: [MODULE_NAME]

## 🎯 Účel modulu
[Purpose description]

---

## 📥 Vstupy (Inputs)
- Zdroj vstupu
- Typ dat
- Povinné hodnoty
- Nepovinné hodnoty
- Očekávané předpoklady

---

## ⚙️ Zpracování (Processing)
1. Step 1
2. Step 2
...

---

## 📤 Výstupy (Outputs)
- Primární výstup
- Formát výstupu
- Vedlejší efekty
- Chování při chybě

---

## 🔗 Vazby a závislosti
- Vstupní závislosti
- Výstupní závislosti
- Dokumentace (optional)

---

## 📝 Poznámky / Rizika
- Poznámky
- Rizika
- Doporučení
```

## ✨ Key Features

### Complete Documentation
- Every section explained in detail
- Clear examples for each subsection
- Best practices documented
- Common mistakes highlighted

### Reusable Components
- `_includes/` directory for common patterns
- Standard separator format
- Consistent formatting rules
- Shared conventions

### Multiple Access Levels
- **Quick**: `QUICK_REFERENCE.md` - Fast lookup
- **Example**: `EXAMPLE_REPORT.md` - See it in action
- **Detailed**: `TEMPLATE_GUIDE.md` - Deep dive
- **Template**: `_template.md` - Start here

## 🎓 Learning Path

1. **Beginner**: Start with `EXAMPLE_REPORT.md` to see complete example
2. **Quick Start**: Use `QUICK_REFERENCE.md` for common patterns
3. **Deep Dive**: Read `TEMPLATE_GUIDE.md` for comprehensive understanding
4. **Practice**: Copy `_template.md` and create your own report

## 📊 Impact

### Before
- ❌ Each report writer reinvented structure
- ❌ Inconsistent formatting across reports
- ❌ No central documentation of standards
- ❌ Hard to ensure completeness
- ❌ Time-consuming for new team members

### After
- ✅ Standardized structure for all reports
- ✅ Central template and documentation
- ✅ Clear guidelines and examples
- ✅ Easy validation with checklists
- ✅ Quick onboarding for new writers

## 🔄 Maintenance

### Updating the Template
If report structure needs to change:
1. Update `_template.md` first
2. Update `EXAMPLE_REPORT.md` to match
3. Update `TEMPLATE_GUIDE.md` documentation
4. Update `QUICK_REFERENCE.md` patterns
5. Consider updating existing reports

### Adding New Sections
1. Add to `_template.md` with placeholder
2. Document in `TEMPLATE_GUIDE.md`
3. Show example in `EXAMPLE_REPORT.md`
4. Add to checklist in `QUICK_REFERENCE.md`
5. Update README.md if needed

## 💬 Feedback Loop

The template system is designed to evolve:
- Report writers can suggest improvements
- Common patterns can be extracted to `_includes/`
- New best practices can be documented
- Examples can be expanded

## 🎯 Success Criteria

The solution is successful if:
- ✅ All new reports use the template
- ✅ Reports are consistent in structure
- ✅ Writers find it easy to use
- ✅ Quality of reports improves
- ✅ Time to create reports decreases
- ✅ New team members onboard quickly

## 📝 Notes

- Template is in Czech (matching existing reports)
- Uses emoji icons for visual consistency
- Preserves existing report numbering system
- Compatible with existing reports
- No changes needed to existing reports (template is for new/updated ones)

---

*Solution implemented: 2026-01-02*
*Version: 1.0*
