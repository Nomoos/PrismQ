"""Universal metrics schema for commerce sources.

This module defines a standardized metrics structure for e-commerce
and marketplace data across platforms like Amazon, Etsy, and App Stores.
"""

from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any, List


@dataclass
class CommerceMetrics:
    """Universal metrics schema for commerce data analysis.
    
    This schema standardizes metrics across different commerce platforms
    to enable consistent analysis and comparison.
    """
    
    # === Core Commerce Metrics ===
    sales_rank: Optional[int] = None              # Overall sales rank
    category_rank: Optional[int] = None           # Rank within category
    rating: Optional[float] = None                # Average rating (0-5)
    review_count: int = 0                         # Total number of reviews
    review_velocity: Optional[float] = None       # Reviews per day
    
    # === Price Metrics ===
    price: Optional[float] = None                 # Current price
    currency: str = "USD"                         # Currency code
    original_price: Optional[float] = None        # Original/list price
    discount_percentage: Optional[float] = None   # Discount %
    
    # === Seller/Developer Metrics ===
    seller_name: Optional[str] = None
    seller_rating: Optional[float] = None
    seller_feedback_count: Optional[int] = None
    
    # === Trend Metrics ===
    rank_change_24h: Optional[int] = None         # Rank change (negative = improvement)
    rank_change_7d: Optional[int] = None
    price_change_percentage: Optional[float] = None
    review_momentum: Optional[str] = None         # 'increasing', 'stable', 'decreasing'
    
    # === Product Metadata ===
    category: Optional[str] = None
    subcategories: List[str] = field(default_factory=list)
    brand: Optional[str] = None
    in_stock: bool = True
    
    # === Quality Indicators ===
    has_prime: bool = False                       # Amazon Prime eligible
    bestseller_badge: bool = False                # Bestseller tag
    amazon_choice: bool = False                   # Amazon's Choice
    verified_purchases: Optional[int] = None      # Verified purchase reviews
    
    # === Universal Scoring ===
    popularity_score: Optional[float] = None      # 0-10 scale
    trend_strength: Optional[float] = None        # 0-10 scale
    consumer_interest: Optional[float] = None     # 0-10 scale
    
    # === Platform Context ===
    platform: str = "unknown"                     # amazon, etsy, app_store
    product_type: Optional[str] = None            # physical, digital, service
    
    # === Additional Context ===
    first_available: Optional[str] = None         # Date first available
    last_updated: Optional[str] = None            # Last data update
    
    # === Raw Platform Data ===
    platform_specific: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_derived_metrics(self):
        """Calculate derived metrics from raw data."""
        # Discount percentage
        if self.price and self.original_price and self.original_price > self.price:
            self.discount_percentage = ((self.original_price - self.price) / self.original_price) * 100
        
        # Popularity score (0-10) based on reviews and rating
        if self.review_count and self.rating:
            # Normalize review count (log scale, capped at 10k reviews = score 10)
            import math
            review_score = min(10, (math.log10(self.review_count + 1) / 4) * 10)
            # Combine with rating (0-5 → 0-10)
            rating_score = (self.rating / 5) * 10
            self.popularity_score = (review_score + rating_score) / 2
        
        # Trend strength based on rank changes
        if self.rank_change_24h is not None:
            # Negative rank change = improvement = positive score
            if self.rank_change_24h < 0:
                self.trend_strength = min(10, abs(self.rank_change_24h) / 10)
            else:
                self.trend_strength = max(0, 5 - (self.rank_change_24h / 10))
        
        # Consumer interest combines popularity and trend
        if self.popularity_score is not None and self.trend_strength is not None:
            self.consumer_interest = (self.popularity_score * 0.6 + self.trend_strength * 0.4)
        elif self.popularity_score is not None:
            self.consumer_interest = self.popularity_score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary, excluding None values."""
        result = asdict(self)
        # Remove None values for cleaner storage
        return {k: v for k, v in result.items() if v is not None and v != [] and v != {}}
    
    @classmethod
    def from_amazon(cls, product_data: Dict[str, Any]) -> 'CommerceMetrics':
        """Create CommerceMetrics from Amazon product data.
        
        Args:
            product_data: Product data from Amazon scraping/API
        """
        metrics = cls(
            platform="amazon",
            product_type="physical",
            
            # Core metrics
            sales_rank=product_data.get('sales_rank'),
            category_rank=product_data.get('category_rank'),
            rating=product_data.get('rating'),
            review_count=product_data.get('review_count', 0),
            
            # Price
            price=product_data.get('price'),
            currency=product_data.get('currency', 'USD'),
            original_price=product_data.get('original_price'),
            
            # Seller
            seller_name=product_data.get('seller_name'),
            seller_rating=product_data.get('seller_rating'),
            seller_feedback_count=product_data.get('seller_feedback_count'),
            
            # Trends
            rank_change_24h=product_data.get('rank_change_24h'),
            
            # Product info
            category=product_data.get('category'),
            subcategories=product_data.get('subcategories', []),
            brand=product_data.get('brand'),
            in_stock=product_data.get('in_stock', True),
            
            # Quality indicators
            has_prime=product_data.get('has_prime', False),
            bestseller_badge=product_data.get('bestseller_badge', False),
            amazon_choice=product_data.get('amazon_choice', False),
            
            # Dates
            first_available=product_data.get('first_available'),
            
            # Platform specific
            platform_specific=product_data.get('platform_specific', {})
        )
        
        # Calculate derived metrics
        metrics.calculate_derived_metrics()
        
        return metrics
    
    @classmethod
    def from_etsy(cls, product_data: Dict[str, Any]) -> 'CommerceMetrics':
        """Create CommerceMetrics from Etsy product data.
        
        Args:
            product_data: Product data from Etsy API
        """
        metrics = cls(
            platform="etsy",
            product_type=product_data.get('product_type', 'physical'),
            
            # Core metrics
            rating=product_data.get('rating'),
            review_count=product_data.get('review_count', 0),
            
            # Price
            price=product_data.get('price'),
            currency=product_data.get('currency', 'USD'),
            original_price=product_data.get('original_price'),
            
            # Seller
            seller_name=product_data.get('shop_name'),
            seller_rating=product_data.get('shop_rating'),
            seller_feedback_count=product_data.get('shop_sales_count'),
            
            # Product info
            category=product_data.get('category'),
            in_stock=product_data.get('in_stock', True),
            
            # Quality indicators
            bestseller_badge=product_data.get('is_bestseller', False),
            
            # Platform specific
            platform_specific=product_data.get('platform_specific', {})
        )
        
        # Calculate derived metrics
        metrics.calculate_derived_metrics()
        
        return metrics
    
    @classmethod
    def from_app_store(cls, app_data: Dict[str, Any]) -> 'CommerceMetrics':
        """Create CommerceMetrics from App Store data.
        
        Args:
            app_data: App data from app store scraping
        """
        metrics = cls(
            platform="app_store",
            product_type="digital",
            
            # Core metrics
            category_rank=app_data.get('rank'),
            rating=app_data.get('rating'),
            review_count=app_data.get('review_count', 0),
            
            # Price
            price=app_data.get('price', 0.0),  # 0 for free apps
            currency=app_data.get('currency', 'USD'),
            
            # Developer (seller equivalent)
            seller_name=app_data.get('developer'),
            
            # Trends
            rank_change_24h=app_data.get('rank_change'),
            
            # Product info
            category=app_data.get('category'),
            
            # Platform specific
            platform_specific=app_data.get('platform_specific', {})
        )
        
        # Calculate derived metrics
        metrics.calculate_derived_metrics()
        
        return metrics
