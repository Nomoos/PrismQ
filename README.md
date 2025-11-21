# PrismQ - Content Production Platform

**Progressive Multi-Format Content Creation: Text → Audio → Video**

PrismQ is a comprehensive content production platform that transforms ideas into multi-format content through a sequential enrichment workflow. Each format builds on the previous one, enabling progressive publication across text, audio, and video platforms.

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
- **[Proposals](./_meta/proposals/)** - Architecture and design proposals
  - [Module Reorganization](./_meta/proposals/module-reorganization.md)
- **[Documentation](./_meta/docs/)** - Project-wide documentation
  - [Storytelling Guide](./_meta/docs/STORYTELLING_GUIDE.md)

### Workflow Documentation
- **[WORKFLOW.md](./WORKFLOW.md)** - Complete state machine documentation
  - Workflow phases and state transitions
  - Progressive enrichment model
  - Quality gates and best practices

## 🏗️ Project Structure

```
PrismQ/
├── T/                  # Text Generation Pipeline
│   ├── Idea/          # Idea development
│   ├── Script/        # Script drafting and review
│   ├── Title/         # Title optimization
│   ├── Publishing/    # Text publishing
│   ├── Rewiew/        # Review and editing
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
├── _meta/             # Project-wide metadata
│   ├── docs/         # Documentation
│   ├── research/     # Research documents
│   └── proposals/    # Design proposals
└── WORKFLOW.md        # State machine documentation
```

## 🚀 Quick Start

1. **Explore a Pipeline**: Start with [T/README.md](./T/README.md) to understand text generation
2. **Review Workflow**: Read [WORKFLOW.md](./WORKFLOW.md) for the complete state machine
3. **Check Research**: Browse [_meta/research/](./_meta/research/) for strategic insights
4. **Use Client**: See [Client/README.md](./Client/README.md) for web interface setup

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

**Start exploring**: [T Module](./T/README.md) | [A Module](./A/README.md) | [V Module](./V/README.md) | [Client](./Client/README.md) | [Workflow](./WORKFLOW.md)
