# Interactive Script Review Questionnaire

**Purpose:** Quick interactive review for each workflow script  
**Format:** Question-and-answer style for agent task UI  
**Usage:** Answer these questions for each stage to validate functionality

---

## Stage 01: Idea Capture

### Basic Functionality
**Q1:** Does the script start without errors?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Q2:** Can you enter an idea description?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Q3:** Does Preview mode work (no database save)?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Q4:** Does Run mode save to database correctly?  
**A:** [ ] Yes / [ ] No - Details: ___________

### Output Quality
**Q5:** Is the saved Idea readable and complete?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Q6:** Does it have a unique ID?  
**A:** [ ] Yes / [ ] No - ID format: ___________

**Ready for next stage?** [ ] Yes / [ ] No

---

## Stage 02: Story Generation

### Basic Functionality
**Q1:** Does the script find Ideas to process?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Q2:** Does story generation complete successfully?  
**A:** [ ] Yes / [ ] No - Time taken: ___________

**Q3:** Are 10 stories created per Idea?  
**A:** [ ] Yes / [ ] No - Actual count: ___________

### Quality Check
**Q4:** Are stories coherent and relevant to the Idea?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Q5:** Do stories have unique content (not duplicates)?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Q6:** Are stories appropriate length (< 3 min target)?  
**A:** [ ] Yes / [ ] No - Typical length: ___________

**Ready for next stage?** [ ] Yes / [ ] No

---

## Stage 03: Title Generation

### Basic Functionality
**Q1:** Does the script find Stories to process?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Q2:** Are titles generated successfully?  
**A:** [ ] Yes / [ ] No - Details: ___________

### Quality Check
**Q3:** Are titles engaging and relevant?  
**A:** [ ] Yes / [ ] No - Example title: ___________

**Q4:** Are titles appropriate length (< 100 chars)?  
**A:** [ ] Yes / [ ] No - Typical length: ___________

**Q5:** Do titles have no grammar errors?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Ready for next stage?** [ ] Yes / [ ] No

---

## Stage 04: Content Generation

### Basic Functionality
**Q1:** Does content generation complete (may be slow)?  
**A:** [ ] Yes / [ ] No - Time taken: ___________

**Q2:** Does content match the title?  
**A:** [ ] Yes / [ ] No - Details: ___________

### Quality Check
**Q3:** Is the opening hook engaging?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Q4:** Does the story flow logically?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Q5:** Is the ending satisfying?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Q6:** Is it suitable for spoken narration?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Ready for next stage?** [ ] Yes / [ ] No

---

## Stage 05: Title Review (by Content & Idea)

### Basic Functionality
**Q1:** Does the review script run successfully?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Q2:** Is an overall score generated (0-100%)?  
**A:** [ ] Yes / [ ] No - Score: ___%

### Review Output
**Q3:** Are alignment scores provided (content & idea)?  
**A:** [ ] Yes / [ ] No - Scores: ___________

**Q4:** Are improvement suggestions listed?  
**A:** [ ] Yes / [ ] No - Count: ___________

**Q5:** Are suggestions actionable and clear?  
**A:** [ ] Yes / [ ] No - Example: ___________

### Decision
**Q6:** Is the score ≥ 80% (passing threshold)?  
**A:** [ ] Yes → Proceed / [ ] No → Needs improvement

**Ready for next stage?** [ ] Yes / [ ] No

---

## Stage 06: Content Review (by Title & Idea)

### Basic Functionality
**Q1:** Does the review script run successfully?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Q2:** Is an overall score generated (0-100%)?  
**A:** [ ] Yes / [ ] No - Score: ___%

### Review Categories
**Q3:** Are multiple category scores provided?  
**A:** [ ] Yes / [ ] No - Categories: ___________

**Q4:** Is engagement score reasonable?  
**A:** [ ] Yes / [ ] No - Score: ___%

**Q5:** Are pacing and clarity assessed?  
**A:** [ ] Yes / [ ] No - Scores: ___________

### Decision
**Q6:** Is the score ≥ 80% (passing threshold)?  
**A:** [ ] Yes → Proceed / [ ] No → Needs improvement

