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
**Impact**: Cannot integrate with existing T/Review modules

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
  reviewScore Int?    // Integration with T/Review
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
CREATE TABLE story_transition_rules (
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
INSERT INTO story_transition_rules (from_state, to_state, requires_approval) VALUES
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
        FROM story_transition_rules
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

### 7.1 Current Stack: PHP + MySQL

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

### 7.2 Integration with Existing Systems

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
   - Integration with T/Review modules

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

## 11. Enriched Model Analysis (S3 + Database Storage)

### 11.1 Overview: Enhanced Story Model with Relational Links

The enriched Story model introduces **relational connections** to other business entities and adopts a **hybrid storage strategy** (S3 + Database) for optimal performance and cost efficiency.

**Relationship Cardinality Clarifications:**

- **Story → Audience**: Many-to-One (many stories can target one audience)
- **Story → Idea**: Many-to-One (many stories/versions can derive from one idea)
- **Story → ChannelGroup**: Many-to-One (many stories can use one channel configuration)
- **Story → Language**: Many-to-One (many stories in one language)
- **Story → Parent Story**: Many-to-One (many translations reference one original story)
- **Story → State**: Many-to-One (many stories in one state)

**Key Design Decisions:**

1. **Parent is a Story**: `parentId` references the `stories` table itself (self-referential FK), NULL for originals
2. **Language as separate table**: `languages` table with ISO codes, descriptions
3. **Version with workflow pattern**: Sequential versions alternate between draft/review/improvement states
4. **States with M:N transitions**: `workflow_states` table with `state_transitions` M:N table defining valid state changes

**New Model Structure:**

```prisma
model Story {
  id              String   @id @default(cuid())

  /// Self-referential: parent is also a Story
  parentId        String?  // NULL for originals, references stories.id for translations
  parent          Story?   @relation("StoryTranslations", fields: [parentId], references: [id])
  translations    Story[]  @relation("StoryTranslations")
  
  channelGroupId  Int      // M:1 - Many stories use one channel config
  channelGroup    ChannelGroup @relation(fields: [channelGroupId], references: [id])
  
  audienceId      Int      // M:1 - Many stories target one audience
  audience        Audience @relation(fields: [audienceId], references: [id])
  
  languageId      Int      // M:1 - Many stories in one language (NEW: separate table)
  language        Language @relation(fields: [languageId], references: [id])
  
  version         Int      // Sequential: 1=draft, 2=review, 3=improved, 4=review, 5=improved...
  
  title           String
  text            String   // May be stored in S3 for large content
  
  ideaId          Int      // M:1 - Many stories/versions from one idea
  idea            Idea     @relation(fields: [ideaId], references: [id])
  
  stateId         Int      // M:1 - Many stories in one state
  state           WorkflowState @relation(fields: [stateId], references: [id])
  
  createdAt       DateTime @default(now())
  
  @@unique([ideaId, channelGroupId, languageId, version])
}

model Language {
  id          Int      @id @default(autoincrement())
  code        String   @unique  // ISO 639-1: "en", "cs", "de"
  name        String              // "English", "Czech", "German"
  nativeName  String              // "English", "Čeština", "Deutsch"
  isActive    Boolean  @default(true)
  stories     Story[]
}

model WorkflowState {
  id              Int      @id @default(autoincrement())
  name            String   @unique
  description     String?
  stateType       String   // "text", "audio", "video", "workflow"
  displayColor    String?
  isTerminal      Boolean  @default(false)
  
  stories         Story[]
  
  // M:N relationship for valid transitions
  transitionsFrom StateTransition[] @relation("FromState")
  transitionsTo   StateTransition[] @relation("ToState")
}

model StateTransition {
  id              Int      @id @default(autoincrement())
  fromStateId     Int
  fromState       WorkflowState @relation("FromState", fields: [fromStateId], references: [id])
  toStateId       Int
  toState         WorkflowState @relation("ToState", fields: [toStateId], references: [id])
  requiresApproval Boolean @default(false)
  
  @@unique([fromStateId, toStateId])
}
```

### 11.2 Key Enhancements

#### Enhancement 1: Parent ID Clarification (NULL for Originals)

**Change**: `parentId String?` with NULL for original stories

**Benefits:**
- ✅ **Clear distinction** between original and translated stories
- ✅ **Simplified queries**: `WHERE parentId IS NULL` finds all originals
- ✅ **No self-referential complexity**: Eliminates `parentId = id` pattern
- ✅ **Better data integrity**: Foreign key can reference stories table without circular dependency

**Query Patterns:**

```sql
-- Find all original stories (not translations)
SELECT * FROM stories WHERE parent_id IS NULL;

-- Find all translations of a specific story
SELECT * FROM stories WHERE parent_id = 'story-123';

-- Find story with all its translations
SELECT * FROM stories 
WHERE id = 'story-123' OR parent_id = 'story-123'
ORDER BY lang_id;
```

**Comparison with Previous Model:**

| Aspect | Previous (Self-Referential) | Enhanced (NULL for Originals) |
|--------|---------------------------|------------------------------|
| Original Story | `parentId = id` | `parentId = NULL` |
| Translation | `parentId = original_id` | `parentId = original_id` |
| Query Clarity | Complex (self-join or filter) | Simple (`IS NULL` check) |
| Data Integrity | Risk of orphans | Clear hierarchy |
| Foreign Key | Problematic (circular) | Self-ref with ON DELETE SET NULL |

**Updated Design with Self-Referential FK:**

```sql
CREATE TABLE stories (
    id VARCHAR(36) PRIMARY KEY,
    parent_id VARCHAR(36) NULL COMMENT 'NULL for originals, references stories.id for translations',
    
    -- Self-referential foreign key
    FOREIGN KEY (parent_id) REFERENCES stories(id) ON DELETE SET NULL,
    
    INDEX idx_parent (parent_id)
);
```

**Key Point**: Parent IS a Story (not a separate table), enabling proper self-referential relationship.

---

#### Enhancement 1b: Language as Separate Table (NEW)

**New Design**: Extract language to separate `languages` table instead of inline `langId` string

**Purpose**: 
- **Centralized language management**: Add/disable languages without touching story data
- **Metadata support**: Store language names, native names, directionality (LTR/RTL)
- **Referential integrity**: Prevent invalid language codes
- **Query optimization**: Better indexing and joins

**Languages Table:**

```sql
CREATE TABLE languages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(5) NOT NULL UNIQUE COMMENT 'ISO 639-1 code: en, cs, de',
    name VARCHAR(100) NOT NULL COMMENT 'English name: English, Czech, German',
    native_name VARCHAR(100) NOT NULL COMMENT 'Native name: English, Čeština, Deutsch',
    direction ENUM('ltr', 'rtl') DEFAULT 'ltr' COMMENT 'Text direction',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_code (code),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Populate with common languages
INSERT INTO languages (code, name, native_name, direction) VALUES
('en', 'English', 'English', 'ltr'),
('cs', 'Czech', 'Čeština', 'ltr'),
('de', 'German', 'Deutsch', 'ltr'),
('es', 'Spanish', 'Español', 'ltr'),
('fr', 'French', 'Français', 'ltr'),
('ar', 'Arabic', 'العربية', 'rtl');
```

**Stories Table Integration:**

```sql
ALTER TABLE stories 
ADD COLUMN language_id INT NOT NULL,
ADD FOREIGN KEY (language_id) REFERENCES languages(id),
ADD INDEX idx_language (language_id);
```

**Benefits:**
- ✅ **Data integrity**: Cannot use invalid language codes
- ✅ **Centralized management**: Add/disable languages in one place
- ✅ **Rich metadata**: Store language properties (direction, native names)
- ✅ **Better queries**: JOIN for language info instead of hardcoded strings
- ✅ **Normalization**: Reduces redundancy

**Query Examples:**

```sql
-- Find all stories in Czech
SELECT s.*, l.name as language_name, l.native_name
FROM stories s
JOIN languages l ON s.language_id = l.id
WHERE l.code = 'cs';

-- Count stories per language
SELECT l.code, l.name, COUNT(s.id) as story_count
FROM languages l
LEFT JOIN stories s ON l.id = s.language_id
GROUP BY l.id
ORDER BY story_count DESC;

-- Find all active languages with published stories
SELECT DISTINCT l.*
FROM languages l
JOIN stories s ON l.id = s.language_id
WHERE l.is_active = TRUE
  AND s.published_text IS NOT NULL;
```

**Comparison:**

| Aspect | Inline langId String | Separate Language Table |
|--------|---------------------|------------------------|
| Data Type | `VARCHAR(5)` | `INT (FK)` |
| Validation | Application level | Database level (FK) |
| Metadata | None | Name, native name, direction |
| Management | Hardcoded | Centralized CRUD |
| Query Performance | String comparison | Integer JOIN (faster) |
| Storage | 5 bytes per row | 4 bytes per row + language table |
| Extensibility | Limited | Easy to add properties |

---

#### Enhancement 2: Channel Group Integration

**New Field**: `channelGroupId Int`

**Cardinality**: Many-to-One (many stories use one channel configuration)

**Purpose**: Links story to channel configuration defining:
- **Language**: Primary language (en, cs, de, etc.)
- **Country**: Geographic targeting (US, CZ, DE, etc.)
- **Platform Mix**: Which platforms to publish to (blog + podcast, or blog + podcast + video)
- **Publication Strategy**: Text-only, Text+Audio, or Full Enrichment

**Channel Group Table (Inferred):**

```sql
CREATE TABLE channel_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    language VARCHAR(5) NOT NULL,  -- ISO 639-1 code
    country VARCHAR(2) NOT NULL,   -- ISO 3166-1 alpha-2
    platforms JSON NOT NULL,       -- {text: ['blog', 'medium'], audio: ['spotify'], video: ['youtube']}
    enrichment_level ENUM('text_only', 'text_audio', 'full') DEFAULT 'text_only',
    is_active BOOLEAN DEFAULT TRUE,
    
    INDEX idx_language (language),
    INDEX idx_country (country)
);
```

**Benefits:**
- ✅ **Centralized platform configuration**: Define once, reuse across stories
- ✅ **Multi-regional support**: Same story, different channels per region
- ✅ **Platform targeting**: Control which platforms per channel
- ✅ **Enrichment control**: Configure progressive enrichment per channel

**Example Use Cases:**

```sql
-- English stories for US audience (full enrichment)
INSERT INTO channel_groups (name, language, country, platforms, enrichment_level) VALUES
('US-English-Full', 'en', 'US', 
 '{"text": ["blog", "medium", "linkedin"], "audio": ["spotify", "apple"], "video": ["youtube", "tiktok"]}', 
 'full');

-- Czech stories for CZ audience (text + audio only)
INSERT INTO channel_groups (name, language, country, platforms, enrichment_level) VALUES
('CZ-Czech-Audio', 'cs', 'CZ', 
 '{"text": ["blog"], "audio": ["spotify"]}', 
 'text_audio');

-- German stories for DE audience (text only)
INSERT INTO channel_groups (name, language, country, platforms, enrichment_level) VALUES
('DE-German-Text', 'de', 'DE', 
 '{"text": ["blog", "medium"]}', 
 'text_only');
```

**Query Examples:**

```sql
-- Find all stories for US English channel
SELECT s.* FROM stories s
JOIN channel_groups cg ON s.channel_group_id = cg.id
WHERE cg.country = 'US' AND cg.language = 'en';

-- Stories that need full enrichment (text + audio + video)
SELECT s.* FROM stories s
JOIN channel_groups cg ON s.channel_group_id = cg.id
WHERE cg.enrichment_level = 'full'
  AND s.text_state = 'published'
  AND s.video_state != 'published';
```

---

#### Enhancement 3: Audience Segmentation

**New Field**: `audienceId Int`

**Cardinality**: Many-to-One (many stories can target ONE audience, but one audience can be targeted by MANY stories)

**Purpose**: Links story to audience segment for:
- **Targeting**: Which demographic sees this content
- **Personalization**: Tailor content to audience interests
- **Analytics**: Track performance per audience segment
- **A/B Testing**: Different versions for different audiences

**Audience Table (Inferred):**

```sql
CREATE TABLE audiences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    demographics JSON,  -- {age_range: '25-45', interests: ['tech', 'ai'], education: 'college+'}
    behavior JSON,      -- {engagement_level: 'high', preferred_format: 'video', reading_time: '5-10min'}
    is_active BOOLEAN DEFAULT TRUE,
    
    INDEX idx_name (name)
);
```

**Benefits:**
- ✅ **Personalized content**: Tailor messaging per audience
- ✅ **Performance analytics**: Track which content resonates with which audience
- ✅ **A/B testing**: Same story, different versions per audience
- ✅ **Campaign management**: Target specific segments

**Example Use Cases:**

```sql
-- Create audience segments
INSERT INTO audiences (name, description, demographics, behavior) VALUES
('Tech Enthusiasts', 'Early adopters interested in AI and technology',
 '{"age_range": "25-45", "interests": ["AI", "tech", "innovation"]}',
 '{"engagement_level": "high", "preferred_format": "video"}'),
 
('Business Leaders', 'C-level executives and entrepreneurs',
 '{"age_range": "35-55", "interests": ["business", "strategy", "leadership"]}',
 '{"engagement_level": "medium", "preferred_format": "text"}'),
 
('Students', 'University students and recent graduates',
 '{"age_range": "18-25", "interests": ["learning", "career", "tech"]}',
 '{"engagement_level": "high", "preferred_format": "short_video"}');

-- Query stories for specific audience
SELECT s.* FROM stories s
JOIN audiences a ON s.audience_id = a.id
WHERE a.name = 'Tech Enthusiasts'
  AND s.text_state = 'published';
```

---

#### Enhancement 4: Idea Integration (Many-to-One Relationship)

**New Field**: `ideaId Int`

**Cardinality**: Many-to-One (ONE idea can spawn MANY stories/versions/translations, but each story derives from ONE idea)

**Clarification**: This is NOT 1:1 as initially stated. One idea can generate:
- Multiple language versions (English, Czech, German stories from same idea)
- Multiple story versions (v1, v2, v3... from same idea)
- Multiple audience-targeted variations (Tech audience, Business audience from same idea)

**Purpose**: Links story to its original creative concept/inspiration

**Benefits:**
- ✅ **Traceability**: Track from idea to published content
- ✅ **Analytics**: See which ideas generate successful content
- ✅ **Workflow integration**: Seamless transition from Idea → Script → Story
- ✅ **Content planning**: Understand idea-to-story conversion rate

**Idea Table (Inferred from T/Idea module):**

```sql
CREATE TABLE ideas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    source VARCHAR(100),       -- YouTube, Twitter, News, Original
    inspiration_url VARCHAR(500),
    score INT,                 -- Idea quality score
    category VARCHAR(100),
    tags JSON,
    status ENUM('inspiration', 'creation', 'outline', 'title', 'approved', 'script_started', 'published') DEFAULT 'inspiration',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_status (status),
    INDEX idx_score (score)
);
```

**Workflow Integration:**

```
Idea (T/Idea module)
    ↓ [1:1]
Story (versioned text content)
    ↓ [1:N progressive enrichment]
PublishedText → PublishedAudio → PublishedVideo
```

**Query Examples:**

```sql
-- Find all stories derived from a specific idea
SELECT s.* FROM stories s
WHERE s.idea_id = 123;

-- Track idea-to-publication conversion
SELECT 
    i.id,
    i.title,
    COUNT(s.id) as story_versions,
    MAX(s.version) as latest_version,
    MAX(CASE WHEN s.text_state = 'published' THEN 1 ELSE 0 END) as is_published
FROM ideas i
LEFT JOIN stories s ON i.id = s.idea_id
GROUP BY i.id;

-- Find ideas that haven't been turned into stories yet
SELECT i.* FROM ideas i
LEFT JOIN stories s ON i.id = s.idea_id
WHERE s.id IS NULL
  AND i.status = 'approved'
ORDER BY i.score DESC;
```

**1:1 Relationship Enforcement:**

```sql
-- Unique constraint to enforce 1:1 per language and version
ALTER TABLE stories
ADD UNIQUE KEY unique_idea_channel_version (idea_id, channel_group_id, version);

-- Note: If supporting A/B testing with different audiences, use:
-- ADD UNIQUE KEY unique_idea_channel_audience_version (idea_id, channel_group_id, audience_id, version);

-- Note: This restricts to one story per idea globally
-- For multiple languages/audiences per idea, use the composite constraint above instead:
-- ALTER TABLE stories
-- ADD UNIQUE KEY unique_idea_channel_audience_version (idea_id, channel_group_id, audience_id, version);
```

---

#### Enhancement 5: State Management with M:N Transitions

**New Field**: `stateId Int` - Reference to current state

**Cardinality**: Many-to-One (many stories in one state)

**Purpose**: External state management for FSM integration with **M:N state transitions** defining valid state changes

**Benefits:**
- ✅ **Flexible state system**: States defined in separate table
- ✅ **Dynamic workflow**: Add new states without schema changes
- ✅ **State metadata**: Store additional state information (description, color, icon)
- ✅ **M:N transitions**: Define which states can transition to which other states
- ✅ **Workflow enforcement**: Prevent invalid state jumps at database level

**State Table:**

```sql
CREATE TABLE workflow_states (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    state_type ENUM('text', 'audio', 'video', 'workflow') NOT NULL,
    description TEXT,
    display_color VARCHAR(7),  -- Hex color for UI
    display_icon VARCHAR(50),   -- Icon name for UI
    is_terminal BOOLEAN DEFAULT FALSE,
    sort_order INT,
    
    INDEX idx_state_type (state_type),
    INDEX idx_name (name)
) ENGINE=InnoDB;

-- Populate with PrismQ workflow states
INSERT INTO workflow_states (name, state_type, description, is_terminal, sort_order) VALUES
('draft', 'text', 'Initial draft state', FALSE, 1),
('review', 'text', 'Under review', FALSE, 2),
('improved', 'text', 'Improvements made after review', FALSE, 3),
('approved', 'text', 'Approved for publishing', FALSE, 4),
('published', 'text', 'Published to platforms', FALSE, 5),
('archived', 'text', 'Archived content', TRUE, 6);
```

**M:N State Transitions Table (NEW):**

```sql
CREATE TABLE state_transitions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    from_state_id INT NOT NULL,
    to_state_id INT NOT NULL,
    requires_approval BOOLEAN DEFAULT FALSE,
    description TEXT,
    
    FOREIGN KEY (from_state_id) REFERENCES workflow_states(id) ON DELETE CASCADE,
    FOREIGN KEY (to_state_id) REFERENCES workflow_states(id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_transition (from_state_id, to_state_id),
    INDEX idx_from_state (from_state_id),
    INDEX idx_to_state (to_state_id)
) ENGINE=InnoDB;

-- Populate valid state transitions
INSERT INTO state_transitions (from_state_id, to_state_id, requires_approval, description) VALUES
-- From draft
(1, 2, FALSE, 'Submit draft for review'),       -- draft → review
(1, 6, FALSE, 'Archive draft'),                 -- draft → archived

-- From review
(2, 3, FALSE, 'Request improvements'),          -- review → improved
(2, 4, TRUE, 'Approve content'),                -- review → approved (requires approval)
(2, 1, FALSE, 'Send back to draft'),            -- review → draft
(2, 6, FALSE, 'Archive during review'),         -- review → archived

-- From improved
(3, 2, FALSE, 'Resubmit for review'),           -- improved → review
(3, 6, FALSE, 'Archive improvements'),          -- improved → archived

-- From approved
(4, 5, FALSE, 'Publish approved content'),      -- approved → published
(4, 2, FALSE, 'Send back to review'),           -- approved → review
(4, 6, FALSE, 'Archive approved content'),      -- approved → archived

-- From published
(5, 6, FALSE, 'Archive published content'),     -- published → archived

-- Note: Terminal state 'archived' has no outgoing transitions
```

**Version Workflow Pattern:**

Versions follow a review-improvement cycle:
- **Version 1**: Initial draft (state: draft)
- **Version 2**: After first review (state: review or improved)
- **Version 3**: Improvements made (state: improved)
- **Version 4**: Second review (state: review)
- **Version 5**: Further improvements (state: improved)
- **Version N**: Final approved/published (state: approved/published)

**Query Examples:**

```sql
-- Find stories in specific state
SELECT s.*, ws.name as current_state
FROM stories s
JOIN workflow_states ws ON s.state_id = ws.id
WHERE ws.name = 'review';

-- Find valid next states for a story's current state
SELECT s.id, s.version, 
       ws_from.name as current_state,
       ws_to.name as possible_next_state,
       st.requires_approval
FROM stories s
JOIN workflow_states ws_from ON s.state_id = ws_from.id
JOIN state_transitions st ON ws_from.id = st.from_state_id
JOIN workflow_states ws_to ON st.to_state_id = ws_to.id
WHERE s.id = 'story-123';

-- Count stories per state with transition options
SELECT ws.name, ws.state_type, 
       COUNT(s.id) as story_count,
       GROUP_CONCAT(ws_next.name) as possible_transitions
FROM workflow_states ws
LEFT JOIN stories s ON ws.id = s.state_id
LEFT JOIN state_transitions st ON ws.id = st.from_state_id
LEFT JOIN workflow_states ws_next ON st.to_state_id = ws_next.id
GROUP BY ws.id
ORDER BY ws.sort_order;

-- Validate state transition before update
SELECT COUNT(*) as is_valid
FROM state_transitions
WHERE from_state_id = (SELECT state_id FROM stories WHERE id = 'story-123')
  AND to_state_id = 4; -- trying to move to 'approved'
-- Returns 1 if valid, 0 if invalid
```

**State Transition Trigger (Optional):**

```sql
DELIMITER //

CREATE TRIGGER validate_state_transition
BEFORE UPDATE ON stories
FOR EACH ROW
BEGIN
    DECLARE valid_transition INT;
    
    IF NEW.state_id != OLD.state_id THEN
        SELECT COUNT(*) INTO valid_transition
        FROM state_transitions
        WHERE from_state_id = OLD.state_id
          AND to_state_id = NEW.state_id;
        
        IF valid_transition = 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Invalid state transition';
        END IF;
    END IF;
END//

DELIMITER ;
```

---

### 11.3 S3 + Database Hybrid Storage Strategy

**Problem**: Large text content can bloat database, increase backup time, and slow queries.

**Solution**: Store large content in S3, keep metadata and small text in database.

**Implementation Approaches:**

#### Approach A: S3 for Large Content Only

```sql
CREATE TABLE stories (
    id VARCHAR(36) PRIMARY KEY,
    parent_id VARCHAR(36) NULL,
    channel_group_id INT NOT NULL,
    audience_id INT NOT NULL,
    idea_id INT NOT NULL UNIQUE,
    version INT NOT NULL,
    
    title VARCHAR(500) NOT NULL,
    
    -- Conditional storage
    text_preview TEXT,           -- First 1000 chars for preview/search
    text_s3_key VARCHAR(500),    -- S3 key if text is large
    text_size_bytes INT,         -- Original text size
    
    state_id INT NOT NULL,
    
    -- State machine fields
    text_state_id INT,
    audio_state_id INT,
    video_state_id INT,
    
    -- Publication tracking
    published_text TIMESTAMP NULL,
    published_audio TIMESTAMP NULL,
    published_video TIMESTAMP NULL,
    publication_state JSON,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (channel_group_id) REFERENCES channel_groups(id),
    FOREIGN KEY (audience_id) REFERENCES audiences(id),
    FOREIGN KEY (idea_id) REFERENCES ideas(id),
    FOREIGN KEY (state_id) REFERENCES workflow_states(id),
    
    UNIQUE KEY unique_story (idea_id, channel_group_id, version),
    INDEX idx_parent (parent_id),
    INDEX idx_channel (channel_group_id),
    INDEX idx_audience (audience_id),
    INDEX idx_state (state_id)
);
```

**Storage Logic:**

```python
class StoryStorage:
    """Hybrid storage strategy for stories"""
    
    THRESHOLD_BYTES = 10000  # 10KB threshold
    
    def save_story(self, story_data):
        text = story_data['text']
        text_size = len(text.encode('utf-8'))
        
        if text_size > self.THRESHOLD_BYTES:
            # Store in S3
            s3_key = f"stories/{story_data['id']}/v{story_data['version']}/text.txt"
            self.s3_client.put_object(
                Bucket='prismq-content',
                Key=s3_key,
                Body=text,
                ContentType='text/plain; charset=utf-8'
            )
            
            # Save metadata to database
            db_data = {
                **story_data,
                'text_preview': text[:1000],
                'text_s3_key': s3_key,
                'text_size_bytes': text_size,
                'text': None  # Don't store full text in DB
            }
        else:
            # Store in database
            db_data = {
                **story_data,
                'text_preview': text,
                'text_s3_key': None,
                'text_size_bytes': text_size
            }
        
        self.db.insert('stories', db_data)
    
    def get_story_text(self, story_id):
        """Retrieve full text from DB or S3"""
        story = self.db.query('SELECT * FROM stories WHERE id = ?', [story_id])
        
        if not story:
            raise ValueError(f"Story {story_id} not found")
        
        if story['text_s3_key']:
            # Fetch from S3 with error handling
            try:
                response = self.s3_client.get_object(
                    Bucket='prismq-content',
                    Key=story['text_s3_key']
                )
                return response['Body'].read().decode('utf-8')
            except self.s3_client.exceptions.NoSuchKey:
                # S3 object missing, fall back to preview
                print(f"Warning: S3 object {story['text_s3_key']} not found, using preview")
                return story['text_preview']
            except Exception as e:
                # Log error and fall back to preview
                print(f"Error fetching from S3: {e}")
                return story['text_preview']
        else:
            # Return from database
            return story['text_preview']
```

**Benefits:**
- ✅ **Cost optimization**: S3 cheaper than database storage
- ✅ **Performance**: Database queries faster without large text fields
- ✅ **Scalability**: Can store unlimited text size in S3
- ✅ **Backup efficiency**: Database backups smaller and faster
- ✅ **Search capability**: text_preview enables full-text search

**Drawbacks:**
- ⚠️ Additional complexity (two storage systems)
- ⚠️ Network latency for S3 fetches
- ⚠️ Need S3 lifecycle management
- ⚠️ Consistency challenges (DB + S3 sync)

---

#### Approach B: S3 for All Content (Recommended for Large Scale)

```sql
CREATE TABLE stories (
    id VARCHAR(36) PRIMARY KEY,
    parent_id VARCHAR(36) NULL,
    channel_group_id INT NOT NULL,
    audience_id INT NOT NULL,
    idea_id INT NOT NULL UNIQUE,
    version INT NOT NULL,
    
    title VARCHAR(500) NOT NULL,
    
    -- All content in S3
    s3_base_key VARCHAR(500) NOT NULL,  -- e.g., stories/abc123/v1/
    content_files JSON,                  -- {text: 'text.txt', audio: 'audio.mp3', video: 'video.mp4'}
    
    -- Search/preview data
    text_preview TEXT,                   -- First 1000 chars for search
    text_size_bytes INT,
    
    -- ... rest of fields
);
```

**S3 Structure:**

```
s3://prismq-content/
  stories/
    {story-id}/
      v1/
        text.txt           (full text content)
        metadata.json      (additional metadata)
        text.cs.txt        (Czech translation)
        text.de.txt        (German translation)
      v2/
        text.txt
        metadata.json
      audio/
        v1/
          audio.mp3
          transcript.txt
      video/
        v1/
          video.mp4
          subtitles.vtt
```

**Benefits:**
- ✅ **Unified storage**: All versions in same location
- ✅ **Version history**: Easy to access old versions
- ✅ **Multi-format**: Text, audio, video in same hierarchy
- ✅ **CDN integration**: Serve content directly from S3/CloudFront
- ✅ **Disaster recovery**: S3 versioning + replication

---

### 11.4 Complete Enriched Model SQL Schema

```sql
-- Languages table (NEW: separate table for language management)
CREATE TABLE languages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(5) NOT NULL UNIQUE COMMENT 'ISO 639-1: en, cs, de',
    name VARCHAR(100) NOT NULL COMMENT 'English name',
    native_name VARCHAR(100) NOT NULL COMMENT 'Native name',
    direction ENUM('ltr', 'rtl') DEFAULT 'ltr',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_code (code),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Populate common languages
INSERT INTO languages (code, name, native_name, direction) VALUES
('en', 'English', 'English', 'ltr'),
('cs', 'Czech', 'Čeština', 'ltr'),
('de', 'German', 'Deutsch', 'ltr'),
('es', 'Spanish', 'Español', 'ltr'),
('fr', 'French', 'Français', 'ltr'),
('ar', 'Arabic', 'العربية', 'rtl');

-- Channel Groups table
CREATE TABLE channel_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(2) NOT NULL COMMENT 'ISO 3166-1 alpha-2',
    platforms JSON NOT NULL,
    enrichment_level ENUM('text_only', 'text_audio', 'full') DEFAULT 'text_only',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_country (country),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Audiences table
CREATE TABLE audiences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    demographics JSON,
    behavior JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_name (name),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Ideas table
CREATE TABLE ideas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    source VARCHAR(100),
    inspiration_url VARCHAR(500),
    score INT,
    category VARCHAR(100),
    tags JSON,
    status ENUM('inspiration', 'creation', 'outline', 'title', 'approved', 'script_started', 'published') DEFAULT 'inspiration',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_status (status),
    INDEX idx_score (score)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Workflow States table
CREATE TABLE workflow_states (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    state_type ENUM('text', 'audio', 'video', 'workflow') NOT NULL,
    description TEXT,
    display_color VARCHAR(7),
    display_icon VARCHAR(50),
    is_terminal BOOLEAN DEFAULT FALSE,
    sort_order INT,
    
    INDEX idx_state_type (state_type),
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Populate workflow states
INSERT INTO workflow_states (name, state_type, description, is_terminal, sort_order) VALUES
('draft', 'text', 'Initial draft', FALSE, 1),
('review', 'text', 'Under review', FALSE, 2),
('improved', 'text', 'Improvements made', FALSE, 3),
('approved', 'text', 'Approved for publishing', FALSE, 4),
('published', 'text', 'Published to platforms', FALSE, 5),
('archived', 'text', 'Archived content', TRUE, 6);

-- State Transitions table (M:N relationship - NEW)
CREATE TABLE state_transitions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    from_state_id INT NOT NULL,
    to_state_id INT NOT NULL,
    requires_approval BOOLEAN DEFAULT FALSE,
    description TEXT,
    
    FOREIGN KEY (from_state_id) REFERENCES workflow_states(id) ON DELETE CASCADE,
    FOREIGN KEY (to_state_id) REFERENCES workflow_states(id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_transition (from_state_id, to_state_id),
    INDEX idx_from_state (from_state_id),
    INDEX idx_to_state (to_state_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Populate valid state transitions
INSERT INTO state_transitions (from_state_id, to_state_id, requires_approval, description) VALUES
(1, 2, FALSE, 'Submit for review'),          -- draft → review
(1, 6, FALSE, 'Archive draft'),              -- draft → archived
(2, 3, FALSE, 'Request improvements'),       -- review → improved
(2, 4, TRUE, 'Approve content'),             -- review → approved (requires approval)
(2, 1, FALSE, 'Back to draft'),              -- review → draft
(2, 6, FALSE, 'Archive'),                    -- review → archived
(3, 2, FALSE, 'Resubmit for review'),        -- improved → review
(3, 6, FALSE, 'Archive'),                    -- improved → archived
(4, 5, FALSE, 'Publish'),                    -- approved → published
(4, 2, FALSE, 'Back to review'),             -- approved → review
(4, 6, FALSE, 'Archive'),                    -- approved → archived
(5, 6, FALSE, 'Archive published content');  -- published → archived

-- Enhanced Stories table with S3 hybrid storage
CREATE TABLE stories (
    id VARCHAR(36) PRIMARY KEY,
    
    -- Self-referential hierarchy (parent IS a story)
    parent_id VARCHAR(36) NULL COMMENT 'NULL for originals, references stories.id for translations',
    
    -- Foreign keys to business entities (M:1 relationships)
    channel_group_id INT NOT NULL COMMENT 'M:1 - Many stories use one channel config',
    audience_id INT NOT NULL COMMENT 'M:1 - Many stories target one audience',
    language_id INT NOT NULL COMMENT 'M:1 - Many stories in one language',
    idea_id INT NOT NULL COMMENT 'M:1 - Many stories/versions from one idea',
    
    version INT NOT NULL COMMENT 'Sequential: 1=draft, 2=review, 3=improved, 4=review, 5=improved...',
    
    -- Content
    title VARCHAR(500) NOT NULL,
    text_preview TEXT COMMENT 'First 1000 chars or full text if small',
    text_s3_key VARCHAR(500) COMMENT 'S3 key for large content',
    text_size_bytes INT COMMENT 'Original text size',
    
    -- State management (single state for simplified model, or use parallel states)
    state_id INT NOT NULL COMMENT 'M:1 - Current workflow state',
    
    -- Multi-platform publication tracking
    published_text TIMESTAMP NULL COMMENT 'Text publication timestamp',
    published_audio TIMESTAMP NULL COMMENT 'Audio publication timestamp',
    published_video TIMESTAMP NULL COMMENT 'Video publication timestamp',
    publication_state JSON NULL COMMENT 'Per-platform publication details',
    
    -- Version lineage
    previous_version_id VARCHAR(36) NULL COMMENT 'Previous version for lineage',
    changes_summary JSON NULL COMMENT 'What changed in this version',
    review_score INT NULL COMMENT 'Quality score from review',
    
    -- Performance flags
    is_latest BOOLEAN DEFAULT FALSE COMMENT 'Latest version flag',
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(255) COMMENT 'Creator identifier',
    
    -- Foreign keys
    FOREIGN KEY (parent_id) REFERENCES stories(id) ON DELETE SET NULL,
    FOREIGN KEY (channel_group_id) REFERENCES channel_groups(id),
    FOREIGN KEY (audience_id) REFERENCES audiences(id),
    FOREIGN KEY (language_id) REFERENCES languages(id),
    FOREIGN KEY (idea_id) REFERENCES ideas(id),
    FOREIGN KEY (state_id) REFERENCES workflow_states(id),
    FOREIGN KEY (previous_version_id) REFERENCES stories(id) ON DELETE SET NULL,
    
    -- Unique constraints
    -- Ensures one story per idea+channel+language+version combination
    UNIQUE KEY unique_story_version (idea_id, channel_group_id, language_id, version),
    
    -- Indexes
    INDEX idx_parent (parent_id),
    INDEX idx_channel (channel_group_id),
    INDEX idx_audience (audience_id),
    INDEX idx_language (language_id),
    INDEX idx_idea (idea_id),
    INDEX idx_state (state_id),
    INDEX idx_is_latest (is_latest),
    INDEX idx_published_text (published_text),
    INDEX idx_published_audio (published_audio),
    INDEX idx_published_video (published_video),
    INDEX idx_created_at (created_at),
    
    -- Full-text search
    FULLTEXT INDEX ft_content (title, text_preview)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Enhanced story model with channel, audience, idea integration and S3 hybrid storage';

-- State transition history (unchanged from previous design)
CREATE TABLE story_state_transitions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    story_id VARCHAR(36) NOT NULL,
    state_type ENUM('text', 'audio', 'video', 'workflow') NOT NULL,
    from_state_id INT NOT NULL,
    to_state_id INT NOT NULL,
    transitioned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    transitioned_by VARCHAR(255),
    metadata JSON,
    
    FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE,
    FOREIGN KEY (from_state_id) REFERENCES workflow_states(id),
    FOREIGN KEY (to_state_id) REFERENCES workflow_states(id),
    
    INDEX idx_story (story_id),
    INDEX idx_state_type (state_type),
    INDEX idx_to_state (to_state_id),
    INDEX idx_transitioned_at (transitioned_at)
) ENGINE=InnoDB;
```

---

### 11.5 Models Subject to Progressive Enrichment

Based on the enriched model, these entities participate in the progressive enrichment workflow:

#### Primary Model: Story
- **Enrichment Flow**: Text → Audio → Video
- **State Tracking**: Parallel state machines (text_state, audio_state, video_state)
- **Content Storage**: Hybrid (DB + S3)
- **Enrichment Level**: Controlled by channel_group_id

#### Supporting Models:

**1. Idea (T/Idea Module)**
- **Role**: Original creative concept
- **Relationship**: 1:1 with Story
- **Enrichment**: Not directly enriched, but triggers Story creation
- **Lifecycle**: Inspiration → Creation → Outline → Title → Approved → Story Created

**2. Channel Group**
- **Role**: Defines enrichment strategy per channel
- **Enrichment Control**: 
  - `text_only`: Only text published
  - `text_audio`: Text + Audio published
  - `full`: Text + Audio + Video published
- **Platform Configuration**: Which platforms per enrichment stage

**3. Audience**
- **Role**: Target segment for personalization
- **Enrichment Impact**: May influence which enrichment levels to pursue
- **Analytics**: Track enrichment effectiveness per audience

**4. Workflow States**
- **Role**: Define valid states for each enrichment stage
- **State Types**: text, audio, video, workflow
- **Enrichment Tracking**: Monitor progress through enrichment stages

---

### 11.6 Pros and Cons of Enriched Model

#### Pros ✅

1. **Clear Original vs Translation Distinction**
   - `parentId = NULL` for originals is cleaner than self-referential
   - Simpler queries for finding originals

2. **Channel Group Integration**
   - Centralized platform configuration
   - Multi-regional support
   - Enrichment level control per channel

3. **Audience Segmentation**
   - Personalization capabilities
   - Analytics per segment
   - A/B testing support

4. **Idea Traceability**
   - Clear link from idea to published content
   - Workflow integration (T/Idea → Story)
   - Analytics on idea-to-story conversion

5. **External State Management**
   - Flexible FSM via state tables
   - Dynamic workflow without schema changes
   - UI metadata support (colors, icons)

6. **S3 Hybrid Storage**
   - Cost optimization
   - Scalability for large content
   - Performance improvement

7. **Rich Relationships**
   - Foreign keys enforce data integrity
   - Easy joins for complex queries
   - Better analytics capabilities

#### Cons ⚠️

1. **Increased Complexity**
   - More tables to manage (channel_groups, audiences, ideas, workflow_states)
   - More foreign keys to maintain
   - More complex queries (multiple joins)

2. **Migration Challenge**
   - Need to migrate existing data to new structure
   - Requires populating channel_groups, audiences, workflow_states
   - Need to link stories to ideas retroactively

3. **S3 Dependency**
   - Additional infrastructure (S3 setup, lifecycle, permissions)
   - Consistency challenges (DB + S3 sync)
   - Network latency for large content fetches

4. **State ID Instead of Enum**
   - Lose database-level validation of state values
   - Must validate states at application level
   - More complex queries (JOIN to get state name)

5. **Idea 1:1 Constraint**
   - May be too restrictive if multiple stories from one idea
   - Need to clarify: 1:1 per language? Or 1:1 total?
   - Could limit flexibility

6. **Multiple State IDs**
   - text_state_id, audio_state_id, video_state_id, workflow_state_id
   - 4 foreign keys to manage
   - Potential inconsistency between parallel states

7. **Channel Group Dependency**
   - Cannot create story without channel group
   - Need to pre-define all channel configurations
   - May be over-engineering for simple use cases

---

### 11.7 Recommendations for Enriched Model

#### Short-Term Implementation (Phase 1)

1. **Start with Core Enhancements**
   - Implement `parentId = NULL` for originals
   - Add `ideaId` for workflow integration
   - Keep state as ENUM initially (simpler validation)

2. **Defer Complex Features**
   - Postpone channel_groups (use simple lang_id + country_id)
   - Postpone audience_id (add later when needed)
   - Keep text in database initially (add S3 when volume grows)

3. **Hybrid Approach**
   ```sql
   CREATE TABLE stories (
       id VARCHAR(36) PRIMARY KEY,
       parent_id VARCHAR(36) NULL,         -- NULL for originals ✅
       idea_id INT NOT NULL,                -- Link to Idea ✅
       lang_id VARCHAR(5) NOT NULL,         -- Keep simple for now
       country_code VARCHAR(2),             -- Add country support
       version INT NOT NULL,
       
       title VARCHAR(500) NOT NULL,
       text LONGTEXT NOT NULL,              -- Keep in DB initially
       
       -- Use ENUMs for simplicity, migrate to state_id later
       text_state ENUM(...),
       audio_state ENUM(...),
       video_state ENUM(...),
       
       -- Multi-platform tracking
       published_text TIMESTAMP NULL,
       published_audio TIMESTAMP NULL,
       published_video TIMESTAMP NULL,
       
       -- ... other fields
       
       FOREIGN KEY (idea_id) REFERENCES ideas(id),
       UNIQUE KEY (idea_id, lang_id, version)
   );
   ```

#### Medium-Term Evolution (Phase 2)

1. **Add Channel Groups**
   - Create channel_groups table
   - Migrate lang_id + country_code to channel_group_id
   - Add enrichment level configuration

2. **Implement S3 Hybrid Storage**
   - Add text_s3_key, text_preview fields
   - Implement conditional storage logic
   - Migrate large content to S3

3. **Add Audience Segmentation**
   - Create audiences table
   - Add audience_id to stories
   - Start tracking per-audience analytics

#### Long-Term Optimization (Phase 3)

1. **State Table Migration**
   - Create workflow_states table
   - Migrate ENUMs to state IDs
   - Implement state transition validation

2. **Advanced Features**
   - State transition analytics
   - Cross-audience A/B testing
   - Multi-channel orchestration
   - S3 lifecycle management

---

### 11.8 Summary: Enriched vs Original Model

| Aspect | Original Model | Enriched Model |
|--------|---------------|----------------|
| **parentId** | Self-referential | NULL for originals ✅ Better |
| **Language** | `langId` field | `channelGroupId` (includes language + country) ✅ More powerful |
| **Audience** | Not included | `audienceId` ✅ Enables personalization |
| **Idea Link** | Not included | `ideaId` (1:1) ✅ Workflow integration |
| **State Management** | String/Enum | `stateId` (external table) ⚠️ More flexible but complex |
| **Storage** | Database only | S3 + Database hybrid ✅ Scalable and cost-effective |
| **Complexity** | Simple (6 fields) | Complex (13+ fields, 6 foreign keys) ⚠️ |
| **Foreign Keys** | None | 6 foreign keys ✅ Better integrity, ⚠️ More constraints |
| **Scalability** | Limited by DB | Excellent (S3 for content) ✅ |
| **Query Complexity** | Simple | Complex (multiple JOINs) ⚠️ |

**Verdict**: The enriched model is **significantly more powerful** but requires careful phased implementation to avoid over-engineering.

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
    review_score INT NULL COMMENT 'Score from T/Review (0-100)',
    
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
