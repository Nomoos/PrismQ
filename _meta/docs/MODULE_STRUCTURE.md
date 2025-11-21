# Module Structure Guide

**Document Type**: Organization Guide  
**Scope**: Project-wide  
**Last Updated**: 2025-11-21

## Purpose

This document defines the standard module organization pattern used throughout PrismQ, ensuring consistency and discoverability across all components.

## Standard Module Pattern

Every module in PrismQ follows this structure:

```
ModuleName/
├── SubModule1/
│   ├── _meta/
│   │   ├── docs/
│   │   ├── examples/
│   │   └── tests/
│   └── README.md
├── SubModule2/
│   ├── _meta/
│   │   ├── docs/
│   │   ├── examples/
│   │   └── tests/
│   └── README.md
├── _meta/
│   ├── docs/
│   ├── examples/
│   └── tests/
└── README.md
```

## Module Components

### 1. README.md
**Purpose**: Navigation hub and module overview

**Required Sections**:
- Module name and namespace
- Purpose and description
- List of submodules with links
- Link to _meta content
- Navigation footer

**Example**:
```markdown
# ModuleName

**Namespace**: `PrismQ.Pipeline.ModuleName`

Brief description of what this module does...

## Submodules

### [SubModule1](./SubModule1/)
Description of SubModule1...

**[→ View SubModule1 Metadata](./SubModule1/_meta/)**

## Module Metadata

**[→ View Docs](./_meta/docs/)**
**[→ View Examples](./_meta/examples/)**
**[→ View Tests](./_meta/tests/)**

## Navigation

**[← Back to Parent](../)** | **[Next Module →](../NextModule/)**
```

### 2. _meta Directory
**Purpose**: Metadata storage separate from production code

**Required Subdirectories**:
- `docs/` - Module documentation
- `examples/` - Usage examples
- `tests/` - Test suites

**Optional Subdirectories**:
- `research/` - Research documents
- `issues/` - Issue tracking
- `proposals/` - Design proposals
- `benchmarks/` - Performance data

### 3. _meta/docs/
**Purpose**: Technical documentation for the module

**Typical Contents**:
- `README.md` - Documentation index
- `API.md` - API reference
- `CONFIGURATION.md` - Configuration guide
- `INTEGRATION.md` - Integration guide
- Module-specific guides

**Guidelines**:
- One topic per file
- Clear, descriptive file names
- Cross-reference related docs
- Keep up-to-date with code

### 4. _meta/examples/
**Purpose**: Working code examples

**Typical Contents**:
- `basic_usage.py` - Simple example
- `advanced_usage.py` - Complex example
- `integration_example.py` - Integration with other modules
- Sample data files

**Guidelines**:
- Runnable examples
- Include comments
- Cover common use cases
- Show best practices

### 5. _meta/tests/
**Purpose**: Test suites for the module

**Typical Contents**:
- Unit tests
- Integration tests
- Test fixtures
- Test data

**Guidelines**:
- Follow project testing standards
- Adequate coverage
- Clear test names
- Document edge cases

## Naming Conventions

### Modules
- **Top-Level**: Single letter (T, A, V) or descriptive name (Client)
- **Sub-Modules**: PascalCase (Idea, Script, Publishing)
- **Deep Modules**: Descriptive names (Draft, Optimization, Keywords)

### Files
- **Documentation**: UPPER_CASE.md (README.md is exception)
- **Code**: snake_case for Python, camelCase for JavaScript
- **Examples**: descriptive_example.ext

### Directories
- **Modules**: PascalCase
- **Metadata**: Lowercase with underscore (_meta)
- **Special**: Lowercase (_tests, _docs, _examples)

## Module Levels

### Level 1: Top-Level Pipelines
**Location**: `/`  
**Examples**: `T/`, `A/`, `V/`, `P/`, `M/`, `Client/`

**Characteristics**:
- Major functional areas
- Top-level namespaces
- Comprehensive README with architecture
- Full _meta structure

### Level 2: Major Modules
**Location**: `/Pipeline/`  
**Examples**: `T/Idea/`, `A/Voiceover/`, `V/Scene/`

**Characteristics**:
- Core functional components
- May contain submodules
- README with module overview
- _meta with documentation

### Level 3: Submodules
**Location**: `/Pipeline/Module/`  
**Examples**: `T/Idea/Model/`, `A/Voiceover/Recording/`

**Characteristics**:
- Specific functionality
- Usually leaf nodes (no further submodules)
- README with usage info
- _meta with examples

## Real-World Examples

### Example 1: T Module (Text Generation)

```
T/
├── Idea/
│   ├── Model/
│   │   ├── _meta/
│   │   │   ├── docs/
│   │   │   │   ├── DATABASE.md
│   │   │   │   ├── FIELDS.md
│   │   │   │   └── QUICK_START.md
│   │   │   ├── examples/
│   │   │   └── tests/
│   │   └── README.md
│   ├── Outline/
│   │   ├── _meta/
│   │   └── README.md
│   ├── _meta/
│   └── README.md
├── Script/
│   ├── Draft/
│   ├── Improvements/
│   ├── _meta/
│   └── README.md
├── _meta/
│   ├── docs/
│   ├── examples/
│   └── tests/
└── README.md
```

### Example 2: A Module (Audio Generation)

```
A/
├── Voiceover/
│   ├── _meta/
│   │   ├── docs/
│   │   │   ├── RECORDING_GUIDE.md
│   │   │   └── QUALITY_STANDARDS.md
│   │   ├── examples/
│   │   └── tests/
│   └── README.md
├── Normalized/
│   ├── _meta/
│   └── README.md
├── _meta/
│   ├── docs/
│   ├── examples/
│   └── tests/
└── README.md
```

## Creating New Modules

### Step 1: Create Directory Structure
```bash
mkdir -p NewModule/_meta/{docs,examples,tests}
```

### Step 2: Create README.md
Use the standard template with:
- Module name and namespace
- Purpose description
- Links to _meta content
- Navigation links

### Step 3: Add to Parent
Update parent module's README.md:
- Add new module to submodules list
- Include description
- Link to README and _meta

### Step 4: Populate _meta
Add initial documentation:
- `_meta/docs/README.md` - Documentation index
- `_meta/examples/basic_usage.*` - Simple example
- `_meta/tests/test_basic.py` - Basic tests

## Best Practices

### Documentation
1. Keep README.md focused on navigation
2. Use _meta/docs/ for detailed documentation
3. One topic per document
4. Cross-reference related docs

### Examples
1. Make examples runnable
2. Use realistic data
3. Comment thoroughly
4. Show best practices

### Tests
1. Follow testing standards
2. Cover key functionality
3. Document edge cases
4. Keep tests maintainable

### Naming
1. Be descriptive but concise
2. Follow established patterns
3. Use consistent casing
4. Avoid abbreviations (unless standard)

## Validation

To check if a module follows the standard:

**Required**:
- ✓ README.md exists
- ✓ _meta/ directory exists
- ✓ _meta/docs/ subdirectory exists
- ✓ _meta/examples/ subdirectory exists
- ✓ _meta/tests/ subdirectory exists

**Recommended**:
- ✓ README has navigation section
- ✓ README lists all submodules
- ✓ _meta/docs/ has content
- ✓ Examples are runnable

## Related Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Overall platform architecture
- **[STRUCTURE_RATING.md](./STRUCTURE_RATING.md)** - Structure evaluation
- **[NAVIGATION_SUMMARY.md](./NAVIGATION_SUMMARY.md)** - Navigation patterns

---

*Consistent module structure makes PrismQ navigable and maintainable.*
