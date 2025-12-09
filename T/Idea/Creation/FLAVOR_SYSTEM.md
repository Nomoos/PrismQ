# Flavor System - Complete Transformation Guide

## Overview

All 93 variant templates have been transformed into thematic flavors that guide AI-powered idea refinement. Each flavor represents a unique conceptual orientation derived from its corresponding variant template.

## Total Flavors: 93

### Flavor Categories (12 Total)

#### 1. Emotional & Dramatic (7 flavors)
- Emotion-First Hook
- Emotional Drama + Growth
- Personal Drama (First-Person Voice)
- Confession Story Seed
- Real Family Drama Seed
- Safe Person Seed
- Holding Space Seed

#### 2. Mystery & Discovery (6 flavors)
- Mystery/Curiosity Gap
- Light Mystery + Adventure
- Mystery with Emotional Hook
- Overheard Truth Seed
- What They Don't Know Seed
- Confession + Mystery Fusion

#### 3. Psychological & Internal (8 flavors)
- Psychological Tension
- Introspective Transformation
- Mirror Moment Seed
- Before/After Transformation Seed
- The Version of Me Seed
- Quiet Rebellion Seed
- Body Acceptance Seed
- Fitting In Seed

#### 4. Identity & Growth (6 flavors)
- Identity + Empowerment
- Heritage Discovery Story Seed
- Emotional Inheritance Seed
- Permission To Seed
- Learned Young Seed
- Rewriting the Story Seed

#### 5. Relationship & Connection (6 flavors)
- Soft Supernatural + Friendship
- Chosen Family Seed
- Growing Apart Seed
- First Butterflies Seed
- Online Connection Seed
- Safe Person Seed

#### 6. Tension & Conflict (5 flavors)
- Competitive + Rivals to Allies
- School + Family Collision
- Social + Home Drama
- Unsent Message Seed
- Almost Said Seed

#### 7. Adventure & Challenge (4 flavors)
- Survival Challenge (Safe)
- Urban Social Quest
- Light Mystery + Adventure
- Sci-Fi + School Realism

#### 8. Transformation & Change (4 flavors)
- Before/After Transformation Seed
- Overheard + Transformation Fusion
- Parallel Lives Seed
- Last Time Seed

#### 9. Existential & Meaning (4 flavors)
- Existential Conflict
- Future Anxiety Seed
- Comparison Trap Seed
- Emotional Inheritance Seed

#### 10. Romance & Attraction (4 flavors)
- Romantic Tension
- First Butterflies Seed
- First Butterflies + Fitting In Blend
- Body Acceptance + First Butterflies Blend

#### 11. Moral & Ethical (4 flavors)
- Moral Dilemma
- Sci-Fi + School Realism
- Quiet Rebellion Seed
- AI as Companion (Safe)

#### 12. Creative & Aesthetic (4 flavors)
- Magical Realism + Aesthetic
- Niche-Blend
- Genre Focus
- Story Skeleton

## How Flavors Work

### Conceptual Orientation

Each flavor provides an abstract direction for tone or emphasis rather than prescriptive content. When you specify a flavor:

1. **Guides refinement**: The AI understands the thematic context
2. **Maintains core idea**: Doesn't add new content, just refines
3. **Conceptual focus**: Emphasizes certain aspects without being descriptive
4. **Consistent output**: Always 5 sentences, regardless of flavor

### Template Integration

The `idea_improvement.txt` template includes:

```
...conceptually orient it toward the thematic flavor specified in [FLAVOR], 
interpreting this flavor as an abstract direction for tone or emphasis 
rather than a cue for descriptive or narrative writing...
```

### API Usage

```python
from ai_generator import AIIdeaGenerator
from flavors import list_flavors, search_flavors_by_keyword, pick_weighted_flavor

# Browse all flavors
all_flavors = list_flavors()  # Returns all 93

# Search for specific themes
mystery_flavors = search_flavors_by_keyword("mystery")
emotional_flavors = search_flavors_by_keyword("emotional")

# Use with AI
generator = AIIdeaGenerator()

# Method 1: Use weighted random flavor (DEFAULT - recommended)
result = generator.generate_with_custom_prompt(
    input_text="Your idea here",
    prompt_template_name="idea_improvement"
)
# Automatically selects a weighted random flavor
# High-weight flavors (100) are more likely: "Emotional Drama + Growth", "Identity + Empowerment", etc.

# Method 2: Specify a particular flavor
result = generator.generate_with_custom_prompt(
    input_text="Your idea here",
    prompt_template_name="idea_improvement",
    flavor="Mystery + Unease"  # Explicit flavor selection
)

# Method 3: Pick a random flavor yourself
selected_flavor = pick_weighted_flavor()
result = generator.generate_with_custom_prompt(
    input_text="Your idea here",
    prompt_template_name="idea_improvement",
    flavor=selected_flavor
)
```

### Weighted Selection

Flavors use **weighted random selection** by default:

- Each flavor inherits the weight from its corresponding variant template
- Weights range from 25 to 100
- **Ultra-primary flavors (weight 100)**: 31 flavors optimized for US girls 15-18
  - Examples: "Emotional Drama + Growth", "Identity + Empowerment", "Body Acceptance Seed"
- **Very high flavors (weight 92-98)**: Strong teen appeal
  - Examples: "Magical Realism + Aesthetic", "School + Family Collision"
- **High flavors (weight 70-88)**: Good appeal across ages
  - Examples: "Light Mystery + Adventure", "Soft Supernatural + Friendship"
- **Moderate flavors (weight 45-65)**: Broader appeal
- **Lower weights (25-40)**: More specialized or structured themes

