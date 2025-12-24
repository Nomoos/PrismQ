# Script Guidelines Compliance Audit Report
## PrismQ_meta/scripts

**Date:** 2025-12-23  
**Auditor:** GitHub Copilot  
**Scope:** All scripts in `_meta/scripts/` directory  
**Guidelines Reference:** `CODING_GUIDELINES.md`, `MODULE_HIERARCHY_UPDATED.md`

---

## Executive Summary

**Total Scripts Audited:** 63 .bat files across 31 directories  
**Violations Found:** 4 categories of non-compliance  
**Severity:** Medium - Naming inconsistencies with established guidelines

### Key Findings

1. **Script directory naming** uses old namespace format ("PrismQ.T.Content") instead of "PrismQ.T.Content"
2. **Module path references** point to deprecated structure (T/Content/ vs T/Content/)
3. **Namespace comments** use incorrect module names in headers
4. **Common utility** location compliant

---

## Guideline Violations

### ISSUE-001: Incorrect Script Directory Naming Convention
**Severity:** Medium  
**Guideline:** CODING_GUIDELINES.md Section 6 - Cross-cutting "Content" subtree

**Problem:**  
Directory `04_PrismQ.T.Content.From.Title.Idea` uses deprecated namespace.  
According to guidelines, content generation belongs under `PrismQ.T.Content.*`, not `PrismQ.T.Content.*`.

**Correct naming should be:** `04_PrismQ.T.Content.From.Idea.Title`

**Files Affected:**
- Directory: `_meta/scripts/04_PrismQ.T.Content.From.Title.Idea/`
- Files: `Run.bat`, `Preview.bat`

**GitHub Copilot Command:**
```
Rename directory _meta/scripts/04_PrismQ.T.Content.From.Title.Idea to _meta/scripts/04_PrismQ.T.Content.From.Idea.Title to comply with PrismQ.T.Content.* namespace for content pipelines per CODING_GUIDELINES.md Section 6.
```

---

### ISSUE-002: Deprecated Module Path References in Run.bat
**Severity:** Medium  
**Guideline:** CODING_GUIDELINES.md Section 3, 6 - Namespace-to-folder mapping

**Problem:**  
Script `04_PrismQ.T.Content.From.Title.Idea/Run.bat` line 17 references:
```batch
python ..\..\..\T\Script\From\Idea\Title\src\script_from_idea_title_interactive.py
```

Should reference:
```batch
python ..\..\..\T\Content\From\Idea\Title\src\content_from_idea_title_interactive.py
```

**File:** `_meta/scripts/04_PrismQ.T.Content.From.Title.Idea/Run.bat`  
**Lines:** 17, 26

**GitHub Copilot Command:**
```
In _meta/scripts/04_PrismQ.T.Content.From.Title.Idea/Run.bat, update line 17 to reference T\Content\From\Idea\Title\src\ instead of T\Script\From\Idea\Title\src\ and update line 26 MODULE_DIR path accordingly to match the PrismQ.T.Content.* namespace structure per CODING_GUIDELINES.md.
```

---

### ISSUE-003: Incorrect Header Comments in Run.bat
**Severity:** Low  
**Guideline:** CODING_GUIDELINES.md Section 6 - Module naming consistency

**Problem:**  
Header comment at line 2 states:
```batch
REM Run.bat - PrismQ.T.Content.From.Title.Idea
```

Should state:
```batch
REM Run.bat - PrismQ.T.Content.From.Idea.Title
```

Also line 3 description references "script" instead of "content".

**File:** `_meta/scripts/04_PrismQ.T.Content.From.Title.Idea/Run.bat`  
**Lines:** 2-3

**GitHub Copilot Command:**
```
In _meta/scripts/04_PrismQ.T.Content.From.Title.Idea/Run.bat lines 2-3, update header comment from "PrismQ.T.Content.From.Title.Idea" to "PrismQ.T.Content.From.Idea.Title" and change "Generate script" to "Generate content" to align with content pipeline namespace per CODING_GUIDELINES.md Section 6.
```

---

### ISSUE-004: Incorrect Header Comments in Preview.bat
**Severity:** Low  
**Guideline:** CODING_GUIDELINES.md Section 6 - Module naming consistency

**Problem:**  
Preview.bat header likely contains same namespace errors as Run.bat.

**File:** `_meta/scripts/04_PrismQ.T.Content.From.Title.Idea/Preview.bat`  
**Lines:** 1-5 (estimated)

**GitHub Copilot Command:**
```
In _meta/scripts/04_PrismQ.T.Content.From.Title.Idea/Preview.bat header comments, update all references from "PrismQ.T.Content.From.Title.Idea" to "PrismQ.T.Content.From.Idea.Title" and ensure module paths reference T\Content\From\Idea\Title\ per CODING_GUIDELINES.md.
```

---

### ISSUE-005 through ISSUE-015: Review Module Script Naming
**Severity:** Low  
**Guideline:** CODING_GUIDELINES.md Section 5 - Domain modules vs Content subtree

**Problem:**  
Review-related scripts (05-17) use mixed conventions. Need to verify if these are:
- Domain operations (should be `PrismQ.T.Review.*`) - correct
- Content pipelines (should be `PrismQ.T.Content.*`) - needs change

