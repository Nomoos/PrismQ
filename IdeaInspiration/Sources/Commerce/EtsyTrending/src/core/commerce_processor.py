"""Commerce data processor for transforming raw product data."""

from typing import Dict, Any
from .metrics import CommerceMetrics


class CommerceProcessor:
    """Processes and transforms commerce data to unified format."""
    
    @staticmethod
    def process_amazon_product(product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Amazon product data to unified format.
        
        Args:
            product_data: Raw product data from Amazon
            
        Returns:
            Unified product dictionary
        """
        # Create commerce metrics
        metrics = CommerceMetrics.from_amazon(product_data)
        
        # Build unified product format
        unified = {
            'source': 'amazon_bestsellers',
            'source_id': product_data.get('asin', ''),
            'product': {
                'name': product_data.get('title', ''),
                'brand': product_data.get('brand', ''),
                'category': product_data.get('category', ''),
                'price': product_data.get('price'),
                'currency': product_data.get('currency', 'USD')
            },
            'seller': {
                'name': product_data.get('seller_name', ''),
                'rating': product_data.get('seller_rating'),
                'feedback_count': product_data.get('seller_feedback_count')
            },
            'metrics': {
                'sales_rank': product_data.get('sales_rank'),
                'category_rank': product_data.get('category_rank'),
                'rating': product_data.get('rating'),
                'review_count': product_data.get('review_count', 0),
                'review_velocity': product_data.get('review_velocity')
            },
            'trends': {
                'rank_change_24h': product_data.get('rank_change_24h'),
                'price_change_pct': metrics.discount_percentage,
                'review_momentum': product_data.get('review_momentum', 'stable')
            },
            'universal_metrics': {
                'popularity_score': metrics.popularity_score,
                'trend_strength': metrics.trend_strength,
                'consumer_interest': metrics.consumer_interest
            }
        }
        
        return unified
    
    @staticmethod
    def extract_tags_from_product(product_data: Dict[str, Any]) -> str:
        """Extract tags from product data.
        
        Args:
            product_data: Product data dictionary
            
        Returns:
            Comma-separated tag string
        """
        tags = []
        
        # Add category as tag
        if product_data.get('category'):
            tags.append(product_data['category'])
        
        # Add brand as tag
        if product_data.get('brand'):
            tags.append(product_data['brand'])
        
        # Add special badges
        if product_data.get('bestseller_badge'):
            tags.append('bestseller')
        
        if product_data.get('amazon_choice'):
            tags.append('amazon_choice')
        
        if product_data.get('has_prime'):
            tags.append('prime')
        
        # Add price range tag
        price = product_data.get('price')
        if price:
            if price < 25:
                tags.append('budget')
            elif price < 100:
                tags.append('mid_range')
            else:
                tags.append('premium')
        
        return ','.join(tags)