**Ready for next stage?** [ ] Yes / [ ] No

---

## Stages 07-13: Iteration Loops

### Iteration Progress
**Q1:** Are scores improving with each iteration?  
**A:** [ ] Yes / [ ] No - Trend: ___________

**Q2:** How many iterations completed?  
**A:** Count: _____ (Max: 5)

### Quality Gates (Stages 12-13)
**Q3:** Does Title pass acceptance gate (≥ 85%)?  
**A:** [ ] Yes / [ ] No - Score: ___%

**Q4:** Does Content pass acceptance gate (≥ 85%)?  
**A:** [ ] Yes / [ ] No - Score: ___%

**Q5:** Are all high-priority issues resolved?  
**A:** [ ] Yes / [ ] No - Remaining: ___________

**Ready for quality reviews?** [ ] Yes / [ ] No

---

## Stage 14: Grammar Review

### Status Check
**Q1:** Is this module implemented yet?  
**A:** [ ] Yes / [ ] No (currently placeholder)

*If implemented:*

**Q2:** Are there any spelling errors?  
**A:** [ ] Yes / [ ] No - Count: ___________

**Q3:** Is punctuation correct throughout?  
**A:** [ ] Yes / [ ] No - Issues: ___________

**Q4:** Is sentence structure grammatically sound?  
**A:** [ ] Yes / [ ] No - Issues: ___________

**Pass/Fail:** [ ] Pass → Stage 15 / [ ] Fail → Refinement

---

## Stage 15: Tone Review

### Status Check
**Q1:** Is this module implemented yet?  
**A:** [ ] Yes / [ ] No (currently placeholder)

*If implemented:*

**Q2:** Is tone consistent throughout?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Q3:** Does tone match target genre?  
**A:** [ ] Yes / [ ] No - Genre: ___________

**Q4:** Is tone appropriate for target audience?  
**A:** [ ] Yes / [ ] No - Audience: ___________

**Pass/Fail:** [ ] Pass → Stage 16 / [ ] Fail → Refinement

---

## Stage 16: Content Accuracy Review

### Status Check
**Q1:** Is this module implemented yet?  
**A:** [ ] Yes / [ ] No (currently placeholder)

*If implemented:*

**Q2:** Does the plot make logical sense?  
**A:** [ ] Yes / [ ] No - Issues: ___________

**Q3:** Are character motivations clear?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Q4:** Are there any plot holes?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Pass/Fail:** [ ] Pass → Stage 17 / [ ] Fail → Refinement

---

## Stage 17: Consistency Review

### Status Check
**Q1:** Is this module implemented yet?  
**A:** [ ] Yes / [ ] No (currently placeholder)

*If implemented:*

**Q2:** Are character names consistent?  
**A:** [ ] Yes / [ ] No - Issues: ___________

**Q3:** Is timeline aligned properly?  
**A:** [ ] Yes / [ ] No - Issues: ___________

**Q4:** Are location details consistent?  
**A:** [ ] Yes / [ ] No - Issues: ___________

**Pass/Fail:** [ ] Pass → Stage 18 / [ ] Fail → Refinement

---

## Stage 18: Editing Review

### Status Check
**Q1:** Is this module implemented yet?  
**A:** [ ] Yes / [ ] No (currently placeholder)

*If implemented:*

**Q2:** Are sentences clear and concise?  
**A:** [ ] Yes / [ ] No - Issues: ___________

**Q3:** Are transitions smooth?  
**A:** [ ] Yes / [ ] No - Issues: ___________

**Q4:** Is redundancy minimized?  
**A:** [ ] Yes / [ ] No - Examples: ___________

**Pass/Fail:** [ ] Pass → Stage 19 / [ ] Fail → Refinement

---

## Stage 19: Title Readability Review

### Status Check
**Q1:** Is this module implemented yet?  
**A:** [ ] Yes / [ ] No (currently placeholder)

*If implemented:*

**Q2:** Is the title easy to pronounce?  
**A:** [ ] Yes / [ ] No - Issues: ___________

**Q3:** Does it have natural speaking rhythm?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Q4:** Is it attention-grabbing when spoken?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Pass/Fail:** [ ] Pass → Stage 20 / [ ] Fail → Refinement

