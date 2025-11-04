"""Command-line interface for PrismQ.IdeaInspiration.Sources.Events.CalendarHolidays."""

import click
import sys
from pathlib import Path
from datetime import datetime
from .core.config import Config
from .plugins.calendar_holidays_plugin import CalendarHolidaysPlugin

# Import central IdeaInspiration database and model from Model module
model_path = Path(__file__).resolve().parents[5] / 'Model'
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from idea_inspiration import IdeaInspiration
from idea_inspiration_db import IdeaInspirationDatabase, get_central_database_path


@click.group()
@click.version_option(version='1.0.0')
def main():
    """PrismQ Calendar Holidays Source - Gather event inspirations from holidays and observances."""
    pass


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--country', '-c', help='Country code (e.g., US, GB, CA)')
@click.option('--year', '-y', type=int, help='Year to fetch holidays for')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape(env_file, country, year, no_interactive):
    """Scrape holidays from Python holidays library.
    
    Examples:
        python -m src.cli scrape --country US --year 2025
        python -m src.cli scrape --country GB --year 2025
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize central database only (single DB approach)
        central_db_path = get_central_database_path()
        central_db = IdeaInspirationDatabase(central_db_path, interactive=not no_interactive)
        
        # Initialize holidays plugin
        holidays_plugin = CalendarHolidaysPlugin(config)
        
        # Determine country and year
        country_code = country if country else config.default_country
        year_val = year if year else int(config.default_year)
        
        # Scrape holidays
        total_scraped = 0
        total_saved_central = 0
        
        click.echo(f"Scraping holidays for {country_code} in {year_val}...")
        
        try:
            # Scrape holidays - returns List[IdeaInspiration]
            ideas = holidays_plugin.scrape(country=country_code, year=year_val)
            total_scraped = len(ideas)
            click.echo(f"Found {len(ideas)} holidays")
            
            # Save each IdeaInspiration to central database (single DB)
            for idea in ideas:
                central_saved = central_db.insert(idea)
                if central_saved:
                    total_saved_central += 1
                    click.echo(f"  ✓ Saved: {idea.title[:60]}")
                else:
                    click.echo(f"  ↻ Updated: {idea.title[:60]}")
            
        except Exception as e:
            click.echo(f"Error scraping holidays: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total holidays found: {total_scraped}")
        click.echo(f"Saved to central database: {total_saved_central}")
        click.echo(f"Central database: {central_db_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--limit', '-l', type=int, default=20, 
              help='Maximum number of events to display')
@click.option('--country', '-c', help='Filter by country')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def list(env_file, limit, country, no_interactive):
    """List collected events."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Open central database
        central_db_path = get_central_database_path()
        central_db = IdeaInspirationDatabase(central_db_path, interactive=not no_interactive)
        
        # Get events - filter by source_platform
        ideas = central_db.get_all(
            limit=limit,
            source_platform="calendar_holidays"
        )
        
        # Filter by country if specified
        if country:
            ideas = [idea for idea in ideas if idea.metadata.get('country', '').upper() == country.upper()]
        
        if not ideas:
            click.echo("No events found.")
            return
        
        # Display events
        click.echo(f"\n{'='*80}")
        click.echo(f"Collected Events ({len(ideas)} total)")
        click.echo(f"{'='*80}\n")
        
        for i, idea in enumerate(ideas, 1):
            click.echo(f"{i}. [{idea.metadata.get('country', 'N/A')}] {idea.title}")
            click.echo(f"   Date: {idea.metadata.get('date', 'N/A')}")
            click.echo(f"   Scope: {idea.metadata.get('scope', 'N/A')} | Importance: {idea.metadata.get('importance', 'N/A')}")
            if idea.metadata.get('audience_size_estimate'):
                click.echo(f"   Audience: {idea.metadata.get('audience_size_estimate')}")
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
    """Show statistics about collected events."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Open central database
        central_db_path = get_central_database_path()
        central_db = IdeaInspirationDatabase(central_db_path, interactive=not no_interactive)
        
        # Get all calendar holidays ideas
        ideas = central_db.get_all(source_platform="calendar_holidays")
        
        if not ideas:
            click.echo("No events collected yet.")
            return
        
        # Calculate statistics
        total = len(ideas)
        by_importance = {}
        by_scope = {}
        by_country = {}
        
        for idea in ideas:
            importance = idea.metadata.get('importance', 'unknown')
            by_importance[importance] = by_importance.get(importance, 0) + 1
            
            scope = idea.metadata.get('scope', 'unknown')
            by_scope[scope] = by_scope.get(scope, 0) + 1
            
            country = idea.metadata.get('country', 'unknown')
            by_country[country] = by_country.get(country, 0) + 1
        
        # Display statistics
        click.echo(f"\n{'='*50}")
        click.echo(f"Event Collection Statistics")
        click.echo(f"{'='*50}\n")
        click.echo(f"Total Events: {total}\n")
        
        click.echo(f"Events by Country:")
        for country, count in sorted(by_country.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            click.echo(f"  {country}: {count} ({percentage:.1f}%)")
        
        click.echo(f"\nEvents by Importance:")
        for importance, count in sorted(by_importance.items()):
            percentage = (count / total) * 100
            click.echo(f"  {importance}: {count} ({percentage:.1f}%)")
        
        click.echo(f"\nEvents by Scope:")
        for scope, count in sorted(by_scope.items()):
            percentage = (count / total) * 100
            click.echo(f"  {scope}: {count} ({percentage:.1f}%)")
        
        click.echo()
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
@click.confirmation_option(prompt='Are you sure you want to clear all calendar holidays events?')
def clear(env_file, no_interactive):
    """Clear calendar holidays events from the central database.
    
    Note: This only removes events from this source, not the entire database.
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Open central database
        central_db_path = get_central_database_path()
        
        # Note: IdeaInspirationDatabase doesn't have a delete by platform method yet
        # For now, just inform the user to use the central database tools
        click.echo("To clear calendar holidays events, use the central IdeaInspiration database tools.")
        click.echo(f"Central database: {central_db_path}")
        click.echo("This ensures data consistency across all sources.")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
