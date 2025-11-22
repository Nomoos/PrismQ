# PrismQ Workflow Documentation

**Complete State Machine for Content Production from Inspiration to Archive**

This directory contains the modular workflow documentation, organized by topic for easy navigation and maintenance.

## Core Workflow Documents

### 1. [State Machine](./state-machine.md)
Complete state diagram and overview of the PrismQ content production workflow.
- State diagram (Mermaid)
- Workflow overview
- State definitions

### 2. [Workflow Phases](./phases.md)
The 9 main phases of content production.
- Phase 1: Inspiration & Ideation
- Phase 2: Script Development
- Phase 3: Text Publication
- Phase 4: Audio Production
- Phase 5: Audio Publication
- Phase 6: Visual Production
- Phase 7: Video Assembly
- Phase 8: Video Publishing
- Phase 9: Archive

### 3. [State Transitions](./transitions.md)
Rules and patterns for moving between states.
- Forward progression
- Backward transitions (revision loops)
- Feedback loops
- Early termination

### 4. [State Characteristics](./states.md)
Detailed characteristics of different state types.
- Entry states
- Intermediate states
- Composite states
- Terminal state

### 5. [Publishing Strategy](./publishing-strategy.md)
Progressive multi-format publishing approach.
- Sequential format enrichment (Text → Audio → Video)
- Content flow benefits
- Platform-specific optimization

### 6. [Workflow Management](./management.md)
Operational aspects of workflow execution.
- Progress tracking
- Quality gates
- Best practices
- Metrics & monitoring
- Automation opportunities

## MVP Implementation

For the detailed 26-stage MVP implementation of the text production phase, see:

- **[MVP Overview](./mvp-overview.md)** - Principles and workflow philosophy
- **[MVP Stages](./mvp-stages.md)** - All 26 stages in detail
- **[MVP API Reference](./mvp-api.md)** - API usage and examples
- **[MVP Best Practices](./mvp-best-practices.md)** - Best practices and troubleshooting

## Quick Navigation

- **Getting Started**: Start with [State Machine](./state-machine.md)
- **Understanding Phases**: Read [Workflow Phases](./phases.md)
- **Implementation Details**: See [MVP Overview](./mvp-overview.md)
- **API Integration**: Check [MVP API Reference](./mvp-api.md)

## Related Documentation

- [ARCHITECTURE.md](../ARCHITECTURE.md) - Overall platform architecture
- [PROGRESSIVE_ENRICHMENT.md](../PROGRESSIVE_ENRICHMENT.md) - Multi-format content strategy
- [QUALITY_GATES.md](../QUALITY_GATES.md) - Quality assurance framework

---

*This modular structure follows SOLID principles with single-responsibility documents focused on specific topics.*
