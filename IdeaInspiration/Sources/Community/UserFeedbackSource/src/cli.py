"""Command-line interface for UserFeedbackSource."""

import click
import sys
import json
from pathlib import Path
from .core.config import Config
from .core.database import Database
from .core.metrics import CommunityMetrics
from .core.sentiment_analyzer import SentimentAnalyzer
from .core.community_processor import CommunityProcessor
from .plugins.youtube_comments_plugin import YouTubeCommentsPlugin


@click.group()
@click.version_option(version='1.0.0')
def main():
    """UserFeedbackSource - Gather feedback from your own channel."""
    pass


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--channel-id', '-c', help='YouTube channel ID')
@click.option('--max-videos', '-v', type=int, default=10,
              help='Maximum videos to fetch comments from')
@click.option('--max-comments', '-m', type=int, help='Maximum comments per video')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape(env_file, channel_id, max_videos, max_comments, no_interactive):
    """Scrape comments from your YouTube channel.
    
    Examples:
        python -m src.cli scrape --channel-id UCxxxxx
        python -m src.cli scrape --max-videos 5 --max-comments 50
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_url, interactive=not no_interactive)
        
        # Initialize sentiment analyzer and processor
        sentiment_analyzer = SentimentAnalyzer()
        processor = CommunityProcessor(sentiment_analyzer)
        
        # Initialize YouTube plugin
        try:
            youtube_plugin = YouTubeCommentsPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        
        # Scrape comments
        total_scraped = 0
        total_saved = 0
        
        # Determine parameters
        channel = channel_id if channel_id else config.youtube_channel_id
        max_comments_value = max_comments if max_comments else config.max_comments
        
        if not channel:
            click.echo("Error: No channel ID specified. Use --channel-id or set USER_FEEDBACK_YOUTUBE_CHANNEL_ID in .env", err=True)
            sys.exit(1)
        
        click.echo(f"Scraping comments from YouTube channel: {channel}")
        click.echo(f"Max videos: {max_videos}")
        click.echo(f"Max comments per video: {max_comments_value}")
        click.echo("")
        
        try:
            # Scrape raw comment data
            raw_comments = youtube_plugin.scrape(
                channel_id=channel,
                max_videos=max_videos,
                max_comments_per_video=max_comments_value
            )
            total_scraped = len(raw_comments)
            click.echo(f"\nFound {len(raw_comments)} comments from channel")
            
            # Process and save each comment
            for comment_data in raw_comments:
                # Process comment into unified format
                signal = processor.process_comment(
                    text=comment_data['text'],
                    author=comment_data['author'],
                    source=comment_data['source'],
                    source_id=comment_data['source_id'],
                    platform=comment_data['platform'],
                    parent_content=comment_data.get('parent_content'),
                    upvotes=comment_data.get('upvotes', 0),
                    replies=comment_data.get('replies', 0),
                    timestamp=comment_data.get('timestamp'),
                    category=comment_data.get('category')
                )
                
                # Save to database
                success = db.insert_signal(signal)
                
                if success:
                    total_saved += 1
            
        except Exception as e:
            click.echo(f"Error scraping YouTube comments: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total comments found: {total_scraped}")
        click.echo(f"Total comments saved: {total_saved}")
        click.echo(f"Database: {config.database_url}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--limit', '-l', type=int, default=20, 
              help='Maximum number of signals to display')
@click.option('--source', '-s', help='Filter by source')
@click.option('--sentiment', help='Filter by sentiment (positive/negative/neutral)')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def list(env_file, limit, source, sentiment, no_interactive):
    """List collected community signals."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Open database
        db = Database(config.database_url, interactive=not no_interactive)
        
        # Get signals
        signals = db.get_all_signals(limit=limit)
        
        # Filter by source if specified
        if source:
            signals = [s for s in signals if s['source'] == source]
        
        # Filter by sentiment if specified
        if sentiment:
            signals = [s for s in signals if s['analysis']['sentiment'] == sentiment]
        
        if not signals:
            click.echo("No signals found.")
            return
        
        # Display signals
        click.echo(f"\n{'='*80}")
        click.echo(f"Community Signals ({len(signals)} total)")
        click.echo(f"{'='*80}\n")
        
        for i, signal in enumerate(signals, 1):
            content = signal['content']
            analysis = signal['analysis']
            universal = signal['universal_metrics']
            
            click.echo(f"{i}. [{signal['source'].upper()}] {content['author']}")
            click.echo(f"   ID: {signal['source_id']}")
            click.echo(f"   Platform: {signal['context']['platform']}")
            click.echo(f"   Sentiment: {analysis['sentiment']} (score: {analysis['sentiment_score']:.2f})")
            click.echo(f"   Intent: {analysis.get('intent', 'unknown')}")
            click.echo(f"   Topics: {', '.join(analysis.get('topics', []))}")
            click.echo(f"   Scores: Engagement={universal['engagement_score']:.1f}, "
                      f"Relevance={universal['relevance_score']:.1f}, "
                      f"Actionability={universal['actionability']:.1f}")
            
            text = content['text'][:150]
            if len(content['text']) > 150:
                text += "..."
            click.echo(f"   Text: {text}")
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
    """Show statistics about collected signals."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Open database
        db = Database(config.database_url, interactive=not no_interactive)
        
        # Get all signals
        signals = db.get_all_signals(limit=1000)  # Get more for stats
        
        if not signals:
            click.echo("No signals collected yet.")
            return
        
        # Calculate statistics
        total = len(signals)
        by_source = {}
        by_sentiment = {}
        by_intent = {}
        
        for signal in signals:
            source = signal['source']
            sentiment = signal['analysis']['sentiment']
            intent = signal['analysis'].get('intent', 'unknown')
            
            by_source[source] = by_source.get(source, 0) + 1
            by_sentiment[sentiment] = by_sentiment.get(sentiment, 0) + 1
            by_intent[intent] = by_intent.get(intent, 0) + 1
        
        # Display statistics
        click.echo(f"\n{'='*50}")
        click.echo(f"Community Signal Statistics")
        click.echo(f"{'='*50}\n")
        click.echo(f"Total Signals: {total}\n")
        
        click.echo(f"Signals by Source:")
        for source, count in sorted(by_source.items()):
            percentage = (count / total) * 100
            click.echo(f"  {source}: {count} ({percentage:.1f}%)")
        
        click.echo(f"\nSignals by Sentiment:")
        for sentiment, count in sorted(by_sentiment.items()):
            percentage = (count / total) * 100
            click.echo(f"  {sentiment}: {count} ({percentage:.1f}%)")
        
        click.echo(f"\nSignals by Intent:")
        for intent, count in sorted(by_intent.items()):
            percentage = (count / total) * 100
            click.echo(f"  {intent}: {count} ({percentage:.1f}%)")
        
        click.echo()
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
@click.confirmation_option(prompt='Are you sure you want to clear all signals?')
def clear(env_file, no_interactive):
    """Clear all signals from the database."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Delete database file (for SQLite)
        if config.database_url.startswith("sqlite:///"):
            db_path = Path(config.database_path)
            if db_path.exists():
                db_path.unlink()
                click.echo(f"Database cleared: {config.database_path}")
            else:
                click.echo("Database does not exist.")
        else:
            click.echo("Clear command only works with SQLite databases.")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
