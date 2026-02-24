# Enforcement Strategies for Layered Architecture

**Date**: 2025-11-14  
**Purpose**: Research approaches to enforce architectural conventions

## Overview

This document explores strategies for enforcing layered architecture conventions in PrismQ.T.Idea.Inspiration, ranging from manual processes to automated tooling.

## 1. Manual Enforcement

### 1.1 Code Reviews

**Approach**: Human reviewers check for architectural violations during PR reviews

**Strengths**:
- ✅ Flexible and context-aware
- ✅ Can catch nuanced violations
- ✅ Educational for team members
- ✅ No tooling required

**Weaknesses**:
- ❌ Time-consuming
- ❌ Inconsistent (depends on reviewer knowledge)
- ❌ Can miss violations
- ❌ Doesn't scale well

**Implementation**:
- Create architecture review checklist in PR template
- Train reviewers on layer boundaries
- Require architecture sign-off for certain changes

**Recommendation**: ✅ **Use as primary enforcement** with automated support

---

### 1.2 Architecture Decision Records (ADRs)

**Approach**: Document architectural decisions for future reference

**Strengths**:
- ✅ Creates institutional knowledge
- ✅ Explains "why" behind decisions
- ✅ Helps onboarding
- ✅ Living documentation

**Weaknesses**:
- ❌ Requires discipline to maintain
- ❌ Can become outdated
- ❌ Doesn't prevent violations

**Implementation**:
- ✅ Created ADR template
- ✅ Created ADR-001 for layered architecture
- Create ADRs for future decisions

**Recommendation**: ✅ **Essential foundation** - already implemented

---

### 1.3 Documentation and Guidelines

**Approach**: Provide clear documentation on conventions

**Strengths**:
- ✅ Self-service learning
- ✅ Reduces questions
- ✅ Consistent reference
- ✅ Can include examples

**Weaknesses**:
- ❌ Developers must read it
- ❌ Can become outdated
- ❌ Doesn't enforce compliance

**Implementation**:
- ✅ SOLID_PRINCIPLES.md created
- ✅ ADR-001 created
- Create CODING_CONVENTIONS.md
- Create CODE_REVIEW_GUIDELINES.md
- Update CONTRIBUTING.md

**Recommendation**: ✅ **Essential** - in progress

---

## 2. Static Analysis

### 2.1 Import Linting

**Approach**: Check import statements to verify dependency direction

**Tools Available**:
- **import-linter** - Python tool specifically for checking import rules
- **pylint** - General linter with import checking
- **flake8-import-order** - Import order checking

**Example with import-linter**:

```toml
# .import-linter.toml
[importlinter]
root_package = "prismq"

[[importlinter.contracts]]
name = "Model has no dependencies"
type = "forbidden"
source_modules = ["prismq.Model"]
forbidden_modules = [
    "prismq.Source",
    "prismq.Classification",
    "prismq.Scoring",
    "prismq.ConfigLoad",
]

[[importlinter.contracts]]
name = "ConfigLoad has no dependencies"
type = "forbidden"
source_modules = ["prismq.ConfigLoad"]
forbidden_modules = [
    "prismq.Source",
    "prismq.Model",
    "prismq.Classification",
    "prismq.Scoring",
]

[[importlinter.contracts]]
name = "Sources cannot depend on processing"
type = "forbidden"
source_modules = ["prismq.Source"]
forbidden_modules = [
    "prismq.Classification",
    "prismq.Scoring",
]

[[importlinter.contracts]]
name = "Classification and Scoring are independent"
type = "independence"
modules = [
    "prismq.Classification",
    "prismq.Scoring",
]
```

**Strengths**:
- ✅ Catches violations automatically
- ✅ Fast and reliable
- ✅ Can run in CI/CD
- ✅ Clear error messages

**Weaknesses**:
- ❌ Only checks imports, not runtime behavior
- ❌ May need configuration per module
- ❌ Can have false positives

**Recommendation**: ✅ **Highly Recommended** for future implementation

---

### 2.2 Pylint Custom Checks

**Approach**: Configure pylint to check architectural rules

**Example Configuration**:

```ini
# .pylintrc
[MASTER]
init-hook='import sys; sys.path.append(".")'

[DESIGN]
max-parents=3
max-attributes=10

[IMPORTS]
# Disallow certain imports
forbidden-import=prismq.Classification:prismq.Scoring,
                 prismq.Scoring:prismq.Classification,
                 prismq.Model:prismq.Source,
                 prismq.Model:prismq.Classification,
                 prismq.ConfigLoad:prismq.Model
```

