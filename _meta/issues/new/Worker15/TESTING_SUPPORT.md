# Worker15 - Testing & Support Documentation

**Purpose**: Guidelines for documentation testing, validation, and support  
**Owner**: Worker15  
**Created**: 2025-11-23  
**Status**: Active

---

## Documentation Testing

### Pre-Publication Checklist

#### Content Validation
- [ ] **Accuracy**: All technical information is correct
- [ ] **Completeness**: All necessary information is included
- [ ] **Clarity**: Language is clear and unambiguous
- [ ] **Examples**: All code examples work correctly
- [ ] **Links**: All cross-references and links are valid
- [ ] **Images**: All diagrams and screenshots are up-to-date

#### Structure Validation
- [ ] **Headers**: Proper heading hierarchy (H1 → H2 → H3)
- [ ] **Navigation**: Clear navigation paths to related docs
- [ ] **Formatting**: Consistent markdown formatting
- [ ] **Code Blocks**: Proper syntax highlighting
- [ ] **Tables**: Well-formatted and readable
- [ ] **Lists**: Proper list formatting (ordered/unordered)

#### Style Validation
- [ ] **Tone**: Consistent professional tone
- [ ] **Terminology**: Consistent use of technical terms
- [ ] **Voice**: Active voice preferred
- [ ] **Tense**: Present tense for descriptions
- [ ] **Spelling**: No spelling errors
- [ ] **Grammar**: Proper grammar and punctuation

---

## Testing Procedures

### 1. Link Validation

**Purpose**: Ensure all documentation links work correctly

**Process**:
```bash
# Check for broken links in markdown files
cd /home/runner/work/PrismQ/PrismQ

# Find all markdown files
find . -name "*.md" -type f | grep -v ".git" | grep -v "node_modules"

# Manually verify key navigation links:
# - Main README → Module READMEs
# - Module READMEs → Submodule docs
# - Cross-references between modules
# - Links to _meta documentation
```

**Validation Checklist**:
- [ ] Main README links to all modules (T, A, V, P, M, Client, EnvLoad)
- [ ] Module READMEs link to submodules
- [ ] Worker READMEs link to related workers
- [ ] Cross-module references work
- [ ] _meta documentation links work
- [ ] External links are valid (if any)

### 2. Code Example Testing

**Purpose**: Verify all code examples work as documented

**Process**:
```python
# Test Python examples in documentation
# Example: Testing namespace imports

from PrismQ.T import Idea, Script, Title
from PrismQ.A import Voiceover, Publishing
from PrismQ.V import Scene, Keyframe

# Verify examples match actual code structure
```

**Validation Checklist**:
- [ ] Import statements work
- [ ] Example code is syntactically correct
- [ ] Examples use correct API calls
- [ ] Examples reflect current implementation
- [ ] Examples include necessary error handling

### 3. Documentation Consistency Testing

**Purpose**: Ensure consistency across all documentation

**Test Areas**:

#### Module Structure Consistency
```bash
# Verify all modules follow the same README structure:
# 1. Title with namespace
# 2. Purpose section
# 3. Modules/Components section
# 4. Navigation section
# 5. Related modules section

# Check each module:
cat T/README.md | grep -E "^#|^##"
cat A/README.md | grep -E "^#|^##"
cat V/README.md | grep -E "^#|^##"
cat P/README.md | grep -E "^#|^##"
cat M/README.md | grep -E "^#|^##"
```

**Validation Checklist**:
- [ ] All module READMEs have consistent structure
- [ ] All modules use consistent heading levels
- [ ] All modules have purpose sections
- [ ] All modules have navigation sections
- [ ] Terminology is consistent across modules

#### Namespace Consistency
- [ ] Python namespace examples match actual structure
- [ ] Module namespaces are correct (PrismQ.T, PrismQ.A, etc.)
- [ ] Import examples are accurate

### 4. Navigation Testing

**Purpose**: Verify users can navigate documentation easily

**User Journeys to Test**:

1. **New User Journey**:
   - Start: Main README
   - Goal: Understand T module workflow
   - Path: Main README → T/README.md → T/TITLE_SCRIPT_WORKFLOW.md
   - [ ] All links work
   - [ ] Information flow is logical
   - [ ] No dead ends

