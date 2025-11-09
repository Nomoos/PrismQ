# Documentation Templates

This directory contains standardized templates for creating consistent documentation across the PrismQ.Client project.

## Available Templates

### 1. ISSUE_TEMPLATE.md
**Purpose**: Template for creating new issue documentation  
**Use When**: Creating issues in the `_meta/issues/` directory  
**Contains**: Status tracking, worker assignment, acceptance criteria, dependencies, testing requirements

**Example Usage**:
```bash
cp _meta/templates/ISSUE_TEMPLATE.md _meta/issues/new/Worker01/ISSUE-COMPONENT-XXX-feature-name.md
```

**Key Sections**:
- Status tracking with emoji indicators
- Worker assignment
- Acceptance criteria checklist
- Implementation details
- Testing requirements
- Timeline tracking

---

### 2. API_DOCUMENTATION_TEMPLATE.md
**Purpose**: Template for documenting REST APIs  
**Use When**: Creating API reference documentation  
**Contains**: Endpoint specifications, request/response examples, error codes, authentication details

**Example Usage**:
```bash
cp _meta/templates/API_DOCUMENTATION_TEMPLATE.md Backend/TaskManager/docs/API_REFERENCE.md
```

**Key Sections**:
- Authentication methods
- Endpoint specifications (CRUD operations)
- Request/response formats
- Error handling and status codes
- Rate limiting
- Language-specific examples (Python, JavaScript, PHP)

---

### 3. DEPLOYMENT_GUIDE_TEMPLATE.md
**Purpose**: Template for deployment documentation  
**Use When**: Creating deployment guides for components or services  
**Contains**: Step-by-step deployment instructions, configuration, verification, rollback procedures

**Example Usage**:
```bash
cp _meta/templates/DEPLOYMENT_GUIDE_TEMPLATE.md Backend/TaskManager/docs/DEPLOYMENT.md
```

**Key Sections**:
- Prerequisites checklist
- Pre-deployment checklist
- Step-by-step deployment instructions
- Configuration management
- Verification procedures
- Rollback procedures
- Troubleshooting common issues
- Monitoring setup

---

### 4. README_TEMPLATE.md
**Purpose**: Template for component/module README files  
**Use When**: Creating README documentation for new components, libraries, or modules  
**Contains**: Overview, features, installation, usage, API reference, examples

**Example Usage**:
```bash
cp _meta/templates/README_TEMPLATE.md Backend/NewComponent/README.md
```

**Key Sections**:
- Overview and features
- Requirements and installation
- Quick start guide
- Configuration options
- Usage examples
- API reference
- Testing instructions
- Contributing guidelines

---

### 5. INTEGRATION_GUIDE_TEMPLATE.md
**Purpose**: Template for integration documentation  
**Use When**: Documenting how to integrate with external services or between components  
**Contains**: Integration methods, step-by-step guides, code examples, troubleshooting

**Example Usage**:
```bash
cp _meta/templates/INTEGRATION_GUIDE_TEMPLATE.md _meta/examples/workers/INTEGRATION_GUIDE.md
```

**Key Sections**:
- Architecture overview
- Integration methods comparison
- Step-by-step integration
- Configuration
- Testing integration
- Common patterns
- Language-specific examples
- Troubleshooting

---

### 6. WORKER_IMPLEMENTATION_TEMPLATE.md
**Purpose**: Template for worker implementation documentation  
**Use When**: Creating documentation for background workers or task processors  
**Contains**: Worker architecture, implementation examples, task processing, error handling

**Example Usage**:
```bash
cp _meta/templates/WORKER_IMPLEMENTATION_TEMPLATE.md _meta/examples/workers/python/WORKER_GUIDE.md
```

**Key Sections**:
- Worker responsibilities
- Architecture and data flow
- Complete implementation examples (Node.js, PHP, Python)
- Task processing patterns
- Error handling and retry logic
- Deployment as a service
- Monitoring and health checks

---

