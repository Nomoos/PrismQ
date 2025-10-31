"""Command-line interface for PrismQ.IdeaInspiration.Sources.Events.EntertainmentReleases."""

import click
import sys
from pathlib import Path
from .core.config import Config
from .core.database import Database
from .core.metrics import UniversalMetrics
from .core.event_processor import EventProcessor
from .plugins.tmdb_plugin import TMDBPlugin


@click.group()
@click.version_option(version='1.0.0')
def main():
    """PrismQ Entertainment Releases Source - Gather event inspirations from entertainment releases."""
    pass


@main.command()
@click.option('--env-file', '-e', type=click.Path(), help='Path to .env file')
@click.option('--media-type', '-t', help='Media type (movie, tv)')
@click.option('--region', '-r', help='Region code (e.g., US, GB)')
@click.option('--max', '-m', type=int, help='Maximum number of releases to scrape')
@click.option('--no-interactive', is_flag=True, help='Disable interactive prompts')
def scrape(env_file, media_type, region, max, no_interactive):
    """Scrape entertainment releases from TMDB."""
    try:
        config = Config(env_file, interactive=not no_interactive)
        db = Database(config.database_path, interactive=not no_interactive)
        
        try:
            tmdb_plugin = TMDBPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            click.echo("\nGet a free API key at: https://www.themoviedb.org/settings/api", err=True)
            sys.exit(1)
        
        total_scraped = 0
        total_saved = 0
        
        media = media_type if media_type else config.default_media_type
        click.echo(f"Scraping {media} releases from TMDB...")
        
        try:
            releases_data = tmdb_plugin.scrape(
                media_type=media,
                region=region,
                upcoming=True,
                max_releases=max
            )
            total_scraped = len(releases_data)
            click.echo(f"Found {len(releases_data)} releases")
            
            for release_data in releases_data:
                event_signal = EventProcessor.process_release(release_data)
                universal_metrics = UniversalMetrics.from_entertainment_release(release_data)
                
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
            click.echo(f"Error scraping releases: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total releases found: {total_scraped}")
        click.echo(f"Total releases saved: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), help='Path to .env file')
@click.option('--limit', '-l', type=int, default=20, help='Maximum number of events to display')
@click.option('--no-interactive', is_flag=True, help='Disable interactive prompts')
def list(env_file, limit, no_interactive):
    """List collected events."""
    try:
        config = Config(env_file, interactive=not no_interactive)
        db = Database(config.database_path, interactive=not no_interactive)
        events = db.get_all_events(limit=limit)
        
        if not events:
            click.echo("No events found.")
            return
        
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
@click.option('--env-file', '-e', type=click.Path(), help='Path to .env file')
@click.option('--no-interactive', is_flag=True, help='Disable interactive prompts')
def stats(env_file, no_interactive):
    """Show statistics about collected events."""
    try:
        config = Config(env_file, interactive=not no_interactive)
        db = Database(config.database_path, interactive=not no_interactive)
        events = db.get_all_events()
        
        if not events:
            click.echo("No events collected yet.")
            return
        
        total = len(events)
        by_source = {}
        by_importance = {}
        by_media = {}
        
        for event in events:
            by_source[event['source']] = by_source.get(event['source'], 0) + 1
            by_importance[event.get('importance', 'unknown')] = by_importance.get(event.get('importance', 'unknown'), 0) + 1
            
            if event.get('metadata'):
                metadata = event['metadata']
                if isinstance(metadata, dict):
                    media = metadata.get('media_type', 'unknown')
                    by_media[media] = by_media.get(media, 0) + 1
        
        click.echo(f"\n{'='*50}")
        click.echo(f"Event Collection Statistics")
        click.echo(f"{'='*50}\n")
        click.echo(f"Total Events: {total}\n")
        
        click.echo(f"Events by Source:")
        for source, count in sorted(by_source.items()):
            click.echo(f"  {source}: {count} ({(count / total) * 100:.1f}%)")
        
        click.echo(f"\nEvents by Importance:")
        for importance, count in sorted(by_importance.items()):
            click.echo(f"  {importance}: {count} ({(count / total) * 100:.1f}%)")
        
        if by_media:
            click.echo(f"\nEvents by Media Type:")
            for media, count in sorted(by_media.items()):
                click.echo(f"  {media}: {count} ({(count / total) * 100:.1f}%)")
        
        click.echo()
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), help='Path to .env file')
@click.option('--no-interactive', is_flag=True, help='Disable interactive prompts')
@click.confirmation_option(prompt='Are you sure you want to clear all events?')
def clear(env_file, no_interactive):
    """Clear all events from the database."""
    try:
        config = Config(env_file, interactive=not no_interactive)
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