2. **Developer Journey**:
   - Start: Main README
   - Goal: Implement new feature in T.Script
   - Path: Main README → T/README.md → T/Script/README.md → API docs
   - [ ] All links work
   - [ ] Technical details are accessible
   - [ ] Examples are available

3. **Worker Journey**:
   - Start: Main README
   - Goal: Understand Worker15 responsibilities
   - Path: Main README → Workers README → Worker15/README.md
   - [ ] All links work
   - [ ] Role is clear
   - [ ] Collaboration patterns are documented

### 5. Documentation Freshness Testing

**Purpose**: Ensure documentation reflects current implementation

**Validation Process**:
```bash
# Check for outdated status markers
grep -r "Coming Soon" ./_meta/ --include="*.md"
grep -r "To Be Implemented" ./ --include="*.md"
grep -r "TODO" ./_meta/ --include="*.md"

# Verify implementation status matches reality
```

**Validation Checklist**:
- [ ] Status markers are accurate
- [ ] Feature descriptions match implementation
- [ ] Deprecated features are marked
- [ ] New features are documented
- [ ] Version numbers are current

---

## Support Procedures

### Documentation Issue Response

#### Issue Classification

**Priority Levels**:

1. **Critical** (Fix within 1 day):
   - Broken links in main navigation
   - Incorrect API documentation causing errors
   - Security information that's wrong
   - Major factual errors

2. **High** (Fix within 2-3 days):
   - Missing required documentation
   - Confusing or unclear critical sections
   - Broken links in module documentation
   - Outdated major feature documentation

3. **Medium** (Fix within 1 week):
   - Minor factual errors
   - Formatting issues
   - Missing examples
   - Navigation improvements

4. **Low** (Fix within sprint):
   - Typos
   - Minor formatting improvements
   - Additional examples
   - Style improvements

#### Response Process

1. **Acknowledge**: Respond within 24 hours
2. **Assess**: Determine priority level
3. **Plan**: Create fix plan
4. **Execute**: Make necessary changes
5. **Review**: Get review from relevant workers
6. **Deploy**: Commit and announce changes
7. **Close**: Verify issue is resolved

### Common Documentation Issues

#### Issue: Broken Links
**Solution**:
```bash
# Find and fix broken links
# 1. Identify broken link
# 2. Check if target file was moved/renamed
# 3. Update link or restore target file
# 4. Verify fix
# 5. Check for other instances of same link
```

#### Issue: Outdated Examples
**Solution**:
```bash
# Update code examples
# 1. Test current example
# 2. If it fails, check current API
# 3. Update example to match current API
# 4. Test updated example
# 5. Update documentation
```

#### Issue: Inconsistent Terminology
**Solution**:
```bash
# Standardize terminology
# 1. Identify all variations of term
# 2. Choose standard term
# 3. Update all instances
# 4. Add to style guide
# 5. Verify consistency
```

#### Issue: Missing Documentation
**Solution**:
```bash
# Add missing documentation
# 1. Identify what's missing
# 2. Research implementation
# 3. Draft documentation
# 4. Review with module owner
# 5. Publish documentation
```

---

## Documentation Maintenance Schedule

### Daily Tasks
- Monitor for documentation issues
- Respond to documentation questions
- Quick fixes for critical issues
- Review documentation PRs

### Weekly Tasks
- Link validation sweep
- Update status markers
- Review recently changed code for doc updates
- Update changelog if needed

### Sprint Tasks
- Complete planned documentation updates
- Document new features
- Update API documentation
- Review all module READMEs
- Update worker documentation

### Monthly Tasks
- Full documentation audit
- Consistency check across all modules
- Example code validation
- Navigation testing
- User feedback review

---

## Documentation Quality Metrics

### Coverage Metrics
- **Module Documentation**: 100% of modules have READMEs
- **API Documentation**: 100% of public APIs documented
- **Example Coverage**: All major features have examples
- **Diagram Coverage**: All workflows have diagrams

### Quality Metrics
- **Link Validity**: 100% of links work
- **Example Validity**: 100% of examples work
- **Consistency Score**: 95%+ consistent terminology
- **Freshness Score**: 95%+ documentation is current

### User Metrics
- **Find Time**: Users find needed info within 3 clicks
- **Clarity Score**: 90%+ users understand documentation
- **Completeness**: 95%+ of user questions answered by docs
- **Issue Rate**: <5 documentation issues per sprint

---

## Testing Tools and Scripts

