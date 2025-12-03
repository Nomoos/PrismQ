"""Analyzed YouTube Video: "When that acting challenge suddenly feels a little too real"

This file contains the IdeaInspiration analysis from a YouTube video that tells
the story of Mera, an 11-year-old autistic girl who uses her bo staff training
to defend her friend Theo from a violent bully.

Video Metadata:
    Title: When that acting challenge suddenly feels a little too real
    Likes: 97
    Views: 2,217
    Posted: 8 hours ago
    Source: YouTube (subtitles provided)

Story Summary:
    An 11-year-old autistic girl named Mera has been training with a bo staff
    (hand-carved by her late grandfather) for 3 years, practicing 5+ hours daily.
    When a 13-year-old bully named Vanessa violently attacks Mera's best friend 
    Theo (who has ADHD), then stalks him and eventually breaks into Mera's home
    with a knife, Mera uses her training to defend them both. The story ends
    with Mera being cleared of any wrongdoing (self-defense in defense of another).

Key Themes:
    - Neurodivergent empowerment (autism and ADHD)
    - Deep friendship and loyalty
    - Dedication and training paying off
    - Legacy from a loved one (grandfather's staff)
    - Standing up to bullies
    - Self-defense in protection of others

Target Audience:
    - Parents of neurodivergent children
    - Neurodivergent community
    - Self-defense/martial arts enthusiasts
    - Anti-bullying advocates
    - Young adults aged 15-35

Content Potential:
    - High emotional engagement (protective friendship)
    - Strong narrative arc (training → threat → triumph)
    - Relatable characters
    - Satisfying resolution
    - Viral potential (neurodivergent empowerment angle)
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add paths for imports
# Path: Video/_meta/examples -> Video -> YouTube -> Source -> Inspiration -> Idea -> Model/src
model_path = Path(__file__).resolve().parents[6] / 'Model' / 'src'
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

# Try to import the Idea model, fallback to minimal definition if not available
try:
    from idea import Idea, ContentGenre, IdeaStatus
except ImportError:
    # Minimal fallback for standalone execution
    from enum import Enum
    from dataclasses import dataclass, field
    from datetime import datetime
    
    class ContentGenre(Enum):
        TRUE_CRIME = "true_crime"
        MYSTERY = "mystery"
        HORROR = "horror"
        SCIENCE_FICTION = "science_fiction"
        DOCUMENTARY = "documentary"
        EDUCATIONAL = "educational"
        ENTERTAINMENT = "entertainment"
        LIFESTYLE = "lifestyle"
        TECHNOLOGY = "technology"
        OTHER = "other"
    
    class IdeaStatus(Enum):
        DRAFT = "draft"
        VALIDATED = "validated"
        APPROVED = "approved"
    
    @dataclass
    class Idea:
        title: str
        concept: str
        idea: str = ""
        premise: str = ""
        logline: str = ""
        hook: str = ""
        skeleton: str = ""
        beat_sheet: str = ""
        pov: str = ""
        emotional_arc: str = ""
        reveal: str = ""
        twist: str = ""
        climax: str = ""
        ending: str = ""
        ending_type: str = ""
        purpose: str = ""
        emotional_quality: str = ""
        target_audience: str = ""
        target_demographics: Dict = field(default_factory=dict)
        target_platforms: list = field(default_factory=list)
        target_formats: list = field(default_factory=list)
        genre: ContentGenre = ContentGenre.OTHER
        style: str = ""
        keywords: list = field(default_factory=list)
        themes: list = field(default_factory=list)
        character_notes: str = ""
        setting_notes: str = ""
        tone_guidance: str = ""
        length_target: str = ""
        potential_scores: Dict = field(default_factory=dict)
        inspiration_ids: list = field(default_factory=list)
        metadata: Dict = field(default_factory=dict)
        status: IdeaStatus = IdeaStatus.DRAFT
        notes: str = ""
        created_by: Optional[str] = None


# Raw subtitle text from the YouTube video
SUBTITLE_TEXT = """When did you realize your neurode divergent child was actually a badass in disguise? My daughter Mera was 11 years old, autistic, and completely obsessed with her bow staff. You know those long wooden poles from martial arts movies? Her grandpa handcarved her one right before he passed away, and she never put it down after that. She spent 5 hours a day every day in the backyard practicing the same movements until her palms blistered over. Teachers kept telling me to redirect her into something more normal, but I never listened to them. The staff made her happy. That's all any parent cares about. When Mera started fifth grade, she met her only real friend, a boy named Theo. He had ADHD and she had autism, and they just fit together like a puzzle. They ate lunch together every day. Did homework at our kitchen table. He even thought her staff was cool. I was so happy she made a friend. Then a 13-year-old girl named Vanessa came into the picture. She'd never spoken to Theo before, but she started following him between classes. She wanted him to be her boyfriend. Apparently, Theo being different intrigued her. Theo kept telling her no, but Vanessa kept pushing. The day after Theo publicly told her no and turned her into a meme in her class, she had enough. She cornered Theo alone behind the gymnasium. She shoved him into the brick wall over and over until his head split open. He fell down and laid on the concrete with a black eye, raw palms, and a gash across his forehead held together with four stitches. Vanessa had pressed scissors to his throat before leaving. Be my boyfriend and I'll cut your face off next time. He was too scared to tell any adult, but he told Meera everything. immediately. She took him back to our house and immediately where she bandaged his wounds up before saying, "Vanessa's never going to touch you again." Theo looked at Merror. "What do you mean?" Merror smirked. "I have Grandpa's staff. I've been training for 3 years. She doesn't know what's coming." Theo shook his head. "She's bigger than you. She's older. She's crazy." Merror didn't blink. But you're my best friend. I'd fight a bear for you. She's not scarier than a big fat bear. After that conversation, something in Mirror changed. 5 hours of daily training became sick. She started watching combat videos online every night. Her accuracy got terrifying. She could knock a nickel off a fence post from 10 feet away. Meanwhile, Theo's parents were trying to handle things the right way. They brought photos of his injuries to the principal's office, filed official complaints, documented everything. But Vanessa's family had donated a lot of money over the years. That money bought her protection. So the school only gave Vanessa a 2-day suspension. That suspension only made things worse. Vanessa got angrier, more unhinged. Notes started showing up in Theo's locker from the first day she was back. Then he started receiving photos of his house, pictures of his mom's car, even threats disguised as love letters. One of them mentioned Mera by name. Called her an obstacle that needed to be removed. That Friday, 5 days after Vanessa came back, Theo was over at our house after school. My wife needed to help our friends carry some furniture. I went with him. We told the kids we'd be back in 20 minutes. Left them on the couch eating chips and watching the staff videos. Theo had been getting into it, too. We got in our car and drove off, and the back door window shattered the second we were out of sight. Vanessa was climbing through the broken glass with a kitchen knife in her hand. But she wasn't there to rob us. She was there to hurt Theo and Merror. Merror heard the glass break and grabbed Theo by the arm. Bedroom, lock the door. Call 911. Go now. Theo ran down the hallway. Mera stayed calm. She grabbed her grandfather's staff from where it always stood in the corner. Planted herself between the hallway and everything behind her. Vanessa came around the wall with a knife raised. Where is he? Mera didn't answer. I said, "Where is he?" Vanessa lunged forward, swinging the blade. That's when three years of muscle memory took over. Mera swung her staff, and it connected with Vanessa's wrist. The knife went flying, but Vanessa wasn't done. She screamed and rushed at Merror with bare hands, but Meera was already moving. The staff connected with Vanessa's legs, ribs, shoulder, even straight over her empty head. controlled strikes exactly like she practiced thousands of times. Vanessa hit the floor hard, blood running from her nose. Couldn't get back up. The bedroom door clicked open. Theo stepped out and saw Meera standing over the girl who'd been terrorizing him for weeks. The stitches were still fresh on his forehead. You actually did it. Mera's hands were starting to shake. She looked down and saw Vanessa's fingers reaching toward the knife on the floor. The front door flew open right then. My wife came through first with me right behind him. Vanessa's parents were there, too. They'd been driving around looking for their daughter. I grabbed the knife before anyone could touch it. My wife was already calling 911. Police showed up fast and documented everything. The broken door, the weapon, the blood, the staff still in Mera's hands. They interviewed both kids separately with specialists in the room. Mera walked them through everything calmly, where she stood, what she aimed for, why she chose each strike. Then her voice got quiet. Am I in trouble for hurting her? The detective looked at her for a long moment. No, sweetheart, you're not in any trouble. Self-defense in defense of another cleared completely."""


# IdeaInspiration data extracted from the video
IDEA_INSPIRATION_DATA: Dict[str, Any] = {
    'title': "When that acting challenge suddenly feels a little too real",
    'description': (
        "A parent shares the story of their 11-year-old autistic daughter Mera, "
        "who used 3 years of dedicated bo staff training to defend her best friend "
        "Theo (who has ADHD) from a violent bully who broke into their home with a knife."
    ),
    'content': SUBTITLE_TEXT,
    'keywords': [
        'autism', 'ADHD', 'neurodivergent', 'self-defense', 'friendship',
        'bo staff', 'martial arts', 'bullying', 'empowerment', 'dedication',
        'training', 'protection', 'legacy', 'grandparent', 'child hero'
    ],
    'source_type': 'video',
    'metadata': {
        'views': '2217',
        'likes': '97',
        'posted_ago': '8 hours',
        'platform': 'youtube',
        'subtitles_available': 'true',
        'content_type': 'story_narration',
        'language': 'en',
        'duration_estimate': '3-4 minutes',
        'engagement_rate': '4.38%',  # likes/views * 100
    },
    'source_id': None,  # Video ID not provided in original problem
    'source_url': None,  # URL not provided in original problem
    'source_created_by': None,  # Channel name not provided
    'source_created_at': None,  # Exact date not provided
    'score': 85,  # High score based on engagement and content quality
    'category': 'inspirational_story',
    'subcategory_relevance': {
        'family_content': 90,
        'neurodivergent_community': 95,
        'self_defense': 85,
        'anti_bullying': 92,
        'empowerment': 88,
    },
    'contextual_category_scores': {
        'region:us': 90,
        'region:uk': 85,
        'age:15-24': 88,
        'age:25-34': 92,
        'age:35-44': 90,  # Parent demographic
        'platform:youtube': 90,
        'platform:tiktok': 85,
        'platform:instagram': 80,
    },
}


def create_idea_from_video() -> Idea:
    """Create a structured Idea from this video analysis.
    
    This demonstrates how the IdeaInspiration would be transformed
    into the Idea model for content production in PrismQ.
    
    Returns:
        Idea instance ready for content production
    """
    return Idea(
        title="The Guardian: An Autistic Girl's Training Pays Off",
        concept=(
            "An 11-year-old autistic girl uses 3 years of dedicated martial arts training "
            "with her late grandfather's hand-carved bo staff to defend her neurodivergent "
            "best friend from a violent home invader."
        ),
        
        # Story Foundation
        idea="Autistic girl defends friend with grandfather's legacy",
        premise=(
            "Mera, an 11-year-old autistic girl, has spent 3 years obsessively training "
            "with a bo staff her grandfather carved before passing. When a bully breaks "
            "into her home to harm her best friend Theo, her dedicated practice transforms "
            "from an 'obsession' into the skill that saves them both."
        ),
        logline=(
            "An autistic girl's 'obsession' becomes her superpower when she must defend "
            "her only friend from the bully who broke into their home with a knife."
        ),
        hook="Teachers kept telling me to redirect her into something more normal. Thank God I never listened.",
        
        # Story Structure
        skeleton=(
            "1. Meet Mera: autistic girl with grandfather's staff, trains 5 hrs daily\n"
            "2. Friendship: Mera meets Theo (ADHD), they connect as neurodivergent peers\n"
            "3. Threat: Vanessa bullies Theo, school fails to protect him\n"
            "4. Preparation: Mera intensifies training after learning about Theo's injuries\n"
            "5. Confrontation: Vanessa breaks in with knife, Mera faces her alone\n"
            "6. Resolution: Mera defends Theo, cleared as self-defense"
        ),
        beat_sheet=(
            "- Hook: Parent question about neurodivergent 'badass' child\n"
            "- Setup: Mera's obsession with staff, grandfather's legacy\n"
            "- Catalyst: Mera meets Theo, forms first real friendship\n"
            "- Rising Action: Vanessa's escalating violence and threats\n"
            "- Midpoint: Mera vows to protect Theo, trains harder\n"
            "- Dark Night: Vanessa breaks in while parents away\n"
            "- Climax: 3 years of training vs knife-wielding bully\n"
            "- Resolution: Detective confirms self-defense, Mera is clear"
        ),
        
        # Narrative Elements
        pov="first person - parent narrator (creates warmth and authenticity)",
        emotional_arc="concern → hope → fear → pride → relief → vindication",
        reveal="The 'obsession' teachers wanted to redirect was actually preparation for this moment",
        twist="The most vulnerable seeming child becomes the protector",
        climax="Mera faces Vanessa alone, staff vs knife",
        ending="Detective tells Mera she's not in trouble - complete vindication",
        ending_type="emotional/triumphant",
        
        # Content Properties
        purpose="Inspire neurodivergent families and challenge assumptions about 'obsessive' interests",
        emotional_quality="inspiring, protective, triumphant, validating",
        target_audience="Parents of neurodivergent children, neurodivergent community, self-defense advocates",
        target_demographics={
            'age_range': '15-45',
            'interests': 'parenting,neurodivergent,self_defense,martial_arts',
            'regions': 'US,UK,CA,AU'
        },
        target_platforms=['youtube', 'tiktok', 'instagram', 'podcast'],
        target_formats=['video', 'audio', 'text'],
        genre=ContentGenre.ENTERTAINMENT,  # Could also be DOCUMENTARY
        style="narrative storytelling with emotional hooks",
        keywords=[
            'autism empowerment', 'ADHD friendship', 'self-defense',
            'bo staff', 'martial arts', 'bullying prevention',
            'neurodivergent strength', 'grandparent legacy', 'child hero'
        ],
        themes=[
            'neurodivergent empowerment',
            'friendship loyalty',
            'dedicated practice',
            'legacy and memory',
            'standing up for others',
            'challenging assumptions',
            'when obsession becomes skill'
        ],
        character_notes=(
            "Mera (11, autistic): Dedicated, focused, loyal, calm under pressure. "
            "Her 'obsession' is actually deep focus and practice.\n"
            "Theo (ADHD): Kind friend, accepted Mera, vulnerable but brave.\n"
            "Vanessa (13): Unstable bully, escalating violence, wealthy family protected her.\n"
            "Grandfather (deceased): Carved the staff as legacy, believed in Mera.\n"
            "Parent narrator: Supportive, trusted Mera's interests, proud."
        ),
        setting_notes=(
            "Suburban home with backyard for training.\n"
            "School where institutional failure occurs.\n"
            "Living room confrontation - staff against knife."
        ),
        tone_guidance=(
            "Start warm and slightly humorous (obsession with staff). "
            "Build concern as threat emerges. "
            "Tension during confrontation. "
            "Relief and pride at resolution. "
            "End on emotional note: vindication of both Mera and parent's choices."
        ),
        length_target="3-4 minute video / 2,500 words text / 5-minute podcast segment",
        
        # Metadata
        potential_scores={
            'platform:youtube': 90,
            'platform:tiktok': 85,
            'region:us': 90,
            'age:25-34': 92,
            'demographic:parent': 95,
        },
        inspiration_ids=[],  # Would link to stored IdeaInspiration ID
        metadata={
            'original_source': 'youtube_video',
            'content_type': 'story_narration',
            'viral_potential': 'high',
            'controversy_risk': 'low',
            'educational_value': 'medium',
            'emotional_impact': 'high',
        },
        status=IdeaStatus.DRAFT,
        notes=(
            "Extracted from YouTube video with high engagement rate (4.38%). "
            "Strong neurodivergent empowerment angle with broad appeal. "
            "Could be developed as standalone content or part of a series "
            "on neurodivergent success stories."
        ),
        created_by="PrismQ.T.Idea.Inspiration.VideoAnalysis",
    )


def main():
    """Demonstrate the video analysis and Idea creation."""
    print("=" * 70)
    print("YouTube Video Analysis: Mera's Bo Staff Defense")
    print("=" * 70)
    
    print("\n📹 ORIGINAL VIDEO METADATA:")
    print("-" * 40)
    print(f"Title: {IDEA_INSPIRATION_DATA['title']}")
    print(f"Views: {IDEA_INSPIRATION_DATA['metadata']['views']}")
    print(f"Likes: {IDEA_INSPIRATION_DATA['metadata']['likes']}")
    print(f"Engagement: {IDEA_INSPIRATION_DATA['metadata']['engagement_rate']}")
    print(f"Score: {IDEA_INSPIRATION_DATA['score']}/100")
    
    print("\n🏷️ KEYWORDS:")
    print("-" * 40)
    for kw in IDEA_INSPIRATION_DATA['keywords'][:10]:
        print(f"  • {kw}")
    
    print("\n📊 SUBCATEGORY RELEVANCE:")
    print("-" * 40)
    for cat, score in IDEA_INSPIRATION_DATA['subcategory_relevance'].items():
        bar = "█" * (score // 10) + "░" * (10 - score // 10)
        print(f"  {cat}: {bar} {score}%")
    
    print("\n💡 CREATED IDEA:")
    print("-" * 40)
    idea = create_idea_from_video()
    print(f"Title: {idea.title}")
    print(f"Concept: {idea.concept[:100]}...")
    print(f"Genre: {idea.genre.value}")
    print(f"Platforms: {', '.join(idea.target_platforms)}")
    print(f"Status: {idea.status.value}")
    
    print("\n📝 STORY ELEMENTS:")
    print("-" * 40)
    print(f"Hook: {idea.hook}")
    print(f"Logline: {idea.logline}")
    print(f"Emotional Arc: {idea.emotional_arc}")
    
    print("\n" + "=" * 70)
    print("Analysis complete! Ready for content production pipeline.")
    print("=" * 70)


if __name__ == "__main__":
    main()
