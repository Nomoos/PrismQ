"""Command-line interface for PrismQ.IdeaInspiration.Sources.Internal.ManualBacklog."""

import click
import sys
import json
from .core.config import Config
from .core.database import Database
from .plugins.manual_entry_plugin import ManualEntryPlugin


@click.group()
@click.version_option(version='1.0.0')
def main():
    """PrismQ Manual Backlog Source - Manage manual idea backlog."""
    pass


@main.command()
@click.argument('title')
@click.option('--description', '-d', type=str, default='',
              help='Idea description')
@click.option('--notes', '-n', type=str, default='',
              help='Additional notes')
@click.option('--category', '-c', type=str,
              help='Category classification')
@click.option('--priority', '-p', type=click.Choice(['high', 'medium', 'low', 'critical', 'urgent']),
              help='Priority level')
@click.option('--status', '-s', type=click.Choice(['new', 'in_progress', 'used', 'archived']),
              help='Status')
@click.option('--tags', '-t', type=str,
              help='Comma-separated tags')
@click.option('--created-by', type=str,
              help='Creator name')
@click.option('--assigned-to', type=str,
              help='Assignee name')
@click.option('--env-file', '-e', type=click.Path(),
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True,
              help='Disable interactive prompts')
def add(title, description, notes, category, priority, status, tags, 
        created_by, assigned_to, env_file, no_interactive):
    """Add a new idea to the backlog.
    
    TITLE: Idea title (required)
    
    Example:
        manual-backlog add "Video idea title" -d "Description" -p high -t "tag1,tag2"
        manual-backlog add "Quick idea" --category content --assigned-to John
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize plugin
        plugin = ManualEntryPlugin(config)
        
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(',')] if tags else []
        
        # Create idea
        click.echo(f"\nCreating idea: {title}")
        idea = plugin.add_idea(
            title=title,
            description=description,
            notes=notes,
            category=category,
            priority=priority,
            status=status,
            tags=tag_list,
            created_by=created_by,
            assigned_to=assigned_to
        )
        
        # Save to database
        saved_count = db.save_ideas([idea])
        
        if saved_count > 0:
            click.echo(f"\n✓ Successfully added idea!")
            click.echo(f"  ID: {idea['source_id']}")
            click.echo(f"  Title: {idea['idea']['title']}")
            click.echo(f"  Category: {idea['idea']['category']}")
            click.echo(f"  Priority: {idea['idea']['priority']}")
            click.echo(f"  Status: {idea['metadata']['status']}")
        else:
            click.echo("Failed to save idea to database.", err=True)
            sys.exit(1)
        
    except ValueError as e:
        click.echo(f"Validation error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('source_id')
@click.option('--title', type=str,
              help='Update title')
@click.option('--description', '-d', type=str,
              help='Update description')
@click.option('--notes', '-n', type=str,
              help='Update notes')
@click.option('--category', '-c', type=str,
              help='Update category')
@click.option('--priority', '-p', type=click.Choice(['high', 'medium', 'low', 'critical', 'urgent']),
              help='Update priority')
@click.option('--status', '-s', type=click.Choice(['new', 'in_progress', 'used', 'archived']),
              help='Update status')
@click.option('--tags', '-t', type=str,
              help='Update tags (comma-separated)')
@click.option('--assigned-to', type=str,
              help='Update assignee')
@click.option('--env-file', '-e', type=click.Path(),
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True,
              help='Disable interactive prompts')
def update(source_id, title, description, notes, category, priority, status,
           tags, assigned_to, env_file, no_interactive):
    """Update an existing idea.
    
    SOURCE_ID: ID of the idea to update
    
    Example:
        manual-backlog update manual_abc123 --status in_progress
        manual-backlog update manual_abc123 --priority high --assigned-to Jane
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize plugin
        plugin = ManualEntryPlugin(config)
        
        # Get existing idea
        ideas = db.get_ideas()
        existing_idea = None
        for idea in ideas:
            if idea['source_id'] == source_id:
                existing_idea = idea
                break
        
        if not existing_idea:
            click.echo(f"Error: Idea with ID '{source_id}' not found.", err=True)
            sys.exit(1)
        
        # Build updates dictionary
        updates = {}
        if title:
            updates['title'] = title
        if description is not None:
            updates['description'] = description
        if notes is not None:
            updates['notes'] = notes
        if category:
            updates['category'] = category
        if priority:
            updates['priority'] = priority
        if status:
            updates['status'] = status
        if tags is not None:
            updates['tags'] = tags
        if assigned_to is not None:
            updates['assigned_to'] = assigned_to
        
        if not updates:
            click.echo("Error: No update fields provided.", err=True)
            sys.exit(1)
        
        # Update idea
        click.echo(f"\nUpdating idea: {existing_idea['idea']['title']}")
        updated_idea = plugin.update_idea(existing_idea, **updates)
        
        # Save to database
        saved_count = db.save_ideas([updated_idea])
        
        if saved_count > 0:
            click.echo(f"\n✓ Successfully updated idea!")
            click.echo(f"  ID: {updated_idea['source_id']}")
            click.echo(f"  Title: {updated_idea['idea']['title']}")
            click.echo(f"  Status: {updated_idea['metadata']['status']}")
        else:
            click.echo("Failed to update idea in database.", err=True)
            sys.exit(1)
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('source_id')
@click.option('--env-file', '-e', type=click.Path(),
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True,
              help='Disable interactive prompts')