**Strengths**:
- ✅ Integrated with existing linting
- ✅ Many built-in checks
- ✅ Configurable

**Weaknesses**:
- ❌ Configuration can be complex
- ❌ Not designed specifically for architecture
- ❌ May not catch all violations

**Recommendation**: ⚠️ **Optional** - import-linter is better for architecture

---

### 2.3 Custom Python Scripts

**Approach**: Write custom scripts to check architecture rules

**Example**:

```python
#!/usr/bin/env python3
"""Check architectural dependencies."""

import ast
import sys
from pathlib import Path
from typing import List, Set

LAYERS = {
    "ConfigLoad": {"allowed_deps": set()},
    "Model": {"allowed_deps": {"ConfigLoad"}},
    "Source": {"allowed_deps": {"Model", "ConfigLoad"}},
    "Classification": {"allowed_deps": {"Model", "ConfigLoad"}},
    "Scoring": {"allowed_deps": {"Model", "ConfigLoad"}},
}

def extract_imports(file_path: Path) -> Set[str]:
    """Extract module imports from a Python file."""
    with open(file_path) as f:
        tree = ast.parse(f.read())
    
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    
    return imports

def check_layer_dependencies(root: Path) -> List[str]:
    """Check for architectural violations."""
    violations = []
    
    for layer, config in LAYERS.items():
        layer_path = root / layer
        if not layer_path.exists():
            continue
        
        for py_file in layer_path.rglob("*.py"):
            imports = extract_imports(py_file)
            
            # Check for disallowed imports
            for imp in imports:
                if imp in LAYERS and imp not in config["allowed_deps"]:
                    violations.append(
                        f"{layer} cannot import {imp}: {py_file}"
                    )
    
    return violations

if __name__ == "__main__":
    root = Path(__file__).parent.parent
    violations = check_layer_dependencies(root)
    
    if violations:
        print("❌ Architecture violations found:")
        for v in violations:
            print(f"  - {v}")
        sys.exit(1)
    else:
        print("✅ No architecture violations found")
        sys.exit(0)
```

**Strengths**:
- ✅ Fully customizable
- ✅ Can check complex rules
- ✅ No external dependencies
- ✅ Easy to understand

**Weaknesses**:
- ❌ Need to maintain custom code
- ❌ May miss edge cases
- ❌ Reinventing the wheel

**Recommendation**: ⚠️ **Optional** - Use if import-linter insufficient

---

## 3. Testing-Based Enforcement

### 3.1 Architectural Tests

**Approach**: Write tests that verify architectural constraints

**Example**:

```python
# tests/test_architecture.py
import importlib
import pkgutil
import pytest

def test_model_has_no_dependencies():
    """Model module should not import other PrismQ modules."""
    import Model
    
    forbidden = ['Source', 'Classification', 'Scoring', 'ConfigLoad']
    
    # Check all submodules
    for importer, modname, ispkg in pkgutil.walk_packages(
        path=Model.__path__,
        prefix=Model.__name__ + '.',
    ):
        module = importlib.import_module(modname)
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if hasattr(attr, '__module__'):
                for forbidden_module in forbidden:
                    assert not attr.__module__.startswith(forbidden_module), \
                        f"Model imports from {forbidden_module}"

def test_classification_scoring_independence():
    """Classification and Scoring should not depend on each other."""
    import Classification
    
    # Classification should not import Scoring
    for importer, modname, ispkg in pkgutil.walk_packages(
        path=Classification.__path__,
        prefix=Classification.__name__ + '.',
    ):
        module = importlib.import_module(modname)
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if hasattr(attr, '__module__'):
                assert not attr.__module__.startswith('Scoring'), \
                    "Classification imports from Scoring"
```

**Strengths**:
- ✅ Runs with regular test suite
- ✅ Fast feedback
- ✅ Easy to run locally
- ✅ Part of CI/CD

**Weaknesses**:
- ❌ Can be slow if checking all modules
- ❌ May not catch all violations
- ❌ Requires test maintenance

**Recommendation**: ✅ **Recommended** as complement to static analysis

---

### 3.2 Contract Tests

**Approach**: Test that interfaces are correctly implemented

**Example**:

```python
# tests/test_contracts.py
import pytest
from typing import Protocol
from Source.Video.src.plugins import SourcePlugin
from Model import IdeaInspiration

def test_source_plugins_implement_interface():
    """All source plugins must implement SourcePlugin interface."""
    from Source.Video.YouTube.Channel.src.plugins import YouTubeChannelPlugin
    
    plugin = YouTubeChannelPlugin(config)
    
    # Check interface methods exist
    assert hasattr(plugin, 'scrape')
    assert hasattr(plugin, 'get_source_name')
    
    # Check return types
    result = plugin.scrape()
    assert isinstance(result, list)
    assert all(isinstance(item, IdeaInspiration) for item in result)
    
    name = plugin.get_source_name()
    assert isinstance(name, str)
```

**Strengths**:
- ✅ Verifies runtime behavior
- ✅ Catches interface violations
- ✅ Documents expectations

**Weaknesses**:
- ❌ Requires test data/mocks
- ❌ Can be slow
- ❌ May not cover all cases

**Recommendation**: ✅ **Recommended** for critical interfaces

---

## 4. CI/CD Integration

### 4.1 Pre-commit Hooks

**Approach**: Run checks before code is committed

**Example `.pre-commit-config.yaml`**:

```yaml
repos:
  - repo: local
    hooks:
      - id: check-architecture
        name: Check Architecture
        entry: python scripts/check_architecture.py
        language: python
        pass_filenames: false
        
      - id: import-linter
        name: Import Linter
        entry: lint-imports
        language: python
        pass_filenames: false
```

**Strengths**:
- ✅ Catches violations early
- ✅ Fast feedback
- ✅ Prevents bad commits
- ✅ Consistent across team

**Weaknesses**:
- ❌ Can slow down commits
- ❌ Developers can bypass (--no-verify)
- ❌ Need to set up

**Recommendation**: ✅ **Highly Recommended**

---

### 4.2 GitHub Actions

**Approach**: Run checks in CI pipeline

**Example `.github/workflows/architecture-check.yml`**:

```yaml
name: Architecture Check

on:
  pull_request:
    branches: [ main ]
  push:
    branches: [ main ]

jobs:
  architecture:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install import-linter pytest
      
      - name: Check imports
        run: |
          lint-imports
      
      - name: Run architecture tests
        run: |
          pytest tests/test_architecture.py -v
```

**Strengths**:
- ✅ Automated checks on every PR
- ✅ Can't be bypassed
- ✅ Visible to all team members
- ✅ Blocks merging on violations

**Weaknesses**:
- ❌ Slower feedback than pre-commit
- ❌ Requires GitHub Actions setup
- ❌ Uses CI minutes

**Recommendation**: ✅ **Essential** - final gate before merge

---

## 5. Documentation-Based Enforcement

### 5.1 Architecture Review Checklist

**Approach**: Provide checklist in PR template

**Example (added to `.github/PULL_REQUEST_TEMPLATE.md`)**:

```markdown
## Architecture Review

- [ ] Changes follow layered architecture (see ADR-001)
- [ ] Dependencies only flow downward
- [ ] No circular dependencies introduced
- [ ] No peer dependencies (Classification ↔ Scoring)
- [ ] New code follows SOLID principles
- [ ] Layer-appropriate naming conventions used
- [ ] Code is in correct layer/module
```

**Strengths**:
- ✅ Reminds reviewers what to check
- ✅ Low overhead
- ✅ Educational
- ✅ Easy to implement

**Weaknesses**:
- ❌ Relies on human compliance
- ❌ Can be ignored
- ❌ Not enforced

**Recommendation**: ✅ **Essential** - already partially implemented

---

### 5.2 Onboarding Documentation

**Approach**: Teach architecture to new team members

**Topics to Cover**:
- Layer definitions and boundaries
- Why we chose this architecture
- How to verify compliance
- Common pitfalls and anti-patterns
- Examples of good/bad code

**Strengths**:
- ✅ Prevents violations at source
- ✅ Builds shared understanding
- ✅ Long-term cultural impact

**Weaknesses**:
- ❌ Requires time investment
- ❌ Only helps new team members
- ❌ Can become outdated

**Recommendation**: ✅ **Essential** - creates culture of quality

---

## 6. Recommended Implementation Strategy

### Phase 1: Foundation (Immediate)

1. ✅ **Create ADRs**
   - ADR-001: Layered Architecture (done)
   - Future ADRs as needed

