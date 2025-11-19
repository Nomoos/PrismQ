# Archived

**Workflow Stage: Final Archive State**

## Overview

The **Archived** stage is the terminal state for content that has completed its active lifecycle. Content in this stage is preserved for reference and historical purposes but is no longer actively managed or promoted.

## Position in Workflow

```
[Any Stage] → Archived (Terminal State)
AnalyticsReview → Archived (Normal Flow)
```

## Purpose

Preserve completed content and production artifacts for:

- Historical reference
- Learning and retrospectives
- Asset reuse and repurposing
- Legal and compliance requirements
- Portfolio and showcase purposes

## Archive Categories

### Successful Completion
Content that has completed the full workflow:
```
IdeaInspiration → ... → AnalyticsReview → [Archived]
```

**Characteristics:**
- Full production cycle completed
- Published and reviewed
- Analytics data collected
- Learning documented
- Ready for long-term storage

### Early Termination
Content that was archived before completion:
```
[Any Stage] → [Archived]
```

**Reasons for Early Archive:**
- Concept no longer relevant
- Resource constraints
- Strategic pivot
- Quality issues unresolvable
- Duplicate/redundant content
- External factors (legal, ethical)

### Content Types

**Published Content**
- Completed videos/audio/text
- All platform versions
- Metadata and descriptions
- Analytics reports
- Performance data

**Production Assets**
- Scripts (all versions)
- Voiceover recordings
- Visual assets (keyframes, B-roll)
- Project files (video editor)
- Source files and raw materials

**Documentation**
- Idea development notes
- Research materials
- Review feedback
- Decision logs
- Learning summaries

## Archive Structure

### File Organization

```
Archived/
├── [Year]/
│   └── [Month]/
│       └── [ProjectID]/
│           ├── published/           # Final published content
│           │   ├── youtube/
│           │   ├── tiktok/
│           │   ├── instagram/
│           │   └── metadata.json
│           ├── production/          # Production files
│           │   ├── scripts/
│           │   ├── audio/
│           │   ├── video/
│           │   ├── visuals/
│           │   └── project_files/
│           ├── analytics/           # Performance data
│           │   ├── youtube_analytics.pdf
│           │   ├── tiktok_analytics.pdf
│           │   └── summary_report.md
│           ├── documentation/       # Notes and docs
│           │   ├── idea_notes.md
│           │   ├── script_reviews.md
│           │   ├── feedback_log.md
│           │   └── lessons_learned.md
│           └── archive_metadata.json
```

### Metadata Schema

```json
{
  "project_id": "PQ001",
  "title": "Digital Detective: The Vanishing Influencer",
  "archive_date": "2025-01-19T10:00:00Z",
  "archive_reason": "completed_lifecycle",
  "workflow_stages_completed": [
    "IdeaInspiration",
    "Idea",
    "Outline",
    "Skeleton",
    "Title",
    "ScriptDraft",
    "ScriptReview",
    "ScriptApproved",
    "Voiceover",
    "VoiceoverReview",
    "VoiceoverApproved",
    "ScenePlanning",
    "KeyframePlanning",
    "KeyframeGeneration",
    "VideoAssembly",
    "VideoReview",
    "VideoFinalized",
    "PublishPlanning",
    "Published",
    "AnalyticsReview"
  ],
  "last_active_stage": "AnalyticsReview",
  "platforms_published": ["YouTube", "TikTok", "Instagram"],
  "publication_date": "2025-01-05T14:00:00Z",
  "total_views": 15420,
  "total_engagement": 782,
  "performance_rating": "successful",
  "key_learnings": [
    "Strong opening hooks crucial for retention",
    "8-10 minute length optimal for this audience",
    "Mystery genre performs well with 25-34 demographic"
  ],
  "team_members": ["Creator A", "Editor B", "Reviewer C"],
  "tags": ["mystery", "true_crime", "digital", "investigation"],
  "archive_size_mb": 4850,
  "retention_period": "indefinite",
  "last_accessed": "2025-01-19T10:00:00Z"
}
```

## Archive Process

### Pre-Archive Checklist

**Content Verification**
- [ ] All final versions collected
- [ ] Platform URLs documented
- [ ] Analytics data exported
- [ ] Performance reports generated
- [ ] Learning documented

**Asset Collection**
- [ ] Master files gathered
- [ ] Source files collected
- [ ] Project files exported
- [ ] Documentation compiled
- [ ] Metadata complete

