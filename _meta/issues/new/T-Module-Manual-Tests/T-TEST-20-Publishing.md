# T-TEST-20: PrismQ.T.Publishing Manual Test

**Module**: PrismQ.T.Publishing  
**Script**: `_meta/scripts/20_PrismQ.T.Publishing/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Text publishing with SEO optimization. Final stage of the T pipeline - prepares and publishes content.

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Publishing - RUN MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Prompt appears** asking for approved Story ID
4. **User provides** Story ID or pastes object
5. **Publishing process**:
   - SEO keyword optimization
   - Meta description generation
   - Tag generation
   - Category assignment
   - Content formatting
6. **Published object created** with fields:
   - `id`: Unique identifier
   - `story_id`: Source Story reference
   - `title`: Final title
   - `content`: Final formatted content
   - `seo_keywords`: Optimized keywords
   - `meta_description`: SEO description
   - `tags`: Content tags
   - `category`: Content category
   - `published_at`: Timestamp
7. **State set** to `PublishedText`
8. **Database write** - Published object saved
9. **Publishing summary** displayed
10. **Script ends** with next pipeline notification (Audio)

---

## Expected Behavior (Preview Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Publishing - PREVIEW MODE"
2. **Warning displayed**: "This mode is for TESTING. Content will NOT be published."
3. **Environment setup** occurs (creates/activates virtual environment if needed)
4. **Prompt appears** asking for Story
5. **User provides** the input
6. **Publishing process simulated**
7. **New state displayed**:
   ```
   ========================================
   NEW STATE (Preview - Not Saved)
   ========================================
   Publishing Preview
   
   Story: [story-id]
   
   Final Title:
   "[final-title]"
   
   Meta Description:
   "[seo-description]"
   
   SEO Keywords:
   - [keyword1]
   - [keyword2]
   - [keyword3]
   ...
   
   Tags:
   [tag1], [tag2], [tag3]
   
   Category: [category]
   
   Content Preview:
   [first 500 characters of formatted content]
   ...
   
   Word Count: [count]
   Reading Time: [X min]
   
   Next State: PublishedText
   Next Pipeline: PrismQ.A (Audio Generation)
   ========================================
   ```
8. **Wait for keystroke** - "Press any key to continue..."
9. **Full content** available in debug log
10. **Script ends**

---

## Test Commands

```batch
REM Navigate to script directory
cd _meta\scripts\20_PrismQ.T.Publishing

REM Run in Preview Mode (recommended for testing)
Preview.bat

REM Run in Production Mode (saves to database)
Run.bat
```

---

## Success Criteria

- [ ] SEO keywords are generated appropriately
- [ ] Meta description is compelling
- [ ] Tags are relevant
- [ ] Category is assigned correctly
- [ ] Content is formatted properly
- [ ] State transitions to `PublishedText`
- [ ] Preview mode shows publishing preview without saving
- [ ] Preview mode waits for keystroke
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: T-TEST-20 Publishing
### Mode: [Preview/Run]
### Date: YYYY-MM-DD

### Input:
Story: [story-id]

### Publishing Results:
Title: "[title]"
Meta Description: "[description]"
Keywords: [count]
Tags: [list]
Category: [category]
Word Count: [count]
Reading Time: [X min]

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

## Workflow Complete

After successful publishing:
- Content is ready for the Audio pipeline (PrismQ.A)
- Text metrics can be tracked in PrismQ.M
- Content can be distributed via PrismQ.P

---

**Created**: 2025-12-04