---

## Stage 20: Content Readability Review

### Status Check
**Q1:** Is this module implemented yet?  
**A:** [ ] Yes / [ ] No (currently placeholder)

*If implemented:*

**Q2:** Is content easy to read aloud?  
**A:** [ ] Yes / [ ] No - Issues: ___________

**Q3:** Is pacing suitable for audio?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Q4:** Are dramatic pauses well-placed?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Q5:** Does it sound good when listened to?  
**A:** [ ] Yes / [ ] No - Details: ___________

### Critical Decision
**Q6:** This is the FINAL review stage. Does content pass?  
**A:** [ ] Yes → Publishing / [ ] No → Major revision needed

**Ready for publishing?** [ ] Yes / [ ] No

---

## Stages 21-22: Expert Review (Optional)

**Q1:** Is expert review being used?  
**A:** [ ] Yes / [ ] No - Skip to Stage 23 if No

*If used:*

**Q2:** Has expert feedback been received?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Q3:** Have improvements been integrated?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Q4:** Does expert approve for publishing?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Ready for publishing?** [ ] Yes / [ ] No

---

## Stage 23: Publishing Finalization

**Q1:** Is content formatted for all platforms?  
**A:** [ ] Yes / [ ] No - Platforms: ___________

**Q2:** Are metadata and tags optimized?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Q3:** Do platform-specific checks pass?  
**A:** [ ] Yes / [ ] No - Issues: ___________

**Q4:** Is content ready for audio production?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Ready for audio/video?** [ ] Yes / [ ] No

---

## Stages 21-24: Audio Production (Quick Check)

**Q1:** Is voiceover quality good?  
**A:** [ ] Yes / [ ] No - Issues: ___________

**Q2:** Is audio normalized and enhanced?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Q3:** Are export files correct format/quality?  
**A:** [ ] Yes / [ ] No - Format: ___________

**Ready for video?** [ ] Yes / [ ] No

---

## Stages 26-28: Video Production (Quick Check)

**Q1:** Are visuals synchronized with audio?  
**A:** [ ] Yes / [ ] No - Issues: ___________

**Q2:** Is video quality high?  
**A:** [ ] Yes / [ ] No - Resolution: ___________

**Q3:** Is export format correct for platform?  
**A:** [ ] Yes / [ ] No - Format: ___________

**Ready for distribution?** [ ] Yes / [ ] No

---

## Stage 30: Analytics

**Q1:** Is tracking configured correctly?  
**A:** [ ] Yes / [ ] No - Metrics: ___________

**Q2:** Are performance baselines established?  
**A:** [ ] Yes / [ ] No - Details: ___________

**Workflow complete?** [ ] Yes / [ ] No

---

## Quick Status Summary

Fill this out after completing all stages:

**Total Stages Reviewed:** _____ / 30

**Stages Passed:** _____  
**Stages Failed:** _____  
**Stages Skipped:** _____

**Overall Workflow Status:**
- [ ] Fully functional
- [ ] Minor issues (documented)
- [ ] Major issues (blocking)

**Primary Blockers:**
```
[List any blocking issues]
```

**Recommended Actions:**
```
[List next steps]
```

**Reviewer:** ___________________________  
**Date:** ___________________________

---

## Usage Instructions

### For Agent Task UI

Copy individual stage sections into agent prompts:

**Example Prompt:**
```
Please review Stage 03 (Title Generation) using these questions:

Q1: Does the script find Stories to process?
Q2: Are titles generated successfully?
Q3: Are titles engaging and relevant?
Q4: Are titles appropriate length (< 100 chars)?
Q5: Do titles have no grammar errors?

Please answer each question with Yes/No and relevant details.
```

### For Manual Review

Print or use digitally as a checklist, marking answers as you validate each script.

### For Automated Review

Parse this format into a testing framework that automates validation where possible.

---

**Version:** 1.0  
**Last Updated:** 2026-01-27  
**Related:** [GUIDED_SCRIPT_REVIEW.md](./GUIDED_SCRIPT_REVIEW.md) - Full detailed version
