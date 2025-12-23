# PrismQ - Content Production Platform

**Progressive Multi-Format Content Creation: Text → Audio → Video**

## 📚 Core Modules

### Production Pipeline
- **[T - Text Generation Pipeline](./T/README.md)** - Transform ideas into high-quality text content
- **[A - Audio Generation Pipeline](./A/README.md)** - Convert published text into professional audio
- **[V - Video Generation Pipeline](./V/README.md)** - Combine audio with visuals for video platforms

## 🏗️ Module Structure & Guidelines

**Essential reading for all developers and AI assistants:**

### Module Structure Standards
- **[Coding Guidelines](./_meta/docs/guidelines/CODING_GUIDELINES.md)** - Core principles, module hierarchy, namespace shortcuts, placement decision tree
- **[Module Hierarchy](./_meta/docs/guidelines/MODULE_HIERARCHY_UPDATED.md)** - Dependency direction, layer responsibilities, abstraction levels
- **[PR Review Checklist](./_meta/docs/guidelines/PR_CODE_REVIEW_CHECKLIST.md)** - Required verification before merging

### Module Layout Convention
```
module/
├── src/        # Production source code only (runtime code)
├── _meta/      # Tests, docs, examples, scripts, auxiliary files
```

**Key Principles:**
- **Generic functionality belongs higher** in the hierarchy (src/ → T/src/ → T/Content/src/)
- **Specialized functionality belongs lower** in the hierarchy
- **Dependencies flow specialized → generic** (never the reverse)
- **Cross-cutting concerns** → `src/` (e.g., database configuration)
- **Domain foundations** → `T/src/` (e.g., AI configuration for Text domain)
- **No duplication** - reusable logic moves upward to common parent

### Module-Specific Documentation
- **[AI Configuration Placement](./T/_meta/docs/AI_CONFIG_PLACEMENT.md)** - Why AI config lives at T/src/ foundation level
- **[Script Compliance Audit](./_meta/docs/guidelines/SCRIPT_COMPLIANCE_AUDIT.md)** - Script naming and structure standards

### Supporting Modules
- **[P - Publishing Module](./P/README.md)** - Multi-platform content distribution
- **[M - Metrics & Analytics Module](./M/README.md)** - Performance tracking and insights
- **[Client - Web Management Interface](./Client/README.md)** - Task queue and workflow coordination
- **[Model - Data Models](./Model/README.md)** - Core data structures and state management
- **[src - Configuration Management](./src/README.md)** - Environment and configuration setup

## 📖 Documentation

### Project Documentation
All comprehensive documentation is in **[_meta/](./_meta/README.md)**:
- **[Workflow Documentation](./_meta/WORKFLOW.md)** - State machine and workflow
- **[Research & Strategy](./_meta/research/README.md)** - Research and insights
- **[Architecture & Proposals](./_meta/proposals/)** - Design proposals
- **[Technical Docs](./_meta/docs/)** - Setup guides and references

### Module Documentation
Each module has its own **_meta/** directory:
- **[T/_meta/](./T/_meta/README.md)** - Text module documentation
- **[A/_meta/](./A/_meta/README.md)** - Audio module documentation
- **[V/_meta/](./V/_meta/README.md)** - Video module documentation
- **[Client/_meta/](./Client/_meta/README.md)** - Client module documentation
- **[P/_meta/](./P/_meta/README.md)** - Publishing module documentation
- **[M/_meta/](./M/_meta/README.md)** - Metrics module documentation

## 🚀 Quick Start

1. **[Setup Environment](./src/README.md)** - Configure your environment
2. **[Explore T Module](./T/README.md)** - Start with text generation
3. **[Review Workflow](./_meta/WORKFLOW.md)** - Understand the workflow
4. **[Run Scripts](./_meta/scripts/NEXT_STEPS.md)** - Execute the production pipeline
5. **[Use Client](./Client/README.md)** - Manage tasks via web interface

## 📄 License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ
