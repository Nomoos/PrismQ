# Story Model Versioning and Translation System - Analysis Report

**Date**: 2025-11-21  
**Author**: PrismQ Development Team  
**Status**: Proposal Analysis  
**Related**: T/Script Module Versioning, Content Production Pipeline

---

## Executive Summary

This report analyzes the proposed Story model for managing text content versions and translations in the PrismQ content production system. The model aims to provide a unified approach for tracking content iterations, managing translations across multiple languages, and maintaining a clear lineage of content evolution.

**Key Findings:**
- ✅ The proposed model addresses critical needs for version tracking and i18n
- ⚠️ Single `isPublished` flag insufficient for multi-platform publishing (blog, podcast, YouTube, TikTok, Instagram)
- ⚠️ Some design decisions require careful consideration for scalability
- 💡 Alternative approaches better fit PrismQ's progressive enrichment model (Text → Audio → Video)
- 🔄 Integration with existing T/Script versioning needs clarification
- 🎯 Recommended: Multi-platform publication state tracking instead of boolean flags
- 🔧 **State Machine (FSM/DFA) integration recommended** for workflow enforcement and audit trail

---

## Key Insights from PrismQ Workflow Analysis

### Multi-Platform Publishing Requirements

The PrismQ workflow follows a **progressive enrichment model** where content flows through three publication stages:

1. **Text Publication (Phase 1)**: Blog, Medium, Substack, LinkedIn, Twitter
2. **Audio Publication (Phase 2)**: Spotify, Apple Podcasts, SoundCloud, Audible
3. **Video Publication (Phase 3)**: YouTube, TikTok, Instagram Reels

**Critical Finding**: A single `isPublished` boolean flag is **insufficient** for tracking this multi-stage, multi-platform workflow. The Story model must support:

- ✅ **Platform-specific publication timestamps** (publishedText, publishedAudio, publishedVideo)
- ✅ **Per-platform metadata** (URLs, status, publish dates for each specific platform)
- ✅ **Progressive enrichment tracking** (identify stories at each stage: text-only, text+audio, fully enriched)
- ✅ **Workflow state mapping** (integration with existing PrismQ states: PublishedText → PublishedAudio → PublishedVideo)

### Translation Model Clarification

**`parentId` Definition**: The original story ID from which all translations are derived. For the original story, `parentId` typically references itself (self-referential) or uses a logical group identifier.

**Examples**:
- Original English story: `id = "story-001"`, `parentId = "story-001"` (self-referential)
- Czech translation: `id = "story-002"`, `parentId = "story-001"`, `langId = "cs"`
- German translation: `id = "story-003"`, `parentId = "story-001"`, `langId = "de"`

All translations share the same `parentId`, enabling queries like "get all languages for story-001".

---

## 1. Proposed Model Structure

```prisma
model Story {
  id         String   @id @default(cuid())

  /// The "parent" story this is derived from.
  /// Same for all translations and versions.
  parentId   String   // e.g. ID of the original English story or logical story group
  langId     String   // ISO code: "en", "cs", etc.
  version    Int      // Version number (starts at 1, increments)

  title      String
  text       String

  createdAt  DateTime @default(now())
  updatedAt  DateTime @updatedAt

  /// Optionally store the creator (AI, editor, translator)
  createdBy  String?  
  comment    String?  // Optional change reason or review notes
}
```

### Model Characteristics

- **Flat Structure**: All versions and translations stored in single table
- **Composite Identifier**: parentId + langId + version uniquely identifies each story variant
- **No Relations**: No formal foreign key relationships defined
- **Prisma-Style**: Uses Prisma ORM syntax (currently system uses PHP/MySQL)
- **Translation Model**: `parentId` represents the original story ID from which all translations are derived

---

## 2. Detailed Analysis

### 2.1 Strengths (PROS)

#### ✅ Simplicity
- **Flat structure** is easy to understand and query
- **No complex joins** needed for basic operations
- Minimal learning curve for developers

#### ✅ Flexibility
- `parentId` represents the original story ID (source for all translations)
- `comment` field allows arbitrary metadata
- Easy to add new language/version combinations

#### ✅ Translation Support
- Clear `langId` field for language identification
- All translations share same `parentId` for grouping
- Supports ISO language codes (en, cs, de, etc.)

#### ✅ Version Tracking
- Simple integer versioning (1, 2, 3...)
- Linear version progression per language
- Easy to fetch latest version: `MAX(version)`

#### ✅ Audit Trail
- `createdAt`/`updatedAt` timestamps track changes
- `createdBy` identifies who created each version
- `comment` field for change documentation

#### ✅ Query Patterns
Simple queries for common use cases:
```sql
-- Get all versions of a story in English
SELECT * FROM Story 
WHERE parentId = 'xyz' AND langId = 'en' 
ORDER BY version DESC;

-- Get latest version for all languages
SELECT * FROM Story s1
WHERE version = (
  SELECT MAX(version) 
  FROM Story s2 
  WHERE s2.parentId = s1.parentId 
  AND s2.langId = s1.langId
);

-- Get specific version
SELECT * FROM Story 
WHERE parentId = 'xyz' AND langId = 'en' AND version = 2;
```

---

### 2.2 Weaknesses (CONS)

#### ⚠️ Data Redundancy
- **Problem**: Full text stored for every version
- **Impact**: Storage grows linearly with versions × languages
- **Example**: 10 languages × 5 versions = 50 full text copies
- **Scale**: For 1000 stories: 50,000 text records

**Cost Analysis:**
```
Average story size: 5KB
Storage per story: 5KB × 50 versions/translations = 250KB
For 1000 stories: 250MB (vs. ~5MB with diff-based approach)
```

#### ⚠️ No Diff Tracking
- Cannot see **what changed** between versions
- Difficult to understand version evolution
- No way to generate changelogs automatically
- Manual comparison required for version analysis

#### ⚠️ Missing Relationships
- No formal `parent` relationship defined
- Cannot enforce referential integrity
- Risk of orphaned versions if parent deleted
- No CASCADE delete behavior

#### ⚠️ Version Conflicts
- **Race condition**: Two editors create version 3 simultaneously
- No locking or optimistic concurrency control
- `version` field not unique alone (needs compound unique constraint)
- Manual conflict resolution required

#### ⚠️ Limited Metadata
- No structured metadata about changes
- `comment` is free-text (hard to query/analyze)
- Missing: change type, change category, review status
- No link to review/approval workflow

#### ⚠️ No Status Tracking
- Cannot track workflow state (draft, review, published)
- All versions have equal status
- No way to track publication across multiple platforms (blog, podcast, YouTube, TikTok, Instagram)
- Single `publishedAt` timestamp insufficient for multi-platform publishing
- Conflicts with existing PrismQ workflow states (PublishedText, PublishedAudio, PublishedVideo)

#### ⚠️ Query Performance
- Getting latest version requires `MAX()` aggregate
- Finding all languages requires full table scan
- No indexes defined in model
- Grows expensive as versions accumulate

#### ⚠️ Technology Mismatch
- **Current Stack**: PHP + MySQL
- **Proposed Model**: Prisma (Node.js/TypeScript)
- Requires technology migration or parallel systems
- Prisma not compatible with existing PHP backend

---

## 3. Comparison with Existing System

### 3.1 Current T/Script Versioning (Python)

The existing system (documented in `T/Script/STRUCTURE_AND_VERSIONING.md`) uses a different approach:

```python
@dataclass
class ScriptVersion:
    version_number: int
    script_text: str
    length_seconds: Optional[int]
    created_at: str
    created_by: str
    changes_from_previous: str  # ← Diff description
    review_score: Optional[int]  # ← Quality metric
    notes: str
```

**Key Differences:**

| Feature | Proposed Story Model | Current T/Script |
|---------|---------------------|------------------|
| **Storage** | Database table | In-memory/JSON |
| **Diff Tracking** | ❌ No | ✅ Yes (`changes_from_previous`) |
| **Quality Metrics** | ❌ No | ✅ Yes (`review_score`) |
| **Metadata** | Limited | Rich (length, scores, detailed notes) |
| **Translation** | ✅ Yes (`langId`) | ❌ No |
| **Parent Grouping** | ✅ Yes (`parentId`) | ❌ No |
| **Persistence** | Database | File/Memory |
| **Technology** | Prisma/SQL | Python dataclass |

---

## 4. Use Case Analysis

### 4.1 Supported Use Cases ✅

#### UC1: Create New Translation
```sql
INSERT INTO Story (id, parentId, langId, version, title, text, createdBy)
VALUES ('s2', 'parent1', 'cs', 1, 'Czech Title', 'Czech text...', 'translator-ai');
```
**Status**: ✅ Fully supported

#### UC2: Create New Version
```sql
-- Get max version first
SELECT MAX(version) FROM Story WHERE parentId = 'parent1' AND langId = 'en';
-- Insert new version
INSERT INTO Story (id, parentId, langId, version, title, text, createdBy, comment)
VALUES ('s3', 'parent1', 'en', 3, 'Updated Title', 'Updated text...', 'editor', 'Fixed typos');
```
**Status**: ✅ Supported (requires manual version number management)

#### UC3: Get Latest Version for Language
```sql
SELECT * FROM Story 
WHERE parentId = 'parent1' AND langId = 'en'
ORDER BY version DESC 
LIMIT 1;
```
**Status**: ✅ Fully supported

#### UC4: List All Languages Available
```sql
SELECT DISTINCT langId FROM Story WHERE parentId = 'parent1';
```
**Status**: ✅ Fully supported

---

### 4.2 Challenging Use Cases ⚠️

#### UC5: Show What Changed Between Versions
```sql
-- Can only fetch both versions, manual diff required
SELECT text FROM Story WHERE parentId = 'p1' AND langId = 'en' AND version IN (2, 3);
```
**Status**: ⚠️ Requires client-side diff algorithm  
**Impact**: Cannot generate automated changelogs

#### UC6: Track Version Lineage
```
Want: "Version 3 is based on version 2, which improved version 1"
```
**Status**: ❌ No explicit parent-child version relationship  
**Workaround**: Use comment field (unstructured)

#### UC7: Concurrent Version Creation
```
Editor A: Creates version 3 at 10:00
Editor B: Creates version 3 at 10:01
Result: Constraint violation or data corruption
```
**Status**: ❌ No concurrency control  
**Solution needed**: Optimistic locking or version number generation

#### UC8: Publish Specific Version
```
Want: Mark version 3 as "published", keep version 4 as "draft"
```
**Status**: ❌ No status field  
**Impact**: Cannot integrate with PrismQ workflow states

#### UC9: Version Approval Workflow
```
Want: Version 2 "pending review" → "approved" → "published"
```
**Status**: ❌ No workflow state tracking  
**Impact**: Cannot integrate with existing T/Rewiew modules

#### UC10: Find All Draft Versions Across All Stories
```sql
-- Cannot do this without status field
SELECT * FROM Story WHERE status = 'draft';
```
**Status**: ❌ Impossible with current model

#### UC11: Track Multi-Platform Publication
```
Want: Story published to blog (text), then Spotify (audio), then YouTube (video)
Need: Track each platform separately with timestamps and metadata
```
**Status**: ❌ Single `publishedAt` timestamp insufficient  
**Impact**: Cannot track PrismQ progressive enrichment workflow (Text → Audio → Video)

#### UC12: Query Stories by Platform
```sql
-- Find all stories published to YouTube
SELECT * FROM Story WHERE published_video IS NOT NULL;

-- Find stories published to text but not audio yet
SELECT * FROM Story WHERE published_text IS NOT NULL AND published_audio IS NULL;
```
**Status**: ❌ Impossible without platform-specific fields  
**Impact**: Cannot manage multi-platform publishing pipeline

---

## 5. Alternative Approaches

### 5.1 Option A: Enhanced Flat Model (Recommended)

**Add these fields to proposed model:**

```prisma
model Story {
  id         String   @id @default(cuid())
  parentId   String   // Original story ID (source for all translations)
  langId     String   
  version    Int      
  
  // Existing fields
  title      String
  text       String
  
  // ADDITIONS:
  status     String   // draft, review, approved, published
  basedOnVersionId String?  // ID of previous version (lineage)
  changeDescription String? // What changed (structured)
  changeType String? // typo_fix, content_update, major_rewrite
  reviewScore Int?    // Integration with T/Rewiew
  isLatest   Boolean  @default(false) // Performance optimization
  
  // Multi-platform publication tracking (PrismQ workflow integration)
  publishedText   DateTime? // Published to blog/Medium/Substack
  publishedAudio  DateTime? // Published to Spotify/Apple Podcasts
  publishedVideo  DateTime? // Published to YouTube/TikTok/Instagram
  publicationState JSON? // Detailed per-platform status: {blog: {status, url}, podcast: {status, url}, youtube: {...}}
  
  createdAt  DateTime @default(now())
  updatedAt  DateTime @updatedAt
  createdBy  String?  
  comment    String?  
  
  // INDEXES for performance
  @@unique([parentId, langId, version])
  @@index([parentId, isLatest])
  @@index([status])
  @@index([langId])
  @@index([publishedText])
  @@index([publishedAudio])
  @@index([publishedVideo])
}
```

**Benefits:**
- ✅ Maintains simplicity of flat model
- ✅ Adds workflow state tracking
- ✅ Adds version lineage
- ✅ Improves query performance
- ✅ Integrates with existing systems
- ✅ **Multi-platform publication tracking** (blog, podcast, YouTube, TikTok, Instagram)
- ✅ **Aligns with PrismQ progressive enrichment model** (Text → Audio → Video)

**Drawbacks:**
- Still has data redundancy
- Still requires full text storage
- Table grows large over time
- Multiple timestamp fields (but necessary for multi-platform publishing)

---

### 5.2 Option B: Normalized Version Model

**Separate tables for better normalization:**

```prisma
// Parent story (logical grouping)
model StoryParent {
  id          String   @id @default(cuid())
  canonicalLang String  // Primary language
  createdAt   DateTime @default(now())
  stories     StoryLanguage[]
}

// Language variant (all versions of one language)
model StoryLanguage {
  id          String   @id @default(cuid())
  parentId    String
  parent      StoryParent @relation(fields: [parentId], references: [id], onDelete: Cascade)
  langId      String
  latestVersionId String?
  versions    StoryVersion[]
  
  @@unique([parentId, langId])
}

// Individual version
model StoryVersion {
  id          String   @id @default(cuid())
  languageId  String
  language    StoryLanguage @relation(fields: [languageId], references: [id], onDelete: Cascade)
  version     Int
  
  title       String
  text        String
  status      String   // draft, review, published
  
  basedOnId   String?  // Previous version
  basedOn     StoryVersion? @relation("VersionLineage", fields: [basedOnId], references: [id])
  derivedVersions StoryVersion[] @relation("VersionLineage")
  
  changeDescription String?
  reviewScore Int?
  
  createdAt   DateTime @default(now())
  createdBy   String?
  publishedAt DateTime?
  
  @@unique([languageId, version])
  @@index([status])
}
```

**Benefits:**
- ✅ Strong referential integrity
- ✅ CASCADE deletes work correctly
- ✅ Clear version lineage with self-reference
- ✅ Can enforce business rules at DB level
- ✅ Better query optimization potential

**Drawbacks:**
- ❌ More complex queries (requires joins)
- ❌ Steeper learning curve
- ❌ More tables to manage
- ❌ Still stores full text per version

---

### 5.3 Option C: Diff-Based Storage (Most Efficient)

**Store only differences between versions:**

```prisma
model StoryBase {
  id          String   @id @default(cuid())
  parentId    String
  langId      String
  baseText    String   // Original version 1
  baseTitle   String
  createdAt   DateTime @default(now())
  versions    StoryDiff[]
  
  @@unique([parentId, langId])
}

model StoryDiff {
  id          String   @id @default(cuid())
  baseId      String
  base        StoryBase @relation(fields: [baseId], references: [id], onDelete: Cascade)
  version     Int
  
  // Store ONLY the diff, not full text
  titleDiff   String?  // JSON patch for title
  textDiff    String?  // JSON patch or unified diff
  
  status      String
  changeDescription String?
  reviewScore Int?
  
  createdAt   DateTime @default(now())
  createdBy   String?
  publishedAt DateTime?
  
  @@unique([baseId, version])
  @@index([status])
}

// Materialized view for current versions (performance)
model StoryMaterialized {
  id          String   @id
  parentId    String
  langId      String
  version     Int
  title       String   // Reconstructed
  text        String   // Reconstructed
  lastUpdated DateTime
  
  @@unique([parentId, langId, version])
  @@index([parentId, langId])
}
```

**Benefits:**
- ✅ **Massive storage savings** (90%+ for typical edits)
- ✅ Built-in diff information
- ✅ Can reconstruct any version
- ✅ Perfect for audit trails
- ✅ Scales to thousands of versions

**Drawbacks:**
- ❌ Complex reconstruction logic needed
- ❌ Slower read performance (must apply diffs)
- ❌ Requires diff algorithm implementation
- ❌ Harder to debug/inspect data
- ⚠️ Need materialized views for performance

---

### 5.4 Option D: Hybrid Approach (Best Balance)

**Combine approaches for optimal balance:**

```prisma
model Story {
  id          String   @id @default(cuid())
  parentId    String   // Original story ID (source for all translations)
  langId      String
  version     Int
  
  // Full text for easy access
  title       String
  text        String
  
  // Diff from previous (optional, for analysis)
  previousVersionId String?
  previousVersion Story? @relation("VersionChain", fields: [previousVersionId], references: [id])
  nextVersions    Story[] @relation("VersionChain")
  changesSummary  String? // Structured JSON: {added: X, removed: Y, modified: Z}
  
  // Workflow integration
  status      String   // draft, review, approved, published
  workflowState String? // Maps to PrismQ workflow states
  reviewScore Int?
  
  // Multi-platform publication tracking (PrismQ progressive enrichment model)
  publishedText   DateTime? // Text publication (blog, Medium, Substack, LinkedIn)
  publishedAudio  DateTime? // Audio publication (Spotify, Apple Podcasts, SoundCloud)
  publishedVideo  DateTime? // Video publication (YouTube, TikTok, Instagram Reels)
  publicationState JSON? // Detailed per-platform status: {
                        //   text: {blog: {...}, medium: {...}, substack: {...}},
                        //   audio: {spotify: {...}, apple_podcasts: {...}, soundcloud: {...}},
                        //   video: {youtube: {...}, tiktok: {...}, instagram: {...}}
                        // }
  
  // Performance optimization
  isLatest    Boolean  @default(false)
  
  // Metadata
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
  createdBy   String?
  comment     String?
  
  @@unique([parentId, langId, version])
  @@index([parentId, isLatest])
  @@index([status])
  @@index([langId])
  @@index([createdAt])
  @@index([publishedText])
  @@index([publishedAudio])
  @@index([publishedVideo])
}
```

**Benefits:**
- ✅ Simple queries for common cases (full text available)
- ✅ Diff information for analysis (changesSummary)
- ✅ Version lineage tracking
- ✅ Workflow integration
- ✅ **Multi-platform publication tracking** (replaces single isPublished flag)
- ✅ **Progressive enrichment support** (Text → Audio → Video)
- ✅ **Platform-specific metadata** via publicationState JSON
- ✅ Reasonable storage (accept redundancy for simplicity)

**Drawbacks:**
- Still stores full text (but acceptable for most use cases)
- Slightly more complex than original proposal
- Need to maintain isLatest flag
- Multiple publication timestamps (but required for multi-platform workflow)

---

## 6. State Machine Integration (FSM/DFA)

### 6.1 Why State Machines for Story Workflow?

The Story model should incorporate **Finite State Machine (FSM)** principles to enforce PrismQ's workflow integrity. This ensures:

- ✅ **Valid state transitions only** (prevent invalid jumps)
- ✅ **Workflow enforcement** (can't publish without review)
- ✅ **Audit trail** (complete state transition history)
- ✅ **Rollback capability** (revert to previous states)
- ✅ **Parallel workflows** (different states for text/audio/video)

### 6.2 PrismQ Workflow State Machine

Based on `WORKFLOW.md`, the complete state machine includes:

```
States (22 total):
├── IdeaInspiration (entry)
├── Idea (composite: Creation → Outline → Title)
├── ScriptDraft
├── ScriptReview
├── ScriptApproved
├── TextPublishing
├── PublishedText ← First publication checkpoint
├── AnalyticsReviewText
├── Voiceover
├── VoiceoverReview
├── VoiceoverApproved
├── AudioPublishing
├── PublishedAudio ← Second publication checkpoint
├── AnalyticsReviewAudio
├── ScenePlanning
├── KeyframePlanning
├── KeyframeGeneration
├── VideoAssembly
├── VideoReview
├── VideoFinalized
├── PublishPlanning
├── PublishedVideo ← Third publication checkpoint
├── AnalyticsReviewVideo
└── Archived (terminal)
```

**Key Characteristics:**
- **Entry State**: IdeaInspiration
- **Terminal State**: Archived
- **Composite State**: Idea (has sub-states)
- **Checkpoints**: PublishedText, PublishedAudio, PublishedVideo

### 6.3 State Machine Implementation Approaches

#### Approach A: Enum-Based Simple FSM

**Add state field with enum validation:**

```prisma
model Story {
  id          String   @id @default(cuid())
  parentId    String
  langId      String
  version     Int
  
  // Content
  title       String
  text        String
  
  // State machine
  currentState String  // Enum: IdeaInspiration, ScriptDraft, PublishedText, etc.
  
  // Multi-platform publication tracking
  publishedText   DateTime?
  publishedAudio  DateTime?
  publishedVideo  DateTime?
  
  // ... other fields
}
```

**SQL Implementation:**

```sql
CREATE TABLE stories (
    id VARCHAR(36) PRIMARY KEY,
    parent_id VARCHAR(36) NOT NULL,
    lang_id VARCHAR(5) NOT NULL,
    version INT NOT NULL,
    
    title VARCHAR(500) NOT NULL,
    text LONGTEXT NOT NULL,
    
    -- State machine
    current_state ENUM(
        'IdeaInspiration',
        'Idea',
        'ScriptDraft', 
        'ScriptReview',
        'ScriptApproved',
        'TextPublishing',
        'PublishedText',
        'AnalyticsReviewText',
        'Voiceover',
        'VoiceoverReview',
        'VoiceoverApproved',
        'AudioPublishing',
        'PublishedAudio',
        'AnalyticsReviewAudio',
        'ScenePlanning',
        'KeyframePlanning',
        'KeyframeGeneration',
        'VideoAssembly',
        'VideoReview',
        'VideoFinalized',
        'PublishPlanning',
        'PublishedVideo',
        'AnalyticsReviewVideo',
        'Archived'
    ) DEFAULT 'IdeaInspiration',
    
    -- Publication checkpoints
    published_text TIMESTAMP NULL,
    published_audio TIMESTAMP NULL,
    published_video TIMESTAMP NULL,
    
    UNIQUE KEY unique_version (parent_id, lang_id, version),
    INDEX idx_current_state (current_state)
);
```

**Pros:**
- ✅ Simple to implement
- ✅ Database-level validation
- ✅ Easy queries by state

**Cons:**
- ❌ No transition validation (can jump to any state)
- ❌ No state history tracking
- ❌ Limited to single linear workflow

---

#### Approach B: State History with Transition Table

**Track complete state history:**

```sql
-- Main stories table
CREATE TABLE stories (
    id VARCHAR(36) PRIMARY KEY,
    parent_id VARCHAR(36) NOT NULL,
    lang_id VARCHAR(5) NOT NULL,
    version INT NOT NULL,
    
    title VARCHAR(500) NOT NULL,
    text LONGTEXT NOT NULL,
    
    -- Current state
    current_state VARCHAR(50) NOT NULL DEFAULT 'IdeaInspiration',
    
    -- Publication tracking
    published_text TIMESTAMP NULL,
    published_audio TIMESTAMP NULL,
    published_video TIMESTAMP NULL,
    publication_state JSON NULL,
    
    UNIQUE KEY unique_version (parent_id, lang_id, version),
    INDEX idx_current_state (current_state)
);

-- State transition history
CREATE TABLE story_state_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    story_id VARCHAR(36) NOT NULL,
    from_state VARCHAR(50) NOT NULL,
    to_state VARCHAR(50) NOT NULL,
    transitioned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    transitioned_by VARCHAR(255),
    transition_reason TEXT,
    metadata JSON COMMENT 'Additional transition data',
    
    FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE,
    INDEX idx_story (story_id),
    INDEX idx_to_state (to_state),
    INDEX idx_transitioned_at (transitioned_at)
) ENGINE=InnoDB;

-- Valid state transitions (FSM rules)
CREATE TABLE story_state_transitions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    from_state VARCHAR(50) NOT NULL,
    to_state VARCHAR(50) NOT NULL,
    is_valid BOOLEAN DEFAULT TRUE,
    requires_approval BOOLEAN DEFAULT FALSE,
    validation_rules JSON COMMENT 'Conditions for transition',
    
    UNIQUE KEY unique_transition (from_state, to_state),
    INDEX idx_from (from_state)
) ENGINE=InnoDB;

-- Populate valid transitions from WORKFLOW.md
INSERT INTO story_state_transitions (from_state, to_state, requires_approval) VALUES
    ('IdeaInspiration', 'Idea', FALSE),
    ('IdeaInspiration', 'Archived', FALSE),
    ('Idea', 'ScriptDraft', FALSE),
    ('Idea', 'IdeaInspiration', FALSE),
    ('Idea', 'Archived', FALSE),
    ('ScriptDraft', 'ScriptReview', FALSE),
    ('ScriptDraft', 'Idea', FALSE),
    ('ScriptDraft', 'Archived', FALSE),
    ('ScriptReview', 'ScriptApproved', TRUE),  -- Requires approval
    ('ScriptReview', 'ScriptDraft', FALSE),
    ('ScriptApproved', 'TextPublishing', FALSE),
    ('TextPublishing', 'PublishedText', FALSE),
    ('PublishedText', 'Voiceover', FALSE),
    ('PublishedText', 'AnalyticsReviewText', FALSE),
    ('PublishedText', 'Archived', FALSE),
    ('Voiceover', 'VoiceoverReview', FALSE),
    ('VoiceoverReview', 'VoiceoverApproved', TRUE),
    ('VoiceoverApproved', 'AudioPublishing', FALSE),
    ('AudioPublishing', 'PublishedAudio', FALSE),
    ('PublishedAudio', 'ScenePlanning', FALSE),
    ('PublishedAudio', 'AnalyticsReviewAudio', FALSE),
    ('ScenePlanning', 'KeyframePlanning', FALSE),
    ('KeyframePlanning', 'KeyframeGeneration', FALSE),
    ('KeyframeGeneration', 'VideoAssembly', FALSE),
    ('VideoAssembly', 'VideoReview', FALSE),
    ('VideoReview', 'VideoFinalized', TRUE),
    ('VideoFinalized', 'PublishPlanning', FALSE),
    ('PublishPlanning', 'PublishedVideo', FALSE),
    ('PublishedVideo', 'AnalyticsReviewVideo', FALSE),
    ('AnalyticsReviewVideo', 'Archived', FALSE);
```

**State Transition Trigger:**

```sql
DELIMITER //

CREATE TRIGGER story_state_transition_validate
BEFORE UPDATE ON stories
FOR EACH ROW
BEGIN
    DECLARE valid_transition INT;
    
    -- Check if state changed
    IF NEW.current_state != OLD.current_state THEN
        -- Validate transition is allowed
        SELECT COUNT(*) INTO valid_transition
        FROM story_state_transitions
        WHERE from_state = OLD.current_state
          AND to_state = NEW.current_state
          AND is_valid = TRUE;
        
        IF valid_transition = 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Invalid state transition';
        END IF;
        
        -- Log state transition
        INSERT INTO story_state_history (story_id, from_state, to_state, transitioned_by)
        VALUES (NEW.id, OLD.current_state, NEW.current_state, NEW.created_by);
    END IF;
END//

DELIMITER ;
```

**Pros:**
- ✅ **Complete audit trail** of all state changes
- ✅ **Enforced valid transitions** at database level
- ✅ **Rollback capability** (view history)
- ✅ **Metadata per transition** (who, why, when)
- ✅ **Query state history** for analytics

**Cons:**
- ❌ More complex implementation
- ❌ Additional tables to manage
- ❌ Performance overhead for validation

---

#### Approach C: Parallel State Machines (Recommended)

**Separate state machines for each content type:**

```sql
CREATE TABLE stories (
    id VARCHAR(36) PRIMARY KEY,
    parent_id VARCHAR(36) NOT NULL,
    lang_id VARCHAR(5) NOT NULL,
    version INT NOT NULL,
    
    title VARCHAR(500) NOT NULL,
    text LONGTEXT NOT NULL,
    
    -- Parallel state machines (progressive enrichment)
    text_state ENUM(
        'draft', 'review', 'approved', 'publishing', 'published', 'archived'
    ) DEFAULT 'draft',
    
    audio_state ENUM(
        'not_started', 'voiceover', 'review', 'approved', 'publishing', 'published', 'archived'
    ) DEFAULT 'not_started',
    
    video_state ENUM(
        'not_started', 'planning', 'production', 'review', 'approved', 'publishing', 'published', 'archived'
    ) DEFAULT 'not_started',
    
    -- Overall workflow state (computed or managed)
    workflow_state VARCHAR(50) COMMENT 'Master state from WORKFLOW.md',
    
    -- Publication tracking (tied to state transitions)
    published_text TIMESTAMP NULL COMMENT 'Set when text_state = published',
    published_audio TIMESTAMP NULL COMMENT 'Set when audio_state = published',
    published_video TIMESTAMP NULL COMMENT 'Set when video_state = published',
    publication_state JSON NULL,
    
    UNIQUE KEY unique_version (parent_id, lang_id, version),
    INDEX idx_text_state (text_state),
    INDEX idx_audio_state (audio_state),
    INDEX idx_video_state (video_state),
    INDEX idx_workflow_state (workflow_state)
);

-- State transition history (for all three state machines)
CREATE TABLE story_state_transitions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    story_id VARCHAR(36) NOT NULL,
    state_type ENUM('text', 'audio', 'video', 'workflow') NOT NULL,
    from_state VARCHAR(50) NOT NULL,
    to_state VARCHAR(50) NOT NULL,
    transitioned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    transitioned_by VARCHAR(255),
    metadata JSON,
    
    FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE,
    INDEX idx_story (story_id),
    INDEX idx_state_type (state_type),
    INDEX idx_to_state (to_state)
);
```

**State Management Logic:**

```python
class StoryStateMachine:
    """Manage parallel state machines for text, audio, video"""
    
    # Text state machine
    TEXT_TRANSITIONS = {
        'draft': ['review', 'archived'],
        'review': ['approved', 'draft', 'archived'],
        'approved': ['publishing', 'review', 'archived'],
        'publishing': ['published', 'approved', 'archived'],
        'published': ['archived'],
        'archived': []
    }
    
    # Audio state machine (depends on text being published)
    AUDIO_TRANSITIONS = {
        'not_started': ['voiceover', 'archived'],
        'voiceover': ['review', 'archived'],
        'review': ['approved', 'voiceover', 'archived'],
        'approved': ['publishing', 'review', 'archived'],
        'publishing': ['published', 'approved', 'archived'],
        'published': ['archived'],
        'archived': []
    }
    
    # Video state machine (depends on audio being published)
    VIDEO_TRANSITIONS = {
        'not_started': ['planning', 'archived'],
        'planning': ['production', 'archived'],
        'production': ['review', 'planning', 'archived'],
        'review': ['approved', 'production', 'archived'],
        'approved': ['publishing', 'review', 'archived'],
        'publishing': ['published', 'approved', 'archived'],
        'published': ['archived'],
        'archived': []
    }
    
    def can_transition(self, state_type: str, from_state: str, to_state: str) -> bool:
        """Check if transition is valid"""
        transitions = {
            'text': self.TEXT_TRANSITIONS,
            'audio': self.AUDIO_TRANSITIONS,
            'video': self.VIDEO_TRANSITIONS
        }
        return to_state in transitions[state_type].get(from_state, [])
    
    def can_start_audio(self, text_state: str) -> bool:
        """Audio can only start after text is published"""
        return text_state == 'published'
    
    def can_start_video(self, audio_state: str) -> bool:
        """Video can only start after audio is published"""
        return audio_state == 'published'
    
    def compute_workflow_state(self, text_state: str, audio_state: str, video_state: str) -> str:
        """Map parallel states to master workflow state"""
        if video_state == 'published':
            return 'PublishedVideo'
        elif audio_state == 'published':
            return 'PublishedAudio'
        elif text_state == 'published':
            return 'PublishedText'
        elif text_state == 'publishing':
            return 'TextPublishing'
        elif text_state == 'approved':
            return 'ScriptApproved'
        elif text_state == 'review':
            return 'ScriptReview'
        elif text_state == 'draft':
            return 'ScriptDraft'
        else:
            return 'IdeaInspiration'
```

**Pros:**
- ✅ **Parallel workflows** (text/audio/video independent)
- ✅ **Progressive enrichment** naturally modeled
- ✅ **Can publish text without audio/video**
- ✅ **Clear dependencies** (audio needs text, video needs audio)
- ✅ **Simpler state machines** (fewer states each)
- ✅ **Better query performance** (separate indexes)

**Cons:**
- Need to maintain 3 state machines
- More complex state management logic
- Computed workflow_state needs synchronization

---

### 6.4 Recommended State Machine Design

**Recommendation**: **Approach C (Parallel State Machines)** with state history tracking

**Rationale:**
1. **Aligns with PrismQ progressive enrichment** (Text → Audio → Video)
2. **Each content type has independent lifecycle**
3. **Clear publication checkpoints** (publishedText, publishedAudio, publishedVideo)
4. **Flexible**: Can publish text-only or text+audio without video
5. **Maintainable**: Simpler state machines easier to reason about

**Implementation Priority:**

**Phase 1**: Basic parallel states
```sql
ALTER TABLE stories ADD COLUMN text_state VARCHAR(20) DEFAULT 'draft';
ALTER TABLE stories ADD COLUMN audio_state VARCHAR(20) DEFAULT 'not_started';
ALTER TABLE stories ADD COLUMN video_state VARCHAR(20) DEFAULT 'not_started';
```

**Phase 2**: State transition history
```sql
CREATE TABLE story_state_transitions (...);
```

**Phase 3**: State validation triggers
```sql
CREATE TRIGGER validate_text_state_transition ...
CREATE TRIGGER validate_audio_state_transition ...
CREATE TRIGGER validate_video_state_transition ...
```

**Phase 4**: Application-level state machine
```python
# Implement StoryStateMachine class with validation
```

### 6.5 State Machine Query Examples

```sql
-- Get all stories in text review state
SELECT * FROM stories WHERE text_state = 'review';

-- Get stories published to text but not audio yet (progressive enrichment opportunity)
SELECT * FROM stories 
WHERE text_state = 'published' 
  AND audio_state = 'not_started';

-- Get fully enriched stories (all three formats published)
SELECT * FROM stories
WHERE text_state = 'published'
  AND audio_state = 'published'
  AND video_state = 'published';

-- Get state transition history for a story
SELECT * FROM story_state_transitions
WHERE story_id = 'story-123'
ORDER BY transitioned_at ASC;

-- Find stories stuck in review (no transition in 7 days)
SELECT s.*, sst.transitioned_at
FROM stories s
LEFT JOIN story_state_transitions sst ON s.id = sst.story_id
WHERE s.text_state = 'review'
  AND sst.transitioned_at < DATE_SUB(NOW(), INTERVAL 7 DAY);
```

### 6.6 State Machine Benefits for Story Model

1. **Workflow Enforcement**: Cannot publish without approval
2. **Audit Compliance**: Complete history of state changes
3. **Analytics**: Track time in each state, bottlenecks
4. **Rollback**: Can revert to previous states if needed
5. **Progressive Enrichment**: Clear checkpoints for each format
6. **Multi-Platform**: Separate tracking for blog, podcast, video
7. **Validation**: Prevent invalid state jumps at database level
8. **Reporting**: Dashboards showing content at each stage

---

## 7. Technology Stack Considerations

### 6.1 Current Stack: PHP + MySQL

**Implications:**
- Prisma models need conversion to SQL DDL
- No Prisma client available in PHP
- Manual SQL queries or use PHP ORM (Eloquent, Doctrine)

**SQL Equivalent of Proposed Model:**

```sql
CREATE TABLE stories (
    id VARCHAR(36) PRIMARY KEY,
    parent_id VARCHAR(36) NOT NULL COMMENT 'Original story ID (source for translations)',
    lang_id VARCHAR(5) NOT NULL,
    version INT NOT NULL,
    
    title TEXT NOT NULL,
    text LONGTEXT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    comment TEXT,
    
    UNIQUE KEY unique_version (parent_id, lang_id, version),
    INDEX idx_parent (parent_id),
    INDEX idx_lang (lang_id),
    INDEX idx_version (version),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Note**: This basic schema lacks multi-platform publication tracking. See **Option D (Hybrid Approach)** in Appendix A for the recommended enhanced schema.

---

### 6.2 Integration with Existing Systems

#### T/Script Python Module
- Currently uses Python dataclasses
- Stores versions in JSON/memory
- Need adapter layer to sync with database

**Potential Integration:**

```python
# Python side (T/Script)
class ScriptVersionDBAdapter:
    def save_to_db(self, script_version: ScriptVersion, parent_id: str, lang: str):
        """Save Python ScriptVersion to Story database"""
        story = {
            'parentId': parent_id,
            'langId': lang,
            'version': script_version.version_number,
            'title': '...',  # Extract from script
            'text': script_version.script_text,
            'createdBy': script_version.created_by,
            'comment': script_version.changes_from_previous
        }
        # Call PHP API or direct DB insert
        
    def load_from_db(self, parent_id: str, lang: str, version: int) -> ScriptVersion:
        """Load Story from DB into Python ScriptVersion"""
        # Fetch from DB, convert to ScriptVersion
```

#### Client Backend (PHP TaskManager)
- Add REST API endpoints for Story CRUD
- Implement in data-driven API framework
- Add to existing `api_endpoints` table

**Example API Endpoints:**

```
POST   /api/stories              # Create new story (v1)
POST   /api/stories/:id/versions # Create new version
GET    /api/stories/:parentId    # Get all versions/languages
GET    /api/stories/:parentId/latest/:lang # Get latest version
PUT    /api/stories/:id          # Update story
DELETE /api/stories/:id          # Delete version
```

---

## 8. Migration Considerations

### 8.1 From Current System to Proposed Model

**Phase 1: Parallel Implementation**
1. Add Story table to database
2. Keep existing T/Script Python versioning
3. Build adapter layer to sync both systems
4. Test with non-critical content

**Phase 2: Migration**
1. Export existing script versions from Python
2. Convert to Story format
3. Import into database
4. Validate data integrity

**Phase 3: Deprecation**
1. Update T/Script to use database directly
2. Remove old versioning code
3. Update documentation

---

### 8.2 Data Migration Script

```sql
-- Assuming existing script_versions table
INSERT INTO stories (id, parent_id, lang_id, version, title, text, created_at, created_by, comment)
SELECT 
    CONCAT(script_id, '-', lang_code, '-v', version_num) as id,
    script_id as parent_id,
    lang_code as lang_id,
    version_num as version,
    title,
    script_text as text,
    created_timestamp as created_at,
    creator as created_by,
    change_notes as comment
FROM legacy_script_versions;
```

---

## 9. Recommendations

### 9.1 Short-Term (Quick Wins)

**Recommendation**: Implement **Option D (Hybrid Approach)** with SQL

**Actions:**
1. ✅ Create SQL schema based on Hybrid model
2. ✅ Add to existing MySQL database
3. ✅ Implement REST API in PHP backend
4. ✅ Build Python adapter for T/Script integration
5. ✅ Add comprehensive indexes for performance
6. ✅ Document with examples

**Timeline**: 1-2 weeks

---

### 9.2 Medium-Term (Improvements)

**Enhance the basic model:**

1. **Add Status Workflow Integration**
   - Map to existing PrismQ workflow states
   - Add state transition validation
   - Integration with T/Rewiew modules

2. **Implement Change Tracking**
   - Add changesSummary JSON field
   - Auto-generate from text diffs
   - Enable changelog generation

3. **Performance Optimization**
   - Add materialized view for latest versions
   - Implement caching layer (Redis)
   - Add full-text search indexes

4. **Rich Metadata**
   - Add structured tags/categories
   - Link to review scores
   - Integration with publishing workflow

**Timeline**: 1-2 months

---

### 9.3 Long-Term (Advanced Features)

**Consider future enhancements:**

1. **Diff-Based Storage (Option C)**
   - Implement when version count grows large
   - Start with hybrid: store full text + diff
   - Migrate older versions to diff-only

2. **Version Branching**
   - Support experimental branches
   - Merge branches back to main
   - Git-like version tree

3. **Collaborative Editing**
   - Real-time conflict detection
   - Merge conflict resolution
   - Operational Transform or CRDT

4. **Advanced Analytics**
   - Version comparison dashboard
   - A/B testing integration
   - Performance metrics per version

**Timeline**: 6-12 months

---

## 10. Conclusion

### 10.1 Summary

The proposed Story model provides a **solid foundation** for version and translation management but requires **enhancements** for production use in PrismQ.

**Key Points:**
- ✅ Core concept is sound and addresses real needs
- ⚠️ Needs workflow state integration
- ⚠️ Missing some critical features for production
- ✅ Can be enhanced incrementally
- ⚠️ Technology stack mismatch (Prisma vs PHP/MySQL)

---

### 10.2 Decision Matrix

| Approach | Simplicity | Features | Performance | Storage | Recommendation |
|----------|-----------|----------|-------------|---------|----------------|
| **Original Proposal** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | Good start |
| **Option A: Enhanced Flat** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ✅ **Recommended** |
| **Option B: Normalized** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | Complex |
| **Option C: Diff-Based** | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | Future |
| **Option D: Hybrid** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ **Best Overall** |

---

### 10.3 Final Recommendation

**Adopt Option D (Hybrid Approach) with Parallel State Machines:**

1. **Phase 1**: Implement core Hybrid model in SQL
   - Add status, isLatest fields
   - **Add multi-platform publication tracking** (publishedText, publishedAudio, publishedVideo)
   - **Add parallel state machines** (text_state, audio_state, video_state)
   - Add publicationState JSON for detailed platform metadata
   - Create state transition history table
   - Create comprehensive indexes
   - Build REST API

2. **Phase 2**: Integrate with existing systems
   - Python adapter for T/Script
   - Workflow state mapping (Text → Audio → Video)
   - **Implement state machine validation** (FSM rules enforcement)
   - Review score integration
   - **Progressive enrichment pipeline support**
   - State transition triggers

3. **Phase 3**: Add advanced features
   - Change tracking/diffs
   - Analytics dashboard per platform
   - **State transition analytics** (time in each state, bottlenecks)
   - Performance optimizations
   - Cross-platform publishing orchestration
   - Rollback capabilities via state history

**Expected Outcomes:**
- ✅ Unified version management across PrismQ
- ✅ Full translation support (parentId = original story ID)
- ✅ Integration with existing workflows
- ✅ **Multi-platform publication tracking** (blog, podcast, YouTube, TikTok, Instagram)
- ✅ **Progressive enrichment support** (Text → Audio → Video)
- ✅ **Finite State Machine enforcement** (valid transitions only, audit trail)
- ✅ **Parallel state tracking** (independent text/audio/video lifecycles)
- ✅ Scalable for future growth
- ✅ Maintains simplicity while adding necessary features

---

## Appendix A: SQL Schema Reference

### Complete Hybrid Model SQL

```sql
CREATE TABLE stories (
    -- Primary identification
    id VARCHAR(36) PRIMARY KEY,
    parent_id VARCHAR(36) NOT NULL COMMENT 'Original story ID (source for all translations)',
    lang_id VARCHAR(5) NOT NULL COMMENT 'ISO 639-1 language code',
    version INT NOT NULL COMMENT 'Version number (1, 2, 3...)',
    
    -- Content
    title VARCHAR(500) NOT NULL,
    text LONGTEXT NOT NULL,
    
    -- Version lineage
    previous_version_id VARCHAR(36) NULL COMMENT 'Previous version for lineage',
    changes_summary JSON NULL COMMENT 'Structured diff summary',
    
    -- Workflow integration
    status ENUM('draft', 'review', 'approved', 'published') DEFAULT 'draft',
    workflow_state VARCHAR(100) NULL COMMENT 'PrismQ workflow state',
    review_score INT NULL COMMENT 'Score from T/Rewiew (0-100)',
    
    -- Multi-platform publication tracking (PrismQ progressive enrichment)
    published_text TIMESTAMP NULL COMMENT 'Text publication (blog, Medium, Substack, LinkedIn, Twitter)',
    published_audio TIMESTAMP NULL COMMENT 'Audio publication (Spotify, Apple Podcasts, SoundCloud, Audible)',
    published_video TIMESTAMP NULL COMMENT 'Video publication (YouTube, TikTok, Instagram Reels)',
    publication_state JSON NULL COMMENT 'Per-platform publication details: {text: {blog: {status, url, publishedAt}, medium: {...}}, audio: {spotify: {...}}, video: {youtube: {...}}}',
    
    -- Performance flags
    is_latest BOOLEAN DEFAULT FALSE COMMENT 'Latest version for this lang',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Metadata
    created_by VARCHAR(255) NULL COMMENT 'Creator identifier',
    comment TEXT NULL COMMENT 'Change notes',
    
    -- Constraints
    UNIQUE KEY unique_version (parent_id, lang_id, version),
    FOREIGN KEY fk_previous (previous_version_id) REFERENCES stories(id) ON DELETE SET NULL,
    
    -- Indexes for performance
    INDEX idx_parent (parent_id),
    INDEX idx_parent_latest (parent_id, is_latest),
    INDEX idx_lang (lang_id),
    INDEX idx_status (status),
    INDEX idx_created (created_at),
    INDEX idx_updated (updated_at),
    INDEX idx_review_score (review_score),
    INDEX idx_published_text (published_text),
    INDEX idx_published_audio (published_audio),
    INDEX idx_published_video (published_video),
    
    -- Full-text search
    FULLTEXT INDEX ft_content (title, text)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Story versions with translations and multi-platform publication tracking';

-- Triggers to maintain is_latest flag
DELIMITER //

CREATE TRIGGER story_after_insert
AFTER INSERT ON stories
FOR EACH ROW
BEGIN
    -- Mark this as latest for this parent+lang
    UPDATE stories 
    SET is_latest = FALSE 
    WHERE parent_id = NEW.parent_id 
      AND lang_id = NEW.lang_id 
      AND id != NEW.id;
    
    UPDATE stories 
    SET is_latest = TRUE 
    WHERE id = NEW.id;
END//

DELIMITER ;
```

---

## Appendix B: API Examples

### REST API Usage Examples

```bash
# Create first version of a story
curl -X POST http://api.prismq.com/stories \
  -H "Content-Type: application/json" \
  -d '{
    "parentId": "story-abc-123",
    "langId": "en",
    "version": 1,
    "title": "The Future of AI",
    "text": "In this article, we explore...",
    "createdBy": "ai-writer"
  }'

# Create Czech translation
curl -X POST http://api.prismq.com/stories \
  -H "Content-Type: application/json" \
  -d '{
    "parentId": "story-abc-123",
    "langId": "cs",
    "version": 1,
    "title": "Budoucnost AI",
    "text": "V tomto článku zkoumáme...",
    "createdBy": "translator-ai"
  }'

