# Guided Review for PrismQ Workflow Scripts

**Purpose:** Step-by-step guided review checklist for validating each workflow stage  
**Usage:** Check off items as you verify each script and its outputs  
**Audience:** Content reviewers, QA testers, workflow validators

---

## How to Use This Guide

1. **Sequential Review**: Work through stages in order (01 → 30)
2. **Check Each Item**: Mark items as complete using `[x]` when verified
3. **Document Issues**: Note any problems in the "Issues Found" section
4. **Validate Outputs**: Ensure each stage produces expected results before proceeding

---

## Stage 01: Idea Capture (PrismQ.T.Idea.From.User)

**Script Location:** `_meta/scripts/01_PrismQ.T.Idea.From.User/`

### Pre-Execution Checks
- [ ] Database file exists at expected location (default: `C:/PrismQ/db.s3db`)
- [ ] Python 3.8+ is installed and accessible
- [ ] Script files exist: `Run.bat` and `Preview.bat`

### Script Execution (Preview Mode)
- [ ] Run `Preview.bat` successfully
- [ ] Ollama service starts automatically (if needed)
- [ ] Virtual environment created in `T/Idea/From/User/.venv/`
- [ ] Dependencies installed without errors
- [ ] Script prompts for idea input

### Input Validation
- [ ] Can enter text description
- [ ] Target audience field accepts input
- [ ] Genre/category can be specified
- [ ] Platform selection works correctly

### Output Verification
- [ ] Idea object created with unique ID
- [ ] Timestamp recorded correctly
- [ ] Metadata fields populated (author, tags)
- [ ] Preview mode does NOT save to database

### Production Mode Test
- [ ] Run `Run.bat` successfully
- [ ] Idea saved to database (verify in `Idea` table)
- [ ] Can retrieve saved idea by ID
- [ ] Continuous mode processes multiple ideas

### Issues Found
```
[Document any issues here]
```

---

## Stage 02: Story Generation (PrismQ.T.Story.From.Idea)

**Script Location:** `_meta/scripts/02_PrismQ.T.Story.From.Idea/`

### Pre-Execution Checks
- [ ] Stage 01 completed successfully (Idea exists in database)
- [ ] Ollama service running with required model
- [ ] Database has at least one Idea in appropriate state

### Script Execution (Preview Mode)
- [ ] `Preview.bat` runs without errors
- [ ] Script finds Ideas needing processing
- [ ] Story generation completes within reasonable time
- [ ] Preview shows generated story content

### Story Generation Validation
- [ ] Creates 10 Story objects per Idea (configurable)
- [ ] Each Story has unique ID
- [ ] Story content is coherent and relevant to Idea
- [ ] Story structure includes beginning, middle, end
- [ ] Character names and settings consistent

### Output Quality Checks
- [ ] Stories match target audience specification
- [ ] Genre/tone aligns with Idea
- [ ] No duplicate or nearly-identical stories
- [ ] Appropriate length (target: < 3 minutes spoken)
- [ ] Ready for title generation

### Production Mode Test
- [ ] `Run.bat` saves stories to database
- [ ] All 10 stories appear in `Story` table
- [ ] State transitions recorded correctly
- [ ] Continuous mode picks up new Ideas

### Issues Found
```
[Document any issues here]
```

---

## Stage 03: Title Generation (PrismQ.T.Title.From.Idea)

**Script Location:** `_meta/scripts/03_PrismQ.T.Title.From.Idea/`

### Pre-Execution Checks
- [ ] Stage 02 completed (Stories exist in database)
- [ ] Stories are in correct state for title generation
- [ ] AI model accessible and responsive

### Script Execution (Preview Mode)
- [ ] Script identifies Stories needing titles
- [ ] Title generation completes successfully
- [ ] Preview displays generated titles
- [ ] Can generate multiple title options

### Title Quality Validation
- [ ] Title reflects story content accurately
- [ ] Appropriate length (< 100 characters recommended)
- [ ] Engaging and clickable
- [ ] No grammatical errors
- [ ] SEO-friendly keywords included
- [ ] Mystery/curiosity element present (if genre appropriate)

### Title Characteristics Check
- [ ] Clear and descriptive
- [ ] Target audience appropriate
- [ ] Platform-optimized (YouTube/TikTok)
- [ ] No clickbait or misleading elements
- [ ] Unique across generated set

### Production Mode Test
- [ ] Titles saved with version "v1"
- [ ] Story state updated correctly
- [ ] Multiple stories processed in batch
- [ ] Ready for content generation

### Issues Found
```
[Document any issues here]
```

---

## Stage 04: Content Generation (PrismQ.T.Content.From.Idea.Title)

**Script Location:** `_meta/scripts/04_PrismQ.T.Content.From.Idea.Title/`

### Pre-Execution Checks
- [ ] Stage 03 completed (Titles exist)
- [ ] Stories have approved titles (v1)
- [ ] Sufficient processing time available (content generation is slow)

### Script Execution (Preview Mode)
- [ ] Script finds Stories with titles needing content
- [ ] Content generation completes (may take several minutes)
- [ ] Preview shows full script content
- [ ] Content matches title and story

### Content Quality Validation
- [ ] Opening hook captures attention
- [ ] Story flows logically (beginning → middle → end)
- [ ] Pacing appropriate for spoken narration
- [ ] No plot holes or inconsistencies
- [ ] Character actions make sense
- [ ] Satisfying conclusion

### Technical Content Checks
- [ ] Length appropriate (< 3 minutes target)
- [ ] Sentence structure suitable for voiceover
- [ ] No overly complex vocabulary
- [ ] Punctuation supports natural pauses
- [ ] Paragraph breaks logical

### Content Alignment
- [ ] Matches title promises
- [ ] Aligns with original Idea intent
- [ ] Target audience appropriate
- [ ] Genre/tone consistent throughout

### Production Mode Test
- [ ] Content saved with version "v1"
- [ ] Story state updated
- [ ] Ready for review stage

### Issues Found
```
[Document any issues here]
```

---

## Stage 05: Title Review by Content & Idea (PrismQ.T.Review.Title.From.Content.Idea)

**Script Location:** `_meta/scripts/05_PrismQ.T.Review.Title.From.Content.Idea/`

### Pre-Execution Checks
- [ ] Content v1 exists from Stage 04
- [ ] Title v1 exists from Stage 03
- [ ] Original Idea accessible

### Script Execution (Preview Mode)
- [ ] Review script runs successfully
- [ ] Generates alignment scores (0-100%)
- [ ] Provides categorized feedback
- [ ] Lists improvement suggestions

### Review Output Validation
- [ ] Overall score calculated
- [ ] Content alignment score present
- [ ] Idea alignment score present
- [ ] Engagement score calculated
- [ ] SEO recommendations provided

### Review Categories Check
- [ ] Relevance score and feedback
- [ ] Clarity score and feedback
- [ ] Engagement score and feedback
- [ ] Accuracy score and feedback
- [ ] SEO optimization feedback
- [ ] Length assessment
- [ ] Platform suitability check
- [ ] Target audience fit

### Improvement Points Review
- [ ] Prioritized list of improvements (high/medium/low)
- [ ] Each point has impact score
- [ ] Suggestions are actionable
- [ ] Addresses real weaknesses

### Decision Making
- [ ] If score ≥ 80%: Consider approved, proceed to Stage 06
- [ ] If score < 80%: Note required improvements
- [ ] Review ready for iteration or approval

### Issues Found
```
[Document any issues here]
```

---

## Stage 06: Content Review by Title & Idea (PrismQ.T.Review.Content.From.Title.Idea)

**Script Location:** `_meta/scripts/06_PrismQ.T.Review.Content.From.Title.Idea/`

### Pre-Execution Checks
- [ ] Content v1 exists
- [ ] Title v1 exists
- [ ] Original Idea accessible

### Script Execution (Preview Mode)
- [ ] Review completes successfully
- [ ] Generates comprehensive scores
- [ ] Provides detailed feedback per category

