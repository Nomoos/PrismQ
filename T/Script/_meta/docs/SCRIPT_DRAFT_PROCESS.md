# Script Draft Process

**Module**: `PrismQ.T.Script.Draft`

## Purpose

This document provides a detailed, step-by-step process for creating script drafts from approved ideas. It serves as an operational guide for content creators and AI systems generating initial script content.

## Process Overview

```
Prerequisites Met → Setup Phase → Writing Phase → Self-Review → Handoff
```

**Estimated Time**: 2-4 hours for medium-form content (1,500-2,500 words)

## Prerequisites

### Required Inputs

Before beginning script draft creation, ensure these inputs are available and approved:

#### 1. From Idea Module (PrismQ.T.Idea)
- **Status**: Idea must be in `IDEA_TITLE` state (Outline → Skeleton → Title completed)
- **Outline**: Complete structural outline from `T/Idea/Outline`
  - Major sections identified
  - Key points defined
  - Logical flow established
- **Story Concept**: From `T/Idea/Model`
  - Core narrative or thesis
  - Purpose and value proposition
  - Emotional quality specifications
- **Target Specifications**:
  - Target audience demographics
  - Target platform(s)
  - Content style guidelines
  - Length requirements

#### 2. From Title Module (PrismQ.T.Title.Draft)
- **Working Title**: At least one title draft
  - Provides hook direction
  - Establishes angle
  - Sets tone expectations

#### 3. Additional Context
- **Research Materials**: Any sources, references, or data needed
- **Brand Guidelines**: Voice and style requirements (if applicable)
- **Platform Constraints**: Technical limitations or requirements

### Verification Checklist

Before proceeding, verify:
- [ ] Idea status is `IDEA_TITLE` or later
- [ ] Complete outline exists with all major sections
- [ ] At least one working title is available
- [ ] Target platform and audience are defined
- [ ] Length requirements are specified
- [ ] Any required research is available

## Setup Phase

### Step 1: Review and Internalize Inputs

**Time**: 15-20 minutes

**Actions**:
1. **Read the Idea Document Thoroughly**
   - Understand the core concept
   - Internalize the purpose
   - Note the emotional quality
   - Review target audience

2. **Study the Outline**
   - Understand section flow
   - Note key points per section
   - Identify transitions
   - Estimate section lengths

3. **Analyze Title Options**
   - Understand the chosen angle
   - Identify hook type
   - Note promise being made
   - Consider opening alignment

4. **Review Platform Requirements**
   - Note length constraints
   - Understand format expectations
   - Consider style requirements
   - Plan for platform-specific elements

### Step 2: Define Script Parameters

**Time**: 10-15 minutes

**Create a Script Parameter Document:**

```markdown
## Script Parameters for [Idea Title]

### Basic Information
- **Idea ID**: [reference]
- **Working Title**: [selected title]
- **Target Platform**: [Blog/Podcast/Video/Multi]
- **Target Format**: [Article/Episode/Video]

### Length Specifications
- **Target Word Count**: [number]
- **Estimated Duration**: [if audio/video]
- **Section Count**: [from outline]
- **Average Section Length**: [calculated]

### Voice and Style
- **Perspective**: [First Person / Third Person]
- **Formality Level**: [Casual / Professional / Academic]
- **Tone**: [Conversational / Authoritative / Educational / Entertaining]
- **Key Characteristics**: [Humorous / Technical / Emotional / Data-driven]

### Structural Approach
- **Opening Style**: [Personal Story / Question / Statement / Statistic]
- **Content Flow**: [Problem-Solution / Narrative Arc / Thesis-Support]
- **Conclusion Type**: [Summary / Call-to-Action / Open Question]

### Audience Considerations
- **Assumed Knowledge Level**: [Beginner / Intermediate / Advanced]
- **Primary Pain Point**: [what problem are we solving]
- **Desired Outcome**: [what should audience be able to do/know/feel]
```

### Step 3: Create Structural Skeleton

**Time**: 15-20 minutes

**Build Section Framework:**

For each section from the outline, create a mini-plan:

```markdown
## Section Skeleton

### 1. HOOK (Target: 75 words / 30 seconds)
**Purpose**: Capture attention and state promise
**Approach**: [Story/Question/Statement/Surprise]
**Key Elements**:
- Opening line that [does what]
- Problem statement or curiosity trigger
- Promise of value

### 2. CONTEXT (Target: 150 words / 1 minute)
**Purpose**: Establish relevance and preview content
**Approach**: [Connection to audience experience]
**Key Elements**:
- Why this matters now
- Who this is for
- What they'll gain

### 3. [SECTION NAME from Outline] (Target: X words)
**Purpose**: [from outline]
**Key Points**:
- Point 1 from outline
- Point 2 from outline
- Point 3 from outline
**Supporting Elements**:
- Example or story needed: [type]
- Data or evidence: [what to reference]
- Transition out: [where does this lead]

[Repeat for each major section...]

### [N]. CONCLUSION (Target: 110 words / 45 seconds)
**Purpose**: Satisfy promise and create memorable ending
**Approach**: [Summary/Transformation/Forward-looking]
**Key Elements**:
- Callback to hook
- Summary of key insights
- Final memorable statement

### [N+1]. CALL TO ACTION (Target: 50 words / 20 seconds)
**Purpose**: Drive specific audience action
**Action**: [specific thing you want them to do]
**Platform**: [where/how]
**Motivation**: [why they should do it]
```

