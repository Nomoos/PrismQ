# Issue #113: Virtual Environment Strategy Decision (Per-Project Analysis)

**Type**: Research/Decision  
**Priority**: High  
**Status**: ✅ COMPLETED  
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM  
**Completion Date**: 2025-10-31  
**Dependencies**: None  
**Related Issues**: #114, #115, #116, #117, #118

---

## ✅ DECISION MADE

**Chosen Strategy**: **Strategy 2 - Per-Project Virtual Environments (Full Isolation)**

**Implementation**: Issue #115 + Issue #118 (direnv)

**Full Analysis**: See [VENV_STRATEGY_DECISION.md](../../docs/VENV_STRATEGY_DECISION.md)

---

## Decision Summary

### Why Per-Project Isolation is MANDATORY

**Critical New Information**: Each project will depend on AI with many different tools.

**The AI Factor Makes This Decision Simple**:

1. **Multiple AI Frameworks Cannot Coexist**:
   - Cannot install PyTorch 2.0.0 AND 2.1.0 in same environment
   - Cannot install transformers 4.30 AND 4.35 in same environment
   - Different projects need different AI frameworks/versions
   - **Result**: Shared or grouped environments are technically impossible

2. **Real Conflict Examples**:
   - Classification: BERT models (transformers 4.30 + torch 2.0)
   - Sources: GPT/Llama models (transformers 4.35 + torch 2.1)
   - Scoring: Multi-modal models (CLIP + vision transformers)
   - Client/Backend: AI-powered interactions (OpenAI API + langchain)
   - **Cannot satisfy all requirements in one environment**

3. **User Requirements Align Perfectly**:
   - User prefers full isolation ✅
   - Disk space "not a problem at all" ✅
   - Switching overhead "not a problem" ✅
   - **Conclusion**: No constraints preventing optimal solution

### Rejected Strategies