### Content Review Scoring
- [ ] Overall score (0-100%)
- [ ] Title alignment score
- [ ] Idea alignment score
- [ ] Engagement score
- [ ] Pacing score
- [ ] Clarity score
- [ ] Story structure score

### Category-Specific Review
- [ ] **Engagement**: Opening hook, curiosity, satisfaction
- [ ] **Pacing**: Scene transitions, rhythm, timing
- [ ] **Clarity**: Understandability, coherence
- [ ] **Character Development**: Motivation, consistency
- [ ] **Plot Logic**: No holes, believable events
- [ ] **Tone**: Matches genre and audience
- [ ] **Dialogue**: Natural, character-appropriate
- [ ] **Ending**: Satisfying, complete

### Improvement Recommendations
- [ ] High-priority issues identified
- [ ] Medium-priority suggestions listed
- [ ] Low-priority enhancements noted
- [ ] Each has actionable guidance

### Decision Making
- [ ] If score ≥ 80%: Proceed to Stage 07 improvements
- [ ] If score < 80%: Major revision needed
- [ ] Ready for iteration cycle

### Issues Found
```
[Document any issues here]
```

---

## Stage 07: Title Review v2 (PrismQ.T.Review.Title.From.Content)

**Script Location:** `_meta/scripts/07_PrismQ.T.Review.Title.From.Content/`

### Pre-Execution Checks
- [ ] Title v2 generated (after improvements)
- [ ] Content v1 or v2 available
- [ ] Previous review feedback addressed

### Script Execution (Preview Mode)
- [ ] Review runs on improved title
- [ ] Compares v2 against v1 scores
- [ ] Shows improvement trajectory

### Improvement Validation
- [ ] Overall score improved from v1
- [ ] Previously identified issues addressed
- [ ] No new problems introduced
- [ ] Alignment scores stable or improved

### Quality Gate Check
- [ ] Score ≥ 85% for v2 (higher threshold)
- [ ] All high-priority issues resolved
- [ ] Ready for iteration acceptance

### Iteration Decision
- [ ] If passed: Proceed to Stage 08
- [ ] If failed: Return to title improvement
- [ ] Track iteration count (prevent infinite loops)

### Issues Found
```
[Document any issues here]
```

---

## Stages 08-13: Iteration Loops (Review & Refinement)

**Script Locations:** `_meta/scripts/08-13_*/`

### Iteration Pattern Validation

For each iteration cycle:

- [ ] **Stage 08**: Title review v2
- [ ] **Stage 09**: Title refinement based on review
- [ ] **Stage 10**: Content review v2
- [ ] **Stage 11**: Content refinement based on review
- [ ] **Stage 12**: Title acceptance gate (≥ 85%)
- [ ] **Stage 13**: Content acceptance gate (≥ 85%)

### Iteration Quality Checks
- [ ] Scores trending upward with each iteration
- [ ] Feedback becoming more positive
- [ ] Fewer critical issues per iteration
- [ ] Changes are substantive, not cosmetic

### Acceptance Gates (Stages 12-13)
- [ ] Title score ≥ 85% sustained
- [ ] Content score ≥ 85% sustained
- [ ] All high-priority issues resolved
- [ ] Review feedback mostly positive
- [ ] Ready for quality review stages

### Loop Prevention
- [ ] Maximum 5 iterations enforced
- [ ] If max reached, flag for manual review
- [ ] Track diminishing returns

### Issues Found
```
[Document any issues here]
```

---

## Stage 14: Grammar Review (PrismQ.T.Review.Content.Grammar)

**Script Location:** `_meta/scripts/11_PrismQ.T.Review.Content.Grammar/`

### Pre-Execution Checks
- [ ] Content passed acceptance gates (Stages 12-13)
- [ ] Grammar review module implemented (currently placeholder)

### Grammar Validation (When Implemented)
- [ ] No spelling errors
- [ ] Punctuation correct throughout
- [ ] Sentence structure grammatically sound
- [ ] Subject-verb agreement correct
- [ ] Tense consistency maintained
- [ ] No run-on sentences
- [ ] Proper capitalization

### Technical Corrections
- [ ] Comma placement correct
- [ ] Apostrophes used correctly
- [ ] Quotation marks paired properly
- [ ] Paragraph breaks appropriate

### Decision
- [ ] If passed: Proceed to Stage 15 (Tone)
- [ ] If failed: Return to Content Refinement (Stage 11)

### Issues Found
```
[Document any issues here]
```

---

## Stage 15: Tone Review (PrismQ.T.Review.Content.Tone)

**Script Location:** `_meta/scripts/12_PrismQ.T.Review.Content.Tone/`

### Pre-Execution Checks
- [ ] Grammar review passed (Stage 14)
- [ ] Tone review module implemented (currently placeholder)

### Tone Validation (When Implemented)
- [ ] Emotional tone consistent throughout
- [ ] Matches target genre (mystery, suspense, etc.)
- [ ] Appropriate for target audience
- [ ] Voice and POV consistent
- [ ] Intensity level appropriate
- [ ] No jarring tone shifts
- [ ] Mystery/creepiness balanced (if applicable)

### Audience Alignment
- [ ] Language age-appropriate
- [ ] Cultural sensitivity maintained
- [ ] Engagement level suitable for demographic

### Decision
- [ ] If passed: Proceed to Stage 16 (Content)
- [ ] If failed: Return to Content Refinement (Stage 11)

### Issues Found
```
[Document any issues here]
```

---

## Stage 16: Content Accuracy Review (PrismQ.T.Review.Content.Content)

**Script Location:** `_meta/scripts/13_PrismQ.T.Review.Content.Content/`

### Pre-Execution Checks
- [ ] Tone review passed (Stage 15)
- [ ] Content review module implemented (currently placeholder)

### Narrative Coherence Validation (When Implemented)
- [ ] Plot makes logical sense
- [ ] No missing story elements
- [ ] Character motivations clear
- [ ] Events follow cause-and-effect
- [ ] No contradictions in plot
- [ ] Scene order logical
- [ ] Pacing issues identified and resolved

### Structural Quality
- [ ] Beginning establishes context
- [ ] Middle develops tension/conflict
- [ ] Ending provides resolution
- [ ] Story arc complete

### Decision
- [ ] If passed: Proceed to Stage 17 (Consistency)
- [ ] If failed: Return to Content Refinement (Stage 11)

### Issues Found
```
[Document any issues here]
```

---

## Stage 17: Consistency Review (PrismQ.T.Review.Content.Consistency)

**Script Location:** `_meta/scripts/14_PrismQ.T.Review.Content.Consistency/`

### Pre-Execution Checks
- [ ] Content review passed (Stage 16)
- [ ] Consistency review module implemented (currently placeholder)

### Internal Consistency Validation (When Implemented)
- [ ] Character names consistent throughout
- [ ] Timeline alignment verified
- [ ] Location/setting consistency
- [ ] Repeated details match
- [ ] Facts and lore aligned
- [ ] No contradictions after edits
- [ ] Character traits consistent

### Continuity Checks
- [ ] Scene transitions make sense
- [ ] Props/objects accounted for
- [ ] Weather/time of day consistent

### Decision
- [ ] If passed: Proceed to Stage 18 (Editing)
- [ ] If failed: Return to Content Refinement (Stage 11)

### Issues Found
```
[Document any issues here]
```

---

## Stage 18: Editing Review (PrismQ.T.Review.Content.Editing)

**Script Location:** `_meta/scripts/15_PrismQ.T.Review.Content.Editing/`

### Pre-Execution Checks
- [ ] Consistency review passed (Stage 17)
- [ ] Editing review module implemented (currently placeholder)

### Clarity & Flow Validation (When Implemented)
- [ ] Sentences clear and concise
- [ ] No redundant phrasing
- [ ] Transitions smooth between paragraphs
- [ ] Confusing sections clarified
- [ ] Unnecessary words removed
- [ ] Flow feels natural when read aloud

### Readability Improvements
- [ ] Sentence variety (length and structure)
- [ ] Active voice preferred over passive
- [ ] Concrete over abstract language
- [ ] Show, don't tell (where appropriate)