## Writing Phase

### Step 4: First Draft - Continuous Writing

**Time**: 2-3 hours (for 2,000-3,000 words)

**Method**: "Vomit Draft" - Write continuously without self-editing

#### Writing Guidelines

**DO:**
- ✅ Write in order from hook to conclusion
- ✅ Speak the words aloud as you type
- ✅ Maintain momentum—keep writing
- ✅ Use your natural voice and vocabulary
- ✅ Trust your outline but don't be constrained by it
- ✅ Include examples and stories as they come to you
- ✅ Mark uncertain areas but don't stop to verify
- ✅ Let the narrative flow naturally

**DON'T:**
- ❌ Stop to edit previous paragraphs
- ❌ Perfect each sentence before moving on
- ❌ Research facts mid-writing (mark and continue)
- ❌ Second-guess word choices (revision comes later)
- ❌ Delete large sections (mark as [RECONSIDER] instead)
- ❌ Worry about grammar or punctuation
- ❌ Aim for the perfect phrase

#### Marking Convention

Use these tags to mark issues without breaking flow:

- `[CHECK]` - Something to verify or improve later
- `[RESEARCH]` - Needs fact-checking or data
- `[EXAMPLE NEEDED]` - Could use a concrete example here
- `[TRANSITION]` - Needs better connection
- `[RECONSIDER]` - Section might need major revision
- `[ALTERNATIVE: text]` - Alternative phrasing to consider

**Example Usage:**
```
The statistics show that [CHECK: get exact percentage] of companies 
now use AI agents in some capacity. This is a massive increase from 
just [RESEARCH: how long ago?] when the number was negligible.

[EXAMPLE NEEDED: real company case study here]

This shift represents [TRANSITION] a fundamental change in how...
```

#### Section-by-Section Approach

**For Each Section:**

1. **Read the Section Plan** (from skeleton)
   - Remind yourself of purpose
   - Review key points
   - Note target length

2. **Write Opening Sentence**
   - Get into the section naturally
   - Connect from previous section
   - Set up what's coming

3. **Develop Key Points**
   - Cover each point from outline
   - Add examples and evidence
   - Use natural voice
   - Maintain conversational flow

4. **Create Transition**
   - Link to next section
   - Maintain narrative momentum
   - Use natural bridges ("Now...", "But here's the thing...", "This leads to...")

5. **Move On**
   - Don't reread
   - Don't perfect
   - Keep momentum

### Step 5: Handle Writing Blocks

If you get stuck on a section:

**Option 1: Skip and Return**
- Mark the section with `[INCOMPLETE - RETURN TO THIS]`
- Write a quick summary of what should be here
- Move to next section
- Return after completing the flow

**Option 2: Simplify the Approach**
- Scale back ambition for the section
- State the point more directly
- Move on to embellish later

**Option 3: Change Tactics**
- Tell it as a story instead of explanation
- Use an analogy
- Ask a question and answer it
- Use a concrete example

**Example Block Solution:**
```
Original stuck point: "Need to explain complex technical concept"

Solution - Story approach:
"Let me tell you about the first time I encountered this. I was 
[story that illustrates the concept naturally]. That's essentially 
what [technical term] means—but in practice, it's just [simple 
explanation]."
```

## Self-Review Phase

### Step 6: Initial Self-Review

**Time**: 20-30 minutes

**Purpose**: Verify completeness and basic coherence, not perfection

#### Review Pass 1: Completeness Check (10 minutes)

Read through quickly and verify:
- [ ] Hook exists and captures attention
- [ ] Context section establishes relevance
- [ ] All major sections from outline are present
- [ ] Each section covers its key points
- [ ] Transitions exist between sections
- [ ] Conclusion delivers on hook's promise
- [ ] Call-to-action is clear and specific

**Mark Missing Pieces:**
If anything is missing, either:
- Fill it in now (if quick)
- Mark clearly what's needed: `[MISSING: explanation of concept X]`

#### Review Pass 2: Read Aloud Test (15 minutes)

Read the entire script aloud (or use text-to-speech):

