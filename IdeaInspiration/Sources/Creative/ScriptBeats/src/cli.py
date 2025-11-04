"""Command-line interface for PrismQ.IdeaInspiration.Sources.Creative.ScriptBeatsSource."""

import click
import sys
from pathlib import Path
from .core.config import Config
from .plugins.template_plugin import TemplatePlugin

# Import central IdeaInspiration database from Model module
model_path = Path(__file__).resolve().parents[5] / 'Model'
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from idea_inspiration_db import IdeaInspirationDatabase, get_central_database_path


@click.group()
@click.version_option(version='1.0.0')
def main():
    """PrismQ Script Beats Source - Gather creative inspiration from narrative structures."""
    pass


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def load_templates(env_file, no_interactive):
    """Load all built-in story structure templates into database.
    
    Examples:
        python -m src.cli load-templates
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize central database only (single DB approach)
        central_db_path = get_central_database_path()
        central_db = IdeaInspirationDatabase(central_db_path, interactive=not no_interactive)
        
        # Initialize template plugin
        template_plugin = TemplatePlugin(config)
        
        click.echo("Loading built-in story structure templates...")
        click.echo()
        
        # Plugin returns List[IdeaInspiration]
        ideas = template_plugin.scrape()
        total_saved = 0
        
        # Save each IdeaInspiration to central database (single DB)
        for idea in ideas:
            central_saved = central_db.insert(idea)
            if central_saved:
                total_saved += 1
                click.echo(f"✓ Loaded: {idea.title}")
            else:
                click.echo(f"⟳ Updated: {idea.title}")
        
        click.echo(f"\nTemplate loading complete!")
        click.echo(f"Total templates loaded: {total_saved}")
        click.echo(f"Central database: {central_db_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def list_templates(env_file, no_interactive):
    """List all available built-in story structure templates.
    
    Examples:
        python -m src.cli list-templates
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize template plugin
        template_plugin = TemplatePlugin(config)
        
        templates = template_plugin.list_templates()
        
        click.echo(f"\n{'='*80}")
        click.echo(f"Built-in Story Structure Templates ({len(templates)} total)")
        click.echo(f"{'='*80}\n")
        
        for template in templates:
            click.echo(f"ID: {template['id']}")
            click.echo(f"Title: {template['title']}")
            click.echo(f"Type: {template['structure_type']}")
            click.echo(f"Beats: {template['beat_count']}")
            click.echo()
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--template-id', '-t', required=True,
              help='Template ID (e.g., save_the_cat, heros_journey)')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def show_template(env_file, template_id, no_interactive):
    """Show details of a specific story structure template.
    
    Examples:
        python -m src.cli show-template --template-id save_the_cat
        python -m src.cli show-template -t heros_journey
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize template plugin
        template_plugin = TemplatePlugin(config)
        
        idea = template_plugin.get_template(template_id)
        
        if not idea:
            click.echo(f"Template '{template_id}' not found.", err=True)
            click.echo("\nAvailable templates:", err=True)
            for t in template_plugin.list_templates():
                click.echo(f"  - {t['id']}", err=True)
            sys.exit(1)
        
        click.echo(f"\n{'='*80}")
        click.echo(idea.content)
        click.echo(f"{'='*80}\n")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--limit', '-l', type=int, default=20, 
              help='Maximum number of structures to display')
@click.option('--source-platform', '-s', help='Filter by source platform')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def list(env_file, limit, source_platform, no_interactive):
    """List collected narrative structures from central database."""
    try:
        # Initialize central database
        central_db_path = get_central_database_path()
        central_db = IdeaInspirationDatabase(central_db_path, interactive=not no_interactive)
        
        # Query all ideas, filter by source_platform if specified
        all_ideas = central_db.query_all(limit=limit * 10)  # Get more to filter
        
        # Filter by source platform
        if source_platform:
            ideas = [idea for idea in all_ideas if idea.source_platform == source_platform][:limit]
        else:
            # Filter to only script_beats platform
            ideas = [idea for idea in all_ideas if idea.source_platform == 'script_beats'][:limit]
        
        if not ideas:
            click.echo("No narrative structures found.")
            return
        
        # Display ideas
        click.echo(f"\n{'='*80}")
        click.echo(f"Collected Narrative Structures ({len(ideas)} total)")
        click.echo(f"{'='*80}\n")
        
        for i, idea in enumerate(ideas, 1):
            click.echo(f"{i}. [{idea.source_platform.upper()}] {idea.title}")
            click.echo(f"   ID: {idea.source_id}")
            if idea.keywords:
                click.echo(f"   Tags: {', '.join(idea.keywords)}")
            if idea.content:
                # Show first few lines
                lines = idea.content.split('\n')[:3]
                preview = '\n   '.join(lines)
                click.echo(f"   Preview:\n   {preview}")
                if len(idea.content.split('\n')) > 3:
                    click.echo("   ...")
            click.echo()
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def stats(env_file, no_interactive):
    """Show statistics about collected narrative structures from central database."""
    try:
        # Initialize central database
        central_db_path = get_central_database_path()
        central_db = IdeaInspirationDatabase(central_db_path, interactive=not no_interactive)
        
        # Get all ideas from script_beats platform
        all_ideas = central_db.query_all(limit=10000)
        ideas = [idea for idea in all_ideas if idea.source_platform == 'script_beats']
        
        if not ideas:
            click.echo("No narrative structures collected yet.")
            return
        
        # Calculate statistics
        total = len(ideas)
        by_template = {}
        
        for idea in ideas:
            template_id = idea.metadata.get('template_id', 'unknown')
            by_template[template_id] = by_template.get(template_id, 0) + 1
        
        # Display statistics
        click.echo(f"\n{'='*50}")
        click.echo(f"Narrative Structure Collection Statistics")
        click.echo(f"{'='*50}\n")
        click.echo(f"Total Structures: {total}\n")
        click.echo(f"Structures by Template:")
        for template_id, count in sorted(by_template.items()):
            percentage = (count / total) * 100
            click.echo(f"  {template_id}: {count} ({percentage:.1f}%)")
        click.echo()
        click.echo(f"Central database: {central_db_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