2. ✅ **Create Documentation**
   - SOLID_PRINCIPLES.md (done)
   - CODING_CONVENTIONS.md (in progress)
   - CODE_REVIEW_GUIDELINES.md (in progress)

3. ✅ **Update PR Template**
   - Add architecture review checklist
   - Link to relevant documentation

4. ✅ **Create Onboarding Guide**
   - Explain architecture to new developers
   - Include examples and anti-patterns

### Phase 2: Manual Enforcement (Week 1-2)

1. **Train Reviewers**
   - Share architecture documentation
   - Conduct architecture review session
   - Practice on example PRs

2. **Establish Review Process**
   - Require architecture sign-off on PRs
   - Use checklist consistently
   - Document exceptions in ADRs

### Phase 3: Basic Automation (Week 3-4)

1. **Add Architecture Tests**
   - Test layer dependencies
   - Test interface compliance
   - Run in CI/CD

2. **Create Custom Scripts**
   - Check import dependencies
   - Verify naming conventions
   - Run as pre-commit hook

### Phase 4: Advanced Automation (Month 2)

1. **Implement import-linter**
   - Configure rules for all layers
   - Integrate with CI/CD
   - Add to pre-commit hooks

2. **Add Pre-commit Hooks**
   - Run quick checks locally
   - Provide fast feedback
   - Standardize across team

3. **Enhance CI/CD**
   - Run all checks on PRs
   - Block merging on violations
   - Generate reports

### Phase 5: Continuous Improvement (Ongoing)

1. **Review and Refine**
   - Gather feedback from team
   - Adjust rules as needed
   - Update documentation

2. **Monitor Effectiveness**
   - Track violations over time
   - Identify common issues
   - Improve tooling

3. **Culture Building**
   - Celebrate good architecture
   - Share lessons learned
   - Encourage discussion

---

## 7. Tool Comparison

| Tool | Setup | Effectiveness | Speed | Maintenance |
|------|-------|---------------|-------|-------------|
| **Manual Review** | Easy | Medium | Slow | Low |
| **ADRs** | Easy | Low (passive) | N/A | Low |
| **Documentation** | Easy | Medium | N/A | Medium |
| **import-linter** | Medium | High | Fast | Low |
| **Pylint** | Medium | Medium | Fast | Medium |
| **Custom Scripts** | Medium | High | Fast | High |
| **Architecture Tests** | Easy | High | Medium | Medium |
| **Pre-commit Hooks** | Medium | High | Fast | Low |
| **CI/CD** | Medium | Very High | Medium | Low |

---

## 8. Recommendations Summary

### Must Have (Essential)
1. ✅ Architecture Decision Records (ADR-001 created)
2. ✅ Documentation (SOLID, conventions, guidelines)
3. ✅ PR template with architecture checklist
4. ✅ Code review guidelines
5. ✅ Onboarding documentation

### Should Have (High Priority)
6. Architecture tests in test suite
7. CI/CD checks for architecture
8. Pre-commit hooks for basic checks

### Nice to Have (Medium Priority)
9. import-linter integration
10. Custom architecture checking scripts
11. GitHub Actions workflow

### Future Enhancements
12. Advanced static analysis
13. Automated architecture reports
14. AI-assisted code review tools

---

## 9. Current Status

### Implemented ✅
- ADR template created
- ADR-001 (Layered Architecture) created
- SOLID_PRINCIPLES.md created
- Research documentation (this file)

### In Progress 🔄
- CODING_CONVENTIONS.md
- CODE_REVIEW_GUIDELINES.md
- PR template enhancements
- Onboarding documentation

### Planned 📋
- Architecture tests
- CI/CD integration
- Pre-commit hooks
- import-linter setup

---

## Conclusion

**Recommended Approach**: **Layered enforcement strategy**

1. **Foundation**: Documentation and guidelines (manual)
2. **First Line**: Code reviews with checklist
3. **Second Line**: Automated tests in CI/CD
4. **Safety Net**: Pre-commit hooks (future)
5. **Advanced**: Static analysis tools (future)

This provides multiple layers of protection while balancing:
- ✅ Effectiveness
- ✅ Developer experience
- ✅ Setup complexity
- ✅ Maintenance burden

**Next Steps**: 
1. Complete documentation (Phase 1)
2. Train team (Phase 2)
3. Add basic automation (Phase 3)
4. Enhance over time (Phase 4-5)

---

**Research By**: Architecture Team  
**Date**: 2025-11-14  
**Status**: Complete