This ensures the most relevant and engaging flavors are selected more frequently while maintaining variety.

## Complete Flavor List

### A-C
1. 4-Point Quick Structure
2. AI as Companion (Safe)
3. Almost Said Seed
4. Before/After Transformation Seed
5. Body Acceptance + Comparison Trap Blend
6. Body Acceptance + First Butterflies Blend
7. Body Acceptance Seed
8. Chosen Family + Growing Apart Fusion
9. Chosen Family + Online Connection Blend
10. Chosen Family Seed
11. Comparison Trap Seed
12. Competitive + Rivals to Allies
13. Confession + Mystery Fusion
14. Confession Moment + Body Acceptance Blend
15. Confession Story Seed

### D-H
16. Emotion-First Hook
17. Emotional Drama + Growth
18. Emotional Inheritance Seed
19. First Butterflies + Fitting In Blend
20. First Butterflies Seed
21. Fitting In + Comparison Trap Blend
22. Fitting In Seed
23. Future Anxiety + Comparison Trap Blend
24. Future Anxiety Seed
25. Genre Focus
26. Grief Growth + Scene Seed Blend
27. Growing Apart + Online Connection Blend
28. Growing Apart Seed
29. Held Space Seed
30. Heritage Discovery + Genre Frame Blend
31. Heritage Discovery Story Seed
32. Holding Space Seed
33. Hook + Frame

### I-M
34. Identity + Empowerment
35. Identity Power + Fitting In Blend
36. Imposter Feelings + Mystery Structure Blend
37. Last Time Seed
38. Learned Young + Body Acceptance Blend
39. Learned Young Seed
40. Light Mystery + Adventure
41. Magical Realism + Aesthetic
42. Mentor Moment + Hook Frame Blend
43. Minimal Idea Packet
44. Mirror Moment + Body Acceptance Blend
45. Mirror Moment + Emotional Inheritance Fusion
46. Mirror Moment Seed
47. Money Reality + Shortform Blend
48. Mystery/Curiosity Gap

### N-R
49. Niche-Blend
50. Online Connection + Fitting In Blend
51. Online Connection + Future Anxiety Blend
52. Online Connection Seed
53. Overheard + Transformation Fusion
54. Overheard Truth Seed
55. Parallel Lives + Permission To Fusion
56. Parallel Lives Seed
57. Permission To + Body Acceptance Blend
58. Permission To Seed
59. Personal Drama (First-Person Voice)
60. Pet Bond + Personal Voice Blend
61. Quiet Rebellion + Body Acceptance Blend
62. Quiet Rebellion Seed
63. Real Family Drama Seed

### S-Z
64. Rewriting the Story + Body Acceptance Blend
65. Rewriting the Story Seed
66. Safe Person + Online Connection Blend
67. Safe Person Seed
68. Scene Seed
69. School + Family Collision
70. Sci-Fi + School Realism
71. Short Form 2.0
72. Short-Form Viral
73. Sibling Truth + Emotion-First Blend
74. Small Moment, Big Meaning + Comparison Trap Blend
75. Small Moment, Big Meaning Seed
76. Social + Home Drama
77. Soft Supernatural + Friendship
78. Story Skeleton
79. Survival Challenge (Safe)
80. The Version of Me Seed
81. Unsent Message + Future Anxiety Blend
82. Unsent Message + Quiet Rebellion Fusion
83. Unsent Message Seed
84. Urban Social Quest
85. What They Don't Know Seed
86. ... (and more blend variations)

## Examples by Use Case

### For Mystery Stories
- Mystery/Curiosity Gap
- Light Mystery + Adventure  
- Mystery with Emotional Hook
- Overheard Truth Seed
- What They Don't Know Seed

### For Character Growth
- Emotional Drama + Growth
- Before/After Transformation Seed
- Introspective Transformation
- Identity + Empowerment
- The Version of Me Seed

### For Relationship Stories
- Soft Supernatural + Friendship
- Chosen Family Seed
- Growing Apart Seed
- First Butterflies Seed
- Romantic Tension

### For Internal Conflict
- Psychological Tension
- Mirror Moment Seed
- Quiet Rebellion Seed
- Body Acceptance Seed
- Fitting In Seed

## Technical Implementation

### Automatic Generation

Flavors are automatically generated from variant templates:

```python
from idea_variants import list_templates, get_template

for template_key in list_templates():
    template = get_template(template_key)
    flavor_name = template['name']  # Becomes flavor
    description = template['description']  # Flavor description
```

### Categorization

Flavors are categorized based on thematic keywords in descriptions:
- emotional, feeling → Emotional & Dramatic
- mystery, puzzle → Mystery & Discovery
- tension, conflict → Psychological & Internal
- transform, growth → Transformation & Change
- etc.

### Search & Retrieval

```python
from flavors import search_flavors_by_keyword, get_flavor_info

# Find flavors
matches = search_flavors_by_keyword("transformation")

# Get details
info = get_flavor_info("Mirror Moment Seed")
# Returns: {description, variant_key, keywords, template_name}
```

## Best Practices

1. **Choose appropriate flavor**: Match flavor to your idea's natural themes
2. **Experiment**: Try different flavors with the same input
3. **Understand conceptual vs. descriptive**: Flavors guide ideas, not descriptions
4. **Browse categories**: Find thematically related flavors
5. **Search by keyword**: Quickly find relevant orientations

## See Also

- `flavors.py` - Full implementation
- `flavor_examples.py` - Working examples
- `CUSTOM_PROMPTS.md` - Complete usage guide
- `idea_improvement.txt` - Updated template with [FLAVOR] support