def mark_used(source_id, env_file, no_interactive):
    """Mark an idea as used.
    
    SOURCE_ID: ID of the idea to mark as used
    
    Example:
        manual-backlog mark-used manual_abc123
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize plugin
        plugin = ManualEntryPlugin(config)
        
        # Get existing idea
        ideas = db.get_ideas()
        existing_idea = None
        for idea in ideas:
            if idea['source_id'] == source_id:
                existing_idea = idea
                break
        
        if not existing_idea:
            click.echo(f"Error: Idea with ID '{source_id}' not found.", err=True)
            sys.exit(1)
        
        # Mark as used
        click.echo(f"\nMarking idea as used: {existing_idea['idea']['title']}")
        updated_idea = plugin.mark_as_used(existing_idea)
        
        # Save to database
        saved_count = db.save_ideas([updated_idea])
        
        if saved_count > 0:
            click.echo(f"\n✓ Successfully marked idea as used!")
        else:
            click.echo("Failed to update idea in database.", err=True)
            sys.exit(1)
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(),
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True,
              help='Disable interactive prompts')
@click.option('--status', '-s', type=str,
              help='Filter by status')
@click.option('--category', '-c', type=str,
              help='Filter by category')
@click.option('--limit', '-l', type=int,
              help='Limit number of results')
@click.option('--format', '-f', type=click.Choice(['table', 'json']), default='table',
              help='Output format (default: table)')
def list_ideas(env_file, no_interactive, status, category, limit, format):
    """List ideas from the backlog.
    
    Example:
        manual-backlog list --status new
        manual-backlog list --category content --limit 10
        manual-backlog list --format json
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get ideas
        ideas = db.get_ideas(status=status, category=category, limit=limit)
        
        if not ideas:
            click.echo("No ideas found.")
            return
        
        if format == 'json':
            click.echo(json.dumps(ideas, indent=2))
        else:
            # Table format
            click.echo(f"\nFound {len(ideas)} idea(s):\n")
            click.echo(f"{'ID':<20} {'Title':<40} {'Status':<12} {'Category':<15} {'Priority':<10}")
            click.echo("="*100)
            
            for idea in ideas:
                source_id = idea['source_id'][:18]
                title = idea['idea']['title'][:38]
                status_val = idea['metadata']['status'][:10]
                category_val = idea['idea']['category'][:13]
                priority_val = idea['idea']['priority'][:8]
                
                click.echo(f"{source_id:<20} {title:<40} {status_val:<12} {category_val:<15} {priority_val:<10}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(),
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True,
              help='Disable interactive prompts')
def stats(env_file, no_interactive):
    """Show backlog statistics.
    
    Example:
        manual-backlog stats
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get statistics
        stats = db.get_stats()
        
        click.echo("\nBacklog Statistics:")
        click.echo(f"{'='*60}")
        click.echo(f"Total ideas: {stats['total']}")
        
        if stats['by_status']:
            click.echo(f"\nBy Status:")
            for status, count in stats['by_status'].items():
                click.echo(f"  {status}: {count}")
        
        if stats['by_category']:
            click.echo(f"\nBy Category:")
            for category, count in stats['by_category'].items():
                click.echo(f"  {category}: {count}")
        
        if stats['by_priority']:
            click.echo(f"\nBy Priority:")
            for priority, count in stats['by_priority'].items():
                click.echo(f"  {priority}: {count}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('source_id')
@click.option('--env-file', '-e', type=click.Path(),
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True,
              help='Disable interactive prompts')
def show(source_id, env_file, no_interactive):
    """Show detailed information about an idea.
    
    SOURCE_ID: ID of the idea to show
    
    Example:
        manual-backlog show manual_abc123
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get idea
        ideas = db.get_ideas()
        existing_idea = None
        for idea in ideas:
            if idea['source_id'] == source_id:
                existing_idea = idea
                break
        
        if not existing_idea:
            click.echo(f"Error: Idea with ID '{source_id}' not found.", err=True)
            sys.exit(1)
        
        # Display idea details
        click.echo(f"\nIdea Details:")
        click.echo(f"{'='*60}")
        click.echo(f"ID: {existing_idea['source_id']}")
        click.echo(f"Title: {existing_idea['idea']['title']}")
        click.echo(f"Description: {existing_idea['idea']['description']}")
        click.echo(f"Notes: {existing_idea['idea']['notes']}")
        click.echo(f"Category: {existing_idea['idea']['category']}")
        click.echo(f"Priority: {existing_idea['idea']['priority']}")
        click.echo(f"Status: {existing_idea['metadata']['status']}")
        click.echo(f"Created by: {existing_idea['metadata']['created_by']}")
        click.echo(f"Assigned to: {existing_idea['metadata']['assigned_to']}")
        click.echo(f"Tags: {', '.join(existing_idea['metadata']['tags'])}")
        click.echo(f"Created at: {existing_idea['tracking']['created_at']}")
        click.echo(f"Modified at: {existing_idea['tracking']['modified_at']}")
        click.echo(f"Used at: {existing_idea['tracking']['used_at'] or 'N/A'}")
        click.echo(f"Age (days): {existing_idea['tracking']['age_days']}")
        click.echo(f"Priority score: {existing_idea['universal_metrics']['priority_score']}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
