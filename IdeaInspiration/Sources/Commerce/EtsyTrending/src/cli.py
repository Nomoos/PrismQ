"""Command-line interface for PrismQ.IdeaInspiration.Sources.Commerce.EtsyTrending."""

import click
import sys
from pathlib import Path
from .core.config import Config
from .core.database import Database
from .core.metrics import CommerceMetrics
from .core.commerce_processor import CommerceProcessor
from .plugins.etsy_trending import EtsyTrendingPlugin


@click.group()
@click.version_option(version='1.0.0')
def main():
    """PrismQ Etsy Trending Source - Gather trending products from Etsy."""
    pass


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape(env_file, no_interactive):
    """Scrape trending products from Etsy.
    
    This command scrapes product data from Etsy across configured categories.
    Note that this uses mock data for demonstration.
    
    For production use, you should:
    1. Use Etsy Open API v3 (requires API key)
    2. Respect Etsy's robots.txt and Terms of Service
    3. Implement proper OAuth 2.0 authentication
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize Etsy plugin
        try:
            etsy_plugin = EtsyTrendingPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        
        # Scrape from Etsy
        total_scraped = 0
        total_saved = 0
        
        click.echo("Scraping Etsy trending products...")
        click.echo(f"Categories: {', '.join(config.etsy_categories)}")
        click.echo(f"Max listings per category: {config.etsy_max_listings}")
        click.echo("")
        
        try:
            products = etsy_plugin.scrape()
            total_scraped = len(products)
            click.echo(f"Found {len(products)} products")
            
            # Process and save each product
            for product in products:
                # Create commerce metrics
                metrics = CommerceMetrics.from_etsy(product)
                
                # Extract tags
                tags = product.get('tags', '')
                if not tags:
                    tags = CommerceProcessor.extract_tags_from_product(product)
                
                # Save to database
                success = db.insert_product(
                    source=etsy_plugin.get_source_name(),
                    source_id=product.get('listing_id', ''),
                    title=product.get('title', ''),
                    brand=product.get('shop_name', ''),
                    category=product.get('category', ''),
                    price=product.get('price'),
                    currency=product.get('currency', 'USD'),
                    description=product.get('description'),
                    tags=tags,
                    score=metrics.consumer_interest or 0.0,
                    score_dictionary=metrics.to_dict()
                )
                
                if success:
                    total_saved += 1
                    click.echo(f"  ✓ Saved: {product.get('title', '')[:60]}")
                else:
                    click.echo(f"  ↻ Updated: {product.get('title', '')[:60]}")
            
        except Exception as e:
            click.echo(f"Error scraping Etsy: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total products found: {total_scraped}")
        click.echo(f"Total products saved: {total_saved}")
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
              help='Maximum number of products to display')
@click.option('--category', '-c', help='Filter by category')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def list(env_file, limit, category, no_interactive):
    """List collected products."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Open database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get products
        if category:
            products = db.get_products_by_category(category, limit=limit)
        else:
            products = db.get_all_products(limit=limit)
        
        if not products:
            click.echo("No products found.")
            return
        
        # Display products
        click.echo(f"\n{'='*80}")
        click.echo(f"Collected Products ({len(products)} total)")
        click.echo(f"{'='*80}\n")
        
        for i, product in enumerate(products, 1):
            click.echo(f"{i}. [{product['category']}] {product['title']}")
            click.echo(f"   Listing ID: {product['source_id']}")
            if product['brand']:
                click.echo(f"   Shop: {product['brand']}")
            if product['price']:
                click.echo(f"   Price: ${product['price']} {product['currency']}")
            if product['score']:
                click.echo(f"   Score: {product['score']:.2f}")
            if product['tags']:
                click.echo(f"   Tags: {product['tags']}")
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
    """Show statistics about collected products."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Open database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get statistics
        statistics = db.get_statistics()
        
        if statistics['total'] == 0:
            click.echo("No products collected yet.")
            return
        
        # Build output as a string first to avoid Click dict iteration bug
        output_lines = []
        output_lines.append("\n" + "=" * 50)
        output_lines.append("Product Collection Statistics")
        output_lines.append("=" * 50 + "\n")
        output_lines.append(f"Total Products: {statistics['total']}\n")
        
        if statistics.get('by_source'):
            output_lines.append("Products by Source:")
            for source, count in sorted(statistics['by_source'].items()):
                percentage = (count / statistics['total']) * 100
                output_lines.append(f"  {source}: {count} ({percentage:.1f}%)")
            output_lines.append("")
        
        if statistics.get('by_category'):
            output_lines.append("Top Categories:")
            # Convert to list before iterating to avoid Click bug
            cat_list = [(k, v) for k, v in statistics['by_category'].items()]
            for category, count in cat_list[:10]:
                percentage = (count / statistics['total']) * 100
                output_lines.append(f"  {category}: {count} ({percentage:.1f}%)")
            output_lines.append("")
        
        # Output everything at once
        click.echo("\n".join(output_lines))
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
@click.confirmation_option(prompt='Are you sure you want to clear all products?')
def clear(env_file, no_interactive):
    """Clear all products from the database."""
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