### Decision
- [ ] If passed: Proceed to Stage 19 (Title Readability)
- [ ] If failed: Return to Content Refinement (Stage 11)

### Issues Found
```
[Document any issues here]
```

---

## Stage 19: Title Readability Review (PrismQ.T.Review.Title.Readability)

**Script Location:** `_meta/scripts/16_PrismQ.T.Review.Title.Readability/`

### Pre-Execution Checks
- [ ] Editing review passed (Stage 18)
- [ ] Title readability module implemented (currently placeholder)

### Title Voiceover Validation (When Implemented)
- [ ] Easy to pronounce
- [ ] Natural speaking rhythm
- [ ] No tongue-twisters
- [ ] Clear when spoken aloud
- [ ] Emphasis points obvious
- [ ] Pauses natural

### Audio Suitability
- [ ] Works well in thumbnail voiceover
- [ ] Attention-grabbing when heard
- [ ] Memorable phrasing

### Decision
- [ ] If passed: Proceed to Stage 20 (Content Readability)
- [ ] If failed: Return to Title Refinement

### Issues Found
```
[Document any issues here]
```

---

## Stage 20: Content Readability Review (PrismQ.T.Review.Content.Readability)

**Script Location:** `_meta/scripts/17_PrismQ.T.Review.Content.Readability/`

### Pre-Execution Checks
- [ ] Title readability passed (Stage 19)
- [ ] Content readability module implemented (currently placeholder)

### Voiceover Suitability Validation (When Implemented)
- [ ] Natural speaking rhythm throughout
- [ ] Sentences easy to read aloud
- [ ] No awkward phrasing for speech
- [ ] Breath points natural (commas, periods)
- [ ] Dramatic pauses well-placed
- [ ] Emphasis words clear
- [ ] Mouthfeel comfortable (no difficult combinations)

### Narration Quality
- [ ] Sounds good when listened to (not just read)
- [ ] Pacing suitable for audio
- [ ] Engagement maintained aurally
- [ ] Pronunciation guide not needed

### Critical Gate
- [ ] **This is the FINAL review stage**
- [ ] If passed: Ready for Publishing (Stage 23) or Expert Review (Stage 21-22)
- [ ] If failed: Return to Content Refinement (Stage 11)
- [ ] Must pass to proceed to audio/video production

### Issues Found
```
[Document any issues here]
```

---

## Stage 21-22: Expert Review Loop (Optional)

**Script Locations:** `_meta/scripts/18-19_*/`

### GPT Expert Review (Stage 21)
- [ ] Content sent to GPT-4 for expert review
- [ ] Comprehensive feedback received
- [ ] Issues categorized by severity
- [ ] Recommendations actionable

### Expert Review Quality
- [ ] Fresh perspective provided
- [ ] Catches issues missed by automated reviews
- [ ] Provides creative suggestions
- [ ] Validates overall quality

### Story Polish (Stage 22)
- [ ] Expert feedback integrated
- [ ] Final polish applied
- [ ] Quality elevated beyond automated reviews

### Decision
- [ ] If improvements needed: Polish and loop to Stage 21
- [ ] If ready: Proceed to Publishing (Stage 23)

### Issues Found
```
[Document any issues here]
```

---

## Stage 23: Publishing Finalization (PrismQ.T.Publishing)

**Script Location:** `_meta/scripts/20_PrismQ.T.Publishing/`

### Pre-Execution Checks
- [ ] All review stages passed (14-20)
- [ ] Optional expert review completed (if used)
- [ ] Content finalized and approved

### Publishing Preparation
- [ ] Content formatted for platforms
- [ ] Metadata prepared (title, description, tags)
- [ ] SEO keywords optimized
- [ ] Platform-specific adjustments made
- [ ] Character count verified for each platform

### Platform-Specific Checks
- [ ] **YouTube**: Description, tags, thumbnail text
- [ ] **TikTok**: Caption, hashtags optimized
- [ ] **Blog**: Formatting, images, links
- [ ] **Social**: Post copy, hashtags

