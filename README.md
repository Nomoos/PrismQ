# PrismQ - Content Production Platform

**Progressive Multi-Format Content Creation: Text → Audio → Video**

PrismQ is a comprehensive content production platform that transforms ideas into multi-format content through a sequential enrichment workflow. Each format builds on the previous one, enabling progressive publication across text, audio, and video platforms.

## 🔄 Next Steps & Parallel Execution

For the current sprint tasks and parallel execution commands, see:
- **[PARALLEL_RUN_NEXT.md](./_meta/issues/PARALLEL_RUN_NEXT.md)** - Current MVP sprint tasks and parallel execution plan
- **[PARALLEL_RUN_NEXT_FULL.md](./_meta/issues/PARALLEL_RUN_NEXT_FULL.md)** - Complete issue breakdown and worker assignments

## 📚 Main Modules

### [T - Text Generation Pipeline](./T/README.md)
**Namespace**: `PrismQ.T`

The foundation of the content pipeline. Transforms ideas into high-quality text content optimized for blogs, articles, and social media.

- Idea development and outlining
- Script drafting and review
- Text publishing and optimization
- SEO and metadata management

**[→ Explore T Module](./T/README.md)**

---

### [A - Audio Generation Pipeline](./A/README.md)
**Namespace**: `PrismQ.A`

The second stage of progressive enrichment. Transforms published text into professional audio content for podcast platforms.

- Voiceover recording and review
- Audio processing and normalization
- Podcast publishing and distribution
- Platform-specific optimization

**[→ Explore A Module](./A/README.md)**

---

### [V - Video Generation Pipeline](./V/README.md)
**Namespace**: `PrismQ.V`

The final stage of the workflow. Combines published audio with synchronized visuals for video platforms.

- Scene planning and keyframe design
- Visual asset generation
- Video assembly and editing
- Multi-platform video publishing (YouTube, TikTok, Instagram)

**[→ Explore V Module](./V/README.md)**

---

### [Client - Web Management Interface](./Client/README.md)
**Namespace**: `PrismQ.Client`

Web-based task queue management system for coordinating content production workflows.

- Task queue management (Backend/Frontend)
- Worker coordination
- Progress tracking and monitoring
- Production deployment ready

**[→ Explore Client Module](./Client/README.md)**

---

## 🎯 Sequential Workflow

```
IdeaInspiration
    ↓
Text Pipeline (T) → PublishedText
    ↓
Audio Pipeline (A) → PublishedAudio
    ↓
Video Pipeline (V) → PublishedVideo
    ↓
Analytics → IdeaInspiration (feedback loop)
```

Each format can be published independently:
- **Text-Only**: Fastest publication (hours to days)
- **Text + Audio**: Medium timeline (days to week)
- **Complete Multi-Format**: Full production (weeks)

## 📖 Documentation & Resources

### Research & Strategy
Foundational research and strategic planning documents.

- **[Research Documents](./_meta/research/)** - Content production research
  - [Content Production Workflow States](./_meta/research/content-production-workflow-states.md)
  - [YouTube Metadata Optimization](./_meta/research/youtube-metadata-optimization-smart-strategy.md)
  - [Popular Media Platforms Research](./_meta/research/popular-media-platforms-research.md)
  - [Content Platforms by Category and Age](./_meta/research/content-platforms-by-category-and-age.md)
  - [Teen Audience Platform Strategy](./_meta/research/teen-audience-platform-strategy.md)
- **[Audio Research](./A/Narrator/_meta/research/)** - Narrator and voiceover research
  - [Default Narrator Voice Profile](./A/Narrator/_meta/research/default-narrator-voice-profile.md) - First-person teen girl narrator template
- **[Proposals](./_meta/proposals/)** - Architecture and design proposals
  - [Module Reorganization](./_meta/proposals/module-reorganization.md)
- **[Documentation](./_meta/docs/)** - Project-wide documentation
  - [Database Objects](./_meta/docs/DATABASE.md) - Database schema and models reference
  - [Storytelling Guide](./_meta/docs/STORYTELLING_GUIDE.md)