# Create new version (v2) of English story
curl -X POST http://api.prismq.com/stories \
  -H "Content-Type: application/json" \
  -d '{
    "parentId": "story-abc-123",
    "langId": "en",
    "version": 2,
    "title": "The Future of AI - Updated",
    "text": "In this updated article...",
    "previousVersionId": "story-en-v1-id",
    "changesSummary": {"type": "content_update", "reason": "Added new examples"},
    "createdBy": "editor",
    "comment": "Added 2024 examples and updated statistics"
  }'

# Get latest version for English
curl http://api.prismq.com/stories/story-abc-123/latest/en

# Get all versions of a story
curl http://api.prismq.com/stories/story-abc-123/versions

# Get all available languages
curl http://api.prismq.com/stories/story-abc-123/languages

# Compare two versions
curl http://api.prismq.com/stories/story-abc-123/compare?from=1&to=2&lang=en

# Update version status (legacy single publication)
curl -X PATCH http://api.prismq.com/stories/{id} \
  -H "Content-Type: application/json" \
  -d '{
    "status": "published"
  }'

# Publish to text platform (blog) - Progressive enrichment step 1
curl -X PATCH http://api.prismq.com/stories/{id}/publish/text \
  -H "Content-Type: application/json" \
  -d '{
    "publishedText": "2025-11-21T14:00:00Z",
    "publicationState": {
      "text": {
        "blog": {
          "status": "published",
          "url": "https://myblog.com/future-of-ai",
          "publishedAt": "2025-11-21T14:00:00Z"
        },
        "medium": {
          "status": "published",
          "url": "https://medium.com/@user/future-of-ai",
          "publishedAt": "2025-11-21T14:05:00Z"
        }
      }
    }
  }'