### Link Checker Script
```bash
#!/bin/bash
# check_links.sh - Validate documentation links

echo "Checking documentation links..."

broken_count=0

# Find all markdown files (handling filenames with spaces and special characters)
find . -name "*.md" -type f -print0 | grep -zv ".git" | while IFS= read -r -d '' file; do
    echo "Checking: $file"
    
    # Extract markdown links [text](path)
    grep -o '\[.*\]([^)]*)' "$file" | while IFS= read -r link; do
        path=$(echo "$link" | sed 's/.*(\(.*\))/\1/')
        
        # Check if it's a relative link
        if [[ ! $path =~ ^https?:// ]]; then
            dir=$(dirname "$file")
            target="$dir/$path"
            
            if [ ! -f "$target" ] && [ ! -d "$target" ]; then
                echo "  BROKEN: $link in $file"
                ((broken_count++))
            fi
        fi
    done
done

echo "Link check complete! Found $broken_count broken links."
exit $broken_count
```

### Example Validator Script
```python
#!/usr/bin/env python3
# validate_examples.py - Test code examples in documentation

import re
import ast
import sys
import os
from pathlib import Path

def extract_python_code(markdown_file):
    """Extract Python code blocks from markdown."""
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find Python code blocks
    pattern = r'```python\n(.*?)\n```'
    code_blocks = re.findall(pattern, content, re.DOTALL)
    return code_blocks

def validate_syntax(code):
    """Check if Python code is syntactically valid."""
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, str(e)

def main():
    """Check all markdown files for Python examples."""
    print("Validating Python examples in documentation...")
    
    errors = []
    validated = 0
    
    # Find all markdown files
    for md_file in Path('.').rglob('*.md'):
        if '.git' in str(md_file):
            continue
            
        code_blocks = extract_python_code(md_file)
        
        for i, code in enumerate(code_blocks, 1):
            validated += 1
            is_valid, error = validate_syntax(code)
            
            if not is_valid:
                errors.append({
                    'file': str(md_file),
                    'block': i,
                    'error': error
                })
                print(f"  ❌ {md_file} - Block {i}: {error}")
            else:
                print(f"  ✅ {md_file} - Block {i}: Valid")
    
    print(f"\nValidation complete!")
    print(f"  Total blocks validated: {validated}")
    print(f"  Errors found: {len(errors)}")
    
    return len(errors)

if __name__ == '__main__':
    sys.exit(main())
```

---

## Best Practices

### Writing Effective Documentation

1. **Start with the User**: Write for your audience
2. **Be Concise**: Say more with fewer words
3. **Use Examples**: Show, don't just tell
4. **Be Consistent**: Follow style guide
5. **Stay Current**: Update as code changes
6. **Test Everything**: Verify links and examples
7. **Get Feedback**: Review with users
8. **Iterate**: Continuously improve

### Common Pitfalls to Avoid

- ❌ Writing for yourself instead of users
- ❌ Assuming prior knowledge
- ❌ Using jargon without explanation
- ❌ Forgetting to update after code changes
- ❌ No examples or outdated examples
- ❌ Broken links and references
- ❌ Inconsistent terminology
- ❌ Poor structure and navigation

### Documentation Success Factors

- ✅ Clear, specific, actionable content
- ✅ Easy to navigate and find information
- ✅ Working examples for all features
- ✅ Consistent style and terminology
- ✅ Always up-to-date
- ✅ Validated and tested
- ✅ User feedback incorporated
- ✅ Regular maintenance schedule

---

## Resources

### Documentation Tools
- **Markdown Preview**: VS Code, Markdown Preview Enhanced
- **Link Checkers**: markdown-link-check, linkchecker
- **Spell Checkers**: VS Code Spell Checker, aspell
- **Diagram Tools**: Mermaid, PlantUML, draw.io

### Style Guides
- **Microsoft Writing Style Guide**: Technical writing reference
- **Google Developer Documentation Style Guide**: API documentation
- **Write the Docs**: Documentation best practices
- **Markdown Guide**: Markdown syntax reference

### Testing Resources
- **Example Testing**: doctest, pytest for examples
- **Link Validation**: markdown-link-check, linkchecker
- **Spell Checking**: aspell, hunspell
- **Grammar Checking**: LanguageTool, Grammarly

---

**Maintained By**: Worker15  
**Review Schedule**: Monthly  
**Next Review**: End of Sprint 4  
**Version**: 1.0
