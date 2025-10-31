"""Command-line interface for PrismQ.IdeaInspiration.Sources.Events.CalendarHolidays."""

import click
import sys
from pathlib import Path
from datetime import datetime
from .core.config import Config
from .core.database import Database
from .core.metrics import UniversalMetrics
from .core.event_processor import EventProcessor
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
        
        # Initialize databases (source-specific AND central)
        db = Database(config.database_path, interactive=not no_interactive)
        central_db_path = get_central_database_path()
        central_db = IdeaInspirationDatabase(central_db_path, interactive=not no_interactive)
        
        # Initialize holidays plugin
        holidays_plugin = CalendarHolidaysPlugin(config)
        
        # Determine country and year
        country_code = country if country else config.default_country
        year_val = year if year else int(config.default_year)
        
        # Scrape holidays
        total_scraped = 0
        total_saved_source = 0
        total_saved_central = 0
        
        click.echo(f"Scraping holidays for {country_code} in {year_val}...")
        
        try:
            holidays_data = holidays_plugin.scrape(country=country_code, year=year_val)
            total_scraped = len(holidays_data)
            click.echo(f"Found {len(holidays_data)} holidays")
            
            # Process and save each holiday
            for holiday_data in holidays_data:
                # Process to unified event format
                event_signal = EventProcessor.process_holiday(holiday_data)
                
                # Calculate universal metrics
                universal_metrics = UniversalMetrics.from_holiday(holiday_data)
                
                # Save to source-specific database (events table)
                source_saved = db.insert_event(
                    source=event_signal['source'],
                    source_id=event_signal['source_id'],
                    name=event_signal['event']['name'],
                    event_type=event_signal['event']['type'],
                    date=event_signal['event']['date'],
                    recurring=event_signal['event']['recurring'],
                    recurrence_pattern=event_signal['event']['recurrence_pattern'],
                    scope=event_signal['significance']['scope'],
                    importance=event_signal['significance']['importance'],
                    audience_size_estimate=event_signal['significance']['audience_size_estimate'],
                    pre_event_days=event_signal['content_window']['pre_event_days'],
                    post_event_days=event_signal['content_window']['post_event_days'],
                    peak_day=event_signal['content_window']['peak_day'],
                    metadata=event_signal['metadata'],
                    universal_metrics=universal_metrics.to_dict()
                )
                
                if source_saved:
                    total_saved_source += 1
                
                # Convert event to IdeaInspiration for central database (DUAL-SAVE)
                # Provide meaningful content beyond just the title
                event_description = (
                    f"{event_signal['event']['name']} is a {event_signal['event']['type']} "
                    f"observed in {country_code} on {event_signal['event']['date']}. "
                    f"Scope: {event_signal['significance']['scope']}, "
                    f"Importance: {event_signal['significance']['importance']}. "
                    f"Content window: {event_signal['content_window']['pre_event_days']} days before "
                    f"to {event_signal['content_window']['post_event_days']} days after."
                )
                
                idea = IdeaInspiration.from_text(
                    title=event_signal['event']['name'],
                    description=f"{event_signal['event']['type']} event in {country_code}",
                    text_content=event_description,  # Meaningful content with event details
                    keywords=[event_signal['event']['type'], country_code, 'holiday'],
                    metadata={
                        'event_type': event_signal['event']['type'],
                        'date': event_signal['event']['date'],
                        'country': country_code,
                        'scope': event_signal['significance']['scope'],
                        'importance': event_signal['significance']['importance'],
                        **event_signal['metadata']
                    },
                    source_id=event_signal['source_id'],
                    source_url=None,
                    source_created_by='calendar_holidays',
                    source_created_at=event_signal['event']['date'],
                    score=int(universal_metrics.overall_score * 10),  # Convert to 0-100 scale
                    category='event'
                )
                
                central_saved = central_db.insert(idea)
                if central_saved:
                    total_saved_central += 1
            
        except Exception as e:
            click.echo(f"Error scraping holidays: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total holidays found: {total_scraped}")
        click.echo(f"Saved to source database: {total_saved_source}")
        click.echo(f"Saved to central database: {total_saved_central}")
        click.echo(f"Source database: {config.database_path}")
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
@click.option('--source', '-s', help='Filter by source')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def list(env_file, limit, source, no_interactive):
    """List collected events."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Open database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get events
        events = db.get_all_events(limit=limit)
        
        # Filter by source if specified
        if source:
            events = [event for event in events if event['source'] == source]
        
        if not events:
            click.echo("No events found.")
            return
        
        # Display events
        click.echo(f"\n{'='*80}")
        click.echo(f"Collected Events ({len(events)} total)")
        click.echo(f"{'='*80}\n")
        
        for i, event in enumerate(events, 1):
            click.echo(f"{i}. [{event['source'].upper()}] {event['name']}")
            click.echo(f"   Date: {event['date']}")
            click.echo(f"   Scope: {event['scope']} | Importance: {event['importance']}")
            if event['universal_metrics']:
                metrics = event['universal_metrics']
                click.echo(f"   Significance: {metrics.get('significance_score', 'N/A')} | "
                          f"Content Opportunity: {metrics.get('content_opportunity', 'N/A')}")
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
        
        # Open database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get all events
        events = db.get_all_events()
        
        if not events:
            click.echo("No events collected yet.")
            return
        
        # Calculate statistics
        total = len(events)
        by_source = {}
        by_importance = {}
        by_scope = {}
        
        for event in events:
            source = event['source']
            by_source[source] = by_source.get(source, 0) + 1
            
            importance = event.get('importance', 'unknown')
            by_importance[importance] = by_importance.get(importance, 0) + 1
            
            scope = event.get('scope', 'unknown')
            by_scope[scope] = by_scope.get(scope, 0) + 1
        
        # Display statistics
        click.echo(f"\n{'='*50}")
        click.echo(f"Event Collection Statistics")
        click.echo(f"{'='*50}\n")
        click.echo(f"Total Events: {total}\n")
        
        click.echo(f"Events by Source:")
        for source, count in sorted(by_source.items()):
            percentage = (count / total) * 100
            click.echo(f"  {source}: {count} ({percentage:.1f}%)")
        
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
@click.confirmation_option(prompt='Are you sure you want to clear all events?')
def clear(env_file, no_interactive):
    """Clear all events from the database."""
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