### Final Validation
- [ ] Content matches all platform requirements
- [ ] No formatting issues
- [ ] Ready for audio production (Stages 21-24)
- [ ] Ready for video production (Stages 26-28)

### Issues Found
```
[Document any issues here]
```

---

## Stages 21-24: Audio Production

**Script Locations:** `_meta/scripts/21-24_*/`

### Stage 21: Voiceover Generation
- [ ] Script converted to speech
- [ ] Voice suitable for content
- [ ] Pronunciation correct
- [ ] Pacing natural
- [ ] Emotion appropriate

### Stage 22: Narrator Enhancement
- [ ] Voice quality enhanced
- [ ] Background noise removed
- [ ] Volume normalized
- [ ] Professional sound quality

### Stage 23: Audio Normalization
- [ ] Volume consistent throughout
- [ ] Levels optimized for platform
- [ ] No clipping or distortion
- [ ] Ready for mixing

### Stage 24: Audio Enhancement
- [ ] Final polish applied
- [ ] Background music (if applicable)
- [ ] Sound effects integrated
- [ ] Export quality verified

### Issues Found
```
[Document any issues here]
```

---

## Stages 26-28: Video Production

**Script Locations:** `_meta/scripts/26-28_*/`

### Stage 26: Scene Generation
- [ ] Visual scenes created for script
- [ ] Scene transitions smooth
- [ ] Images match narration
- [ ] Timing synchronized

### Stage 27: Keyframe Extraction
- [ ] Key moments identified
- [ ] Keyframes extracted
- [ ] Quality sufficient for video
- [ ] Timing accurate

### Stage 28: Video Assembly
- [ ] Audio and visual synchronized
- [ ] Transitions polished
- [ ] Text overlays (if any) readable
- [ ] Platform format correct (vertical/horizontal)
- [ ] Export quality high
- [ ] File size appropriate

### Issues Found
```
[Document any issues here]
```

---

## Stage 30: Analytics Tracking

**Script Location:** `_meta/scripts/30_PrismQ.M.Analytics/`

### Analytics Setup
- [ ] Tracking configured for all platforms
- [ ] Metrics collected: views, engagement, retention
- [ ] Performance baselines established
- [ ] A/B testing data recorded (if applicable)

### Performance Monitoring
- [ ] Video performance tracked over time
- [ ] Audience feedback collected
- [ ] Engagement patterns analyzed
- [ ] Lessons learned documented

### Issues Found
```
[Document any issues here]
```

---

## Summary Checklist

### Complete Workflow Validation
- [ ] All 30 stages reviewed
- [ ] Each stage produces expected outputs
- [ ] Quality gates functioning correctly
- [ ] Iteration loops work as designed
- [ ] No blocking issues found

### Documentation Quality
- [ ] All scripts have Run.bat and Preview.bat
- [ ] Environment setup automatic
- [ ] Error messages clear and helpful
- [ ] Logs provide useful debugging info

### System Health
- [ ] Database operations performant
- [ ] AI model responses timely
- [ ] No memory leaks or resource issues
- [ ] Scripts recoverable from errors

### Recommendations for Improvement
```
[List any systemic improvements needed]
```

---

## Review Sign-Off

**Reviewer Name:** ___________________________

**Date Completed:** ___________________________

**Overall Assessment:**
- [ ] All stages functional
- [ ] Ready for production use
- [ ] Issues documented and prioritized

**Notes:**
```
[Additional comments or observations]
```

---

## Related Documentation

- [PR Review Checklist](./PR_CODE_REVIEW_CHECKLIST.md) - For code changes
- [Script Compliance Audit](./SCRIPT_COMPLIANCE_AUDIT.md) - Known script issues
- [User Review Summary](_meta/reports/USER_REVIEW_SUMMARY.md) - Current state overview
- [Full State Report](_meta/reports/USER_REVIEW_STEPS_STATE_REPORT.md) - Comprehensive details
- [MVP Stages](_meta/docs/workflow/mvp-stages.md) - Stage documentation

---

**Version:** 1.0  
**Last Updated:** 2026-01-27  
**Status:** ✅ Ready for use