# Publish to audio platform (podcast) - Progressive enrichment step 2
curl -X PATCH http://api.prismq.com/stories/{id}/publish/audio \
  -H "Content-Type: application/json" \
  -d '{
    "publishedAudio": "2025-11-22T10:00:00Z",
    "publicationState": {
      "audio": {
        "spotify": {
          "status": "published",
          "url": "https://spotify.com/episode/xyz",
          "publishedAt": "2025-11-22T10:00:00Z"
        },
        "apple_podcasts": {
          "status": "published",
          "url": "https://podcasts.apple.com/episode/xyz",
          "publishedAt": "2025-11-22T10:15:00Z"
        }
      }
    }
  }'

# Publish to video platform (YouTube, TikTok) - Progressive enrichment step 3
curl -X PATCH http://api.prismq.com/stories/{id}/publish/video \
  -H "Content-Type: application/json" \
  -d '{
    "publishedVideo": "2025-11-25T12:00:00Z",
    "publicationState": {
      "video": {
        "youtube": {
          "status": "published",
          "url": "https://youtube.com/watch?v=xyz",
          "publishedAt": "2025-11-25T12:00:00Z"
        },
        "tiktok": {
          "status": "published",
          "url": "https://tiktok.com/@user/video/xyz",
          "publishedAt": "2025-11-25T12:30:00Z"
        },
        "instagram": {
          "status": "published",
          "url": "https://instagram.com/reel/xyz",
          "publishedAt": "2025-11-25T13:00:00Z"
        }
      }
    }
  }'

