# Research

This directory contains research materials, experiments, and exploratory work for the PrismQ.IdeaInspiration project.

## Purpose

Store research-related content including:
- Experimental code and prototypes
- Research papers and references
- Performance benchmarks and analysis
- Model comparisons and evaluations
- Algorithm explorations

## Structure

Organize research by topic or experiment:
- Create subdirectories for major research areas
- Use descriptive names for research files and folders
- Include README files to explain the research context
- Document findings and conclusions

## Current Research

### TOON vs JSON for AI Applications (2025-11-17)

Comprehensive research comparing TOON (Token-Oriented Object Notation) and JSON data formats for use in AI applications within the PrismQ ecosystem.

**Documents**:
- `TOON_VS_JSON_SUMMARY.md` - Quick summary and decision guide (⭐ **START HERE**)
- `TOON_VS_JSON_AI_APPLICATIONS.md` - Complete research document (47K words)

**Key Findings**:
- **TOON optimal for**: LLM prompts with structured data (30-60% token cost reduction)
- **JSON optimal for**: APIs, storage, ML frameworks, internal processing (universal standard)
- **Hybrid approach recommended**: Use JSON internally, convert to TOON for LLM inputs
- **Token savings**: 30-60% on uniform tabular arrays, less on nested structures
- **Cost impact**: $400-$7,200/year savings depending on LLM usage volume

**What is TOON?**:
- Format specifically designed for Large Language Models
- Lossless JSON representation with minimal syntax
- YAML-style indentation + CSV-style tabular arrays
- Explicit structure (length declarations, field headers)
- Production-ready (v2.0, MIT licensed)
- Spec: https://github.com/toon-format/spec

**Recommendations**:
- Keep JSON as default for all internal processing, APIs, and storage
- Convert structured data to TOON specifically for LLM prompts
- Pilot in Classification module (highest LLM usage)
- Measure actual token cost savings and ROI
- Monitor Python TOON library ecosystem

**Related Context**: LLM token cost optimization, AI-powered content generation pipeline

### Client API - Simplified Queue (2025-11-05)

Research on a simplified approach to the SQLite-based task queue Client API.

**Documents**:
- `README-CLIENT-API-RESEARCH.md` - Executive summary and overview
- `client-api-simplified-queue.md` - Detailed research document (15K words)
- `DECISION-MATRIX-CLIENT-API.md` - Decision framework comparing approaches
- `simplified_queue_client.py` - Working prototype implementation (350 LOC)
- `test_simplified_queue_client.py` - 15 unit tests (all passing)

**Key Findings**:
- Simplified approach: 1-2 days vs 4 weeks for full design
- Adequate for current needs: 100-500 tasks/min
- Priority-based ordering: Higher numbers = higher importance
- Production-ready prototype with 0 security vulnerabilities

**Related Issues**: #320 (Queue Analysis), #323 (Client API Implementation)

## Best Practices

- Keep research separate from production code
- Document methodology and findings
- Include reproduction steps for experiments
- Note hardware specifications for benchmarks (especially RTX 5090 results)
- Link to related issues or features when applicable

## Note

Research materials here may eventually be incorporated into the main codebase or published as separate documentation.