### Workflow Documentation
- **[WORKFLOW.md](./_meta/WORKFLOW.md)** - Complete state machine documentation
  - Workflow phases and state transitions
  - Progressive enrichment model
  - Quality gates and best practices
  - **[Ultra-Clean Pipeline](./_meta/docs/workflow/ultra-clean-pipeline.md)** - Simplified execution flow representation

## 🏗️ Project Structure

```
PrismQ/
├── T/                  # Text Generation Pipeline
│   ├── Idea/          # Idea development
│   ├── Script/        # Script drafting and review
│   ├── Title/         # Title optimization
│   ├── Publishing/    # Text publishing
│   ├── Review/        # Review and editing
│   └── _meta/         # Module metadata
├── A/                  # Audio Generation Pipeline
│   ├── Voiceover/     # Voice recording
│   ├── Narrator/      # Narrator selection
│   ├── Normalized/    # Audio normalization
│   ├── Enhancement/   # Audio enhancement
│   ├── Publishing/    # Audio publishing
│   └── _meta/         # Module metadata
├── V/                  # Video Generation Pipeline
│   ├── Scene/         # Scene planning
│   ├── Keyframe/      # Keyframe generation
│   ├── Video/         # Video assembly
│   └── _meta/         # Module metadata
├── Client/            # Web Management Interface
│   ├── Backend/       # Backend API (TaskManager)
│   ├── Frontend/      # Frontend UI (TaskManager)
│   └── _meta/         # Module metadata
├── src/           # Environment & Configuration Management
│   ├── config.py      # Centralized configuration
│   ├── tests/         # Test suite
│   └── README.md      # src configuration documentation
└── _meta/             # Project-wide metadata
    ├── docs/         # Documentation
    ├── research/     # Research documents
    ├── proposals/    # Design proposals
    └── WORKFLOW.md   # State machine documentation
```

## 📁 Working Directory Structure

PrismQ uses a standardized working directory for all runtime data and outputs:

- **Windows**: `C:\PrismQ` (permanent MVP location)
- **Unix-like**: `~/PrismQ` (user's home directory)

The working directory contains:

```
C:\PrismQ/              # Working Directory (Windows) or ~/PrismQ (Unix)
├── .env                # Configuration (managed by src module)
├── db.s3db             # Database
├── T/{id}/             # Text content by ID
│   ├── {Platform}/    # Platform-specific output
│   └── Text/          # Final text content
├── A/{id}/             # Audio content by ID
│   ├── {Platform}/    # Platform-specific output
│   └── Audio/         # Final audio files
├── V/{id}/             # Video content by ID
│   ├── {Platform}/    # Platform-specific output
│   └── Video/         # Final video files
├── P/                  # Publishing records (by date hierarchy)
│   └── {Year}/{Month}/{day-range}/{day}/{hour}/{id}/{platform}/
└── M/                  # Metrics data (by date hierarchy)
    └── {Year}/{Month}/{day-range}/{day}/{hour}/{id}/Metrics/{platform}/
```

See [src/README.md](./src/README.md) for complete configuration documentation.

## 🚀 Quick Start

1. **Explore a Pipeline**: Start with [T/README.md](./T/README.md) to understand text generation
2. **Configure Environment**: See [src/README.md](./src/README.md) for setup
3. **Review Workflow**: Read [WORKFLOW.md](./_meta/WORKFLOW.md) for the complete state machine
4. **Check Research**: Browse [_meta/research/](./_meta/research/) for strategic insights
5. **Use Client**: See [Client/README.md](./Client/README.md) for web interface setup

## 🔄 State Machine Architecture

PrismQ implements a **comprehensive state machine workflow** across five core modules:

### Pipeline Flow: T → A → V → P → M

```
┌─────────────────────────────────────────────────────────────────┐
│                    PrismQ State Machine                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  T (Text)  →  A (Audio)  →  V (Video)  →  P (Publishing) -> M (Metrics/Analytics)                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Module Descriptions

1. **T (Text Generation)**
   - **Purpose**: Transform ideas into high-quality text content
   - **State Machine**: 16-stage iterative workflow with co-improvement cycles
   - **Key States**: Idea.Creation → Title.Draft → Script.Draft → Reviews → Improvements → Refinements → Publishing
   - **Quality Gates**: Title acceptance, script acceptance, readability validation
   - **Output**: SEO-optimized published text
   - **structure inside working directory** T/{id}/{Platform}, T/{id}/Text (there will live finished text)
   - **[📄 View T State Machine Documentation](./T/STATE_MACHINE.md)** *(Coming Soon)*

2. **A (Audio Generation)**
   - **Purpose**: Convert published text into professional audio content
   - **State Machine**: Voice generation, enhancement, and podcast publishing *(To Be Implemented)*
   - **Input**: Published text from T module
   - **Output**: Professional audio files, podcast episodes
   - **structure inside working directory** A/{id}/{Platform}, A/{id}/Audio
   - **[📄 View A State Machine Documentation](./A/STATE_MACHINE.md)** *(Coming Soon)*

3. **V (Video Generation)**
   - **Purpose**: Combine audio with visuals for video platforms
   - **State Machine**: Scene planning, keyframe generation, video assembly *(To Be Implemented)*
   - **Input**: Published audio from A module
   - **Output**: Platform-optimized videos (YouTube, TikTok, Instagram)
   - **structure inside working directory** V/{id}/{Platform}, V/{id}/Video
   - **[📄 View V State Machine Documentation](./V/STATE_MACHINE.md)** *(Coming Soon)*

4. **P (Publishing)**
   - **Purpose**: Bulk distribution across platforms after content completion
   - **State Machine**: Multi-platform publishing, scheduling, cross-posting *(To Be Implemented)*
   - **Input**: Completed content from T, A, V modules
   - **Output**: Published content across all target platforms
   - **structure inside working directory** P/{Year}/{Month}/{00-10/10-20/20-end}/{day}/{hour}/{id}/{platform}
   - **[📄 View P State Machine Documentation](./P/STATE_MACHINE.md)** *(Coming Soon)*

5. **M (Metrics/Analytics)**
   - **Purpose**: Monitor published content performance
   - **Type**: Meta-module (monitors published content from T/A/V/P)
   - **Functions**: Performance tracking of published content, KPI collection, engagement metrics, A/B testing results
   - **Output**: Insights feeding back to idea generation
   - **Feedback loop for Inspiration** 
    - **Collect performance data from published things** 
   - **structure inside working directory** M/{Year}/{Month}/{00-10/10-20/20-end}/{day}/{hour}/{id}/Metrics/{platform}
   - **[📄 View M State Machine Documentation](./M/STATE_MACHINE.md)** *(Coming Soon)*

### State Machine Principles

- **Sequential Pipeline**: T → A → V → P (each stage builds on previous)
- **Quality Gates**: Explicit acceptance criteria at each transition
- **Iterative Refinement**: Loops and feedback cycles within each module
- **Progressive Publication**: Release at any stage based on goals
- **Cross-Module Observability**: M module tracks metrics across all stages
- **Version Tracking**: Dynamic versioning (v1, v2, v3+) with unlimited iterations

### Current Implementation Status

✅ **T Module**: Complete 16-stage iterative workflow with MVP documentation  
🔄 **A Module**: State machine design in progress  
🔄 **V Module**: State machine design in progress  
🔄 **P Module**: Architecture planning phase  
🔄 **M Module**: Metrics framework definition phase

---

## 🔄 Progressive Enrichment Model

PrismQ uses a **sequential format enrichment** approach:

1. **Text First**: Quick publication, SEO benefits, immediate reach
2. **Audio Second**: Enhanced engagement, podcast distribution
3. **Video Last**: Maximum impact, platform optimization

Each stage uses the previous format as its foundation:
- Audio reads from **published text** (not draft scripts)
- Video syncs to **published audio** (not raw voiceover)
- Analytics from each format inform future content

## 📊 Key Features

- ✅ **Progressive Publication**: Release content at each stage
- ✅ **Quality Gates**: Review and approval at each transition
- ✅ **Format Optimization**: Platform-specific processing
- ✅ **Analytics Integration**: Performance data feeds back to ideation
- ✅ **Flexible Workflow**: Stop at any stage based on goals
- ✅ **Namespace Organization**: Clear module boundaries

## 📄 License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ

---

**Start exploring**: [T Module](./T/README.md) | [A Module](./A/README.md) | [V Module](./V/README.md) | [Client](./Client/README.md) | [Workflow](./_meta/WORKFLOW.md)