# Query stories by publication status
curl http://api.prismq.com/stories?publishedText=true&publishedAudio=false
# Returns: Stories published to text but not yet to audio

curl http://api.prismq.com/stories?publishedVideo=true
# Returns: Stories published to video platforms (fully enriched)
```

---

## Appendix C: Integration Code Examples

### Python Integration (T/Script Module)

```python
# File: T/Script/storage/story_db_adapter.py

from dataclasses import dataclass
from typing import Optional, List
import requests

@dataclass
class StoryDBAdapter:
    """Adapter to sync ScriptVersion with Story database"""
    
    api_base_url: str = "http://api.prismq.com"
    
    def save_script_version(
        self,
        script_version: 'ScriptVersion',
        parent_id: str,
        lang_id: str = "en",
        status: str = "draft"
    ) -> dict:
        """Save a ScriptVersion to Story database"""
        
        # Convert ScriptVersion to Story format
        story_data = {
            "parentId": parent_id,
            "langId": lang_id,
            "version": script_version.version_number,
            "title": self._extract_title(script_version.script_text),
            "text": script_version.script_text,
            "status": status,
            "reviewScore": script_version.review_score,
            "createdBy": script_version.created_by,
            "comment": script_version.changes_from_previous,
            "changesSummary": {
                "notes": script_version.notes,
                "length_seconds": script_version.length_seconds
            }
        }
        
        # Post to API
        response = requests.post(
            f"{self.api_base_url}/stories",
            json=story_data
        )
        response.raise_for_status()
        return response.json()
    
    def load_script_version(
        self,
        parent_id: str,
        lang_id: str,
        version: int
    ) -> 'ScriptVersion':
        """Load a Story from database into ScriptVersion"""
        
        response = requests.get(
            f"{self.api_base_url}/stories/{parent_id}/version/{version}",
            params={"lang": lang_id}
        )
        response.raise_for_status()
        story = response.json()
        
        # Convert to ScriptVersion
        return ScriptVersion(
            version_number=story['version'],
            script_text=story['text'],
            length_seconds=story.get('changesSummary', {}).get('length_seconds'),
            created_at=story['createdAt'],
            created_by=story['createdBy'],
            changes_from_previous=story['comment'] or '',
            review_score=story.get('reviewScore'),
            notes=story.get('changesSummary', {}).get('notes', '')
        )
    
    def get_all_versions(
        self,
        parent_id: str,
        lang_id: str = "en"
    ) -> List['ScriptVersion']:
        """Get all versions for a story"""
        
        response = requests.get(
            f"{self.api_base_url}/stories/{parent_id}/versions",
            params={"lang": lang_id}
        )
        response.raise_for_status()
        stories = response.json()
        
        return [
            self._story_to_script_version(story)
            for story in stories
        ]
    
    @staticmethod
    def _extract_title(script_text: str) -> str:
        """Extract title from script text (first line or first 100 chars)"""
        lines = script_text.strip().split('\n')
        if lines:
            return lines[0][:100]
        return script_text[:100]
    
    def _story_to_script_version(self, story: dict) -> 'ScriptVersion':
        """Convert story dict to ScriptVersion"""
        return ScriptVersion(
            version_number=story['version'],
            script_text=story['text'],
            length_seconds=story.get('changesSummary', {}).get('length_seconds'),
            created_at=story['createdAt'],
            created_by=story['createdBy'],
            changes_from_previous=story['comment'] or '',
            review_score=story.get('reviewScore'),
            notes=story.get('changesSummary', {}).get('notes', '')
        )