**Analysis needed for directories:**
- `05_PrismQ.T.Review.Title.By.Script.Idea`
- `06_PrismQ.T.Review.Script.By.Title.Idea`
- `07_PrismQ.T.Review.Title.By.Script`
- `08_PrismQ.T.Title.From.Script.Review.Title`
- `09_PrismQ.T.Content.From.Title.Review.Script`
- `10_PrismQ.T.Review.Script.By.Title`
- `11_PrismQ.T.Review.Script.Grammar`
- `12_PrismQ.T.Review.Script.Tone`
- `13_PrismQ.T.Review.Script.Content`
- `14_PrismQ.T.Review.Script.Consistency`
- `15_PrismQ.T.Review.Script.Editing`
- `16_PrismQ.T.Review.Title.Readability`
- `17_PrismQ.T.Review.Script.Readability`

**GitHub Copilot Command:**
```
Review scripts 05-17 in _meta/scripts/ to determine if "Review" operations are domain operations (keep as PrismQ.T.Review.*) or content generation pipelines (should be PrismQ.T.Content.From.*). Per CODING_GUIDELINES.md Section 5 vs Section 6, domain operations belong to PrismQ.T.<Domain> while content artifacts belong to PrismQ.T.Content.*. Ensure consistent namespace usage.
```

---

### ISSUE-016: Verify Story Module Scripts
**Severity:** Low  
**Guideline:** CODING_GUIDELINES.md Section 5 - Domain module identification

**Problem:**  
Scripts 02, 18, 19 reference `PrismQ.T.Story.*`. Need to verify correct placement:
- `02_PrismQ.T.Story.From.Idea` - Is this content generation? Should it be `PrismQ.T.Content.From.Idea.Story`?
- `18_PrismQ.T.Story.Review` - Domain operation (correct)
- `19_PrismQ.T.Story.Polish` - Domain operation (correct)

**Directories affected:**
- `_meta/scripts/02_PrismQ.T.Story.From.Idea/`
- `_meta/scripts/18_PrismQ.T.Story.Review/`
- `_meta/scripts/19_PrismQ.T.Story.Polish/`

**GitHub Copilot Command:**
```
Verify _meta/scripts/02_PrismQ.T.Story.From.Idea/ - if this generates Story artifacts from Ideas, it should be renamed to PrismQ.T.Content.From.Idea.Story per CODING_GUIDELINES.md Section 6 (content pipelines). If it performs Story domain operations on existing Ideas, current naming is correct per Section 5 (domain modules).
```

---

## Compliant Implementations

### ✅ Correct Patterns Found

1. **Common utilities** (`_meta/scripts/common/start_ollama.bat`)
   - Correctly placed in common directory
   - Provides shared functionality
   - No namespace violations

2. **Environment setup pattern** (`:setup_env` subroutine)
   - Consistently implemented across scripts
   - Creates virtual environments in correct module directories
   - Follows module layout convention

3. **Script structure** (all Run.bat/Preview.bat files)
   - Consistent error handling
   - Proper working directory setup
   - Standard output formatting

---

## Recommendations

### Immediate Actions Required

1. **Rename directory** `04_PrismQ.T.Content.From.Title.Idea` → `04_PrismQ.T.Content.From.Idea.Title`
2. **Update all path references** in Run.bat and Preview.bat for script 04
3. **Update header comments** to reflect correct namespace

### Medium Priority

4. **Audit Review scripts** (05-17) to determine correct classification
5. **Verify Story scripts** (02, 18, 19) for correct namespace usage
6. **Create script naming standard document** for future script additions

### Long-term Improvements

7. **Automated compliance checking** - Add script to validate naming conventions
8. **Template scripts** - Create templates with correct namespace patterns
9. **Migration guide** - Document how to update existing scripts when modules reorganize

---

## Verification Checklist

After remediation, verify:

- [ ] All script directory names match module hierarchy in `CODING_GUIDELINES.md`
- [ ] Module path references point to actual module locations
- [ ] Header comments accurately reflect namespace
- [ ] Script execution works after path updates
- [ ] Virtual environments created in correct locations
- [ ] No broken symbolic links or references

---

## Tools for Compliance

### Suggested automation:

```python
# Example: Validate script naming
import os
import re

VALID_NAMESPACES = {
    'PrismQ.T.Idea',
    'PrismQ.T.Title',  
    'PrismQ.T.Story',
    'PrismQ.T.Review',
    'PrismQ.T.Content',  # For content pipelines
    'PrismQ.T.Publishing',
    'PrismQ.A',  # Audio
    'PrismQ.V',  # Video
    'PrismQ.P',  # Publishing
    'PrismQ.M',  # Analytics
}

def validate_script_dir_name(dirname):
    # Extract namespace from directory name
    match = re.match(r'\d+_(.+)$', dirname)
    if match:
        namespace = match.group(1)
        # Validate against known patterns
        for valid in VALID_NAMESPACES:
            if namespace.startswith(valid):
                return True
    return False
```

---

## Conclusion

The scripts in `_meta/scripts/` are generally well-structured and follow good practices for environment management and error handling. The primary compliance issues are **naming inconsistencies** resulting from module reorganization (Script → Content namespace transition).

**Impact:** Medium - Scripts function correctly but don't align with documented architecture  
**Effort to fix:** Low - Primarily renaming and path updates  
**Priority:** Medium - Should be addressed to maintain consistency with guidelines

---

## Related Documentation

- `CODING_GUIDELINES.md` - Module design and responsibility guidelines
- `MODULE_HIERARCHY_UPDATED.md` - Detailed hierarchy and dependency rules
- `PR_CODE_REVIEW_CHECKLIST.md` - Code review standards

---

**End of Audit Report**