### 7. RELEASE_NOTES_TEMPLATE.md
**Purpose**: Template for release notes  
**Use When**: Creating GitHub release notes  
**Location**: `_meta/docs/RELEASE_NOTES_TEMPLATE.md` (already exists)

**Key Sections**:
- Release summary
- New features
- Improvements
- Bug fixes
- Breaking changes
- Deployment notes
- Testing metrics

---

## How to Use These Templates

### Step 1: Choose the Right Template

Select the template that matches your documentation needs:
- **Creating an issue?** → Use ISSUE_TEMPLATE.md
- **Documenting an API?** → Use API_DOCUMENTATION_TEMPLATE.md
- **Writing a deployment guide?** → Use DEPLOYMENT_GUIDE_TEMPLATE.md
- **Creating a component README?** → Use README_TEMPLATE.md
- **Documenting integration?** → Use INTEGRATION_GUIDE_TEMPLATE.md
- **Implementing a worker?** → Use WORKER_IMPLEMENTATION_TEMPLATE.md

### Step 2: Copy the Template

```bash
# Example: Creating a new component README
cp _meta/templates/README_TEMPLATE.md Backend/MyComponent/README.md
```

### Step 3: Fill in the Template

1. Replace all placeholder text in `[brackets]`
2. Update version numbers and dates
3. Remove sections that don't apply
4. Add project-specific sections if needed
5. Fill in all required information

### Step 4: Customize for Your Needs

Templates are starting points. Customize them to fit your specific needs:
- Add sections relevant to your component
- Remove irrelevant sections
- Adjust examples to match your use case
- Update code samples to use your actual code

### Step 5: Review and Validate

Before committing:
- [ ] All placeholders replaced
- [ ] Code examples are accurate
- [ ] Links work correctly
- [ ] Formatting is consistent
- [ ] Content is complete

---

## Template Guidelines

### Writing Style

- **Be Clear and Concise**: Use simple, direct language
- **Be Specific**: Include exact commands, file paths, and values
- **Be Complete**: Provide all necessary information
- **Be Consistent**: Follow the same patterns across documents

### Code Examples

- Always include complete, runnable code
- Show expected output
- Include error handling
- Use realistic examples
- Support multiple languages where applicable (PHP, Python, JavaScript)

### Formatting