# Usage example
adapter = StoryDBAdapter()

# Save a script version
script_v1 = ScriptVersion(
    version_number=1,
    script_text="The future of AI...",
    length_seconds=145,
    created_at="2025-11-21T10:00:00Z",
    created_by="ai-writer",
    changes_from_previous="Initial version",
    review_score=75,
    notes="First draft"
)

adapter.save_script_version(
    script_v1,
    parent_id="story-ai-future",
    lang_id="en"
)

# Load back
loaded = adapter.load_script_version(
    parent_id="story-ai-future",
    lang_id="en",
    version=1
)
```

---

## Appendix D: Performance Benchmarks

### Query Performance Estimates

Based on table with 100,000 stories (10 versions × 5 languages average):

| Query | Without Indexes | With Indexes | Notes |
|-------|----------------|--------------|-------|
| Get latest version | ~500ms | ~5ms | Using `is_latest=TRUE` |
| Get all versions | ~200ms | ~10ms | Using `parent_id` index |
| List languages | ~300ms | ~15ms | Using `DISTINCT lang_id` |
| Full-text search | ~2s | ~50ms | Using FULLTEXT index |
| Get by status | ~800ms | ~20ms | Using `status` index |
| Version comparison | ~100ms | ~8ms | Using `version` index |

**Storage Estimates:**

```
Average story:
- Title: 100 chars = 100 bytes
- Text: 5000 chars = 5 KB
- Metadata: ~500 bytes
- Total per version: ~5.6 KB

For 1000 stories × 10 versions × 5 languages:
= 50,000 records × 5.6 KB = 280 MB

With indexes: +30% = 364 MB

Acceptable for MySQL/MariaDB
```

---

## Document Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-11-21 | 1.0 | Initial report creation | PrismQ Team |

---

**End of Report**
