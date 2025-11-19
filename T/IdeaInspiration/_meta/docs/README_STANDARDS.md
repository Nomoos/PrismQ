# README Standards for PrismQ Modules

## Purpose

README files in the PrismQ ecosystem serve as **navigation hubs** that help users quickly understand what a module does and where to find detailed information. They should NOT contain detailed documentation that belongs in dedicated doc files.

## Philosophy

**README = Navigation Hub**
- Quick overview and orientation
- Links to detailed documentation
- Minimal quick start (1-2 commands)
- NOT a comprehensive guide

**docs/ = Detailed Information**
- Complete installation instructions
- Comprehensive usage guides
- Architecture explanations
- API references
- Contributing guidelines

## README Structure

All README files should follow this standard structure:

### 1. Title and Brief Description
- Project/module name as H1
- 1-2 sentence description immediately below
- No lengthy explanations

### 2. Highlights Section (✨)
- 3-5 key features as bullet points
- Each point should be brief (one line)
- Focus on what makes this module valuable

### 3. Quick Start Section (🚀)
- Absolute minimal commands to get started
- 1-2 commands maximum
- Link to detailed setup guide for more
- Example: `pip install -e .` and `python -m module_name`

### 4. Documentation Section (📚)
- **Primary purpose of README**
- Links to all relevant documentation files
- Use bold for link text
- Include brief description after each link
- Standard documentation files:
  - **Setup Guide** - Installation and configuration
  - **User Guide** - How to use the module
  - **API Reference** - API documentation (if applicable)
  - **Architecture** - System design and internals
  - **Contributing** - How to contribute

### 5. Related Section (🔗)
- Links to related modules
- Links to parent/child modules
- Links to documentation directories
- Keep descriptions brief

### 6. License Section (📄)
- License type
- Copyright notice if applicable

## What NOT to Include

README files should NOT contain:

1. **Detailed Installation Instructions**
   - ❌ Step-by-step setup procedures
   - ❌ Troubleshooting guides
   - ❌ System requirements details
   - ✅ Link to docs/SETUP.md instead

2. **Comprehensive Architecture Explanations**
   - ❌ System diagrams and detailed architecture
   - ❌ Component descriptions
   - ❌ Design decisions
   - ✅ Link to docs/ARCHITECTURE.md instead

3. **Complete Usage Guides**
   - ❌ Detailed usage examples
   - ❌ Configuration options
   - ❌ Advanced usage patterns
   - ✅ Link to docs/USER_GUIDE.md instead

4. **Full API Documentation**
   - ❌ Complete API reference
   - ❌ Method signatures
   - ❌ Detailed parameter descriptions
   - ✅ Link to docs/API.md instead

5. **Contributing Guidelines**
   - ❌ Code style guidelines
   - ❌ PR process
   - ❌ Development setup
   - ✅ Link to docs/CONTRIBUTING.md instead

## Template

Use the standard template located at:
`_meta/docs/templates/README_TEMPLATE.md`

## Examples

### Good README (Navigation Hub)

```markdown
# MyModule

Fast content processing and analysis engine.

## ✨ Highlights

- Batch processing with GPU acceleration
- Extensible plugin system
- Built-in caching for performance

## 🚀 Quick Start

\`\`\`bash
pip install -e .
python -m mymodule --help
\`\`\`

## 📚 Documentation

- **[Setup Guide](./docs/SETUP.md)** - Installation and configuration
- **[User Guide](./docs/USER_GUIDE.md)** - Complete usage instructions
- **[Architecture](./docs/ARCHITECTURE.md)** - System design and internals

## 🔗 Related

- [Main Repository](../../) - Project overview
- [Sources Module](../Sources/) - Data sources

## 📄 License

Proprietary - All Rights Reserved
```

### Bad README (Too Detailed)

```markdown
# MyModule

MyModule is a comprehensive tool for content processing...
[200 words of description]

## Installation

1. Clone the repository
2. Create virtual environment:
   \`\`\`bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\\Scripts\\activate  # Windows
   \`\`\`
3. Install dependencies:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`
[20 more steps...]

## Architecture

The system consists of three layers...
[500 lines of architecture details]

## Usage

To use MyModule, first you need to...
[300 lines of usage instructions]

## API Reference

### Class: MyProcessor
...
[Full API documentation]
```

## Repository vs Module READMEs

### Repository-Level README

The root README.md should:
- Provide overview of the entire repository
- List all modules with brief descriptions
- Link to module READMEs
- Link to project-level documentation in `_meta/docs/`
- Include quick start for developers

### Module-Level README

Each module README.md should:
- Focus only on that specific module
- Link to module-specific documentation in `Module/docs/`
- Link back to repository README for context
- Link to related modules

## Maintenance

When updating documentation:

1. **Single Source of Truth**: Each piece of information should exist in exactly ONE place
2. **README Updates**: Should only update links and highlights, not detailed content
3. **Documentation Updates**: Detailed changes go in docs/ files, not README
4. **Consistency**: Use the same structure across all modules
5. **Link Validation**: Ensure all links work after updates

## Migration Checklist

When converting an existing README:

- [ ] Identify duplicated content between README and docs/
- [ ] Move detailed installation to docs/SETUP.md
- [ ] Move detailed usage to docs/USER_GUIDE.md
- [ ] Move architecture details to docs/ARCHITECTURE.md
- [ ] Move contributing guidelines to docs/CONTRIBUTING.md
- [ ] Update README to navigation-only format using template
- [ ] Verify all links work
- [ ] Remove duplicated content from README
- [ ] Test quick start commands

## Related Documents

- [README Template](./templates/README_TEMPLATE.md) - Standard template to use
- [Contributing Guidelines](./CONTRIBUTING.md) - How to contribute
- [Documentation Hierarchy](./README.md) - Overview of documentation structure
