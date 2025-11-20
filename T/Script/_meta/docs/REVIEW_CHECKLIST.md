# Script Review Checklist

**Module**: `PrismQ.T.Rewiew` (applies to all review dimensions)

## Purpose

This document provides comprehensive checklists for reviewing script drafts across all quality dimensions. Use this as a systematic guide for evaluating scripts before moving to improvements and optimization phases.

## Review Process Overview

```
Script Draft → Multi-Dimensional Review → Script Improvements
                      ↑
                YOU ARE HERE
```

**Review Dimensions:**
1. Grammar and Syntax
2. Readability
3. Tone and Voice
4. Content Accuracy
5. Consistency
6. Final Editing

**Each dimension can be reviewed in parallel**

## Pre-Review Verification

Before starting detailed review, verify:
- [ ] Script is marked as SCRIPT_DRAFT status
- [ ] Script includes complete metadata header
- [ ] Script has hook, body, conclusion, and CTA
- [ ] No major sections are marked [INCOMPLETE]
- [ ] Issues log is available (if provided)

## 1. Grammar and Syntax Review

**Module**: `T/Rewiew/Grammar`

### Purpose
Ensure grammatical correctness while respecting conversational script style.

### Special Consideration for Scripts
Scripts use conversational voice, so some "grammatical errors" are acceptable if they sound natural when spoken.

### Checklist

#### Sentence Structure
- [ ] All sentences are complete (unless fragment is intentional for style)
- [ ] No run-on sentences that are difficult to speak
- [ ] Sentence boundaries are clear
- [ ] Nested clauses don't cause confusion
- [ ] Sentences can be read aloud comfortably

**Acceptable Script Style:**
```
✅ "And that's the point." (Intentional fragment for emphasis)
✅ "Here's the thing—productivity isn't about doing more." (Conversational dash usage)
✅ "So... what does this mean for you?" (Intentional ellipsis for pause)
```

**Needs Correction:**
```
❌ "Because productivity while important is something that." (Incomplete thought)
❌ "The system works well it helps you focus it saves time it's simple." (Run-on without pauses)
```

#### Subject-Verb Agreement
- [ ] All subjects and verbs agree in number
- [ ] Collective nouns handled correctly
- [ ] Compound subjects handled correctly
- [ ] No agreement errors after interrupting phrases

**Examples to Check:**
```
❌ "The team of developers are working..." 
✅ "The team of developers is working..."

❌ "Each of the strategies require..."
✅ "Each of the strategies requires..."
```

#### Verb Tense Consistency
- [ ] Consistent tense within each section
- [ ] Intentional tense shifts are clear and justified
- [ ] Past tense for stories/examples
- [ ] Present tense for current state/instructions
- [ ] Future tense for predictions/outcomes

**Check for:**
```
❌ "I was working on this project, and then I realize something."
✅ "I was working on this project, and then I realized something."
```

#### Pronoun Usage
- [ ] All pronouns have clear antecedents
- [ ] No ambiguous "it" or "they" references
- [ ] Consistent point of view (I/you/we)
- [ ] Gender-neutral language where appropriate

**Examples:**
```
❌ "When you use the system and check the list, it helps you focus." (What does "it" refer to?)
✅ "When you use the system and check the list, the system helps you focus."
OR
✅ "When you use the system and check the list, that process helps you focus."
```

#### Punctuation for Speech
- [ ] Commas indicate natural pauses
- [ ] Periods provide breathing points
- [ ] Dashes and ellipses used for conversational rhythm
- [ ] Question marks where voice would rise
- [ ] Exclamation points used sparingly for emphasis

**Script-Specific Punctuation:**
```
✅ Use comma for short pause: "First, let me explain this."
✅ Use dash for aside: "The system—which I've used for years—actually works."
✅ Use ellipsis for thoughtful pause: "So... what does this mean?"
✅ Use period for full stop/breath: "Stop. Think about this. Really think."
```

#### Common Errors to Flag
- [ ] Misplaced apostrophes (its vs it's)
- [ ] Incorrect homophones (there/their/they're, your/you're)
- [ ] Double negatives (unless intentional for emphasis)
- [ ] Dangling modifiers
- [ ] Parallel structure in lists

### Grammar Review Outcome

**Classify Issues:**
- **Critical**: Errors that confuse meaning
- **Important**: Errors that distract but don't confuse
- **Minor**: Style improvements that enhance professionalism

**Recommendation:**
- Pass to Improvements if: Critical or Important issues found
- Pass to Optimization if: Only minor issues found
- Return to Draft if: Fundamental grammatical problems throughout

---

## 2. Readability Review

**Module**: `T/Rewiew/Readability`

### Purpose
Ensure script can be easily read aloud and understood by target audience.

### Checklist

#### Read-Aloud Test
- [ ] Entire script read aloud without stumbling
- [ ] No tongue-twisters or awkward word combinations
- [ ] Natural breathing points exist
- [ ] Pacing feels appropriate when spoken
- [ ] No sentences cause breathlessness

**Test Method:**
1. Read script aloud at conversational pace
2. Mark any place you stumble or struggle
3. Mark any place you run out of breath
4. Mark any phrase that sounds awkward
5. Mark any section that feels rushed

**Examples:**
```
❌ "The statistics show significantly substantial systematic improvements."
(Too many similar-sounding words)
✅ "The statistics show major improvements across the board."

❌ "She sells seashells by the systematic seashore solutions."
(Accidental tongue-twister)
```

#### Sentence Length Analysis
- [ ] Average sentence length: 15-20 words for general audience
- [ ] Sentence length varies (short, medium, long mixed)
- [ ] No sentence exceeds 30 words without clear pause/breath point
- [ ] Long sentences use clear structure (list, contrast, etc.)

**Audit Method:**
```
Short (< 12 words): Should be ~30% of sentences
Medium (12-20 words): Should be ~50% of sentences
Long (20-30 words): Should be ~15% of sentences
Very Long (> 30 words): Should be <5% and have clear pauses
```

#### Paragraph/Segment Length
- [ ] Paragraphs are 3-5 sentences maximum (for text)
- [ ] Continuous speaking segments are 20-45 seconds maximum (for audio)
- [ ] Natural break points every 1-2 minutes
- [ ] White space or pauses provide breathing room

#### Reading Level Assessment
- [ ] Appropriate for target audience
- [ ] Technical complexity matches audience expertise
- [ ] Vocabulary is accessible without dumbing down
- [ ] Complex concepts explained simply when needed

**Reading Level Targets:**
- General audience: Grade 7-9 reading level
- Professional audience: Grade 10-12 reading level
- Technical audience: Grade 12+ acceptable
- Youth audience: Grade 5-7 reading level

**Tools:**
- Flesch Reading Ease: 60-70 for general audience
- Flesch-Kincaid Grade Level: Matches target audience

#### Word Choice Clarity
- [ ] Active voice preferred (passive acceptable when intentional)
- [ ] Concrete nouns over abstract when possible
- [ ] Strong verbs over weak verb + adverb
- [ ] Simple words over complex when meaning is equivalent
- [ ] Jargon explained or replaced

**Examples:**
```
Passive → Active:
❌ "The system was designed by our team to help productivity."
✅ "Our team designed this system to boost productivity."

Abstract → Concrete:
❌ "It facilitates optimization of temporal resource allocation."
✅ "It helps you use your time better."

Weak → Strong:
❌ "Walk quickly to the door."
✅ "Rush to the door."
```

#### Flow and Transitions
- [ ] Each section connects logically to the next
- [ ] Transitions are smooth and natural
- [ ] No abrupt topic changes
- [ ] Forward momentum maintained

**Transition Quality Check:**
```
❌ Abrupt: "So that's email. Let's talk about calendars."
✅ Smooth: "Email sorted. Now let's apply the same thinking to calendars."
✅ Better: "Once your email flows smoothly, your calendar is the next bottleneck to fix."
```

### Readability Metrics

**Calculate and Document:**
- Total word count: [number]
- Average sentence length: [number] words
- Longest sentence: [number] words
- Reading level: [grade level]
- Estimated speaking time: [minutes] at 150 words/minute

### Readability Review Outcome

**Pass Criteria:**
- [ ] Can be read aloud comfortably throughout
- [ ] Reading level matches target audience
- [ ] Sentence and paragraph lengths vary naturally
- [ ] Flow and transitions work smoothly

**Red Flags:**
- Multiple stumbling points when reading aloud
- Consistent breathlessness at natural speaking pace
- Reading level too high or too low for audience
- Monotonous sentence structure throughout

---

## 3. Tone and Voice Review

**Module**: `T/Rewiew/Tone`

### Purpose
Ensure consistent, appropriate tone and voice that matches brand and audience expectations.

### Checklist

#### Voice Consistency
- [ ] Point of view consistent (first/third person)
- [ ] Person doesn't shift unexpectedly (I/we/you confusion)
- [ ] Voice style consistent throughout (casual/professional/academic)
- [ ] Personality traits consistent (humorous, serious, empathetic)

**Check for Inconsistencies:**
```
❌ "I tested this approach... We found that... One might conclude..."
(Shifting between first, plural, and impersonal)
✅ "I tested this approach... I found that... I concluded..."
(Consistent first-person)
```

#### Tone Appropriateness
- [ ] Tone matches target audience expectations
- [ ] Formality level appropriate for platform
- [ ] Emotional quality aligns with content purpose
- [ ] Tone serves the message (not just for style)

**Tone Mapping:**
```
Audience: Young professionals → Tone: Conversational but professional
Audience: Executives → Tone: Authoritative, data-driven
Audience: Beginners → Tone: Encouraging, patient, clear
Audience: Experts → Tone: Peer-level, nuanced, detailed
```

#### Emotional Consistency
- [ ] Emotional tone consistent within sections
- [ ] Emotional shifts are intentional and justified
- [ ] Emotional quality matches Idea specifications
- [ ] Emotion serves engagement, not manipulation

**Emotional Arc Check:**
```
✅ Deliberate shift: "I was frustrated [emotion: frustration]. 
But then I discovered [emotion: hope]. Now I'm energized [emotion: triumph]."

❌ Unintentional clash: "This is a serious, critical problem. Anyway, lol, 
let's fix it!"
```

#### Formality Level
- [ ] Contractions used (or not) consistently
- [ ] Casual language appropriate for platform
- [ ] Technical language level matches audience
- [ ] Slang or colloquialisms work for target demographic

**Formality Spectrum:**
```
Very Casual: "Gonna show you how to crush your to-do list"
Casual: "I'll show you how to tackle your to-do list"
Professional: "I will demonstrate an effective approach to task management"
Formal: "This methodology presents a systematic approach to task prioritization"
Academic: "We propose a framework for optimizing task allocation efficiency"
```

#### Brand Voice Alignment
- [ ] Matches established brand voice guidelines (if applicable)
- [ ] Reflects creator's authentic style
- [ ] Differentiates from competitors
- [ ] Feels genuine, not forced

**Brand Voice Attributes to Check:**
- Friendly vs Professional
- Confident vs Humble
- Innovative vs Traditional
- Playful vs Serious
- Expert vs Peer

#### Cultural Sensitivity
- [ ] Language is inclusive and respectful
- [ ] No unintentional bias or stereotypes
- [ ] Cultural references are appropriate and explained
- [ ] Humor doesn't alienate or offend

### Tone Review Outcome

**Document:**
- Overall tone classification: [description]
- Consistency rating: [Excellent/Good/Needs Work]
- Appropriateness for audience: [Yes/Needs Adjustment]
- Specific tone issues: [list]

**Pass Criteria:**
- Tone is consistent throughout
- Tone matches audience and platform
- Emotional quality aligns with Idea
- Voice feels authentic

---

## 4. Content Accuracy Review

**Module**: `T/Rewiew/Content`

### Purpose
Verify factual accuracy, logical coherence, and content completeness.

### Checklist

#### Factual Accuracy
- [ ] All specific claims are accurate
- [ ] Statistics are current and sourced
- [ ] Quotes are accurate and attributed
- [ ] Technical concepts are correctly explained
- [ ] Examples are factually sound

**Verification Process:**
```
For each factual claim:
1. Identify the claim
2. Check source or verify independently
3. Confirm it's current (not outdated)
4. Ensure context isn't misleading
5. Document source for reference
```

**Common Accuracy Issues:**
```
❌ "Studies show 90% of people..." (Which studies? When? What methodology?)
✅ "A 2024 Stanford study of 10,000 knowledge workers found that 90%..."

❌ "X is the best tool for Y" (Subjective, not factual)
✅ "X is my preferred tool for Y because..." (Opinion clearly stated)
```

#### Source Verification
- [ ] All statistics cited have sources
- [ ] Sources are credible and recent
- [ ] Sources support the claims made
- [ ] No cherry-picking or misrepresentation
- [ ] Secondary sources verified against primary when possible

**Source Quality Tiers:**
1. **Strong**: Peer-reviewed research, official statistics, primary sources
2. **Good**: Reputable publications, expert interviews, industry reports
3. **Acceptable**: Established blogs, case studies, surveys (if methodology sound)
4. **Weak**: Anonymous sources, outdated data, opinion pieces
5. **Unacceptable**: Unsourced claims, fake statistics, misleading data

#### Technical Accuracy
- [ ] Technical concepts explained correctly
- [ ] No oversimplification that creates inaccuracy
- [ ] Technical terminology used correctly
- [ ] Complexity appropriate for audience (can be simplified without being wrong)

**Have Expert Review If:**
- Technical concepts are central to content
- Claims could mislead if inaccurate
- Audience includes subject matter experts
- Reputation risk if content is wrong

#### Logical Coherence
- [ ] Arguments follow logical structure
- [ ] Conclusions supported by evidence
- [ ] No logical fallacies
- [ ] Cause-effect relationships valid
- [ ] No contradiction between sections

**Common Logical Issues:**
```
❌ False Causation: "I started using X and my productivity improved, 
so X improves productivity." (Correlation ≠ causation)
✅ Better: "I started using X. Over 3 months, I tracked a 20% improvement. 
While other factors may have contributed, X was the main change I made."

❌ Hasty Generalization: "I tried this once and it worked, so it always works."
✅ Better: "In my experience, this worked. Your results may vary depending on..."
```

#### Completeness
- [ ] All outline sections covered
- [ ] No critical gaps in explanation
- [ ] Examples provided where needed
- [ ] Questions raised are answered
- [ ] Promise made in hook is delivered

**Completeness Check:**
```
For each major section from outline:
- [ ] Topic introduced clearly
- [ ] Key points all addressed
- [ ] Supporting evidence provided
- [ ] Practical application shown
- [ ] Transition to next section exists
```

#### Relevance
- [ ] All content relates to core thesis
- [ ] No significant tangents
- [ ] Examples support main points
- [ ] Length appropriate to importance
- [ ] No padding or filler

**Trim or Expand:**
```
Trim: Interesting but tangential stories
Trim: Redundant explanations of same point
Expand: Critical concepts explained too briefly
Expand: Claims without sufficient support
```

### Content Accuracy Outcome

**Document:**
- Factual claims verified: [count] / [total]
- Sources checked: [count]
- Technical accuracy: [Verified/Needs Expert Review]
- Logical coherence: [Strong/Adequate/Needs Work]
- Completeness: [Complete/Gaps Identified]

**Critical Issues:**
- List any factual errors found
- Note any unverifiable claims
- Flag any logical fallacies
- Identify any completeness gaps

---

## 5. Consistency Review

**Module**: `T/Rewiew/Consistency`

### Purpose
Ensure consistent terminology, style, formatting, and voice throughout the script.

### Checklist

#### Terminology Consistency
- [ ] Key terms used consistently throughout
- [ ] No switching between synonyms unnecessarily
- [ ] Acronyms defined on first use, then used consistently
- [ ] Product/concept names spelled consistently
- [ ] Technical terms used consistently

**Consistency Audit:**
```
Create a terminology map:
- "AI agent" → Always "AI agent" (not "AI assistant", "agent", "AI system" interchangeably)
- "to-do list" → Always "to-do list" (not "todo list", "task list", "checklist" interchangeably)
- First use: "Getting Things Done (GTD)" → Then: "GTD" consistently
```

**When Variation is Acceptable:**
- Pronoun references to avoid repetition
- Intentional escalation ("challenge" → "problem" → "crisis")
- Different contexts genuinely need different terms

#### Style Consistency
- [ ] Contractions used consistently (all or none or intentional mix)
- [ ] Numbers formatted consistently (spelled out or numerals)
- [ ] Time references consistent (12-hour/24-hour)
- [ ] Date formats consistent
- [ ] Capitalization style consistent

**Style Guidelines to Check:**
```
Contractions:
- Consistent: "I'll, you'll, we'll" throughout
- OR Consistent: "I will, you will, we will" throughout
- Inconsistent: Mix without clear reason

Numbers:
- "One, two, three" for small numbers
- "15, 100, 1,000" for larger numbers
- "10%" or "ten percent" (choose one style)

Lists:
- Either all bulleted or all numbered consistently
- Either all complete sentences or all fragments
- Either all ending with periods or none
```

#### Formatting Consistency
- [ ] Headers formatted consistently
- [ ] Lists formatted consistently
- [ ] Code/technical elements marked consistently
- [ ] Emphasis (bold/italic) used consistently
- [ ] Section breaks consistent

#### Voice Consistency
- [ ] Same person/perspective throughout
- [ ] Same personality throughout
- [ ] Same energy level (or intentional variation)
- [ ] Same relationship with audience (peer/expert/guide)

**Voice Shift Check:**
```
❌ Inconsistent: 
Section 1: "Let me show you..." (Guide voice)
Section 2: "As we all know..." (Peer voice)
Section 3: "Research indicates..." (Expert voice)

✅ Consistent:
Throughout: "Let me walk you through..." (Guide voice maintained)
```

#### Reference Consistency
- [ ] Time references make sense (earlier/later)
- [ ] Section references are accurate
- [ ] "Above" and "below" appropriate for format
- [ ] Callback references are clear and accurate

**Platform-Specific:**
```
For Audio/Video:
- "As I mentioned earlier" ✓
- "Coming up next" ✓
- "As shown above" ✗ (no spatial reference in audio)

For Text:
- "See the image below" ✓
- "As discussed in the previous section" ✓
- "A moment ago" ✗ (time reference not clear in text)
```

### Consistency Review Outcome

**Document:**
- Terminology map created: [Yes/No]
- Style inconsistencies found: [count]
- Formatting issues: [count]
- Voice consistency: [Excellent/Good/Needs Work]

**Required Actions:**
- List specific consistency fixes needed
- Note any acceptable variations to preserve
- Identify any patterns of inconsistency

---

## 6. Final Editing Review

**Module**: `T/Rewiew/Editing`

### Purpose
Final polish pass to eliminate redundancy, improve efficiency, and ensure maximum impact.

### Checklist

#### Redundancy Elimination
- [ ] No unnecessary repetition of points
- [ ] No redundant words in sentences
- [ ] No overlapping sections
- [ ] Repetition is intentional (for emphasis/retention)

**Common Redundancies:**
```
❌ "First and foremost, the most important thing is..."
✅ "The most important thing is..."

❌ "The reason is because..."
✅ "The reason is..." OR "Because..."

❌ "In my personal opinion, I think..."
✅ "I believe..."
```

#### Word Economy
- [ ] Filler words removed or minimized
- [ ] Wordy phrases tightened
- [ ] Each word earns its place
- [ ] No padding to hit length target

**Common Filler to Remove:**
```
❌ "Basically, what I'm trying to say is that productivity is important."
✅ "Productivity is important."

❌ "In order to improve your workflow..."
✅ "To improve your workflow..."

❌ "Due to the fact that..."
✅ "Because..."

❌ "At this point in time..."
✅ "Now..."
```

**Wordy → Concise:**
```
❌ "Give consideration to..." → ✅ "Consider..."
❌ "Make a decision about..." → ✅ "Decide..."
❌ "In the event that..." → ✅ "If..."
❌ "A majority of..." → ✅ "Most..."
```

#### Verb Strength
- [ ] Active verbs preferred
- [ ] Weak verb + adverb replaced with strong verb
- [ ] "To be" verbs minimized where stronger options exist
- [ ] Action verbs create energy

**Verb Strengthening:**
```
❌ "He walked quickly" → ✅ "He rushed"
❌ "She talked loudly" → ✅ "She shouted"
❌ "The system is working" → ✅ "The system works"
❌ "It was improving" → ✅ "It improved"
```

#### Sentence Efficiency
- [ ] No unnecessary clauses
- [ ] Complex sentences simplified where possible
- [ ] Nested structures reduced
- [ ] Each sentence has clear purpose

**Simplification:**
```
❌ "The system, which was designed by our team over the course of 
several months of intensive development, helps users manage tasks."
✅ "Our system helps users manage tasks. We spent months perfecting it."

❌ "What I'm going to do is explain the process that you need to follow 
in order to achieve the results that you want."
✅ "I'll explain how to achieve your desired results."
```

#### Transition Quality
- [ ] All transitions are smooth
- [ ] Transitions add value (not just filler)
- [ ] Natural progression between ideas
- [ ] Momentum maintained

**Transition Improvement:**
```
❌ Weak: "Now I want to talk about email."
✅ Better: "Let's apply this to email."
✅ Best: "Your task list is organized. Now let's tackle the email inbox the same way."
```

#### Impact Maximization
- [ ] Opening hook is as strong as possible
- [ ] Key points land with impact
- [ ] Conclusion is memorable
- [ ] CTA is compelling
- [ ] Quotable moments exist

**Punchline Sharpening:**
```
Before: "So basically, what this means is that you should probably 
focus on what's important."
After: "Focus on what matters. Everything else is noise."

Before: "The interesting thing about this approach is that it really 
works well for most people."
After: "This approach works. Period."
```

#### Length Optimization
- [ ] Script length appropriate for platform
- [ ] No sections feel too long or rushed
- [ ] Pacing supports engagement
- [ ] Trim without losing substance

**Length Guidelines:**
- Short-form (TikTok/Reels): 300-600 words (90-180 seconds)
- Medium-form (YouTube): 1,500-2,500 words (10-15 minutes)
- Long-form (Podcast/Blog): 2,500-5,000 words (15-30+ minutes)

#### Polish
- [ ] Flow is smooth throughout
- [ ] Rhythm varies appropriately
- [ ] Energy matches content
- [ ] Ready for final approval

### Final Editing Outcome

**Document:**
- Words removed: [count]
- Redundancies eliminated: [count]
- Transitions improved: [count]
- Impact enhancements: [count]
- Final word count: [number]
- Ready for optimization: [Yes/No]

---

## Overall Review Summary

### Review Completion Checklist

After completing all review dimensions:

- [ ] **Grammar**: All critical and important issues documented
- [ ] **Readability**: Read-aloud test passed, metrics calculated
- [ ] **Tone**: Consistency verified, appropriateness confirmed
- [ ] **Content**: Facts checked, logic verified, completeness assessed
- [ ] **Consistency**: Terminology mapped, style standardized
- [ ] **Editing**: Redundancy removed, impact maximized

### Review Outcome Classification

**Grade A: Ready for Optimization**
- All dimensions passed
- Only minor issues identified
- Strong foundation for optimization
- Can proceed directly to Script Optimization phase

**Grade B: Needs Improvements**
- Some important issues found
- No critical structural problems
- Should pass through Script Improvements phase
- Will be ready for optimization after improvements

**Grade C: Needs Significant Revision**
- Multiple important issues across dimensions
- Some structural concerns
- Requires Script Improvements phase
- May need multiple improvement passes

**Grade D: Return to Draft**
- Critical issues in multiple dimensions
- Structural problems
- Fundamental gaps or errors
- Should return to Script Draft phase

**Grade F: Return to Idea/Outline**
- Fundamental concept problems
- Script doesn't work as written
- Outline was insufficient
- Should return to Idea phase

### Consolidated Feedback Document

Create comprehensive feedback document:

```markdown
# Script Review Feedback

## Script Information
- Idea ID: [reference]
- Title: [working title]
- Review Date: [YYYY-MM-DD]
- Reviewer: [name/ID]
- Overall Grade: [A/B/C/D/F]

## Review Summary

### Strengths
- [List 3-5 things script does well]

### Areas for Improvement
- [Prioritized list of improvements needed]

### Critical Issues (Must Fix)
- [Any issues that prevent moving forward]

## Dimension-Specific Feedback

### Grammar and Syntax
- Status: [Pass/Needs Improvement/Fail]
- Issues: [count]
- Details: [specific issues]

### Readability
- Status: [Pass/Needs Improvement/Fail]
- Reading Level: [grade level]
- Read-Aloud: [Pass/Issues]
- Details: [specific issues]

### Tone and Voice
- Status: [Pass/Needs Improvement/Fail]
- Consistency: [Excellent/Good/Poor]
- Details: [specific issues]

### Content Accuracy
- Status: [Pass/Needs Improvement/Fail]
- Facts Verified: [count/total]
- Details: [specific issues]

### Consistency
- Status: [Pass/Needs Improvement/Fail]
- Issues: [count]
- Details: [specific issues]

### Final Editing
- Status: [Pass/Needs Improvement/Fail]
- Efficiency: [Excellent/Good/Needs Work]
- Details: [specific issues]

## Recommended Next Steps

1. [Priority 1 action]
2. [Priority 2 action]
3. [Priority 3 action]

## Next Phase
- [ ] Proceed to Script Optimization
- [ ] Route to Script Improvements
- [ ] Return to Script Draft
- [ ] Return to Idea Phase

---
Review completed: [timestamp]
```

## Using This Checklist

### For Human Reviewers
1. Work through dimensions systematically
2. Document issues as you find them
3. Provide specific, actionable feedback
4. Balance criticism with recognition of strengths
5. Consider the script's goals and audience

### For AI Reviewers
1. Apply each checklist dimension thoroughly
2. Provide specific examples for each issue
3. Suggest concrete improvements
4. Maintain objectivity while considering context
5. Output structured feedback document

### For Self-Review
1. Use as final check before submitting
2. Be honest about issues found
3. Fix obvious problems before formal review
4. Document any uncertainty for reviewers
5. Don't skip dimensions

## Related Documentation

- [Script Draft Creation Guide](/_meta/research/script-draft-creation-guide.md)
- [Script Draft Process](./SCRIPT_DRAFT_PROCESS.md)
- [Optimization Strategies](./OPTIMIZATION_STRATEGIES.md)
- [T/Rewiew Module](../../Rewiew/README.md)

---

*A thorough review ensures quality improvements and optimization efforts are built on a solid foundation.*
