"""Template plugin for built-in story structure templates."""

from typing import List, Dict, Any
from . import SourcePlugin, IdeaInspiration


class TemplatePlugin(SourcePlugin):
    """Plugin providing built-in story structure templates."""

    # Built-in story structure templates
    TEMPLATES = {
        'save_the_cat': {
            'title': "Save the Cat! 15-Beat Structure",
            'beats': [
                "Opening Image - Visual that represents struggle & tone of story",
                "Theme Stated - What your story is about",
                "Set-Up - Expand on opening image, establish tone",
                "Catalyst - Life-changing event",
                "Debate - Doubt, caring about the goal, push away new world",
                "Break Into Two - Make a choice, leave comfort zone",
                "B Story - New characters, Mirror theme, love story often",
                "Fun and Games - Promise of the premise, trailer moments",
                "Midpoint - False victory or false defeat",
                "Bad Guys Close In - Internal and external pressure",
                "All Is Lost - Opposite of midpoint, lowest point",
                "Dark Night of the Soul - Wallow in hopelessness",
                "Break Into Three - Aha moment, realize what's needed",
                "Finale - Synthesize old and new world, prove change",
                "Final Image - Opposite of opening, show change"
            ],
            'structure_type': 'three-act',
            'genres': ['adventure', 'drama', 'comedy', 'action'],
            'themes': ['transformation', 'growth', 'redemption']
        },
        'heros_journey': {
            'title': "Hero's Journey (Campbell)",
            'beats': [
                "Ordinary World - Hero in normal life",
                "Call to Adventure - Inciting incident",
                "Refusal of the Call - Hero hesitates",
                "Meeting the Mentor - Guidance appears",
                "Crossing the Threshold - Enter special world",
                "Tests, Allies, Enemies - Learn rules of new world",
                "Approach to Inmost Cave - Preparation for ordeal",
                "Ordeal - Crisis, face greatest fear",
                "Reward - Seize the sword",
                "The Road Back - Return to ordinary world",
                "Resurrection - Final test, purification",
                "Return with Elixir - Bring boon to ordinary world"
            ],
            'structure_type': 'circular',
            'genres': ['fantasy', 'adventure', 'sci-fi', 'epic'],
            'themes': ['transformation', 'adventure', 'self-discovery']
        },
        'three_act': {
            'title': "Classic Three-Act Structure",
            'beats': [
                "Act 1: Setup - Introduce characters, world, conflict",
                "Inciting Incident - Event that starts the story",
                "Plot Point 1 - Major turn into Act 2",
                "Act 2: Confrontation - Rising action, complications",
                "Midpoint - Perspective shift, raise stakes",
                "Plot Point 2 - Crisis, all seems lost",
                "Act 3: Resolution - Climax and resolution",
                "Climax - Highest tension, final confrontation",
                "Resolution - Tie up loose ends, new normal"
            ],
            'structure_type': 'three-act',
            'genres': ['drama', 'thriller', 'romance', 'mystery'],
            'themes': ['conflict', 'resolution', 'change']
        },
        'five_act': {
            'title': "Five-Act Structure (Freytag's Pyramid)",
            'beats': [
                "Act 1: Exposition - Introduction, normal world",
                "Act 2: Rising Action - Conflicts and complications develop",
                "Act 3: Climax - Turning point, highest tension",
                "Act 4: Falling Action - Unraveling of plot",
                "Act 5: Denouement - Resolution, new equilibrium"
            ],
            'structure_type': 'five-act',
            'genres': ['tragedy', 'drama', 'classical'],
            'themes': ['rise and fall', 'fate', 'consequence']
        },
        'kishotenketsu': {
            'title': "Kishōtenketsu (4-Act East Asian Structure)",
            'beats': [
                "Ki (Introduction) - Establish characters and setting",
                "Shō (Development) - Develop introduced elements",
                "Ten (Twist) - Introduce new element, perspective shift",
                "Ketsu (Conclusion) - Reconcile previous elements"
            ],
            'structure_type': 'four-act',
            'genres': ['literary', 'slice-of-life', 'contemplative'],
            'themes': ['harmony', 'perspective', 'synthesis']
        },
        'seven_point': {
            'title': "Seven-Point Story Structure",
            'beats': [
                "Hook - Grab attention, show starting state",
                "Plot Turn 1 - Call to adventure",
                "Pinch Point 1 - Introduce antagonistic force",
                "Midpoint - Move from reaction to action",
                "Pinch Point 2 - Force is greater than thought",
                "Plot Turn 2 - Obtain final piece needed",
                "Resolution - Solve problem, new equilibrium"
            ],
            'structure_type': 'seven-point',
            'genres': ['action', 'thriller', 'mystery'],
            'themes': ['conflict', 'escalation', 'resolution']
        }
    }

    def __init__(self, config):
        """Initialize template plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)

    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "template"

    def scrape(self) -> List[IdeaInspiration]:
        """Get all built-in templates.
        
        Returns:
            List of IdeaInspiration objects
        """
        ideas = []
        
        for template_id, template_data in self.TEMPLATES.items():
            idea = self._template_to_idea_inspiration(template_id, template_data)
            ideas.append(idea)
        
        return ideas

    def get_template(self, template_id: str) -> IdeaInspiration:
        """Get a specific template by ID.
        
        Args:
            template_id: Template identifier (e.g., 'save_the_cat', 'heros_journey')
            
        Returns:
            IdeaInspiration object or None
        """
        if template_id not in self.TEMPLATES:
            return None
        
        template_data = self.TEMPLATES[template_id]
        return self._template_to_idea_inspiration(template_id, template_data)

    def list_templates(self) -> List[Dict[str, str]]:
        """List all available templates.
        
        Returns:
            List of template summaries
        """
        templates = []
        
        for template_id, template_data in self.TEMPLATES.items():
            templates.append({
                'id': template_id,
                'title': template_data['title'],
                'structure_type': template_data['structure_type'],
                'beat_count': len(template_data['beats'])
            })
        
        return templates

    def _template_to_idea_inspiration(self, template_id: str, template_data: Dict[str, Any]) -> IdeaInspiration:
        """Convert template data to IdeaInspiration.
        
        Args:
            template_id: Template identifier
            template_data: Template data dictionary
            
        Returns:
            IdeaInspiration object
        """
        # Build content from beats
        content_lines = [template_data['title'], "", "Story Beats:", ""]
        for i, beat in enumerate(template_data['beats'], 1):
            content_lines.append(f"{i}. {beat}")
        
        content = '\n'.join(content_lines)
        
        # Build tags
        tags = ['narrative', 'structure', 'template', template_data['structure_type']]
        tags.extend(template_data['genres'])
        tags.extend(template_data['themes'])
        
        # Build metadata with string values for SQLite compatibility
        metadata = {
            'template_id': template_id,
            'beat_count': str(len(template_data['beats'])),
            'structure_type': template_data['structure_type'],
            'genres': ','.join(template_data['genres']),
            'themes': ','.join(template_data['themes']),
            'type': 'narrative',
            'format': 'text',
            'emotional_impact': '7.0',
            'versatility': '9.5',
            'inspiration_value': '9.0'
        }
        
        # Create IdeaInspiration using from_text factory method
        idea = IdeaInspiration.from_text(
            title=template_data['title'],
            description=f"{template_data['structure_type']} story structure with {len(template_data['beats'])} beats",
            text_content=content,
            keywords=tags,
            metadata=metadata,
            source_id=f"template_{template_id}",
            source_url=None,
            source_platform="script_beats",
            source_created_by="script_beats_templates",
            source_created_at=None
        )
        
        return idea
