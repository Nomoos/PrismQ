"""Command-line interface for PrismQ.IdeaInspiration.Sources.Creative.ScriptBeatsSource."""

import click
import sys
import json
from pathlib import Path
from .core.config import Config
from .core.database import Database
from .core.metrics import CreativeMetrics
from .plugins.template_plugin import TemplatePlugin
from .plugins.manual_import_plugin import ManualImportPlugin


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
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize template plugin
        template_plugin = TemplatePlugin(config)
        
        click.echo("Loading built-in story structure templates...")
        click.echo()
        
        resources = template_plugin.scrape()
        total_saved = 0
        
        for resource in resources:
            # Convert to creative metrics
            creative_metrics = CreativeMetrics.from_manual(resource['metrics'])
            
            # Save to database
            success = db.insert_resource(
                source='template',
                source_id=resource['source_id'],
                title=resource['title'],
                content=resource['content'],
                tags=resource['tags'],
                score=creative_metrics.inspiration_value or 0.0,
                score_dictionary=creative_metrics.to_dict()
            )
            
            if success:
                total_saved += 1
                click.echo(f"✓ Loaded: {resource['title']}")
            else:
                click.echo(f"⟳ Updated: {resource['title']}")
        
        click.echo(f"\nTemplate loading complete!")
        click.echo(f"Total templates loaded: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
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
        
        resource = template_plugin.get_template(template_id)
        
        if not resource:
            click.echo(f"Template '{template_id}' not found.", err=True)
            click.echo("\nAvailable templates:", err=True)
            for t in template_plugin.list_templates():
                click.echo(f"  - {t['id']}", err=True)
            sys.exit(1)
        
        click.echo(f"\n{'='*80}")
        click.echo(resource['content'])
        click.echo(f"{'='*80}\n")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--file', '-f', required=True, type=click.Path(exists=True),
              help='Path to JSON or CSV file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def import_file(env_file, file, no_interactive):
    """Import narrative structures from JSON or CSV file.
    
    Examples:
        python -m src.cli import-file --file story_beats.json
        python -m src.cli import-file --file narratives.csv
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize manual import plugin
        manual_plugin = ManualImportPlugin(config)
        
        file_path = Path(file)
        click.echo(f"Importing from: {file_path}")
        click.echo()
        
        # Import based on file extension
        if file_path.suffix.lower() == '.json':
            resources = manual_plugin.import_from_json(str(file_path))
        elif file_path.suffix.lower() == '.csv':
            resources = manual_plugin.import_from_csv(str(file_path))
        else:
            click.echo(f"Unsupported file format: {file_path.suffix}", err=True)
            click.echo("Supported formats: .json, .csv", err=True)
            sys.exit(1)
        
        if not resources:
            click.echo("No resources found in file.")
            return
        
        total_saved = 0
        
        for resource in resources:
            # Convert to creative metrics
            creative_metrics = CreativeMetrics.from_manual(resource['metrics'])
            
            # Save to database
            success = db.insert_resource(
                source='manual',
                source_id=resource['source_id'],
                title=resource['title'],
                content=resource['content'],
                tags=resource['tags'],
                score=creative_metrics.inspiration_value or 0.0,
                score_dictionary=creative_metrics.to_dict()
            )
            
            if success:
                total_saved += 1
                click.echo(f"✓ Imported: {resource['title'][:60]}...")
        
        click.echo(f"\nImport complete!")
        click.echo(f"Total structures imported: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--limit', '-l', type=int, default=20, 
              help='Maximum number of structures to display')
@click.option('--source', '-s', help='Filter by source')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def list(env_file, limit, source, no_interactive):
    """List collected narrative structures."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Open database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get resources
        resources = db.get_all_resources(limit=limit)
        
        # Filter by source if specified
        if source:
            resources = [r for r in resources if r['source'] == source]
        
        if not resources:
            click.echo("No narrative structures found.")
            return
        
        # Display resources
        click.echo(f"\n{'='*80}")
        click.echo(f"Collected Narrative Structures ({len(resources)} total)")
        click.echo(f"{'='*80}\n")
        
        for i, resource in enumerate(resources, 1):
            click.echo(f"{i}. [{resource['source'].upper()}] {resource['title']}")
            click.echo(f"   ID: {resource['source_id']}")
            if resource['tags']:
                click.echo(f"   Tags: {resource['tags']}")
            if resource['content']:
                # Show first few lines
                lines = resource['content'].split('\n')[:3]
                preview = '\n   '.join(lines)
                click.echo(f"   Preview:\n   {preview}")
                if len(resource['content'].split('\n')) > 3:
                    click.echo("   ...")
            click.echo()
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def stats(env_file, no_interactive):
    """Show statistics about collected narrative structures."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Open database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get all resources
        resources = db.get_all_resources(limit=10000)  # Get all
        
        if not resources:
            click.echo("No narrative structures collected yet.")
            return
        
        # Calculate statistics
        total = len(resources)
        by_source = {}
        
        for resource in resources:
            source = resource['source']
            by_source[source] = by_source.get(source, 0) + 1
        
        # Display statistics
        click.echo(f"\n{'='*50}")
        click.echo(f"Narrative Structure Collection Statistics")
        click.echo(f"{'='*50}\n")
        click.echo(f"Total Structures: {total}\n")
        click.echo(f"Structures by Source:")
        for source, count in sorted(by_source.items()):
            percentage = (count / total) * 100
            click.echo(f"  {source.capitalize()}: {count} ({percentage:.1f}%)")
        click.echo()
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
@click.confirmation_option(prompt='Are you sure you want to clear all narrative structures?')
def clear(env_file, no_interactive):
    """Clear all narrative structures from the database."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Delete database file
        db_path = Path(config.database_path)
        if db_path.exists():
            db_path.unlink()
            click.echo(f"Database cleared: {config.database_path}")
        else:
            click.echo("Database does not exist.")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
