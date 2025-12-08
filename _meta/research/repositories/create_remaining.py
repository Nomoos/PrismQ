repos = [
    {
        "filename": "YouTube-AI-Automation-Pipeline.md",
        "name": "zammaar/YouTube-AI-Automation-Pipeline",
        "category": "YouTube and Video Automation",
        "url": "https://github.com/zammaar/YouTube-AI-Automation-Pipeline",
        "stars": 1,
        "language": "Python",
        "description": "Fully automated YouTube content creation pipeline",
        "features": ["Topic research", "Script generation", "Voice synthesis (ElevenLabs)", "Video assembly", "Thumbnail creation", "Automated publishing", "OpenAI and YouTube APIs"],
        "comparison_strengths": ["Complete automation pipeline", "Script → Voice → Video workflow (similar to PrismQ)", "Automated publishing", "Python-based"],
        "comparison_limitations": ["YouTube-only (no blog/podcast)", "No analytics/metrics module", "Simpler than PrismQ's state machine"],
        "extractable": ["Complete Automation Pipeline", "ElevenLabs TTS Integration", "Thumbnail Generation", "YouTube API Publishing"],
        "priority": "High",
        "priority_note": "Most similar to PrismQ's approach. Automation and publishing patterns very relevant."
    },
    {
        "filename": "more-attention.md",
        "name": "Marques-079/more-attention",
        "category": "YouTube and Video Automation",
        "url": "https://github.com/Marques-079/more-attention",
        "stars": 1,
        "language": "Jupyter Notebook",
        "description": "Automated content generation from Script → Video → Editing → Posting",
        "features": ["Sequential workflow", "Kokoro TTS", "YouTube automation"],
        "comparison_strengths": ["Similar sequential workflow", "YouTube automation"],
        "comparison_limitations": ["Narrower scope", "No separate audio/text publishing"],
        "extractable": ["Sequential Pipeline Pattern", "Kokoro TTS Integration"],
        "priority": "Low",
        "priority_note": "Limited unique patterns beyond what other repos offer."
    }
]

template = '''# {name}

**Category:** {category}  
**GitHub URL:** {url}  
**Stars:** ⭐ {stars}  
**Language:** {language}

---

## Overview

{description}

## Key Features

{features_list}

## Technology Stack

- **Primary Language:** {language}
{tech_extras}

## Comparison to PrismQ

### Strengths
{strengths_list}

### Limitations
{limitations_list}

## Extractable Mechanics

{extractables_list}

## Implementation Priority

**{priority}** - {priority_note}

---

*Last Updated: December 8, 2024*  
*Research Document: [Similar Repositories Research](../similar-repositories-research.md)*
'''

for repo in repos:
    content = template.format(
        name=repo['name'],
        category=repo['category'],
        url=repo['url'],
        stars=repo['stars'],
        language=repo['language'],
        description=repo['description'],
        features_list='\n'.join([f"- **{f}**" if i == 0 else f"- {f}" for i, f in enumerate(repo['features'])]),
        tech_extras='- **Additional:** ' + ', '.join(repo['features'][:2]) if len(repo['features']) > 2 else '',
        strengths_list='\n'.join([f"- ✅ **{s}**" for s in repo['comparison_strengths']]),
        limitations_list='\n'.join([f"- ❌ **{l}**" for l in repo['comparison_limitations']]),
        extractables_list='\n'.join([f"{i+1}. **{e}**" for i, e in enumerate(repo['extractable'])]),
        priority=repo['priority'],
        priority_note=repo['priority_note']
    )
    
    with open(repo['filename'], 'w') as f:
        f.write(content)
    print(f"Created {repo['filename']}")