**Listen For:**
- Sections that are hard to read/speak
- Awkward phrasing or tongue-twisters
- Sentences that are too long to speak comfortably
- Unclear pronouns or references
- Abrupt transitions
- Voice consistency issues

**Mark with Audio Tags:**
- `[AWKWARD]` - Phrasing is difficult to speak
- `[TOO LONG]` - Sentence needs breaking up
- `[UNCLEAR]` - Meaning gets lost when spoken
- `[JARRING]` - Transition or shift is too abrupt

#### Review Pass 3: Alignment Check (5 minutes)

Quick verification:
- [ ] Script delivers on title's promise
- [ ] Tone matches audience expectations
- [ ] Length is appropriate for platform
- [ ] Voice is consistent throughout
- [ ] Opening and conclusion are strong

### Step 7: Quality Gate Assessment

**Evaluate Against Minimum Requirements:**

#### Must-Have (Required to Proceed):
- [ ] Complete narrative from hook to conclusion
- [ ] No major sections missing entirely
- [ ] Script can be read aloud without breaking down
- [ ] Length is within 50-150% of target (will be adjusted later)
- [ ] Voice perspective is consistent (not switching between I/we/you randomly)

#### Should-Have (Strong Indicators):
- [ ] Hook captures attention effectively
- [ ] Conclusion satisfies the opening promise
- [ ] Transitions feel natural
- [ ] Examples and evidence support points
- [ ] Call-to-action is clear

#### Could-Have (Nice but Not Required for Draft):
- Perfect grammar and punctuation
- Optimal word choice throughout
- Maximum emotional impact
- Platform-specific optimization
- SEO keyword integration

**Decision Point:**

**If Must-Haves are Met → Proceed to Handoff**
**If Must-Haves are Missing → Fix Critical Issues Then Proceed**
**If Fundamental Problems → Return to Idea/Outline Phase**

## Handoff Phase

### Step 8: Prepare for Review

**Time**: 10-15 minutes

#### Create Draft Package

**1. Save the Script Draft**
```
Location: T/Script/Draft/
Filename: {idea_id}_script_draft_v1.md
Format: Markdown with metadata header
```

**2. Document Metadata**
```yaml
---
idea_id: [reference to source idea]
title: [working title]
version: 1.0
status: SCRIPT_DRAFT
created: YYYY-MM-DD
author: [human or AI identifier]
target_platform: [Blog/Podcast/Video/Multi]
target_length: [word count target]
actual_length: [actual word count]
estimated_duration: [if audio/video]
---
```

**3. Create Issues Log**
Document all marked issues:
```markdown
## Known Issues for Review

### Critical Issues
- [Items marked MISSING or INCOMPLETE]

### Verification Needed
- [Items marked CHECK or RESEARCH]

### Improvement Opportunities
- [Items marked AWKWARD, TOO LONG, UNCLEAR, JARRING]

### Questions for Reviewer
- [Specific areas where feedback is needed]
```

**4. Generate Statistics**
```markdown
## Script Draft Statistics

- **Word Count**: [actual]
- **Target Word Count**: [target]
- **Variance**: [+/- X%]
- **Section Count**: [actual]
- **Average Section Length**: [words]
- **Estimated Speaking Time**: [minutes at 150 wpm]
- **Marked Issues**: [total count]
- **Completion Percentage**: [estimate]
```

### Step 9: Update Workflow Status

**System Actions:**
1. Update Idea status: `IDEA_TITLE` → `SCRIPT_DRAFT`
2. Log timestamp for draft completion
3. Associate draft file with Idea record
4. Create review task in workflow system
5. Notify reviewers (if applicable)

**Documentation:**
```markdown
## Workflow Transition Log

- **Previous State**: IDEA_TITLE
- **New State**: SCRIPT_DRAFT
- **Transition Date**: YYYY-MM-DD HH:MM
- **Draft Version**: 1.0
- **Next Step**: SCRIPT_REVIEW
- **Assigned Reviewer**: [if applicable]
- **Review Deadline**: [if applicable]
```

### Step 10: Handoff to Review

**Package Delivery:**
Transfer to `T/Review` modules for multi-dimensional review:

1. **Grammar Review** (`T/Review/Grammar`)
   - Syntax and grammar check
   - Punctuation review
   - Sentence structure analysis

2. **Readability Review** (`T/Review/Readability`)
   - Reading level assessment
   - Clarity evaluation
   - Flow and pacing review

3. **Tone Review** (`T/Review/Tone`)
   - Voice consistency check
   - Tone appropriateness
   - Brand alignment

4. **Content Review** (`T/Review/Content`)
   - Fact verification
   - Accuracy check
   - Completeness review

5. **Consistency Review** (`T/Review/Consistency`)
   - Terminology consistency
   - Style guideline compliance
   - Format consistency

6. **Editing Review** (`T/Review/Editing`)
   - Redundancy removal
   - Efficiency improvements
   - Final polish