**Quality Control**
- [ ] File integrity verified
- [ ] Backups confirmed
- [ ] Metadata accurate
- [ ] Links and references working
- [ ] Compression appropriate

### Archive Execution

**Step 1: Collection**
```bash
# Gather all files from active locations
# Organize by archive structure
# Verify file completeness
```

**Step 2: Documentation**
```
Create archive metadata file
Generate project summary
Export analytics reports
Compile lessons learned
Document team credits
```

**Step 3: Storage**
```
Primary Archive: Cloud Storage (AWS S3, Google Cloud)
Secondary Backup: External Drive
Tertiary Backup: Cold Storage (optional)
```

**Step 4: Cleanup**
```
Remove from active production folders
Update project tracking systems
Archive email threads and communications
Close project management tasks
```

**Step 5: Indexing**
```
Add to searchable archive index
Tag with relevant keywords
Link related projects
Update portfolio/showcase (if applicable)
```

## Archive Access

### Access Levels

**Public Access**
- Published content (YouTube, TikTok, etc.)
- Portfolio showcase items
- Case studies and examples
- Public documentation

**Team Access**
- Production assets
- Full project files
- Internal documentation
- Performance analytics

**Restricted Access**
- Raw footage and takes
- Sensitive information
- Private communications
- Financial data

### Retrieval Process

**For Reference**
```
1. Search archive index
2. Locate project folder
3. Access needed files
4. Document retrieval in access log
```

**For Repurposing**
```
1. Identify reusable assets
2. Export from archive
3. Create derivative work folder
4. Link to original archive
5. Update archive metadata with usage
```

**For Learning**
```
1. Review project documentation
2. Study analytics and outcomes
3. Extract key learnings
4. Apply to new projects
5. Update best practices
```

## Archive Management

### Retention Policy

**Indefinite Retention**
- Published successful content
- High-performing assets
- Portfolio pieces
- Case studies

**Long-Term Retention (5-10 years)**
- Production assets
- Project files
- Most documentation
- Analytics data

**Short-Term Retention (1-3 years)**
- Draft versions
- Rejected takes
- Temporary files
- Communication logs

**Immediate Deletion**
- True temporary files
- Duplicate copies
- Personal/sensitive data (after anonymization)
- Legally required removals

### Storage Optimization

**Compression**
- Archive finished projects as compressed packages
- Use efficient compression (ZIP, 7Z, TAR.GZ)
- Balance compression ratio with access speed
- Maintain checksum for integrity

**Deduplication**
- Remove duplicate assets across projects
- Use reference links when possible
- Single source of truth for shared assets

**Tiered Storage**
- Hot: Recent/frequently accessed (SSD, Cloud)
- Warm: Occasionally accessed (HDD, Cloud)
- Cold: Rarely accessed (Tape, Glacier, Cold Cloud Storage)

## Learning Integration

### Post-Project Review

**What Went Well**
```
Process:
- [List successful process elements]

Content:
- [List successful content elements]

Team:
- [List successful team practices]
```

**What To Improve**
```
Process:
- [List process improvements needed]

Content:
- [List content improvements needed]

Team:
- [List team improvements needed]
```

**Action Items for Future**
```
1. [Specific action based on learning]
2. [Specific action based on learning]
3. [Specific action based on learning]
```

### Knowledge Base Updates

**Best Practices**
- Update templates based on learnings
- Refine processes based on experience
- Document successful techniques
- Share team knowledge

**Workflow Improvements**
- Identify bottlenecks resolved
- Document time-saving techniques
- Update standard operating procedures
- Improve quality gates

## Archive Statistics

### Project Metrics

```
Archive Statistics (Last 12 Months):
- Total Projects Archived: 45
- Successful Completions: 38 (84%)
- Early Terminations: 7 (16%)
- Total Storage Used: 2.3 TB
- Average Project Size: 51 GB

Performance Distribution:
- Exceptional (>150% target): 8 projects
- Successful (100-150% target): 22 projects
- Acceptable (75-100% target): 8 projects
- Below Target (<75%): 7 projects

Top Performing Genres:
1. Mystery/Investigation: Avg 12,500 views
2. Technology Explainer: Avg 9,800 views
3. True Crime: Avg 8,200 views
```

## Related Documentation

- [Content Production Workflow States](../_meta/research/content-production-workflow-states.md)
- [AnalyticsReview](../Publishing/AnalyticsReview/README.md) - Previous stage (typical)
- [IdeaInspiration](../IdeaInspiration/README.md) - Can loop back for new ideas

---

*Part of the PrismQ Content Production Workflow - Terminal State*