- Use markdown consistently
- Use headers for structure (# for H1, ## for H2, etc.)
- Use code blocks with language specification (```javascript, ```php, ```bash)
- Use tables for structured data
- Use checklists for tasks (- [ ] or - [x])

### Placeholders

Templates use these placeholder patterns:
- `[Component Name]` - Replace with actual component name
- `[X.Y.Z]` - Replace with actual version number
- `[YYYY-MM-DD]` - Replace with actual date
- `[Description]` - Replace with actual description
- `[language]` - Replace with programming language (javascript, php, python, etc.)

---

## Template Maintenance

### Updating Templates

When updating templates:
1. Update the template file
2. Update this README if sections change
3. Consider backwards compatibility
4. Document changes in template version history

### Template Versioning

Each template includes a version number at the bottom:
```markdown
**[Template Name] Version**: 1.0  
**Last Updated**: YYYY-MM-DD  
**Maintained by**: Worker06 (Documentation Specialist)
```

### Contributing to Templates

To improve templates:
1. Create an issue describing the improvement
2. Make changes to the template
3. Update this README
4. Submit a pull request

---

## Examples of Template Usage

### Example 1: Creating an Issue

```bash
# Copy template
cp _meta/templates/ISSUE_TEMPLATE.md \
   Backend/TaskManager/_meta/issues/new/Worker03/ISSUE-TASKMANAGER-XXX-new-feature.md

# Edit the file and fill in:
# - Replace [COMPONENT] with TASKMANAGER
# - Replace [NUMBER] with 010
# - Replace [Title] with "Add caching layer"
# - Fill in all sections
# - Remove irrelevant sections
```

### Example 2: Creating API Documentation

```bash
# Copy template
cp _meta/templates/API_DOCUMENTATION_TEMPLATE.md \
   Backend/NewService/docs/API_REFERENCE.md

# Customize for your API:
# - Replace [Component/Service Name] with "NewService"
# - Update Base URL
# - Add your endpoints
# - Include authentication details
# - Add code examples in PHP, Python, JavaScript
```

### Example 3: Creating a Worker Guide

```bash
# Copy template
cp _meta/templates/WORKER_IMPLEMENTATION_TEMPLATE.md \
   _meta/examples/workers/nodejs/WORKER_GUIDE.md

# Fill in:
# - Worker type and responsibilities
# - Implementation code examples
# - Configuration details
# - Deployment instructions
```

---

## Best Practices

### Do's ✅

- ✅ Use templates as a starting point
- ✅ Customize templates to fit your needs
- ✅ Keep documentation up to date
- ✅ Include code examples
- ✅ Test all commands and code samples
- ✅ Link between related documents
- ✅ Use consistent formatting
- ✅ Include version numbers and dates

### Don'ts ❌

- ❌ Don't leave placeholder text in final docs
- ❌ Don't copy-paste without customization
- ❌ Don't include untested code examples
- ❌ Don't forget to update dates and versions
- ❌ Don't skip sections without considering if they apply
- ❌ Don't use inconsistent formatting
- ❌ Don't create documentation without using templates

---

## Template Structure Overview

All templates follow a consistent structure:

1. **Title and Metadata**
   - Document title
   - Version number
   - Last updated date
   - Target audience (if applicable)

2. **Table of Contents**
   - Quick navigation
   - Linked sections

3. **Overview**
   - What this document covers
   - Why it's important
   - Who should read it

4. **Main Content**
   - Organized in logical sections
   - Progressive complexity (simple → advanced)
   - Examples throughout

5. **Reference Material**
   - Additional resources
   - Links to related docs
   - Support information

6. **Footer**
   - Version information
   - Maintenance information
   - Contact details

---

## Quality Checklist

Before finalizing documentation created from a template:

### Content Completeness
- [ ] All sections filled in or removed if not applicable
- [ ] No placeholder text remaining
- [ ] All links work correctly
- [ ] All code examples are tested and work
- [ ] Version numbers are current
- [ ] Dates are accurate

### Technical Accuracy
- [ ] Commands produce expected output
- [ ] File paths are correct
- [ ] Configuration examples are valid
- [ ] Code examples run successfully
- [ ] API endpoints are accurate

### Formatting and Style
- [ ] Consistent markdown formatting
- [ ] Code blocks have language specification
- [ ] Tables are properly formatted
- [ ] Headers follow hierarchy
- [ ] Lists are consistent

### Usability
- [ ] Clear and concise writing
- [ ] Examples are realistic and helpful
- [ ] Troubleshooting covers common issues
- [ ] Prerequisites are clearly stated
- [ ] Next steps are clear

---

## Getting Help

If you need help using these templates:

1. **Check Examples**: Look at existing documentation that uses these templates:
   - `Backend/TaskManager/README.md`
   - `Backend/TaskManager/docs/API_REFERENCE.md`
   - `Backend/TaskManager/docs/DEPLOYMENT.md`

2. **Ask Questions**: Create an issue or contact:
   - **Worker06**: Documentation Specialist
   - **Worker01**: Project Manager

3. **Contribute**: If you find ways to improve templates, submit a PR!

---

## Related Documentation

- [Documentation Index](_meta/docs/README.md) - Complete documentation overview
- [Worker Implementation Guidelines](_meta/docs/WORKER_IMPLEMENTATION_GUIDELINES.md) - Worker development guide
- [Development Guide](_meta/docs/DEVELOPMENT.md) - Contributing guide

---

**Templates README Version**: 1.0  
**Last Updated**: 2025-11-09  
**Maintained by**: Worker06 (Documentation Specialist)  
**Template Count**: 7 templates
