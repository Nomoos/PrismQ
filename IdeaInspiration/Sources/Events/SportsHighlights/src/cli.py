"""Command-line interface for PrismQ.IdeaInspiration.Sources.Events.SportsHighlights."""

import click
import sys
from pathlib import Path
from datetime import datetime
from .core.config import Config
from .core.database import Database
from .core.metrics import UniversalMetrics
from .core.event_processor import EventProcessor
from .plugins.thesportsdb_plugin import TheSportsDBPlugin


@click.group()
@click.version_option(version='1.0.0')
def main():
    """PrismQ Sports Highlights Source - Gather event inspirations from sports events."""
    pass


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--league', '-l', help='League name (e.g., "English Premier League")')
@click.option('--season', '-s', help='Season (e.g., "2024-2025")')
@click.option('--date', '-d', help='Specific date (YYYY-MM-DD)')
@click.option('--next', '-n', is_flag=True, default=True,
              help='Get next upcoming events (default)')
@click.option('--max', '-m', type=int, help='Maximum number of events to scrape')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape(env_file, league, season, date, next, max, no_interactive):
    """Scrape sports events from TheSportsDB.
    
    Examples:
        python -m src.cli scrape --next
        python -m src.cli scrape --league "English Premier League" --next
        python -m src.cli scrape --date 2025-01-15
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize sports plugin
        try:
            sports_plugin = TheSportsDBPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        
        # Scrape sports events
        total_scraped = 0
        total_saved = 0
        
        if date:
            click.echo(f"Scraping sports events for {date}...")
        elif league:
            click.echo(f"Scraping next events for {league}...")
        else:
            click.echo(f"Scraping next events from popular leagues...")
        
        try:
            events_data = sports_plugin.scrape(
                league=league,
                season=season,
                date=date,
                next_events=next,
                max_events=max
            )
            total_scraped = len(events_data)
            click.echo(f"Found {len(events_data)} events")
            
            # Process and save each event
            for event_data in events_data:
                # Process to unified event format
                event_signal = EventProcessor.process_sports_event(event_data)
                
                # Calculate universal metrics
                universal_metrics = UniversalMetrics.from_sports_event(event_data)
                
                # Save to database
                success = db.insert_event(
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
                
                if success:
                    total_saved += 1
            
        except Exception as e:
            click.echo(f"Error scraping sports events: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total events found: {total_scraped}")
        click.echo(f"Total events saved: {total_saved}")
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
            if event.get('metadata'):
                metadata = event['metadata']
                if isinstance(metadata, dict):
                    league = metadata.get('league', '')
                    if league:
                        click.echo(f"   League: {league}")
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
        by_sport = {}
        
        for event in events:
            source = event['source']
            by_source[source] = by_source.get(source, 0) + 1
            
            importance = event.get('importance', 'unknown')
            by_importance[importance] = by_importance.get(importance, 0) + 1
            
            scope = event.get('scope', 'unknown')
            by_scope[scope] = by_scope.get(scope, 0) + 1
            
            # Extract sport from metadata
            if event.get('metadata'):
                metadata = event['metadata']
                if isinstance(metadata, dict):
                    sport = metadata.get('sport', 'unknown')
                    by_sport[sport] = by_sport.get(sport, 0) + 1
        
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
        
        if by_sport:
            click.echo(f"\nEvents by Sport:")
            for sport, count in sorted(by_sport.items(), key=lambda x: x[1], reverse=True)[:5]:
                percentage = (count / total) * 100
                click.echo(f"  {sport}: {count} ({percentage:.1f}%)")
        
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