**Strategy 1 (Shared - Issue #114)**: ❌ DO NOT IMPLEMENT
- Technically impossible with AI in each project
- Cannot install conflicting PyTorch/transformers versions
- Would fail immediately when projects add AI dependencies

**Strategy 3 (Grouped - Issue #116)**: ❌ DO NOT IMPLEMENT  
- Same AI conflicts within groups
- "Core" group with multiple AI projects → same problems as shared
- Adds complexity without solving AI version conflicts

**Strategy 4 (Layered - Issue #117)**: ❌ DO NOT IMPLEMENT
- Over-engineered
- Doesn't solve AI version conflicts
- Non-standard setup with high maintenance burden

### Implementation Plan

**Implement**:
1. ✅ **Issue #115**: Per-Project Virtual Environments
   - Create venv/ in each project directory
   - Automation scripts for setup, update, testing
   - Per-project requirements.txt

2. ✅ **Issue #118**: direnv Integration
   - Auto-activate correct environment on `cd`
   - Auto-load project-specific environment variables
   - Seamless switching (zero manual intervention)

**Timeline**: 2 weeks
- Week 1: Core setup + scripts + testing
- Week 2: direnv integration + IDE setup + documentation

### Expected Outcomes

**Disk Space**: ~20-30GB total
- Each AI project: ~4-6GB (PyTorch + transformers + models)
- Lightweight projects: ~180-250MB
- Acceptable per user constraints

**Benefits**:
- ✅ Zero AI dependency conflicts (impossible to have conflicts)
- ✅ Each project chooses its AI framework/version independently
- ✅ Safe AI model experimentation
- ✅ Production-like isolation
- ✅ Team independence (ML, web, data teams work separately)

**Risks**: None (only viable strategy)

---

## Background: Original Issue Analysis Framework

The sections below contain the original analysis framework used to evaluate all strategies.

## Description

Determine and document the optimal virtual environment management strategy for the PrismQ.IdeaInspiration monorepo, analyzing each project individually and identifying logical groupings where shared environments make sense.

## Monorepo Projects

- **Classification**: Lightweight, zero runtime dependencies
- **ConfigLoad**: Lightweight, minimal dependencies (python-dotenv, psutil)
- **Model**: Lightweight, zero runtime dependencies
- **Scoring**: Medium weight, python-dotenv, future ML dependencies
- **Sources**: Lightweight, python-dotenv
- **Client/Backend**: Heavy, FastAPI stack with many dependencies

## Problem Statement

Managing virtual environments across multiple Python projects in a monorepo presents several challenges:
- **Redundant installations**: Common packages duplicated across multiple venvs
- **Dependency drift**: Projects using different versions of shared dependencies
- **Developer experience**: Manually activating/switching environments is error-prone
- **IDE/Copilot integration**: Tools need access to all project dependencies
- **Disk space**: Multiple venvs consume significant storage

**Key Question**: Should we use one approach for all projects, or tailor the strategy per project/group?

## Project-Specific Analysis

### Group 1: Lightweight Core Modules (Classification, Model)
**Characteristics**:
- Zero runtime dependencies (stdlib only)
- Only dev dependencies (pytest, black, mypy, flake8)
- Tight integration, often developed together
- Similar dependency profiles

**Recommendation to evaluate**: Shared dev environment OR shared monorepo-wide dev tools

### Group 2: Infrastructure Modules (ConfigLoad, Sources)
**Characteristics**:
- Minimal dependencies (python-dotenv, psutil)
- Support modules for other projects
- Often used together
- Similar lightweight profile

**Recommendation to evaluate**: Share with Group 1 OR separate lightweight env

### Group 3: Processing Module (Scoring)
**Characteristics**:
- Currently light (python-dotenv)
- **Future**: Heavy ML dependencies (torch, transformers, sentence-transformers)
- GPU-intensive workloads planned
- May need specific package versions for ML compatibility

**Recommendation to evaluate**: Isolated environment (especially when ML is added)

### Group 4: Web Application (Client/Backend)
**Characteristics**:
- Heavy dependencies (FastAPI, Uvicorn, Pydantic, SSE-Starlette)
- Web framework with specific version requirements
- Completely different domain from data processing
- Frequent updates and iterations

**Recommendation to evaluate**: Isolated environment (separate from data processing)

## Strategy Options

### Strategy 1: One Shared Virtual Environment (Monorepo-Wide)
- **Pros**: No duplication, simple IDE setup, consistent versions
- **Cons**: No isolation, conflicts likely (web framework vs ML), very large environment
- **Verdict**: Likely problematic when ML and web frameworks coexist

### Strategy 2: Per-Project Virtual Environments (Full Isolation)
- **Pros**: Full isolation, independent version control, lean per-project
- **Cons**: Duplicate installations even for identical dependencies, manual env switching
- **Verdict**: Safe but inefficient for groups with identical dependencies

### Strategy 3: Grouped Virtual Environments (Pragmatic Hybrid)
- **Group A**: Lightweight modules (Classification, Model, ConfigLoad, Sources)
- **Group B**: ML Processing (Scoring) - isolated when ML dependencies added
- **Group C**: Web Client (Client/Backend) - isolated
- **Pros**: Balance between sharing and isolation, logical groupings
- **Cons**: Need to manage 3 environments instead of 1 or 6

### Strategy 4: Layered Hybrid (Base + Project-Specific)
- **Base layer**: Common dev tools (pytest, black, mypy, ruff)
- **Project layers**: Project-specific runtime dependencies
- **Pros**: Avoid duplicating dev tools 6 times
- **Cons**: Complexity with pip-tools, .pth files, or system-site-packages

## Evaluation Criteria (Per Project/Group)

### For Each Project Group:
1. **Dependency Profile**: Runtime vs dev-only, weight, ML vs web vs minimal
2. **Isolation Needs**: Can it coexist with others or needs specific versions?
3. **Development Patterns**: Developed together or independently?
4. **Future Growth**: Will dependencies diverge or stay aligned?
5. **IDE Integration**: Single interpreter works or needs per-folder setup?

### Overall System:
1. **Disk Space**: Total storage for all environments
2. **Install Time**: Combined time to set up all environments
3. **Developer Experience**: Effort to switch contexts and manage envs
4. **Maintenance**: Keeping dependencies updated across groups
5. **Scalability**: Adding new projects to existing groups

## Deliverables

- [ ] Per-project dependency analysis document
- [ ] Logical grouping recommendations with rationale
- [ ] Comparison matrix for each strategy applied to our specific projects
- [ ] Disk space measurements for each strategy
- [ ] Developer workflow documentation for each strategy
- [ ] Final recommendation: Which projects share envs, which stay isolated
- [ ] Migration plan from current state to recommended state

## Tasks

### Phase 1: Analysis (Week 1)
- [ ] Document all current dependencies per project
- [ ] Identify overlapping dependencies (exact versions)
- [ ] Map development patterns (which projects developed together)
- [ ] Analyze future roadmap for each project (ML, web, etc.)
- [ ] Create dependency overlap matrix

### Phase 2: Prototyping (Week 1-2)
- [ ] Test Strategy 1: Single monorepo env with all dependencies
- [ ] Test Strategy 2: Full isolation (6 separate venvs)
- [ ] Test Strategy 3: Grouped (3 venvs: lightweight/ML/web)
- [ ] Test Strategy 4: Layered with pip-tools
- [ ] Measure disk space, install time for each
- [ ] Test IDE/Copilot integration for each

### Phase 3: Decision (Week 2)
- [ ] Create comparison matrix with real measurements
- [ ] Identify winning strategy or hybrid approach
- [ ] Document per-project recommendations
- [ ] Draft implementation plan
- [ ] Get stakeholder feedback
- [ ] Finalize decision document

## Acceptance Criteria

- [ ] All projects analyzed individually
- [ ] Logical groupings identified and justified
- [ ] All strategies tested hands-on with actual projects
- [ ] Quantitative metrics collected (disk space, install time, memory)
- [ ] Per-project recommendations documented
- [ ] Decision approved: which projects share envs, which stay isolated
- [ ] Implementation issues created (#114, #115, #116, #117)

## Expected Outcome Example

**Recommended Strategy**: Grouped Virtual Environments

- **Environment 1: "core"** → Classification, Model, ConfigLoad, Sources
  - Justification: All lightweight, zero/minimal dependencies, developed together
  
- **Environment 2: "ml"** → Scoring (when ML dependencies added)
  - Justification: Future heavy ML deps, GPU-specific, may need pinned torch versions
  
- **Environment 3: "web"** → Client/Backend
  - Justification: Web framework stack, independent dev cycle, unrelated to ML

- **Development tools**: Either in each env OR shared base layer via pip-tools

## References

- [Tweag Blog - Python Monorepo Structure](https://www.tweag.io/)
- [Graphite Docs - Python Monorepos](https://graphite.dev/)
- [pip-tools workflow](https://jamescooke.info/)
- [Python virtualenv documentation](https://docs.python.org/3/library/venv.html)
- [Stack Overflow - virtualenv redundancy](https://stackoverflow.com/)

---

**Related Issues**: This decision will inform implementation issues #114-#117