**Review Coordination:**
- All review dimensions can happen in parallel
- Feedback consolidated before moving to Improvements
- Critical issues may require immediate re-draft

## Process Variations

### For Different Content Types

#### Short-Form Video (300-600 words)
- **Setup Time**: 15 minutes
- **Writing Time**: 45-90 minutes
- **Review Time**: 15 minutes
- **Focus**: Extremely tight hook, rapid pacing, clear payoff

#### Medium-Form Content (1,500-2,500 words)
- **Setup Time**: 30 minutes
- **Writing Time**: 2-3 hours
- **Review Time**: 30 minutes
- **Focus**: Balanced depth, clear structure, engaging flow

#### Long-Form Content (3,000-5,000 words)
- **Setup Time**: 45 minutes
- **Writing Time**: 4-6 hours
- **Review Time**: 45 minutes
- **Focus**: Comprehensive coverage, multiple story arcs, sustained engagement

### For Different Platforms

#### Blog/Article
- Emphasis on scanability
- Include subheading placeholders
- Note where lists/bullets make sense
- Plan for internal linking opportunities

#### Podcast
- Emphasis on verbal transitions
- Include verbal signposting
- Plan for chapter markers
- Note where music/sound effects could enhance

#### Video
- Emphasis on visual syncing
- Note B-roll opportunities
- Plan for on-screen text
- Include timing cues for pacing

## Troubleshooting

### Common Problems and Solutions

#### Problem: "Can't get started / blank page syndrome"
**Solutions:**
- Start with the easiest section (not necessarily the hook)
- Write a terrible first sentence just to get moving
- Speak your thoughts out loud and transcribe
- Set a 10-minute timer and write anything

#### Problem: "Script is way too long"
**Solutions:**
- Don't worry in first draft—trimming happens in Optimization
- Mark sections that feel verbose with `[COULD TRIM]`
- Finish the draft, assess total overrun, then decide if it's a problem
- Consider splitting into multi-part series

#### Problem: "Script is too short"
**Solutions:**
- Identify sections that need more depth
- Add examples or case studies
- Develop transitions more fully
- Expand on key points with supporting detail

#### Problem: "Voice feels wrong"
**Solutions:**
- Check script parameters—is voice definition clear?
- Re-read Idea document—did you internalize the tone?
- Start a fresh section with exaggerated style, then dial back
- Record yourself speaking the content, then write what you said

#### Problem: "Can't find the right hook"
**Solutions:**
- Write the body first, then return to hook with better understanding
- Try 5 completely different hook approaches in 5 minutes
- Use the working title as temporary hook and continue
- Start with a story from your own experience

#### Problem: "Research needed but not available"
**Solutions:**
- Mark clearly: `[RESEARCH NEEDED: specific question]`
- Write the section with placeholder: "Studies show [X%] of people..."
- Continue with draft—don't let research gaps stop progress
- Note in Issues Log for review phase

## Success Metrics

A successful Script Draft process results in:

**Deliverables:**
- ✅ Complete script file in proper format
- ✅ Metadata header with all required fields
- ✅ Issues log documenting known problems
- ✅ Statistics document
- ✅ Updated workflow status

**Quality Indicators:**
- ✅ Readable aloud without major issues
- ✅ Covers all outline sections
- ✅ Maintains consistent voice
- ✅ Delivers on title promise
- ✅ Appropriate length (within reasonable range)

**Process Efficiency:**
- ✅ Completed within estimated timeframe
- ✅ Minimal backtracking or rewriting
- ✅ Clear issues documentation for review
- ✅ Ready for multi-dimensional review

## Appendix: Quick Reference

### Pre-Writing Checklist
- [ ] Idea status verified (IDEA_TITLE)
- [ ] Outline reviewed and internalized
- [ ] Working title selected
- [ ] Script parameters defined
- [ ] Structural skeleton created
- [ ] Writing environment prepared

### During Writing Checklist
- [ ] Writing continuously without excessive editing
- [ ] Reading aloud as I write
- [ ] Marking issues with tags
- [ ] Maintaining consistent voice
- [ ] Following structural skeleton
- [ ] Keeping momentum

### Post-Writing Checklist
- [ ] Completeness check done
- [ ] Read-aloud test completed
- [ ] Alignment verified
- [ ] Quality gates assessed
- [ ] Metadata documented
- [ ] Issues log created
- [ ] Statistics calculated
- [ ] Workflow status updated
- [ ] Handoff to review initiated

---

**Related Documentation:**
- [Script Draft Creation Guide](/_meta/research/script-draft-creation-guide.md)
- [Optimization Strategies](./OPTIMIZATION_STRATEGIES.md)
- [Review Checklist](./REVIEW_CHECKLIST.md)
- [T/Script README](../README.md)
